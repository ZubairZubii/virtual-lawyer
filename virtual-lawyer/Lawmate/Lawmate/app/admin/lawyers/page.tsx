"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, Clock, Loader2, AlertCircle } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { getLawyers, verifyLawyer, createLawyer, type Lawyer, type CreateLawyerRequest } from "@/lib/services/admin-lawyers"

export default function LawyersPage() {
  const [lawyers, setLawyers] = useState<Lawyer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isAddLawyerOpen, setIsAddLawyerOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [newLawyer, setNewLawyer] = useState<CreateLawyerRequest>({
    name: "",
    email: "",
    specialization: "General Practice",
    password: ""
  })

  useEffect(() => {
    loadLawyers()
  }, [])

  const loadLawyers = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getLawyers()
      setLawyers(response.lawyers)
    } catch (err: any) {
      console.error("Error loading lawyers:", err)
      setError(err.message || "Failed to load lawyers")
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async (lawyerId: string, status: "Verified" | "Rejected") => {
    try {
      await verifyLawyer(lawyerId, status)
      await loadLawyers() // Reload list
    } catch (err: any) {
      console.error("Error verifying lawyer:", err)
      alert(err.message || "Failed to verify lawyer")
    }
  }

  const handleAddLawyer = async () => {
    if (!newLawyer.name || !newLawyer.email || !newLawyer.password) {
      alert("Please fill in all required fields")
      return
    }
    setIsCreating(true)
    try {
      await createLawyer(newLawyer)
      setIsAddLawyerOpen(false)
      setNewLawyer({ name: "", email: "", specialization: "General Practice", password: "" })
      await loadLawyers()
      alert("Lawyer created successfully!")
    } catch (err: any) {
      console.error("Error creating lawyer:", err)
      alert(err.message || "Failed to create lawyer")
    } finally {
      setIsCreating(false)
    }
  }

  const getVerificationIcon = (status: string) => {
    switch (status) {
      case "Verified":
        return <CheckCircle2 className="w-5 h-5 text-primary" />
      case "Pending":
        return <Clock className="w-5 h-5 text-accent" />
      case "Rejected":
        return <XCircle className="w-5 h-5 text-destructive" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Verified":
        return "bg-primary/10 text-primary"
      case "Pending":
        return "bg-accent/10 text-accent"
      case "Rejected":
        return "bg-destructive/10 text-destructive"
      default:
        return "bg-muted/10 text-muted-foreground"
    }
  }

  return (
    <div className="flex">
      <Sidebar userType="admin" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Lawyer Management</h1>
              <p className="text-muted-foreground mt-2">Verify and manage lawyer profiles</p>
            </div>
            <Button onClick={() => setIsAddLawyerOpen(true)}>Add Lawyer</Button>
          </div>

          {/* Error Message */}
          {error && (
            <Card className="p-6 mb-6 border border-destructive/50 bg-destructive/10">
              <div className="flex items-center gap-3 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <div>
                  <p className="font-semibold">Error loading lawyers</p>
                  <p className="text-sm">{error}</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={loadLawyers}>
                    Retry
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Lawyer Cards */}
          {loading ? (
            <div className="flex items-center justify-center p-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading lawyers...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {lawyers.length === 0 ? (
                <Card className="p-12 text-center border border-border">
                  <p className="text-muted-foreground">No lawyers found</p>
                </Card>
              ) : (
                lawyers.map((lawyer) => (
                  <Card key={lawyer.id} className="p-6 border border-border">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {getVerificationIcon(lawyer.verificationStatus)}
                          <h3 className="text-lg font-semibold text-foreground">{lawyer.name}</h3>
                          <Badge className={getStatusColor(lawyer.verificationStatus)}>{lawyer.verificationStatus}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">{lawyer.email}</p>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Specialization</p>
                            <p className="font-medium text-foreground">{lawyer.specialization}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Cases Solved</p>
                            <p className="font-medium text-foreground">{lawyer.casesSolved}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Win Rate</p>
                            <p className="font-medium text-foreground">
                              {typeof lawyer.winRate === "number" ? `${lawyer.winRate}%` : lawyer.winRate || "-"}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Joined</p>
                            <p className="font-medium text-foreground">{lawyer.joinDate}</p>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        {lawyer.verificationStatus === "Pending" && (
                          <>
                            <Button 
                              size="sm" 
                              className="bg-primary"
                              onClick={() => handleVerify(lawyer.id, "Verified")}
                            >
                              Approve
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="bg-transparent"
                              onClick={() => handleVerify(lawyer.id, "Rejected")}
                            >
                              Reject
                            </Button>
                          </>
                        )}
                        {lawyer.verificationStatus === "Verified" && (
                          <Button size="sm" variant="outline" className="bg-transparent">
                            View Profile
                          </Button>
                        )}
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* Add Lawyer Dialog */}
          <Dialog open={isAddLawyerOpen} onOpenChange={setIsAddLawyerOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Lawyer</DialogTitle>
                <DialogDescription>
                  Create a new lawyer account. The lawyer will need to be verified before they can use the platform.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="lawyer-name">Full Name</Label>
                  <Input
                    id="lawyer-name"
                    placeholder="Enter lawyer name (e.g., Adv. Sharma)"
                    value={newLawyer.name}
                    onChange={(e) => setNewLawyer({ ...newLawyer, name: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="lawyer-email">Email</Label>
                  <Input
                    id="lawyer-email"
                    type="email"
                    placeholder="lawyer@example.com"
                    value={newLawyer.email}
                    onChange={(e) => setNewLawyer({ ...newLawyer, email: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="specialization">Specialization</Label>
                  <Input
                    id="specialization"
                    placeholder="e.g., Criminal Law, Bail & Remand"
                    value={newLawyer.specialization}
                    onChange={(e) => setNewLawyer({ ...newLawyer, specialization: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="lawyer-password">Password</Label>
                  <Input
                    id="lawyer-password"
                    type="password"
                    placeholder="Enter password"
                    value={newLawyer.password}
                    onChange={(e) => setNewLawyer({ ...newLawyer, password: e.target.value })}
                    className="mt-2"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddLawyerOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddLawyer} disabled={isCreating}>
                  {isCreating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Lawyer"
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </main>
    </div>
  )
}
