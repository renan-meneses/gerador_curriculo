"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { resumes as resumesApi, jobs, templates as templatesApi, exports_api } from "@/services/api"
import { Header } from "@/components/layout/header"

interface ResumeDetail {
  id: string
  title: string
  target_job_title?: string
  target_company?: string
  locale: string
  source?: string
  created_at: string
  updated_at: string
  version_count: number
}

export default function ResumeDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [resume, setResume] = useState<ResumeDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"view" | "analyze" | "export">("view")

  useEffect(() => {
    loadResume()
  }, [])

  const loadResume = async () => {
    try {
      const response = await resumesApi.get(params.id as string)
      setResume(response.data)
    } catch {
      router.push("/resumes")
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: string) => {
    try {
      const exportApi = exports_api[format as keyof typeof exports_api] as Function
      const response = await exportApi({ resume_id: params.id })
      alert(`Export ${format.toUpperCase()} queued! (ID: ${response.data.export_id})`)
    } catch (err) {
      console.error("Export failed", err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="container py-8">
          <p className="text-muted-foreground">Loading resume...</p>
        </div>
      </div>
    )
  }

  if (!resume) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="container py-8">
          <p className="text-destructive">Resume not found</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{resume.title}</h1>
            <p className="text-sm text-muted-foreground">
              {resume.target_job_title && `${resume.target_job_title}`}
              {resume.target_company && ` at ${resume.target_company}`}
              <span className="ml-2">· {resume.version_count} versions</span>
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleExport("pdf")}
              className="border px-3 py-1.5 rounded-md text-sm hover:bg-secondary transition-colors"
            >
              Export PDF
            </button>
            <button
              onClick={() => handleExport("docx")}
              className="border px-3 py-1.5 rounded-md text-sm hover:bg-secondary transition-colors"
            >
              Export DOCX
            </button>
          </div>
        </div>

        <div className="border-b mb-6">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab("view")}
              className={`pb-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "view"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Resume Content
            </button>
            <button
              onClick={() => setActiveTab("analyze")}
              className={`pb-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "analyze"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Job Analysis
            </button>
            <button
              onClick={() => setActiveTab("export")}
              className={`pb-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "export"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Export
            </button>
          </div>
        </div>

        {activeTab === "view" && (
          <div className="border rounded-lg p-8 min-h-[400px]">
            <p className="text-muted-foreground text-center py-12">
              Resume editor coming soon. Use the API to populate resume content.
            </p>
          </div>
        )}

        {activeTab === "analyze" && (
          <div className="border rounded-lg p-8">
            <h2 className="text-lg font-semibold mb-4">Job Match Analysis</h2>
            <p className="text-muted-foreground mb-4">
              Analyze this resume against a job description to get AI-powered suggestions.
            </p>
            <button
              onClick={() => router.push("/jobs")}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm hover:bg-primary/90 transition-colors"
            >
              Select Job Description
            </button>
          </div>
        )}

        {activeTab === "export" && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Export Resume</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { format: "pdf", label: "PDF", desc: "Preserves template layout" },
                { format: "docx", label: "DOCX", desc: "Editable Word document" },
                { format: "markdown", label: "Markdown", desc: "Plain text format" },
                { format: "html", label: "HTML", desc: "Web page format" },
              ].map(({ format, label, desc }) => (
                <button
                  key={format}
                  onClick={() => handleExport(format)}
                  className="border rounded-lg p-4 text-left hover:border-primary transition-colors"
                >
                  <div className="font-medium">{label}</div>
                  <div className="text-sm text-muted-foreground">{desc}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
