"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { AlertCircle, Brain, Loader2, CheckCircle2, XCircle, BarChart3, Lightbulb } from "lucide-react"
import {
  analyzeCitizenCaseQuick,
  type CitizenQuickCaseAnalysisResponse,
} from "@/lib/services/analysis"

export default function CaseAnalysisPage() {
  const [loading, setLoading] = useState(false)
  const [caseDescription, setCaseDescription] = useState("")
  const [urgency, setUrgency] = useState<"low" | "medium" | "high">("medium")
  const [city, setCity] = useState("")
  const [hearingCourt, setHearingCourt] = useState("")
  const [custodyStatus, setCustodyStatus] = useState<"in_custody" | "not_in_custody" | "unknown">("unknown")
  const [results, setResults] = useState<CitizenQuickCaseAnalysisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await analyzeCitizenCaseQuick({
        case_description: caseDescription,
        urgency,
        city,
        hearing_court: hearingCourt,
        custody_status: custodyStatus,
      })
      setResults(response)
    } catch (err: any) {
      setError(err.message || "Analysis failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (risk: number) => {
    if (risk >= 80) return "text-destructive"
    if (risk >= 60) return "text-orange-500"
    if (risk >= 40) return "text-yellow-500"
    return "text-green-500"
  }

  const getRiskBg = (risk: number) => {
    if (risk >= 80) return "bg-destructive/20 border-destructive/50"
    if (risk >= 60) return "bg-orange-500/20 border-orange-500/50"
    if (risk >= 40) return "bg-yellow-500/20 border-yellow-500/50"
    return "bg-green-500/20 border-green-500/50"
  }

  return (
    <div className="flex">
      <Sidebar userType="citizen" />
      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-primary/5 p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">Simple Case Analysis</h1>
            <p className="text-muted-foreground">
              Describe your situation in normal language. The system will extract legal sections and give fast guidance.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Form */}
            <div className="lg:col-span-1 space-y-6">
              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  Citizen Input
                </h2>
                <div className="space-y-2">
                  <label className="text-sm font-medium mb-2 block">Case Description *</label>
                  <Textarea
                    value={caseDescription}
                    onChange={(e) => setCaseDescription(e.target.value)}
                    placeholder="Example: Police arrested my brother in a cyber fraud case. FIR says section 420. We need bail and hearing is next week..."
                    rows={8}
                  />
                  <div>
                    <label className="text-sm font-medium mb-2 block">Urgency</label>
                    <select
                      value={urgency}
                      onChange={(e) => setUrgency(e.target.value as "low" | "medium" | "high")}
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">City (optional)</label>
                    <Input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Islamabad" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Hearing Court (optional)</label>
                    <Input
                      value={hearingCourt}
                      onChange={(e) => setHearingCourt(e.target.value)}
                      placeholder="Sessions Court"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Custody Status</label>
                    <select
                      value={custodyStatus}
                      onChange={(e) =>
                        setCustodyStatus(e.target.value as "in_custody" | "not_in_custody" | "unknown")
                      }
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="unknown">Unknown</option>
                      <option value="in_custody">In Custody</option>
                      <option value="not_in_custody">Not in Custody</option>
                    </select>
                  </div>
                </div>
              </Card>

              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4">Run Fast Analysis</h2>
                <div className="space-y-4">
                  <Button
                    onClick={handleAnalyze}
                    disabled={loading || caseDescription.trim().length < 20}
                    className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground mt-6"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Analyze My Case
                      </>
                    )}
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    Tip: write full story in simple words. No need to know legal sections.
                  </p>
                </div>
              </Card>
            </div>

            {/* Results */}
            <div className="lg:col-span-2 space-y-6">
              {error && (
                <Card className="p-6 border-destructive/50 bg-destructive/10">
                  <div className="flex items-center gap-2 text-destructive">
                    <XCircle className="w-5 h-5" />
                    <p className="font-semibold">Error: {error}</p>
                  </div>
                </Card>
              )}

              {results && (
                <>
                  <Card className="p-6 border border-border/50 bg-gradient-to-br from-card to-card/80">
                    <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                      <BarChart3 className="w-6 h-6 text-primary" />
                      Case Summary
                    </h2>
                    <p className="text-sm text-muted-foreground mb-4">{results.summary}</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className={`p-4 rounded-lg border ${getRiskBg(results.risk_score)}`}>
                        <p className="text-sm text-muted-foreground mb-1">Risk Score</p>
                        <p className={`text-3xl font-bold ${getRiskColor(results.risk_score)}`}>{results.risk_score}%</p>
                        <p className="text-xs text-muted-foreground mt-1">{results.risk_level} Risk</p>
                      </div>
                      <div className="p-4 rounded-lg border border-border/50 bg-card">
                        <p className="text-sm text-muted-foreground mb-1">Likely Case Type</p>
                        <p className="text-lg font-semibold text-foreground">{results.likely_case_type}</p>
                      </div>
                      <div className="p-4 rounded-lg border border-border/50 bg-card">
                        <p className="text-sm text-muted-foreground mb-1">Extracted Sections</p>
                        <p className="text-sm font-semibold text-foreground">
                          {results.extracted_sections.length > 0 ? results.extracted_sections.join(", ") : "Not clearly identified"}
                        </p>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-6 border border-border/50">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <Lightbulb className="w-5 h-5 text-primary" />
                      Recommendations
                    </h3>
                    <ul className="space-y-2">
                      {results.recommendations.map((rec, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{rec}</p>
                        </li>
                      ))}
                    </ul>
                  </Card>

                  <Card className="p-6 border border-border/50">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-primary" />
                      Immediate Next Steps
                    </h3>
                    <ul className="space-y-2">
                      {results.next_steps.map((step, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{step}</p>
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs text-muted-foreground mt-4">{results.disclaimer}</p>
                  </Card>
                </>
              )}

              {!results && !error && (
                <Card className="p-12 text-center border border-border/50">
                  <Brain className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                  <p className="text-muted-foreground">
                    Write your issue in simple words and click "Analyze My Case" for fast guidance.
                  </p>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

