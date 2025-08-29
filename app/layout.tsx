import type React from "react"
import type { Metadata } from "next"
import { DM_Sans } from "next/font/google"
import "./globals.css"
import { NavBarDemo } from "@/components/navbar"

const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm-sans",
})

export const metadata: Metadata = {
  title: "TrueLens: AI Crisis Clarity Agent",
  description: "Proactively combating misinformation with AI-powered inoculation",
  generator: "v0.app",
  manifest: "/manifest.json",
  icons: {
    icon: [
      { url: "/icon0.svg", type: "image/svg+xml" },
      { url: "/icon1.png", type: "image/png" },
    ],
    shortcut: "/favicon.ico",
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <style>{`
          html {
            font-family: ${dmSans.style.fontFamily};
            --font-sans: ${dmSans.variable};
          }
        `}</style>
      </head>
      <body className={dmSans.className}>
        <NavBarDemo />
        {children}
      </body>
    </html>
  )
}
