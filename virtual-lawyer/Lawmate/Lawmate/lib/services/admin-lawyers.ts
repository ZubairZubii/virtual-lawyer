import { api } from "../api";

export interface Lawyer {
  id: string;
  name: string;
  email: string;
  specialization: string;
  verificationStatus: "Verified" | "Pending" | "Rejected";
  casesSolved: number;
  winRate: number | string;
  joinDate: string;
  location?: string;
  rating?: number;
  reviews?: number;
  specializations?: string[];
  yearsExp?: number;
  cases?: number;
  phone?: string;
}

export interface CreateLawyerRequest {
  name: string;
  email: string;
  specialization?: string;
  password: string;
}

export interface LawyersResponse {
  lawyers: Lawyer[];
  total: number;
}

export async function getLawyers(): Promise<LawyersResponse> {
  return api.get<LawyersResponse>("/api/admin/lawyers");
}

export async function createLawyer(request: CreateLawyerRequest) {
  return api.post("/api/admin/lawyers", request);
}

export async function verifyLawyer(lawyerId: string, status: "Verified" | "Rejected" = "Verified") {
  return api.put(`/api/admin/lawyers/${lawyerId}/verify?status=${status}`);
}

export async function deleteLawyer(lawyerId: string) {
  return api.delete(`/api/admin/lawyers/${lawyerId}`);
}

