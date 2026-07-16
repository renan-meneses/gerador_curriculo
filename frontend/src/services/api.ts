import axios, { AxiosError, InternalAxiosRequestConfig } from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token")
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem("refresh_token")
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token } = response.data
          localStorage.setItem("access_token", access_token)
          localStorage.setItem("refresh_token", refresh_token)
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return api(originalRequest)
        }
      } catch {
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        if (typeof window !== "undefined") {
          window.location.href = "/login"
        }
      }
    }
    return Promise.reject(error)
  }
)

declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retry?: boolean
  }
}

export const auth = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
  refresh: (data: { refresh_token: string }) =>
    api.post("/auth/refresh", data),
}

export const resumes = {
  list: () => api.get("/resumes"),
  get: (id: string) => api.get(`/resumes/${id}`),
  create: (data: any) => api.post("/resumes", data),
  delete: (id: string) => api.delete(`/resumes/${id}`),
  duplicate: (id: string) => api.post(`/resumes/${id}/duplicate`),
}

export const jobs = {
  list: () => api.get("/jobs"),
  get: (id: string) => api.get(`/jobs/${id}`),
  create: (data: any) => api.post("/jobs", data),
  analyze: (id: string) => api.post(`/jobs/${id}/analyze`),
}

export const templates = {
  list: () => api.get("/templates"),
  get: (id: string) => api.get(`/templates/${id}`),
  create: (data: any) => api.post("/templates", data),
  delete: (id: string) => api.delete(`/templates/${id}`),
}

export const imports = {
  linkedin: (data: any) => api.post("/imports/linkedin", data),
  linkedinExport: (file: File) => {
    const formData = new FormData()
    formData.append("file", file)
    return api.post("/imports/linkedin-export", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  },
  markdown: (data: any) => api.post("/imports/markdown", data),
  status: (id: string) => api.get(`/imports/${id}/status`),
  confirm: (id: string, data: any) => api.post(`/imports/${id}/confirm`, data),
}

export const exports_api = {
  pdf: (data: any) => api.post("/exports/pdf", data),
  docx: (data: any) => api.post("/exports/docx", data),
  markdown: (data: any) => api.post("/exports/markdown", data),
  html: (data: any) => api.post("/exports/html", data),
  status: (id: string) => api.get(`/exports/${id}/status`),
  download: (id: string) => api.get(`/exports/${id}/download`),
}

export const ai = {
  suggestions: (analysisId: string) => api.get(`/ai-suggestions/${analysisId}`),
  accept: (suggestionId: string) =>
    api.post(`/ai-suggestions/${suggestionId}/accept`),
  reject: (suggestionId: string) =>
    api.post(`/ai-suggestions/${suggestionId}/reject`),
  edit: (suggestionId: string, data: any) =>
    api.post(`/ai-suggestions/${suggestionId}/edit`, data),
}
