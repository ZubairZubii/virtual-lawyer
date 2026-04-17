"use client"

import { useState, ReactNode } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Home,
  MessageSquare,
  Folder,
  Users,
  BarChart3,
  Settings,
  Bell,
  Search,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User,
  Scale as Scales,
  Sparkles,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface NavItem {
  icon: any
  label: string
  href: string
  badge?: number
}

interface PremiumDashboardLayoutProps {
  children: ReactNode
  user: {
    name: string
    email: string
    avatar?: string
    role: string
  }
  navItems?: NavItem[]
  onNavClick?: (href: string) => void
  onLogout?: () => void
}

const defaultNavItems: NavItem[] = [
  { icon: Home, label: "Dashboard", href: "/dashboard" },
  { icon: MessageSquare, label: "AI Chat", href: "/chat", badge: 3 },
  { icon: Folder, label: "Cases", href: "/cases" },
  { icon: Users, label: "Lawyers", href: "/lawyers" },
  { icon: BarChart3, label: "Analytics", href: "/analytics" },
  { icon: Settings, label: "Settings", href: "/settings" },
]

export function PremiumDashboardLayout({
  children,
  user,
  navItems = defaultNavItems,
  onNavClick,
  onLogout,
}: PremiumDashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeItem, setActiveItem] = useState("/dashboard")

  const handleNavClick = (href: string) => {
    setActiveItem(href)
    setMobileMenuOpen(false)
    onNavClick?.(href)
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Desktop Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 80 : 280 }}
        className="hidden lg:flex flex-col border-r border-border bg-card/30 backdrop-blur-sm relative"
      >
        {/* Logo */}
        <div className="p-6 border-b border-border/50">
          <motion.div
            className="flex items-center gap-3 cursor-pointer"
            whileHover={{ scale: 1.02 }}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
              <Scales className="w-6 h-6 text-primary-foreground" />
            </div>
            <AnimatePresence>
              {!sidebarCollapsed && (
                <motion.div
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  className="overflow-hidden"
                >
                  <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    Lawmate
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navItems.map((item, index) => (
            <motion.button
              key={item.href}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => handleNavClick(item.href)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all relative group",
                activeItem === item.href
                  ? "bg-gradient-to-r from-primary/10 to-accent/10 text-primary"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
              )}
            >
              {/* Active Indicator */}
              {activeItem === item.href && (
                <motion.div
                  layoutId="activeNav"
                  className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-primary to-accent rounded-r"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}

              <item.icon className="w-5 h-5 shrink-0" />

              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: "auto" }}
                    exit={{ opacity: 0, width: 0 }}
                    className="font-medium overflow-hidden whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>

              {/* Badge */}
              {item.badge && item.badge > 0 && !sidebarCollapsed && (
                <Badge className="ml-auto bg-primary text-primary-foreground">
                  {item.badge}
                </Badge>
              )}

              {/* Tooltip for collapsed state */}
              {sidebarCollapsed && (
                <div className="absolute left-full ml-2 px-3 py-2 bg-popover text-popover-foreground rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                  {item.label}
                  {item.badge && item.badge > 0 && (
                    <Badge className="ml-2 bg-primary text-primary-foreground">
                      {item.badge}
                    </Badge>
                  )}
                </div>
              )}
            </motion.button>
          ))}
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-border/50">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <motion.button
                whileHover={{ scale: 1.02 }}
                className={cn(
                  "w-full flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-all",
                  sidebarCollapsed && "justify-center"
                )}
              >
                <Avatar className="w-9 h-9 border-2 border-primary/20">
                  <AvatarImage src={user.avatar} />
                  <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-primary-foreground">
                    {user.name[0]}
                  </AvatarFallback>
                </Avatar>
                <AnimatePresence>
                  {!sidebarCollapsed && (
                    <motion.div
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: "auto" }}
                      exit={{ opacity: 0, width: 0 }}
                      className="flex-1 overflow-hidden text-left"
                    >
                      <div className="font-medium text-foreground truncate">{user.name}</div>
                      <div className="text-xs text-muted-foreground truncate">{user.role}</div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem>
                <User className="w-4 h-4 mr-2" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onLogout} className="text-destructive">
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Collapse Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="absolute -right-3 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full border border-border bg-background shadow-md hover:shadow-lg p-0 z-10"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-3 h-3" />
          ) : (
            <ChevronLeft className="w-3 h-3" />
          )}
        </Button>
      </motion.aside>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileMenuOpen(false)}
              className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 20 }}
              className="fixed left-0 top-0 bottom-0 w-80 bg-card border-r border-border z-50 lg:hidden flex flex-col"
            >
              {/* Mobile Header */}
              <div className="p-6 border-b border-border/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                    <Scales className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    Lawmate
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              {/* Mobile Navigation */}
              <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                {navItems.map((item) => (
                  <button
                    key={item.href}
                    onClick={() => handleNavClick(item.href)}
                    className={cn(
                      "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all",
                      activeItem === item.href
                        ? "bg-gradient-to-r from-primary/10 to-accent/10 text-primary"
                        : "text-muted-foreground hover:bg-muted/50"
                    )}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                    {item.badge && item.badge > 0 && (
                      <Badge className="ml-auto bg-primary text-primary-foreground">
                        {item.badge}
                      </Badge>
                    )}
                  </button>
                ))}
              </nav>

              {/* Mobile User Profile */}
              <div className="p-4 border-t border-border/50">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                  <Avatar className="w-10 h-10 border-2 border-primary/20">
                    <AvatarImage src={user.avatar} />
                    <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-primary-foreground">
                      {user.name[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{user.name}</div>
                    <div className="text-xs text-muted-foreground">{user.role}</div>
                  </div>
                </div>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="border-b border-border bg-card/30 backdrop-blur-sm">
          <div className="flex items-center gap-4 p-4">
            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </Button>

            {/* Search */}
            <div className="flex-1 max-w-xl">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search cases, lawyers, documents..."
                  className="pl-10 bg-background/50 border-border/50"
                />
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full" />
              </Button>

              <Button size="sm" className="gap-2 bg-gradient-to-r from-primary to-accent text-primary-foreground border-0 hidden sm:flex">
                <Sparkles className="w-4 h-4" />
                Ask AI
              </Button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}
