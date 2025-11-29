"use client"

import { Home, User, Briefcase, FileText, LayoutDashboard } from 'lucide-react'
import { NavBar } from "@/components/tubelight-navbar"

export function NavBarDemo() {
  const navItems = [
    { name: 'Home', url: 'http://localhost:3000', icon: Home },
    { name: 'Features', url: 'http://localhost:3000#features', icon: User },
    { name: 'User Journey', url: 'http://localhost:3000#user-journey', icon: Briefcase },
    { name: 'Blog', url: 'http://localhost:3000#blog', icon: FileText },
    { name: 'Dashboard', url: 'http://localhost:3000/dashboard', icon: LayoutDashboard }
  ]

  return <NavBar items={navItems} />
}