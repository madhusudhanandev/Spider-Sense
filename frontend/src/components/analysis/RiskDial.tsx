import type { RiskLevel } from "../../types";
import { RISK_COLORS } from "../../utils/risk";

interface Props {
  score: number;
  level: RiskLevel;
}

const RADIUS = 70;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function RiskDial({ score, level }: Props) {
  const color = RISK_COLORS[level];
  const offset = CIRCUMFERENCE * (1 - score / 100);

  return (
    <div className="relative flex h-48 w-48 items-center justify-center">
      <svg viewBox="0 0 160 160" className="h-full w-full -rotate-90">
        <circle cx="80" cy="80" r={RADIUS} fill="none" stroke="#232C40" strokeWidth="10" />
        <circle
          cx="80"
          cy="80"
          r={RADIUS}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 700ms ease-out" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-condensed text-5xl font-bold leading-none">{score}</span>
        <span className="mt-1 text-xs text-ink-muted">/ 100</span>
        <span
          className="mt-2 font-condensed text-sm font-semibold uppercase tracking-wide"
          style={{ color }}
        >
          {level} RISK
        </span>
      </div>
    </div>
  );
}
