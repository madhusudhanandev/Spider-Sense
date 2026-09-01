from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.agent.orchestrator import Orchestrator
from app.schemas.case import CaseInput, ExposureInput, InvestigationResult, MessageInput

router = APIRouter()
orchestrator = Orchestrator()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "spider-twin-agent"}


@router.post("/analyze", response_model=InvestigationResult)
def analyze_case(case: CaseInput) -> InvestigationResult:
    case_id = f"SPIDER-{uuid4().hex[:8].upper()}"
    case_data = case.model_dump()
    message = (case_data.get("message") or "").strip()
    subject = (case_data.get("subject") or "Scam alert").strip() or "Scam alert"
    description = (case_data.get("description") or message).strip() or message
    platform = (case_data.get("platform") or case_data.get("source") or "unknown").strip() or "unknown"
    language = (case_data.get("language") or "English").strip() or "English"

    payload = {
        "case_id": case_id,
        "subject": subject,
        "description": description,
        "source": platform,
        "risk_level": case_data.get("risk_level") or "medium",
        "tags": case_data.get("tags", []),
        "metadata": {
            **(case_data.get("metadata") or {}),
            "platform": platform,
            "language": language,
        },
    }

    result = orchestrator.handle_case(payload)
    if result.get("status") == "rejected":
        raise HTTPException(status_code=400, detail=result.get("message", "Invalid case"))

    return InvestigationResult(
        case_id=result["case_id"],
        status="processed",
        summary=result["summary"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        indicators=result["indicators"],
        findings=result["patterns"],
        recommended_actions=result["next_steps"],
        created_at=result.get("created_at"),
        updated_at=result.get("updated_at"),
        generated_at="now",
    )


@router.get("/cases")
def list_cases() -> dict:
    return {"cases": orchestrator.store.list()}


@router.get("/cases/{case_id}")
def get_case(case_id: str) -> dict:
    case = orchestrator.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/cases/{case_id}/messages")
def add_message(case_id: str, payload: MessageInput) -> dict:
    case = orchestrator.add_message(case_id, payload.message)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/cases/{case_id}/exposure")
def update_exposure(case_id: str, payload: ExposureInput) -> dict:
    case = orchestrator.update_exposure_status(case_id, payload.status.value)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
