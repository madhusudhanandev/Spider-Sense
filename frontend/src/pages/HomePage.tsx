import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageShell from "../components/layout/PageShell";
import AnalyzeInputPanel from "../components/analysis/AnalyzeInputPanel";
import ScanningOverlay from "../components/analysis/ScanningOverlay";
import SpiderEmblem from "../components/common/SpiderEmblem";
import { api } from "../services/api";

export default function HomePage() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handle(promise: Promise<{ incident_id: string }>) {
    setBusy(true);
    setError(null);
    try {
      const result = await promise;
      navigate(`/incidents/${result.incident_id}/result`, { state: { result } });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
      setBusy(false);
    }
  }

  return (
    <PageShell>
      <section className="web-field mb-12 rounded-xl border border-navy-border bg-gradient-to-b from-navy-surface/60 to-transparent px-8 py-14 text-center">
        <SpiderEmblem className="mx-auto mb-5 h-12 w-12 text-spider-red" />
        <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">Spider-Sense AI</h1>
        <p className="mx-auto mt-3 max-w-xl text-ink-muted">
          Drop something suspicious and I&rsquo;ll investigate it — a message, a link, a screenshot, or a voice
          note.
        </p>
        <p className="mt-1 font-condensed text-sm uppercase tracking-widest text-web-blue">
          Detect. Explain. Protect.
        </p>
      </section>

      <div className="mx-auto max-w-2xl">
        {busy ? (
          <div className="panel web-field">
            <ScanningOverlay />
          </div>
        ) : (
          <AnalyzeInputPanel
            busy={busy}
            onSubmitText={(text) => handle(api.analyzeText(text))}
            onSubmitUrl={(url) => handle(api.analyzeUrl(url))}
            onSubmitImage={(file) => handle(api.analyzeImage(file))}
            onSubmitAudio={(file) => handle(api.analyzeAudio(file))}
          />
        )}
        {error && <p className="mt-4 text-center text-sm text-spider-red">{error}</p>}
      </div>
    </PageShell>
  );
}