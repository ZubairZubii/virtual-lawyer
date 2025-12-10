import { api } from "../api";

export interface Lawyer {
  id: string;
  name: string;
  expertise: string;
  location: string;
  winRate: number;
  cases: number;
  rating: number;
  reviews: number;
  specialization: string[];
  yearsExp: number;
  email?: string;
  phone?: string;
}

export interface LawyersResponse {
  lawyers: Lawyer[];
  total: number;
}

export async function getLawyers(search?: string, specialization?: string): Promise<LawyersResponse> {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (specialization) params.append("specialization", specialization);
  const queryString = params.toString();
  return api.get<LawyersResponse>(`/api/lawyers${queryString ? `?${queryString}` : ""}`);
}

export async function getLawyerProfile(lawyerId: string): Promise<Lawyer> {
  return api.get<Lawyer>(`/api/lawyers/${lawyerId}`);
}

