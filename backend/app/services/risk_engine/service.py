"""
RiskEngine (section 14).

Combines signals from the AI analysis, URL analysis, and (later) community
evidence into one explainable 0-100 score. The LLM's own `confidence` is one
input among several -- never the sole basis for the final number, per the
spec's "do not blindly trust an LLM-generated number".
"""
from app.models.enums import RiskLevel
from app.schemas.common import RiskBreakdown
from app.schemas.common import URLAnalysisResult
from app.services.ai.base import AIAnalysisOutput

# Requested actions that indicate the scam is asking for something
# high-value/irreversible (credentials, money, OTP) weigh more heavily.
_HIGH_VALUE_ACTIONS = {"provide_credentials", "provide_otp", "transfer_money", "scan_qr_code"}


class RiskEngineResult:
    def __init__(self, score: int, level: RiskLevel, breakdown: RiskBreakdown):
        self.score = score
        self.level = level
        self.breakdown = breakdown


def _risk_level_from_score(score: int) -> RiskLevel:
    if score >= 80:
        return RiskLevel.CRITICAL
    if score >= 55:
        return RiskLevel.HIGH
    if score >= 30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def compute_risk(
    ai_output: AIAnalysisOutput,
    url_results: list[URLAnalysisResult] | None = None,
    related_incident_count: int = 0,
) -> RiskEngineResult:
    url_results = url_results or []

    # --- Component 1: text / social-engineering signals ---
    tactic_component = 0.0
    for tactic in ai_output.psychological_tactics:
        tactic_component += tactic.confidence * 8  # up to ~8 pts per strong tactic
    tactic_component = min(tactic_component, 40)

    ai_confidence_component = ai_output.confidence * 20 if ai_output.scam_detected else 0
    text_component = min(int(tactic_component + ai_confidence_component), 45)

    # --- Component 2: URL signals ---
    url_component = 0
    if url_results:
        url_component = min(max(r.risk_score for r in url_results) // 3, 30)  # scale 0-100 -> 0-30

    # --- Component 3: credential / payment request ---
    credential_component = 0
    if any(a in _HIGH_VALUE_ACTIONS for a in ai_output.requested_actions):
        credential_component = 20

    # --- Component 4: community evidence (populated once similar reports exist) ---
    community_component = min(related_incident_count * 2, 15)

    other_component = 0

    total = text_component + url_component + credential_component + community_component + other_component
    total = max(0, min(int(total), 100))

    breakdown = RiskBreakdown(
        text_social_engineering=text_component,
        url_signals=url_component,
        credential_or_payment_request=credential_component,
        community_evidence=community_component,
        other=other_component,
    )

    return RiskEngineResult(score=total, level=_risk_level_from_score(total), breakdown=breakdown)
