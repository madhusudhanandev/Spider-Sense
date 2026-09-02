import { useEffect, useState } from "react";
import SpiderEmblem from "../common/SpiderEmblem";

const STAGES = [
  "Extracting evidence…",
  "Scanning indicators…",
  "Analyzing social-engineering tactics…",
  "Calculating threat level…",
];

/**
 * Cinematic scanning overlay shown while an analysis request is in flight.
 * Purely presentational -- cycles through stage labels on a timer, it has
 * no knowledge of the real request's progress (the backend doesn't stream
 * incremental status). Capped at a few seconds of stages so it never
 * makes the user wait longer than the request itself would anyway.
 */
export default function ScanningOverlay() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, STAGES.length - 1));
    }, 700);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-10">
      <div className="relative flex h-28 w-28 items-center justify-center">
        <div className="absolute inset-0 animate-ping rounded-full border border-web-blue/40" />
        <div className="absolute inset-2 animate-ping rounded-full border border-spider-red/30 [animation-delay:200ms]" />
        <div className="absolute inset-0 rounded-full border border-navy-border" />
        <SpiderEmblem className="h-10 w-10 text-spider-red" />
      </div>
      <p className="mt-6 font-condensed text-sm uppercase tracking-widest text-web-blue">
        Spider-Sense Engaged
      </p>
      <p className="mt-2 text-sm text-ink-muted transition-opacity duration-300">{STAGES[stageIndex]}</p>
    </div>
  );
}