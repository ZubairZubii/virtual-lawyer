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
import { uploadDocument } from "@/lib/services/documents"

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

type DynamicFieldConfig = {
  key: string
  label: string
  placeholder: string
  required?: boolean
}

const CASE_TYPE_OPTIONS = [
  "Bail Application",
  "FIR Complaint",
  "Criminal Appeal",
  "Revision Petition",
  "Cyber Crime Complaint",
  "Domestic Violence",
  "Narcotics Matter",
  "Fraud / Cheating",
  "Appeal",
  "Other",
]

const CASE_TYPE_DYNAMIC_FIELDS: Record<string, DynamicFieldConfig[]> = {
  "Bail Application": [
    { key: "arrest_date", label: "Arrest Date", placeholder: "YYYY-MM-DD", required: true },
    { key: "custody_status", label: "Custody Status", placeholder: "In custody / Not in custody", required: true },
    { key: "urgent_ground", label: "Urgent Ground", placeholder: "Medical, family hardship, weak evidence..." },
  ],
  "FIR Complaint": [
    { key: "incident_date", label: "Incident Date", placeholder: "YYYY-MM-DD", required: true },
    { key: "incident_location", label: "Incident Location", placeholder: "Area, city, landmark", required: true },
    { key: "accused_details", label: "Accused Details", placeholder: "Known/unknown, identifiers if available" },
  ],
  "Criminal Appeal": [
    { key: "trial_order_date", label: "Trial Court Order Date", placeholder: "YYYY-MM-DD", required: true },
    { key: "sentence_details", label: "Sentence / Order Summary", placeholder: "Conviction, sentence length, fine..." },
    { key: "appeal_ground", label: "Primary Appeal Ground", placeholder: "Misreading evidence, procedural defect..." },
  ],
  "Revision Petition": [
    { key: "impugned_order_date", label: "Impugned Order Date", placeholder: "YYYY-MM-DD", required: true },
    { key: "procedural_defect", label: "Procedural Defect", placeholder: "Jurisdiction issue, illegal order..." },
    { key: "relief_sought", label: "Relief Sought", placeholder: "Set aside order / remand / other relief" },
  ],
  "Cyber Crime Complaint": [
    { key: "platform", label: "Platform / Channel", placeholder: "WhatsApp, Facebook, email, website..." },
    { key: "digital_evidence", label: "Digital Evidence", placeholder: "Screenshots, logs, account IDs..." },
  ],
  "Domestic Violence": [
    { key: "relationship", label: "Relationship", placeholder: "Spouse / family relation / guardian..." },
    { key: "incident_frequency", label: "Incident Frequency", placeholder: "Single, repeated, ongoing..." },
  ],
  "Narcotics Matter": [
    { key: "recovery_details", label: "Recovery Details", placeholder: "Quantity, place of recovery..." },
    { key: "search_witnesses", label: "Search Witnesses", placeholder: "Independent witnesses present or not" },
  ],
  "Fraud / Cheating": [
    { key: "amount_involved", label: "Amount Involved", placeholder: "PKR amount if any" },
    { key: "transaction_mode", label: "Transaction Mode", placeholder: "Cash, bank transfer, online wallet..." },
  ],
}

const MAX_CASE_DOCS = 2

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
  const [dynamicFields, setDynamicFields] = useState<Record<string, string>>({})
  const [uploadedDocs, setUploadedDocs] = useState<Array<{ doc_id: string; file_name: string }>>([])
  const [docLimitError, setDocLimitError] = useState<string | null>(null)
  const selectedCaseType = formData.case_type
  const selectedDynamicFieldConfig = CASE_TYPE_DYNAMIC_FIELDS[selectedCaseType] || []
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

  const handleDocUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setDocLimitError(null)
    const allowed = Math.max(0, MAX_CASE_DOCS - uploadedDocs.length)
    if (allowed <= 0) {
      setDocLimitError(`Maximum ${MAX_CASE_DOCS} case documents are allowed.`)
      return
    }
    const selected = Array.from(files).slice(0, allowed)
    try {
      const userRaw = typeof window !== "undefined" ? localStorage.getItem("user") : null
      const user = userRaw ? JSON.parse(userRaw) : {}
      const role = userType === "lawyer" ? "lawyer" : "citizen"
      const uploaded = await Promise.all(
        selected.map((f) =>
          uploadDocument(f, {
            email: user?.email || "",
            role,
          }),
        ),
      )
      setUploadedDocs((prev) => [...prev, ...uploaded.map((u) => ({ doc_id: u.doc_id, file_name: u.file_name }))])
      if (files.length > allowed) {
        setDocLimitError(`Only ${allowed} file(s) were added due to max ${MAX_CASE_DOCS} documents.`)
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to upload case documents."
      setError(message)
    }
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
      for (const field of selectedDynamicFieldConfig) {
        if (field.required && !(dynamicFields[field.key] || "").trim()) {
          throw new Error(`${field.label} is required for ${selectedCaseType}.`)
        }
      }

      const caseSummary = [
        `Case Type: ${formData.case_type}`,
        selectedCity ? `City: ${selectedCity}` : "",
        `Court: ${formData.court}`,
        ...selectedDynamicFieldConfig
          .map((f) => `${f.label}: ${dynamicFields[f.key] || "Not provided"}`),
      ]
        .filter(Boolean)
        .join(" | ")

      const response = await createCase(
        {
          ...formData,
          case_summary: caseSummary,
          case_metadata: {
            city: selectedCity || "",
            ...dynamicFields,
          },
          uploaded_documents: uploadedDocs,
        },
        userType,
      )
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
                onValueChange={(value) => {
                  setFormData({ ...formData, case_type: value })
                  setDynamicFields({})
                }}
              >
                <SelectTrigger id="case_type" className="w-full border-2 border-border focus:border-primary">
                  <SelectValue placeholder="Select case type" />
                </SelectTrigger>
                <SelectContent>
                  {CASE_TYPE_OPTIONS.map((caseType) => (
                    <SelectItem key={caseType} value={caseType}>
                      {caseType}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedDynamicFieldConfig.length > 0 && (
              <div className="space-y-3 p-4 rounded-lg border border-border/50 bg-muted/20">
                <p className="text-sm font-semibold">Case-Type Intake Fields</p>
                {selectedDynamicFieldConfig.map((field) => (
                  <div key={field.key}>
                    <Label htmlFor={field.key}>
                      {field.label}
                      {field.required ? " *" : ""}
                    </Label>
                    <Input
                      id={field.key}
                      value={dynamicFields[field.key] || ""}
                      onChange={(e) =>
                        setDynamicFields((prev) => ({
                          ...prev,
                          [field.key]: e.target.value,
                        }))
                      }
                      placeholder={field.placeholder}
                      className="w-full border-2 border-border focus:border-primary"
                    />
                  </div>
                ))}
              </div>
            )}

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

            <div className="space-y-2 p-4 rounded-lg border border-border/50">
              <Label htmlFor="caseDocs">Case Documents (optional, max 2)</Label>
              <Input
                id="caseDocs"
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                onChange={(e) => void handleDocUpload(e.target.files)}
              />
              {docLimitError && <p className="text-xs text-orange-500">{docLimitError}</p>}
              {uploadedDocs.length > 0 && (
                <ul className="text-xs text-muted-foreground space-y-1">
                  {uploadedDocs.map((doc) => (
                    <li key={doc.doc_id}>Attached: {doc.file_name}</li>
                  ))}
                </ul>
              )}
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

