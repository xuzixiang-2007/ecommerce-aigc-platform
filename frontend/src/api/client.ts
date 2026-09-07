import axios from 'axios'

// 后端 API 地址
const API_BASE = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // AIGC 生成可能较慢
})

// ===== 类型定义 =====

export interface Task {
  id: number
  merchant_id: number
  product_name: string
  product_category: string
  prompt: string | null
  status: string
  created_at: string | null
}

export interface GenerateResult {
  task_id: number
  status: string
  message: string
  image?: {
    id: number
    image_url: string | null
    image_hash: string
    phash: string
  }
  compliance?: {
    content_safety: string
    copyright_check: string
    spec_check: string
    score: number
    passed: boolean
  }
  certificate?: {
    id: number
    certificate_no: string
    tx_hash: string
    block_number: number
  }
}

export interface Certificate {
  id: number
  task_id: number
  image_hash: string
  phash: string | null
  tx_hash: string | null
  block_number: number | null
  certificate_no: string | null
  timestamp: string | null
  created_at: string | null
}

export interface VerifyResult {
  verified: boolean
  certificate: Certificate | null
  message: string
}

export interface StatsData {
  overview: {
    total_tasks: number
    total_certified: number
    total_failed: number
    total_pending: number
    total_merchants: number
    total_certificates: number
    total_images: number
  }
  compliance: {
    total: number
    passed: number
    failed: number
    pass_rate: number
    avg_score: number
  }
  status_dist: { name: string; value: number }[]
  category_dist: { name: string; value: number }[]
  daily_trend: { date: string; count: number }[]
  daily_cert_trend: { date: string; count: number }[]
}

// ===== API 方法 =====

export const taskApi = {
  create: (data: { merchant_id: number; product_name: string; product_category?: string; prompt?: string }) =>
    api.post<Task>('/api/tasks', data),

  list: () => api.get<Task[]>('/api/tasks'),

  get: (id: number) => api.get<Task>(`/api/tasks/${id}`),

  generate: (id: number) => api.post<GenerateResult>(`/api/tasks/${id}/generate`),
}

export const certificateApi = {
  list: () => api.get<Certificate[]>('/api/certificates'),

  verify: (image_hash: string) => api.post<VerifyResult>('/api/verify', { image_hash }),
}

// 别名（兼容不同页面用法）
export const certApi = certificateApi

export const merchantApi = {
  list: () => api.get('/api/merchants'),
}

export const statsApi = {
  get: () => api.get<StatsData>('/api/stats'),
}

export interface AuthResponse {
  token: string
  merchant_id: number
  name: string
  phone: string
}

export const authApi = {
  register: (data: { name: string; phone: string; password: string; email?: string }) =>
    api.post<AuthResponse>('/api/auth/register', data),
  login: (data: { phone: string; password: string }) =>
    api.post<AuthResponse>('/api/auth/login', data),
}

// ===== AIGC 识别 =====

export interface DetectionIndicator {
  name: string
  score: number
  desc: string
}

export interface DetectionResult {
  is_aigc: boolean
  confidence: number
  label: string
  indicators: DetectionIndicator[]
  image_hash: string
  image_size: string
  details: string
  detected_at: string
}

export interface DetectionRecord {
  id: number
  image_hash: string
  is_aigc: boolean
  confidence: number
  label: string
  created_at: string | null
}

export const detectionApi = {
  detect: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<DetectionResult>('/api/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  records: () => api.get<DetectionRecord[]>('/api/detect/records'),
}

export default api
