from __future__ import annotations

import json
from pathlib import Path
from typing import List


class IndicatorExtractor:
    def __init__(self, patterns_path: str | None = None) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.patterns_path = Path(patterns_path) if patterns_path else base_dir.parent / "data" / "scam_patterns.json"
        self._patterns = self._load_patterns()

    def _load_patterns(self) -> List[dict]:
        if not self.patterns_path.exists():
            return []
        with self.patterns_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def extract(self, text: str) -> tuple[List[str], List[str]]:
        normalized = text.lower()
        indicators: List[str] = []
        matched_patterns: List[str] = []

        for pattern in self._patterns:
            keywords = pattern.get("keywords", [])
            if any(keyword.lower() in normalized for keyword in keywords):
                matched_patterns.append(pattern.get("name", "unknown_pattern"))
                indicators.extend([keyword for keyword in keywords if keyword.lower() in normalized])

        if not indicators:
            indicators = ["general-risk-signal"]
        return sorted(set(indicators)), sorted(set(matched_patterns))

    def risk_multiplier(self, patterns: List[str]) -> float:
        total = 1.0
        for pattern in self._patterns:
            name = pattern.get("name")
            if name in patterns:
                total *= float(pattern.get("risk_multiplier", 1.0))
        return total
