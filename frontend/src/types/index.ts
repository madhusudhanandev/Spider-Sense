export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface TacticOut {
  name: string;
  confidence: number;
  evidence?: string | null;
}

export interface IndicatorOut {
  type: string;
  value: string;
  confidence?: number | null;
  source?: string | null;
}

export interface URLSignal {
  type: string;
  severity: "low" | "medium" | "high";
  description: string;
}

export interface URLAnalysisResult {
  url: string;
  domain?: string | null;
  is_https?: boolean | null;
  risk_score: number;
  signals: URLSignal[];
  provider: string;
}

export interface RiskBreakdown {
  text_social_engineering: number;
  url_signals: number;
  credential_or_payment_request: number;
  community_evidence: number;
  other: number;
}

export interface RecommendedAction {
  label: string;
  kind: "avoid" | "protect" | "report";
}

export interface AnalysisResult {
  incident_id: string;
  scam_detected: boolean;
  confidence: number;
  risk_score: number;
  risk_level: RiskLevel;
  risk_breakdown: RiskBreakdown;
  scam_category: string;
  claimed_organization?: string | null;
  language?: string | null;
  platform?: string | null;
  tactics: TacticOut[];
  indicators: IndicatorOut[];
  requested_actions: string[];
  url_analysis: URLAnalysisResult[];
  summary: string;
  explanation: string;
  recommended_actions: RecommendedAction[];
  related_incident_count: number;
}

export interface IncidentOut {
  id: string;
  created_at: string;
  updated_at: string;
  input_type: string;
  platform?: string | null;
  language?: string | null;
  raw_text?: string | null;
  transcription?: string | null;
  risk_score?: number | null;
  risk_level?: RiskLevel | null;
  scam_category?: string | null;
  claimed_organization?: string | null;
  ai_summary?: string | null;
  ai_explanation?: string | null;
  community_visible: boolean;
  tactics: TacticOut[];
  indicators: IndicatorOut[];
  evidence: { id: string; evidence_type: string; storage_uri?: string | null; mime_type?: string | null; created_at: string }[];
  fingerprint?: {
    target_organization?: string | null;
    scam_category?: string | null;
    platform?: string | null;
    language?: string | null;
    delivery_method?: string | null;
    tactics: string[];
    requested_actions: string[];
  } | null;
}

export interface CommunityReportOut {
  id: string;
  incident_id: string;
  platform?: string | null;
  language?: string | null;
  scam_category?: string | null;
  claimed_organization?: string | null;
  risk_level?: RiskLevel | null;
  tactics: string[];
  requested_action?: string | null;
  suspicious_domain?: string | null;
  suspicious_phone?: string | null;
  ai_summary?: string | null;
  report_count: number;
  created_at: string;
}

export interface TrendingThreat {
  scam_category: string;
  claimed_organization?: string | null;
  report_count: number;
  risk_level: RiskLevel;
}

export interface CommunityStats {
  total_reports: number;
  reports_today: number;
  high_risk_reports: number;
  top_category?: string | null;
  category_distribution: Record<string, number>;
  platform_distribution: Record<string, number>;
  language_distribution: Record<string, number>;
  trending_threats: TrendingThreat[];
}

export interface RelatedIncidentsResult {
  resembles_count: number;
  common_characteristics: string[];
  related_report_ids: string[];
  confidence_note: string;
}

export interface CampaignOut {
  id: string;
  created_at: string;
  updated_at: string;
  label: string;
  scam_category?: string | null;
  target_organization?: string | null;
  platforms_seen: string[];
  languages_seen: string[];
  delivery_methods_seen: string[];
  report_count: number;
}

export interface CampaignEventOut {
  id: string;
  event_type: string;
  previous_values: string[];
  new_value: string;
  created_at: string;
}

export interface CampaignDetailOut extends CampaignOut {
  events: CampaignEventOut[];
}
