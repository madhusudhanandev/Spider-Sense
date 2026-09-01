from __future__ import annotations


class ForecastEngine:
    def predict(self, risk_score: float) -> dict:
        if risk_score >= 75:
            return {"likelihood": "high", "confidence": 0.88, "expected_outcome": "rapid escalation and blocking"}
        if risk_score >= 45:
            return {"likelihood": "medium", "confidence": 0.73, "expected_outcome": "targeted review and evidence collection"}
        return {"likelihood": "low", "confidence": 0.62, "expected_outcome": "continued monitoring"}

    def predict_next_tactic(self, message: str, stage: str | None = None) -> str:
        normalized = (message or "").lower()
        if "otp" in normalized or "one-time password" in normalized or "code" in normalized:
            return "REQUEST_OTP"
        if "click" in normalized or "link" in normalized:
            return "CLICK_URL"
        if "transfer" in normalized or "money" in normalized or "payment" in normalized:
            return "UNAUTHORIZED_TRANSACTION"
        if stage == "INFORMATION_CAPTURE":
            return "REQUEST_OTP"
        return "PROVIDE_CREDENTIALS"
