"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  AlertCircle,
  TrendingUp,
  Shield,
  FileText,
  Brain,
  Loader2,
  CheckCircle2,
  XCircle,
  BarChart3,
  Target,
  Lightbulb,
} from "lucide-react"
import {
  analyzeRisk,
  predictCase,
  advancedAnalysis,
  comprehensiveAnalysis,
  analyzeCaseFromText,
  predictBail,
  analyzeLawyerCaseQuick,
  type CaseDetails,
  type CitizenQuickCaseAnalysisResponse,
} from "@/lib/services/analysis"

export default function LawyerCaseAnalysisPage() {
  const [workspaceMode, setWorkspaceMode] = useState<"quick" | "structured">("quick")
  const [quickDescription, setQuickDescription] = useState("")
  const [quickUrgency, setQuickUrgency] = useState<"low" | "medium" | "high">("medium")
  const [quickCity, setQuickCity] = useState("")
  const [quickHearingCourt, setQuickHearingCourt] = useState("")
  const [quickCustody, setQuickCustody] = useState<"in_custody" | "not_in_custody" | "unknown">("unknown")
  const [quickKnownSections, setQuickKnownSections] = useState("")
  const [quickCaseStage, setQuickCaseStage] = useState("")
  const [quickProceduralNotes, setQuickProceduralNotes] = useState("")
  const [quickLoading, setQuickLoading] = useState(false)
  const [quickResults, setQuickResults] = useState<CitizenQuickCaseAnalysisResponse | null>(null)
  const [quickError, setQuickError] = useState<string | null>(null)

  const [loading, setLoading] = useState(false)
  const [analysisType, setAnalysisType] = useState<"risk" | "prediction" | "advanced" | "comprehensive" | "text" | "bail">("comprehensive")
  
  // Form state - Comprehensive fields
  const [sections, setSections] = useState<string>("")
  const [caseDescription, setCaseDescription] = useState<string>("")
  const [evidence, setEvidence] = useState<string>("medium")
  const [evidenceStrength, setEvidenceStrength] = useState<string>("medium")
  const [witnesses, setWitnesses] = useState<number>(0)
  const [previousCases, setPreviousCases] = useState<number>(0)
  const [bailStatus, setBailStatus] = useState<string>("unknown")
  const [clientInCustody, setClientInCustody] = useState<boolean>(false)
  const [lawyerExperience, setLawyerExperience] = useState<number>(0)
  const [proceduralViolations, setProceduralViolations] = useState<boolean>(false)
  const [flightRisk, setFlightRisk] = useState<boolean>(false)
  const [mitigatingFactors, setMitigatingFactors] = useState<string>("")
  const [aggravatingFactors, setAggravatingFactors] = useState<string>("")
  
  // Results state
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      let response

      if (analysisType === "text") {
        const sectionNumbers = sections.split(",").map(s => s.trim()).filter(Boolean)
        response = await analyzeCaseFromText(caseDescription, sectionNumbers.length > 0 ? sectionNumbers : undefined)
      } else if (analysisType === "bail") {
        const sectionList = sections.split(",").map(s => s.trim()).filter(Boolean)
        const mitigating = mitigatingFactors.split(",").map(f => f.trim()).filter(Boolean)
        const aggravating = aggravatingFactors.split(",").map(f => f.trim()).filter(Boolean)
        response = await predictBail(sectionList, mitigating, aggravating)
      } else {
        // Structured analysis - Comprehensive case details
        const caseDetails: CaseDetails = {
          sections: sections.split(",").map(s => s.trim()).filter(Boolean),
          evidence: evidence,
          witnesses: witnesses,
          previous_cases: previousCases,
          bail_status: bailStatus,
          evidence_strength: evidenceStrength,
          case_description: caseDescription || undefined,
          client_in_custody: clientInCustody,
          lawyer_experience: lawyerExperience,
          procedural_violations: proceduralViolations,
          flight_risk: flightRisk,
        }

        switch (analysisType) {
          case "risk":
            response = await analyzeRisk(caseDetails)
            break
          case "prediction":
            response = await predictCase(caseDetails)
            break
          case "advanced":
            response = await advancedAnalysis(caseDetails)
            break
          case "comprehensive":
            response = await comprehensiveAnalysis(caseDetails)
            break
        }
      }

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

  const handleQuickAnalyze = async () => {
    setQuickLoading(true)
    setQuickError(null)
    setQuickResults(null)
    try {
      const response = await analyzeLawyerCaseQuick({
        case_description: quickDescription,
        urgency: quickUrgency,
        city: quickCity,
        hearing_court: quickHearingCourt,
        custody_status: quickCustody,
        known_ppc_sections: quickKnownSections,
        case_stage: quickCaseStage,
        procedural_notes: quickProceduralNotes,
      })
      setQuickResults(response)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Analysis failed. Please try again."
      setQuickError(message)
    } finally {
      setQuickLoading(false)
    }
  }

  return (
    <div className="flex">
      <Sidebar userType="lawyer" />
      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-primary/5 p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">AI Case Analysis</h1>
            <p className="text-muted-foreground mb-4">
              Fast advocate triage uses the same engine as citizen quick analysis, tuned for counsel input. Structured tools
              remain for deep risk and prediction workflows.
            </p>
            <div className="flex flex-wrap gap-2 mb-6">
              <Button variant={workspaceMode === "quick" ? "default" : "outline"} onClick={() => setWorkspaceMode("quick")}>
                Quick case triage
              </Button>
              <Button
                variant={workspaceMode === "structured" ? "default" : "outline"}
                onClick={() => setWorkspaceMode("structured")}
              >
                Structured analysis
              </Button>
            </div>
          </div>

          {workspaceMode === "quick" ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1 space-y-6">
                <Card className="p-6 border border-border/50">
                  <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-primary" />
                    Advocate intake
                  </h2>
                  <div className="space-y-2">
                    <label className="text-sm font-medium mb-2 block">Matter summary / memo *</label>
                    <Textarea
                      value={quickDescription}
                      onChange={(e) => setQuickDescription(e.target.value)}
                      placeholder="FIR sections, key facts, custody status, witness issues, and what you need from triage (same detail you would brief a colleague)…"
                      rows={8}
                    />
                    <label className="text-sm font-medium mb-2 block">Known PPC sections (optional)</label>
                    <Input
                      value={quickKnownSections}
                      onChange={(e) => setQuickKnownSections(e.target.value)}
                      placeholder="e.g. 302, 34 or narrative if already in memo"
                    />
                    <label className="text-sm font-medium mb-2 block">Procedural stage (optional)</label>
                    <Input
                      value={quickCaseStage}
                      onChange={(e) => setQuickCaseStage(e.target.value)}
                      placeholder="Investigation / challan / trial / appeal"
                    />
                    <label className="text-sm font-medium mb-2 block">Tactical / procedural notes (optional)</label>
                    <Textarea
                      value={quickProceduralNotes}
                      onChange={(e) => setQuickProceduralNotes(e.target.value)}
                      placeholder="Illegal search, identification parade issues, remand gaps, disclosure requests…"
                      rows={3}
                    />
                    <label className="text-sm font-medium mb-2 block">Urgency</label>
                    <select
                      value={quickUrgency}
                      onChange={(e) => setQuickUrgency(e.target.value as "low" | "medium" | "high")}
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                    <label className="text-sm font-medium mb-2 block">City (optional)</label>
                    <Input value={quickCity} onChange={(e) => setQuickCity(e.target.value)} placeholder="Lahore" />
                    <label className="text-sm font-medium mb-2 block">Hearing court (optional)</label>
                    <Input
                      value={quickHearingCourt}
                      onChange={(e) => setQuickHearingCourt(e.target.value)}
                      placeholder="Sessions Court"
                    />
                    <label className="text-sm font-medium mb-2 block">Client custody</label>
                    <select
                      value={quickCustody}
                      onChange={(e) =>
                        setQuickCustody(e.target.value as "in_custody" | "not_in_custody" | "unknown")
                      }
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="unknown">Unknown</option>
                      <option value="in_custody">In custody</option>
                      <option value="not_in_custody">Not in custody</option>
                    </select>
                  </div>
                </Card>
                <Card className="p-6 border border-border/50">
                  <h2 className="text-xl font-bold mb-4">Run analysis</h2>
                  <Button
                    onClick={handleQuickAnalyze}
                    disabled={quickLoading || quickDescription.trim().length < 20}
                    className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground"
                  >
                    {quickLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing…
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Analyze matter
                      </>
                    )}
                  </Button>
                  <p className="text-xs text-muted-foreground mt-3">
                    Uses the lawyer quick-analysis API with the same risk guards as citizen quick triage. Add sections and
                    stage for sharper output.
                  </p>
                </Card>
              </div>
              <div className="lg:col-span-2 space-y-6">
                {quickError && (
                  <Card className="p-6 border-destructive/50 bg-destructive/10">
                    <div className="flex items-center gap-2 text-destructive">
                      <XCircle className="w-5 h-5" />
                      <p className="font-semibold">Error: {quickError}</p>
                    </div>
                  </Card>
                )}
                {quickResults && (
                  <>
                    <Card className="p-6 border border-border/50 bg-gradient-to-br from-card to-card/80">
                      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                        <BarChart3 className="w-6 h-6 text-primary" />
                        Case summary
                      </h2>
                      <p className="text-sm text-muted-foreground mb-4">{quickResults.summary}</p>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className={`p-4 rounded-lg border ${getRiskBg(quickResults.risk_score)}`}>
                          <p className="text-sm text-muted-foreground mb-1">Risk score</p>
                          <p className={`text-3xl font-bold ${getRiskColor(quickResults.risk_score)}`}>
                            {quickResults.risk_score}%
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">{quickResults.risk_level} risk</p>
                        </div>
                        <div className="p-4 rounded-lg border border-border/50 bg-card">
                          <p className="text-sm text-muted-foreground mb-1">Likely case type</p>
                          <p className="text-lg font-semibold text-foreground">{quickResults.likely_case_type}</p>
                        </div>
                        <div className="p-4 rounded-lg border border-border/50 bg-card">
                          <p className="text-sm text-muted-foreground mb-1">Extracted sections</p>
                          <p className="text-sm font-semibold text-foreground">
                            {quickResults.extracted_sections.length > 0
                              ? quickResults.extracted_sections.join(", ")
                              : "Not clearly identified"}
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
                        {quickResults.recommendations.map((rec, i) => (
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
                        Immediate next steps
                      </h3>
                      <ul className="space-y-2">
                        {quickResults.next_steps.map((step, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                            <p className="text-sm">{step}</p>
                          </li>
                        ))}
                      </ul>
                      <p className="text-xs text-muted-foreground mt-4">{quickResults.disclaimer}</p>
                    </Card>
                  </>
                )}
                {!quickResults && !quickError && (
                  <Card className="p-12 text-center border border-border/50">
                    <Brain className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                    <p className="text-muted-foreground">
                      Enter your matter memo (and optional sections or stage), then run analysis for fast triage aligned
                      with citizen quick analysis.
                    </p>
                  </Card>
                )}
              </div>
            </div>
          ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-6">
              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  Analysis Type
                </h2>
                <div className="space-y-2">
                  {[
                    { value: "comprehensive", label: "Comprehensive (All-in-One)", icon: Brain },
                    { value: "risk", label: "Risk Analysis", icon: AlertCircle },
                    { value: "prediction", label: "Case Prediction", icon: TrendingUp },
                    { value: "advanced", label: "Advanced Analysis", icon: Target },
                    { value: "text", label: "Text Analysis", icon: FileText },
                    { value: "bail", label: "Bail Prediction", icon: Shield },
                  ].map((type) => (
                    <Button
                      key={type.value}
                      variant={analysisType === type.value ? "default" : "outline"}
                      onClick={() => setAnalysisType(type.value as any)}
                      className="w-full justify-start"
                    >
                      <type.icon className="w-4 h-4 mr-2" />
                      {type.label}
                    </Button>
                  ))}
                </div>
              </Card>

              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4">Case Details</h2>
                <div className="space-y-4">
                  {analysisType === "text" ? (
                    <div>
                      <label className="text-sm font-medium mb-2 block">Case Description</label>
                      <Textarea
                        value={caseDescription}
                        onChange={(e) => setCaseDescription(e.target.value)}
                        placeholder="Describe your case in detail..."
                        rows={6}
                        className="w-full"
                      />
                      <label className="text-sm font-medium mb-2 block mt-4">Section Numbers (optional)</label>
                      <Input
                        value={sections}
                        onChange={(e) => setSections(e.target.value)}
                        placeholder="302, 34, 109"
                      />
                    </div>
                  ) : analysisType === "bail" ? (
                    <>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Section Numbers</label>
                        <Input
                          value={sections}
                          onChange={(e) => setSections(e.target.value)}
                          placeholder="302, 34, 109"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Mitigating Factors</label>
                        <Textarea
                          value={mitigatingFactors}
                          onChange={(e) => setMitigatingFactors(e.target.value)}
                          placeholder="First time offender, good character"
                          rows={3}
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Aggravating Factors</label>
                        <Textarea
                          value={aggravatingFactors}
                          onChange={(e) => setAggravatingFactors(e.target.value)}
                          placeholder="Previous convictions, flight risk"
                          rows={3}
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      {/* Basic Information */}
                      <div className="space-y-4">
                        <h3 className="font-semibold text-foreground border-b pb-2">Basic Information</h3>
                        
                        <div>
                          <label className="text-sm font-medium mb-2 block">
                            Section Numbers (comma-separated) <span className="text-destructive">*</span>
                          </label>
                          <Input
                            value={sections}
                            onChange={(e) => setSections(e.target.value)}
                            placeholder="302, 34, 109"
                            required
                          />
                          <p className="text-xs text-muted-foreground mt-1">Enter PPC section numbers involved in the case</p>
                        </div>

                        <div>
                          <label className="text-sm font-medium mb-2 block">Case Description (Optional)</label>
                          <Textarea
                            value={caseDescription}
                            onChange={(e) => setCaseDescription(e.target.value)}
                            placeholder="Brief description of the case circumstances..."
                            rows={3}
                            className="w-full"
                          />
                        </div>
                      </div>

                      {/* Evidence & Witnesses */}
                      <div className="space-y-4 pt-4 border-t">
                        <h3 className="font-semibold text-foreground border-b pb-2">Evidence & Witnesses</h3>
                        
                        <div>
                          <label className="text-sm font-medium mb-2 block">Evidence Type</label>
                          <select
                            value={evidence}
                            onChange={(e) => setEvidence(e.target.value)}
                            className="w-full px-3 py-2 border rounded-md bg-background"
                          >
                            <option value="weak">Weak Evidence</option>
                            <option value="medium">Medium Evidence</option>
                            <option value="strong">Strong Evidence</option>
                            <option value="direct">Direct Evidence</option>
                            <option value="circumstantial">Circumstantial Evidence</option>
                          </select>
                        </div>

                        <div>
                          <label className="text-sm font-medium mb-2 block">Evidence Strength</label>
                          <select
                            value={evidenceStrength}
                            onChange={(e) => setEvidenceStrength(e.target.value)}
                            className="w-full px-3 py-2 border rounded-md bg-background"
                          >
                            <option value="weak">Weak</option>
                            <option value="medium">Medium</option>
                            <option value="strong">Strong</option>
                          </select>
                        </div>

                        <div>
                          <label className="text-sm font-medium mb-2 block">Number of Witnesses</label>
                          <Input
                            type="number"
                            value={witnesses}
                            onChange={(e) => setWitnesses(parseInt(e.target.value) || 0)}
                            min="0"
                            placeholder="0"
                          />
                          <p className="text-xs text-muted-foreground mt-1">Total number of prosecution witnesses</p>
                        </div>
                      </div>

                      {/* Case History & Status */}
                      <div className="space-y-4 pt-4 border-t">
                        <h3 className="font-semibold text-foreground border-b pb-2">Case History & Status</h3>
                        
                        <div>
                          <label className="text-sm font-medium mb-2 block">Previous Convictions</label>
                          <Input
                            type="number"
                            value={previousCases}
                            onChange={(e) => setPreviousCases(parseInt(e.target.value) || 0)}
                            min="0"
                            placeholder="0"
                          />
                          <p className="text-xs text-muted-foreground mt-1">Number of previous criminal cases/convictions</p>
                        </div>

                        <div>
                          <label className="text-sm font-medium mb-2 block">Current Bail Status</label>
                          <select
                            value={bailStatus}
                            onChange={(e) => setBailStatus(e.target.value)}
                            className="w-full px-3 py-2 border rounded-md bg-background"
                          >
                            <option value="unknown">Unknown</option>
                            <option value="granted">Bail Granted</option>
                            <option value="rejected">Bail Rejected</option>
                            <option value="pending">Bail Pending</option>
                            <option value="not_applied">Not Applied</option>
                          </select>
                        </div>

                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            id="clientInCustody"
                            checked={clientInCustody}
                            onChange={(e) => setClientInCustody(e.target.checked)}
                            className="w-4 h-4"
                          />
                          <label htmlFor="clientInCustody" className="text-sm font-medium cursor-pointer">
                            Client Currently in Custody
                          </label>
                        </div>
                      </div>

                      {/* Legal Representation */}
                      <div className="space-y-4 pt-4 border-t">
                        <h3 className="font-semibold text-foreground border-b pb-2">Legal Representation</h3>
                        
                        <div>
                          <label className="text-sm font-medium mb-2 block">Lawyer Experience (Years)</label>
                          <Input
                            type="number"
                            value={lawyerExperience}
                            onChange={(e) => setLawyerExperience(parseInt(e.target.value) || 0)}
                            min="0"
                            placeholder="0"
                          />
                          <p className="text-xs text-muted-foreground mt-1">Years of experience of the defense lawyer</p>
                        </div>
                      </div>

                      {/* Risk Factors */}
                      <div className="space-y-4 pt-4 border-t">
                        <h3 className="font-semibold text-foreground border-b pb-2">Risk Factors</h3>
                        
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            id="proceduralViolations"
                            checked={proceduralViolations}
                            onChange={(e) => setProceduralViolations(e.target.checked)}
                            className="w-4 h-4"
                          />
                          <label htmlFor="proceduralViolations" className="text-sm font-medium cursor-pointer">
                            Procedural Violations Detected
                          </label>
                        </div>
                        <p className="text-xs text-muted-foreground ml-6">Any violations in investigation or arrest procedure</p>

                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            id="flightRisk"
                            checked={flightRisk}
                            onChange={(e) => setFlightRisk(e.target.checked)}
                            className="w-4 h-4"
                          />
                          <label htmlFor="flightRisk" className="text-sm font-medium cursor-pointer">
                            Flight Risk
                          </label>
                        </div>
                        <p className="text-xs text-muted-foreground ml-6">Risk of accused absconding or fleeing</p>
                      </div>
                    </>
                  )}

                  <Button
                    onClick={handleAnalyze}
                    disabled={loading || (!sections && analysisType !== "text")}
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
                        Analyze Case
                      </>
                    )}
                  </Button>
                </div>
              </Card>
            </div>

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
                  {results.summary && (
                    <Card className="p-6 border border-border/50 bg-gradient-to-br from-card to-card/80">
                      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                        <BarChart3 className="w-6 h-6 text-primary" />
                        Analysis Summary
                      </h2>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {results.summary.overall_risk !== undefined && (
                          <div className={`p-4 rounded-lg border ${getRiskBg(results.summary.overall_risk)}`}>
                            <p className="text-sm text-muted-foreground mb-1">Overall Risk</p>
                            <p className={`text-3xl font-bold ${getRiskColor(results.summary.overall_risk)}`}>
                              {results.summary.overall_risk}%
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">{results.summary.risk_level}</p>
                          </div>
                        )}
                        {results.summary.conviction_probability !== undefined && (
                          <div className="p-4 rounded-lg border border-border/50 bg-card">
                            <p className="text-sm text-muted-foreground mb-1">Conviction Probability</p>
                            <p className="text-3xl font-bold text-foreground">
                              {Math.round(results.summary.conviction_probability * 100)}%
                            </p>
                          </div>
                        )}
                        {results.summary.bail_probability !== undefined && (
                          <div className="p-4 rounded-lg border border-border/50 bg-card">
                            <p className="text-sm text-muted-foreground mb-1">Bail Probability</p>
                            <p className="text-3xl font-bold text-foreground">
                              {Math.round(results.summary.bail_probability * 100)}%
                            </p>
                          </div>
                        )}
                        {results.summary.immediate_action && (
                          <div className="p-4 rounded-lg border border-primary/50 bg-primary/10">
                            <p className="text-sm text-muted-foreground mb-1">Immediate Action</p>
                            <p className="text-sm font-semibold text-foreground">{results.summary.immediate_action}</p>
                          </div>
                        )}
                      </div>
                    </Card>
                  )}

                  {results.risk_assessment && (
                    <Card className="p-6 border border-border/50">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-primary" />
                        Risk Assessment
                      </h3>
                      <div className={`p-4 rounded-lg border mb-4 ${getRiskBg(results.risk_assessment.overall_risk)}`}>
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-muted-foreground">Overall Risk Score</p>
                            <p className={`text-4xl font-bold ${getRiskColor(results.risk_assessment.overall_risk)}`}>
                              {results.risk_assessment.overall_risk}%
                            </p>
                            <p className="text-sm text-muted-foreground mt-1">Risk Level: {results.risk_assessment.risk_level}</p>
                          </div>
                        </div>
                      </div>
                      {results.risk_assessment.factors && (
                        <div className="space-y-2 mb-4">
                          <p className="font-semibold">Risk Factors:</p>
                          {results.risk_assessment.factors.map((factor: any, i: number) => (
                            <div key={i} className="p-3 bg-muted/50 rounded-lg">
                              <div className="flex justify-between items-start mb-1">
                                <p className="font-medium">{factor.factor}</p>
                                <span className="text-sm text-muted-foreground">Impact: {factor.impact}%</span>
                              </div>
                              <p className="text-sm text-muted-foreground">{factor.description}</p>
                            </div>
                          ))}
                        </div>
                      )}
                      {results.risk_assessment.recommendations && (
                        <div>
                          <p className="font-semibold mb-2 flex items-center gap-2">
                            <Lightbulb className="w-4 h-4" />
                            Recommendations:
                          </p>
                          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                            {results.risk_assessment.recommendations.map((rec: string, i: number) => (
                              <li key={i}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </Card>
                  )}

                  {results.predictions && (
                    <Card className="p-6 border border-border/50">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-primary" />
                        Case Predictions
                      </h3>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="p-4 rounded-lg border border-border/50">
                          <p className="text-sm text-muted-foreground mb-1">Conviction Probability</p>
                          <p className="text-2xl font-bold text-foreground">
                            {Math.round((results.predictions.conviction_probability || 0) * 100)}%
                          </p>
                        </div>
                        <div className="p-4 rounded-lg border border-border/50">
                          <p className="text-sm text-muted-foreground mb-1">Bail Probability</p>
                          <p className="text-2xl font-bold text-foreground">
                            {Math.round((results.predictions.bail_probability || 0) * 100)}%
                          </p>
                        </div>
                      </div>
                      {results.predictions.sentence_prediction && (
                        <div className="p-4 rounded-lg border border-border/50 mb-4">
                          <p className="text-sm text-muted-foreground mb-1">Sentence Prediction</p>
                          <p className="font-medium">{results.predictions.sentence_prediction}</p>
                        </div>
                      )}
                      {results.predictions.timeline_prediction && (
                        <div className="p-4 rounded-lg border border-border/50">
                          <p className="text-sm text-muted-foreground mb-1">Timeline Prediction</p>
                          <p className="font-medium">{results.predictions.timeline_prediction}</p>
                        </div>
                      )}
                    </Card>
                  )}

                  {results.recommendations && results.recommendations.length > 0 && (
                    <Card className="p-6 border border-border/50">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Target className="w-5 h-5 text-primary" />
                        Recommendations
                      </h3>
                      <ul className="space-y-2">
                        {results.recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex items-start gap-2">
                            <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                            <p className="text-sm">{rec}</p>
                          </li>
                        ))}
                      </ul>
                    </Card>
                  )}

                  {results.bail_prediction && (
                    <Card className="p-6 border border-border/50">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-primary" />
                        Bail Prediction
                      </h3>
                      <div className={`p-4 rounded-lg border mb-4 ${getRiskBg(results.bail_prediction.likelihood)}`}>
                        <p className="text-sm text-muted-foreground mb-1">Bail Likelihood</p>
                        <p className={`text-4xl font-bold ${getRiskColor(100 - results.bail_prediction.likelihood)}`}>
                          {results.bail_prediction.likelihood}%
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">{results.bail_prediction.probability}</p>
                      </div>
                      <p className="font-medium mb-2">{results.bail_prediction.recommendation}</p>
                      {results.bail_prediction.factors && results.bail_prediction.factors.length > 0 && (
                        <div>
                          <p className="text-sm font-semibold mb-2">Key Factors:</p>
                          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                            {results.bail_prediction.factors.map((factor: string, i: number) => (
                              <li key={i}>{factor}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </Card>
                  )}
                </>
              )}

              {!results && !error && (
                <Card className="p-12 text-center border border-border/50">
                  <Brain className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                  <p className="text-muted-foreground">Fill in the case details and click "Analyze Case" to get AI-powered analysis</p>
                </Card>
              )}
            </div>
          </div>
          )}
        </div>
      </main>
    </div>
  )
}

