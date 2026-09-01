from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.agent.forecast_engine import ForecastEngine
from app.agent.guardian import Guardian
from app.agent.investigation_planner import InvestigationPlanner
from app.agent.stage_engine import StageEngine
from app.agent.tool_registry import ToolRegistry
from app.schemas.case import ExposureStatus
from app.services.demo_analyzer import DemoAnalyzer
from app.storage.case_store import CaseStore


class Orchestrator:
    def __init__(self) -> None:
        self.guardian = Guardian()
        self.planner = InvestigationPlanner()
        self.stage_engine = StageEngine()
        self.forecast = ForecastEngine()
        self.tools = ToolRegistry()
        self.analyzer = DemoAnalyzer()
        self.store = CaseStore()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _base_case_record(self, case: dict, analysis: dict) -> dict:
        case_id = case.get("case_id") or str(uuid.uuid4())
        created_at = self._now_iso()
        initial_text = case.get("description") or case.get("message") or case.get("subject") or ""
        initial_stage = self.stage_engine.determine_stage("HOOK", initial_text, analysis["risk_score"])
        case_record = {
            "case_id": case_id,
            "subject": case.get("subject", ""),
            "description": case.get("description", ""),
            "source": case.get("source", "unknown"),
            "risk_level": case.get("risk_level", "low"),
            "risk_score": analysis["risk_score"],
            "summary": analysis["summary"],
            "indicators": analysis["indicators"],
            "patterns": analysis["patterns"],
            "messages": [],
            "current_stage": initial_stage,
            "previous_stage": None,
            "stage_history": [{"from": None, "to": initial_stage, "trigger": "initial_analysis"}],
            "exposure_status": ExposureStatus.NOTHING_YET.value,
            "predicted_next_tactic": self.forecast.predict_next_tactic(initial_text, initial_stage),
            "investigation_questions": self.guardian.investigation_questions(initial_stage, ExposureStatus.NOTHING_YET.value),
            "recommended_actions": self.guardian.recovery_actions(ExposureStatus.NOTHING_YET.value, initial_stage, analysis["risk_score"]),
            "forecast": self.forecast.predict(analysis["risk_score"]),
            "next_steps": analysis["next_steps"],
            "analysis": analysis,
            "plan": self.planner.plan(case),
            "stages": self.stage_engine.stages(analysis["risk_score"]),
            "created_at": created_at,
            "updated_at": created_at,
        }
        return case_record

    def handle_case(self, case: dict) -> dict:
        valid, message = self.guardian.validate(case)
        if not valid:
            return {"status": "rejected", "message": message}

        case_id = case.get("case_id") or f"SPIDER-{uuid.uuid4().hex[:8].upper()}"
        case["case_id"] = case_id
        case["subject"] = case.get("subject") or "Scam alert"
        case["description"] = case.get("description") or case.get("message") or "Scam alert"
        analysis = self.analyzer.analyze(case)
        case_record = self._base_case_record(case, analysis)
        case_record["case_id"] = case_id
        self.store.save(case_record)

        result = {
            "status": "accepted",
            "case_id": case_id,
            "summary": analysis["summary"],
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "indicators": analysis["indicators"],
            "patterns": analysis["patterns"],
            "plan": case_record["plan"],
            "stages": case_record["stages"],
            "forecast": case_record["forecast"],
            "next_steps": analysis["next_steps"],
            "created_at": case_record["created_at"],
            "updated_at": case_record["updated_at"],
        }
        return result

    def get_case(self, case_id: str) -> dict | None:
        return self.store.get(case_id)

    def add_message(self, case_id: str, message: str) -> dict | None:
        case = self.store.get(case_id)
        if case is None:
            return None

        previous_stage = case.get("current_stage") or "HOOK"
        case.setdefault("messages", [])
        case["messages"].append(message)

        combined_text = " ".join([case.get("subject", ""), case.get("description", ""), *case["messages"]])
        analysis = self.analyzer.analyze({
            "case_id": case_id,
            "subject": case.get("subject", ""),
            "description": combined_text,
            "source": case.get("source", "unknown"),
            "risk_level": case.get("risk_level", "low"),
        })

        new_stage = self.stage_engine.determine_stage(previous_stage, message, analysis["risk_score"])
        case["previous_stage"] = previous_stage
        case["current_stage"] = new_stage
        case["risk_score"] = analysis["risk_score"]
        case["risk_level"] = "CRITICAL" if new_stage in {"MONETIZATION", "ESCALATION", "CONTAINMENT"} or analysis["risk_score"] >= 85 else analysis["risk_level"]
        case["summary"] = analysis["summary"]
        case["indicators"] = analysis["indicators"]
        case["patterns"] = analysis["patterns"]
        case["next_steps"] = analysis["next_steps"]
        case["forecast"] = self.forecast.predict(analysis["risk_score"])
        case["predicted_next_tactic"] = self.forecast.predict_next_tactic(message, new_stage)
        case["investigation_questions"] = self.guardian.investigation_questions(new_stage, case.get("exposure_status"))
        case["recommended_actions"] = self.guardian.recovery_actions(case.get("exposure_status", ExposureStatus.NOTHING_YET.value), new_stage, analysis["risk_score"])
        case["stage_history"] = case.get("stage_history", [])
        case["stage_history"].append({"from": previous_stage, "to": new_stage, "trigger": message})
        case["analysis"] = analysis
        case["stages"] = self.stage_engine.stages(analysis["risk_score"])
        case["updated_at"] = self._now_iso()
        self.store.save(case)
        return case

    def update_exposure_status(self, case_id: str, status: str) -> dict | None:
        case = self.store.get(case_id)
        if case is None:
            return None
        if not self.guardian.validate_exposure_status(status):
            raise ValueError(f"Invalid exposure status: {status}")

        case["exposure_status"] = status.upper()
        case["recommended_actions"] = self.guardian.recovery_actions(case["exposure_status"], case.get("current_stage"), case.get("risk_score"))
        case["investigation_questions"] = self.guardian.investigation_questions(case.get("current_stage"), case.get("exposure_status"))
        case["updated_at"] = self._now_iso()
        self.store.save(case)
        return case
