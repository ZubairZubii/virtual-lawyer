"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
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
import {
  Mail,
  Phone,
  Loader2,
  AlertCircle,
  Search,
  Scale,
  Users,
  CalendarClock,
  Wallet,
  Building2,
  ShieldAlert,
  MapPin,
  Plus,
  BriefcaseBusiness,
} from "lucide-react"
import {
  createClient,
  createClientCase,
  getClientCases,
  getClients,
  type Client,
  type ClientCase,
} from "@/lib/services/lawyer-clients"

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lawyerId, setLawyerId] = useState<string>("")
  const [lawyerEmail, setLawyerEmail] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<"All" | "Active" | "On Hold" | "Closed">("All")
  const [riskFilter, setRiskFilter] = useState<"All" | "High" | "Medium" | "Low">("All")
  const [isAddClientOpen, setIsAddClientOpen] = useState(false)
  const [isAddCaseOpen, setIsAddCaseOpen] = useState(false)
  const [isViewCasesOpen, setIsViewCasesOpen] = useState(false)
  const [activeClient, setActiveClient] = useState<Client | null>(null)
  const [clientCases, setClientCases] = useState<ClientCase[]>([])
  const [casesLoading, setCasesLoading] = useState(false)
  const [isSubmittingClient, setIsSubmittingClient] = useState(false)
  const [isSubmittingCase, setIsSubmittingCase] = useState(false)
  const [newClient, setNewClient] = useState({
    clientName: "",
    clientEmail: "",
    clientPhone: "",
    city: "",
    notes: "",
    status: "Active" as "Active" | "On Hold" | "Closed",
    riskLevel: "Medium" as "Low" | "Medium" | "High",
    priority: "Medium" as "Low" | "Medium" | "High",
  })
  const [newCase, setNewCase] = useState({
    caseType: "",
    status: "Active" as "Active" | "On Hold" | "Closed",
    firNumber: "",
    court: "",
    policeStation: "",
    caseStage: "Initial Review",
    riskLevel: "Medium" as "Low" | "Medium" | "High",
    priority: "Medium" as "Low" | "Medium" | "High",
    nextHearing: "",
    outstandingAmount: 0,
    notes: "",
  })

  useEffect(() => {
    try {
      const raw = localStorage.getItem("user")
      if (raw) {
        const user = JSON.parse(raw) as { id?: string; email?: string }
        if (user?.id) setLawyerId(user.id)
        if (user?.email) setLawyerEmail(user.email)
        if (user?.id || user?.email) {
          loadClients(user?.id, user?.email)
          return
        }
      }
      loadClients()
    } catch {
      loadClients()
    }
  }, [])

  const loadClients = async (id?: string, email?: string) => {
    try {
      setLoading(true)
      setError(null)
      const lid = (id ?? lawyerId)?.trim() || undefined
      const em = (email ?? lawyerEmail)?.trim() || undefined
      const response = await getClients(lid, em)
      setClients(response.clients)
    } catch (err: any) {
      console.error("Error loading clients:", err)
      setError(err.message || "Failed to load clients")
    } finally {
      setLoading(false)
    }
  }

  const handleAddClient = async () => {
    if (!lawyerId && !lawyerEmail) {
      alert("Lawyer session not found. Please login again.")
      return
    }
    if (!newClient.clientName || !newClient.clientEmail || !newClient.clientPhone) {
      alert("Please fill client name, email, and phone.")
      return
    }
    try {
      setIsSubmittingClient(true)
      await createClient({
        lawyerId: lawyerId || "temp-lawyer",
        lawyerEmail: lawyerEmail || undefined,
        ...newClient,
      })
      setIsAddClientOpen(false)
      setNewClient({
        clientName: "",
        clientEmail: "",
        clientPhone: "",
        city: "",
        notes: "",
        status: "Active",
        riskLevel: "Medium",
        priority: "Medium",
      })
      await loadClients()
      alert("Client added successfully.")
    } catch (err: any) {
      alert(err.message || "Failed to add client")
    } finally {
      setIsSubmittingClient(false)
    }
  }

  const openAddCaseDialog = (client: Client) => {
    setActiveClient(client)
    setNewCase({
      caseType: "",
      status: "Active",
      firNumber: "",
      court: "",
      policeStation: "",
      caseStage: "Initial Review",
      riskLevel: "Medium",
      priority: "Medium",
      nextHearing: "",
      outstandingAmount: 0,
      notes: "",
    })
    setIsAddCaseOpen(true)
  }

  const handleAddCase = async () => {
    if ((!lawyerId && !lawyerEmail) || !activeClient) {
      alert("Lawyer/client context missing. Please log in again.")
      return
    }
    if (!newCase.caseType.trim()) {
      alert("Please enter case type.")
      return
    }
    try {
      setIsSubmittingCase(true)
      await createClientCase(activeClient.id, {
        lawyerId: lawyerId || "temp-lawyer",
        lawyerEmail: lawyerEmail || undefined,
        clientId: activeClient.id,
        ...newCase,
      })
      setIsAddCaseOpen(false)
      await loadClients()
      alert("Client case created successfully.")
    } catch (err: any) {
      alert(err.message || "Failed to create client case")
    } finally {
      setIsSubmittingCase(false)
    }
  }

  const handleViewCases = async (client: Client) => {
    setActiveClient(client)
    setIsViewCasesOpen(true)
    setCasesLoading(true)
    try {
      const response = await getClientCases(
        client.id,
        lawyerId || undefined,
        lawyerEmail || undefined
      )
      setClientCases(response.cases)
    } catch (err: any) {
      setClientCases([])
      alert(err.message || "Failed to load client cases")
    } finally {
      setCasesLoading(false)
    }
  }

  const filteredClients = clients.filter((client) => {
    const q = searchTerm.toLowerCase()
    const matchesSearch =
      q.length === 0 ||
      client.name.toLowerCase().includes(q) ||
      client.caseType.toLowerCase().includes(q) ||
      (client.caseId || "").toLowerCase().includes(q) ||
      (client.firNumber || "").toLowerCase().includes(q)
    const matchesStatus = statusFilter === "All" || client.status === statusFilter
    const matchesRisk = riskFilter === "All" || (client.riskLevel || "Medium") === riskFilter
    return matchesSearch && matchesStatus && matchesRisk
  })

  const dashboardStats = {
    totalClients: clients.length,
    activeClients: clients.filter((c) => c.status === "Active").length,
    upcomingHearings: clients.filter((c) => !!c.nextHearing).length,
    outstanding: clients.reduce((sum, c) => sum + (c.outstandingAmount || 0), 0),
  }

  const riskBadgeClass = (risk?: string) =>
    risk === "High"
      ? "bg-destructive/10 text-destructive border-destructive/30"
      : risk === "Low"
        ? "bg-primary/10 text-primary border-primary/30"
        : "bg-accent/10 text-accent border-accent/30"

  const statusBadgeClass = (status: string) =>
    status === "Active"
      ? "bg-primary/10 text-primary border-primary/30"
      : status === "Closed"
        ? "bg-muted/20 text-muted-foreground border-border"
        : "bg-accent/10 text-accent border-accent/30"

  return (
    <div className="flex">
      <Sidebar userType="lawyer" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8 flex items-start justify-between gap-4 flex-col lg:flex-row">
            <div>
              <h1 className="text-3xl font-bold text-foreground">My Clients Dashboard</h1>
              <p className="text-muted-foreground mt-2">
                Professional client portfolio for criminal matters: hearing readiness, risk, and case progress.
              </p>
            </div>
            <div className="text-sm text-muted-foreground">
              Last synced: {new Date().toLocaleString()}
            </div>
          </div>
          <div className="mb-6 flex items-center gap-3">
            <Button onClick={() => setIsAddClientOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add New Client
            </Button>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
            <Card className="p-4 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">Total Clients</p>
                  <p className="text-2xl font-bold">{dashboardStats.totalClients}</p>
                </div>
                <Users className="w-5 h-5 text-primary" />
              </div>
            </Card>
            <Card className="p-4 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">Active Matters</p>
                  <p className="text-2xl font-bold">{dashboardStats.activeClients}</p>
                </div>
                <Scale className="w-5 h-5 text-accent" />
              </div>
            </Card>
            <Card className="p-4 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">Upcoming Hearings</p>
                  <p className="text-2xl font-bold">{dashboardStats.upcomingHearings}</p>
                </div>
                <CalendarClock className="w-5 h-5 text-secondary" />
              </div>
            </Card>
            <Card className="p-4 border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">Outstanding Billing</p>
                  <p className="text-2xl font-bold">Rs. {dashboardStats.outstanding.toLocaleString()}</p>
                </div>
                <Wallet className="w-5 h-5 text-destructive" />
              </div>
            </Card>
          </div>

          {/* Filters */}
          <Card className="p-4 mb-6 border border-border">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="md:col-span-2 relative">
                <Search className="absolute left-3 top-3.5 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search by client, case type, FIR, case ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
              <select
                className="h-10 rounded-md border border-border bg-background px-3 text-sm"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as any)}
              >
                <option value="All">All Statuses</option>
                <option value="Active">Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Closed">Closed</option>
              </select>
              <select
                className="h-10 rounded-md border border-border bg-background px-3 text-sm"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value as any)}
              >
                <option value="All">All Risk Levels</option>
                <option value="High">High Risk</option>
                <option value="Medium">Medium Risk</option>
                <option value="Low">Low Risk</option>
              </select>
            </div>
          </Card>

          {/* Error Message */}
          {error && (
            <Card className="p-6 mb-6 border border-destructive/50 bg-destructive/10">
              <div className="flex items-center gap-3 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <div>
                  <p className="font-semibold">Error loading clients</p>
                  <p className="text-sm">{error}</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={loadClients}>
                    Retry
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Client Cards */}
          {loading ? (
            <div className="flex items-center justify-center p-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading clients...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredClients.length === 0 ? (
                <Card className="p-12 text-center border border-border">
                  <p className="text-muted-foreground">No clients found for current filters.</p>
                </Card>
              ) : (
                filteredClients.map((client) => (
              <Card key={client.id} className="p-6 border border-border hover:border-primary/50 transition">
                <div className="flex items-start justify-between gap-4 mb-4 flex-col lg:flex-row">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-lg font-semibold text-foreground">{client.name}</h3>
                      <Badge className={`border ${statusBadgeClass(client.status)}`}>{client.status}</Badge>
                      <Badge className={`border ${riskBadgeClass(client.riskLevel)}`}>{client.riskLevel || "Medium"} Risk</Badge>
                      <Badge className="border bg-muted/20 text-muted-foreground">{client.priority || "Medium"} Priority</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{client.caseType}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 text-sm">
                      <div>
                        <p className="text-xs text-muted-foreground">Case ID</p>
                        <p className="font-medium">{client.caseId || "N/A"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">FIR Number</p>
                        <p className="font-medium">{client.firNumber || "N/A"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Case Stage</p>
                        <p className="font-medium">{client.caseStage || "Initial Review"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Next Hearing</p>
                        <p className="font-medium">{client.nextHearing || "Not scheduled"}</p>
                      </div>
                    </div>
                  </div>
                  <div className="text-right min-w-[220px]">
                    <p className="text-xs text-muted-foreground">Outstanding Billing</p>
                    <p className="text-xl font-semibold">Rs. {(client.outstandingAmount || 0).toLocaleString()}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      Assigned: {client.assignedDate || "N/A"} | Last Contact: {client.lastContactDate || "N/A"}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4 text-sm">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Mail className="w-4 h-4" />
                    <a href={`mailto:${client.email}`} className="hover:text-foreground transition">
                      {client.email}
                    </a>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Phone className="w-4 h-4" />
                    <a href={`tel:${client.phone}`} className="hover:text-foreground transition">
                      {client.phone}
                    </a>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Building2 className="w-4 h-4" />
                    <span>{client.court || "Court not specified"}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <MapPin className="w-4 h-4" />
                    <span>{client.city || "City not specified"}</span>
                  </div>
                </div>

                {client.notes && (
                  <div className="mb-4 p-3 rounded-lg bg-muted/20 border border-border">
                    <p className="text-xs text-muted-foreground mb-1">Lawyer Notes</p>
                    <p className="text-sm leading-relaxed">{client.notes}</p>
                  </div>
                )}

                <div className="flex items-center justify-between pt-4 border-t border-border">
                  <div className="text-sm">
                    <span className="text-muted-foreground">Case Load: </span>
                    <span className="font-semibold text-foreground">{client.activeCases}</span>
                    <span className="text-muted-foreground"> / </span>
                    <span className="font-semibold text-foreground">{client.totalCases}</span>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="bg-transparent" disabled title="Coming soon">
                      Contact Client
                    </Button>
                    <Button size="sm" variant="outline" className="px-4 bg-transparent" onClick={() => openAddCaseDialog(client)}>
                      <Plus className="w-4 h-4 mr-1" />
                      Add Case
                    </Button>
                    <Button size="sm" className="px-4" onClick={() => handleViewCases(client)}>
                      View Cases
                    </Button>
                  </div>
                </div>
              </Card>
                ))
              )}
            </div>
          )}
        </div>
      </main>

      <Dialog open={isAddClientOpen} onOpenChange={setIsAddClientOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add New Client</DialogTitle>
            <DialogDescription>
              Create a professional client profile. You can add multiple cases after saving.
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Client Name</Label>
              <Input value={newClient.clientName} onChange={(e) => setNewClient((s) => ({ ...s, clientName: e.target.value }))} />
            </div>
            <div>
              <Label>Email</Label>
              <Input type="email" value={newClient.clientEmail} onChange={(e) => setNewClient((s) => ({ ...s, clientEmail: e.target.value }))} />
            </div>
            <div>
              <Label>Phone</Label>
              <Input value={newClient.clientPhone} onChange={(e) => setNewClient((s) => ({ ...s, clientPhone: e.target.value }))} />
            </div>
            <div>
              <Label>City</Label>
              <Input value={newClient.city} onChange={(e) => setNewClient((s) => ({ ...s, city: e.target.value }))} />
            </div>
            <div>
              <Label>Status</Label>
              <select className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm" value={newClient.status} onChange={(e) => setNewClient((s) => ({ ...s, status: e.target.value as any }))}>
                <option value="Active">Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            <div>
              <Label>Risk Level</Label>
              <select className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm" value={newClient.riskLevel} onChange={(e) => setNewClient((s) => ({ ...s, riskLevel: e.target.value as any }))}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <Label>Lawyer Notes</Label>
              <textarea
                className="min-h-[90px] w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
                value={newClient.notes}
                onChange={(e) => setNewClient((s) => ({ ...s, notes: e.target.value }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddClientOpen(false)}>Cancel</Button>
            <Button onClick={handleAddClient} disabled={isSubmittingClient}>
              {isSubmittingClient ? "Saving..." : "Save Client"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isAddCaseOpen} onOpenChange={setIsAddCaseOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add New Case</DialogTitle>
            <DialogDescription>
              Add a new case for {activeClient?.name || "selected client"}.
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Case Type</Label>
              <Input value={newCase.caseType} onChange={(e) => setNewCase((s) => ({ ...s, caseType: e.target.value }))} />
            </div>
            <div>
              <Label>FIR Number</Label>
              <Input value={newCase.firNumber} onChange={(e) => setNewCase((s) => ({ ...s, firNumber: e.target.value }))} />
            </div>
            <div>
              <Label>Court</Label>
              <Input value={newCase.court} onChange={(e) => setNewCase((s) => ({ ...s, court: e.target.value }))} />
            </div>
            <div>
              <Label>Police Station</Label>
              <Input value={newCase.policeStation} onChange={(e) => setNewCase((s) => ({ ...s, policeStation: e.target.value }))} />
            </div>
            <div>
              <Label>Case Stage</Label>
              <Input value={newCase.caseStage} onChange={(e) => setNewCase((s) => ({ ...s, caseStage: e.target.value }))} />
            </div>
            <div>
              <Label>Next Hearing</Label>
              <Input type="date" value={newCase.nextHearing} onChange={(e) => setNewCase((s) => ({ ...s, nextHearing: e.target.value }))} />
            </div>
            <div>
              <Label>Status</Label>
              <select className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm" value={newCase.status} onChange={(e) => setNewCase((s) => ({ ...s, status: e.target.value as any }))}>
                <option value="Active">Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            <div>
              <Label>Priority</Label>
              <select className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm" value={newCase.priority} onChange={(e) => setNewCase((s) => ({ ...s, priority: e.target.value as any }))}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
            <div>
              <Label>Risk Level</Label>
              <select className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm" value={newCase.riskLevel} onChange={(e) => setNewCase((s) => ({ ...s, riskLevel: e.target.value as any }))}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
            <div>
              <Label>Outstanding Amount (Rs.)</Label>
              <Input
                type="number"
                min={0}
                value={newCase.outstandingAmount}
                onChange={(e) => setNewCase((s) => ({ ...s, outstandingAmount: Number(e.target.value || 0) }))}
              />
            </div>
            <div className="md:col-span-2">
              <Label>Case Notes</Label>
              <textarea
                className="min-h-[90px] w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
                value={newCase.notes}
                onChange={(e) => setNewCase((s) => ({ ...s, notes: e.target.value }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddCaseOpen(false)}>Cancel</Button>
            <Button onClick={handleAddCase} disabled={isSubmittingCase}>
              {isSubmittingCase ? "Saving..." : "Save Case"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isViewCasesOpen} onOpenChange={setIsViewCasesOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Client Cases</DialogTitle>
            <DialogDescription>
              {activeClient?.name ? `Case portfolio for ${activeClient.name}` : "Client case portfolio"}
            </DialogDescription>
          </DialogHeader>
          {casesLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground py-6">
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading cases...
            </div>
          ) : clientCases.length === 0 ? (
            <div className="py-6 text-sm text-muted-foreground">No cases found for this client yet.</div>
          ) : (
            <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
              {clientCases.map((caseItem) => (
                <Card key={caseItem.caseId} className="p-4 border border-border">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <BriefcaseBusiness className="w-4 h-4 text-primary" />
                        <p className="font-semibold">{caseItem.caseType}</p>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">Case ID: {caseItem.caseId}</p>
                    </div>
                    <Badge className="border">{caseItem.status}</Badge>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 text-sm">
                    <p><span className="text-muted-foreground">FIR:</span> {caseItem.firNumber || "N/A"}</p>
                    <p><span className="text-muted-foreground">Court:</span> {caseItem.court || "N/A"}</p>
                    <p><span className="text-muted-foreground">Stage:</span> {caseItem.caseStage || "N/A"}</p>
                    <p><span className="text-muted-foreground">Next Hearing:</span> {caseItem.nextHearing || "N/A"}</p>
                    <p><span className="text-muted-foreground">Priority:</span> {caseItem.priority || "Medium"}</p>
                    <p><span className="text-muted-foreground">Outstanding:</span> Rs. {(caseItem.outstandingAmount || 0).toLocaleString()}</p>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
