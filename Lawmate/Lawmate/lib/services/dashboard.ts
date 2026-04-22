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

// Types for Citizen Dashboard
export interface CitizenDashboardStats {
  active_cases: number;
  pending_hearings: number;
  documents: number;
  top_lawyers: number;
}

export interface CitizenCase {
  id: string;
  status: string;
  type: string;
  progress: number;
  date: string;
  court: string;
  judge: string;
  next_action: string;
}

export interface CitizenRecommendation {
  title: string;
  description: string;
  action: string;
  type: "warning" | "success" | "info";
}

export interface NextHearing {
  case_id: string;
  date: string;
  time: string;
  court: string;
  judge: string;
}

export interface CitizenDashboardData {
  stats: CitizenDashboardStats;
  recent_cases: CitizenCase[];
  recommendations: CitizenRecommendation[];
  next_hearing: NextHearing;
  trends: {
    cases_this_month: number;
    documents_this_month: number;
    next_hearing_date: string;
  };
}

// Types for Lawyer Dashboard
export interface LawyerDashboardMetrics {
  active_cases: number;
  win_rate: number;
  pending_hearings: number;
  total_clients: number;
}

export interface UrgentCase {
  id: string;
  priority: "High" | "Medium" | "Low";
  client_name: string;
  deadline: string;
  hours_billed: number;
  progress: number;
}

export interface PerformanceMetrics {
  cases_won: number;
  cases_total: number;
  avg_resolution_months: number;
  client_rating: number;
}

export interface LawyerDashboardData {
  metrics: LawyerDashboardMetrics;
  urgent_cases: UrgentCase[];
  performance: PerformanceMetrics;
  trends: {
    cases_this_month: number;
    win_rate_trend: string;
    next_hearing_date: string;
    active_clients: number;
  };
}

// API Functions
export async function getCitizenDashboard(): Promise<CitizenDashboardData> {
  const user = getLoggedInUser();
  const params = user.id ? `?citizen_id=${encodeURIComponent(user.id)}` : "";
  console.log(`📡 Calling /api/dashboard/citizen${params}...`)
  try {
    const data = await api.get<CitizenDashboardData>(`/api/dashboard/citizen${params}`);
    console.log("✅ Citizen dashboard API response:", data)
    return data;
  } catch (error) {
    console.error("❌ Error calling /api/dashboard/citizen:", error)
    throw error;
  }
}

export async function getLawyerDashboard(): Promise<LawyerDashboardData> {
  const user = getLoggedInUser();
  const params = user.id ? `?lawyer_id=${encodeURIComponent(user.id)}` : "";
  console.log(`📡 Calling /api/dashboard/lawyer${params}...`)
  try {
    const data = await api.get<LawyerDashboardData>(`/api/dashboard/lawyer${params}`);
    console.log("✅ Lawyer dashboard API response:", data)
    return data;
  } catch (error) {
    console.error("❌ Error calling /api/dashboard/lawyer:", error)
    throw error;
  }
}

