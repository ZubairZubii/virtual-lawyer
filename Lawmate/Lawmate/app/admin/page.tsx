"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Users, Shield, BarChart3, AlertCircle, Activity, CheckCircle2, ArrowRight, Bell, Server, Loader2 } from "lucide-react"
import Link from "next/link"
import { getAdminDashboard, type AdminDashboardData } from "@/lib/services/admin"

export default function AdminDashboard() {
  const [isLoaded, setIsLoaded] = useState(false)
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setIsLoaded(true)
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getAdminDashboard()
      setDashboardData(data)
    } catch (err: any) {
      console.error("Error loading admin dashboard:", err)
      setError(err.message || "Failed to load dashboard data")
    } finally {
      setLoading(false)
    }
  }

  const systemMetrics = dashboardData ? [
    {
      label: "Total Users",
      value: dashboardData.metrics.total_users.toLocaleString(),
      icon: Users,
      color: "from-primary to-accent",
      trend: `${dashboardData.metrics.total_users} total`,
      desc: "Registered users",
    },
    {
      label: "Verified Lawyers",
      value: dashboardData.metrics.verified_lawyers.toLocaleString(),
      icon: Shield,
      color: "from-accent to-secondary",
      trend: `${dashboardData.metrics.verified_lawyers} verified`,
      desc: "Active lawyers",
    },
    {
      label: "Active Cases",
      value: dashboardData.metrics.active_cases.toLocaleString(),
      icon: BarChart3,
      color: "from-secondary to-primary",
      trend: `${dashboardData.metrics.active_cases} tracked`,
      desc: "Cases in progress",
    },
    {
      label: "Pending Reviews",
      value: dashboardData.metrics.pending_reviews.toLocaleString(),
      icon: AlertCircle,
      color: "from-destructive to-accent",
      trend: `${dashboardData.metrics.pending_reviews} pending`,
      desc: "To be reviewed",
    },
  ] : []

  return (
    <div className="flex">
      <Sidebar userType="admin" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-secondary/5">
        <div className="fixed inset-0 ml-64 -z-10">
          <div className="absolute top-20 right-0 w-96 h-96 bg-secondary/12 rounded-full blur-3xl opacity-25 animate-float"></div>
          <div
            className="absolute bottom-0 left-1/3 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-20 animate-float"
            style={{ animationDelay: "1.5s" }}
          ></div>
          <div
            className="absolute top-1/2 right-1/4 w-80 h-80 bg-accent/8 rounded-full blur-3xl opacity-15 animate-float"
            style={{ animationDelay: "3s" }}
          ></div>
          <div className="absolute inset-0 bg-grid-pattern opacity-3"></div>
        </div>

        <div className="p-8">
          {/* Header */}
          <div
            className={`mb-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
          >
            <div className="flex items-start justify-between mb-6 flex-col md:flex-row gap-4">
              <div>
                <h1 className="text-5xl font-bold text-foreground mb-2">System Administration</h1>
                <p className="text-lg text-muted-foreground">Monitor platform health, users, and security</p>
              </div>
              <Button
                variant="outline"
                className="bg-card/50 backdrop-blur border-border/50 hover:bg-card hover:border-primary/50 transition-all"
              >
                <Bell className="w-4 h-4 mr-2" />
                Alerts
              </Button>
            </div>
          </div>

          {/* System Metrics - Enhanced metrics */}
          {loading ? (
            <div className="flex items-center justify-center p-12 mb-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading dashboard...</span>
            </div>
          ) : error ? (
            <Card className="p-6 mb-12 border border-destructive/50">
              <div className="flex items-center gap-3 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <div>
                  <p className="font-semibold">Error loading dashboard</p>
                  <p className="text-sm">{error}</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={loadDashboard}>
                    Retry
                  </Button>
                </div>
              </div>
            </Card>
          ) : (
            <div
              className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
              style={{ transitionDelay: "100ms" }}
            >
              {systemMetrics.map((metric, i) => (
              <div
                key={i}
                className="group cursor-pointer"
                style={{ animation: `fadeInUp 0.6s ease-out ${i * 100}ms forwards`, opacity: 0 }}
              >
                <Card className="p-6 border border-border/50 hover:border-primary/50 transition-all duration-300 overflow-hidden relative group-hover:shadow-lg group-hover:translate-y-[-4px]">
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${metric.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                  ></div>
                  <div className="relative z-10">
                    <div className="flex items-center justify-between mb-4">
                      <div
                        className={`w-14 h-14 rounded-lg bg-gradient-to-br ${metric.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}
                      >
                        <metric.icon className="w-7 h-7 text-white" />
                      </div>
                      <span className="text-xs font-semibold text-primary bg-primary/10 px-2.5 py-1 rounded-full">
                        {metric.trend}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">{metric.label}</p>
                    <p className="text-3xl font-bold text-foreground group-hover:text-primary transition-colors">
                      {metric.value}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">{metric.desc}</p>
                  </div>
                </Card>
              </div>
            ))}
            </div>
          )}

          {/* Main Grid */}
          <div
            className={`grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "200ms" }}
          >
            {/* Recent Activity - Enhanced activity feed */}
            <div className="lg:col-span-2">
              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80 hover:shadow-lg transition-all">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-primary" />
                    <h2 className="text-xl font-bold text-foreground">Recent Activity</h2>
                  </div>
                  <Link href="/admin/analytics">
                    <Button variant="ghost" size="sm" className="hover:bg-primary/10">
                      View All <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
                <div className="space-y-3">
                  {loading ? (
                    <div className="flex items-center justify-center p-8">
                      <Loader2 className="w-6 h-6 animate-spin text-primary" />
                      <span className="ml-2 text-muted-foreground">Loading activity...</span>
                    </div>
                  ) : dashboardData?.recent_activity.length === 0 ? (
                    <div className="text-center p-8 text-muted-foreground">
                      <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No recent activity</p>
                    </div>
                  ) : (
                    dashboardData?.recent_activity.map((activity, i) => {
                      const iconMap: Record<string, typeof Users> = {
                        info: Users,
                        success: CheckCircle2,
                        warning: AlertCircle,
                        error: AlertCircle,
                      }
                      const ActivityIcon = iconMap[activity.type] || Users
                      return (
                    <div
                      key={i}
                      className="group p-4 border border-border/50 rounded-lg hover:border-primary/50 hover:bg-primary/5 transition-all duration-300"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex gap-3 flex-1">
                          <div
                            className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${activity.type === "success" ? "bg-primary/20" : activity.type === "warning" ? "bg-accent/20" : "bg-secondary/20"}`}
                          >
                            <ActivityIcon
                              className={`w-5 h-5 ${activity.type === "success" ? "text-primary" : activity.type === "warning" ? "text-accent" : "text-secondary"}`}
                            />
                          </div>
                          <div className="flex-1">
                            <p className="font-semibold text-foreground">{activity.action}</p>
                            <p className="text-xs text-muted-foreground">{activity.user}</p>
                            <p className="text-xs text-muted-foreground mt-1">{activity.detail}</p>
                          </div>
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap">{activity.time}</span>
                      </div>
                    </div>
                      )
                    })
                  )}
                </div>
              </Card>
            </div>

            {/* System Status & Quick Links - Enhanced status monitoring */}
            <div className="space-y-6">
              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80">
                <div className="flex items-center gap-2 mb-4">
                  <Server className="w-5 h-5 text-primary" />
                  <h3 className="font-bold text-foreground">System Status</h3>
                </div>
                <div className="space-y-3">
                  {loading ? (
                    <div className="flex items-center justify-center p-4">
                      <Loader2 className="w-5 h-5 animate-spin text-primary" />
                    </div>
                  ) : (
                    dashboardData?.system_status.map((service, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-green-500/20 to-transparent border border-green-200/30"
                    >
                      <div>
                        <p className="text-sm font-semibold text-foreground">{service.service}</p>
                        <p className="text-xs text-muted-foreground">{service.uptime} uptime</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-xs font-medium text-green-600">{service.status}</span>
                      </div>
                    </div>
                    ))
                  )}
                </div>
              </Card>

              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80">
                <h3 className="font-bold text-foreground mb-4">Quick Access</h3>
                <div className="space-y-2">
                  <Link href="/admin/users">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent hover:bg-primary/10 border-border/50 transition-all"
                    >
                      <Users className="w-4 h-4 mr-2" />
                      Manage Users
                    </Button>
                  </Link>
                  <Link href="/admin/lawyers">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent hover:bg-accent/10 border-border/50 transition-all"
                    >
                      <Shield className="w-4 h-4 mr-2" />
                      Verify Lawyers
                    </Button>
                  </Link>
                  <Link href="/admin/settings">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent hover:bg-secondary/10 border-border/50 transition-all"
                    >
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Settings
                    </Button>
                  </Link>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
