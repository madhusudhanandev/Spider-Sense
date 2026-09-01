import type { TacticOut } from "../../types";

function label(name: string): string {
  return name
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export default function TacticCard({ tactic }: { tactic: TacticOut }) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-ink-primary">{label(tactic.name)}</h4>
        <span className="text-sm font-medium text-spider-red">{Math.round(tactic.confidence * 100)}%</span>
      </div>
      {tactic.evidence && <p className="mt-1.5 text-sm text-ink-muted">{tactic.evidence}</p>}
    </div>
  );
}
