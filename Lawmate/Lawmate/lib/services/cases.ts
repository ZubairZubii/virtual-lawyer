import { api } from "../api";

// Types for Cases
export interface Case {
  id: string;
  case_type: string;
  status: string;
  case_summary?: string;
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
  case_summary?: string;
  case_metadata?: Record<string, string>;
  case_documents?: Array<{ doc_id: string; file_name: string }>;
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

// API Functions
export async function getCitizenCases(status?: string): Promise<CasesResponse> {
  const user = getLoggedInUser();
  const query: string[] = [];
  if (status) query.push(`status=${encodeURIComponent(status)}`);
  if (user.id) query.push(`citizen_id=${encodeURIComponent(user.id)}`);
  const params = query.length ? `?${query.join("&")}` : "";
  console.log(`📡 Calling /api/cases/citizen${params}...`);
  try {
    const data = await api.get<CasesResponse>(`/api/cases/citizen${params}`);
    console.log(`✅ Citizen cases API response:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Error calling /api/cases/citizen:`, error);
    throw error;
  }
}

export async function getLawyerCases(status?: string): Promise<CasesResponse> {
  const user = getLoggedInUser();
  const query: string[] = [];
  if (status) query.push(`status=${encodeURIComponent(status)}`);
  if (user.id) query.push(`lawyer_id=${encodeURIComponent(user.id)}`);
  const params = query.length ? `?${query.join("&")}` : "";
  console.log(`📡 Calling /api/cases/lawyer${params}...`);
  try {
    const data = await api.get<CasesResponse>(`/api/cases/lawyer${params}`);
    console.log(`✅ Lawyer cases API response:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Error calling /api/cases/lawyer:`, error);
    throw error;
  }
}

export async function getCaseDetails(caseId: string): Promise<CaseDetails> {
  // Case IDs may contain "/" (e.g. "123/2023"), so encode the full ID.
  const encodedId = encodeURIComponent(caseId);
  try {
    return await api.get<CaseDetails>(`/api/cases/${encodedId}`);
  } catch (error) {
    // Fallback for environments/proxies that mishandle slash-based path params.
    return api.get<CaseDetails>(`/api/cases/by-id?case_id=${encodedId}`);
  }
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
  case_summary?: string;
  case_metadata?: Record<string, string>;
  uploaded_documents?: Array<{ doc_id: string; file_name: string }>;
  owner_citizen_id?: string;
  owner_lawyer_id?: string;
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
    const user = getLoggedInUser();
    const payload: CreateCaseRequest & { owner_citizen_id?: string; owner_lawyer_id?: string } = { ...data };
    if (user.id && userType === "citizen") payload.owner_citizen_id = user.id;
    if (user.id && userType === "lawyer") payload.owner_lawyer_id = user.id;
    const response = await api.post<CreateCaseResponse>(
      `/api/cases?user_type=${userType}`,
      payload
    );
    console.log(`✅ Case created:`, response);
    return response;
  } catch (error) {
    console.error(`❌ Error creating case:`, error);
    throw error;
  }
}

