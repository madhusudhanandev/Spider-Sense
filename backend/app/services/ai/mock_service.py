"""
Deterministic, keyword-based stand-in for a real LLM call.

Used when AI_PROVIDER=mock, or as an automatic fallback if OPENAI_API_KEY
is missing, so the app (and the demo) still works end-to-end without a key
configured -- per section 8/35 ("gracefully handle ... missing API keys").
"""
import re

from app.services.ai.base import AIAnalysisOutput, AIAnalysisService, ExtractedEntity, TacticFinding

_URGENCY_WORDS = ["immediately", "urgent", "today", "24 hours", "expire", "blocked", "suspend"]
_AUTHORITY_WORDS = ["bank", "rbi", "income tax", "government", "police", "customs", "courier", "kyc"]
_CREDENTIAL_WORDS = ["otp", "password", "pin", "cvv", "verify your account", "click the link", "update your details"]
_REWARD_WORDS = ["won", "prize", "lottery", "congratulations", "reward", "cashback"]

_URL_RE = re.compile(r"https?://[^\s]+")
_PHONE_RE = re.compile(r"(\+?\d[\d\-\s]{7,}\d)")


class MockAIAnalysisService(AIAnalysisService):
    async def analyze(
        self,
        *,
        text: str,
        platform: str | None = None,
        language_hint: str | None = None,
        url_facts: list[dict] | None = None,
    ) -> AIAnalysisOutput:
        lower = text.lower()

        tactics: list[TacticFinding] = []
        if any(w in lower for w in _URGENCY_WORDS):
            tactics.append(TacticFinding(name="urgency", confidence=0.85, evidence="Message uses urgent/time-pressure language."))
        if any(w in lower for w in _AUTHORITY_WORDS):
            tactics.append(TacticFinding(name="authority_impersonation", confidence=0.75, evidence="Message references an authority/organization."))
        if any(w in lower for w in _CREDENTIAL_WORDS):
            tactics.append(TacticFinding(name="credential_harvesting", confidence=0.9, evidence="Message asks for credentials/OTP or to click a verification link."))
        if any(w in lower for w in _REWARD_WORDS):
            tactics.append(TacticFinding(name="reward_greed", confidence=0.8, evidence="Message promises a prize/reward."))

        requested_actions: list[str] = []
        if "otp" in lower:
            requested_actions.append("provide_otp")
        if any(w in lower for w in ["pin", "password", "cvv", "card number"]):
            requested_actions.append("provide_credentials")
        if _URL_RE.search(text):
            requested_actions.append("click_url")
        if "transfer" in lower or "pay" in lower:
            requested_actions.append("transfer_money")
        if "call" in lower and _PHONE_RE.search(text):
            requested_actions.append("call_number")
        if not requested_actions and tactics:
            requested_actions.append("other")

        entities: list[ExtractedEntity] = []
        for m in _URL_RE.findall(text):
            entities.append(ExtractedEntity(type="url", value=m, confidence=0.99))
        for m in _PHONE_RE.findall(text):
            entities.append(ExtractedEntity(type="phone", value=m.strip(), confidence=0.7))

        scam_detected = len(tactics) >= 1
        confidence = min(0.5 + 0.15 * len(tactics), 0.97) if scam_detected else 0.15

        category = "unknown"
        if any(w in lower for w in ["bank", "kyc", "account"]):
            category = "bank_impersonation" if "kyc" not in lower else "kyc_fraud"
        elif any(w in lower for w in _REWARD_WORDS):
            category = "lottery_prize_scam"
        elif "job" in lower or "hiring" in lower or "work from home" in lower:
            category = "job_scam"
        elif "courier" in lower or "customs" in lower or "parcel" in lower:
            category = "courier_delivery_scam"
        elif scam_detected:
            category = "other"

        summary = (
            "This message shows several common scam warning signs."
            if scam_detected
            else "This message doesn't show obvious scam warning signs, but stay cautious with unexpected messages."
        )
        explanation = (
            "It combines pressure tactics with a request for sensitive information or an urgent action, "
            "which is a common pattern in scam messages."
            if scam_detected
            else "No strong urgency, authority-impersonation, or credential-harvesting language was detected."
        )

        recommended_actions = (
            ["Do not click any links in the message", "Do not share OTPs, passwords, or PINs", "Verify directly with the organization using an official number", "Report and block the sender"]
            if scam_detected
            else ["Stay cautious with unsolicited messages", "Verify independently if anything seems off"]
        )

        return AIAnalysisOutput(
            scam_detected=scam_detected,
            confidence=confidence,
            scam_category=category,
            risk_factors=[t.evidence for t in tactics],
            psychological_tactics=tactics,
            requested_actions=requested_actions or ["other"] if scam_detected else [],
            claimed_organization=None,
            language=language_hint,
            entities=entities,
            summary=summary,
            explanation=explanation,
            recommended_actions=recommended_actions,
        )