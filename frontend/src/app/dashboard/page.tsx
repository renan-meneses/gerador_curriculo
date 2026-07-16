"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { resumes, jobs, templates } from "@/services/api"
import { Header } from "@/components/layout/header"

interface ResumeSummary {
  id: string
  title: string
  target_job_title?: string
  target_company?: string
  created_at: string
  updated_at: string
}

interface QuickStat {
  label: string
  value: number
  href: string
  icon: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [resumeList, setResumeList] = useState<ResumeSummary[]>([])
  const [stats, setStats] = useState<QuickStat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }
    loadDashboard()
  }, [router])

  const loadDashboard = async () => {
    try {
      const [resumesRes, jobsRes, templatesRes] = await Promise.all([
        resumes.list(),
        jobs.list(),
        templates.list(),
      ])
      setResumeList(resumesRes.data)
      setStats([
        { label: "Resumes", value: resumesRes.data.length, href: "/resumes", icon: "📄" },
        { label: "Saved Jobs", value: jobsRes.data.length, href: "/jobs", icon: "💼" },
        { label: "Templates", value: templatesRes.data.length, href: "/templates", icon: "🎨" },
      ])
    } catch {
      router.push("/login")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="container py-8">
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <Link
            href="/resumes/new"
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-primary/90 transition-colors"
          >
            New Resume
          </Link>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {stats.map((stat) => (
            <Link
              key={stat.label}
              href={stat.href}
              className="border rounded-lg p-4 hover:border-primary transition-colors"
            >
              <div className="text-2xl mb-1">{stat.icon}</div>
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </Link>
          ))}
          <Link
            href="/imports"
            className="border rounded-lg p-4 hover:border-primary transition-colors border-dashed"
          >
            <div className="text-2xl mb-1">📥</div>
            <div className="text-sm font-medium">Import</div>
            <div className="text-sm text-muted-foreground">LinkedIn / Markdown</div>
          </Link>
        </div>

        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recent Resumes</h2>
            <Link href="/resumes" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          {resumeList.length === 0 ? (
            <div className="border rounded-lg p-8 text-center">
              <p className="text-muted-foreground mb-4">No resumes yet</p>
              <Link
                href="/resumes/new"
                className="text-primary hover:underline font-medium"
              >
                Create your first resume
              </Link>
            </div>
          ) : (
            <div className="grid gap-4">
              {resumeList.slice(0, 5).map((resume) => (
                <Link
                  key={resume.id}
                  href={`/resumes/${resume.id}`}
                  className="border rounded-lg p-4 hover:border-primary transition-colors flex items-center justify-between"
                >
                  <div>
                    <h3 className="font-medium">{resume.title}</h3>
                    {(resume.target_job_title || resume.target_company) && (
                      <p className="text-sm text-muted-foreground">
                        {resume.target_job_title}
                        {resume.target_company && ` at ${resume.target_company}`}
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(resume.updated_at).toLocaleDateString()}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
