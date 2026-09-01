import type { IndicatorOut, URLAnalysisResult } from "../../types";

export function IndicatorCard({ indicator }: { indicator: IndicatorOut }) {
  return (
    <div className="panel flex items-center justify-between px-4 py-3">
      <div>
        <div className="text-xs uppercase tracking-wide text-ink-faint">{indicator.type}</div>
        <div className="mt-0.5 break-all text-sm text-ink-primary">{indicator.value}</div>
      </div>
      {indicator.confidence != null && (
        <span className="ml-3 shrink-0 text-xs text-ink-muted">{Math.round(indicator.confidence * 100)}%</span>
      )}
    </div>
  );
}

const SEVERITY_COLOR: Record<string, string> = {
  low: "text-ink-muted",
  medium: "text-risk-medium",
  high: "text-spider-red",
};

export function UrlAnalysisCard({ result }: { result: URLAnalysisResult }) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between">
        <div className="min-w-0">
          <div className="text-xs uppercase tracking-wide text-ink-faint">Domain</div>
          <div className="truncate font-mono text-sm text-ink-primary">{result.domain ?? result.url}</div>
        </div>
        <div className="ml-3 shrink-0 text-right">
          <div className="text-xs uppercase tracking-wide text-ink-faint">Risk</div>
          <div className="font-condensed text-lg font-semibold">{result.risk_score}</div>
        </div>
      </div>
      {result.signals.length > 0 && (
        <ul className="mt-3 space-y-1.5 border-t border-navy-border pt-3">
          {result.signals.map((s, i) => (
            <li key={i} className={`text-sm ${SEVERITY_COLOR[s.severity] ?? "text-ink-muted"}`}>
              {s.description}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
