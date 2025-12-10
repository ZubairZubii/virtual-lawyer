"use client"

import { useEffect, useState } from "react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export function UserBadge() {
  const [user, setUser] = useState<{ name?: string; email?: string } | null>(null)

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem("user") : null
    if (stored) {
      try {
        setUser(JSON.parse(stored))
      } catch {
        setUser(null)
      }
    }
  }, [])

  if (!user) return null

  const initials =
    user.name?.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() ||
    (user.email ? user.email[0].toUpperCase() : "U")

  return (
    <div className="flex items-center gap-3">
      <Avatar className="h-9 w-9">
        <AvatarFallback>{initials}</AvatarFallback>
      </Avatar>
      <div className="leading-tight">
        <div className="font-semibold text-foreground">{user.name || "User"}</div>
        <div className="text-xs text-muted-foreground">{user.email}</div>
      </div>
    </div>
  )
}

