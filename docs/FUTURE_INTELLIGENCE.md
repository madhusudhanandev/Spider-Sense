# Future Campaign-Intelligence Architecture

Phases 1-3 (implemented) are the **data-generation layer**. This document
explains what Phase 4+ (not implemented) will build on top, and exactly
which pieces of today's schema/services already exist to support it.

## The future pipeline

```
Individual Incident
        v
Structured Intelligence        <- Phases 1-3 (done): Incident, Indicator,
        v                          Tactic, ScamFingerprint, IncidentReport
    Embedding                  <- NOT implemented. Natural home: a vector
        v                          column on ScamFingerprint (see model docstring)
  Similarity Search             <- Phase 3 ships a rule-based version today
        v                          (app/services/intelligence/similarity.py);
                                   swap in pgvector/embeddings later behind
                                   the same function signature.
  Campaign Discovery            <- NOT implemented. Would group incidents
        v                          whose fingerprints/embeddings cluster.
  Campaign Clustering           <- NOT implemented.
        v
  Mutation Detection             <- NOT implemented. Compares fingerprints
        v                          within a campaign over time (e.g. platform
                                   changes from SMS -> WhatsApp).
  Campaign Evolution             <- NOT implemented. Time-ordered view of
        v                          mutations within one campaign.
  Evolution Drivers               <- NOT implemented.
        v
  Predictive Model                <- NOT implemented.
        v
  Future Scam Variant Prediction  <- NOT implemented.
        v
  Early Warning                   <- NOT implemented.
```

## What today's schema already provides

- **Deduplicated indicators** (`Indicator` + `IncidentIndicator`): a domain,
  phone number, or payment ID is one row regardless of how many incidents
  reference it. Campaign discovery can start from "which incidents share an
  indicator?" as a single join, with no text-mining required.
- **Normalized tactics** (`Tactic` + `IncidentTactic`): tactic taxonomy is a
  lookup table, so "which campaigns increasingly use voice + urgency?" is a
  group-by, not a full-text search.
- **`ScamFingerprint`**: one row per incident capturing the properties that
  are expected to stay *stable* across a campaign's mutations (target
  organization, category, tactics, requested actions) separately from the
  properties expected to *change* (exact wording, specific domain, exact
  phone number). This is the natural place to add an `embedding` column
  later (see the commented-out example in
  `app/models/intelligence.py::ScamFingerprint`) without restructuring
  anything.
- **`IncidentReport.payload`**: a frozen, complete structured snapshot of an
  incident at analysis time -- the eventual ingestion unit for a future
  offline clustering/training job, so historical incidents don't need to be
  reconstructed from live (and possibly since-edited) rows.
- **Rule-based similarity today, swappable tomorrow**:
  `find_related_community_reports()` in
  `app/services/intelligence/similarity.py` already answers "what looks
  related to this incident?" using exact indicator matches and fuzzy text
  similarity. Its signature (`Session, Incident -> list[SimilarityMatch]`)
  is designed so a future embedding-based implementation is a drop-in
  replacement for the callers in `app/api/routes/analysis.py` and
  `app/api/routes/reports.py`.

## What is explicitly deferred

Per the product spec, this build does **not** implement: embeddings,
vector similarity search, campaign clustering, mutation detection, campaign
evolution timelines, evolution-driver analysis, or any predictive model.
Building fake versions of these (e.g. a hardcoded "76% confidence" number)
would misrepresent the system's actual capabilities and was intentionally
avoided -- the foundation must be real and extensible, not a demo illusion.

## Privacy model for future community data

`CommunityReport` is deliberately a separate, sanitized table from
`Incident` (see `app/utils/sanitize.py`). When campaigns are introduced, a
future `campaign_id` foreign key should be added to `CommunityReport` (or a
new `incident_campaigns` join table), not to the private `Incident` table --
keeping the private/public boundary at the same seam it's at today.
