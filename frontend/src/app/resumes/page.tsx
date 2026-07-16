"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { resumes as resumesApi } from "@/services/api"
import { Header } from "@/components/layout/header"

interface ResumeSummary {
  id: string
  title: string
  target_job_title?: string
  target_company?: string
  created_at: string
  updated_at: string
}

export default function ResumesPage() {
  const router = useRouter()
  const [resumeList, setResumeList] = useState<ResumeSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }
    loadResumes()
  }, [router])

  const loadResumes = async () => {
    try {
      const response = await resumesApi.list()
      setResumeList(response.data)
    } catch {
      router.push("/login")
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm("Delete this resume? This action cannot be undone.")) return
    try {
      await resumesApi.delete(id)
      setResumeList((prev) => prev.filter((r) => r.id !== id))
    } catch (err) {
      console.error("Failed to delete resume", err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="container py-8">
          <p className="text-muted-foreground">Loading resumes...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Resumes</h1>
          <Link
            href="/resumes/new"
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-primary/90 transition-colors"
          >
            Create Resume
          </Link>
        </div>

        {resumeList.length === 0 ? (
          <div className="border rounded-lg p-12 text-center">
            <h2 className="text-xl font-semibold mb-2">No resumes yet</h2>
            <p className="text-muted-foreground mb-6">
              Create your first resume or import from LinkedIn or Markdown.
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/resumes/new"
                className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-primary/90"
              >
                Create Resume
              </Link>
              <Link
                href="/imports"
                className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-secondary/80"
              >
                Import
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid gap-3">
            {resumeList.map((resume) => (
              <div
                key={resume.id}
                className="border rounded-lg p-4 hover:border-primary transition-colors flex items-center justify-between cursor-pointer"
                onClick={() => router.push(`/resumes/${resume.id}`)}
              >
                <div>
                  <h3 className="font-medium">{resume.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {resume.target_job_title || "No target job"}
                    {resume.target_company && ` at ${resume.target_company}`}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">
                    {new Date(resume.updated_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={(e) => handleDelete(resume.id, e)}
                    className="text-xs text-destructive hover:underline"
                    aria-label={`Delete ${resume.title}`}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
