"use client"

export type StoredUser = {
  id: string
  name: string
  email: string
  role?: string
  userType?: string
  status?: string
  verificationStatus?: string
}

export function getStoredUser(): StoredUser | null {
  if (typeof window === "undefined") return null
  try {
    const raw = localStorage.getItem("user")
    if (!raw) return null
    return JSON.parse(raw) as StoredUser
  } catch {
    return null
  }
}

/** Display name from login, or fallback while loading / logged out */
export function getUserDisplayName(fallback: string): string {
  const u = getStoredUser()
  const n = u?.name?.trim()
  return n || fallback
}

/** Role for document list/upload APIs (`owner_role` on the server). */
export function getDocumentApiRole(
  fallback: "citizen" | "lawyer"
): "citizen" | "lawyer" {
  const u = getStoredUser()
  const r = `${u?.role ?? u?.userType ?? ""}`.toLowerCase()
  if (r === "citizen" || r.includes("citizen")) return "citizen"
  if (r === "lawyer" || r.includes("lawyer")) return "lawyer"
  return fallback
}
