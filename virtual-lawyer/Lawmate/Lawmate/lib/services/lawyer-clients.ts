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
}

export interface ClientsResponse {
  clients: Client[];
  total: number;
}

export async function getClients(lawyerId?: string): Promise<ClientsResponse> {
  const params = lawyerId ? `?lawyer_id=${lawyerId}` : "";
  return api.get<ClientsResponse>(`/api/lawyer/clients${params}`);
}

