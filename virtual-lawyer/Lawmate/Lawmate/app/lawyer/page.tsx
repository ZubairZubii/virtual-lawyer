"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BarChart3, TrendingUp, AlertCircle, Users, Calendar, Target, ArrowRight, Bell, Brain, Loader2 } from "lucide-react"
import Link from "next/link"
import { useLawyerDashboard } from "@/lib/store/dashboardStore"
import { UserBadge } from "@/components/user-badge"

export default function LawyerDashboard() {
  const [isLoaded, setIsLoaded] = useState(false)
  const [userName, setUserName] = useState("Lawyer")
  const { data: dashboardData, loading, error, refresh } = useLawyerDashboard()

  useEffect(() => {
    setIsLoaded(true)
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("user")
      if (stored) {
        try {
          const u = JSON.parse(stored) as { name?: string }
          if (u?.name) setUserName(u.name)
        } catch {
          setUserName("Lawyer")
        }
      }
    }
  }, [])

  // Show error message if there's an error
  if (error) {
    console.error("Dashboard error:", error)
  }

  // Use data from store, fallback to defaults if loading or error
  const metrics = dashboardData ? [
    {
      label: "Active Cases",
      value: dashboardData.metrics.active_cases.toString(),
      icon: BarChart3,
      color: "from-primary to-accent",
      trend: `+${dashboardData.trends.cases_this_month} this month`,
      desc: "Cases in progress",
    },
    {
      label: "Win Rate",
      value: `${dashboardData.metrics.win_rate}%`,
      icon: TrendingUp,
      color: "from-accent to-secondary",
      trend: dashboardData.trends.win_rate_trend || "Average",
      desc: "Success rate",
    },
    {
      label: "Pending Hearings",
      value: dashboardData.metrics.pending_hearings.toString(),
      icon: Calendar,
      color: "from-secondary to-primary",
      trend: dashboardData.trends.next_hearing_date || "No upcoming",
      desc: "Next hearing",
    },
    {
      label: "Total Clients",
      value: dashboardData.metrics.total_clients.toString(),
      icon: Users,
      color: "from-primary to-secondary",
      trend: `+${dashboardData.trends.active_clients} active`,
      desc: "Active clients",
    },
  ] : [
    {
      label: "Active Cases",
      value: "0",
      icon: BarChart3,
      color: "from-primary to-accent",
      trend: "Loading...",
      desc: "Cases in progress",
    },
    {
      label: "Win Rate",
      value: "0%",
      icon: TrendingUp,
      color: "from-accent to-secondary",
      trend: "Loading...",
      desc: "Success rate",
    },
    {
      label: "Pending Hearings",
      value: "0",
      icon: Calendar,
      color: "from-secondary to-primary",
      trend: "Loading...",
      desc: "Next hearing",
    },
    {
      label: "Total Clients",
      value: "0",
      icon: Users,
      color: "from-primary to-secondary",
      trend: "Loading...",
      desc: "Active clients",
    },
  ]

  const urgentCases = dashboardData?.urgent_cases || []
  const performance = dashboardData?.performance

  return (
    <div className="flex">
      <Sidebar userType="lawyer" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-accent/5">
        <div className="fixed inset-0 ml-64 -z-10">
          <div className="absolute top-20 right-0 w-96 h-96 bg-accent/12 rounded-full blur-3xl opacity-25 animate-float"></div>
          <div
            className="absolute bottom-0 left-1/3 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-20 animate-float"
            style={{ animationDelay: "1.5s" }}
          ></div>
          <div
            className="absolute top-1/3 right-1/4 w-80 h-80 bg-secondary/8 rounded-full blur-3xl opacity-15 animate-float"
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
                <h1 className="text-5xl font-bold text-foreground mb-2">Welcome, {userName}</h1>
                <p className="text-lg text-muted-foreground">Manage cases, track performance, and grow your practice</p>
              </div>
              <div className="flex gap-3 items-center">
                <UserBadge />
                {error && (
                  <Button
                    variant="outline"
                    className="bg-destructive/10 text-destructive border-destructive/20"
                    onClick={refresh}
                  >
                    Retry
                  </Button>
                )}
                <Button
                  variant="outline"
                  className="bg-card/50 backdrop-blur border-border/50 hover:bg-card hover:border-primary/50 transition-all"
                >
                  <Bell className="w-4 h-4 mr-2" />
                  Alerts
                </Button>
              </div>
            </div>
            {error && (
              <div className="mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                <p className="text-sm text-destructive">
                  <AlertCircle className="w-4 h-4 inline mr-2" />
                  {error}. Please restart your backend server.
                </p>
              </div>
            )}
          </div>

          {/* Performance Metrics - Enhanced with detailed info */}
          <div
            className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "100ms" }}
          >
            {metrics.map((metric, i) => (
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
                      <span className="text-xs font-semibold text-accent bg-accent/10 px-2.5 py-1 rounded-full">
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

          {/* Main Grid */}
          <div
            className={`grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "200ms" }}
          >
            {/* Urgent Cases - Enhanced case details */}
            <div className="lg:col-span-2">
              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80 hover:shadow-lg transition-all">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-destructive" />
                    <h2 className="text-xl font-bold text-foreground">Urgent Cases</h2>
                  </div>
                  <Link href="/lawyer/cases">
                    <Button variant="ghost" size="sm" className="hover:bg-primary/10">
                      View All <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
                <div className="space-y-3">
                  {loading ? (
                    <div className="flex items-center justify-center p-8">
                      <Loader2 className="w-6 h-6 animate-spin text-primary" />
                      <span className="ml-2 text-muted-foreground">Loading cases...</span>
                    </div>
                  ) : urgentCases.length === 0 ? (
                    <div className="text-center p-8 text-muted-foreground">
                      <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No urgent cases</p>
                    </div>
                  ) : (
                    urgentCases.map((case_, i) => (
                    <div
                      key={i}
                      className="group p-5 border border-border/50 rounded-lg hover:border-primary/50 hover:bg-primary/5 transition-all duration-300 cursor-pointer"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-bold text-foreground">{case_.id}</p>
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${case_.priority === "High" ? "bg-destructive/20 text-destructive" : case_.priority === "Medium" ? "bg-accent/20 text-accent" : "bg-muted/20 text-muted-foreground"}`}
                            >
                              {case_.priority} Priority
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">{case_.client_name}</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div className="text-xs text-muted-foreground">
                          <span className="block font-medium text-foreground">Deadline</span>
                          {case_.deadline}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          <span className="block font-medium text-foreground">Hours</span>
                          {case_.hours_billed}h billed
                        </div>
                      </div>
                      <div className="w-full bg-border/50 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
                          style={{ width: `${case_.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    ))
                  )}
                </div>
              </Card>
            </div>

            {/* Performance & Stats - Enhanced side panel */}
            <div className="space-y-6">
              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="w-5 h-5 text-primary" />
                  <h3 className="font-bold text-foreground">Performance Metrics</h3>
                </div>
                <div className="space-y-4">
                  {loading ? (
                    <div className="flex items-center justify-center p-4">
                      <Loader2 className="w-5 h-5 animate-spin text-primary" />
                    </div>
                  ) : performance ? (
                    [
                      { 
                        label: "Cases Won", 
                        value: `${performance.cases_won}/${performance.cases_total}`, 
                        percent: performance.cases_total > 0 ? Math.round((performance.cases_won / performance.cases_total) * 100) : 0 
                      },
                      { 
                        label: "Avg. Resolution", 
                        value: `${performance.avg_resolution_months} mo`, 
                        percent: Math.min(100, Math.round((performance.avg_resolution_months / 12) * 100)) 
                      },
                      { 
                        label: "Client Rating", 
                        value: `${performance.client_rating}★`, 
                        percent: Math.round((performance.client_rating / 5) * 100) 
                      },
                    ].map((item, i) => (
                    <div key={i}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-foreground">{item.label}</span>
                        <span className="font-bold text-primary text-sm">{item.value}</span>
                      </div>
                      <div className="w-full bg-border/50 rounded-full h-2.5 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
                          style={{ width: `${item.percent}%` }}
                        ></div>
                      </div>
                    </div>
                    ))
                  ) : (
                    <div className="text-center p-4 text-muted-foreground text-sm">
                      No performance data available
                    </div>
                  )}
                </div>
              </Card>

              {/* Quick Actions */}
              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80">
                <h3 className="font-bold text-foreground mb-4">Quick Actions</h3>
                <div className="space-y-2">
                  <Link href="/lawyer/chatbot">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent hover:bg-primary/10 border-border/50 transition-all"
                    >
                      <Brain className="w-4 h-4 mr-2" />
                      AI Assistant
                    </Button>
                  </Link>
                  <Link href="/lawyer/cases/analyze">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent hover:bg-primary/10 border-border/50 transition-all"
                    >
                      <TrendingUp className="w-4 h-4 mr-2" />
                      Analyze Case
                    </Button>
                  </Link>
                  <Link href="/lawyer/clients">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent hover:bg-primary/10 border-border/50 transition-all"
                    >
                      <Users className="w-4 h-4 mr-2" />
                      Manage Clients
                    </Button>
                  </Link>
                  <Link href="/lawyer/analytics">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent hover:bg-accent/10 border-border/50 transition-all"
                    >
                      <BarChart3 className="w-4 h-4 mr-2" />
                      View Analytics
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
