"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, Target, Brain, Zap } from "lucide-react"
import { useEffect, useState } from "react"

const features = [
  {
    icon: Shield,
    title: "Proactive Strategy vs. Reactive Process",
    description:
      "Detects misinformation early and inoculates before it spreads, building herd immunity in the population.",
  },
  {
    icon: Target,
    title: "Focus on Tactics over Claims",
    description:
      "Identifies manipulation techniques like scapegoating, false dichotomies, and emotional language rather than individual claims.",
  },
  {
    icon: Brain,
    title: "Goal of Empowerment, Not Just Correction",
    description:
      "Explains why something is manipulative, building critical thinking skills and long-term cognitive resilience.",
  },
  {
    icon: Zap,
    title: "Autonomous Content Generation",
    description:
      "Generates prebunking blogs, infographics, and videos automatically at machine speed to outpace viral spread.",
  },
]

export function Features() {
  const [visibleCards, setVisibleCards] = useState<number[]>([])

  useEffect(() => {
    const timer = setInterval(() => {
      setVisibleCards((prev) => {
        if (prev.length < features.length) {
          return [...prev, prev.length]
        }
        return prev
      })
    }, 200)

    return () => clearInterval(timer)
  }, [])

  return (
    <section id="features" className="py-20 px-4">
      <div className="container mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
            Key Features
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Revolutionary AI technology that transforms the fight against misinformation
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            const isVisible = visibleCards.includes(index)

            return (
              <Card
                key={index}
                className={`glassmorphism border-border/50 hover:border-primary/50 transition-all duration-500 group hover:scale-105 ${
                  isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
                }`}
              >
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 p-3 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 w-fit group-hover:from-primary/30 group-hover:to-secondary/30 transition-all">
                    <Icon className="h-8 w-8 text-primary group-hover:text-secondary transition-colors" />
                  </div>
                  <CardTitle className="text-lg font-semibold text-card-foreground">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300 leading-relaxed">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
