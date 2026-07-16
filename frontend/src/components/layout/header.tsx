"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { api } from "@/services/api"
import { cn } from "@/lib/utils"

export function Header() {
  const router = useRouter()
  const [user, setUser] = useState<{ email: string; full_name: string } | null>(null)
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      api
        .get("/auth/me")
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
        })
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setUser(null)
    router.push("/login")
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="font-bold text-lg">
            Resume Builder
          </Link>
          {user && (
            <nav className="hidden md:flex items-center gap-4 text-sm">
              <Link href="/dashboard" className="hover:text-primary transition-colors">
                Dashboard
              </Link>
              <Link href="/resumes" className="hover:text-primary transition-colors">
                Resumes
              </Link>
              <Link href="/templates" className="hover:text-primary transition-colors">
                Templates
              </Link>
              <Link href="/jobs" className="hover:text-primary transition-colors">
                Jobs
              </Link>
            </nav>
          )}
        </div>
        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground hidden sm:inline">
                {user.full_name}
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-muted-foreground hover:text-destructive transition-colors"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="text-sm bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90 transition-colors"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
