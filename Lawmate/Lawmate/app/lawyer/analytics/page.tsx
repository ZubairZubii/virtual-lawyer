"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, AlertCircle } from "lucide-react"
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { getLawyerAnalytics, type LawyerAnalyticsData } from "@/lib/services/lawyer-analytics"

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<LawyerAnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getLawyerAnalytics()
      setAnalytics(data)
    } catch (err: any) {
      console.error("Error loading lawyer analytics:", err)
      setError(err.message || "Failed to load analytics")
    } finally {
      setLoading(false)
    }
  }

  const caseData = analytics?.case_outcomes || []
  const caseTypeData = analytics?.case_type_performance || []
  const summaryMetrics = analytics?.summary_metrics
  const trends = analytics?.trends

  return (
    <div className="flex">
      <Sidebar userType="lawyer" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Case Analytics</h1>
              <p className="text-muted-foreground mt-2">Performance metrics and case insights</p>
            </div>
            <Button onClick={loadAnalytics} variant="outline" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                "Refresh"
              )}
            </Button>
          </div>

          {/* Error Message */}
          {error && (
            <Card className="p-6 mb-6 border border-destructive/50 bg-destructive/10">
              <div className="flex items-center gap-3 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <div>
                  <p className="font-semibold">Error loading analytics</p>
                  <p className="text-sm">{error}</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={loadAnalytics}>
                    Retry
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {loading ? (
            <div className="flex items-center justify-center p-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading analytics...</span>
            </div>
          ) : (
            <>
              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Line Chart */}
                <Card className="p-6 border border-border">
                  <h2 className="text-lg font-semibold text-foreground mb-4">Case Outcomes (6 Months)</h2>
                  {caseData.length === 0 ? (
                    <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                      No case outcome data available
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={caseData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis stroke="var(--color-muted-foreground)" />
                  <YAxis stroke="var(--color-muted-foreground)" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--color-card)",
                      border: `1px solid var(--color-border)`,
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="won" stroke="var(--color-primary)" strokeWidth={2} />
                  <Line type="monotone" dataKey="lost" stroke="var(--color-destructive)" strokeWidth={2} />
                        <Line type="monotone" dataKey="pending" stroke="var(--color-accent)" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </Card>

                {/* Bar Chart */}
                <Card className="p-6 border border-border">
                  <h2 className="text-lg font-semibold text-foreground mb-4">Case Type Performance</h2>
                  {caseTypeData.length === 0 ? (
                    <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                      No case type performance data available
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={caseTypeData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis stroke="var(--color-muted-foreground)" dataKey="type" />
                  <YAxis stroke="var(--color-muted-foreground)" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--color-card)",
                      border: `1px solid var(--color-border)`,
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                        <Bar dataKey="count" fill="var(--color-primary)" />
                        <Bar dataKey="winRate" fill="var(--color-accent)" />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </Card>
              </div>

              {/* Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {summaryMetrics && trends ? [
                  {
                    label: "Average Resolution Time",
                    value: `${summaryMetrics.avg_resolution_time_months.toFixed(1)} months`,
                    trend: trends.resolution_time_change < 0
                      ? `↓ ${Math.abs(trends.resolution_time_change).toFixed(1)} months`
                      : `↑ ${trends.resolution_time_change.toFixed(1)} months`
                  },
                  {
                    label: "Client Satisfaction",
                    value: `${summaryMetrics.client_satisfaction.toFixed(1)}/5.0`,
                    trend: trends.satisfaction_change > 0
                      ? `↑ ${trends.satisfaction_change.toFixed(1)} points`
                      : `↓ ${Math.abs(trends.satisfaction_change).toFixed(1)} points`
                  },
                  {
                    label: "Case Success Rate",
                    value: `${summaryMetrics.case_success_rate}%`,
                    trend: trends.success_rate_change > 0
                      ? `↑ ${trends.success_rate_change}%`
                      : `↓ ${Math.abs(trends.success_rate_change)}%`
                  },
                ].map((stat, i) => (
                  <Card key={i} className="p-6 border border-border">
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-3xl font-bold text-foreground mt-2">{stat.value}</p>
                    <p className="text-xs text-primary mt-2">{stat.trend}</p>
                  </Card>
                )) : (
                  <div className="col-span-3 text-center p-8 text-muted-foreground">
                    No summary metrics available
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
