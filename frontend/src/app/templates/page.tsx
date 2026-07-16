"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { templates as templatesApi } from "@/services/api"
import { Header } from "@/components/layout/header"

interface TemplateItem {
  id: string
  name: string
  description?: string
  author?: string
  is_built_in: boolean
  is_shared: boolean
  category?: string
  created_at: string
}

export default function TemplatesPage() {
  const router = useRouter()
  const [templateList, setTemplateList] = useState<TemplateItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }
    loadTemplates()
  }, [router])

  const loadTemplates = async () => {
    try {
      const response = await templatesApi.list()
      setTemplateList(response.data)
    } catch {
      router.push("/login")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Templates</h1>
          <button
            onClick={() => document.getElementById("upload-template")?.click()}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-primary/90"
          >
            Upload Template
          </button>
          <input id="upload-template" type="file" accept=".zip" className="hidden" />
        </div>

        {loading ? (
          <p className="text-muted-foreground">Loading templates...</p>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {templateList.map((template) => (
              <div
                key={template.id}
                className="border rounded-lg p-4 hover:border-primary transition-colors cursor-pointer"
                onClick={() => router.push(`/templates/${template.id}`)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">{template.name}</h3>
                  {template.is_built_in && (
                    <span className="text-xs bg-secondary px-2 py-0.5 rounded">Built-in</span>
                  )}
                </div>
                {template.description && (
                  <p className="text-sm text-muted-foreground mb-2">{template.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{template.author || "Resume Builder"}</span>
                  <span>{template.category || "general"}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
