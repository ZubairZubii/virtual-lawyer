"use client"

import type React from "react"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { FileText, Download } from "lucide-react"
import { useState } from "react"

export function DocumentGenerator() {
  const [documentType, setDocumentType] = useState("")
  const [formData, setFormData] = useState({
    name: "",
    firNumber: "",
    court: "",
    charges: "",
  })

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Generating document:", { documentType, ...formData })
  }

  return (
    <Card className="p-6 border border-border">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-primary" />
        <h2 className="text-lg font-semibold text-foreground">Generate Legal Document</h2>
      </div>

      <form onSubmit={handleGenerate} className="space-y-4">
        <div>
          <Label htmlFor="doc-type">Document Type</Label>
          <Select value={documentType} onValueChange={setDocumentType}>
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Select document type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="bail">Bail Petition</SelectItem>
              <SelectItem value="appeal">Appeal Petition</SelectItem>
              <SelectItem value="remand">Remand Challenge</SelectItem>
              <SelectItem value="evidence">Evidence Submission</SelectItem>
              <SelectItem value="fir">FIR Application</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="name">Your Name</Label>
            <Input
              id="name"
              placeholder="Enter full name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="fir">FIR Number</Label>
            <Input
              id="fir"
              placeholder="FIR/2024/001"
              value={formData.firNumber}
              onChange={(e) => setFormData({ ...formData, firNumber: e.target.value })}
              className="mt-1"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="court">Court Name</Label>
            <Input
              id="court"
              placeholder="District Court, Delhi"
              value={formData.court}
              onChange={(e) => setFormData({ ...formData, court: e.target.value })}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="charges">Charges</Label>
            <Input
              id="charges"
              placeholder="Sections or charges"
              value={formData.charges}
              onChange={(e) => setFormData({ ...formData, charges: e.target.value })}
              className="mt-1"
            />
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <Button type="submit" className="flex-1">
            Generate Document
          </Button>
          <Button type="button" variant="outline" className="bg-transparent">
            <Download className="w-4 h-4 mr-2" />
            Download Template
          </Button>
        </div>
      </form>
    </Card>
  )
}
