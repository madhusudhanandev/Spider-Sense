import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import { IndicatorCard } from "../components/analysis/IndicatorCards";
import TacticCard from "../components/analysis/TacticCard";
import { api } from "../services/api";
import type { IncidentOut, RelatedIncidentsResult } from "../types";
import { formatCategory } from "../utils/risk";

export default function IncidentDetailsPage() {
  const { incidentId } = useParams();
  const [incident, setIncident] = useState<IncidentOut | null>(null);
  const [related, setRelated] = useState<RelatedIncidentsResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!incidentId) return;
    setLoading(true);
    Promise.all([api.getIncident(incidentId), api.getRelatedIncidents(incidentId)])
      .then(([i, r]) => {
        setIncident(i);
        setRelated(r);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load this incident."))
      .finally(() => setLoading(false));
  }, [incidentId]);

  if (loading) {
    return (
      <PageShell>
        <p className="text-center text-ink-muted">Following the digital trail&hellip;</p>
      </PageShell>
    );
  }

  if (error || !incident) {
    return (
      <PageShell>
        <p className="text-center text-spider-red">{error ?? "Incident not found."}</p>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="mb-8">
        <p className="font-condensed text-sm uppercase tracking-widest text-ink-muted">
          Incident #{incident.id.slice(0, 8).toUpperCase()}
        </p>
        <h1 className="mt-1 font-display text-2xl font-semibold">{formatCategory(incident.scam_category)}</h1>
        <p className="text-ink-muted">
          {incident.risk_level ?? "UNSCORED"} &middot; {incident.risk_score ?? "—"}/100 &middot;{" "}
          {new Date(incident.created_at).toLocaleString()}
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="space-y-8 lg:col-span-2">
          {incident.ai_explanation && (
            <section>
              <h2 className="mb-2 font-display text-lg font-semibold">Risk analysis</h2>
              <p className="text-sm text-ink-muted">{incident.ai_explanation}</p>
            </section>
          )}

          {incident.tactics.length > 0 && (
            <section>
              <h2 className="mb-3 font-display text-lg font-semibold">Psychological tactics</h2>
              <div className="grid gap-3 sm:grid-cols-2">
                {incident.tactics.map((t, i) => (
                  <TacticCard key={i} tactic={t} />
                ))}
              </div>
            </section>
          )}

          {incident.indicators.length > 0 && (
            <section>
              <h2 className="mb-3 font-display text-lg font-semibold">Indicators</h2>
              <div className="grid gap-2 sm:grid-cols-2">
                {incident.indicators.map((ind, i) => (
                  <IndicatorCard key={i} indicator={ind} />
                ))}
              </div>
            </section>
          )}
        </div>

        <aside className="space-y-6">
          <div className="panel p-5">
            <h3 className="mb-1.5 font-display text-base font-semibold">Community status</h3>
            <p className="text-sm text-ink-muted">
              {incident.community_visible ? "Shared with the community." : "Not shared with the community."}
            </p>
          </div>

          {related && (
            <div className="panel p-5">
              <h3 className="mb-1.5 font-display text-base font-semibold">Your Spider-Sense found connections</h3>
              {related.resembles_count > 0 ? (
                <>
                  <p className="text-sm text-ink-muted">
                    This incident resembles <strong className="text-ink-primary">{related.resembles_count}</strong>{" "}
                    previous reports.
                  </p>
                  {related.common_characteristics.length > 0 && (
                    <ul className="mt-3 space-y-1 text-sm text-ink-primary">
                      {related.common_characteristics.map((c, i) => (
                        <li key={i}>&bull; {c}</li>
                      ))}
                    </ul>
                  )}
                  <p className="mt-3 text-xs italic text-ink-faint">{related.confidence_note}</p>
                </>
              ) : (
                <p className="text-sm text-ink-faint">No related reports found yet.</p>
              )}
            </div>
          )}
        </aside>
      </div>
    </PageShell>
  );
}
