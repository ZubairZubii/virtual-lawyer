"use client"

import { motion } from "framer-motion"
import { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface AnimatedCardProps {
  children: ReactNode
  className?: string
  hoverScale?: number
  hoverY?: number
  delay?: number
  onClick?: () => void
}

export function AnimatedCard({
  children,
  className = "",
  hoverScale = 1.02,
  hoverY = -4,
  delay = 0,
  onClick,
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5, delay, ease: [0.25, 0.4, 0.25, 1] }}
      whileHover={{
        scale: hoverScale,
        y: hoverY,
        transition: { duration: 0.2 },
      }}
      onClick={onClick}
      className={cn(
        "rounded-xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-xl",
        onClick && "cursor-pointer",
        className
      )}
    >
      {children}
    </motion.div>
  )
}
