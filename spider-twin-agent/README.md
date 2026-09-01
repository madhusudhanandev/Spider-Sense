# spider-twin-agent

A minimal FastAPI-based investigation orchestration prototype for scam and fraud analysis.

## Features
- Case intake and investigation orchestration
- Risk scoring and indicator extraction
- Scam-pattern detection using local JSON patterns
- In-memory case storage
- REST API endpoints for health and case analysis

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Example

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case-001",
    "subject": "Urgent bank verification request",
    "description": "Victim received a fake SMS asking to verify a payment detail.",
    "source": "sms",
    "risk_level": "medium"
  }'
```
