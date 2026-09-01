import type {
  AnalysisResult,
  CampaignDetailOut,
  CampaignOut,
  CommunityReportOut,
  CommunityStats,
  IncidentOut,
  RelatedIncidentsResult,
} from "../types";

const BASE = "/api";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore parse failure */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  analyzeText: (text: string, platform?: string, language_hint?: string) =>
    fetch(`${BASE}/analyze/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, platform, language_hint }),
    }).then((r) => handle<AnalysisResult>(r)),

  analyzeUrl: (url: string, context_text?: string) =>
    fetch(`${BASE}/analyze/url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, context_text }),
    }).then((r) => handle<AnalysisResult>(r)),

  analyzeImage: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${BASE}/analyze/image`, { method: "POST", body: form }).then((r) => handle<AnalysisResult>(r));
  },

  analyzeAudio: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${BASE}/analyze/audio`, { method: "POST", body: form }).then((r) => handle<AnalysisResult>(r));
  },

  getIncident: (id: string) => fetch(`${BASE}/incidents/${id}`).then((r) => handle<IncidentOut>(r)),

  shareToCommunity: (incidentId: string) =>
    fetch(`${BASE}/incidents/${incidentId}/community-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ consent: true }),
    }).then((r) => handle<CommunityReportOut>(r)),

  getCommunityReports: (params?: { category?: string; platform?: string }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return fetch(`${BASE}/community/reports${qs ? `?${qs}` : ""}`).then((r) => handle<CommunityReportOut[]>(r));
  },

  getCommunityStats: () => fetch(`${BASE}/community/stats`).then((r) => handle<CommunityStats>(r)),

    getRelatedIncidents: (incidentId: string) =>
    fetch(`${BASE}/community/related/${incidentId}`).then((r) => handle<RelatedIncidentsResult>(r)),

  getCampaigns: () => fetch(`${BASE}/campaigns`).then((r) => handle<CampaignOut[]>(r)),

  getCampaign: (id: string) => fetch(`${BASE}/campaigns/${id}`).then((r) => handle<CampaignDetailOut>(r)),
};
