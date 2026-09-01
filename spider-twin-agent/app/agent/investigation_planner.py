from __future__ import annotations

from typing import List


class InvestigationPlanner:
    def plan(self, case: dict) -> List[str]:
        subject = case.get("subject", "")
        actions = ["Review inbound communications and sender metadata."]
        if "bank" in subject.lower() or "payment" in subject.lower():
            actions.append("Verify whether the subject mentions account security or payment action.")
        if "urgent" in subject.lower() or "alert" in subject.lower():
            actions.append("Check whether urgency tactics were used to pressure a response.")
        actions.append("Prepare a concise incident summary for the investigation lead.")
        return actions
