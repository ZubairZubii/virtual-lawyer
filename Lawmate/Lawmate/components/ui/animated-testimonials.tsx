"use client"

import { IconArrowLeft, IconArrowRight } from "@tabler/icons-react"
import { AnimatePresence, motion } from "framer-motion"
import Image from "next/image"
import { useEffect, useState } from "react"

type Testimonial = {
  quote: string
  name: string
  designation: string
  src: string
}

export function AnimatedTestimonials({ testimonials, autoplay = false }: { testimonials: Testimonial[]; autoplay?: boolean }) {
  const [active, setActive] = useState(0)
  const [mounted, setMounted] = useState(false)
  // Pre-generate random rotations to avoid hydration mismatch
  const [rotations, setRotations] = useState<number[]>([])

  const handleNext = () => setActive((prev) => (prev + 1) % testimonials.length)
  const handlePrev = () => setActive((prev) => (prev - 1 + testimonials.length) % testimonials.length)
  const isActive = (index: number) => index === active

  // Generate rotations only on client side after mount
  useEffect(() => {
    setMounted(true)
    // Generate deterministic rotations based on index (consistent between server/client)
    const initialRotations = testimonials.map((_, index) => {
      // Use index-based seed for consistency, but add some variation
      return ((index * 7 + 13) % 21) - 10
    })
    setRotations(initialRotations)
  }, [testimonials])

  useEffect(() => {
    if (!autoplay) return
    const interval = setInterval(handleNext, 5000)
    return () => clearInterval(interval)
  }, [autoplay, testimonials.length])

  // Use pre-generated rotations or fallback to 0 during SSR
  const getRotation = (index: number) => {
    if (!mounted || rotations.length === 0) return 0
    return rotations[index] || 0
  }

  return (
    <div className="mx-auto max-w-sm px-4 py-16 font-sans antialiased md:max-w-5xl md:px-8 lg:px-12">
      <div className="relative grid grid-cols-1 gap-12 md:gap-20 md:grid-cols-2 items-center">
        <div>
          <div className="relative h-72 sm:h-80 w-full">
            <AnimatePresence>
              {testimonials.map((testimonial, index) => {
                const rotation = getRotation(index)
                return (
                <motion.div
                  key={testimonial.src}
                  initial={{ opacity: 0, scale: 0.9, z: -100, rotate: rotation }}
                  animate={{
                    opacity: isActive(index) ? 1 : 0.7,
                    scale: isActive(index) ? 1 : 0.95,
                    z: isActive(index) ? 0 : -100,
                    rotate: isActive(index) ? 0 : rotation,
                    zIndex: isActive(index) ? 40 : testimonials.length + 2 - index,
                    y: isActive(index) ? [0, -60, 0] : 0,
                  }}
                  exit={{ opacity: 0, scale: 0.9, z: 100, rotate: rotation }}
                  transition={{ duration: 0.45, ease: "easeInOut" }}
                  className="absolute inset-0 origin-bottom"
                >
                  <Image
                    src={testimonial.src || "/placeholder-user.jpg"}
                    alt={testimonial.name}
                    width={600}
                    height={600}
                    draggable={false}
                    className="h-full w-full rounded-3xl object-cover object-center shadow-xl"
                  />
                </motion.div>
                )
              })}
            </AnimatePresence>
          </div>
        </div>

        <div className="flex flex-col justify-between py-4">
          <motion.div
            key={active}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
          >
            <h3 className="text-2xl font-bold text-foreground">{testimonials[active].name}</h3>
            <p className="text-sm text-muted-foreground">{testimonials[active].designation}</p>
            <motion.p className="mt-6 text-base sm:text-lg text-muted-foreground leading-relaxed">
              {testimonials[active].quote.split(" ").map((word, index) => (
                <motion.span
                  key={index}
                  initial={{ filter: "blur(10px)", opacity: 0, y: 5 }}
                  animate={{ filter: "blur(0px)", opacity: 1, y: 0 }}
                  transition={{ duration: 0.18, ease: "easeInOut", delay: 0.018 * index }}
                  className="inline-block"
                >
                  {word}&nbsp;
                </motion.span>
              ))}
            </motion.p>
          </motion.div>

          <div className="flex gap-3 pt-10 md:pt-0">
            <button
              onClick={handlePrev}
              className="group flex h-9 w-9 items-center justify-center rounded-full border border-border bg-background/80 backdrop-blur-sm"
            >
              <IconArrowLeft className="h-5 w-5 text-foreground transition-transform duration-300 group-hover:-translate-x-0.5" />
            </button>
            <button
              onClick={handleNext}
              className="group flex h-9 w-9 items-center justify-center rounded-full border border-border bg-background/80 backdrop-blur-sm"
            >
              <IconArrowRight className="h-5 w-5 text-foreground transition-transform duration-300 group-hover:translate-x-0.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

