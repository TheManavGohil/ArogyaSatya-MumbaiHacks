"use client"

import { memo, useEffect, useLayoutEffect, useMemo, useState } from "react"
import {
  AnimatePresence,
  motion,
  useAnimation,
  useMotionValue,
  useTransform,
} from "framer-motion"
import { Brain, Shield, Target, Zap } from "lucide-react"

export const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect

type UseMediaQueryOptions = {
  defaultValue?: boolean
  initializeWithValue?: boolean
}

const IS_SERVER = typeof window === "undefined"

export function useMediaQuery(
  query: string,
  {
    defaultValue = false,
    initializeWithValue = true,
  }: UseMediaQueryOptions = {}
): boolean {
  const getMatches = (query: string): boolean => {
    if (IS_SERVER) {
      return defaultValue
    }
    return window.matchMedia(query).matches
  }

  const [matches, setMatches] = useState<boolean>(() => {
    if (initializeWithValue) {
      return getMatches(query)
    }
    return defaultValue
  })

  const handleChange = () => {
    setMatches(getMatches(query))
  }

  useIsomorphicLayoutEffect(() => {
    const matchMedia = window.matchMedia(query)
    handleChange()

    matchMedia.addEventListener("change", handleChange)

    return () => {
      matchMedia.removeEventListener("change", handleChange)
    }
  }, [query])

  return matches
}

const features = [
  {
    icon: Shield,
    title: "Proactive Strategy vs. Reactive Process",
    description:
      "Detects misinformation early and inoculates before it spreads, building herd immunity in the population.",
    img: "https://picsum.photos/200/300?night",
  },
  {
    icon: Target,
    title: "Focus on Tactics over Claims",
    description:
      "Identifies manipulation techniques like scapegoating, false dichotomies, and emotional language rather than individual claims.",
    img: "https://picsum.photos/200/300?city",
  },
  {
    icon: Brain,
    title: "Goal of Empowerment, Not Just Correction",
    description:
      "Explains why something is manipulative, building critical thinking skills and long-term cognitive resilience.",
    img: "https://picsum.photos/200/300?sky",
  },
  {
    icon: Zap,
    title: "Autonomous Content Generation",
    description:
      "Generates prebunking blogs, infographics, and videos automatically at machine speed to outpace viral spread.",
    img: "https://picsum.photos/200/300?sunset",
  },
  {
    icon: Shield,
    title: "Proactive Strategy vs. Reactive Process",
    description:
      "Detects misinformation early and inoculates before it spreads, building herd immunity in the population.",
    img: "https://picsum.photos/200/300?sunrise",
  },
  {
    icon: Brain,
    title: "Goal of Empowerment, Not Just Correction",
    description:
      "Explains why something is manipulative, building critical thinking skills and long-term cognitive resilience.",
    img: "https://picsum.photos/200/300?winter",
  },
]

const duration = 0.15
const transition = { duration, ease: [0.32, 0.72, 0, 1], filter: "blur(4px)" }
const transitionOverlay = { duration: 0.5, ease: [0.32, 0.72, 0, 1] }

