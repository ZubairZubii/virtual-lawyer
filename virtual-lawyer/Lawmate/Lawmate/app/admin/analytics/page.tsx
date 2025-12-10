"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"
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
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { getAnalytics, type AnalyticsResponse } from "@/lib/services/analytics"

export default function AdminAnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      const data = await getAnalytics(30)
      setAnalytics(data)
    } catch (err: any) {
      setError(err.message || "Failed to load analytics")
    } finally {
      setLoading(false)
    }
  }

  // Query volume data from backend
  const queryVolumeData = analytics?.trends?.query_volume?.map(v => ({
    month: new Date(v.date).toLocaleDateString('en-US', { month: 'short' }),
    queries: v.count
  })) || [
    { month: "Jan", queries: 150 },
    { month: "Feb", queries: 280 },
    { month: "Mar", queries: 420 },
    { month: "Apr", queries: 580 },
    { month: "May", queries: 890 },
    { month: "Jun", queries: 1200 },
  ]

  // Quality trend data from backend
  const qualityTrendData = analytics?.trends?.quality_trend?.map(v => ({
    month: new Date(v.date).toLocaleDateString('en-US', { month: 'short' }),
    quality: v.avg_quality
  })) || []

  // Case type distribution - using top sections from backend
  const caseTypeData = analytics?.popular_topics?.top_sections?.slice(0, 4).map((s, i) => ({
    name: `Section ${s.section}`,
    value: s.count,
    fill: i === 0 ? "var(--color-primary)" : i === 1 ? "var(--color-accent)" : i === 2 ? "var(--color-secondary)" : "var(--color-chart-4)"
  })) || [
    { name: "Bail Applications", value: 420, fill: "var(--color-primary)" },
    { name: "Appeals", value: 280, fill: "var(--color-accent)" },
    { name: "Evidence Review", value: 190, fill: "var(--color-secondary)" },
    { name: "Remand Challenges", value: 165, fill: "var(--color-chart-4)" },
  ]

  // Most searched queries from backend
  const queryData = analytics?.popular_topics?.top_keywords?.slice(0, 5).map(k => ({
    query: k.keyword,
    count: k.count
  })) || [
    { query: "Bail process", count: 1240 },
    { query: "Constitutional rights", count: 890 },
    { query: "FIR procedures", count: 756 },
    { query: "Appeal process", count: 634 },
    { query: "Evidence submission", count: 542 },
  ]

  if (loading) {
    return (
      <div className="flex">
        <Sidebar userType="admin" />
        <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading analytics...</p>
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex">
        <Sidebar userType="admin" />
        <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background p-8">
          <Card className="p-6 border-destructive/50 bg-destructive/10">
            <p className="text-destructive font-semibold">Error: {error}</p>
            <Button onClick={loadAnalytics} className="mt-4">Retry</Button>
          </Card>
        </main>
      </div>
    )
  }

  return (
    <div className="flex">
      <Sidebar userType="admin" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Platform Analytics</h1>
              <p className="text-muted-foreground mt-2">System-wide metrics and usage statistics</p>
            </div>
            <Button onClick={loadAnalytics} variant="outline">
              Refresh
            </Button>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Query Volume Trend */}
            <Card className="p-6 border border-border">
              <h2 className="text-lg font-semibold text-foreground mb-4">Query Volume Trend</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={queryVolumeData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="month" stroke="var(--color-muted-foreground)" />
                  <YAxis stroke="var(--color-muted-foreground)" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--color-card)",
                      border: `1px solid var(--color-border)`,
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="queries" stroke="var(--color-primary)" strokeWidth={2} name="Queries" />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            {/* Section Distribution */}
            <Card className="p-6 border border-border">
              <h2 className="text-lg font-semibold text-foreground mb-4">Top Sections Queried</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={caseTypeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    dataKey="value"
                  >
                    {caseTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--color-card)",
                      border: `1px solid var(--color-border)`,
                      borderRadius: "0.5rem",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Most Searched Queries */}
          <Card className="p-6 border border-border mb-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">Most Searched Queries</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={queryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis stroke="var(--color-muted-foreground)" dataKey="query" />
                <YAxis stroke="var(--color-muted-foreground)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-card)",
                    border: `1px solid var(--color-border)`,
                    borderRadius: "0.5rem",
                  }}
                />
                <Bar dataKey="count" fill="var(--color-primary)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="p-6 border border-border">
              <p className="text-sm text-muted-foreground">Total Queries</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {analytics?.overview?.total_queries || 0}
              </p>
              <p className="text-xs text-primary mt-2">
                {analytics?.overview?.unique_sessions || 0} sessions
              </p>
            </Card>
            <Card className="p-6 border border-border">
              <p className="text-sm text-muted-foreground">Avg. Response Time</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {analytics?.overview?.avg_response_time?.toFixed(2) || "0.00"}s
              </p>
              <p className="text-xs text-primary mt-2">
                {analytics?.performance?.fast_responses || 0} fast responses
              </p>
            </Card>
            <Card className="p-6 border border-border">
              <p className="text-sm text-muted-foreground">RAG Usage Rate</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {analytics?.overview?.rag_usage_rate?.toFixed(1) || 0}%
              </p>
              <p className="text-xs text-primary mt-2">
                {analytics?.overview?.total_sources_retrieved || 0} sources retrieved
              </p>
            </Card>
            <Card className="p-6 border border-border">
              <p className="text-sm text-muted-foreground">Quality Score</p>
              <p className="text-3xl font-bold text-foreground mt-2">
                {analytics?.quality_insights?.avg_quality_score?.toFixed(1) || "0.0"}
              </p>
              <p className="text-xs text-primary mt-2">
                {analytics?.quality_insights?.answers_with_legal_terms || 0} with legal terms
              </p>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
