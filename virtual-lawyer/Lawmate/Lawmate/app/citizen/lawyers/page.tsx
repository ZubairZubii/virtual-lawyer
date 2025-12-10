"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Star, MapPin, Search, Loader2, AlertCircle } from "lucide-react"
import { getLawyers, type Lawyer } from "@/lib/services/citizen-lawyers"

export default function LawyerDirectoryPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [expertise, setExpertise] = useState("all")
  const [lawyers, setLawyers] = useState<Lawyer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadLawyers()
  }, [])

  useEffect(() => {
    // Debounce search
    const timer = setTimeout(() => {
      loadLawyers()
    }, 300)
    return () => clearTimeout(timer)
  }, [searchTerm, expertise])

  const loadLawyers = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getLawyers(
        searchTerm || undefined,
        expertise !== "all" ? expertise : undefined
      )
      setLawyers(response.lawyers)
    } catch (err: any) {
      console.error("Error loading lawyers:", err)
      setError(err.message || "Failed to load lawyers")
    } finally {
      setLoading(false)
    }
  }

  const filteredLawyers = lawyers

  return (
    <div className="flex">
      <Sidebar userType="citizen" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Find Lawyers</h1>
            <p className="text-muted-foreground mt-2">Browse and connect with experienced criminal law specialists</p>
          </div>

          {/* Search and Filter */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name or expertise..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={expertise} onValueChange={setExpertise}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by expertise" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Specializations</SelectItem>
                <SelectItem value="Bail">Bail Applications</SelectItem>
                <SelectItem value="Constitutional">Constitutional Rights</SelectItem>
                <SelectItem value="Remand">Remand Challenges</SelectItem>
                <SelectItem value="Evidence">Evidence & FIR</SelectItem>
              </SelectContent>
            </Select>
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

          {/* Lawyers Grid */}
          {loading ? (
            <div className="flex items-center justify-center p-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading lawyers...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredLawyers.length === 0 ? (
                <Card className="p-12 text-center border border-border col-span-2">
                  <p className="text-muted-foreground">No lawyers found matching your criteria.</p>
                </Card>
              ) : (
                filteredLawyers.map((lawyer) => (
              <Card key={lawyer.id} className="p-6 border border-border hover:shadow-lg transition">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-foreground">{lawyer.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <MapPin className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">{lawyer.location}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 justify-end">
                      <Star className="w-4 h-4 fill-primary text-primary" />
                      <span className="font-semibold text-foreground">{lawyer.rating}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">{lawyer.reviews} reviews</span>
                  </div>
                </div>

                <div className="flex gap-4 mb-4">
                  <div>
                    <span className="text-xs text-muted-foreground">Win Rate</span>
                    <p className="text-lg font-semibold text-primary">{lawyer.winRate}%</p>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground">Cases Handled</span>
                    <p className="text-lg font-semibold text-accent">{lawyer.cases}</p>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground">Experience</span>
                    <p className="text-lg font-semibold text-secondary">{lawyer.yearsExp} years</p>
                  </div>
                </div>

                <div className="mb-4">
                  <span className="text-xs text-muted-foreground">Specializations</span>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    {lawyer.specialization.map((spec) => (
                      <Badge key={spec} variant="secondary">
                        {spec}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button className="flex-1">Contact Lawyer</Button>
                  <Button variant="outline" className="flex-1 bg-transparent">
                    View Profile
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
