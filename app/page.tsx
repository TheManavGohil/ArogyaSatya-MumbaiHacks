import { Hero } from "@/components/hero"
import { UserJourney } from "@/components/user-journey"
import { BlogSection } from "@/components/blog-section"
import { Footer } from "@/components/footer"
import { SplineSceneBasic } from "@/components/demo"
import { ThreeDPhotoCarousel } from "@/components/3d-caurosel"

export default function Home() {
  return (
    <main className="min-h-screen bg-black">
      <SplineSceneBasic />
      <ThreeDPhotoCarousel />
      <UserJourney />
      <BlogSection />
      <Footer />
    </main>
  )
}
