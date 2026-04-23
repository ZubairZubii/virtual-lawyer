"use client"

import { useEffect, useMemo, useState } from "react"
import type { ReactNode } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { ArrowLeft, Calendar, FileText, Loader2, Scale, User } from "lucide-react"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { getCaseDetails, type CaseDetails } from "@/lib/services/cases"

export default function CitizenCaseDetailsPage() {
  const params = useParams<{ caseId: string | string[] }>()
  const [caseDetails, setCaseDetails] = useState<CaseDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const resolvedCaseId = useMemo(() => {
    const raw = params?.caseId
    if (!raw) return ""
    if (Array.isArray(raw)) {
      return raw.map((part) => decodeURIComponent(part)).join("/")
    }
    return decodeURIComponent(raw)
  }, [params?.caseId])

  useEffect(() => {
    const loadCase = async () => {
      if (!resolvedCaseId) {
        setLoading(false)
        setError("Invalid case ID")
        return
      }

      try {
        setLoading(true)
        setError(null)
        const data = await getCaseDetails(resolvedCaseId)
        setCaseDetails(data)
      } catch (err: any) {
        setError(err.message || "Failed to load case details")
      } finally {
        setLoading(false)
      }
    }

    loadCase()
  }, [resolvedCaseId])

  return (
    <div className="flex">
      <Sidebar userType="citizen" />
      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background p-8">
        <Link href="/citizen/cases">
          <Button variant="outline" className="mb-6 bg-transparent">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to My Cases
          </Button>
        </Link>

        {loading ? (
          <div className="flex items-center justify-center p-20">
            <Loader2 className="w-7 h-7 animate-spin text-primary" />
          </div>
        ) : error ? (
          <Card className="p-6 border border-destructive/50">
            <p className="text-destructive font-semibold">Unable to load case details</p>
            <p className="text-sm mt-2 text-muted-foreground">{error}</p>
          </Card>
        ) : !caseDetails ? (
          <Card className="p-6 border border-border">
            <p className="text-muted-foreground">Case details not found.</p>
          </Card>
        ) : (
          <div className="space-y-6">
            <Card className="p-6 border border-border">
              <h1 className="text-2xl font-bold text-foreground">{caseDetails.id}</h1>
              <p className="text-muted-foreground mt-1">{caseDetails.case_type}</p>
              <div className="grid md:grid-cols-3 gap-4 mt-6">
                <DetailItem icon={<Scale className="w-4 h-4" />} label="Court" value={caseDetails.court || "Not specified"} />
                <DetailItem icon={<User className="w-4 h-4" />} label="Judge" value={caseDetails.judge || "Not assigned"} />
                <DetailItem
                  icon={<Calendar className="w-4 h-4" />}
                  label="Next Hearing"
                  value={caseDetails.next_hearing ? new Date(caseDetails.next_hearing).toLocaleDateString() : "Not scheduled"}
                />
              </div>
            </Card>

            {caseDetails.case_summary && (
              <Card className="p-6 border border-border">
                <h2 className="text-lg font-semibold mb-2">Case Summary</h2>
                <p className="text-sm text-muted-foreground leading-relaxed">{caseDetails.case_summary}</p>
              </Card>
            )}

            {caseDetails.description && (
              <Card className="p-6 border border-border">
                <h2 className="text-lg font-semibold mb-2">Description</h2>
                <p className="text-sm text-muted-foreground leading-relaxed">{caseDetails.description}</p>
              </Card>
            )}

            {caseDetails.case_documents && caseDetails.case_documents.length > 0 && (
              <Card className="p-6 border border-border">
                <h2 className="text-lg font-semibold mb-4">Documents</h2>
                <div className="space-y-2">
                  {caseDetails.case_documents.map((doc) => (
                    <div key={doc.doc_id} className="flex items-center gap-3 text-sm">
                      <FileText className="w-4 h-4 text-muted-foreground" />
                      <span>{doc.file_name}</span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

function DetailItem({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border p-3">
      <p className="text-xs text-muted-foreground flex items-center gap-2">
        {icon}
        {label}
      </p>
      <p className="text-sm font-medium mt-1">{value}</p>
    </div>
  )
}
