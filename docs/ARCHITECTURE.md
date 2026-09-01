# Architecture

## Layers

```
Input (text / url / screenshot / audio)
        v
Input-specific pre-processing (OCR / speech-to-text / URL extraction)
        v
AnalysisPipeline (app/services/pipeline.py)
    - AIAnalysisService       -> structured JSON findings (never the final risk number)
    - URLAnalysisService      -> deterministic technical URL signals
    - RiskEngine              -> explainable, weighted 0-100 score
        v
Structured Incident (+ Evidence, Indicators, Tactics, RequestedActions, Fingerprint, IncidentReport)
        v
(optional, explicit opt-in) CommunityReport
        v
Community intelligence (feed, stats, related-incident matching)
```

## Backend module map

| Module | Responsibility |
|---|---|
| `app/core/config.py` | Environment-driven settings; every external integration is optional |
| `app/core/database.py` | SQLAlchemy engine/session |
| `app/models/` | Normalized schema (see `docs/FUTURE_INTELLIGENCE.md` for why) |
| `app/schemas/` | Pydantic request/response contracts (never expose ORM models directly) |
| `app/services/ai/` | `AIAnalysisService` interface + OpenAI implementation + mock fallback + factory |
| `app/services/ocr/` | `OCRService` interface + Tesseract implementation + mock fallback |
| `app/services/speech/` | `SpeechToTextService` interface + OpenAI Whisper implementation + mock fallback |
| `app/services/url_analysis/` | Deterministic technical URL analyzer (never asks the LLM alone) |
| `app/services/risk_engine/` | Weighted, explainable scoring |
| `app/services/intelligence/` | Fingerprint builder + rule-based similarity/duplicate detection |
| `app/services/reports/` | Structured `IncidentReport` payload builder |
| `app/services/pipeline.py` | Orchestrates all of the above into one persisted `Incident` |
| `app/api/routes/` | FastAPI routers: `health`, `analysis`, `incidents`, `reports` (community) |

## Provider abstraction pattern

Every external dependency (LLM, OCR, speech-to-text, URL reputation) follows
the same shape:

1. An abstract base class (`base.py`) defining the interface.
2. One or more concrete implementations.
3. A `factory.py` (or equivalent) that picks an implementation from
   `Settings` and **falls back to a mock implementation** if the real one
   can't initialize (missing key, missing binary, etc.) -- so the app always
   starts and the demo always runs, even with zero API keys configured.

Nothing outside a service's own module should import a concrete
implementation directly; always go through the factory function.

## Security notes

- **SSRF**: `URLAnalysisService` never fetches a submitted URL's content. It
  only parses the URL string and applies heuristics. If a future version
  adds redirect-following or content fetching, it must validate resolved
  IPs against private/link-local ranges before connecting.
- **Uploads**: image/audio uploads are validated by declared `content_type`
  and size before processing; nothing uploaded is ever executed.
- **Secrets**: all API keys live in `.env` (see `.env.example`), loaded via
  `pydantic-settings`, and are never sent to the frontend.
- **Community redaction**: `CommunityReport` is a separate table from
  `Incident`, populated only by an explicit opt-in endpoint
  (`POST /api/incidents/{id}/community-report`). See `app/utils/sanitize.py`
  and `docs/FUTURE_INTELLIGENCE.md` for the privacy model.
