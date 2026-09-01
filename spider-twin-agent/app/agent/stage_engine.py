from __future__ import annotations


class StageEngine:
    _RANK = {
        "HOOK": 0,
        "PRESSURE": 1,
        "INFORMATION_CAPTURE": 2,
        "MONETIZATION": 3,
        "ESCALATION": 4,
        "CONTAINMENT": 5,
    }

    def stages(self, risk_score: float) -> list[str]:
        if risk_score >= 75:
            return ["triage", "containment", "evidence_collection", "response"]
        if risk_score >= 45:
            return ["triage", "evidence_collection", "validation"]
        return ["triage", "monitoring"]

    def determine_stage(self, current_stage: str | None, message: str, risk_score: float | None = None) -> str:
        normalized = (message or "").lower()
        current = (current_stage or "HOOK").upper()
        candidate = current

        if "otp" in normalized or "one-time password" in normalized or "verification code" in normalized or "password" in normalized:
            candidate = "INFORMATION_CAPTURE"
        elif "transfer" in normalized or "payment" in normalized or "money" in normalized:
            candidate = "MONETIZATION"
        elif "install" in normalized or "app" in normalized:
            candidate = "ESCALATION"
        elif "link" in normalized or "click" in normalized or "visit" in normalized or "kyc" in normalized:
            candidate = "PRESSURE"
        elif risk_score is not None and risk_score >= 75:
            candidate = "CONTAINMENT"
        elif current == "HOOK" and ("urgent" in normalized or "account" in normalized or "blocked" in normalized):
            candidate = "PRESSURE"

        current_rank = self._RANK.get(current, 0)
        candidate_rank = self._RANK.get(candidate.upper(), 0)
        if candidate_rank < current_rank:
            return current
        return candidate.upper()
