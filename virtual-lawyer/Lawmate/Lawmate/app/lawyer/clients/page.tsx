"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MoreVertical, Mail, Phone, Loader2, AlertCircle } from "lucide-react"
import { getClients, type Client } from "@/lib/services/lawyer-clients"

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadClients()
  }, [])

  const loadClients = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getClients()
      setClients(response.clients)
    } catch (err: any) {
      console.error("Error loading clients:", err)
      setError(err.message || "Failed to load clients")
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
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">My Clients</h1>
            <p className="text-muted-foreground mt-2">Manage your client relationships and cases</p>
          </div>

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
              {clients.length === 0 ? (
                <Card className="p-12 text-center border border-border">
                  <p className="text-muted-foreground">No clients found</p>
                </Card>
              ) : (
                clients.map((client) => (
              <Card key={client.id} className="p-6 border border-border hover:border-primary transition">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">{client.name}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{client.caseType}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge
                      className={
                        client.status === "Active"
                          ? "bg-primary/10 text-primary"
                          : client.status === "Closed"
                            ? "bg-muted/10 text-muted-foreground"
                            : "bg-accent/10 text-accent"
                      }
                    >
                      {client.status}
                    </Badge>
                    <button className="p-2 hover:bg-muted rounded-lg transition">
                      <MoreVertical size={18} className="text-muted-foreground" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
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
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-border">
                  <div className="text-sm">
                    <span className="text-muted-foreground">Active: </span>
                    <span className="font-semibold text-foreground">{client.activeCases}</span>
                    <span className="text-muted-foreground"> / </span>
                    <span className="font-semibold text-foreground">{client.totalCases}</span>
                  </div>
                  <Button size="sm" className="px-4">
                    View Cases
                  </Button>
                </div>
              </Card>
                ))
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
