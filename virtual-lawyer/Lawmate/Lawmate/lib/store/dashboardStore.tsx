"use client"

import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from "react"
import { 
  getCitizenDashboard, 
  getLawyerDashboard,
  type CitizenDashboardData,
  type LawyerDashboardData 
} from "@/lib/services/dashboard"

// Context Types
interface DashboardContextType {
  // Citizen Dashboard
  citizenData: CitizenDashboardData | null
  citizenLoading: boolean
  citizenError: string | null
  refreshCitizenDashboard: () => Promise<void>
  
  // Lawyer Dashboard
  lawyerData: LawyerDashboardData | null
  lawyerLoading: boolean
  lawyerError: string | null
  refreshLawyerDashboard: () => Promise<void>
}

// Create Context
const DashboardContext = createContext<DashboardContextType | undefined>(undefined)

// Provider Component
export function DashboardProvider({ children }: { children: ReactNode }) {
  // Citizen Dashboard State
  const [citizenData, setCitizenData] = useState<CitizenDashboardData | null>(null)
  const [citizenLoading, setCitizenLoading] = useState(true)
  const [citizenError, setCitizenError] = useState<string | null>(null)
  
  // Lawyer Dashboard State
  const [lawyerData, setLawyerData] = useState<LawyerDashboardData | null>(null)
  const [lawyerLoading, setLawyerLoading] = useState(true)
  const [lawyerError, setLawyerError] = useState<string | null>(null)
  
  // Load Citizen Dashboard
  const refreshCitizenDashboard = async () => {
    setCitizenLoading(true)
    setCitizenError(null)
    try {
      const stored = typeof window !== "undefined" ? localStorage.getItem("user") : null
      const user = stored ? JSON.parse(stored) as { id?: string } : null
      const data = await getCitizenDashboard(user?.id)
      console.log("✅ Citizen dashboard data loaded:", data)
      setCitizenData(data)
    } catch (err: any) {
      console.error("❌ Error loading citizen dashboard:", err)
      setCitizenError(err.message || "Failed to load dashboard data")
      // Don't set default data - let components handle null state
      // This way we can show proper error messages
    } finally {
      setCitizenLoading(false)
    }
  }
  
  // Load Lawyer Dashboard
  const refreshLawyerDashboard = async () => {
    setLawyerLoading(true)
    setLawyerError(null)
    try {
      const stored = typeof window !== "undefined" ? localStorage.getItem("user") : null
      const user = stored ? JSON.parse(stored) as { id?: string } : null
      const data = await getLawyerDashboard(user?.id)
      console.log("✅ Lawyer dashboard data loaded:", data)
      setLawyerData(data)
    } catch (err: any) {
      console.error("❌ Error loading lawyer dashboard:", err)
      setLawyerError(err.message || "Failed to load dashboard data")
      // Don't set default data - let components handle null state
      // This way we can show proper error messages
    } finally {
      setLawyerLoading(false)
    }
  }
  
  // Load data on mount (optional - can be called manually from components)
  // useEffect(() => {
  //   refreshCitizenDashboard()
  //   refreshLawyerDashboard()
  // }, [])
  
  const value: DashboardContextType = {
    citizenData,
    citizenLoading,
    citizenError,
    refreshCitizenDashboard,
    lawyerData,
    lawyerLoading,
    lawyerError,
    refreshLawyerDashboard,
  }
  
  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

// Hook to use Dashboard Context
export function useDashboard() {
  const context = useContext(DashboardContext)
  if (context === undefined) {
    throw new Error("useDashboard must be used within a DashboardProvider")
  }
  return context
}

// Hook for Citizen Dashboard
export function useCitizenDashboard() {
  const { citizenData, citizenLoading, citizenError, refreshCitizenDashboard } = useDashboard()
  const hasLoadedRef = useRef(false)
  
  useEffect(() => {
    console.log("🔄 useCitizenDashboard useEffect triggered")
    console.log("   citizenData:", citizenData ? "exists" : "null")
    console.log("   citizenLoading:", citizenLoading)
    console.log("   hasLoadedRef.current:", hasLoadedRef.current)
    
    // Load data once on mount
    if (!hasLoadedRef.current) {
      console.log("✅ Triggering citizen dashboard data load...")
      hasLoadedRef.current = true
      refreshCitizenDashboard()
    } else {
      console.log("⏭️ Skipping load - already loaded or loading")
    }
  }, []) // Only run on mount
  
  return {
    data: citizenData,
    loading: citizenLoading,
    error: citizenError,
    refresh: refreshCitizenDashboard
  }
}

// Hook for Lawyer Dashboard
export function useLawyerDashboard() {
  const { lawyerData, lawyerLoading, lawyerError, refreshLawyerDashboard } = useDashboard()
  const hasLoadedRef = useRef(false)
  
  useEffect(() => {
    console.log("🔄 useLawyerDashboard useEffect triggered")
    console.log("   lawyerData:", lawyerData ? "exists" : "null")
    console.log("   lawyerLoading:", lawyerLoading)
    console.log("   hasLoadedRef.current:", hasLoadedRef.current)
    
    // Load data once on mount
    if (!hasLoadedRef.current) {
      console.log("✅ Triggering lawyer dashboard data load...")
      hasLoadedRef.current = true
      refreshLawyerDashboard()
    } else {
      console.log("⏭️ Skipping load - already loaded or loading")
    }
  }, []) // Only run on mount
  
  return {
    data: lawyerData,
    loading: lawyerLoading,
    error: lawyerError,
    refresh: refreshLawyerDashboard
  }
}

