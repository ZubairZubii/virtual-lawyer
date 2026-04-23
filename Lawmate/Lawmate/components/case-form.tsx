"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { X, Loader2 } from "lucide-react"
import { createCase, type CreateCaseRequest } from "@/lib/services/cases"

const COURTS_BY_CITY: Record<string, string[]> = {
  Karachi: [
    "Sindh High Court, Karachi",
    "City Courts Karachi",
    "District & Sessions Court Karachi South",
    "District & Sessions Court Karachi East",
    "District & Sessions Court Karachi West",
    "District & Sessions Court Karachi Central",
    "District & Sessions Court Malir",
    "District & Sessions Court Korangi",
    "Banking Court Karachi",
    "Special Court (Anti-Corruption), Karachi",
    "Anti-Terrorism Court Karachi",
  ],
  Lahore: [
    "Lahore High Court, Lahore",
    "District & Sessions Court Lahore",
    "Model Criminal Trial Court Lahore",
    "Anti-Terrorism Court Lahore",
    "Banking Court Lahore",
    "Special Court (CNS), Lahore",
  ],
  Islamabad: [
    "Islamabad High Court",
    "District & Sessions Court Islamabad",
    "Accountability Court Islamabad",
    "Special Court (Central), Islamabad",
    "Banking Court Islamabad",
    "Anti-Terrorism Court Islamabad",
  ],
  Rawalpindi: [
    "District & Sessions Court Rawalpindi",
    "Special Judge Central Rawalpindi",
    "Banking Court Rawalpindi",
    "Anti-Terrorism Court Rawalpindi",
  ],
  Peshawar: [
    "Peshawar High Court",
    "District & Sessions Court Peshawar",
    "Banking Court Peshawar",
    "Special Court (Anti-Corruption), Peshawar",
    "Anti-Terrorism Court Peshawar",
  ],
  Quetta: [
    "Balochistan High Court, Quetta",
    "District & Sessions Court Quetta",
    "Banking Court Quetta",
    "Anti-Terrorism Court Quetta",
  ],
  Multan: [
    "Lahore High Court, Multan Bench",
    "District & Sessions Court Multan",
    "Banking Court Multan",
    "Anti-Terrorism Court Multan",
  ],
  Faisalabad: [
    "Lahore High Court, Faisalabad Bench",
    "District & Sessions Court Faisalabad",
    "Banking Court Faisalabad",
    "Anti-Terrorism Court Faisalabad",
  ],
  Hyderabad: [
    "Sindh High Court, Hyderabad Bench",
    "District & Sessions Court Hyderabad",
    "Banking Court Hyderabad",
    "Anti-Terrorism Court Hyderabad",
  ],
  Sukkur: [
    "District & Sessions Court Sukkur",
    "Banking Court Sukkur",
    "Anti-Terrorism Court Sukkur",
  ],
  Sialkot: [
    "District & Sessions Court Sialkot",
    "Banking Court Sialkot",
  ],
  Gujranwala: [
    "District & Sessions Court Gujranwala",
    "Banking Court Gujranwala",
    "Anti-Terrorism Court Gujranwala",
  ],
  Gujrat: [
    "District & Sessions Court Gujrat",
    "Banking Court Gujrat",
  ],
  Sargodha: [
    "District & Sessions Court Sargodha",
    "Banking Court Sargodha",
  ],
  Bahawalpur: [
    "Lahore High Court, Bahawalpur Bench",
    "District & Sessions Court Bahawalpur",
    "Banking Court Bahawalpur",
  ],
  DeraGhaziKhan: [
    "District & Sessions Court Dera Ghazi Khan",
    "Banking Court Dera Ghazi Khan",
  ],
  Abbottabad: [
    "District & Sessions Court Abbottabad",
    "Banking Court Abbottabad",
  ],
  Mardan: [
    "District & Sessions Court Mardan",
    "Banking Court Mardan",
  ],
  Swat: [
    "District & Sessions Court Swat",
    "Banking Court Swat",
  ],
}

interface CaseFormProps {
  userType: "citizen" | "lawyer"
  onSuccess: () => void
  onCancel: () => void
}

