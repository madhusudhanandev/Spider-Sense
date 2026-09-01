import pytest
from fastapi.testclient import TestClient

from app.api import routes
from app.main import app


@pytest.fixture(autouse=True)
def reset_case_store():
    routes.orchestrator.store.clear()
    yield
    routes.orchestrator.store.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def create_case(client):
    def _create(payload=None):
        case_payload = payload or {
            "message": "Your bank account will be blocked. Complete KYC now.",
            "platform": "WhatsApp",
            "language": "English",
        }
        response = client.post("/analyze", json=case_payload)
        assert response.status_code == 200, response.text
        return response.json()

    return _create


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_case_creation(client):
    response = client.post(
        "/analyze",
        json={
            "message": "Your bank account will be blocked. Complete KYC now.",
            "platform": "WhatsApp",
            "language": "English",
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["case_id"].startswith("SPIDER-")
    assert "created_at" in data
    assert "updated_at" in data
    assert data["created_at"]
    assert data["updated_at"]


def test_message_update(client, create_case):
    initial = create_case({
        "message": "Your account will be blocked. Complete KYC now.",
        "platform": "WhatsApp",
        "language": "English",
    })
    case_id = initial["case_id"]
    created_at = initial["created_at"]
    original_score = initial["risk_score"]

    response = client.post(f"/cases/{case_id}/messages", json={"message": "Enter your internet banking password."})

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["case_id"] == case_id
    assert data["messages"][-1] == "Enter your internet banking password."
    assert data["updated_at"] != created_at
    assert data["created_at"] == created_at
    assert data["current_stage"] == "INFORMATION_CAPTURE"
    assert data["risk_score"] >= original_score


def test_multiple_stage_updates(client):
    analyze = client.post(
        "/analyze",
        json={
            "message": "Your bank account is blocked. Complete KYC now.",
            "platform": "WhatsApp",
            "language": "English",
        },
    )
    case_id = analyze.json()["case_id"]

    messages = [
        "Complete KYC through https://fake-bank.example",
        "Enter your username and password.",
        "Enter the OTP received on your phone.",
        "Transfer Rs. 5000 to complete verification.",
    ]

    for message in messages:
        response = client.post(f"/cases/{case_id}/messages", json={"message": message})
        assert response.status_code == 200, response.text

    case = client.get(f"/cases/{case_id}").json()
    assert len(client.get("/cases").json()["cases"]) == 1
    assert len(case["messages"]) == len(messages)
    assert len(case["stage_history"]) >= len(messages)
    assert case["current_stage"] == "MONETIZATION"
    assert case["risk_level"] == "CRITICAL"


def test_stage_does_not_regress(client):
    response = client.post(
        "/analyze",
        json={
            "message": "Transfer Rs. 5000 to complete verification.",
            "platform": "WhatsApp",
            "language": "English",
        },
    )
    case_id = response.json()["case_id"]

    update = client.post(f"/cases/{case_id}/messages", json={"message": "Thank you."})
    assert update.status_code == 200, update.text
    case = update.json()
    assert case["current_stage"] not in {"HOOK", "UNKNOWN"}
    assert case["current_stage"] == "MONETIZATION"


def test_exposure_guidance_valid_statuses(client):
    analyze = client.post(
        "/analyze",
        json={
            "message": "Your bank account will be blocked. Complete KYC now.",
            "platform": "WhatsApp",
            "language": "English",
        },
    )
    case_id = analyze.json()["case_id"]
    statuses = [
        "NOTHING_YET",
        "CLICKED_LINK",
        "SHARED_DETAILS",
        "SHARED_PASSWORD",
        "SHARED_OTP",
        "TRANSFERRED_MONEY",
        "INSTALLED_APPLICATION",
    ]

    for status in statuses:
        response = client.post(f"/cases/{case_id}/exposure", json={"status": status})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["case_id"] == case_id
        assert data["exposure_status"] == status
        assert data["recommended_actions"]

    first = client.post(f"/cases/{case_id}/exposure", json={"status": "NOTHING_YET"}).json()
    second = client.post(f"/cases/{case_id}/exposure", json={"status": "SHARED_OTP"}).json()
    third = client.post(f"/cases/{case_id}/exposure", json={"status": "INSTALLED_APPLICATION"}).json()
    assert first["recommended_actions"] != second["recommended_actions"]
    assert second["recommended_actions"] != third["recommended_actions"]


def test_shared_otp_guidance(client):
    case_id = client.post(
        "/analyze",
        json={"message": "Complete KYC now.", "platform": "WhatsApp", "language": "English"},
    ).json()["case_id"]
    response = client.post(f"/cases/{case_id}/exposure", json={"status": "SHARED_OTP"})
    text = " ".join(response.json()["recommended_actions"]).lower()
    assert "contact" in text or "institution" in text
    assert "account activity" in text or "review" in text


def test_transferred_money_guidance(client):
    case_id = client.post(
        "/analyze",
        json={"message": "Complete KYC now.", "platform": "WhatsApp", "language": "English"},
    ).json()["case_id"]
    response = client.post(f"/cases/{case_id}/exposure", json={"status": "TRANSFERRED_MONEY"})
    text = " ".join(response.json()["recommended_actions"]).lower()
    assert "bank" in text or "payment provider" in text
    assert "transaction evidence" in text or "evidence" in text


def test_installed_application_guidance(client):
    case_id = client.post(
        "/analyze",
        json={"message": "Complete KYC now.", "platform": "WhatsApp", "language": "English"},
    ).json()["case_id"]
    response = client.post(f"/cases/{case_id}/exposure", json={"status": "INSTALLED_APPLICATION"})
    text = " ".join(response.json()["recommended_actions"]).lower()
    assert "disconnect" in text or "device" in text
    assert "remove" in text or "software" in text or "credentials" in text


def test_invalid_exposure_status(client):
    case_id = client.post(
        "/analyze",
        json={"message": "Complete KYC now.", "platform": "WhatsApp", "language": "English"},
    ).json()["case_id"]
    before = client.get(f"/cases/{case_id}").json()["exposure_status"]

    response = client.post(f"/cases/{case_id}/exposure", json={"status": "RANDOM_VALUE"})
    assert response.status_code == 422
    after = client.get(f"/cases/{case_id}").json()["exposure_status"]
    assert after == before


def test_invalid_case_requests(client):
    for method, path, payload in [
        ("GET", "/cases/does-not-exist", None),
        ("POST", "/cases/does-not-exist/messages", {"message": "Oops"}),
        ("POST", "/cases/does-not-exist/exposure", {"status": "SHARED_OTP"}),
    ]:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json=payload)
        assert response.status_code == 404
        assert response.json() == {"detail": "Case not found"}


def test_analyze_generates_case_id(client):
    response = client.post(
        "/analyze",
        json={
            "message": "Your account will be blocked. Complete KYC now.",
            "platform": "WhatsApp",
            "language": "English",
        },
    )

    assert response.status_code == 200
    assert response.json()["case_id"].startswith("SPIDER-")


def test_invalid_case_is_rejected(client):
    response = client.post("/analyze", json={"subject": "", "description": ""})
    assert response.status_code == 400


def test_analyze_case_produces_risk_score(client):
    payload = {
        "message": "Urgent bank verification required. Please verify immediately.",
        "platform": "SMS",
        "language": "English",
    }

    response = client.post("/analyze", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case_id"].startswith("SPIDER-")
    assert body["risk_score"] > 0
    assert body["risk_level"] in {"low", "medium", "high", "CRITICAL"}
    assert len(body["indicators"]) > 0
