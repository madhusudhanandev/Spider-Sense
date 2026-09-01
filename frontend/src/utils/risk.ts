import type { RiskLevel } from "../types";

export const RISK_COLORS: Record<RiskLevel, string> = {
  LOW: "#4ADE80",
  MEDIUM: "#FBBF24",
  HIGH: "#F97316",
  CRITICAL: "#E8322B",
};

export const RISK_COPY: Record<RiskLevel, string> = {
  LOW: "Looks relatively safe, but stay alert.",
  MEDIUM: "Some warning signs here. Proceed carefully.",
  HIGH: "Strong warning signs. Treat this as a likely scam.",
  CRITICAL: "This matches a scam pattern closely. Do not act on it.",
};

export function formatCategory(category?: string | null): string {
  if (!category) return "Unclassified";
  return category
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
