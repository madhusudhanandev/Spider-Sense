"""
Builds the ScamFingerprint for an incident: the stable-property summary
used today for simple similarity matching, and later as the input to a real
embedding step (section 20, section 32's future pipeline diagram).
"""
from app.models.enums import ScamCategory
from app.services.ai.base import AIAnalysisOutput


def build_fingerprint_data(
    ai_output: AIAnalysisOutput,
    platform: str | None,
    language: str | None,
    input_type: str,
) -> dict:
    delivery_method = {
        "text": "message",
        "screenshot": "message",
        "image": "message",
        "url": "message",
        "audio": "voice_call",
    }.get(input_type, "message")

    try:
        category = ScamCategory(ai_output.scam_category)
    except ValueError:
        category = ScamCategory.UNKNOWN

    return {
        "target_organization": ai_output.claimed_organization,
        "scam_category": category,
        "platform": platform,
        "language": language,
        "delivery_method": delivery_method,
        "tactics": [t.name for t in ai_output.psychological_tactics],
        "requested_actions": list(ai_output.requested_actions),
    }
