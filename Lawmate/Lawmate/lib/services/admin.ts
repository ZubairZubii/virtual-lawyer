import { api } from "../api";

// Types for Admin Dashboard
export interface AdminMetrics {
  total_users: number;
  verified_lawyers: number;
  active_cases: number;
  pending_reviews: number;
}

export interface RecentActivity {
  action: string;
  user: string;
  time: string;
  type: "info" | "success" | "warning" | "error";
  detail: string;
}

export interface SystemStatus {
  service: string;
  status: string;
  uptime: string;
}

export interface AdminDashboardData {
  metrics: AdminMetrics;
  recent_activity: RecentActivity[];
  system_status: SystemStatus[];
}

// Types for Admin Settings
export interface AdminSettings {
  platform_name: string;
  support_email: string;
  max_file_upload_size_mb: number;
  email_notifications: boolean;
  ai_monitoring: boolean;
  auto_backup: boolean;
  maintenance_mode: boolean;
}

export interface UpdateSettingsRequest {
  platform_name?: string;
  support_email?: string;
  max_file_upload_size_mb?: number;
  email_notifications?: boolean;
  ai_monitoring?: boolean;
  auto_backup?: boolean;
  maintenance_mode?: boolean;
}

export interface UpdateSettingsResponse {
  success: boolean;
  settings: AdminSettings;
  message: string;
}

// API Functions
export async function getAdminDashboard(): Promise<AdminDashboardData> {
  console.log("📡 Calling /api/admin/dashboard...");
  try {
    const data = await api.get<AdminDashboardData>("/api/admin/dashboard");
    console.log("✅ Admin dashboard API response:", data);
    return data;
  } catch (error) {
    console.error("❌ Error calling /api/admin/dashboard:", error);
    throw error;
  }
}

export async function getAdminSettings(): Promise<AdminSettings> {
  console.log("📡 Calling /api/admin/settings...");
  try {
    const data = await api.get<AdminSettings>("/api/admin/settings");
    console.log("✅ Admin settings API response:", data);
    return data;
  } catch (error) {
    console.error("❌ Error calling /api/admin/settings:", error);
    throw error;
  }
}

export async function updateAdminSettings(
  settings: UpdateSettingsRequest
): Promise<UpdateSettingsResponse> {
  console.log("📡 Updating admin settings...", settings);
  try {
    const data = await api.post<UpdateSettingsResponse>(
      "/api/admin/settings",
      settings
    );
    console.log("✅ Admin settings updated:", data);
    return data;
  } catch (error) {
    console.error("❌ Error updating admin settings:", error);
    throw error;
  }
}

