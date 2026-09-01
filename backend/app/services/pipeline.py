"""
AnalysisPipeline: the single orchestrator that turns raw input (text, a URL,
OCR'd screenshot text, or a transcription) into a persisted, structured
Incident -- with its indicators, tactics, requested actions, fingerprint,
and generated report all created together.

Every route (analyze/text, analyze/url, analyze/image, analyze/audio)
converges on `run_pipeline()` after doing its input-type-specific
pre-processing (OCR, transcription, direct URL analysis). This is what keeps
the "don't build this as Input -> LLM -> SCAM" principle (section 34) real:
the LLM is one component feeding a larger structured process, not the whole
pipeline.
"""
from sqlalchemy.orm import Session

from app.models.enums import IndicatorType, RequestedActionType, RiskLevel, ScamCategory, TacticName
from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.indicator import IncidentIndicator, Indicator
from app.models.intelligence import IncidentRequestedAction, IncidentReport, ScamFingerprint
from app.models.tactic import IncidentTactic, Tactic
from app.schemas.analysis import AnalysisResult
from app.schemas.common import IndicatorOut, RecommendedAction, RiskBreakdown, TacticOut, URLAnalysisResult
from app.services.ai.base import AIAnalysisOutput
from app.services.ai.factory import get_ai_service
from app.services.intelligence.fingerprint import build_fingerprint_data
from app.services.reports.incident_report_service import build_incident_report_payload
from app.services.risk_engine.service import compute_risk
from app.services.url_analysis.service import get_url_analysis_service
from app.utils.extraction import extract_emails, extract_phone_numbers, extract_urls, normalize_domain, normalize_phone


async def run_pipeline(
    db: Session,
    *,
    input_type,  # app.models.enums.InputType
    text: str,
    platform: str | None = None,
    language_hint: str | None = None,
    user_id=None,
    explicit_url: str | None = None,
) -> AnalysisResult:
    url_service = get_url_analysis_service()
    ai_service = get_ai_service()

    # --- 1. Deterministic extraction (backstop, independent of the model) ---
    candidate_urls = list({*extract_urls(text), *([explicit_url] if explicit_url else [])})
    url_results: list[URLAnalysisResult] = [url_service.analyze(u) for u in candidate_urls]

    # --- 2. AI analysis, given the URL facts as ground truth ---
    ai_output: AIAnalysisOutput = await ai_service.analyze(
        text=text,
        platform=platform,
        language_hint=language_hint,
        url_facts=[r.model_dump() for r in url_results] or None,
    )

    # --- 3. Deterministic risk scoring (never trust the LLM's number alone) ---
    risk = compute_risk(ai_output, url_results, related_incident_count=0)

    # --- 4. Persist the Incident ---
    try:
        scam_category = ScamCategory(ai_output.scam_category)
    except ValueError:
        scam_category = ScamCategory.UNKNOWN

    incident = Incident(
        user_id=user_id,
        input_type=input_type,
        platform=platform,
        language=ai_output.language or language_hint,
        raw_text=text,
        risk_score=risk.score,
        risk_level=risk.level,
        scam_category=scam_category,
        claimed_organization=ai_output.claimed_organization,
        ai_summary=ai_output.summary,
        ai_explanation=ai_output.explanation,
    )
    db.add(incident)
    db.flush()  # assign incident.id without committing yet

    # --- 5. Evidence: preserve the raw content itself ---
    db.add(Evidence(incident_id=incident.id, evidence_type="original_text", content_text=text))

    # --- 6. Tactics ---
    for finding in ai_output.psychological_tactics:
        try:
            tactic_name = TacticName(finding.name)
        except ValueError:
            continue
        tactic = db.query(Tactic).filter(Tactic.name == tactic_name).one_or_none()
        if tactic is None:
            tactic = Tactic(name=tactic_name)
            db.add(tactic)
            db.flush()
        db.add(IncidentTactic(incident_id=incident.id, tactic_id=tactic.id, confidence=finding.confidence, evidence=finding.evidence))

    # --- 7. Requested actions ---
    for action in ai_output.requested_actions:
        try:
            action_type = RequestedActionType(action)
        except ValueError:
            action_type = RequestedActionType.OTHER
        db.add(IncidentRequestedAction(incident_id=incident.id, action=action_type))

    # --- 8. Indicators: from the AI's entity extraction + the deterministic backstop ---
    indicator_entries: list[tuple[IndicatorType, str, float, str]] = []
    for entity in ai_output.entities:
        try:
            itype = IndicatorType(entity.type.upper())
        except ValueError:
            continue
        indicator_entries.append((itype, entity.value, entity.confidence, "ai_extraction"))

    for u in candidate_urls:
        indicator_entries.append((IndicatorType.URL, u, 0.99, "regex"))
        domain = normalize_domain(u)
        if domain:
            indicator_entries.append((IndicatorType.DOMAIN, domain, 0.99, "regex"))
    for phone in extract_phone_numbers(text):
        indicator_entries.append((IndicatorType.PHONE, phone, 0.7, "regex"))
    for email in extract_emails(text):
        indicator_entries.append((IndicatorType.EMAIL, email, 0.7, "regex"))

    seen_in_this_incident: set[tuple[str, str]] = set()
    indicator_outs: list[IndicatorOut] = []
    for itype, raw_value, confidence, source in indicator_entries:
        normalized = raw_value.strip().lower() if itype != IndicatorType.PHONE else normalize_phone(raw_value)
        dedup_key = (itype.value, normalized)
        if dedup_key in seen_in_this_incident:
            continue
        seen_in_this_incident.add(dedup_key)

        indicator = db.query(Indicator).filter(Indicator.type == itype, Indicator.normalized_value == normalized).one_or_none()
        if indicator is None:
            indicator = Indicator(type=itype, normalized_value=normalized)
            db.add(indicator)
            db.flush()
        else:
            indicator.times_seen += 1

        db.add(IncidentIndicator(incident_id=incident.id, indicator_id=indicator.id, raw_value=raw_value, confidence=confidence, source=source))
        indicator_outs.append(IndicatorOut(type=itype.value, value=raw_value, confidence=confidence, source=source))

    # --- 9. Fingerprint ---
    fp_data = build_fingerprint_data(ai_output, platform, ai_output.language or language_hint, input_type.value)
    db.add(ScamFingerprint(incident_id=incident.id, **fp_data))

    db.flush()
    db.refresh(incident)

    # --- 10. Structured report ---
    payload = build_incident_report_payload(incident)
    db.add(IncidentReport(incident_id=incident.id, payload=payload, recommended_actions=ai_output.recommended_actions))

    db.commit()
    db.refresh(incident)

    return AnalysisResult(
        incident_id=incident.id,
        scam_detected=ai_output.scam_detected,
        confidence=ai_output.confidence,
        risk_score=risk.score,
        risk_level=risk.level.value,
        risk_breakdown=risk.breakdown,
        scam_category=scam_category.value,
        claimed_organization=ai_output.claimed_organization,
        language=incident.language,
        platform=platform,
        tactics=[TacticOut(name=t.name, confidence=t.confidence, evidence=t.evidence) for t in ai_output.psychological_tactics],
        indicators=indicator_outs,
        requested_actions=list(ai_output.requested_actions),
        url_analysis=url_results,
        summary=ai_output.summary,
        explanation=ai_output.explanation,
        recommended_actions=[RecommendedAction(label=a, kind="protect") for a in ai_output.recommended_actions],
        related_incident_count=0,
    )
