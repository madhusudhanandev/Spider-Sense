from __future__ import annotations

from typing import List, Tuple


class RiskEngine:
    def score(self, text: str, indicators: List[str], patterns: List[str]) -> Tuple[float, str]:
        base = 20
        indicator_count = max(len(indicators), 1)
        base += min(indicator_count * 12, 35)
        base += min(len(patterns) * 15, 25)

        urgency_hits = sum(1 for item in indicators if any(token in item.lower() for token in ["urgent", "verify", "alert", "suspended", "immediately", "action required"]))
        base += min(urgency_hits * 10, 20)

        score = min(base, 100)
        if score >= 75:
            return score, "high"
        if score >= 45:
            return score, "medium"
        return score, "low"
