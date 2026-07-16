"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { jobs as jobsApi } from "@/services/api"
import { Header } from "@/components/layout/header"

export default function NewJobPage() {
  const router = useRouter()
  const [title, setTitle] = useState("")
  const [company, setCompany] = useState("")
  const [description, setDescription] = useState("")
  const [requiredQuals, setRequiredQuals] = useState("")
  const [preferredQuals, setPreferredQuals] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      setError("Job title is required")
      return
    }
    setLoading(true)
    setError("")
    try {
      const response = await jobsApi.create({
        title: title.trim(),
        company_name: company.trim() || undefined,
        job_description: description.trim() || undefined,
        required_qualifications: requiredQuals.split("\n").filter(Boolean).map((s) => s.trim()),
        preferred_qualifications: preferredQuals.split("\n").filter(Boolean).map((s) => s.trim()),
      })
      router.push(`/jobs/${response.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create job")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Add Job Description</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium mb-1">
              Job Title *
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="e.g., Senior Software Engineer"
              required
            />
          </div>
          <div>
            <label htmlFor="company" className="block text-sm font-medium mb-1">
              Company
            </label>
            <input
              id="company"
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="e.g., Tech Corp"
            />
          </div>
          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-1">
              Job Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[150px]"
              placeholder="Paste the full job description here..."
            />
          </div>
          <div>
            <label htmlFor="requiredQuals" className="block text-sm font-medium mb-1">
              Required Qualifications (one per line)
            </label>
            <textarea
              id="requiredQuals"
              value={requiredQuals}
              onChange={(e) => setRequiredQuals(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
              placeholder="Python&#10;5+ years experience&#10;React"
            />
          </div>
          <div>
            <label htmlFor="preferredQuals" className="block text-sm font-medium mb-1">
              Preferred Qualifications (one per line)
            </label>
            <textarea
              id="preferredQuals"
              value={preferredQuals}
              onChange={(e) => setPreferredQuals(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
              placeholder="Kubernetes&#10;AWS&#10;GraphQL"
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
            {loading ? "Saving..." : "Save Job Description"}
          </button>
        </form>
      </main>
    </div>
  )
}
