import { api } from "../api";

function getLoggedInUser(): { id?: string; userType?: string } {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem("user");
    if (!raw) return {};
    const parsed = JSON.parse(raw) as { id?: string; userType?: string };
    return parsed || {};
  } catch {
    return {};
  }
}

// Types for Lawyer Analytics
export interface CaseOutcome {
  month: string;
  won: number;
  lost: number;
  pending: number;
}

export interface CaseTypePerformance {
  type: string;
  count: number;
  winRate: number;
}

export interface SummaryMetrics {
  avg_resolution_time_months: number;
  client_satisfaction: number;
  case_success_rate: number;
  total_cases: number;
  cases_won: number;
  cases_lost: number;
  cases_pending: number;
}

export interface Trends {
  resolution_time_change: number;  // months
  satisfaction_change: number;  // points
  success_rate_change: number;  // percentage
}

export interface LawyerAnalyticsData {
  case_outcomes: CaseOutcome[];
  case_type_performance: CaseTypePerformance[];
  summary_metrics: SummaryMetrics;
  trends: Trends;
}

// API Functions
export async function getLawyerAnalytics(): Promise<LawyerAnalyticsData> {
  const user = getLoggedInUser();
  const params = user.id ? `?lawyer_id=${encodeURIComponent(user.id)}` : "";
  console.log(`📡 Calling /api/analytics/lawyer${params}...`);
  try {
    const data = await api.get<LawyerAnalyticsData>(`/api/analytics/lawyer${params}`);
    console.log("✅ Lawyer analytics API response:", data);
    return data;
  } catch (error) {
    console.error("❌ Error calling /api/analytics/lawyer:", error);
    throw error;
  }
}

