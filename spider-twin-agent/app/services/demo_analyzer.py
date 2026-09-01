from __future__ import annotations

from app.services.ai_service import AIService
from app.services.indicator_extractor import IndicatorExtractor
from app.services.risk_engine import RiskEngine


class DemoAnalyzer:
    def __init__(self) -> None:
        self.indicator_extractor = IndicatorExtractor()
        self.risk_engine = RiskEngine()
        self.ai_service = AIService()

    def analyze(self, case: dict) -> dict:
        combined_text = f"{case.get('subject', '')} {case.get('description', '')} {case.get('source', '')}"
        indicators, patterns = self.indicator_extractor.extract(combined_text)
        risk_score, risk_level = self.risk_engine.score(combined_text, indicators, patterns)
        multiplier = self.indicator_extractor.risk_multiplier(patterns)
        final_score = min(100, round(risk_score * multiplier, 2))
        final_level = "high" if final_score >= 75 else "medium" if final_score >= 45 else "low"

        summary = self.ai_service.summarize(case.get("subject", ""), indicators, final_score)
        next_steps = self.ai_service.plan_next_steps(final_score)

        return {
            "case_id": case.get("case_id"),
            "subject": case.get("subject"),
            "source": case.get("source", "unknown"),
            "risk_score": final_score,
            "risk_level": final_level,
            "indicators": indicators,
            "patterns": patterns,
            "summary": summary,
            "confidence": 0.82 if final_score >= 45 else 0.68,
            "next_steps": next_steps,
            "metadata": {"raw_risk_score": risk_score, "risk_multiplier": multiplier},
        }
