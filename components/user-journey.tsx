"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageSquare, AlertTriangle, Search, CheckCircle, FileText } from "lucide-react"
import { useEffect, useState } from "react"

const journeySteps = [
  {
    icon: MessageSquare,
    title: "The Encounter with Misinformation",
    description:
      "Priya receives a forwarded message in her family WhatsApp group about a 'miracle cure' video that looks professional and urgent.",
  },
  {
    icon: AlertTriangle,
    title: "The Moment of Hesitation",
    description:
      "Instead of forwarding the message, Priya remembers TrueLens and sends the video to our WhatsApp verification service.",
  },
  {
    icon: Search,
    title: "The Agent's Instant Analysis",
    description:
      "AI analyzes the video content, transcribes audio, and identifies the manipulation tactic: impersonating medical authority.",
  },
  {
    icon: CheckCircle,
    title: "Immediate, Empowering Response",
    description:
      "Priya receives an educational response explaining the impersonation tactic and directing her to official health sources.",
  },
  {
    icon: FileText,
    title: "Proactive Inoculation",
    description:
      "AI generates a comprehensive blog post debunking the claim with proof from official sources and government websites.",
  },
]

export function UserJourney() {
  const [visibleSteps, setVisibleSteps] = useState<number[]>([])

  useEffect(() => {
    const timer = setInterval(() => {
      setVisibleSteps((prev) => {
        if (prev.length < journeySteps.length) {
          return [...prev, prev.length]
        }
        return prev
      })
    }, 300)

    return () => clearInterval(timer)
  }, [])

  return (
    <section className="py-20 px-4 bg-black">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-white to-green-200 bg-clip-text text-transparent">
            How It Works: Priya's Journey
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Follow a real user's experience with our AI-powered misinformation detection system
          </p>
        </div>

        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-gradient-to-b from-primary via-secondary to-primary opacity-30 hidden lg:block"></div>

          <div className="space-y-12">
            {journeySteps.map((step, index) => {
              const Icon = step.icon
              const isVisible = visibleSteps.includes(index)
              const isEven = index % 2 === 0

              return (
                <div
                  key={index}
                  className={`flex items-center ${isEven ? "lg:flex-row" : "lg:flex-row-reverse"} transition-all duration-700 ${
                    isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
                  }`}
                >
                  <div className={`flex-1 ${isEven ? "lg:pr-8" : "lg:pl-8"}`}>
                    <Card className="glassmorphism border-border/50 hover:border-primary/50 transition-all duration-300 group">
                      <CardHeader>
                        <div className="flex items-center gap-4">
                          <div className="p-3 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 group-hover:from-primary/30 group-hover:to-secondary/30 transition-all">
                            <Icon className="h-6 w-6 text-primary group-hover:text-secondary transition-colors" />
                          </div>
                          <div>
                            <div className="text-sm text-secondary font-medium mb-1">Step {index + 1}</div>
                            <CardTitle className="text-lg text-card-foreground">{step.title}</CardTitle>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <CardDescription className="text-gray-300 leading-relaxed">{step.description}</CardDescription>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Timeline dot */}
                  <div className="hidden lg:flex w-4 h-4 bg-gradient-to-r from-primary to-secondary rounded-full border-4 border-background z-10 flex-shrink-0"></div>

                  <div className="flex-1"></div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
