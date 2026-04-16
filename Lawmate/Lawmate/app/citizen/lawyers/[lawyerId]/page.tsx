"use client"

import { useEffect, useState } from "react"
import type { ReactNode } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Loader2, MapPin, Mail, Phone, Star, ArrowLeft } from "lucide-react"
import { getLawyerProfile, resolveLawyerImageUrl, type Lawyer } from "@/lib/services/citizen-lawyers"

export default function CitizenLawyerProfilePage() {
  const params = useParams<{ lawyerId: string }>()
  const [lawyer, setLawyer] = useState<Lawyer | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      if (!params?.lawyerId) return
      try {
        setLoading(true)
        setError(null)
        const data = await getLawyerProfile(params.lawyerId)
        setLawyer(data)
      } catch (err: any) {
        setError(err.message || "Failed to load lawyer profile")
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [params?.lawyerId])

  const specializationList =
    lawyer && Array.isArray(lawyer.specialization)
      ? lawyer.specialization
      : lawyer && typeof lawyer.specialization === "string"
        ? [lawyer.specialization]
        : lawyer && Array.isArray((lawyer as any).specializations)
          ? (lawyer as any).specializations
          : []

  return (
    <div className="flex">
      <Sidebar userType="citizen" />
      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background p-8">
        <Link href="/citizen/lawyers">
          <Button variant="outline" className="mb-6 bg-transparent">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Directory
          </Button>
        </Link>

        {loading ? (
          <div className="flex items-center justify-center p-20">
            <Loader2 className="w-7 h-7 animate-spin text-primary" />
          </div>
        ) : error ? (
          <Card className="p-8 border border-destructive/40">
            <p className="text-destructive">{error}</p>
          </Card>
        ) : !lawyer ? (
          <Card className="p-8">
            <p className="text-muted-foreground">Lawyer profile not found.</p>
          </Card>
        ) : (
          <Card className="p-8 border border-border">
            <div className="flex flex-col md:flex-row gap-6">
              <div className="w-28 h-28 rounded-full overflow-hidden border border-border bg-muted flex items-center justify-center text-xs text-muted-foreground shrink-0">
                {lawyer.profileImage ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={resolveLawyerImageUrl(lawyer.profileImage)} alt={`${lawyer.name} profile`} className="w-full h-full object-cover" />
                ) : (
                  "No Photo"
                )}
              </div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold">{lawyer.name}</h1>
                <p className="text-muted-foreground mt-1">{lawyer.expertise}</p>
                <div className="flex flex-wrap gap-4 mt-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {lawyer.location || "Not specified"}
                  </span>
                  <span className="flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {lawyer.email || "Not available"}
                  </span>
                  <span className="flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    {lawyer.phone || "Not available"}
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                  <Stat label="Win Rate" value={`${lawyer.winRate || 0}%`} />
                  <Stat label="Cases" value={`${lawyer.cases || 0}`} />
                  <Stat label="Experience" value={`${lawyer.yearsExp || 0} yrs`} />
                  <Stat
                    label="Rating"
                    value={
                      <span className="inline-flex items-center gap-1">
                        <Star className="w-4 h-4 text-primary fill-primary" />
                        {lawyer.rating || 0}
                      </span>
                    }
                  />
                </div>
                {specializationList.length > 0 && (
                  <div className="mt-6">
                    <p className="text-sm text-muted-foreground mb-2">Specializations</p>
                    <div className="flex flex-wrap gap-2">
                      {specializationList.map((spec) => (
                        <Badge key={spec} variant="secondary">
                          {spec}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {lawyer.bio && (
                  <div className="mt-6">
                    <p className="text-sm text-muted-foreground mb-2">About</p>
                    <p className="text-sm leading-relaxed">{lawyer.bio}</p>
                  </div>
                )}
                <div className="mt-8">
                  <Button disabled title="Coming soon">
                    Contact Lawyer (Coming soon)
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        )}
      </main>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string | ReactNode }) {
  return (
    <div className="rounded-lg border border-border p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  )
}
