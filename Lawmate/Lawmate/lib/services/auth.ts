import { api } from "../api";

export interface LoginRequest {
  email: string;
  password: string;
  userType: "citizen" | "lawyer" | "admin";
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
  userType: "citizen" | "lawyer";
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  userType: string;
  status?: string;
  verificationStatus?: string;
}

export interface AuthResponse {
  success: boolean;
  user: User;
  message: string;
  token?: string;
  access_token?: string;
  token_type?: string;
  expires_in?: number;
}

export async function login(request: LoginRequest): Promise<AuthResponse> {
  console.log("📡 Calling /api/auth/login...", request);
  try {
    const response = await api.post<AuthResponse>("/api/auth/login", request);
    console.log("✅ Login response:", response);
    return response;
  } catch (error) {
    console.error("❌ Error calling /api/auth/login:", error);
    throw error;
  }
}

export async function signup(request: SignupRequest): Promise<AuthResponse> {
  console.log("📡 Calling /api/auth/signup...", request);
  try {
    const response = await api.post<AuthResponse>("/api/auth/signup", request);
    console.log("✅ Signup response:", response);
    return response;
  } catch (error) {
    console.error("❌ Error calling /api/auth/signup:", error);
    throw error;
  }
}

