"use client"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { Loader2 } from "lucide-react"

type Role = "citizen" | "lawyer" | "admin"

type StoredUser = {
  id: string
  name: string
  email: string
  role: string
  userType: Role
}

export function AuthGuard({
  requiredRole,
  children,
}: {
  requiredRole: Role
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    try {
      const raw = localStorage.getItem("user")
      if (!raw) {
        router.replace(`/login?redirect=${encodeURIComponent(pathname || `/${requiredRole}`)}`)
        return
      }

      const user = JSON.parse(raw) as StoredUser
      if (!user?.userType) {
        localStorage.removeItem("user")
        router.replace(`/login?redirect=${encodeURIComponent(pathname || `/${requiredRole}`)}`)
        return
      }

      if (user.userType !== requiredRole) {
        router.replace(`/${user.userType}`)
        return
      }

      setChecking(false)
    } catch {
      localStorage.removeItem("user")
      router.replace(`/login?redirect=${encodeURIComponent(pathname || `/${requiredRole}`)}`)
    }
  }, [requiredRole, pathname, router])

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Checking authentication...</span>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

