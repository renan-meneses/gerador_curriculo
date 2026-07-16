"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { resumes as resumesApi } from "@/services/api"
import { Header } from "@/components/layout/header"

export default function NewResumePage() {
  const router = useRouter()
  const [title, setTitle] = useState("")
  const [targetJobTitle, setTargetJobTitle] = useState("")
  const [targetCompany, setTargetCompany] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      setError("Title is required")
      return
    }
    setLoading(true)
    setError("")
    try {
      const response = await resumesApi.create({
        title: title.trim(),
        target_job_title: targetJobTitle.trim() || undefined,
        target_company: targetCompany.trim() || undefined,
      })
      router.push(`/resumes/${response.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create resume")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8 max-w-lg mx-auto">
        <h1 className="text-2xl font-bold mb-6">New Resume</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium mb-1">
              Resume Title *
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="e.g., Software Engineer Resume"
              required
            />
          </div>
          <div>
            <label htmlFor="targetJob" className="block text-sm font-medium mb-1">
              Target Job Title
            </label>
            <input
              id="targetJob"
              type="text"
              value={targetJobTitle}
              onChange={(e) => setTargetJobTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="e.g., Senior Software Engineer"
            />
          </div>
          <div>
            <label htmlFor="targetCompany" className="block text-sm font-medium mb-1">
              Target Company
            </label>
            <input
              id="targetCompany"
              type="text"
              value={targetCompany}
              onChange={(e) => setTargetCompany(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="e.g., Tech Corp"
            />
          </div>
          {error && (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-primary-foreground py-2 rounded-md font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Creating..." : "Create Resume"}
          </button>
        </form>
      </main>
    </div>
  )
}
