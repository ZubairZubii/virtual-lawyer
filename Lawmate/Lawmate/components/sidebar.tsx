"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Shield, Home, BarChart3, Users, Settings, LogOut, FileText, Brain } from "lucide-react"
import { cn } from "@/lib/utils"

export function Sidebar({ userType }: { userType: "citizen" | "lawyer" | "admin" }) {
  const pathname = usePathname()
  const router = useRouter()

  const getMenuItems = () => {
    const baseItems = [{ label: "Dashboard", href: `/${userType}`, icon: Home }]

    if (userType === "citizen") {
      return [
        ...baseItems,
        { label: "AI Assistant", href: `/${userType}/chatbot`, icon: Brain },
        { label: "My Cases", href: `/${userType}/cases`, icon: FileText },
        { label: "Documents", href: `/${userType}/documents`, icon: FileText },
        { label: "Find Lawyers", href: `/${userType}/lawyers`, icon: Users },
      ]
    }

    if (userType === "lawyer") {
      return [ 
        ...baseItems,
      { label: "AI Assistant", href: `/${userType}/chatbot`, icon: Brain },
        { label: "My Clients", href: `/${userType}/clients`, icon: Users },
        { label: "Cases", href: `/${userType}/cases`, icon: FileText },
        { label: "Analytics", href: `/${userType}/analytics`, icon: BarChart3 },
        { label: "Documents", href: `/${userType}/documents`, icon: FileText },
      ]
    }

    return [
      ...baseItems,
      { label: "Users", href: `/${userType}/users`, icon: Users },
      { label: "Lawyers", href: `/${userType}/lawyers`, icon: Users },
      { label: "Analytics", href: `/${userType}/analytics`, icon: BarChart3 },
      { label: "Settings", href: `/${userType}/settings`, icon: Settings },
    ]
  }

  const items = getMenuItems()
  const handleLogout = () => {
    localStorage.removeItem("user")
    localStorage.removeItem("token")
    router.push("/login")
  }

  return (
    <aside className="w-64 h-screen border-r border-sidebar-border bg-gradient-to-b from-sidebar to-sidebar/95 fixed left-0 top-0 flex flex-col shadow-xl">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border/50 flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-sidebar-primary to-sidebar-accent flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
          <Shield className="w-6 h-6 text-sidebar-primary-foreground" />
        </div>
        <div>
          <span className="font-bold text-sidebar-foreground text-lg">Lawmate</span>
          <p className="text-xs text-sidebar-foreground/60">Legal Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-2">
          {items.map((item, idx) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
            return (
              <li
                key={item.href}
                style={{ animation: `slideInLeft 0.3s ease-out ${idx * 50}ms forwards` }}
                className="opacity-0"
              >
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group relative",
                    isActive
                      ? "bg-gradient-to-r from-sidebar-primary to-sidebar-accent text-sidebar-primary-foreground shadow-lg"
                      : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-primary",
                  )}
                >
                  <item.icon size={18} />
                  <span className="text-sm font-medium">{item.label}</span>
                  {isActive && (
                    <div className="absolute right-0 top-0 bottom-0 w-1 bg-gradient-to-b from-sidebar-primary-foreground to-sidebar-accent-foreground rounded-r-lg"></div>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border/50">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent/50 transition-all duration-300 group"
        >
          <LogOut size={18} />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>
    </aside>
  )
}
