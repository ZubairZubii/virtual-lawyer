import { api } from "../api";

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  joinDate: string;
  status: string;
  casesInvolved: number;
}

export interface CreateUserRequest {
  name: string;
  email: string;
  role: string;
  password: string;
}

export interface UsersResponse {
  users: User[];
  total: number;
}

export async function getUsers(search?: string): Promise<UsersResponse> {
  const params = search ? `?search=${encodeURIComponent(search)}` : "";
  return api.get<UsersResponse>(`/api/admin/users${params}`);
}

export async function createUser(request: CreateUserRequest) {
  return api.post("/api/admin/users", request);
}

export async function updateUser(userId: string, updates: Partial<User>) {
  return api.put(`/api/admin/users/${userId}`, updates);
}

export async function deleteUser(userId: string) {
  return api.delete(`/api/admin/users/${userId}`);
}

