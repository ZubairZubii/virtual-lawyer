"use client"

import { motion } from "framer-motion"
import { Star, MapPin, Award, CheckCircle2, MessageSquare, Video, Calendar, TrendingUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

export interface LawyerData {
  id: string
  name: string
  avatar?: string
  specialization: string[]
  location: string
  rating: number
  reviewCount: number
  casesWon: number
  experience: number
  hourlyRate: number
  languages: string[]
  verified: boolean
  available: boolean
  responseTime: string
  successRate: number
}

interface LawyerCardPremiumProps {
  lawyer: LawyerData
  onConnect?: () => void
  onViewProfile?: () => void
  delay?: number
}

export function LawyerCardPremium({ lawyer, onConnect, onViewProfile, delay = 0 }: LawyerCardPremiumProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5, delay, ease: [0.25, 0.4, 0.25, 1] }}
      whileHover={{
        y: -8,
        transition: { duration: 0.2 },
      }}
      className="group relative"
    >
      {/* Gradient Glow on Hover */}
      <div className="absolute -inset-0.5 rounded-2xl bg-gradient-to-r from-primary to-accent opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-300" />

      {/* Main Card */}
      <div className="relative rounded-2xl border border-border bg-card p-6 shadow-sm transition-all duration-300 group-hover:border-primary/50 group-hover:shadow-xl overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.02] group-hover:opacity-[0.04] transition-opacity" />

        {/* Verified Badge */}
        {lawyer.verified && (
          <div className="absolute top-4 right-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: delay + 0.2, type: "spring", stiffness: 200 }}
            >
              <Badge className="bg-primary/10 text-primary border-primary/30 gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Verified
              </Badge>
            </motion.div>
          </div>
        )}

        {/* Availability Indicator */}
        {lawyer.available && (
          <div className="absolute top-4 left-4">
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/30"
            >
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-xs font-medium text-green-700 dark:text-green-400">Available</span>
            </motion.div>
          </div>
        )}

        {/* Header */}
        <div className="flex items-start gap-4 mb-6 mt-8">
          {/* Avatar with Ring */}
          <div className="relative">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="relative"
            >
              <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-primary to-accent opacity-50 blur group-hover:opacity-100 transition-opacity" />
              <Avatar className="relative w-16 h-16 border-2 border-background">
                <AvatarImage src={lawyer.avatar} alt={lawyer.name} />
                <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-primary-foreground font-bold">
                  {lawyer.name.split(" ").map(n => n[0]).join("").toUpperCase()}
                </AvatarFallback>
              </Avatar>
            </motion.div>

            {/* Success Rate Badge */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: delay + 0.3, type: "spring" }}
              className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center border-2 border-background shadow-lg"
            >
              <TrendingUp className="w-4 h-4 text-primary-foreground" />
            </motion.div>
          </div>

          {/* Name and Basic Info */}
          <div className="flex-1">
            <h3 className="font-bold text-lg text-foreground mb-1 group-hover:text-primary transition-colors">
              {lawyer.name}
            </h3>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={cn(
                      "w-3.5 h-3.5",
                      i < Math.floor(lawyer.rating)
                        ? "fill-yellow-400 text-yellow-400"
                        : "fill-muted text-muted"
                    )}
                  />
                ))}
              </div>
              <span className="text-sm font-semibold text-foreground">{lawyer.rating.toFixed(1)}</span>
              <span className="text-xs text-muted-foreground">({lawyer.reviewCount})</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <MapPin className="w-3.5 h-3.5" />
              {lawyer.location}
            </div>
          </div>
        </div>

        {/* Specializations */}
        <div className="flex flex-wrap gap-2 mb-4">
          {lawyer.specialization.slice(0, 3).map((spec, i) => (
            <motion.div
              key={spec}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: delay + 0.1 * i }}
            >
              <Badge variant="secondary" className="text-xs">
                {spec}
              </Badge>
            </motion.div>
          ))}
          {lawyer.specialization.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{lawyer.specialization.length - 3}
            </Badge>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3 mb-4 p-3 rounded-lg bg-muted/30 border border-border/50">
          <div className="text-center">
            <div className="text-lg font-bold text-primary">{lawyer.casesWon}+</div>
            <div className="text-xs text-muted-foreground">Cases Won</div>
          </div>
          <div className="text-center border-x border-border/50">
            <div className="text-lg font-bold text-accent">{lawyer.experience}y</div>
            <div className="text-xs text-muted-foreground">Experience</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-green-600 dark:text-green-400">{lawyer.successRate}%</div>
            <div className="text-xs text-muted-foreground">Success</div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="space-y-2 mb-4 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Response Time:</span>
            <span className="font-semibold text-foreground">{lawyer.responseTime}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Hourly Rate:</span>
            <span className="font-semibold text-primary">${lawyer.hourlyRate}/hr</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Languages:</span>
            <span className="font-medium text-foreground">{lawyer.languages.join(", ")}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <Button
            size="sm"
            variant="outline"
            className="gap-2 hover:bg-primary/10 hover:border-primary/50"
            onClick={onViewProfile}
          >
            <MessageSquare className="w-4 h-4" />
            Message
          </Button>
          <Button
            size="sm"
            className="gap-2 bg-gradient-to-r from-primary to-accent text-primary-foreground border-0 hover:shadow-lg"
            onClick={onConnect}
          >
            <Video className="w-4 h-4" />
            Consult
          </Button>
        </div>

        {/* Bottom CTA */}
        <motion.button
          onClick={onViewProfile}
          className="w-full mt-3 py-2 text-xs font-medium text-primary hover:text-accent transition-colors flex items-center justify-center gap-1.5 group/btn"
          whileHover={{ scale: 1.02 }}
        >
          <Calendar className="w-3.5 h-3.5" />
          View Full Profile & Availability
          <motion.span
            className="inline-block"
            initial={{ x: 0 }}
            animate={{ x: [0, 4, 0] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          >
            →
          </motion.span>
        </motion.button>
      </div>
    </motion.div>
  )
}