const Carousel = memo(
  ({
    handleClick,
    controls,
    cards,
    isCarouselActive,
  }: {
    handleClick: (imgUrl: string, index: number) => void
    controls: any
    cards: typeof features
    isCarouselActive: boolean
  }) => {
    const isScreenSizeSm = useMediaQuery("(max-width: 640px)")
    const cylinderWidth = isScreenSizeSm ? 1100 : 1800
    const faceCount = cards.length
    const faceWidth = cylinderWidth / faceCount
    const radius = cylinderWidth / (2 * Math.PI)
    const rotation = useMotionValue(0)
    const transform = useTransform(
      rotation,
      (value) => `rotate3d(0, 1, 0, ${value}deg)`
    )

    return (
      <div
        className="flex h-full items-center justify-center bg-mauve-dark-2"
        style={{
          perspective: "1000px",
          transformStyle: "preserve-3d",
          willChange: "transform",
        }}
      >
        <motion.div
          drag={isCarouselActive ? "x" : false}
          className="relative flex h-full origin-center cursor-grab justify-center active:cursor-grabbing"
          style={{
            transform,
            rotateY: rotation,
            width: cylinderWidth,
            transformStyle: "preserve-3d",
          }}
          onDrag={(_, info) =>
            isCarouselActive &&
            rotation.set(rotation.get() + info.offset.x * 0.05)
          }
          onDragEnd={(_, info) =>
            isCarouselActive &&
            controls.start({
              rotateY: rotation.get() + info.velocity.x * 0.05,
              transition: {
                type: "spring",
                stiffness: 100,
                damping: 30,
                mass: 0.1,
              },
            })
          }
          animate={controls}
        >
          {cards.map((feature, i) => (
            <motion.div
              key={`key-${feature.img}-${i}`}
              className="absolute flex h-full origin-center items-center justify-center rounded-xl bg-mauve-dark-2 p-2"
              style={{
                width: `${faceWidth}px`,
                transform: `rotateY(${
                  i * (360 / faceCount)
                }deg) translateZ(${radius}px)`,
              }}
              onClick={() => handleClick(feature.img, i)}
              whileHover="hover"
            >
              <motion.img
                src={feature.img}
                alt={feature.title}
                layoutId={`img-${feature.img}`}
                className="pointer-events-none  w-full rounded-xl object-cover aspect-square"
                initial={{ filter: "blur(4px)" }}
                layout="position"
                animate={{ filter: "blur(0px)" }}
                transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const }}
              />
              <motion.div
                className="absolute inset-0 bg-black bg-opacity-60 flex flex-col items-center justify-center p-4 rounded-xl text-white"
                initial={{ opacity: 0 }}
                variants={{ hover: { opacity: 1 } }}
                transition={{ duration: 0.3 }}
              >
                <feature.icon className="w-8 h-8 mb-2" />
                <h3 className="text-lg font-bold text-center mb-1">{feature.title}</h3>
                <p className="text-xs text-center">{feature.description}</p>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    )
  }
)

const hiddenMask = `repeating-linear-gradient(to right, rgba(0,0,0,0) 0px, rgba(0,0,0,0) 30px, rgba(0,0,0,1) 30px, rgba(0,0,0,1) 30px)`
const visibleMask = `repeating-linear-gradient(to right, rgba(0,0,0,0) 0px, rgba(0,0,0,0) 0px, rgba(0,0,0,1) 0px, rgba(0,0,0,1) 30px)`
function ThreeDPhotoCarousel() {
  const [activeImg, setActiveImg] = useState<string | null>(null)
  const [isCarouselActive, setIsCarouselActive] = useState(true)
  const controls = useAnimation()
  const cards = features

  const activeFeatureDetails = useMemo(() => {
    if (!activeImg) return null
    return features.find((feature) => feature.img === activeImg)
  }, [activeImg])

  useEffect(() => {
    console.log("Cards loaded:", cards)
  }, [cards])

  const handleClick = (imgUrl: string) => {
    setActiveImg(imgUrl)
    setIsCarouselActive(false)
    controls.stop()
  }

  const handleClose = () => {
    setActiveImg(null)
    setIsCarouselActive(true)
  }

  return (
    <motion.div layout className="relative">
      <AnimatePresence>
        {activeImg && activeFeatureDetails && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8"
            onClick={handleClose}
            style={{ willChange: "opacity" }}
          >
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1, transition: { duration: 0.4, ease: [0.25, 1, 0.5, 1] } }}
              exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.3, ease: [0.5, 0, 0.75, 0] } }}
              className="bg-[#111] border border-white/10 rounded-2xl p-8 flex flex-col md:flex-row gap-8 w-full max-w-6xl mx-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="w-full md:w-1/2 flex items-center justify-center">
                <motion.img
                  layoutId={`img-${activeImg}`}
                  src={activeImg}
                  className="w-full h-auto max-h-[80vh] object-contain rounded-lg shadow-2xl"
                />
              </div>
              <motion.div className="w-full md:w-1/2 text-white flex flex-col justify-center">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    transition: { delay: 0.3, duration: 0.5 },
                  }}
                >
                  <activeFeatureDetails.icon className="w-12 h-12 mb-4 text-blue-400" />
                  <h2 className="text-3xl lg:text-4xl font-bold mb-4">
                    {activeFeatureDetails.title}
                  </h2>
                  <p className="text-lg text-gray-300">
                    {activeFeatureDetails.description}
                  </p>
                </motion.div>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      <div className="relative h-[700px] w-full overflow-hidden">
        <Carousel
          handleClick={handleClick}
          controls={controls}
          cards={cards}
          isCarouselActive={isCarouselActive}
        />
      </div>
    </motion.div>
  )
}

export { ThreeDPhotoCarousel };
