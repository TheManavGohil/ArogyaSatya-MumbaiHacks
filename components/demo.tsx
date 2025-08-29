'use client'

import { SplineScene } from "@/components/splite";
import { Card } from "@/components/card"
import { Spotlight } from "@/components/spotlight"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Play } from "lucide-react"
import { useEffect, useState, useRef } from "react"
 
export function SplineSceneBasic() {
  const [isVisible, setIsVisible] = useState(false)
  const [isHovered, setIsHovered] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: -1000, y: -1000 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsVisible(true)
  }, [])

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setMousePosition({ x: event.clientX - rect.left, y: event.clientY - rect.top });
    }
  };

  return (
    <Card 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="w-full h-screen bg-black relative overflow-hidden border-0">
      <div
        className="pointer-events-none absolute inset-0 z-0 transition-opacity duration-500"
        style={{
          backgroundImage: 'url(/newspaper.jpg)',
          backgroundPosition: 'center',
          backgroundSize: 'cover',
          maskImage: `radial-gradient(circle 150px at ${mousePosition.x}px ${mousePosition.y}px, black, transparent)`,
          WebkitMaskImage: `radial-gradient(circle 150px at ${mousePosition.x}px ${mousePosition.y}px, black, transparent)`,
          opacity: isHovered ? 1 : 0,
        }}
      />
      
      <div className="flex h-full">
        {/* Left content */}
        <div className="flex-1 p-8 relative z-10 flex flex-col justify-center items-center lg:items-start">
          <div
            className={`bg-clip-padding p-10 max-w-2xl text-center lg:text-left space-y-8 transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
          >
            <div className="space-y-6">
              <Badge
                variant="outline"
                className="bg-gradient-to-r from-blue-500/20 to-cyan-400/20 text-blue-300 border-blue-400/30 shadow-lg mb-4"
              >
                New & Improved AI Model
              </Badge>
              <h1 className="text-5xl lg:text-7xl font-bold bg-gradient-to-r from-white via-blue-300 to-cyan-400 bg-clip-text text-transparent leading-tight drop-shadow-xl">
                TrueLens
              </h1>
              <h2 className="text-2xl lg:text-3xl font-semibold text-blue-200/90">The AI Crisis Clarity Agent</h2>
              <p className="text-xl text-gray-400/80 leading-relaxed">
                Proactively combating misinformation with AI-powered inoculation. Building cognitive immunity before the
                harm is done.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500 text-white shadow-lg group transform hover:-translate-y-1 transition-all duration-300"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white group bg-transparent transition-colors"
              >
                <Play className="mr-2 h-5 w-5 group-hover:scale-110 transition-transform" />
                Learn More
              </Button>
            </div>
          </div>
        </div>

        {/* Right content */}
        <div className="flex-1 relative">
          <SplineScene 
            scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
            className="w-full h-full"
          />
        </div>
      </div>
    </Card>
  )
}