"use client"

import { useRouter } from "next/navigation"
import { useEffect, useRef, useState } from "react"
import Script from "next/script"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { AnimatedTestimonials } from "@/components/ui/animated-testimonials"
import { DotLottieReact } from "@lottiefiles/dotlottie-react"
import { motion } from "framer-motion"
import { useScroll, useTransform } from "framer-motion"

// Declare custom element for TypeScript
declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'dotlottie-wc': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
        src?: string
        autoplay?: boolean
        loop?: boolean
        style?: React.CSSProperties
      }
    }
  }
}
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
  Sparkles,
  MessageSquareQuote,
  Building2,
  PlayCircle,
} from "lucide-react"

function PremiumVideo({
  sources,
  className,
}: {
  sources: string[]
  className?: string
}) {
  const [sourceIndex, setSourceIndex] = useState(0)
  const currentSource = sources[Math.min(sourceIndex, sources.length - 1)]

  return (
    <video
      key={currentSource}
      className={className}
      autoPlay
      muted
      loop
      playsInline
      onError={() => {
        if (sourceIndex < sources.length - 1) setSourceIndex((prev) => prev + 1)
      }}
      src={currentSource}
    />
  )
}

function SectionVideoBg({ sources, opacity = "opacity-20" }: { sources: string[]; opacity?: string }) {
  return (
    <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
      <PremiumVideo sources={sources} className={`w-full h-full object-cover ${opacity}`} />
      <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/65 to-background/90" />
    </div>
  )
}

