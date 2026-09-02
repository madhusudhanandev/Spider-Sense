import { useEffect, useState } from "react";
import PageShell from "../components/layout/PageShell";
import { api } from "../services/api";
import type { CommunityReportOut, CommunityStats } from "../types";
import { formatCategory } from "../utils/risk";
import communityBg from "../assets/community-bg.png";
import PageBackground from "../components/layout/PageBackground";

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="panel p-5">
      <div className="text-xs uppercase tracking-wide text-ink-faint">
        {label}
      </div>
      <div className="mt-1 font-condensed text-3xl font-bold">{value}</div>
    </div>
  );
}

export default function CommunityPage() {
  const [stats, setStats] = useState<CommunityStats | null>(null);
  const [reports, setReports] = useState<CommunityReportOut[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getCommunityStats(), api.getCommunityReports()])
      .then(([s, r]) => {
        setStats(s);
        setReports(r);
      })
      .catch(() => {
        setStats(null);
        setReports([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageBackground image={communityBg}>
      <PageShell>
        <div className="mb-10 web-field rounded-xl border border-navy-border bg-navy-surface/40 px-8 py-10 text-center">
          <h1 className="font-display text-3xl font-semibold">
            The Spider Network
          </h1>

          <p className="mt-2 text-ink-muted">
            Collective scam intelligence from the community.
          </p>
        </div>

        {loading && (
          <p className="text-center text-ink-muted">
            Checking the threat network…
          </p>
        )}

        {!loading && stats && (
          <div className="mb-10 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <StatCard
              label="Total Reports"
              value={stats.total_reports}
            />

            <StatCard
              label="Reports Today"
              value={stats.reports_today}
            />

            <StatCard
              label="High-Risk Reports"
              value={stats.high_risk_reports}
            />

            <StatCard
              label="Most Common"
              value={formatCategory(stats.top_category) || "—"}
            />
          </div>
        )}

        {!loading &&
          stats &&
          stats.trending_threats.length > 0 && (
            <section className="mb-10">
              <h2 className="mb-4 font-display text-xl font-semibold">
                Trending Threats
              </h2>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {stats.trending_threats.map((t, i) => (
                  <div key={i} className="panel p-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">
                        {t.claimed_organization ??
                          formatCategory(t.scam_category)}
                      </h3>

                      <span className="text-spider-red">
                        🔥
                      </span>
                    </div>

                    <p className="text-sm text-ink-muted">
                      {formatCategory(t.scam_category)}
                    </p>

                    <p className="mt-2 font-condensed text-sm font-semibold uppercase tracking-wide text-ink-muted">
                      {t.report_count} reports &middot; {t.risk_level}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          )}

        <section>
          <h2 className="mb-4 font-display text-xl font-semibold">
            Recent Reports
          </h2>

          {!loading && reports.length === 0 && (
            <div className="web-field panel p-10 text-center">
              <p className="font-condensed text-sm uppercase tracking-wide text-ink-muted">
                Your Spider-Sense is quiet…
              </p>

              <p className="mt-1 text-ink-faint">
                No matching threats detected yet.
              </p>
            </div>
          )}

          <div className="space-y-3">
            {reports.map((r) => (
              <div key={r.id} className="panel p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-semibold">
                    {formatCategory(r.scam_category)}
                  </h3>

                  <span className="text-xs font-medium text-ink-muted">
                    {r.platform ?? "Unknown platform"} &middot;{" "}
                    {r.language ?? "Unknown language"}
                  </span>
                </div>

                {r.claimed_organization && (
                  <p className="text-sm text-ink-muted">
                    Claims to be from {r.claimed_organization}
                  </p>
                )}

                {r.ai_summary && (
                  <p className="mt-2 text-sm text-ink-primary">
                    {r.ai_summary}
                  </p>
                )}

                {r.suspicious_domain && (
                  <p className="mt-2 font-mono text-xs text-spider-red">
                    {r.suspicious_domain}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      </PageShell>
    </PageBackground>
  );
}