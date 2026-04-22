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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Validate required fields
      if (!formData.case_type || !formData.court) {
        throw new Error("Case type and court are required")
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

  const addSection = () => {
    const section = prompt("Enter section number (e.g., 302):")
    if (section && section.trim()) {
      setFormData({
        ...formData,
        sections: [...(formData.sections || []), section.trim()],
      })
    }
  }

  const removeSection = (index: number) => {
    setFormData({
      ...formData,
      sections: formData.sections?.filter((_, i) => i !== index) || [],
    })
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

            {/* Court */}
            <div>
              <Label htmlFor="court">Court *</Label>
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

            {/* Citizen-specific fields */}
            {userType === "citizen" && (
              <>
                <div>
                  <Label htmlFor="fir_number">FIR Number</Label>
                  <Input
                    id="fir_number"
                    value={formData.fir_number}
                    onChange={(e) =>
                      setFormData({ ...formData, fir_number: e.target.value })
                    }
                    placeholder="e.g., FIR/2024/150"
                    className="w-full border-2 border-border focus:border-primary"
                  />
                </div>

                <div>
                  <Label htmlFor="police_station">Police Station</Label>
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

                <div>
                  <Label>Sections</Label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.sections?.map((section, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center gap-2"
                      >
                        {section}
                        <button
                          type="button"
                          onClick={() => removeSection(index)}
                          className="hover:text-destructive"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addSection}
                  >
                    + Add Section
                  </Button>
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
                    placeholder="e.g., Ahmed Khan"
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
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Case description (optional)"
                className="w-full border-2 border-border focus:border-primary"
                rows={3}
              />
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

