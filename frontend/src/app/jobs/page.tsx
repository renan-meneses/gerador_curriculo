"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { jobs as jobsApi } from "@/services/api"
import { Header } from "@/components/layout/header"

interface JobSummary {
  id: string
  title: string
  company_name?: string
  industry?: string
  seniority_level?: string
  created_at: string
}

export default function JobsPage() {
  const router = useRouter()
  const [jobList, setJobList] = useState<JobSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }
    loadJobs()
  }, [router])

  const loadJobs = async () => {
    try {
      const response = await jobsApi.list()
      setJobList(response.data)
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
          <h1 className="text-3xl font-bold">Job Descriptions</h1>
          <Link
            href="/jobs/new"
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-primary/90"
          >
            Add Job
          </Link>
        </div>

        {loading ? (
          <p className="text-muted-foreground">Loading jobs...</p>
        ) : jobList.length === 0 ? (
          <div className="border rounded-lg p-12 text-center">
            <h2 className="text-xl font-semibold mb-2">No job descriptions yet</h2>
            <p className="text-muted-foreground mb-6">
              Add a job description to tailor your resume.
            </p>
            <Link
              href="/jobs/new"
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-primary/90"
            >
              Add Job Description
            </Link>
          </div>
        ) : (
          <div className="grid gap-3">
            {jobList.map((job) => (
              <div
                key={job.id}
                className="border rounded-lg p-4 hover:border-primary transition-colors cursor-pointer"
                onClick={() => router.push(`/jobs/${job.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">{job.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {job.company_name} {job.industry && `· ${job.industry}`}
                      {job.seniority_level && ` · ${job.seniority_level}`}
                    </p>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(job.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
