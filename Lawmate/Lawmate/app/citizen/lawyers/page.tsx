"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Star, MapPin, Search, Loader2, AlertCircle, Brain, Target, Scale, Building2 } from "lucide-react"
import {
  getLawyers,
  getLawyerRecommendations,
  resolveLawyerImageUrl,
  type Lawyer,
  type RecommendedLawyer,
  type LawyerRecommendationRequest,
} from "@/lib/services/citizen-lawyers"
import Link from "next/link"
import { PremiumMarketplace } from "@/components/marketplace/premium-marketplace"
import type { LawyerData } from "@/components/marketplace/lawyer-card-premium"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"

export default function LawyerDirectoryPage() {
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState("")
  const [expertise, setExpertise] = useState("all")
  const [lawyers, setLawyers] = useState<Lawyer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recommending, setRecommending] = useState(false)
  const [recommendationError, setRecommendationError] = useState<string | null>(null)
  const [recommendedLawyers, setRecommendedLawyers] = useState<RecommendedLawyer[]>([])
  const [caseTags, setCaseTags] = useState<string[]>([])
  const [form, setForm] = useState<LawyerRecommendationRequest>({
    case_type: "",
    case_description: "",
    charges_or_sections: "",
    city: "",
    urgency: "medium",
    preferred_experience_years: 5,
    budget_range: "medium",
    preferred_language: "English",
    hearing_court: "",
  })

  // Convert Lawyer to LawyerData format for premium component
  const convertToLawyerData = (lawyer: Lawyer): LawyerData => {
    const specs = normalizeSpecs(lawyer)
    return {
      id: lawyer.id,
      name: lawyer.name,
      avatar: lawyer.profileImage ? resolveLawyerImageUrl(lawyer.profileImage) : undefined,
      specialization: specs,
      location: lawyer.location || "Pakistan",
      rating: lawyer.rating || 0,
      reviewCount: lawyer.reviews || 0,
      casesWon: Math.floor((lawyer.cases || 0) * (lawyer.winRate || 0) / 100),
      experience: lawyer.yearsExp || 0,
      hourlyRate: lawyer.estimatedFee || 100,
      languages: ["English", "Urdu"],
      verified: true,
      available: true,
      responseTime: "< 4 hours",
      successRate: lawyer.winRate || 0,
    }
  }

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
  const normalizeSpecs = (lawyer: Lawyer): string[] =>
    Array.isArray(lawyer.specialization)
      ? lawyer.specialization
      : lawyer.specializations && Array.isArray(lawyer.specializations)
        ? lawyer.specializations
        : lawyer.specialization
          ? [lawyer.specialization]
          : []

  const runRecommendation = async () => {
    if (!form.case_description?.trim()) {
      setRecommendationError("Please provide case description. Other fields are optional.")
      return
    }
    try {
      setRecommending(true)
      setRecommendationError(null)
      const response = await getLawyerRecommendations(form)
      setRecommendedLawyers(response.recommendations || [])
      setCaseTags(response.caseTags || [])
    } catch (err: any) {
      setRecommendationError(err.message || "Failed to generate recommendations")
      setRecommendedLawyers([])
      setCaseTags([])
    } finally {
      setRecommending(false)
    }
  }

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

          {/* Recommendation Engine */}
          <Card className="p-6 border border-border mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-bold text-foreground">Criminal Case Lawyer Recommendation System</h2>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              Enter your criminal case details below. The system will rank best-fit lawyers using professional criteria:
              specialization relevance, location alignment, experience, win-rate performance, urgency readiness, and budget fit.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Input
                placeholder="Case Type (e.g., Bail, FIR, Appeal, Cyber Crime)"
                value={form.case_type}
                onChange={(e) => setForm((prev) => ({ ...prev, case_type: e.target.value }))}
              />
              <Input
                placeholder="Charges/Sections (e.g., PPC 302, 420, CrPC 497)"
                value={form.charges_or_sections}
                onChange={(e) => setForm((prev) => ({ ...prev, charges_or_sections: e.target.value }))}
              />
              <Input
                placeholder="City / Preferred Location"
                value={form.city}
                onChange={(e) => setForm((prev) => ({ ...prev, city: e.target.value }))}
              />
              <Input
                placeholder="Hearing Court (optional)"
                value={form.hearing_court}
                onChange={(e) => setForm((prev) => ({ ...prev, hearing_court: e.target.value }))}
              />
              <Select
                value={form.urgency || "medium"}
                onValueChange={(value) => setForm((prev) => ({ ...prev, urgency: value as "low" | "medium" | "high" }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Urgency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low urgency</SelectItem>
                  <SelectItem value="medium">Medium urgency</SelectItem>
                  <SelectItem value="high">High urgency</SelectItem>
                </SelectContent>
              </Select>
              <Select
                value={form.budget_range || "medium"}
                onValueChange={(value) => setForm((prev) => ({ ...prev, budget_range: value as "low" | "medium" | "high" }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Budget Range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Budget Sensitive</SelectItem>
                  <SelectItem value="medium">Balanced Budget</SelectItem>
                  <SelectItem value="high">Premium Counsel</SelectItem>
                </SelectContent>
              </Select>
              <Input
                type="number"
                min={0}
                placeholder="Preferred minimum experience (years)"
                value={form.preferred_experience_years || 0}
                onChange={(e) => setForm((prev) => ({ ...prev, preferred_experience_years: Number(e.target.value) || 0 }))}
              />
              <Input
                placeholder="Preferred language (optional)"
                value={form.preferred_language}
                onChange={(e) => setForm((prev) => ({ ...prev, preferred_language: e.target.value }))}
              />
            </div>

            <div className="mt-3">
              <textarea
                className="w-full min-h-28 rounded-md border border-border bg-background px-3 py-2 text-sm"
                placeholder="Describe your case facts, police stage, custody status, evidence concerns, and immediate legal objective..."
                value={form.case_description}
                onChange={(e) => setForm((prev) => ({ ...prev, case_description: e.target.value }))}
              />
            </div>

            <div className="mt-4 flex items-center gap-3">
              <Button onClick={runRecommendation} disabled={recommending}>
                {recommending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Generating Recommendations...
                  </>
                ) : (
                  <>
                    <Target className="w-4 h-4 mr-2" />
                    Recommend Best Lawyers
                  </>
                )}
              </Button>
              {caseTags.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {caseTags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      {tag.replace("_", " ")}
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {recommendationError && (
              <p className="text-sm text-destructive mt-3">{recommendationError}</p>
            )}

            {recommendedLawyers.length > 0 && (
              <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
                {recommendedLawyers.map((lawyer) => (
                  <Card key={lawyer.id} className="p-5 border border-primary/30 bg-primary/5">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-semibold text-lg">{lawyer.name}</h3>
                        <p className="text-sm text-muted-foreground">{lawyer.expertise}</p>
                      </div>
                      <Badge className="bg-primary/15 text-primary border border-primary/30">
                        Match {lawyer.matchScore}%
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <MapPin className="w-4 h-4" />
                        {lawyer.location}
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Scale className="w-4 h-4" />
                        {lawyer.yearsExp} yrs exp
                      </div>
                      <div className="text-muted-foreground">Win Rate: {lawyer.winRate}%</div>
                      <div className="text-muted-foreground">Fee Band: {lawyer.estimatedFeeBand}</div>
                    </div>
                    <div className="mt-3">
                      <p className="text-xs text-muted-foreground mb-1">Why recommended</p>
                      <ul className="list-disc list-inside text-sm text-foreground space-y-1">
                        {lawyer.whyRecommended?.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <Button disabled className="flex-1" title="Coming soon">
                        Contact Lawyer (Coming soon)
                      </Button>
                      <Link href={`/citizen/lawyers/${lawyer.id}`} className="flex-1">
                        <Button variant="outline" className="w-full bg-transparent">
                          View Profile
                        </Button>
                      </Link>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </Card>

          {/* Note: Search and filtering is now handled by the Premium Marketplace component below */}

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

          {/* Premium Lawyers Marketplace */}
          {loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center p-12"
            >
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading lawyers...</span>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <PremiumMarketplace
                lawyers={filteredLawyers.map(convertToLawyerData)}
                onConnect={(lawyerId) => {
                  console.log("Connect with lawyer:", lawyerId)
                  // TODO: Implement connection logic
                }}
                onViewProfile={(lawyerId) => {
                  router.push(`/citizen/lawyers/${lawyerId}`)
                }}
              />
            </motion.div>
          )}
        </div>
      </main>
    </div>
  )
}
