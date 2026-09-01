import { useState } from "react";
import { useLocation, useParams, Navigate, Link } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import RiskDial from "../components/analysis/RiskDial";
import TacticCard from "../components/analysis/TacticCard";
import { IndicatorCard, UrlAnalysisCard } from "../components/analysis/IndicatorCards";
import { api } from "../services/api";
import type { AnalysisResult } from "../types";
import { RISK_COPY, formatCategory } from "../utils/risk";

export default function AnalysisResultPage() {
  const { state } = useLocation() as { state?: { result?: AnalysisResult } };
  const { incidentId } = useParams();
  const [shared, setShared] = useState(false);
  const [sharing, setSharing] = useState(false);

  if (!state?.result) {
    // Direct link / refresh without in-memory state: send to the incident
    // details page, which fetches from the API instead.
    return <Navigate to={`/incidents/${incidentId}`} replace />;
  }

  const result = state.result;

  async function share() {
    setSharing(true);
    try {
      await api.shareToCommunity(result.incident_id);
      setShared(true);
    } catch {
      // non-fatal for the demo; surface inline
    } finally {
      setSharing(false);
    }
  }

  return (
    <PageShell>
      <div className="mb-8 flex flex-col items-center text-center">
        <p className="font-condensed text-sm uppercase tracking-widest text-ink-muted">Spider-Sense Alert</p>
        <div className="mt-4">
          <RiskDial score={result.risk_score} level={result.risk_level} />
        </div>
        <h1 className="mt-4 font-display text-2xl font-semibold">{formatCategory(result.scam_category)}</h1>
        {result.claimed_organization && (
          <p className="text-ink-muted">Claims to be from {result.claimed_organization}</p>
        )}
        <p className="mt-2 max-w-md text-sm text-ink-muted">{RISK_COPY[result.risk_level]}</p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-8">
          <section>
            <h2 className="mb-3 font-display text-lg font-semibold">Why is your Spider-Sense alerting you?</h2>
            <p className="mb-4 text-sm text-ink-muted">{result.explanation}</p>
            {result.tactics.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {result.tactics.map((t, i) => (
                  <TacticCard key={i} tactic={t} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-ink-faint">No specific manipulation tactics were detected.</p>
            )}
          </section>

          {result.url_analysis.length > 0 && (
            <section>
              <h2 className="mb-3 font-display text-lg font-semibold">Spider-Sense technical scan</h2>
              <div className="space-y-3">
                {result.url_analysis.map((u, i) => (
                  <UrlAnalysisCard key={i} result={u} />
                ))}
              </div>
            </section>
          )}

          {result.indicators.length > 0 && (
            <section>
              <h2 className="mb-3 font-display text-lg font-semibold">Extracted indicators</h2>
              <div className="grid gap-2 sm:grid-cols-2">
                {result.indicators.map((ind, i) => (
                  <IndicatorCard key={i} indicator={ind} />
                ))}
              </div>
            </section>
          )}
        </div>

        <aside className="space-y-6">
          <div className="panel p-5">
            <h3 className="mb-3 font-display text-base font-semibold">What should you do now?</h3>
            <ul className="space-y-2 text-sm">
              {result.recommended_actions.map((a, i) => (
                <li key={i} className="flex gap-2 text-ink-primary">
                  <span className="text-spider-red">
                    {a.kind === "avoid" ? "\u2715" : a.kind === "report" ? "\u25B2" : "\u2713"}
                  </span>
                  {a.label}
                </li>
              ))}
            </ul>
          </div>

          {result.related_incident_count > 0 && (
            <div className="panel p-5">
              <h3 className="mb-1.5 font-display text-base font-semibold">Following the web</h3>
              <p className="text-sm text-ink-muted">
                This incident resembles <strong className="text-ink-primary">{result.related_incident_count}</strong>{" "}
                previous community reports.
              </p>
              <Link to="/community" className="mt-2 inline-block text-sm text-web-blue hover:underline">
                See the Spider Network &rarr;
              </Link>
            </div>
          )}

          <div className="panel p-5">
            <h3 className="mb-1.5 font-display text-base font-semibold">Add to the Spider Network</h3>
            <p className="mb-3 text-sm text-ink-muted">
              Help protect other users by sharing this sanitized threat intelligence. Your private information
              will not be publicly exposed.
            </p>
            <button
              onClick={share}
              disabled={shared || sharing}
              className="w-full rounded-md border border-spider-red py-2.5 text-sm font-medium text-spider-red transition-colors hover:bg-spider-red hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {shared ? "Shared with the community" : sharing ? "Sharing…" : "Share with the community"}
            </button>
          </div>
        </aside>
      </div>
    </PageShell>
  );
}
