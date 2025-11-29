import { Hero } from "@/components/hero"
import { UserJourney } from "@/components/user-journey"
import { BlogSection } from "@/components/blog-section"
import { Footer } from "@/components/footer"
import { SplineSceneBasic } from "@/components/demo"
// import { ThreeDPhotoCarousel } from "@/components/3d-caurosel"
import { Features } from "@/components/features"
import { AnalyzeTextPanel } from "@/components/analyze-text"

export default function Home() {
  return (
    <main className="min-h-screen bg-black">
      <SplineSceneBasic />
      <Features />
      <AnalyzeTextPanel />
      <UserJourney />
      <BlogSection />
      <Footer />
    </main>
  )
}
