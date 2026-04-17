"use client"

import { useState } from "react"
import { motion, AnimatePresence, Reorder } from "framer-motion"
import {
  Calendar,
  Clock,
  User,
  FileText,
  AlertCircle,
  CheckCircle2,
  MoreVertical,
  Plus,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

export interface CaseItem {
  id: string
  title: string
  caseNumber: string
  client: {
    name: string
    avatar?: string
  }
  status: "pending" | "in-progress" | "review" | "completed"
  priority: "low" | "medium" | "high" | "urgent"
  nextHearing?: Date
  assignedTo?: {
    name: string
    avatar?: string
  }
  description: string
  tags: string[]
  documents: number
  createdAt: Date
}

interface Column {
  id: string
  title: string
  status: CaseItem["status"]
  color: string
  icon: any
}

const columns: Column[] = [
  {
    id: "pending",
    title: "Pending Review",
    status: "pending",
    color: "text-yellow-600 dark:text-yellow-400",
    icon: Clock,
  },
  {
    id: "in-progress",
    title: "In Progress",
    status: "in-progress",
    color: "text-blue-600 dark:text-blue-400",
    icon: AlertCircle,
  },
  {
    id: "review",
    title: "Under Review",
    status: "review",
    color: "text-purple-600 dark:text-purple-400",
    icon: FileText,
  },
  {
    id: "completed",
    title: "Completed",
    status: "completed",
    color: "text-green-600 dark:text-green-400",
    icon: CheckCircle2,
  },
]

const priorityColors = {
  low: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/30",
  medium: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/30",
  high: "bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/30",
  urgent: "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/30",
}

interface PremiumCaseKanbanProps {
  cases: CaseItem[]
  onCaseClick?: (caseId: string) => void
  onStatusChange?: (caseId: string, newStatus: CaseItem["status"]) => void
  onAddCase?: (status: CaseItem["status"]) => void
}

export function PremiumCaseKanban({ cases, onCaseClick, onStatusChange, onAddCase }: PremiumCaseKanbanProps) {
  const [items, setItems] = useState(cases)

  const getCasesByStatus = (status: CaseItem["status"]) => {
    return items.filter((item) => item.status === status)
  }

  const handleDragEnd = (caseId: string, newStatus: CaseItem["status"]) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === caseId ? { ...item, status: newStatus } : item
      )
    )
    onStatusChange?.(caseId, newStatus)
  }

  return (
    <div className="h-full overflow-x-auto">
      <div className="flex gap-6 p-6 min-w-max">
        {columns.map((column, columnIndex) => (
          <motion.div
            key={column.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: columnIndex * 0.1 }}
            className="flex flex-col w-80 shrink-0"
          >
            {/* Column Header */}
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn("w-10 h-10 rounded-lg bg-card border border-border flex items-center justify-center", column.color)}>
                  <column.icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{column.title}</h3>
                  <span className="text-xs text-muted-foreground">
                    {getCasesByStatus(column.status).length} cases
                  </span>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => onAddCase?.(column.status)}
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>

            {/* Cases List */}
            <div className="flex-1 space-y-3 min-h-[200px] p-1">
              <AnimatePresence mode="popLayout">
                {getCasesByStatus(column.status).map((caseItem, index) => (
                  <CaseCard
                    key={caseItem.id}
                    caseItem={caseItem}
                    index={index}
                    onClick={() => onCaseClick?.(caseItem.id)}
                    onStatusChange={handleDragEnd}
                  />
                ))}
              </AnimatePresence>

              {getCasesByStatus(column.status).length === 0 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center justify-center h-32 border-2 border-dashed border-border rounded-lg text-muted-foreground text-sm"
                >
                  No cases
                </motion.div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function CaseCard({
  caseItem,
  index,
  onClick,
  onStatusChange,
}: {
  caseItem: CaseItem
  index: number
  onClick: () => void
  onStatusChange: (caseId: string, newStatus: CaseItem["status"]) => void
}) {
  const [isDragging, setIsDragging] = useState(false)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.2, delay: index * 0.05 }}
      whileHover={{ scale: 1.02, y: -2 }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragStart={() => setIsDragging(true)}
      onDragEnd={() => setIsDragging(false)}
      className={cn(
        "group relative rounded-lg border border-border bg-card p-4 cursor-pointer shadow-sm hover:shadow-md transition-all",
        isDragging && "opacity-50"
      )}
      onClick={onClick}
    >
      {/* Priority Badge */}
      <div className="absolute top-3 right-3 flex items-center gap-2">
        <Badge className={cn("text-xs font-medium", priorityColors[caseItem.priority])}>
          {caseItem.priority}
        </Badge>
        <DropdownMenu>
          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <MoreVertical className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
            <DropdownMenuItem onClick={() => onStatusChange(caseItem.id, "pending")}>
              Move to Pending
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onStatusChange(caseItem.id, "in-progress")}>
              Move to In Progress
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onStatusChange(caseItem.id, "review")}>
              Move to Review
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onStatusChange(caseItem.id, "completed")}>
              Move to Completed
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Case Number */}
      <div className="text-xs text-muted-foreground mb-2">{caseItem.caseNumber}</div>

      {/* Title */}
      <h4 className="font-semibold text-foreground mb-2 pr-20 line-clamp-2 group-hover:text-primary transition-colors">
        {caseItem.title}
      </h4>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
        {caseItem.description}
      </p>

      {/* Tags */}
      {caseItem.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-4">
          {caseItem.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
          {caseItem.tags.length > 2 && (
            <Badge variant="outline" className="text-xs">
              +{caseItem.tags.length - 2}
            </Badge>
          )}
        </div>
      )}

      {/* Next Hearing */}
      {caseItem.nextHearing && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4 p-2 rounded bg-muted/30">
          <Calendar className="w-3.5 h-3.5" />
          <span>Next: {caseItem.nextHearing.toLocaleDateString()}</span>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-border/50">
        {/* Client */}
        <div className="flex items-center gap-2">
          <Avatar className="w-6 h-6 border border-border">
            <AvatarImage src={caseItem.client.avatar} />
            <AvatarFallback className="text-xs bg-muted">
              {caseItem.client.name[0]}
            </AvatarFallback>
          </Avatar>
          <span className="text-xs text-muted-foreground">{caseItem.client.name}</span>
        </div>

        {/* Documents Count */}
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <FileText className="w-3.5 h-3.5" />
          {caseItem.documents}
        </div>
      </div>

      {/* Assigned To */}
      {caseItem.assignedTo && (
        <div className="mt-3 pt-3 border-t border-border/50 flex items-center gap-2">
          <Avatar className="w-5 h-5">
            <AvatarImage src={caseItem.assignedTo.avatar} />
            <AvatarFallback className="text-xs bg-primary/10 text-primary">
              {caseItem.assignedTo.name[0]}
            </AvatarFallback>
          </Avatar>
          <span className="text-xs text-muted-foreground">
            Assigned to {caseItem.assignedTo.name}
          </span>
        </div>
      )}
    </motion.div>
  )
}
