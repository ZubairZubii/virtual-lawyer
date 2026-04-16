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
export async function getCitizenCases(status?: string): Promise<CasesResponse> {
  const params = status ? `?status=${status}` : "";
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
  const params = status ? `?status=${status}` : "";
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
    const response = await api.post<CreateCaseResponse>(
      `/api/cases?user_type=${userType}`,
      data
    );
    console.log(`✅ Case created:`, response);
    return response;
  } catch (error) {
    console.error(`❌ Error creating case:`, error);
    throw error;
  }
}

