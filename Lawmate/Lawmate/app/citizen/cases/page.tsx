"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Plus, Calendar, FileText, Eye, TrendingUp, Loader2, AlertCircle } from "lucide-react"
import Link from "next/link"
import { getCitizenCases, type Case } from "@/lib/services/cases"
import { CaseForm } from "@/components/case-form"

export default function CitizenCasesPage() {
  const [isLoaded, setIsLoaded] = useState(false)
  const [filterStatus, setFilterStatus] = useState("all")
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
    loadCases()
  }, [filterStatus])

  const loadCases = async () => {
    setLoading(true)
    setError(null)
    try {
      const statusParam = filterStatus === "all" ? undefined : filterStatus.toLowerCase()
      const response = await getCitizenCases(statusParam)
      setCases(response.cases)
    } catch (err: any) {
      console.error("Error loading cases:", err)
      setError(err.message || "Failed to load cases")
    } finally {
      setLoading(false)
    }
  }

  const filteredCases = cases

  return (
    <div className="flex">
      <Sidebar userType="citizen" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
        <div className="fixed inset-0 ml-64 -z-10">
          <div className="absolute top-20 right-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-20 animate-float"></div>
          <div
            className="absolute bottom-0 left-1/3 w-96 h-96 bg-accent/10 rounded-full blur-3xl opacity-20 animate-float"
            style={{ animationDelay: "1s" }}
          ></div>
        </div>

        <div className="p-8">
          {/* Header */}
          <div
            className={`mb-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
          >
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div>
                <h1 className="text-4xl font-bold text-foreground mb-2">My Cases</h1>
                <p className="text-muted-foreground">Track all your ongoing and completed criminal cases</p>
              </div>
              <div className="flex gap-3 flex-wrap">
                <Button 
                  className="gradient-primary text-primary-foreground border-0"
                  onClick={() => setShowForm(true)}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Case
                </Button>
              </div>
            </div>
          </div>

          {/* Filter Tags */}
          <div
            className={`mb-8 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "100ms" }}
          >
            <div className="flex gap-2 flex-wrap">
              {["all", "Active", "Hearing Scheduled", "Appeal Filed", "Closed"].map((filter) => (
                <Button
                  key={filter}
                  variant="outline"
                  onClick={() => setFilterStatus(filter)}
                  className={`transition-all ${
                    filterStatus === filter
                      ? "gradient-primary text-primary-foreground border-0"
                      : "bg-transparent hover:bg-primary/10 border-border/50"
                  }`}
                >
                  {filter === "all" ? "All Cases" : filter}
                </Button>
              ))}
            </div>
          </div>

          {/* Cases Grid */}
          <div
            className={`transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "200ms" }}
          >
            {loading ? (
              <div className="flex items-center justify-center p-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <span className="ml-3 text-muted-foreground">Loading cases...</span>
              </div>
            ) : error ? (
              <Card className="p-6 border border-destructive/50">
                <div className="flex items-center gap-3 text-destructive">
                  <AlertCircle className="w-5 h-5" />
                  <div>
                    <p className="font-semibold">Error loading cases</p>
                    <p className="text-sm">{error}</p>
                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-3"
                      onClick={loadCases}
                    >
                      Retry
                    </Button>
                  </div>
                </div>
              </Card>
            ) : filteredCases.length === 0 ? (
              <Card className="p-12 text-center border border-border/50">
                <FileText className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-lg font-semibold text-foreground mb-2">No cases found</p>
                <p className="text-muted-foreground mb-4">You don't have any cases matching this filter.</p>
                <Button className="gradient-primary text-primary-foreground border-0">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Case
                </Button>
              </Card>
            ) : (
              <div className="grid grid-cols-1 gap-6">
                {filteredCases.map((caseItem, idx) => (
                  <div
                    key={caseItem.id}
                    style={{
                      animation: `fadeInUp 0.6s ease-out ${idx * 100}ms forwards`,
                      opacity: 0,
                    }}
                    className="group"
                  >
                    <Card className="p-6 border border-border/50 hover:border-primary/50 hover:shadow-lg transition-all duration-300 cursor-pointer">
                      <div className="flex flex-col md:flex-row gap-6 justify-between">
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="text-lg font-bold text-foreground">{caseItem.id}</h3>
                              <p className="text-sm text-muted-foreground mt-1">{caseItem.case_type}</p>
                            </div>
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${
                                caseItem.status === "Active"
                                  ? "bg-primary/20 text-primary"
                                  : caseItem.status === "Hearing Scheduled"
                                    ? "bg-accent/20 text-accent"
                                    : "bg-secondary/20 text-secondary"
                              }`}
                            >
                              {caseItem.status}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">Court</span>
                              <p className="font-medium text-foreground">{caseItem.court}</p>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Judge</span>
                              <p className="font-medium text-foreground">{caseItem.judge}</p>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Documents</span>
                              <p className="font-medium text-foreground">{caseItem.documents_count || 0}</p>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Lawyer</span>
                              <p className="font-medium text-foreground">{caseItem.assigned_lawyer || "Not assigned"}</p>
                            </div>
                          </div>

                          {caseItem.next_hearing && (
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <Calendar className="w-4 h-4" />
                              <span>Next Hearing: {new Date(caseItem.next_hearing).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>

                        <div className="flex flex-col gap-2 justify-start">
                          <Link href={`/citizen/cases/${caseItem.id}`}>
                            <Button
                              size="sm"
                              className="w-full justify-center bg-primary text-primary-foreground border-0"
                            >
                              <Eye className="w-4 h-4 mr-2" />
                              View Details
                            </Button>
                          </Link>
                          <Link href="/citizen/cases/analyze">
                            <Button
                              size="sm"
                              variant="outline"
                              className="w-full justify-center bg-transparent hover:bg-primary/10"
                            >
                              <TrendingUp className="w-4 h-4 mr-2" />
                              Analyze
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </Card>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      {showForm && (
        <CaseForm
          userType="citizen"
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
