"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink } from "lucide-react"
import { useEffect, useState } from "react"

const blogPosts = [
  {
    title: "Garlic water cures the virus?",
    description:
      "This claim uses impersonation tactics, falsely presenting unverified individuals as medical experts. No scientific evidence supports garlic water as a COVID-19 cure.",
    tags: ["Health", "Fact-Check", "WHO Verified"],
    sources: ["Ministry of Health", "WHO Guidelines", "AIIMS Research"],
  },
  {
    title: "5G towers spread coronavirus?",
    description:
      "This narrative employs scapegoating and false causation. Multiple international health organizations confirm no link between 5G technology and virus transmission.",
    tags: ["Technology", "Fact-Check", "Scientific Evidence"],
    sources: ["WHO", "IEEE Standards", "Government Tech Policy"],
  },
  {
    title: "Miracle immunity boosters?",
    description:
      "Claims use emotional language and false authority to promote unproven supplements. Legitimate immunity support comes from balanced diet and verified medical advice.",
    tags: ["Health", "Consumer Protection", "Medical Verification"],
    sources: ["FDA Guidelines", "Medical Council", "Nutrition Research"],
  },
]

export function BlogSection() {
  const [visiblePosts, setVisiblePosts] = useState<number[]>([])

  useEffect(() => {
    const timer = setInterval(() => {
      setVisiblePosts((prev) => {
        if (prev.length < blogPosts.length) {
          return [...prev, prev.length]
        }
        return prev
      })
    }, 250)

    return () => clearInterval(timer)
  }, [])

  return (
    <section id="blog" className="py-20 px-4">
      <div className="container mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
            Live Prebunking Content
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Real-time analysis and debunking of trending misinformation with official sources and proof
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {blogPosts.map((post, index) => {
            const isVisible = visiblePosts.includes(index)

            return (
              <Card
                key={index}
                className={`glassmorphism border-border/50 hover:border-primary/50 transition-all duration-500 group hover:scale-105 cursor-pointer ${
                  isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
                }`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg font-semibold text-card-foreground group-hover:text-primary transition-colors">
                      {post.title}
                    </CardTitle>
                    <ExternalLink className="h-5 w-5 text-gray-400 group-hover:text-secondary transition-colors flex-shrink-0" />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {post.tags.map((tag, tagIndex) => (
                      <Badge
                        key={tagIndex}
                        variant="secondary"
                        className="bg-secondary/20 text-secondary border-secondary/30"
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <CardDescription className="text-gray-300 leading-relaxed">{post.description}</CardDescription>

                  <div>
                    <h4 className="text-sm font-medium text-primary mb-2">Official Sources:</h4>
                    <div className="flex flex-wrap gap-2">
                      {post.sources.map((source, sourceIndex) => (
                        <Badge
                          key={sourceIndex}
                          variant="outline"
                          className="text-xs border-primary/30 text-primary/80"
                        >
                          {source}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
