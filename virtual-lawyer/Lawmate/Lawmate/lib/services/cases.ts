import { api } from "../api";

// Types for Cases
export interface Case {
  id: string;
  case_type: string;
  status: string;
  next_hearing?: string;
  documents_count?: number;
  assigned_lawyer?: string | null;
  judge: string;
  court: string;
  filing_date?: string;
  progress?: number;
  // Lawyer-specific fields
  priority?: "High" | "Medium" | "Low";
  client_name?: string;
  deadline?: string;
  hours_billed?: number;
}

export interface CaseDetails extends Case {
  sections?: string[];
  police_station?: string;
  fir_number?: string;
  client_name?: string;
  description?: string;
  timeline?: Array<{
    date: string;
    event: string;
  }>;
}

export interface CasesResponse {
  cases: Case[];
  total: number;
  status_filter?: string;
}

// API Functions
export async function getCitizenCases(status?: string, userId?: string): Promise<CasesResponse> {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (userId) params.set("user_id", userId);
  // also send email to match cases created with email fallback
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("user");
    if (stored) {
      try {
        const u = JSON.parse(stored) as { email?: string };
        if (u.email) params.set("user_email", u.email);
      } catch {
        /* ignore */
      }
    }
  }
  const qs = params.toString() ? `?${params.toString()}` : "";
  console.log(`📡 Calling /api/cases/citizen${qs}...`);
  try {
    const data = await api.get<CasesResponse>(`/api/cases/citizen${qs}`);
    console.log(`✅ Citizen cases API response:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Error calling /api/cases/citizen:`, error);
    throw error;
  }
}

export async function getLawyerCases(status?: string, lawyerId?: string): Promise<CasesResponse> {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (lawyerId) params.set("lawyer_id", lawyerId);
  // also send email to match cases created with email fallback
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("user");
    if (stored) {
      try {
        const u = JSON.parse(stored) as { email?: string };
        if (u.email) params.set("lawyer_email", u.email);
      } catch {
        /* ignore */
      }
    }
  }
  const qs = params.toString() ? `?${params.toString()}` : "";
  console.log(`📡 Calling /api/cases/lawyer${qs}...`);
  try {
    const data = await api.get<CasesResponse>(`/api/cases/lawyer${qs}`);
    console.log(`✅ Lawyer cases API response:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Error calling /api/cases/lawyer:`, error);
    throw error;
  }
}

export async function getCaseDetails(caseId: string): Promise<CaseDetails> {
  return api.get<CaseDetails>(`/api/cases/${caseId}`);
}

export interface CreateCaseRequest {
  case_type: string;
  court: string;
  judge?: string;
  sections?: string[];
  police_station?: string;
  fir_number?: string;
  client_name?: string; // For lawyer cases
  description?: string;
  filing_date?: string;
  next_hearing?: string;
  priority?: "High" | "Medium" | "Low"; // For lawyer cases
  userId?: string;
  userEmail?: string;
  lawyerId?: string;
  lawyerEmail?: string;
}

export interface CreateCaseResponse {
  success: boolean;
  case: Case;
  message: string;
}

export async function createCase(
  data: CreateCaseRequest,
  userType: "citizen" | "lawyer" = "citizen"
): Promise<CreateCaseResponse> {
  console.log(`📡 Creating case (${userType})...`);
  try {
    // Pull logged-in user from localStorage
    let userId: string | undefined;
    let userEmail: string | undefined;
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("user");
      if (stored) {
        try {
          const u = JSON.parse(stored) as { id?: string; email?: string };
          userId = u.id;
          userEmail = u.email;
        } catch {
          /* ignore parse errors */
        }
      }
    }

    const params = new URLSearchParams({ user_type: userType });
    if (userType === "citizen" && userId) params.set("user_id", userId);
    if (userType === "citizen" && userEmail) params.set("user_email", userEmail);
    if (userType === "lawyer" && userId) params.set("lawyer_id", userId);
    if (userType === "lawyer" && userEmail) params.set("lawyer_email", userEmail);

    const body: CreateCaseRequest = {
      ...data,
      userId: userType === "citizen" ? (data as any).userId ?? userId : undefined,
      userEmail: userType === "citizen" ? (data as any).userEmail ?? userEmail : undefined,
      lawyerId: userType === "lawyer" ? (data as any).lawyerId ?? userId : undefined,
      lawyerEmail: userType === "lawyer" ? (data as any).lawyerEmail ?? userEmail : undefined,
    };

    const response = await api.post<CreateCaseResponse>(
      `/api/cases?${params.toString()}`,
      body
    );
    console.log(`✅ Case created:`, response);
    return response;
  } catch (error) {
    console.error(`❌ Error creating case:`, error);
    throw error;
  }
}

