import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import { api } from "../services/api";
import type { CampaignOut } from "../types";
import { formatCategory } from "../utils/risk";

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignOut[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getCampaigns()
      .then(setCampaigns)
      .catch(() => setCampaigns([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageShell>
      <div className="mb-10 web-field rounded-xl border border-navy-border bg-navy-surface/40 px-8 py-10 text-center">
        <h1 className="font-display text-3xl font-semibold">Campaign Intelligence</h1>
        <p className="mx-auto mt-2 max-w-xl text-ink-muted">
          Related community reports automatically grouped by scam pattern and tracked as they evolve across
          platforms and languages.
        </p>
      </div>

      {loading && <p className="text-center text-ink-muted">Following the web…</p>}

      {!loading && campaigns.length === 0 && (
        <div className="web-field panel p-10 text-center">
          <p className="font-condensed text-sm uppercase tracking-wide text-ink-muted">
            Your Spider-Sense is quiet&hellip;
          </p>
          <p className="mt-1 text-ink-faint">
            No campaigns detected yet — share a few similar incidents to the community to see clustering in
            action.
          </p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {campaigns.map((c) => (
          <Link key={c.id} to={`/campaigns/${c.id}`} className="panel block p-5 transition-colors hover:border-web-blue">
            <div className="flex items-center justify-between">
              <h3 className="font-display text-lg font-semibold">{c.label || formatCategory(c.scam_category)}</h3>
              <span className="font-condensed text-2xl font-bold text-spider-red">{c.report_count}</span>
            </div>
            <p className="text-sm text-ink-muted">{formatCategory(c.scam_category)}</p>
            {c.platforms_seen.length > 0 && (
              <p className="mt-3 text-xs text-ink-faint">Seen on: {c.platforms_seen.join(", ")}</p>
            )}
          </Link>
        ))}
      </div>
    </PageShell>
  );
}