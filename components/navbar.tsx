"use client"

import { Home, User, Briefcase, FileText } from 'lucide-react'
import { NavBar } from "@/components/tubelight-navbar"

export function NavBarDemo() {
  const navItems = [
    { name: 'Home', url: '#', icon: Home },
    { name: 'Features', url: '#features', icon: User },
    { name: 'User Journey', url: '#user-journey', icon: Briefcase },
    { name: 'Blog', url: '#blog', icon: FileText }
  ]

  return <NavBar items={navItems} />
}