"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { CaseTracker } from "@/components/case-tracker"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Plus, Filter, Loader2, AlertCircle, FileText } from "lucide-react"
import { getLawyerCases, type Case } from "@/lib/services/cases"
import { CaseForm } from "@/components/case-form"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export default function LawyerCasesPage() {
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filterStatus, setFilterStatus] = useState("all")
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    loadCases()
  }, [filterStatus])

  const loadCases = async () => {
    setLoading(true)
    setError(null)
    try {
      const statusParam = filterStatus === "all" ? undefined : filterStatus.toLowerCase()
      const response = await getLawyerCases(statusParam)
      // Convert API cases to CaseTracker format
      // Backend returns: id, case_type, status, priority, client_name, deadline, hours_billed, progress, next_hearing, court, judge
      const formattedCases = response.cases.map((c) => ({
        id: c.id,
        firNumber: c.id,
        status: c.status as "Active" | "Hearing Scheduled" | "Appeal Filed" | "Closed",
        caseType: c.case_type,
        court: c.court || "Not specified",
        judge: c.judge || "Not assigned",
        nextHearing: c.next_hearing ? new Date(c.next_hearing).toLocaleDateString() : "Not scheduled",
        documents: 0, // Backend doesn't return documents_count for lawyer cases
        assignedLawyer: undefined, // Lawyer's own cases don't have assigned_lawyer
      }))
      setCases(formattedCases)
    } catch (err: any) {
      console.error("Error loading cases:", err)
      setError(err.message || "Failed to load cases")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex">
      <Sidebar userType="lawyer" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-foreground">My Cases</h1>
              <p className="text-muted-foreground mt-2">Manage all your assigned cases</p>
            </div>
            <div className="flex gap-3">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="bg-transparent">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter: {filterStatus === "all" ? "All" : filterStatus}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setFilterStatus("all")}>
                    All Cases
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("active")}>
                    Active
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("urgent")}>
                    Urgent (High Priority)
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("hearing_scheduled")}>
                    Hearing Scheduled
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("closed")}>
                    Closed
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <Button onClick={() => setShowForm(true)}>
                <Plus className="w-4 h-4 mr-2" />
                New Case
              </Button>
            </div>
          </div>

          {/* Cases */}
          {loading ? (
            <Card className="p-12">
              <div className="flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <span className="ml-3 text-muted-foreground">Loading cases...</span>
              </div>
            </Card>
          ) : error ? (
            <Card className="p-6 border border-destructive/50">
              <div className="flex items-center gap-3 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <p>{error}</p>
              </div>
            </Card>
          ) : cases.length === 0 ? (
            <Card className="p-12 text-center">
              <FileText className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <p className="text-lg font-semibold text-foreground mb-2">No cases found</p>
              <p className="text-muted-foreground">You don't have any cases matching this filter.</p>
            </Card>
          ) : (
            <CaseTracker cases={cases} />
          )}
        </div>
      </main>
      {showForm && (
        <CaseForm
          userType="lawyer"
          onSuccess={() => {
            setShowForm(false)
            loadCases()
          }}
          onCancel={() => setShowForm(false)}
        />
      )}
    </div>
  )
}
