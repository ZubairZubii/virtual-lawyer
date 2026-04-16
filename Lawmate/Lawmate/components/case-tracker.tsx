"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Calendar, Users, FileText, AlertCircle } from "lucide-react"

interface CaseData {
  id: string
  firNumber: string
  status: "Active" | "Hearing Scheduled" | "Appeal Filed" | "Closed"
  caseType: string
  court: string
  judge: string
  nextHearing: string
  documents: number
  assignedLawyer?: string
}

export function CaseTracker({ cases }: { cases: CaseData[] }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active":
        return "bg-primary/10 text-primary"
      case "Hearing Scheduled":
        return "bg-accent/10 text-accent"
      case "Appeal Filed":
        return "bg-secondary/10 text-secondary"
      case "Closed":
        return "bg-muted/10 text-muted-foreground"
      default:
        return "bg-muted/10 text-muted-foreground"
    }
  }

  return (
    <div className="space-y-4">
      {cases.map((case_) => (
        <Card key={case_.id} className="p-6 border border-border hover:border-primary transition">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-semibold text-foreground">{case_.firNumber}</h3>
              <p className="text-sm text-muted-foreground">{case_.caseType}</p>
            </div>
            <Badge className={getStatusColor(case_.status)}>{case_.status}</Badge>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <div>
                <p className="text-xs text-muted-foreground">Next Hearing</p>
                <p className="text-foreground">{case_.nextHearing}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="w-4 h-4" />
              <div>
                <p className="text-xs text-muted-foreground">Judge</p>
                <p className="text-foreground">{case_.judge}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <FileText className="w-4 h-4" />
              <div>
                <p className="text-xs text-muted-foreground">Documents</p>
                <p className="text-foreground">{case_.documents}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <AlertCircle className="w-4 h-4" />
              <div>
                <p className="text-xs text-muted-foreground">Court</p>
                <p className="text-foreground">{case_.court}</p>
              </div>
            </div>
          </div>

          {case_.assignedLawyer && (
            <div className="mt-4 pt-4 border-t border-border">
              <p className="text-xs text-muted-foreground mb-1">Assigned Lawyer</p>
              <p className="text-sm font-medium text-foreground">{case_.assignedLawyer}</p>
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
