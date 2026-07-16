"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { imports as importsApi } from "@/services/api"
import { Header } from "@/components/layout/header"

export default function ImportsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<"linkedin" | "markdown">("linkedin")
  const [linkedinData, setLinkedinData] = useState("")
  const [markdownContent, setMarkdownContent] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [result, setResult] = useState<{ import_id: string; message: string } | null>(null)

  const handleLinkedInSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!linkedinData.trim()) {
      setError("Please paste your LinkedIn data")
      return
    }
    setLoading(true)
    setError("")
    try {
      const response = await importsApi.linkedin({ linkedin_data: linkedinData })
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Import failed")
    } finally {
      setLoading(false)
    }
  }

  const handleMarkdownSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!markdownContent.trim()) {
      setError("Please enter Markdown content")
      return
    }
    setLoading(true)
    setError("")
    try {
      const response = await importsApi.markdown({ content: markdownContent })
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Import failed")
    } finally {
      setLoading(false)
    }
  }

  const handleMarkdownFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError("")
    try {
      const formData = new FormData()
      formData.append("file", file)
      const response = await importsApi.markdown(formData)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Import failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Import Resume Data</h1>

        <div className="border-b mb-6">
          <div className="flex gap-4">
            <button
              onClick={() => { setActiveTab("linkedin"); setResult(null); setError("") }}
              className={`pb-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "linkedin"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground"
              }`}
            >
              LinkedIn
            </button>
            <button
              onClick={() => { setActiveTab("markdown"); setResult(null); setError("") }}
              className={`pb-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "markdown"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground"
              }`}
            >
              Markdown
            </button>
          </div>
        </div>

        {result ? (
          <div className="border rounded-lg p-6 text-center">
            <div className="text-3xl mb-2">📥</div>
            <h2 className="font-semibold mb-2">Import Queued</h2>
            <p className="text-sm text-muted-foreground mb-4">{result.message}</p>
            <p className="text-xs text-muted-foreground mb-4">Import ID: {result.import_id}</p>
            <button
              onClick={() => router.push(`/imports/${result.import_id}`)}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm"
            >
              View Status
            </button>
          </div>
        ) : activeTab === "linkedin" ? (
          <form onSubmit={handleLinkedInSubmit} className="space-y-4">
            <div>
              <label htmlFor="linkedinData" className="block text-sm font-medium mb-1">
                Paste LinkedIn Profile Data
              </label>
              <textarea
                id="linkedinData"
                value={linkedinData}
                onChange={(e) => setLinkedinData(e.target.value)}
                className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[200px]"
                placeholder="Paste your LinkedIn profile information here..."
              />
            </div>
            <p className="text-xs text-muted-foreground">
              You can paste text from your LinkedIn profile or upload a LinkedIn data export.
            </p>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground py-2 rounded-md font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {loading ? "Processing..." : "Import LinkedIn Data"}
            </button>
          </form>
        ) : (
          <div className="space-y-6">
            <form onSubmit={handleMarkdownSubmit} className="space-y-4">
              <div>
                <label htmlFor="markdownContent" className="block text-sm font-medium mb-1">
                  Paste Markdown Resume
                </label>
                <textarea
                  id="markdownContent"
                  value={markdownContent}
                  onChange={(e) => setMarkdownContent(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono min-h-[300px]"
                  placeholder={`# Full Name\n\n## Professional Summary\n...`}
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary text-primary-foreground py-2 rounded-md font-medium hover:bg-primary/90 disabled:opacity-50"
              >
                {loading ? "Processing..." : "Import Markdown"}
              </button>
            </form>

            <div className="border-t pt-6">
              <p className="text-sm text-muted-foreground mb-2">Or upload a .md file:</p>
              <input
                type="file"
                accept=".md"
                onChange={handleMarkdownFileUpload}
                className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:bg-secondary file:text-secondary-foreground hover:file:bg-secondary/80"
              />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