export function CaseForm({ userType, onSuccess, onCancel }: CaseFormProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState<CreateCaseRequest>({
    case_type: "",
    court: "",
    judge: "",
    sections: [],
    police_station: "",
    fir_number: "",
    client_name: "",
    description: "",
    filing_date: new Date().toISOString().split("T")[0],
    next_hearing: "",
    priority: "Medium",
  })
  const [selectedCity, setSelectedCity] = useState("")
  const [courtInputMode, setCourtInputMode] = useState<"dropdown" | "manual">("dropdown")
  const selectedCaseType = formData.case_type
  const showPoliceFields = ["FIR Complaint", "Bail Application", "Criminal Appeal", "Revision Petition"].includes(
    selectedCaseType,
  )

  const cityOptions = Object.keys(COURTS_BY_CITY)
  const selectedCityCourts = selectedCity ? COURTS_BY_CITY[selectedCity] || [] : []

  const descriptionPlaceholderByType: Record<string, string> = {
    "FIR Complaint":
      "Write full facts: incident date/time, place, what happened, accused details (if known), police response, whether FIR was refused, witnesses, and evidence.",
    "Bail Application":
      "Write full facts: arrest date, custody status, FIR details (if any), allegations, previous record, medical/family hardship, and what relief you need.",
    "Criminal Appeal":
      "Write full facts: trial court result, sentence/order date, key legal errors, important evidence/witness issues, and relief sought in appeal.",
    "Revision Petition":
      "Write full facts: impugned order, date, procedural/legal defects, prejudice caused, and exact revision relief sought.",
    Appeal:
      "Write full facts: order challenged, legal mistakes, factual background, available documents, and the specific outcome you want.",
    Other:
      "Write complete timeline in plain language: what happened, where, who is involved, documents/evidence available, current stage, and desired outcome.",
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Validate required fields
      if (!formData.case_type || !formData.court) {
        throw new Error("Case type and court are required")
      }
      if (!formData.description || formData.description.trim().length < 20) {
        throw new Error("Please provide complete case facts (at least 20 characters).")
      }

      const response = await createCase(formData, userType)
      console.log("✅ Case created:", response)
      onSuccess()
    } catch (err: any) {
      console.error("Error creating case:", err)
      setError(err.message || "Failed to create case")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-foreground">
              Create New Case
            </h2>
            <Button variant="ghost" size="sm" onClick={onCancel}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Case Type */}
            <div>
              <Label htmlFor="case_type">Case Type *</Label>
              <Select
                value={formData.case_type}
                onValueChange={(value) =>
                  setFormData({ ...formData, case_type: value })
                }
              >
                <SelectTrigger id="case_type" className="w-full border-2 border-border focus:border-primary">
                  <SelectValue placeholder="Select case type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Bail Application">Bail Application</SelectItem>
                  <SelectItem value="Appeal">Appeal</SelectItem>
                  <SelectItem value="Revision Petition">Revision Petition</SelectItem>
                  <SelectItem value="Criminal Appeal">Criminal Appeal</SelectItem>
                  <SelectItem value="FIR Complaint">FIR Complaint</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* City */}
            <div>
              <Label htmlFor="city">City *</Label>
              <Select
                value={selectedCity}
                onValueChange={(value) => {
                  setSelectedCity(value)
                  setFormData({ ...formData, court: "" })
                }}
              >
                <SelectTrigger id="city" className="w-full border-2 border-border focus:border-primary">
                  <SelectValue placeholder="Select city" />
                </SelectTrigger>
                <SelectContent>
                  {cityOptions.map((city) => (
                    <SelectItem key={city} value={city}>
                      {city === "DeraGhaziKhan" ? "Dera Ghazi Khan" : city}
                    </SelectItem>
                  ))}
                  <SelectItem value="Other">Other / Not listed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Court */}
            <div>
              <Label htmlFor="court">Court *</Label>
              {courtInputMode === "dropdown" && selectedCity && selectedCity !== "Other" ? (
                <>
                  <Select
                    value={formData.court || ""}
                    onValueChange={(value) => {
                      if (value === "__manual__") {
                        setCourtInputMode("manual")
                        setFormData({ ...formData, court: "" })
                        return
                      }
                      setFormData({ ...formData, court: value })
                    }}
                  >
                    <SelectTrigger id="court" className="w-full border-2 border-border focus:border-primary">
                      <SelectValue placeholder="Select court" />
                    </SelectTrigger>
                    <SelectContent>
                      {selectedCityCourts.map((court) => (
                        <SelectItem key={court} value={court}>
                          {court}
                        </SelectItem>
                      ))}
                      <SelectItem value="__manual__">Other court (type manually)</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground mt-1">
                    If your exact court is missing, choose "Other court" and type it manually.
                  </p>
                </>
              ) : (
                <>
                  <Input
                    id="court"
                    value={formData.court}
                    onChange={(e) =>
                      setFormData({ ...formData, court: e.target.value })
                    }
                    placeholder="e.g., Lahore High Court"
                    className="w-full border-2 border-border focus:border-primary"
                    required
                  />
                  {selectedCity && selectedCity !== "Other" && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="mt-2"
                      onClick={() => setCourtInputMode("dropdown")}
                    >
                      Back to court dropdown
                    </Button>
                  )}
                </>
              )}
            </div>

            {/* Judge */}
            <div>
              <Label htmlFor="judge">Judge</Label>
              <Input
                id="judge"
                value={formData.judge}
                onChange={(e) =>
                  setFormData({ ...formData, judge: e.target.value })
                }
                placeholder="e.g., Hon. Justice Ayesha Malik"
                className="w-full border-2 border-border focus:border-primary"
              />
            </div>

            {/* Case-type specific police fields */}
            {userType === "citizen" && showPoliceFields && (
              <>
                <div>
                  <Label htmlFor="fir_number">FIR Number (if registered)</Label>
                  <Input
                    id="fir_number"
                    value={formData.fir_number}
                    onChange={(e) =>
                      setFormData({ ...formData, fir_number: e.target.value })
                    }
                    placeholder="Leave blank if FIR is not registered yet"
                    className="w-full border-2 border-border focus:border-primary"
                  />
                </div>

                <div>
                  <Label htmlFor="police_station">Police Station (if relevant)</Label>
                  <Input
                    id="police_station"
                    value={formData.police_station}
                    onChange={(e) =>
                      setFormData({ ...formData, police_station: e.target.value })
                    }
                    placeholder="e.g., Civil Lines Police Station, Lahore"
                    className="w-full border-2 border-border focus:border-primary"
                  />
                </div>

              </>
            )}

            {/* Lawyer-specific fields */}
            {userType === "lawyer" && (
              <>
                <div>
                  <Label htmlFor="client_name">Client Name</Label>
                  <Input
                    id="client_name"
                    value={formData.client_name}
                    onChange={(e) =>
                      setFormData({ ...formData, client_name: e.target.value })
                    }
                    placeholder="e.g., Client full name"
                    className="w-full border-2 border-border focus:border-primary"
                  />
                </div>

                <div>
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={formData.priority}
                    onValueChange={(value: "High" | "Medium" | "Low") =>
                      setFormData({ ...formData, priority: value })
                    }
                  >
                    <SelectTrigger id="priority" className="w-full border-2 border-border focus:border-primary">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="High">High</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="Low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}

            {/* Common fields */}
            <div>
              <Label htmlFor="filing_date">Filing Date</Label>
              <Input
                id="filing_date"
                type="date"
                value={formData.filing_date}
                onChange={(e) =>
                  setFormData({ ...formData, filing_date: e.target.value })
                }
                className="w-full border-2 border-border focus:border-primary"
              />
            </div>

            <div>
              <Label htmlFor="next_hearing">Next Hearing Date</Label>
              <Input
                id="next_hearing"
                type="date"
                value={formData.next_hearing}
                onChange={(e) =>
                  setFormData({ ...formData, next_hearing: e.target.value })
                }
                className="w-full border-2 border-border focus:border-primary"
              />
            </div>

            <div>
              <Label htmlFor="description">Case Facts *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder={descriptionPlaceholderByType[selectedCaseType] || descriptionPlaceholderByType.Other}
                className="w-full border-2 border-border focus:border-primary"
                rows={5}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Include timeline, parties, evidence/documents, current stage, and the outcome you want.
              </p>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                disabled={loading}
                className="flex-1"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  "Create Case"
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  )
}

