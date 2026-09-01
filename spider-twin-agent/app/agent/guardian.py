from __future__ import annotations

from app.schemas.case import ExposureStatus


class Guardian:
    def __init__(self) -> None:
        self.policy_version = "v1"

    def validate(self, case: dict) -> tuple[bool, str]:
        if not case.get("subject"):
            return False, "subject is required"
        if not case.get("description"):
            return False, "description is required"
        return True, "ok"

    def validate_exposure_status(self, value: str | ExposureStatus) -> bool:
        if isinstance(value, ExposureStatus):
            return True
        return value in {status.value for status in ExposureStatus}

    def recovery_actions(self, exposure_status: str, current_stage: str | None = None, risk_score: float | None = None) -> list[str]:
        status = (exposure_status or "NOTHING_YET").upper()
        actions = {
            "NOTHING_YET": [
                "Continue monitoring for pressure tactics and social-engineering cues.",
                "Document all observed contact details and time stamps.",
            ],
            "CLICKED_LINK": [
                "Isolate the device from the network and run a malware scan.",
                "Reset credentials associated with the contacted account.",
            ],
            "SHARED_DETAILS": [
                "Notify the account owner and revoke active sessions immediately.",
                "Check for suspicious login activity and contact the platform security team.",
            ],
            "SHARED_PASSWORD": [
                "Force a password reset on all related accounts.",
                "Enable multi-factor authentication and review recent transactions.",
            ],
            "SHARED_OTP": [
                "Block the linked account and treat the OTP as compromised.",
                "Contact the relevant institution and review recent account activity, then notify the bank or payment provider to prevent unauthorized transfers.",
            ],
            "TRANSFERRED_MONEY": [
                "Freeze the affected account and initiate incident response.",
                "Contact the bank or payment provider, preserve transaction evidence, and file a fraud report with the relevant financial institutions.",
            ],
            "INSTALLED_APPLICATION": [
                "Disconnect the device from the network, remove the suspicious software, and change credentials from a trusted device.",
                "Escalate to digital forensics and incident response specialists, then review installed applications and remote access permissions.",
            ],
        }
        base_actions = list(actions.get(status, actions["NOTHING_YET"]))
        if current_stage == "INFORMATION_CAPTURE" and risk_score is not None and risk_score >= 45:
            base_actions.append("Escalate the case to a higher priority investigation and collect evidence immediately.")
        return base_actions

    def investigation_questions(self, stage: str | None, exposure_status: str | None = None) -> list[str]:
        stage_name = (stage or "HOOK").upper()
        questions = {
            "HOOK": [
                "What contact channel was used, and when did it first appear?",
                "Did the message create urgency, fear, or a sense of authority?",
            ],
            "PRESSURE": [
                "What specific pressure language was used to push a rapid response?",
                "Did the victim receive a request to act before checking the source?",
            ],
            "INFORMATION_CAPTURE": [
                "What credentials, personal details, or OTPs were requested from the victim?",
                "Were any personal identifiers or account credentials already shared?",
            ],
            "MONETIZATION": [
                "Was any payment or transfer requested or completed?",
                "What financial details were exposed, and how were they used?",
            ],
            "ESCALATION": [
                "Did the attacker ask the victim to install tools or grant remote access?",
                "What access or monitoring privileges were provided to the attacker?",
            ],
            "CONTAINMENT": [
                "What immediate containment steps have already been taken?",
                "Which stakeholders need to be notified to prevent further harm?",
            ],
        }
        result = list(questions.get(stage_name, questions["HOOK"]))
        if exposure_status and exposure_status.upper() == "SHARED_OTP":
            result.append("Did the victim share the OTP or verification code with the attacker?")
        return result
