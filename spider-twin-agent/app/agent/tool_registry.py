from __future__ import annotations

from typing import Dict, List


class ToolRegistry:
    def __init__(self) -> None:
        self.tools: Dict[str, dict] = {
            "indicator_extractor": {"name": "indicator_extractor", "description": "Extract scam indicators from narrative text."},
            "risk_engine": {"name": "risk_engine", "description": "Compute a risk score for a case."},
            "case_store": {"name": "case_store", "description": "Persist and lookup investigation cases."},
        }

    def list_tools(self) -> List[dict]:
        return list(self.tools.values())

    def get(self, name: str) -> dict | None:
        return self.tools.get(name)
