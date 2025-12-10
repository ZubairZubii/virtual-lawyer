"use client"

import { useRouter } from "next/navigation"
import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { AnimatedTestimonials } from "@/components/ui/animated-testimonials"
import { motion } from "framer-motion"
import {
  Shield,
  BarChart3,
  Users,
  Brain,
  FileText,
  Lock,
  Zap,
  TrendingUp,
  ArrowRight,
  ChevronRight,
  CheckCircle2,
  Scale as Scales,
  Award,
  Globe,
  Activity,
  Check,
} from "lucide-react"

export default function Home() {
  const router = useRouter()
  const [isLoaded, setIsLoaded] = useState(false)
  const [activeFeature, setActiveFeature] = useState(0)
  const [scrollY, setScrollY] = useState(0)
  const marqueeItems = [
    "Instant FIR & bail explainer in plain English",
    "AI-drafted petitions reviewed by lawyers",
    "Court-date reminders with smart next steps",
    "Evidence checklists tailored to your case",
    "Direct access to verified criminal lawyers",
    "Secure document vault with role-based sharing",
    "Actionable insights from case timelines",
    "Rights guidance backed by current precedents",
    "Bail preparation packs",
    "Section-wise legal clarity",
    "AI + human review loop",
    "Victim rights assistance",
    "Appeal & revision guidance",
  ]
  const firstSetRef = useRef<HTMLDivElement>(null)
  const [marqueeWidth, setMarqueeWidth] = useState(0)

  const steps = [
    { number: "01", title: "Tell us the situation", desc: "Share charges, FIR number, court, and dates. We keep it private." },
    { number: "02", title: "Get instant clarity", desc: "AI explains options, sections involved, and practical next steps." },
    { number: "03", title: "Draft with review", desc: "Generate petitions and packs; verified lawyers refine before filing." },
    { number: "04", title: "Track & respond", desc: "Reminders, evidence tasks, and hearing prep so nothing slips." },
  ]
  const [currentStep, setCurrentStep] = useState(0)
  const [isMobile, setIsMobile] = useState(false)
  const dotRefs = useRef<(HTMLDivElement | null)[]>([])
  const [dotX, setDotX] = useState<number[]>([])

  useEffect(() => {
    setIsLoaded(true)
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    if (firstSetRef.current) {
      let width = 0
      const children = Array.from(firstSetRef.current.children) as HTMLElement[]
      children.forEach((child, i) => {
        width += child.offsetWidth
        if (i < children.length - 1) width += 32 // gap size
      })
      setMarqueeWidth(width)
    }
  }, [])

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener("resize", checkMobile)
    return () => window.removeEventListener("resize", checkMobile)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [steps.length])

  useEffect(() => {
    if (isMobile) return
    const updatePositions = () => {
      const positions = dotRefs.current.map((dot) => {
        if (dot) {
          const rect = dot.getBoundingClientRect()
          const containerRect = dot.closest(".timeline-container")?.getBoundingClientRect()
          return containerRect ? rect.left - containerRect.left + rect.width / 2 : 0
        }
        return 0
      })
      setDotX(positions)
    }
    updatePositions()
    window.addEventListener("resize", updatePositions)
    return () => window.removeEventListener("resize", updatePositions)
  }, [isMobile])

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-card/10 overflow-hidden">
      {/* Animated background with multiple gradient orbs */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/8 via-background to-accent/8"></div>

        {/* Animated gradient orbs */}
        <div className="absolute top-0 right-1/3 w-[600px] h-[600px] bg-primary/15 rounded-full blur-3xl opacity-40 animate-float"></div>
        <div
          className="absolute top-1/4 right-0 w-[500px] h-[500px] bg-accent/12 rounded-full blur-3xl opacity-30 animate-float"
          style={{ animationDelay: "1.5s" }}
        ></div>
        <div
          className="absolute -bottom-1/4 left-1/4 w-[600px] h-[600px] bg-secondary/10 rounded-full blur-3xl opacity-35 animate-float"
          style={{ animationDelay: "3s" }}
        ></div>

        {/* Grid background pattern */}
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

        {/* Radial gradient overlay */}
        <div className="absolute inset-0 bg-radial-gradient opacity-40"></div>
      </div>

      {/* Navigation Header */}
      <header
        className={`border-b border-border/30 sticky top-0 z-50 glass-effect transition-all duration-700 ${
          isLoaded ? "translate-y-0 opacity-100" : "-translate-y-full opacity-0"
        }`}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div
            className="flex items-center gap-3 group cursor-pointer hover:scale-105 transition-transform"
            onClick={() => router.push("/")}
          >
            <div className="w-11 h-11 rounded-xl gradient-primary flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all">
              <Scales className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Lawmate
              </span>
              <p className="text-xs text-muted-foreground">Legal Excellence Platform</p>
            </div>
          </div>

          <nav className="hidden lg:flex gap-8 items-center">
            {[
              { label: "Features", id: "features" },
              { label: "Process", id: "process" },
              { label: "Impact", id: "impact" },
              { label: "FAQ", id: "faq" },
            ].map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors duration-300 relative group"
              >
                {item.label}
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-primary to-accent group-hover:w-full transition-all duration-300"></span>
              </a>
            ))}
          </nav>

          <div className="flex gap-3">
            <Button
              variant="outline"
              className="hidden sm:flex bg-transparent hover:bg-primary/10 border-primary/30"
              onClick={() => router.push("/login")}
            >
              Sign In
            </Button>
            <Button
              className="gradient-primary text-primary-foreground border-0"
              onClick={() => router.push("/signup")}
            >
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section - Premium Design */}
      <section className="relative pt-20 pb-32 sm:pt-32 sm:pb-40 overflow-hidden">
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl opacity-30 animate-pulse"></div>
        </div>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div
            className={`text-center transition-all duration-1000 ${
              isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
            }`}
          >
            {/* Badge */}
            <div className="inline-block mb-8 px-5 py-2.5 rounded-full bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/40 text-sm font-semibold text-primary animate-pulse-glow group hover:animate-none transition-all cursor-pointer">
              <span className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Revolutionizing Criminal Legal Access with AI
                <ArrowRight className="w-4 h-4" />
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-6xl font-bold text-foreground mb-6 text-balance leading-tight tracking-tight">
              Criminal-law answers in minutes, <br />
              <span className="relative inline-block">
                <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-primary animate-shimmer opacity-75"></span>
                <span className="relative bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  guided by Lawmate
                </span>
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-base sm:text-lg lg:text-xl text-muted-foreground mb-10 text-balance max-w-3xl mx-auto leading-relaxed font-light">
              AI clarity plus verified criminal-law attorneys. Understand your rights, draft filings that comply, and
              stay on top of every hearing without getting lost in procedure.
            </p>

            {/* CTA Buttons */}
            <div className="flex gap-4 justify-center flex-col sm:flex-row items-center mb-16 flex-wrap">
              <Button
                size="lg"
                className="gradient-primary text-primary-foreground border-0 shadow-xl hover:shadow-2xl hover:scale-105 transition-all px-8"
                onClick={() => router.push("/citizen")}
              >
                <Zap className="w-5 h-5 mr-2" />
                Start Free Now
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="hover:bg-primary/10 bg-transparent border-primary/50 px-8"
                onClick={() => router.push("/login")}
              >
                Watch Demo
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex justify-center items-center gap-8 flex-wrap text-sm bg-card/40 glass-effect backdrop-blur-sm rounded-2xl p-6 max-w-2xl mx-auto border border-border/50">
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5 text-primary" />
                <span className="font-semibold text-foreground">2,340+ Users</span>
              </div>
              <div className="w-px h-6 bg-border/50"></div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-accent" />
                <span className="font-semibold text-foreground">456+ Verified Lawyers</span>
              </div>
              <div className="w-px h-6 bg-border/50"></div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                <span className="font-semibold text-foreground">99.9% Uptime</span>
              </div>
            </div>
          </div>

        {/* Moving Value Marquee */}
        <section className="py-12 mt-14" id="features">
          <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-6 text-center">
            <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">What we deliver every day</p>
            <div className="relative overflow-hidden rounded-xl border border-border/40 bg-card/70 marquee-mask">
              <div className="flex overflow-hidden relative z-10">
                <motion.div
                  className="flex items-center gap-8"
                  animate={{ x: marqueeWidth ? [0, -marqueeWidth] : 0 }}
                  transition={{
                    x: { repeat: Number.POSITIVE_INFINITY, repeatType: "loop", duration: marqueeWidth ? marqueeWidth / 60 : 12, ease: "linear" },
                  }}
                >
                  <div ref={firstSetRef} className="flex items-center gap-8 flex-shrink-0">
                    {marqueeItems.map((item, index) => (
                      <span
                        key={`${item}-${index}-first`}
                        className="flex-shrink-0 px-4 py-2 rounded-full border border-border/50 bg-background/80 text-sm text-foreground flex items-center gap-2"
                      >
                        <span className="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-accent shadow"></span>
                        {item}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-8 flex-shrink-0">
                    {marqueeItems.map((item, index) => (
                      <span
                        key={`${item}-${index}-second`}
                        className="flex-shrink-0 px-4 py-2 rounded-full border border-border/50 bg-background/80 text-sm text-foreground flex items-center gap-2"
                      >
                        <span className="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-accent shadow"></span>
                        {item}
                      </span>
                    ))}
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </section>

        {/* Case Journey - animated timeline */}
        <section id="process" className="py-14 border-t border-b border-border/30 bg-gradient-to-b from-card/10 via-background to-card/10">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-10">
            <div className="text-center space-y-2">
              <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">How you move forward</p>
              <h3 className="text-3xl sm:text-4xl font-bold text-foreground">A clear path from panic to prepared</h3>
            </div>

            {isMobile ? (
              <div className="relative">
                <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-border via-border/80 to-border/40" />
                <div className="space-y-8">
                  {steps.map((step, index) => {
                    const isActive = index === currentStep
                    const isCompleted = index < currentStep
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        className="relative flex items-start"
                      >
                        <motion.div
                          onClick={() => setCurrentStep(index)}
                          animate={{ scale: isActive ? 1.1 : 1 }}
                          whileHover={{ scale: 1.15 }}
                          className="relative cursor-pointer z-10 mr-4"
                        >
                          <div
                            className={`w-11 h-11 rounded-full border-2 flex items-center justify-center transition-all duration-400 backdrop-blur-sm ${
                              isCompleted || isActive ? "border-primary bg-background shadow-lg shadow-primary/20" : "border-border bg-background/80"
                            }`}
                          >
                            {isCompleted ? (
                              <motion.div
                                className="w-6 h-6 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center"
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                              >
                                <Check size={12} className="text-primary-foreground" />
                              </motion.div>
                            ) : (
                              <motion.div
                                className={`w-3 h-3 rounded-full ${isActive ? "bg-gradient-to-br from-primary to-accent" : "bg-border"}`}
                              />
                            )}
                          </div>
                        </motion.div>

                        <motion.div
                          animate={{ scale: isActive ? 1.02 : 1 }}
                          whileHover={{ scale: 1.03, y: -2 }}
                          className={`flex-1 p-5 bg-card/80 backdrop-blur-sm rounded-xl border transition-all duration-400 ${
                            isActive ? "border-primary/30 shadow-lg shadow-primary/10" : "border-border hover:border-border/80"
                          }`}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <span className="text-primary text-sm font-semibold">{step.number}</span>
                              <span className="font-semibold text-foreground">{step.title}</span>
                            </div>
                          </div>
                          <p className="text-sm text-muted-foreground leading-relaxed">{step.desc}</p>
                        </motion.div>
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            ) : (
              <div className="timeline-container relative">
                <motion.div
                  className="absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border/70 to-transparent -translate-y-1/2 z-10"
                  initial={{ scaleX: 0 }}
                  whileInView={{ scaleX: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 1, ease: "easeInOut" }}
                />

                {dotX.length > 0 && (
                  <>
                    <motion.div
                      className="absolute top-1/2 h-px bg-gradient-to-r from-primary to-accent -translate-y-1/2 z-20"
                      animate={{ width: currentStep === 0 ? 0 : dotX[currentStep] - dotX[0], x: dotX[0] || 0 }}
                      transition={{ duration: 0.6, ease: "easeInOut" }}
                    />
                    <motion.div
                      className="absolute top-1/2 w-3 h-3 bg-gradient-to-br from-primary to-accent rounded-full -translate-y-1/2 z-30 shadow-lg shadow-primary/30"
                      animate={{ x: (dotX[currentStep] || 0) - 6 }}
                      transition={{ duration: 0.6, ease: "easeInOut" }}
                    />
                  </>
                )}

                <div className="relative z-40 py-12">
                  <div className="grid grid-cols-4 gap-6 lg:gap-10">
                    {steps.map((step, index) => {
                      const isBelow = index % 2 !== 0
                      const isActive = index === currentStep
                      const isCompleted = index < currentStep

                      const Card = (
                        <motion.div
                          initial={{ opacity: 0, y: isBelow ? 30 : -30, scale: 0.95 }}
                          whileInView={{ opacity: 1, y: 0, scale: isActive ? 1.02 : 1 }}
                          viewport={{ once: true }}
                          transition={{ duration: 0.6, delay: index * 0.15 }}
                          whileHover={{ scale: 1.04, y: isBelow ? -6 : 6 }}
                          className={`w-full max-w-xs p-6 bg-card/80 backdrop-blur-sm rounded-xl border transition-all duration-400 ${
                            isActive ? "border-primary/30 shadow-xl shadow-primary/10" : "border-border hover:border-border/80"
                          }`}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <span className="text-primary font-semibold">{step.number}</span>
                              <span className="text-lg font-semibold text-foreground">{step.title}</span>
                            </div>
                          </div>
                          <p className="text-sm text-muted-foreground leading-relaxed">{step.desc}</p>
                          <div className="mt-4 h-1 bg-border rounded-full overflow-hidden">
                            <motion.div
                              className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                              initial={{ width: "0%" }}
                              animate={{ width: isCompleted ? "100%" : isActive ? "70%" : "0%" }}
                              transition={{ duration: 0.6 }}
                            />
                          </div>
                        </motion.div>
                      )

                      return (
                        <div key={index} className="relative flex flex-col items-center">
                          {!isBelow && <div className="mb-14 lg:mb-24">{Card}</div>}

                          <motion.div
                            ref={(el) => (dotRefs.current[index] = el)}
                            onClick={() => setCurrentStep(index)}
                            initial={{ opacity: 0, scale: 0 }}
                            whileInView={{ opacity: 1, scale: isActive ? 1.1 : 1 }}
                            viewport={{ once: true }}
                            transition={{ type: "spring", stiffness: 260, damping: 18, delay: index * 0.1 }}
                            whileHover={{ scale: 1.2 }}
                            className="relative cursor-pointer z-50"
                          >
                            <div
                              className={`w-12 h-12 rounded-full border-2 flex items-center justify-center transition-all duration-400 backdrop-blur-sm ${
                                isCompleted || isActive
                                  ? "border-primary bg-background shadow-xl shadow-primary/20"
                                  : "border-border bg-background/80 hover:border-border/80"
                              }`}
                            >
                              {isCompleted ? (
                                <motion.div
                                  className="w-6 h-6 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center"
                                  initial={{ scale: 0 }}
                                  animate={{ scale: 1 }}
                                >
                                  <Check size={12} className="text-primary-foreground" />
                                </motion.div>
                              ) : (
                                <motion.div
                                  className={`w-3 h-3 rounded-full ${isActive ? "bg-gradient-to-br from-primary to-accent" : "bg-border"}`}
                                />
                              )}
                            </div>
                          </motion.div>

                          {isBelow && <div className="mt-14 lg:mt-24">{Card}</div>}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

          {/* Role Cards - Enhanced Design */}
          <div
            className={`grid grid-cols-1 md:grid-cols-3 gap-6 mt-24 transition-all duration-1000 ${
              isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
            }`}
            style={{ transitionDelay: "200ms" }}
          >
            {[
              {
                icon: Shield,
                title: "For Citizens",
                desc: "Navigate criminal law with confidence. Get 24/7 AI guidance, auto-generate legal documents, track cases in real-time, and find the perfect lawyer.",
                features: ["24/7 AI Chatbot", "Smart Document Gen", "Real-time Case Tracking", "Lawyer Marketplace"],
                role: "/citizen",
                gradient: "from-primary to-accent",
              },
              {
                icon: BarChart3,
                title: "For Lawyers",
                desc: "Grow your practice exponentially. Manage clients, access AI-powered analytics, handle cases smartly, and scale your legal business.",
                features: ["Client Dashboard", "Advanced Analytics", "Case Management", "Performance Metrics"],
                role: "/lawyer",
                gradient: "from-accent to-secondary",
              },
              {
                icon: Users,
                title: "For Admins",
                desc: "Oversee the entire platform. Monitor users, verify lawyers, track compliance, analyze system health, and ensure platform excellence.",
                features: ["User Management", "System Health", "Platform Analytics", "Security Controls"],
                role: "/admin",
                gradient: "from-secondary to-primary",
              },
            ].map((item, i) => (
              <div
                key={i}
                className="group relative cursor-pointer"
                onClick={() => router.push(item.role)}
                style={{
                  animation: `fadeInUp 0.6s ease-out ${200 + i * 100}ms backwards`,
                }}
              >
                <div className="absolute inset-0 gradient-primary opacity-0 group-hover:opacity-20 blur-2xl rounded-2xl transition-all duration-300"></div>
                <Card className="relative p-8 border-2 border-border/50 hover:border-primary hover:shadow-2xl transition-all duration-300 overflow-hidden h-full flex flex-col group-hover:bg-card/80">
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-all duration-300 bg-gradient-to-br from-primary/5 to-accent/5"></div>

                  <div className="relative z-10 flex-1 flex flex-col">
                    {/* Icon */}
                    <div
                      className={`w-16 h-16 rounded-xl bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform`}
                    >
                      <item.icon className="w-8 h-8 text-primary-foreground" />
                    </div>

                    {/* Title and Description */}
                    <h3 className="text-2xl font-bold text-foreground mb-3">{item.title}</h3>
                    <p className="text-sm text-muted-foreground mb-8 leading-relaxed flex-1">{item.desc}</p>

                    {/* Features List */}
                    <div className="space-y-3 mb-8">
                      {item.features.map((feature, j) => (
                        <div key={j} className="flex items-center gap-3">
                          <div className="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-accent"></div>
                          <span className="text-sm text-muted-foreground font-medium">{feature}</span>
                        </div>
                      ))}
                    </div>

                    {/* CTA Button */}
                    <Button className="w-full gradient-primary text-primary-foreground border-0 group-hover:shadow-lg transition-all font-semibold">
                      Get Started <ChevronRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 border-t border-border/30 bg-gradient-to-b from-card/30 to-background">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 text-balance">
              World-Class Legal Features
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to navigate criminal law with unparalleled confidence and ease
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Brain,
                title: "24/7 AI Chatbot",
                desc: "Instant legal guidance on FIRs, bail procedures, constitutional rights, appeals, and complex court procedures",
                highlights: ["Instant responses", "Personalized guidance", "Multi-language support", "Context-aware"],
              },
              {
                icon: FileText,
                title: "Smart Document Generation",
                desc: "AI-powered auto-generation of bail petitions, appeals, evidence submissions, and legal applications",
                highlights: ["100+ templates", "Auto-fill forms", "PDF export", "Digital signature"],
              },
              {
                icon: BarChart3,
                title: "Advanced Case Analytics",
                desc: "Real-time case tracking with detailed timelines, hearing schedules, and outcome predictions",
                highlights: ["Live updates", "Timeline tracking", "Hearing alerts", "Status reports"],
              },
              {
                icon: TrendingUp,
                title: "AI-Powered Predictions",
                desc: "Win probability and case outcome predictions based on similar cases and legal precedents",
                highlights: ["ML predictions", "Success rates", "Risk analysis", "Recommendations"],
              },
              {
                icon: Users,
                title: "Elite Lawyer Network",
                desc: "Access 456+ verified lawyers filtered by expertise, location, success rates, and specialization",
                highlights: ["Expert filters", "5-star ratings", "Direct chat", "Video consultation"],
              },
              {
                icon: Lock,
                title: "Enterprise Security",
                desc: "Military-grade encryption, GDPR compliance, and multi-layer security for absolute data protection",
                highlights: ["AES-256", "GDPR certified", "2FA security", "Audit trails"],
              },
            ].map((feature, i) => (
              <div
                key={i}
                className="group p-8 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300 cursor-pointer hover:shadow-xl hover:translate-y-[-4px] hover:bg-card/90"
                style={{
                  animation: `fadeInUp 0.6s ease-out ${i * 100}ms backwards`,
                }}
              >
                <div className="w-14 h-14 rounded-lg gradient-primary flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg">
                  <feature.icon className="w-7 h-7 text-primary-foreground" />
                </div>

                <h3 className="font-bold text-foreground mb-3 text-lg">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed mb-6">{feature.desc}</p>

                <div className="space-y-2">
                  {feature.highlights.map((highlight, j) => (
                    <div key={j} className="flex items-center text-xs text-muted-foreground">
                      <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-primary to-accent mr-3"></div>
                      {highlight}
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex items-center text-primary text-sm font-semibold group-hover:translate-x-2 transition-transform">
                  Explore more <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 border-t border-border/30">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6">How Lawmate Works</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Simple, secure, and extraordinarily powerful
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Steps */}
            <div className="space-y-8">
              {[
                {
                  step: "01",
                  title: "Create Your Account",
                  desc: "Sign up as citizen, lawyer, or admin. Secure verification and role-based access in seconds.",
                  icon: Shield,
                },
                {
                  step: "02",
                  title: "Get Instant Legal Guidance",
                  desc: "Chat with our AI anytime. Get answers on procedures, laws, and legal strategies 24/7.",
                  icon: Brain,
                },
                {
                  step: "03",
                  title: "Generate Legal Documents",
                  desc: "Create professional legal documents with AI assistance. Download and share instantly.",
                  icon: FileText,
                },
                {
                  step: "04",
                  title: "Track & Optimize",
                  desc: "Monitor cases in real-time with AI insights, predictions, and actionable recommendations.",
                  icon: Activity,
                },
              ].map((item, i) => (
                <div key={i} className="group flex gap-6 animate-fadeInUp" style={{ animationDelay: `${i * 100}ms` }}>
                  <div className="flex-shrink-0 w-16 h-16 rounded-full gradient-primary flex items-center justify-center text-primary-foreground font-bold shadow-lg group-hover:scale-110 transition-transform text-lg">
                    {item.step}
                  </div>
                  <div className="pt-2">
                    <h3 className="font-bold text-foreground mb-2 text-lg group-hover:text-primary transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Visual */}
            <div className="relative h-96 bg-gradient-to-br from-primary/15 to-accent/15 rounded-2xl border border-border/50 flex items-center justify-center overflow-hidden group hover:shadow-2xl transition-all">
              <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-br from-primary/8 to-accent/8"></div>

              <div className="relative z-10 text-center p-8">
                <div className="w-36 h-36 rounded-full gradient-primary flex items-center justify-center mx-auto mb-6 animate-pulse-glow shadow-2xl">
                  <Brain className="w-20 h-20 text-primary-foreground" />
                </div>
                <h3 className="text-2xl font-bold text-foreground mb-3">AI-Powered Platform</h3>
                <p className="text-muted-foreground">Intelligent guidance at every step of your legal journey</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section id="impact" className="py-24 border-t border-border/30 bg-gradient-to-b from-background to-card/20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                number: "2,340+",
                label: "Active Users",
                icon: Users,
                desc: "Across India",
                color: "from-primary to-accent",
              },
              {
                number: "456+",
                label: "Verified Lawyers",
                icon: Shield,
                desc: "Expert specialists",
                color: "from-accent to-secondary",
              },
              {
                number: "12,450+",
                label: "Cases Managed",
                icon: FileText,
                desc: "Successfully tracked",
                color: "from-secondary to-primary",
              },
              {
                number: "99.9%",
                label: "Uptime",
                icon: TrendingUp,
                desc: "Enterprise reliability",
                color: "from-primary to-accent",
              },
            ].map((stat, i) => (
              <div
                key={i}
                className="text-center p-8 rounded-xl bg-card border border-border hover:border-primary/50 transition-all group cursor-pointer hover:shadow-xl hover:translate-y-[-4px] hover:bg-card/90"
                style={{
                  animation: `fadeInUp 0.6s ease-out ${i * 100}ms backwards`,
                }}
              >
                <div
                  className={`w-14 h-14 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg`}
                >
                  <stat.icon className="w-7 h-7 text-primary-foreground" />
                </div>
                <div className="text-4xl lg:text-5xl font-bold text-primary mb-2 group-hover:text-accent transition-colors">
                  {stat.number}
                </div>
                <div className="text-foreground font-semibold mb-1">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-24 border-t border-border/30">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-foreground mb-4">Frequently Asked Questions</h2>
            <p className="text-muted-foreground text-lg">Everything you need to know</p>
          </div>

          <div className="space-y-4">
            {[
              {
                q: "Is Lawmate a substitute for a lawyer?",
                a: "No. Lawmate provides legal information and AI-powered guidance, but cannot replace professional legal advice. Always consult a qualified lawyer for specific cases.",
              },
              {
                q: "How secure is my personal data?",
                a: "We use military-grade AES-256 encryption and comply with GDPR standards. Your documents and personal information are completely confidential and secure.",
              },
              {
                q: "What is the cost of using Lawmate?",
                a: "Basic features are free. Premium plans start at affordable rates with optional lawyer consultations billed separately.",
              },
              {
                q: "Can I connect with a lawyer directly?",
                a: "Yes. Our directory has 456+ verified lawyers. You can search, view their profiles, and connect directly through our secure platform.",
              },
              {
                q: "Is the AI guidance accurate?",
                a: "Our AI is trained on 50,000+ legal cases and uses current legal precedents. However, always verify with a lawyer for critical decisions.",
              },
              {
                q: "How do I download my case documents?",
                a: "Simply generate documents using our AI templates, review them, and download as PDF. You can share them directly with your lawyer.",
              },
            ].map((faq, i) => (
              <details
                key={i}
                className="group rounded-lg border border-border hover:border-primary/50 transition-all cursor-pointer bg-card hover:bg-card/80"
                style={{
                  animation: `fadeInUp 0.6s ease-out ${i * 50}ms backwards`,
                }}
              >
                <summary className="p-6 font-semibold text-foreground flex items-center justify-between hover:text-primary transition-colors">
                  {faq.q}
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-open:rotate-90 transition-transform" />
                </summary>
                <div className="px-6 pb-6 text-muted-foreground border-t border-border/50">{faq.a}</div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Reviews */}
      <section id="reviews" className="py-14 bg-card/20 border-t border-border/30">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="text-center space-y-2">
            <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">Trusted outcomes</p>
            <h3 className="text-3xl sm:text-4xl font-bold text-foreground">What people say about Lawmate</h3>
          </div>
          <AnimatedTestimonials
            autoplay
            testimonials={[
              {
                quote: "We filed bail faster because the steps were clear and a Lawmate lawyer reviewed our draft in minutes.",
                name: "Ahmed Khan",
                designation: "Defendant’s family, Lahore",
                src: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=1200&auto=format&fit=crop",
              },
              {
                quote: "AI summaries plus my edits cut my drafting time in half while keeping citations tight for the court.",
                name: "Adv. Ayesha Siddiqui",
                designation: "Criminal lawyer, Karachi",
                src: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=1200&auto=format&fit=crop",
              },
              {
                quote: "Court dates, evidence tasks, and reminders in one view meant we never missed a deadline.",
                name: "Fatima Malik",
                designation: "Victim support lead, Islamabad",
                src: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?q=80&w=1200&auto=format&fit=crop",
              },
              {
                quote: "The evidence checklists and petition packs made our filings cleaner and faster to approve.",
                name: "Bilal Hussain",
                designation: "Legal aid coordinator, Peshawar",
                src: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=1200&auto=format&fit=crop",
              },
            ]}
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 border-t border-border/30">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="relative rounded-2xl bg-gradient-to-br from-primary/20 via-accent/15 to-secondary/10 border border-border/50 p-12 sm:p-16 overflow-hidden group hover:border-primary/50 transition-all">
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-br from-primary/10 to-accent/10"></div>
            <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

            <div className="relative z-10 text-center">
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 text-balance">
                Ready to Transform Your Legal Journey?
              </h2>
              <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
                Join thousands of citizens and lawyers who are already using Lawmate to navigate the complexities of
                criminal law with confidence.
              </p>

              <div className="flex gap-4 justify-center flex-col sm:flex-row">
                <Button
                  size="lg"
                  className="gradient-primary text-primary-foreground border-0 shadow-lg hover:shadow-xl hover:scale-105 transition-all"
                  onClick={() => router.push("/citizen")}
                >
                  Get Started Free <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="hover:bg-primary/10 bg-transparent border-primary/50"
                  onClick={() => router.push("/login")}
                >
                  Schedule Demo
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/30 bg-card/30 backdrop-blur-sm py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-10 h-10 rounded-lg gradient-primary flex items-center justify-center">
                  <Scales className="w-6 h-6 text-primary-foreground" />
                </div>
                <span className="font-bold text-foreground">Lawmate</span>
              </div>
              <p className="text-sm text-muted-foreground">Making legal justice accessible to everyone.</p>
            </div>

            <div>
              <h4 className="font-semibold text-foreground mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {["Features", "Pricing", "Security", "Roadmap"].map((link) => (
                  <li key={link}>
                    <a href="#" className="hover:text-primary transition-colors">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-foreground mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {["About", "Blog", "Careers", "Contact"].map((link) => (
                  <li key={link}>
                    <a href="#" className="hover:text-primary transition-colors">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-foreground mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {["Privacy", "Terms", "Compliance", "Disclaimer"].map((link) => (
                  <li key={link}>
                    <a href="#" className="hover:text-primary transition-colors">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="border-t border-border/50 pt-8 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">© 2025 Lawmate. All rights reserved.</p>
            <div className="flex gap-4">
              {["Twitter", "LinkedIn", "Facebook"].map((social) => (
                <a
                  key={social}
                  href="#"
                  className="w-10 h-10 rounded-lg bg-card border border-border hover:border-primary hover:bg-primary/10 transition-all flex items-center justify-center text-muted-foreground hover:text-primary"
                >
                  <Globe className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
