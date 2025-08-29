"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Play } from "lucide-react"
import { useEffect, useState } from "react"

// Spline component placeholder
function SplineScene({ scene, className }: { scene: string; className: string }) {
  return (
    <div className={`${className} flex items-center justify-center glassmorphism rounded-2xl`}>
      <div className="text-center p-8">
        <div className="w-32 h-32 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-green-400 rounded-full animate-pulse-glow flex items-center justify-center">
          <div className="w-16 h-16 bg-white/20 rounded-full animate-spin"></div>
        </div>
        <p className="text-sm text-muted opacity-60">3D AI Robot Animation</p>
      </div>
    </div>
  )
}

export function Hero() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <section className="min-h-screen flex items-center justify-center px-4 py-20">
      <div className="container mx-auto max-w-7xl">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Content */}
          <div
            className={`space-y-10 transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
          >
            <div className="space-y-4">
              <h1 className="text-7xl lg:text-8xl font-bold bg-gradient-to-r from-white via-blue-200 to-green-200 bg-clip-text text-transparent leading-tight">
                TrueLens
              </h1>
              <h2 className="text-4xl lg:text-4xl font-semibold text-blue-300">The AI Crisis Clarity Agent</h2>
              <p className="text-2xl text-gray-300 leading-relaxed max-w-lg">
                Proactively combating misinformation with AI-powered inoculation. Building cognitive immunity before the
                harm is done.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground animate-glow group">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-secondary text-secondary hover:bg-secondary/10 group bg-transparent"
              >
                <Play className="mr-2 h-5 w-5 group-hover:scale-110 transition-transform" />
                Learn More
              </Button>
            </div>
          </div>

          {/* Right side - Spline 3D */}
          <div
            className={`transition-all duration-1000 delay-300 ${isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-10"}`}
          >
            <SplineScene
              scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
              className="w-full h-96 lg:h-[500px]"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
