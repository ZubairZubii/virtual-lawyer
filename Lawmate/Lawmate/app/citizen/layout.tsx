import type React from "react"
import { AuthGuard } from "@/components/auth-guard"

export default function CitizenLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard requiredRole="citizen">{children}</AuthGuard>
}

