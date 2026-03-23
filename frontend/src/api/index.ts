import axios from 'axios'
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Transaction,
  TransactionCreate,
  TransactionListResponse,
  Report,
  ReportGenerateRequest,
  ReportListResponse
} from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<AuthResponse>('/auth/login', data),
  register: (data: RegisterRequest) =>
    api.post<AuthResponse>('/auth/register', data),
  me: () => api.get('/auth/me')
}

export const transactionApi = {
  list: (params: {
    page?: number
    page_size?: number
    asset?: string
    type?: string
    status?: string
  }) => api.get<TransactionListResponse>('/transactions', { params }),
  create: (data: TransactionCreate) =>
    api.post<Transaction>('/transactions', data),
  get: (id: string) => api.get<Transaction>(`/transactions/${id}`),
  update: (id: string, data: { status: string }) =>
    api.patch<Transaction>(`/transactions/${id}`, data)
}

export const reportApi = {
  list: () => api.get<ReportListResponse>('/reports'),
  generate: (data: ReportGenerateRequest) =>
    api.post<Report>('/reports/generate', data),
  download: (id: string) => `/api/v1/reports/${id}/download`
}

export default api
