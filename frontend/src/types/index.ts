export interface User {
  id: string
  username: string
  email: string
  full_name: string
  role: 'admin' | 'user' | 'guest'
  department_id: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Department {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

export interface UserListResponse {
  total: number
  page: number
  page_size: number
  items: User[]
}

export interface Stats {
  total: number
  active: number
  inactive: number
}
