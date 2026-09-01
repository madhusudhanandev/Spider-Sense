from __future__ import annotations

from typing import Iterable, List


class AIService:
    def __init__(self, model_name: str = "demo-model") -> None:
        self.model_name = model_name

    def summarize(self, subject: str, indicators: Iterable[str], risk_score: float) -> str:
        indicator_text = ", ".join(indicators) if indicators else "no prominent indicators"
        severity = "high" if risk_score >= 75 else "medium" if risk_score >= 45 else "low"
        return (
            f"Investigation for '{subject}' indicates {severity} concern, with key signals including "
            f"{indicator_text}."
        )

    def plan_next_steps(self, risk_score: float) -> List[str]:
        if risk_score >= 75:
            return [
                "Escalate for manual review immediately.",
                "Collect all communication artifacts and sender metadata.",
                "Notify relevant containment stakeholders.",
            ]
        if risk_score >= 45:
            return [
                "Continue investigation with targeted evidence gathering.",
                "Cross-check related claims against known scam patterns.",
                "Prepare a brief for the response team.",
            ]
        return [
            "Monitor for additional signals and new activity.",
            "Record the case for future baseline comparison.",
        ]
