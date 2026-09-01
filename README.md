# Spider-Sense AI

An AI-powered multimodal scam-detection and threat-intelligence platform.

**Detect. Explain. Protect.** — and, in the long run, learn how scam
campaigns evolve so tomorrow's variants can be predicted before they spread.

This repository implements **Phases 1-3** of the product vision:

1. **Basic multimodal scam detection** — text, URL, screenshot/image, and
   voice input, all producing an explainable risk score.
2. **Structured scam intelligence** — every analysis becomes a normalized
   `Incident` with indicators, tactics, requested actions, and a
   fingerprint, not just a `message + scam/not-scam` row.
3. **Community threat intelligence** — optional, sanitized sharing;
   duplicate/related-report detection; a trending-threats feed.

Phase 4+ (embeddings, campaign clustering, mutation detection, predictive
early warning) is **not implemented** — see `docs/FUTURE_INTELLIGENCE.md`
for exactly how the current schema and services are designed to support it
without being rebuilt.

## Project structure

```
spider-sense/
├── backend/     FastAPI + SQLAlchemy + PostgreSQL
├── frontend/    React + TypeScript + Vite
├── data/        Synthetic sample scams + example community reports
└── docs/        Architecture + future-intelligence design notes
```

## Quick start

### 1. Database

Any Postgres instance works (local, Docker, or Supabase Postgres). Create a
database, then set `DATABASE_URL` in `backend/.env` accordingly.

```bash
createdb spidersense   # or use Docker / Supabase
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set DATABASE_URL, and OPENAI_API_KEY if you want real AI analysis
# (AI_PROVIDER falls back to a deterministic mock analyzer if the key is missing)
uvicorn app.main:app --reload
```

The API starts at `http://localhost:8000`. Interactive docs at
`http://localhost:8000/docs`. Tables are created automatically on startup
via `create_all` for local dev; see below for real migrations.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app starts at `http://localhost:5173` and proxies `/api` requests to
the backend (see `vite.config.ts`).

### 4. Try the demo flow

1. Go to `/` and paste a suspicious message, or upload a screenshot.
2. Review the risk score, detected tactics, and technical URL scan.
3. Click **Share with the community**.
4. Go to `/community` to see it in the feed and stats.
5. Analyze a second, similar message — the result page will show
   **"Following the web"** with a related-report count.

## Environment variables

See `backend/.env.example` and `frontend/.env.example` for the full list.
Nothing is hard-coded: every external integration (LLM provider, OCR,
speech-to-text, URL reputation) has a working mock fallback, so the app
runs end-to-end with zero API keys configured.

| Variable | Purpose | Default behavior if unset |
|---|---|---|
| `DATABASE_URL` | Postgres connection string | Required — the app needs a DB |
| `AI_PROVIDER` / `OPENAI_API_KEY` | LLM-backed scam analysis | Falls back to a deterministic keyword-based analyzer |
| `OCR_PROVIDER` | Screenshot text extraction | Falls back to a placeholder if Tesseract isn't installed |
| `SPEECH_PROVIDER` | Voice-note transcription | Falls back to a placeholder unless set to `openai_whisper` with a key |
| `URL_REPUTATION_PROVIDER` | Domain reputation/age lookups | Runs the built-in heuristic analyzer only |

## Database

See `docs/ARCHITECTURE.md` for the full module map, and
`backend/app/models/` for the schema itself: `User`, `Incident`, `Evidence`,
`Indicator`/`IncidentIndicator`, `Tactic`/`IncidentTactic`,
`IncidentRequestedAction`, `ScamFingerprint`, `IncidentReport`,
`CommunityReport`.

### Migrations

The scaffold uses `Base.metadata.create_all()` on startup for fast local
iteration. Before shipping past a hackathon demo, switch to Alembic:

```bash
cd backend
alembic init alembic
# configure alembic/env.py to import app.core.database.Base and app.models
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## API overview

```
POST   /api/analyze/text
POST   /api/analyze/url
POST   /api/analyze/image
POST   /api/analyze/audio

GET    /api/incidents/{id}
POST   /api/incidents/{id}/community-report

GET    /api/community/reports
GET    /api/community/stats
GET    /api/community/related/{incident_id}

GET    /api/health
```

Full request/response schemas are in `backend/app/schemas/` and live at
`/docs` once the backend is running.

## What's NOT built yet (by design)

Per the product spec: no browser extension, no WhatsApp bot, no mobile app,
no deepfake detection, no custom model training, no embeddings/vector
search, no campaign clustering or mutation detection, no predictive model.
See `docs/FUTURE_INTELLIGENCE.md`.

## Design language

The frontend follows the Spider-Man-inspired cybersecurity direction from
the design brief, using original spider/web-motif illustrations rather than
licensed character artwork (see `frontend/src/components/common/SpiderEmblem.tsx`)
so the product never depends on copyrighted assets to function.
