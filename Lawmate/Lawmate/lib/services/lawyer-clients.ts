import { api } from "../api";

export interface Client {
  id: string;
  name: string;
  email: string;
  phone: string;
  caseType: string;
  status: "Active" | "Closed" | "On Hold";
  activeCases: number;
  totalCases: number;
  caseId?: string;
  firNumber?: string;
  court?: string;
  policeStation?: string;
  caseStage?: string;
  riskLevel?: "Low" | "Medium" | "High";
  priority?: "Low" | "Medium" | "High";
  nextHearing?: string;
  lastContactDate?: string;
  assignedDate?: string;
  outstandingAmount?: number;
  notes?: string;
  city?: string;
}

export interface ClientsResponse {
  clients: Client[];
  total: number;
}

export interface ClientCase {
  caseId: string;
  caseType: string;
  status: "Active" | "Closed" | "On Hold";
  firNumber?: string;
  court?: string;
  policeStation?: string;
  caseStage?: string;
  riskLevel?: "Low" | "Medium" | "High";
  priority?: "Low" | "Medium" | "High";
  nextHearing?: string;
  outstandingAmount?: number;
  notes?: string;
  assignedDate?: string;
  lastContactDate?: string;
}

export interface ClientCasesResponse {
  clientId: string;
  cases: ClientCase[];
  total: number;
}

export interface CreateClientRequest {
  lawyerId: string;
  /** Sent with create so the API can resolve the advocate if lawyerId is a temp session id */
  lawyerEmail?: string;
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  city?: string;
  notes?: string;
  status?: "Active" | "Closed" | "On Hold";
  riskLevel?: "Low" | "Medium" | "High";
  priority?: "Low" | "Medium" | "High";
}

export interface CreateClientCaseRequest {
  lawyerId: string;
  lawyerEmail?: string;
  clientId: string;
  caseType: string;
  status?: "Active" | "Closed" | "On Hold";
  firNumber?: string;
  court?: string;
  policeStation?: string;
  caseStage?: string;
  riskLevel?: "Low" | "Medium" | "High";
  priority?: "Low" | "Medium" | "High";
  nextHearing?: string;
  outstandingAmount?: number;
  notes?: string;
}

export async function getClients(
  lawyerId?: string,
  lawyerEmail?: string
): Promise<ClientsResponse> {
  const params = new URLSearchParams();
  if (lawyerId) params.set("lawyer_id", lawyerId);
  if (lawyerEmail) params.set("email", lawyerEmail);
  const q = params.toString();
  return api.get<ClientsResponse>(`/api/lawyer/clients${q ? `?${q}` : ""}`);
}

export async function createClient(request: CreateClientRequest): Promise<{ success: boolean; message: string; clientId: string }> {
  return api.post<{ success: boolean; message: string; clientId: string }>(`/api/lawyer/clients`, request);
}

export async function getClientCases(
  clientId: string,
  lawyerId?: string,
  lawyerEmail?: string
): Promise<ClientCasesResponse> {
  const params = new URLSearchParams();
  if (lawyerId) params.set("lawyer_id", lawyerId);
  if (lawyerEmail) params.set("email", lawyerEmail);
  const q = params.toString();
  return api.get<ClientCasesResponse>(
    `/api/lawyer/clients/${clientId}/cases${q ? `?${q}` : ""}`
  );
}

export async function createClientCase(
  clientId: string,
  request: CreateClientCaseRequest,
): Promise<{ success: boolean; message: string; caseId: string }> {
  return api.post<{ success: boolean; message: string; caseId: string }>(`/api/lawyer/clients/${clientId}/cases`, request);
}

