"use client"

import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
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
import { uploadDocument } from "@/lib/services/documents"
import { getCaseDetails } from "@/lib/services/cases"
import { listUserDocuments, getSummary } from "@/lib/services/documents"

export default function CaseAnalysisPage() {
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)
  const [caseDescription, setCaseDescription] = useState("")
  const [urgency, setUrgency] = useState<"low" | "medium" | "high">("medium")
  const [city, setCity] = useState("")
  const [hearingCourt, setHearingCourt] = useState("")
  const [custodyStatus, setCustodyStatus] = useState<"in_custody" | "not_in_custody" | "unknown">("unknown")
  const [caseStage, setCaseStage] = useState("")
  const [incidentDate, setIncidentDate] = useState("")
  const [incidentLocation, setIncidentLocation] = useState("")
  const [firApplicability, setFirApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [firStatus, setFirStatus] = useState("")
  const [policeStation, setPoliceStation] = useState("")
  const [witnessApplicability, setWitnessApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [witnessStatus, setWitnessStatus] = useState("")
  const [witnessCount, setWitnessCount] = useState(0)
  const [evidenceApplicability, setEvidenceApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [evidenceSummary, setEvidenceSummary] = useState("")
  const [documentsApplicability, setDocumentsApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [availableDocuments, setAvailableDocuments] = useState("")
  const [keyQuestion, setKeyQuestion] = useState("")
  const [desiredOutcome, setDesiredOutcome] = useState("")
  const [childInvolved, setChildInvolved] = useState(false)
  const [results, setResults] = useState<CitizenQuickCaseAnalysisResponse | null>(null)
  const [uploadedDocs, setUploadedDocs] = useState<Array<{ doc_id: string; file_name: string }>>([])
  const [prefillLoading, setPrefillLoading] = useState(false)
  const [docsLoading, setDocsLoading] = useState(false)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [userDocuments, setUserDocuments] = useState<Array<{ doc_id: string; file_name: string }>>([])
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])
  const [docSummaries, setDocSummaries] = useState<Record<string, string>>({})
  const [error, setError] = useState<string | null>(null)
  const [docLimitError, setDocLimitError] = useState<string | null>(null)

  const MAX_ONBOARD_DOCS = 2
  const MAX_SELECTED_CASE_DOCS = 4

  const handleDocUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setDocLimitError(null)
    const existingCount = uploadedDocs.length
    const allowed = Math.max(0, MAX_ONBOARD_DOCS - existingCount)
    if (allowed <= 0) {
      setDocLimitError(`You can upload up to ${MAX_ONBOARD_DOCS} documents in onboarding.`)
      return
    }
    const selected = Array.from(files).slice(0, allowed)
    try {
      const userRaw = typeof window !== "undefined" ? localStorage.getItem("user") : null
      const user = userRaw ? JSON.parse(userRaw) : {}
      const uploaded = await Promise.all(
        selected.map((f) =>
          uploadDocument(f, {
            email: user?.email || "",
            role: "citizen",
          }),
        ),
      )
      setUploadedDocs((prev) => [...prev, ...uploaded.map((u) => ({ doc_id: u.doc_id, file_name: u.file_name }))])
      if (files.length > allowed) {
        setDocLimitError(`Only ${allowed} file(s) uploaded due to onboarding limit.`)
      }
    } catch (err: any) {
      setError(err.message || "Failed to upload document(s).")
    }
  }

  useEffect(() => {
    const caseId = searchParams.get("caseId")
    if (!caseId) return

    const prefillCase = async () => {
      setPrefillLoading(true)
      try {
        const details = await getCaseDetails(caseId)
        setCaseDescription(details.description || "")
        setHearingCourt(details.court || "")
        setIncidentDate(details.filing_date || "")
        setCaseStage((details.status as string) || "")
        setFirStatus(details.fir_number ? "registered" : "")
        setPoliceStation(details.police_station || "")
        if (details.fir_number) setFirApplicability("applicable")
        setKeyQuestion(`Please analyze this case (${details.case_type || "criminal matter"}) and suggest best legal steps.`)
        setDesiredOutcome("Best legal strategy and next steps")
      } catch (err: any) {
        setError(err.message || "Failed to auto-load case details.")
      } finally {
        setPrefillLoading(false)
      }
    }

    void prefillCase()
  }, [searchParams])

  useEffect(() => {
    const loadUserDocs = async () => {
      try {
        setDocsLoading(true)
        const userRaw = typeof window !== "undefined" ? localStorage.getItem("user") : null
        const user = userRaw ? JSON.parse(userRaw) : {}
        const listed = await listUserDocuments(user?.email || "", "citizen")
        const docs = (listed.documents || []).map((d) => ({ doc_id: d.doc_id, file_name: d.file_name }))
        setUserDocuments(docs)
      } catch {
        // Non-blocking UX: ignore document-list fetch failures
      } finally {
        setDocsLoading(false)
      }
    }
    void loadUserDocs()
  }, [])

  useEffect(() => {
    const runDocSummary = async () => {
      if (selectedDocIds.length === 0) return
      try {
        setSummaryLoading(true)
        const selected = selectedDocIds.slice(0, MAX_SELECTED_CASE_DOCS)
        const entries = await Promise.all(
          selected.map(async (docId) => {
            const res = await getSummary(docId)
            return [docId, res.summary || "No summary available"] as const
          }),
        )
        const next: Record<string, string> = {}
        for (const [docId, summary] of entries) next[docId] = summary
        setDocSummaries(next)
      } catch {
        // Keep flow resilient even if one summary call fails
      } finally {
        setSummaryLoading(false)
      }
    }
    void runDocSummary()
  }, [selectedDocIds])

  const toggleSelectedDoc = (docId: string) => {
    setSelectedDocIds((prev) => {
      if (prev.includes(docId)) return prev.filter((id) => id !== docId)
      if (prev.length >= MAX_SELECTED_CASE_DOCS) return prev
      return [...prev, docId]
    })
  }

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const effectiveFirStatus =
        firApplicability === "not_applicable" ? "not_applicable" : firStatus || firApplicability
      const effectiveWitnessStatus =
        witnessApplicability === "not_applicable" ? "not_applicable" : witnessStatus || witnessApplicability
      const effectiveWitnessCount = witnessApplicability === "applicable" ? witnessCount : 0
      const effectiveEvidenceSummary =
        evidenceApplicability === "not_applicable" ? "not_applicable" : evidenceSummary
      const selectedDocNames = userDocuments
        .filter((d) => selectedDocIds.includes(d.doc_id))
        .map((d) => d.file_name)
      const quickDocSummary = selectedDocIds
        .map((id) => docSummaries[id])
        .filter(Boolean)
        .join(" ")
      const effectiveDocuments =
        documentsApplicability === "not_applicable"
          ? "not_applicable"
          : uploadedDocs.length > 0
            ? uploadedDocs.map((d) => d.file_name).join(", ")
            : selectedDocNames.length > 0
              ? selectedDocNames.join(", ")
              : availableDocuments

      const response = await analyzeCitizenCaseQuick({
        case_description: `${caseDescription}${quickDocSummary ? `\n\nDocument quick summary:\n${quickDocSummary}` : ""}`,
        urgency,
        city,
        hearing_court: hearingCourt,
        custody_status: custodyStatus,
        case_stage: caseStage,
        incident_date: incidentDate,
        incident_location: incidentLocation,
        fir_status: effectiveFirStatus,
        police_station: policeStation,
        witness_status: effectiveWitnessStatus,
        witness_count: effectiveWitnessCount,
        evidence_summary:
          quickDocSummary && effectiveEvidenceSummary !== "not_applicable"
            ? `${effectiveEvidenceSummary}\n\nDocument summary: ${quickDocSummary}`
            : effectiveEvidenceSummary,
        available_documents: effectiveDocuments,
        key_question: keyQuestion,
        desired_outcome: desiredOutcome,
        child_involved: childInvolved,
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
            <h1 className="text-4xl font-bold text-foreground mb-2">Case Analysis</h1>
            <p className="text-muted-foreground">
              Add full case facts in simple language. More details give more accurate Pakistan criminal-law guidance.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Form */}
            <div className="lg:col-span-1 space-y-6">
              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  Case Onboarding
                </h2>
                <div className="space-y-2">
                  <label className="text-sm font-medium mb-2 block">Case Description *</label>
                  <Textarea
                    value={caseDescription}
                    onChange={(e) => setCaseDescription(e.target.value)}
                    placeholder="Write complete timeline: what happened, when, where, who was involved, what police did, and what help you need."
                    rows={8}
                  />
                  <div>
                    <label className="text-sm font-medium mb-2 block">Main Legal Question (optional)</label>
                    <Input
                      value={keyQuestion}
                      onChange={(e) => setKeyQuestion(e.target.value)}
                      placeholder="e.g., Police refused FIR. What is my next legal remedy?"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Related Documents (max 2)</label>
                    <Input
                      type="file"
                      multiple
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={(e) => void handleDocUpload(e.target.files)}
                    />
                    {docLimitError && <p className="text-xs text-orange-500 mt-1">{docLimitError}</p>}
                    {uploadedDocs.length > 0 && (
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        {uploadedDocs.map((doc) => (
                          <li key={doc.doc_id}>Uploaded: {doc.file_name}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                  {prefillLoading && (
                    <p className="text-xs text-muted-foreground">Loading selected case details...</p>
                  )}
                  <div className="mt-3 p-3 border rounded-lg bg-card">
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <p className="text-sm font-semibold">Case Documents</p>
                      <p className="text-xs text-muted-foreground">Select up to {MAX_SELECTED_CASE_DOCS} for analysis</p>
                    </div>
                    {docsLoading ? (
                      <p className="text-xs text-muted-foreground">Loading your documents...</p>
                    ) : userDocuments.length === 0 ? (
                      <p className="text-xs text-muted-foreground">No saved documents found. Upload above if needed.</p>
                    ) : (
                      <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                        {userDocuments.map((doc) => (
                          <label key={doc.doc_id} className="flex items-start gap-2 text-xs">
                            <input
                              type="checkbox"
                              className="mt-0.5"
                              checked={selectedDocIds.includes(doc.doc_id)}
                              onChange={() => toggleSelectedDoc(doc.doc_id)}
                              disabled={!selectedDocIds.includes(doc.doc_id) && selectedDocIds.length >= MAX_SELECTED_CASE_DOCS}
                            />
                            <span className="text-muted-foreground break-words">{doc.file_name}</span>
                          </label>
                        ))}
                      </div>
                    )}
                    {summaryLoading && <p className="text-xs text-muted-foreground mt-2">Generating quick summaries...</p>}
                    {!summaryLoading && selectedDocIds.length > 0 && (
                      <div className="mt-2 space-y-2">
                        <p className="text-xs font-medium">Quick Summary (auto)</p>
                        {selectedDocIds.map((docId) => (
                          <div key={docId} className="p-2 rounded border text-xs text-muted-foreground">
                            {docSummaries[docId] || "Summary not available yet."}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
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
                  <div>
                    <label className="text-sm font-medium mb-2 block">Case Stage</label>
                    <Input
                      value={caseStage}
                      onChange={(e) => setCaseStage(e.target.value)}
                      placeholder="Pre-FIR / Post-FIR / Investigation / Trial"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Incident Date (optional)</label>
                    <Input type="date" value={incidentDate} onChange={(e) => setIncidentDate(e.target.value)} />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Incident Location</label>
                    <Input
                      value={incidentLocation}
                      onChange={(e) => setIncidentLocation(e.target.value)}
                      placeholder="Area, city, place of incident"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">FIR Relevance</label>
                    <select
                      value={firApplicability}
                      onChange={(e) =>
                        setFirApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")
                      }
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="unknown">Unknown</option>
                      <option value="applicable">Applicable</option>
                      <option value="not_applicable">Not applicable in this case</option>
                    </select>
                  </div>
                  {firApplicability === "applicable" && (
                    <>
                      <div>
                        <label className="text-sm font-medium mb-2 block">FIR Status</label>
                        <Input
                          value={firStatus}
                          onChange={(e) => setFirStatus(e.target.value)}
                          placeholder="Registered / Refused / Under process"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Police Station (optional)</label>
                        <Input
                          value={policeStation}
                          onChange={(e) => setPoliceStation(e.target.value)}
                          placeholder="e.g., Civil Lines Police Station"
                        />
                      </div>
                    </>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Witness Relevance</label>
                    <select
                      value={witnessApplicability}
                      onChange={(e) =>
                        setWitnessApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")
                      }
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="unknown">Unknown</option>
                      <option value="applicable">Applicable</option>
                      <option value="not_applicable">No witness needed in this case</option>
                    </select>
                  </div>
                  {witnessApplicability === "applicable" && (
                    <>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Witness Status</label>
                        <Input
                          value={witnessStatus}
                          onChange={(e) => setWitnessStatus(e.target.value)}
                          placeholder="Available / hostile / unknown"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Witness Count</label>
                        <Input
                          type="number"
                          min={0}
                          value={witnessCount}
                          onChange={(e) => setWitnessCount(Number.parseInt(e.target.value, 10) || 0)}
                        />
                      </div>
                    </>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Evidence Relevance</label>
                    <select
                      value={evidenceApplicability}
                      onChange={(e) =>
                        setEvidenceApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")
                      }
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="unknown">Unknown</option>
                      <option value="applicable">Applicable</option>
                      <option value="not_applicable">No evidence details available yet</option>
                    </select>
                  </div>
                  {evidenceApplicability === "applicable" && (
                    <div>
                      <label className="text-sm font-medium mb-2 block">Evidence Summary</label>
                      <Textarea
                        value={evidenceSummary}
                        onChange={(e) => setEvidenceSummary(e.target.value)}
                        placeholder="CCTV, medico-legal report, screenshots, call logs, receipts, photos, etc."
                        rows={3}
                      />
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Document Relevance</label>
                    <select
                      value={documentsApplicability}
                      onChange={(e) =>
                        setDocumentsApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")
                      }
                      className="w-full px-3 py-2 border rounded-md bg-background"
                    >
                      <option value="unknown">Unknown</option>
                      <option value="applicable">Applicable</option>
                      <option value="not_applicable">No documents available</option>
                    </select>
                  </div>
                  {documentsApplicability === "applicable" && (
                    <div>
                      <label className="text-sm font-medium mb-2 block">Available Documents</label>
                      <Textarea
                        value={availableDocuments}
                        onChange={(e) => setAvailableDocuments(e.target.value)}
                        placeholder="FIR copy, notices, medical reports, arrest memo, court orders"
                        rows={2}
                      />
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Desired Outcome</label>
                    <Input
                      value={desiredOutcome}
                      onChange={(e) => setDesiredOutcome(e.target.value)}
                      placeholder="FIR registration, bail, recovery, protection, cancellation, etc."
                    />
                  </div>
                  <label className="flex items-center gap-2 text-sm font-medium mt-1">
                    <input
                      type="checkbox"
                      checked={childInvolved}
                      onChange={(e) => setChildInvolved(e.target.checked)}
                      className="w-4 h-4"
                    />
                    Child/juvenile involved in this case
                  </label>
                </div>
              </Card>

              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4">Run Analysis & Prediction</h2>
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
                    Tip: no need to know legal sections. Focus on facts, timeline, police action, and evidence.
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

                  {(results.confidence_note || (results.missing_information && results.missing_information.length > 0)) && (
                    <Card className="p-6 border border-border/50">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-primary" />
                        Analysis Quality
                      </h3>
                      {results.confidence_note && (
                        <p className="text-sm text-muted-foreground mb-3">{results.confidence_note}</p>
                      )}
                      {results.missing_information && results.missing_information.length > 0 && (
                        <ul className="space-y-2">
                          {results.missing_information.map((item, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <XCircle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                              <p className="text-sm">{item}</p>
                            </li>
                          ))}
                        </ul>
                      )}
                    </Card>
                  )}

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
                    Add your full facts and click "Analyze My Case" for tailored guidance.
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