export default function Home() {
  const router = useRouter()
  const [isLoaded, setIsLoaded] = useState(false)
  const marqueeItems = [
    "Intelligent AI Legal Consultation for All Stakeholders",
    "Instant Access to Pakistani Statutes & Case Law",
    "Premium Verified Lawyer Marketplace with Smart Matching",
    "AI-Powered Document Analysis & Legal Summaries",
    "Comprehensive Case Timeline & Hearing Management",
    "Enterprise-Grade Secure Document Vault",
    "Streamlined Advocate Onboarding & Matter Distribution",
    "Automated Billing & Financial Management",
    "Advanced Analytics for Law Firm Performance",
    "End-to-End Encrypted Legal Communications",
    "Hybrid AI-Lawyer Collaborative Review Workflow",
    "Complete Client & Matter Lifecycle Management",
    "Compliance-Ready Legal Operations Platform",
  ]
  const firstSetRef = useRef<HTMLDivElement>(null)
  const [marqueeWidth, setMarqueeWidth] = useState(0)

  const steps = [
    { number: "01", title: "Intelligent Legal Intake", desc: "Describe your legal matter and receive instant AI-powered guidance tailored to your specific needs and jurisdiction." },
    { number: "02", title: "Research & Expert Discovery", desc: "Access comprehensive statutory references, case law precedents, and connect with specialized verified lawyers perfectly matched to your case." },
    { number: "03", title: "Unified Collaboration Hub", desc: "Seamlessly manage all documents, communications, legal drafts, and case developments within a single secure collaborative workspace." },
    { number: "04", title: "Real-Time Case Intelligence", desc: "Monitor comprehensive timelines, hearing schedules, billing transparency, and performance metrics through an integrated analytics dashboard." },
  ]
  const [currentStep, setCurrentStep] = useState(0)
  const [isMobile, setIsMobile] = useState(false)
  const dotRefs = useRef<(HTMLDivElement | null)[]>([])
  const [dotX, setDotX] = useState<number[]>([])
  const heroRef = useRef<HTMLElement | null>(null)
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  })
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 120])
  const heroOpacity = useTransform(scrollYProgress, [0, 0.7], [1, 0.35])

  useEffect(() => {
    setIsLoaded(true)
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

  const platformPillars = [
    "Streamlined Advocate Onboarding & Intelligent Matter Distribution",
    "Comprehensive Client & Matter Lifecycle Orchestration",
    "Advanced Case Timeline with Automated Hearing Notifications",
    "Bank-Grade Secure Document Vault with Granular Permissions",
    "Automated Billing, Invoicing & Financial Reporting",
    "Military-Grade Encrypted Legal Communication Channels",
  ]

  const journeyRows = [
    {
      title: "AI-Powered Legal Research Intelligence",
      subtitle: "Instant Access to Statutes & Precedents",
      description:
        "Transform hours of research into minutes. Our advanced AI instantly maps legal queries to relevant statutory provisions and case law precedents with contextual analysis and jurisdiction-specific insights.",
      metric: "400% Research Efficiency",
      align: "left" as const,
    },
    {
      title: "End-to-End Case Workflow Automation",
      subtitle: "From Initial Intake to Final Resolution",
      description:
        "Eliminate administrative bottlenecks with intelligent automation. Track hearings, manage deadlines, coordinate filings, and maintain real-time client communication through a unified workflow management system.",
      metric: "62% Admin Time Saved",
      align: "right" as const,
    },
    {
      title: "Premium Lawyer Marketplace & Collaboration",
      subtitle: "Smart Matching & Secure Collaboration",
      description:
        "Connect clients with the perfect legal expertise through intelligent matching algorithms. Facilitate seamless coordination between clients, lawyers, and legal teams with enterprise-grade collaboration tools and secure communication channels.",
      metric: "270% Faster Connections",
      align: "left" as const,
    },
  ]

  const fallbackLegalVideos = [
    "https://player.vimeo.com/external/434045526.sd.mp4?s=4f04c1df9b6f9c9cb4f8716f640f2cdb6400ed1c&profile_id=139&oauth2_token_id=57447761",
    "https://player.vimeo.com/external/517625176.sd.mp4?s=7f21ed6f53f8cb0e8741ce7f2e6ec66216c0daac&profile_id=139&oauth2_token_id=57447761",
    "https://player.vimeo.com/external/371433846.sd.mp4?s=236f38ddaf53a3216fbbf6ce430e0f53ea50ccaa&profile_id=139&oauth2_token_id=57447761",
  ]

  const sectionVideos = {
    marquee: [
      "/videos/pexels-5637927.mp4",
      fallbackLegalVideos[0],
    ],
    process: [
      "/videos/pexels-5637303.mp4",
      fallbackLegalVideos[1],
    ],
    features: [
      "/videos/pexels-5646341.mp4",
      fallbackLegalVideos[2],
    ],
    journey: [
      "/videos/pexels-5637927.mp4",
      fallbackLegalVideos[0],
    ],
    showcase: [
      "/videos/pexels-5637303.mp4",
      fallbackLegalVideos[1],
    ],
    how: [
      "/videos/pexels-5646341.mp4",
      fallbackLegalVideos[2],
    ],
    stats: [
      "/videos/pexels-5637927.mp4",
      fallbackLegalVideos[0],
    ],
    platform: [
      "/videos/pexels-5637303.mp4",
      fallbackLegalVideos[1],
    ],
    community: [
      "/videos/pexels-5646341.mp4",
      fallbackLegalVideos[2],
    ],
    faq: [
      "/videos/pexels-5637927.mp4",
      fallbackLegalVideos[0],
    ],
    reviews: [
      "/videos/pexels-5637303.mp4",
      fallbackLegalVideos[1],
    ],
    cta: [
      "/videos/pexels-5646341.mp4",
      fallbackLegalVideos[2],
    ],
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-card/10 overflow-hidden">
      {/* Load dotlottie web component */}
      <Script
        src="https://unpkg.com/@lottiefiles/dotlottie-wc@0.9.10/dist/dotlottie-wc.js"
        type="module"
        strategy="lazyOnload"
      />

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
        <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-10 py-5">
          <div className="flex items-center justify-between gap-4">
            <div
              className="flex items-center gap-3 group cursor-pointer hover:scale-105 transition-transform flex-shrink-0"
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

            <nav className="hidden lg:flex items-center absolute left-1/2 transform -translate-x-1/2">
              <div className="flex items-center gap-10">
                {[
                  { label: "Features", id: "features" },
                  { label: "Process", id: "process" },
                  { label: "Impact", id: "impact" },
                  { label: "FAQ", id: "faq" },
                ].map((item) => (
                  <a
                    key={item.id}
                    href={`#${item.id}`}
                    className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors duration-300 relative group whitespace-nowrap px-1"
                  >
                    {item.label}
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-primary to-accent group-hover:w-full transition-all duration-300"></span>
                  </a>
                ))}
              </div>
            </nav>

            <div className="flex gap-3 flex-shrink-0">
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
        </div>
      </header>

      {/* Hero Section - Premium Redesign */}
      <section ref={heroRef} className="relative pt-24 pb-20 sm:pt-40 sm:pb-32 overflow-hidden min-h-[90vh] flex items-center">
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 premium-hero-gradient" />
          <div className="absolute inset-0 bg-grid-pattern opacity-[0.06]" />
          <motion.div
            className="absolute top-10 left-0 w-[480px] h-[480px] rounded-full bg-primary/25 blur-3xl"
            animate={{ x: [0, 90, 0], y: [0, 30, 0] }}
            transition={{ duration: 14, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute top-1/4 right-0 w-[560px] h-[560px] rounded-full bg-accent/25 blur-3xl"
            animate={{ x: [0, -80, 0], y: [0, -35, 0] }}
            transition={{ duration: 16, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
        </div>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full">
          <motion.div
            className={`transition-all duration-1000 ${
              isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
            }`}
            style={{ y: heroY, opacity: heroOpacity }}
          >
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
              <div className="lg:col-span-6 text-center lg:text-left space-y-6 sm:space-y-8">
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  className="inline-flex px-5 py-2.5 rounded-full bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/40 text-sm font-semibold text-primary animate-pulse-glow"
                >
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Enterprise Legal Technology Platform
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </motion.div>

                <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-foreground text-balance leading-[1.1] tracking-tight">
                  Pakistan's Premier
                  <span className="block relative mt-3">
                    <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-primary animate-shimmer opacity-70" />
                    <span className="relative bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                      AI-Powered Legal Platform
                    </span>
                  </span>
                </h1>

                <p className="text-base sm:text-lg lg:text-xl text-muted-foreground max-w-2xl mx-auto lg:mx-0 leading-relaxed">
                  Transform legal operations with intelligent AI consultation, verified legal professionals, and comprehensive case management—all unified in Pakistan's most advanced legal technology ecosystem.
                </p>

                <div className="flex gap-4 justify-center lg:justify-start flex-col sm:flex-row items-center flex-wrap">
                  <Button
                    size="lg"
                    className="gradient-primary text-primary-foreground border-0 shadow-xl hover:shadow-2xl hover:scale-105 transition-all px-8"
                    onClick={() => router.push("/citizen")}
                  >
                    <Zap className="w-5 h-5 mr-2" />
                    Get Started Free
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className="hover:bg-primary/10 bg-transparent border-primary/50 px-8"
                    onClick={() => router.push("/login")}
                  >
                    Schedule Demo
                    <PlayCircle className="w-4 h-4 ml-2" />
                  </Button>
                </div>

                <div className="flex lg:justify-start justify-center items-center gap-4 flex-wrap text-sm">
                  <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-border/60 bg-card/60 backdrop-blur-sm">
                    <Award className="w-4 h-4 text-primary" />
                    <span className="font-medium">15,000+ Active Users</span>
                  </span>
                  <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-border/60 bg-card/60 backdrop-blur-sm">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    <span className="font-medium">750+ Verified Advocates</span>
                  </span>
                  <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-border/60 bg-card/60 backdrop-blur-sm">
                    <TrendingUp className="w-4 h-4 text-primary" />
                    <span className="font-medium">99.9% Platform Reliability</span>
                  </span>
                </div>
              </div>

              <div className="lg:col-span-6">
                <motion.div
                  initial={{ opacity: 0, x: 24 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.7 }}
                  className="relative rounded-3xl overflow-hidden border border-border/60 shadow-2xl bg-card/40 backdrop-blur-md"
                >
                  <div className="w-full h-[460px] bg-gradient-to-br from-primary/20 via-background to-accent/20 flex items-center justify-center">
                    <div className="w-full h-full max-w-[540px]">
                      <DotLottieReact
                        src="https://lottie.host/ade2b84a-d791-4720-8a6b-dd50a52f4994/BHPMjEOqdV.lottie"
                        loop
                        autoplay
                      />
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>

        </div>
      </section>

        {/* Moving Value Marquee */}
        <section className="py-16 relative overflow-hidden border-t border-border/30" id="features">
          <SectionVideoBg sources={sectionVideos.marquee} opacity="opacity-15" />
          <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-6 text-center">
            <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">Comprehensive Platform Capabilities</p>
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
        <section id="process" className="py-14 border-t border-b border-border/30 bg-gradient-to-b from-card/10 via-background to-card/10 relative overflow-hidden">
          <SectionVideoBg sources={sectionVideos.process} opacity="opacity-10" />
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-10">
            <div className="text-center space-y-2">
              <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">How you move forward</p>
              <h3 className="text-3xl sm:text-4xl font-bold text-foreground">A clear path from question to resolution</h3>
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
                              <motion.span
                                className="text-primary font-semibold"
                                animate={isActive ? { scale: [1, 1.15, 1] } : { scale: 1 }}
                                transition={{ duration: 1.1, repeat: isActive ? Number.POSITIVE_INFINITY : 0 }}
                              >
                                {step.number}
                              </motion.span>
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
                                  animate={isActive ? { scale: [1, 1.4, 1], opacity: [0.8, 1, 0.8] } : { scale: 1 }}
                                  transition={{ duration: 1, repeat: isActive ? Number.POSITIVE_INFINITY : 0 }}
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
      <section className="py-24 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div
            className={`grid grid-cols-1 md:grid-cols-3 gap-6 transition-all duration-1000 ${
              isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
            }`}
            style={{ transitionDelay: "200ms" }}
          >
            {[
              {
                icon: Shield,
                title: "For Consumers",
                desc: "Get instant legal understanding, discover trusted lawyers, and follow your case journey with clarity and confidence.",
                features: ["AI Legal Chat", "Case History Tracking", "Lawyer Discovery", "Document Summaries"],
                role: "/citizen",
                gradient: "from-primary to-accent",
                image:
                  "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=1600&auto=format&fit=crop",
              },
              {
                icon: BarChart3,
                title: "For Advocates",
                desc: "Manage clients, research faster, draft smarter, and collaborate through a modern legal workspace built for growth.",
                features: ["Research Assistant", "Case Workspace", "Client Collaboration", "Practice Analytics"],
                role: "/lawyer",
                gradient: "from-accent to-secondary",
                image:
                  "https://images.unsplash.com/photo-1436450412740-6b988f486c6b?q=80&w=1600&auto=format&fit=crop",
              },
              {
                icon: Users,
                title: "For Legal Operations",
                desc: "Run firm-level workflows, compliance, billing, and reporting from a secure operational control layer.",
                features: ["Team Operations", "Compliance Controls", "Billing Insights", "Security Oversight"],
                role: "/admin",
                gradient: "from-secondary to-primary",
                image:
                  "https://images.unsplash.com/photo-1462899006636-339e08d1844e?q=80&w=1600&auto=format&fit=crop",
              },
            ].map((item, i) => (
              <motion.div
                key={i}
                className="group relative cursor-pointer"
                onClick={() => router.push(item.role)}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.2 + i * 0.1 }}
                whileHover={{ y: -8 }}
              >
                <div className="absolute inset-0 gradient-primary opacity-0 group-hover:opacity-20 blur-2xl rounded-2xl transition-all duration-300"></div>
                <Card className="relative p-8 border-2 border-border/50 hover:border-primary hover:shadow-2xl transition-all duration-300 overflow-hidden h-full flex flex-col group-hover:bg-card/80">
                  <img
                    src={item.image}
                    alt={item.title}
                    className="absolute inset-0 w-full h-full object-cover opacity-[0.16] group-hover:opacity-[0.24] transition-opacity duration-500"
                  />
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
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 border-t border-border/30 bg-gradient-to-b from-card/30 to-background relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.features} opacity="opacity-12" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 text-balance">
              Comprehensive Legal Technology Suite
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Enterprise-grade features empowering citizens, advocates, and law firms to operate with unprecedented efficiency and intelligence
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Brain,
                title: "Intelligent AI Legal Consultation",
                desc: "Receive instant, context-aware legal guidance powered by advanced AI trained on Pakistani law. Navigate complex legal matters with confidence through intelligent question processing and strategic recommendations.",
                highlights: ["Instant Analysis", "Jurisdiction-Specific", "Multi-Lingual Interface", "24/7 Availability"],
                image:
                  "https://images.unsplash.com/photo-1453945619913-79ec89a82c51?q=80&w=1600&auto=format&fit=crop",
              },
              {
                icon: FileText,
                title: "AI-Enhanced Document Management",
                desc: "Transform document workflows with intelligent summarization, automated drafting, and AI-lawyer collaborative review. Generate professional legal documents with unprecedented speed and accuracy.",
                highlights: ["Smart Summaries", "Automated Drafting", "Template Library", "Secure Sharing"],
                image:
                  "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=1600&auto=format&fit=crop",
              },
              {
                icon: BarChart3,
                title: "Advanced Case Timeline Analytics",
                desc: "Maintain complete visibility over case progression with intelligent timeline management, automated hearing notifications, and real-time status updates. Never miss critical deadlines or court appearances.",
                highlights: ["Real-Time Updates", "Smart Reminders", "Progress Tracking", "Milestone Alerts"],
                image:
                  "https://images.unsplash.com/photo-1589578228447-e1a4e481c6c8?q=80&w=1600&auto=format&fit=crop",
              },
              {
                icon: TrendingUp,
                title: "Enterprise Analytics Dashboard",
                desc: "Drive data-informed decisions with comprehensive performance metrics, workload optimization insights, revenue analytics, and firm-wide efficiency tracking. Transform operations through actionable intelligence.",
                highlights: ["Performance Metrics", "Revenue Analytics", "Workflow Optimization", "Strategic Insights"],
                image:
                  "https://images.unsplash.com/photo-1531973576160-7125cd663d86?q=80&w=1600&auto=format&fit=crop",
              },
              {
                icon: Users,
                title: "Premium Verified Lawyer Network",
                desc: "Access Pakistan's most comprehensive network of verified legal professionals. Connect with specialized advocates through intelligent matching algorithms based on expertise, location, and case requirements.",
                highlights: ["Verified Credentials", "AI Matching", "Instant Connection", "Transparent Profiles"],
                image:
                  "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1600&auto=format&fit=crop",
              },
              {
                icon: Lock,
                title: "Military-Grade Security Infrastructure",
                desc: "Safeguard sensitive legal information with bank-level encryption, granular role-based access controls, and fully auditable secure communication channels. Enterprise security for legal excellence.",
                highlights: ["End-to-End Encryption", "Access Controls", "Secure Communications", "Audit Trails"],
                image:
                  "https://images.unsplash.com/photo-1563013544-824ae1b704d3?q=80&w=1600&auto=format&fit=crop",
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                className="group relative overflow-hidden p-8 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300 cursor-pointer hover:shadow-xl hover:translate-y-[-4px] hover:bg-card/90"
                initial={{ opacity: 0, y: 20, scale: 0.98 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.45, delay: i * 0.07 }}
                whileHover={{ y: -6, scale: 1.02 }}
              >
                <img
                  src={feature.image}
                  alt={feature.title}
                  className="absolute inset-0 w-full h-full object-cover opacity-[0.13] group-hover:opacity-[0.22] transition-opacity duration-500 pointer-events-none"
                />
                <div className="absolute inset-0 bg-gradient-to-b from-background/40 via-background/65 to-background/85 pointer-events-none" />
                <div className="relative z-10">
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
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Motion Journey Rows - Premium Design */}
      <section className="py-32 border-t border-border/30 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-primary/5 to-background" />
        <SectionVideoBg sources={sectionVideos.journey} opacity="opacity-5" />

        {/* Floating gradient orbs */}
        <div className="absolute top-20 left-10 w-96 h-96 bg-primary/20 rounded-full blur-3xl opacity-30 animate-float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-3xl opacity-30 animate-float" style={{ animationDelay: '2s' }} />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-20">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6"
            >
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-xs uppercase tracking-[0.28em] text-primary font-semibold">Experience Layer</span>
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-4 bg-gradient-to-r from-foreground via-foreground to-foreground/80 bg-clip-text"
            >
              Advanced Legal Technology in Action
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-lg text-muted-foreground max-w-3xl mx-auto"
            >
              Experience unprecedented efficiency through intelligent automation, AI-powered research, and seamless collaboration across the complete legal ecosystem
            </motion.p>
          </div>

          <div className="space-y-20">
            {journeyRows.map((row, idx) => (
              <motion.div
                key={row.title}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.7, delay: idx * 0.1 }}
                className={`grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center ${
                  row.align === "right" ? "lg:text-right" : ""
                }`}
              >
                <div className={`lg:col-span-5 ${row.align === "right" ? "lg:order-2" : ""}`}>
                  <motion.div
                    initial={{ opacity: 0, x: row.align === "right" ? 20 : -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                  >
                    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 mb-4 ${row.align === "right" ? "lg:ml-auto" : ""}`}>
                      <span className="text-xs font-bold text-primary uppercase tracking-wider">{row.subtitle}</span>
                    </div>
                    <h3 className="text-3xl sm:text-4xl font-bold text-foreground mb-4 leading-tight">
                      {row.title}
                    </h3>
                    <p className="text-base text-muted-foreground leading-relaxed mb-6">
                      {row.description}
                    </p>
                  </motion.div>
                </div>

                <div className={`lg:col-span-7 ${row.align === "right" ? "lg:order-1" : ""}`}>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="relative group"
                  >
                    <div className="relative p-8 sm:p-10 rounded-3xl border border-border/60 bg-card/60 backdrop-blur-xl overflow-hidden shadow-2xl hover:shadow-3xl transition-all duration-500">
                      {/* Animated background gradient */}
                      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                      {/* Progress bar container */}
                      <div className="relative">
                        <div className="flex items-center justify-between mb-4">
                          <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Impact Metrics</span>
                          <motion.div
                            initial={{ scale: 0 }}
                            whileInView={{ scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
                            className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center shadow-lg"
                          >
                            <TrendingUp className="w-5 h-5 text-primary-foreground" />
                          </motion.div>
                        </div>

                        {/* Enhanced progress bar */}
                        <div className="relative h-20 rounded-2xl border border-border/40 bg-background/80 backdrop-blur-sm overflow-hidden shadow-inner">
                          {/* Animated gradient fill */}
                          <motion.div
                            className="absolute inset-y-0 left-0 rounded-2xl bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_100%] animate-gradient-x shadow-lg"
                            initial={{ width: 0 }}
                            whileInView={{ width: `${68 + idx * 10}%` }}
                            viewport={{ once: true }}
                            transition={{ duration: 1.5, ease: "easeOut", delay: 0.4 }}
                          />

                          {/* Shimmer effect */}
                          <motion.div
                            className="absolute inset-y-0 left-0 rounded-2xl bg-gradient-to-r from-transparent via-white/25 to-transparent"
                            initial={{ x: "-100%", width: "30%" }}
                            animate={{ x: "120%" }}
                            transition={{ duration: 3, repeat: Number.POSITIVE_INFINITY, ease: "linear", delay: idx * 0.3 }}
                          />

                          {/* Content */}
                          <div className="absolute inset-0 flex items-center justify-between px-6">
                            <span className="text-sm font-medium text-foreground/80 z-10">Platform Performance</span>
                            <motion.span
                              initial={{ scale: 0, opacity: 0 }}
                              whileInView={{ scale: 1, opacity: 1 }}
                              viewport={{ once: true }}
                              transition={{ delay: 0.8, type: "spring", stiffness: 200 }}
                              className="text-xl sm:text-2xl font-bold text-foreground z-10 px-4 py-1 rounded-full bg-background/80 backdrop-blur-sm border border-border/60 shadow-lg"
                            >
                              {row.metric}
                            </motion.span>
                          </div>
                        </div>

                        {/* Stats indicators */}
                        <div className="grid grid-cols-3 gap-4 mt-6">
                          {['Efficiency', 'Speed', 'Accuracy'].map((label, i) => (
                            <motion.div
                              key={label}
                              initial={{ opacity: 0, y: 10 }}
                              whileInView={{ opacity: 1, y: 0 }}
                              viewport={{ once: true }}
                              transition={{ delay: 0.6 + i * 0.1 }}
                              className="text-center"
                            >
                              <div className="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-accent mx-auto mb-2" />
                              <span className="text-xs text-muted-foreground font-medium">{label}</span>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 border-t border-border/30 relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.how} opacity="opacity-10" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6">Seamless Legal Operations</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Empowering citizens, legal professionals, and law firms with intelligent, streamlined workflows
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Steps */}
            <div className="space-y-8">
              {[
                {
                  step: "01",
                  title: "Select Your Profile",
                  desc: "Begin with secure, role-based onboarding as a citizen seeking legal guidance, a licensed advocate, or a law firm administrator managing legal operations.",
                  icon: Shield,
                },
                {
                  step: "02",
                  title: "AI-Powered Legal Research",
                  desc: "Leverage advanced AI consultation combined with comprehensive access to Pakistani statutes and case law to understand your legal position and explore strategic options.",
                  icon: Brain,
                },
                {
                  step: "03",
                  title: "Expert Collaboration",
                  desc: "Connect with specialized verified lawyers, facilitate secure document exchange, and coordinate all case activities within a unified, professional workspace.",
                  icon: FileText,
                },
                {
                  step: "04",
                  title: "Intelligence & Growth",
                  desc: "Monitor comprehensive case timelines, manage all communications, automate billing processes, and gain actionable insights through advanced analytics dashboards.",
                  icon: Activity,
                },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  className="group flex gap-6 animate-fadeInUp"
                  style={{ animationDelay: `${i * 100}ms` }}
                  initial={{ opacity: 0, x: -14 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.45, delay: i * 0.08 }}
                >
                  <div className="flex-shrink-0 w-16 h-16 rounded-full gradient-primary flex items-center justify-center text-primary-foreground font-bold shadow-lg group-hover:scale-110 transition-transform text-lg">
                    <motion.span
                      animate={{ scale: [1, 1.12, 1], rotate: [0, 4, 0] }}
                      transition={{ duration: 2.2, repeat: Number.POSITIVE_INFINITY, delay: i * 0.2 }}
                    >
                      {item.step}
                    </motion.span>
                  </div>
                  <div className="pt-2">
                    <h3 className="font-bold text-foreground mb-2 text-lg group-hover:text-primary transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Visual */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative h-full min-h-[600px] rounded-2xl border border-border/50 overflow-hidden shadow-2xl hover:shadow-3xl transition-all"
            >
              <div className="relative h-full bg-gradient-to-br from-primary/10 to-accent/10">
                <video
                  className="w-full h-full object-cover"
                  autoPlay
                  muted
                  loop
                  playsInline
                >
                  <source src="/videos/how-it-works.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                <div className="absolute inset-0 bg-gradient-to-t from-background/20 to-transparent pointer-events-none"></div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-background/90 to-transparent">
                <h3 className="text-xl font-bold text-foreground mb-2">AI + Legal Marketplace</h3>
                <p className="text-sm text-muted-foreground">One connected ecosystem for guidance, lawyers, and case workflows</p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section id="impact" className="py-24 border-t border-border/30 bg-gradient-to-b from-background to-card/20 relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.stats} opacity="opacity-10" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                number: "10k+",
                label: "Active Users",
                icon: Users,
                desc: "Across Pakistan",
                color: "from-primary to-accent",
              },
              {
                number: "500+",
                label: "Verified Lawyers",
                icon: Shield,
                desc: "Trusted legal experts",
                color: "from-accent to-secondary",
              },
              {
                number: "20k+",
                label: "Legal Queries Assisted",
                icon: FileText,
                desc: "Across core legal categories",
                color: "from-secondary to-primary",
              },
              {
                number: "99.95%",
                label: "Uptime",
                icon: TrendingUp,
                desc: "Enterprise reliability",
                color: "from-primary to-accent",
              },
            ].map((stat, i) => (
              <motion.div
                key={i}
                className="text-center p-8 rounded-xl bg-card border border-border hover:border-primary/50 transition-all group cursor-pointer hover:shadow-xl hover:translate-y-[-4px] hover:bg-card/90"
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.45, delay: i * 0.08 }}
                whileHover={{ y: -6, scale: 1.02 }}
              >
                <div
                  className={`w-14 h-14 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg`}
                >
                  <stat.icon className="w-7 h-7 text-primary-foreground" />
                </div>
                <div className="text-4xl lg:text-5xl font-bold text-primary mb-2 group-hover:text-accent transition-colors">
                  <motion.span
                    className="inline-block"
                    animate={{ scale: [1, 1.08, 1] }}
                    transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, delay: i * 0.2 }}
                  >
                    {stat.number}
                  </motion.span>
                </div>
                <div className="text-foreground font-semibold mb-1">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.desc}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Management Section */}
      <section className="py-24 border-t border-border/30 bg-gradient-to-b from-card/20 to-background relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.platform} opacity="opacity-10" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground mb-3">Platform Portal</p>
              <h2 className="text-4xl sm:text-5xl font-bold text-foreground mb-5">
                Your legal practice management solution
              </h2>
              <p className="text-muted-foreground text-lg leading-relaxed mb-7">
                Empower companies and advocates with smarter tools for assignments, timelines, documents, billing, and
                collaboration in one secure platform.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {platformPillars.map((pillar, idx) => (
                  <motion.div
                    key={pillar}
                    initial={{ opacity: 0, x: -15 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.45, delay: idx * 0.06 }}
                    className="rounded-lg border border-border/60 bg-card/70 px-4 py-3 text-sm text-foreground/90"
                  >
                    <span className="inline-flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" />
                      {pillar}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative min-h-[420px] rounded-2xl border border-border/60 overflow-hidden bg-gradient-to-br from-primary/10 via-card/60 to-accent/10 backdrop-blur-sm shadow-xl"
            >
              <div className="absolute inset-0 bg-grid-pattern opacity-5" />
              <div className="relative z-10 h-full p-8 flex items-center justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/30 to-accent/30 rounded-full blur-3xl opacity-60"></div>
                  {/* @ts-ignore - dotlottie-wc is a valid web component */}
                  <dotlottie-wc
                    src="https://lottie.host/9105c244-dbf7-4860-934f-e5f24e404665/PqiATITgvl.lottie"
                    style={{ width: '400px', height: '400px' }}
                    autoplay
                    loop
                  ></dotlottie-wc>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Why Choose + Community */}
      <section className="py-24 border-t border-border/30 relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.community} opacity="opacity-10" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            <div className="rounded-2xl border border-border/60 bg-card/60 p-8">
              <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground mb-3">Why Choose Lawmate</p>
              <h3 className="text-3xl sm:text-4xl font-bold text-foreground mb-6">
                Built for Modern Legal Excellence
              </h3>
              <div className="space-y-4">
                {[
                  "Precision-engineered for legal professionals and clients at every experience level",
                  "Accelerate advocate-client collaboration with intelligent workflow automation",
                  "Eliminate administrative overhead through smart automation and AI assistance",
                  "Unified platform consolidating research, case management, and secure communications",
                ].map((point, idx) => (
                  <motion.div
                    key={point}
                    initial={{ opacity: 0, y: 12 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: idx * 0.08 }}
                    className="flex items-start gap-3"
                  >
                    <div className="w-7 h-7 shrink-0 rounded-full gradient-primary flex items-center justify-center mt-0.5">
                      <Check className="w-4 h-4 text-primary-foreground" />
                    </div>
                    <p className="text-muted-foreground leading-relaxed">{point}</p>
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-border/60 bg-card/60 p-8 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/8 via-transparent to-accent/8" />
              <div className="relative z-10">
                <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground mb-3">Professional Network</p>
                <h3 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">Join Pakistan's Legal Innovation Community</h3>
                <p className="text-muted-foreground mb-7">
                  Connect with forward-thinking legal professionals, access exclusive product insights, forge strategic partnerships, and participate in the future of legal technology across Pakistan.
                </p>
                <div className="space-y-4">
                  {[
                    "Feature launches and legal-tech roadmap updates",
                    "Founders and advocate networking channels",
                    "Community sessions on AI, law, and operations",
                  ].map((item) => (
                    <div key={item} className="flex items-center gap-3">
                      <MessageSquareQuote className="w-4 h-4 text-primary" />
                      <p className="text-sm text-foreground/90">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-24 border-t border-border/30 relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.faq} opacity="opacity-10" />
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-foreground mb-4">Frequently Asked Questions</h2>
            <p className="text-muted-foreground text-lg">Everything you need to know about Lawmate</p>
          </div>

          <div className="space-y-4">
            {[
              {
                q: "Does Lawmate replace traditional legal counsel?",
                a: "No. Lawmate is a powerful legal technology platform that provides AI-powered research, workflow automation, and collaboration tools. However, professional legal advice and representation must always come from qualified, licensed lawyers. Our platform enhances—not replaces—the attorney-client relationship.",
              },
              {
                q: "How does Lawmate protect sensitive legal information?",
                a: "We employ military-grade encryption, bank-level security protocols, and granular permission controls. All data is encrypted both in transit and at rest, with secure communication channels specifically designed for confidential legal matters. Our infrastructure undergoes regular security audits and complies with international data protection standards.",
              },
              {
                q: "Who can benefit from using Lawmate?",
                a: "Lawmate serves three primary user groups: citizens and businesses seeking legal guidance, licensed advocates managing their practice, and law firms coordinating team operations. Each user type has dedicated workflows, tools, and features optimized for their specific needs.",
              },
              {
                q: "How does the verified lawyer marketplace work?",
                a: "Our intelligent matching system connects clients with specialized legal professionals based on practice area, location, case complexity, and verified credentials. All advocates undergo thorough verification, and clients can review ratings, experience, and response times before making a connection.",
              },
              {
                q: "What level of accuracy can I expect from AI guidance?",
                a: "Our AI is trained on Pakistani legal statutes and case law to provide contextually relevant, practical guidance. While highly accurate for research and initial consultation, all AI responses should be reviewed and validated by qualified legal counsel before making critical legal decisions.",
              },
              {
                q: "Does Lawmate provide enterprise solutions for law firms?",
                a: "Yes. Lawmate offers comprehensive enterprise features including advocate onboarding, intelligent matter distribution, complete client lifecycle management, secure document workflows, automated billing and invoicing, team collaboration tools, and advanced analytics dashboards for firm-wide performance insights.",
              },
            ].map((faq, i) => (
              <details
                key={i}
                className="group rounded-lg border border-border hover:border-primary/50 transition-all cursor-pointer bg-card hover:bg-card/80"
                style={{
                  animation: `fadeInUp 0.6s ease-out ${i * 50}ms backwards`,
                }}
              >
                <summary className="p-6 font-semibold text-foreground hover:text-primary transition-colors list-none [&::-webkit-details-marker]:hidden" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
                  <span style={{ flex: '1 1 auto', minWidth: 0 }}>{faq.q}</span>
                  <ChevronRight className="group-open:rotate-90 transition-transform" style={{ width: '20px', height: '20px', flexShrink: 0, color: 'var(--muted-foreground)' }} />
                </summary>
                <div className="px-6 pb-6 text-muted-foreground border-t border-border/50">{faq.a}</div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Reviews */}
      <section id="reviews" className="py-14 bg-card/20 border-t border-border/30 relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.reviews} opacity="opacity-10" />
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="text-center space-y-2">
            <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">Client Success Stories</p>
            <h3 className="text-3xl sm:text-4xl font-bold text-foreground">What users say about Lawmate</h3>
          </div>
          <AnimatedTestimonials
            autoplay
            testimonials={[
              {
                quote: "Lawmate transformed how we navigate legal matters. The AI guidance is remarkably intuitive, and connecting with specialized lawyers has never been easier. This platform truly democratizes access to quality legal support.",
                name: "Sumair S.",
                designation: "Business Owner, Karachi",
                src: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=1200&auto=format&fit=crop",
              },
              {
                quote: "As a practicing advocate, Lawmate's intelligent research capabilities and AI-powered case analysis have revolutionized my workflow. What used to take hours now takes minutes, allowing me to focus on strategy and client service.",
                name: "Advocate Zohaib Ahmad",
                designation: "Senior Advocate, Lahore High Court",
                src: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=1200&auto=format&fit=crop",
              },
              {
                quote: "Lawmate unified our entire legal operations. From client intake to case resolution, every process is streamlined and transparent. The analytics dashboard provides insights we never had before. It's indispensable for modern law firm management.",
                name: "Hammad R.",
                designation: "Managing Partner, Law Associates Islamabad",
                src: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?q=80&w=1200&auto=format&fit=crop",
              },
              {
                quote: "The verified lawyer marketplace gave me confidence and transparency in selecting legal representation. The platform's smart matching connected me with an advocate who perfectly understood my case complexity. Exceptional experience.",
                name: "Waris A.",
                designation: "Corporate Executive, Rawalpindi",
                src: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=1200&auto=format&fit=crop",
              },
            ]}
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 border-t border-border/30 relative overflow-hidden">
        <SectionVideoBg sources={sectionVideos.cta} opacity="opacity-10" />
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="relative rounded-2xl bg-gradient-to-br from-primary/20 via-accent/15 to-secondary/10 border border-border/50 p-12 sm:p-16 overflow-hidden group hover:border-primary/50 transition-all">
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-br from-primary/10 to-accent/10"></div>
            <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

            <div className="relative z-10 text-center">
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 text-balance">
                Transform Legal Operations Today
              </h2>
              <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
                Join thousands of citizens, advocates, and law firms leveraging Pakistan's most advanced legal technology platform for intelligent case management, AI-powered research, and seamless collaboration.
              </p>

              <div className="flex gap-4 justify-center flex-col sm:flex-row">
                <Button
                  size="lg"
                  className="gradient-primary text-primary-foreground border-0 shadow-lg hover:shadow-xl hover:scale-105 transition-all"
                  onClick={() => router.push("/citizen")}
                >
                  Start Free Trial <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="hover:bg-primary/10 bg-transparent border-primary/50"
                  onClick={() => router.push("/login")}
                >
                  Schedule Live Demo
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
              <p className="text-sm text-muted-foreground">Empowering legal professionals and clients through technology.</p>
            </div>

            <div>
              <h4 className="font-semibold text-foreground mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {["Features", "How It Works", "Marketplace", "Platform"].map((link) => (
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
                {["About", "Community", "Advisors", "Contact"].map((link) => (
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
                {["Privacy Policy", "Terms", "Compliance", "Disclaimer"].map((link) => (
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
            <p className="text-sm text-muted-foreground">© 2026 Lawmate. All rights reserved.</p>
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
