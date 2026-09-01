from __future__ import annotations

from typing import Dict, List, Optional


class CaseStore:
    def __init__(self) -> None:
        self._cases: Dict[str, dict] = {}

    def save(self, case: dict) -> dict:
        self._cases[case["case_id"]] = case
        return case

    def get(self, case_id: str) -> Optional[dict]:
        return self._cases.get(case_id)

    def list(self) -> List[dict]:
        return list(self._cases.values())

    def clear(self) -> None:
        self._cases.clear()
