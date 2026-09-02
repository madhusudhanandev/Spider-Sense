import { useRef, useState } from "react";

export type InputTab = "text" | "url" | "image" | "audio";

interface Props {
  onSubmitText: (text: string) => void;
  onSubmitUrl: (url: string) => void;
  onSubmitImage: (file: File) => void;
  onSubmitAudio: (file: File) => void;
  busy: boolean;
}

const TABS: { key: InputTab; label: string }[] = [
  { key: "text", label: "Text" },
  { key: "url", label: "URL" },
  { key: "image", label: "Screenshot" },
  { key: "audio", label: "Audio" },
];

export default function AnalyzeInputPanel({
  onSubmitText,
  onSubmitUrl,
  onSubmitImage,
  onSubmitAudio,
  busy,
}: Props) {
  const [tab, setTab] = useState<InputTab>("text");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const imageInput = useRef<HTMLInputElement>(null);
  const audioInput = useRef<HTMLInputElement>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);

  function handleSubmit() {
    if (busy) return;

    if (tab === "text" && text.trim()) {
      onSubmitText(text.trim());
    }

    if (tab === "url" && url.trim()) {
      onSubmitUrl(url.trim());
    }

    if (tab === "image" && imageFile) {
      onSubmitImage(imageFile);
    }

    if (tab === "audio" && audioFile) {
      onSubmitAudio(audioFile);
    }
  }

  const canSubmit =
    (tab === "text" && text.trim().length > 0) ||
    (tab === "url" && url.trim().length > 0) ||
    (tab === "image" && !!imageFile) ||
    (tab === "audio" && !!audioFile);

  return (
    <div className="panel web-field border border-navy-border/70 bg-navy-surface/25 p-6 backdrop-blur-[2px]">
      <div className="mb-5 flex gap-1 border-b border-navy-border/60">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
              tab === t.key
                ? "border-spider-red text-ink-primary"
                : "border-transparent text-ink-muted hover:text-ink-primary"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "text" && (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste the suspicious message here — SMS, WhatsApp, email, or DM."
          rows={6}
          className="w-full resize-none rounded-md border border-navy-border/70 bg-void/30 p-4 text-sm text-ink-primary placeholder:text-ink-faint focus:border-web-blue focus:outline-none"
        />
      )}

      {tab === "url" && (
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://suspicious-link.example"
          className="w-full rounded-md border border-navy-border/70 bg-void/30 p-4 text-sm text-ink-primary placeholder:text-ink-faint focus:border-web-blue focus:outline-none"
        />
      )}

      {tab === "image" && (
        <div
          onClick={() => imageInput.current?.click()}
          className="flex cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-navy-border/70 bg-void/30 p-10 text-center hover:border-web-blue"
        >
          <input
            ref={imageInput}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            className="hidden"
            onChange={(e) =>
              setImageFile(e.target.files?.[0] ?? null)
            }
          />

          <p className="text-sm text-ink-primary">
            {imageFile
              ? imageFile.name
              : "Upload a screenshot"}
          </p>

          <p className="mt-1 text-xs text-ink-muted">
            PNG, JPEG, or WebP — up to 10MB
          </p>
        </div>
      )}

      {tab === "audio" && (
        <div
          onClick={() => audioInput.current?.click()}
          className="flex cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-navy-border/70 bg-void/30 p-10 text-center hover:border-web-blue"
        >
          <input
            ref={audioInput}
            type="file"
            accept="audio/mpeg,audio/wav,audio/mp4,audio/ogg"
            className="hidden"
            onChange={(e) =>
              setAudioFile(e.target.files?.[0] ?? null)
            }
          />

          <p className="text-sm text-ink-primary">
            {audioFile
              ? audioFile.name
              : "Upload a voice recording"}
          </p>

          <p className="mt-1 text-xs text-ink-muted">
            MP3, WAV, M4A, or OGG — up to 10MB
          </p>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={!canSubmit || busy}
        className="mt-5 w-full rounded-md bg-spider-red py-3 font-condensed text-base font-semibold uppercase tracking-wide text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {busy ? "Scanning…" : "Activate Spider-Sense"}
      </button>
    </div>
  );
}