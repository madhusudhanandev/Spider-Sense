import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import { api } from "../services/api";
import type { CampaignDetailOut, SuggestedNextMutation } from "../types";
import { formatCategory } from "../utils/risk";

function eventLabel(eventType: string): string {
  switch (eventType) {
    case "new_platform":
      return "New platform observed";
    case "new_language":
      return "New language observed";
    case "new_delivery_method":
      return "New delivery method observed";
    default:
      return eventType;
  }
}

export default function CampaignDetailPage() {
  const { campaignId } = useParams();
  const [campaign, setCampaign] = useState<CampaignDetailOut | null>(null);
  const [suggestion, setSuggestion] = useState<SuggestedNextMutation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!campaignId) return;
    Promise.all([api.getCampaign(campaignId), api.getSuggestedNextMutation(campaignId)])
      .then(([c, s]) => {
        setCampaign(c);
        setSuggestion(s);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load this campaign."))
      .finally(() => setLoading(false));
  }, [campaignId]);

  if (loading) {
    return (
      <PageShell>
        <p className="text-center text-ink-muted">Following the digital trail&hellip;</p>
      </PageShell>
    );
  }

  if (error || !campaign) {
    return (
      <PageShell>
        <p className="text-center text-spider-red">{error ?? "Campaign not found."}</p>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="mb-8">
        <p className="font-condensed text-sm uppercase tracking-widest text-ink-muted">
          Campaign #{campaign.id.slice(0, 8).toUpperCase()}
        </p>
        <h1 className="mt-1 font-display text-2xl font-semibold">{campaign.label}</h1>
        <p className="text-ink-muted">
          {formatCategory(campaign.scam_category)} &middot; {campaign.report_count} related reports
        </p>
        {campaign.is_emerging && (
          <span className="mt-2 inline-block rounded-full border border-spider-red/40 bg-spider-red/10 px-2.5 py-1 text-xs font-medium text-spider-red">
            🔥 Emerging — {campaign.recent_report_count} reports recently
          </span>
        )}
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="space-y-8 lg:col-span-2">
          <section>
            <h2 className="mb-3 font-display text-lg font-semibold">Observed evolution</h2>
            {campaign.events.length === 0 ? (
              <p className="text-sm text-ink-faint">
                No mutations observed yet — every report so far has used the same platform and language.
              </p>
            ) : (
              <div className="space-y-3 border-l-2 border-navy-border pl-5">
                {campaign.events.map((e) => (
                  <div key={e.id} className="relative">
                    <div className="absolute -left-[26px] top-1.5 h-2.5 w-2.5 rounded-full bg-spider-red" />
                    <p className="text-xs text-ink-faint">{new Date(e.created_at).toLocaleString()}</p>
                    <p className="text-sm text-ink-primary">
                      <span className="font-medium">{eventLabel(e.event_type)}:</span> {e.new_value}
                      {e.previous_values.length > 0 && (
                        <span className="text-ink-muted"> (previously: {e.previous_values.join(", ")})</span>
                      )}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          {suggestion && (
            <section>
              <h2 className="mb-2 font-display text-lg font-semibold">What happened next in similar cases</h2>
              <p className="mb-3 text-xs text-ink-faint">
                This is a lookup over historical cases, not a prediction — Spider-Sense does not forecast what
                this specific campaign will do next.
              </p>
              {suggestion.distribution.length > 0 ? (
                <ul className="space-y-1.5 text-sm text-ink-primary">
                  {suggestion.distribution.map((d, i) => (
                    <li key={i}>
                      &bull; {eventLabel(d.event_type)} — {d.occurrence_count} case
                      {d.occurrence_count !== 1 ? "s" : ""}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-ink-faint">No comparable historical cases found.</p>
              )}
              <p className="mt-3 text-xs italic text-ink-faint">{suggestion.note}</p>
            </section>
          )}
        </div>

        <aside className="space-y-6">
          <div className="panel p-5">
            <h3 className="mb-3 font-display text-base font-semibold">Campaign profile</h3>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-xs uppercase tracking-wide text-ink-faint">Platforms seen</dt>
                <dd className="text-ink-primary">{campaign.platforms_seen.join(", ") || "—"}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-ink-faint">Languages seen</dt>
                <dd className="text-ink-primary">{campaign.languages_seen.join(", ") || "—"}</dd>
              </div>
              {campaign.target_organization && (
                <div>
                  <dt className="text-xs uppercase tracking-wide text-ink-faint">Claimed organization</dt>
                  <dd className="text-ink-primary">{campaign.target_organization}</dd>
                </div>
              )}
            </dl>
          </div>
        </aside>
      </div>
    </PageShell>
  );
}