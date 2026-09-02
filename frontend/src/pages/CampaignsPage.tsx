import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import { api } from "../services/api";
import type { CampaignOut, EvolutionPatternsResult } from "../types";
import { formatCategory } from "../utils/risk";
import intelligenceBg from "../assets/intelligence-bg.png";
import PageBackground from "../components/layout/PageBackground";

function transitionLabel(eventType: string): string {
  return eventType === "new_platform"
    ? "platform"
    : eventType === "new_language"
      ? "language"
      : eventType;
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignOut[]>([]);
  const [patterns, setPatterns] =
    useState<EvolutionPatternsResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getCampaigns(), api.getEvolutionPatterns()])
      .then(([c, p]) => {
        setCampaigns(c);
        setPatterns(p);
      })
      .catch(() => {
        setCampaigns([]);
        setPatterns(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageBackground image={intelligenceBg}>
      <PageShell>
        <div className="mb-10 web-field rounded-xl border border-navy-border bg-navy-surface/40 px-8 py-10 text-center">
          <h1 className="font-display text-3xl font-semibold">
            Campaign Intelligence
          </h1>

          <p className="mx-auto mt-2 max-w-xl text-ink-muted">
            Related community reports automatically grouped by scam pattern
            and tracked as they evolve across platforms and languages.
          </p>
        </div>

        {loading && (
          <p className="text-center text-ink-muted">
            Following the web…
          </p>
        )}

        {!loading &&
          patterns &&
          patterns.campaigns_with_mutations > 0 && (
            <section className="mb-10 panel p-5">
              <h2 className="mb-2 font-display text-lg font-semibold">
                Observed evolution patterns
              </h2>

              {patterns.common_transitions.length > 0 && (
                <ul className="space-y-1.5 text-sm text-ink-primary">
                  {patterns.common_transitions.map((t, i) => (
                    <li key={i}>
                      &bull; {transitionLabel(t.event_type)} change{" "}
                      <span className="font-mono">
                        {t.from_value}
                      </span>{" "}
                      &rarr;{" "}
                      <span className="font-mono">
                        {t.to_value}
                      </span>
                      <span className="text-ink-muted">
                        {" "}
                        — seen {t.occurrence_count}x
                      </span>
                    </li>
                  ))}
                </ul>
              )}

              {patterns.median_time_to_first_mutation_hours != null && (
                <p className="mt-2 text-sm text-ink-muted">
                  Median time to first mutation:{" "}
                  {patterns.median_time_to_first_mutation_hours.toFixed(1)}{" "}
                  hours
                </p>
              )}

              <p className="mt-3 text-xs italic text-ink-faint">
                {patterns.sample_size_note}
              </p>
            </section>
          )}

        {!loading && campaigns.length === 0 && (
          <div className="web-field panel p-10 text-center">
            <p className="font-condensed text-sm uppercase tracking-wide text-ink-muted">
              Your Spider-Sense is quiet&hellip;
            </p>

            <p className="mt-1 text-ink-faint">
              No campaigns detected yet — share a few similar incidents to
              the community to see clustering in action.
            </p>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          {campaigns.map((c) => (
            <Link
              key={c.id}
              to={`/campaigns/${c.id}`}
              className="panel block p-5 transition-colors hover:border-web-blue"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-display text-lg font-semibold">
                  {c.label || formatCategory(c.scam_category)}
                </h3>

                <span className="font-condensed text-2xl font-bold text-spider-red">
                  {c.report_count}
                </span>
              </div>

              <p className="text-sm text-ink-muted">
                {formatCategory(c.scam_category)}
              </p>

              {c.platforms_seen.length > 0 && (
                <p className="mt-3 text-xs text-ink-faint">
                  Seen on: {c.platforms_seen.join(", ")}
                </p>
              )}

              {c.is_emerging && (
                <span className="mt-3 inline-block rounded-full border border-spider-red/40 bg-spider-red/10 px-2.5 py-1 text-xs font-medium text-spider-red">
                  🔥 Emerging — {c.recent_report_count} reports recently
                </span>
              )}
            </Link>
          ))}
        </div>
      </PageShell>
    </PageBackground>
  );
}