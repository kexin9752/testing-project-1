export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export type TransactionType = 'buy' | 'sell'
export type TransactionStatus = 'pending' | 'completed' | 'cancelled'

export interface Transaction {
  id: string
  user_id: string
  type: TransactionType
  asset: string
  amount: number
  price: number
  status: TransactionStatus
  created_at: string
}

export interface TransactionCreate {
  type: TransactionType
  asset: string
  amount: number
  price: number
  trade_time?: string
}

export interface TransactionListResponse {
  total: number
  page: number
  page_size: number
  items: Transaction[]
}

export type ReportType = 'daily' | 'monthly' | 'quarterly' | 'yearly'

export interface Report {
  id: string
  user_id: string
  name: string
  type: ReportType
  file_path: string | null
  created_at: string
}

export interface ReportGenerateRequest {
  name: string
  type: ReportType
}

export interface ReportListResponse {
  total: number
  items: Report[]
}

export interface MenuItem {
  key: string
  label: string
  icon?: string
  children?: MenuItem[]
}
