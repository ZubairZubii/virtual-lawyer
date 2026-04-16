import type React from "react"
import { AuthGuard } from "@/components/auth-guard"

export default function LawyerLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard requiredRole="lawyer">{children}</AuthGuard>
}

