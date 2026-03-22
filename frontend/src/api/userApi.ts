import client from './client'
import type { User, UserListResponse, Stats } from '../types'

export const userApi = {
  list: async (params?: { page?: number; page_size?: number; search?: string }) => {
    const response = await client.get<UserListResponse>('/users', { params })
    return response.data
  },

  get: async (id: string) => {
    const response = await client.get<User>(`/users/${id}`)
    return response.data
  },

  create: async (data: {
    username: string
    email: string
    password: string
    full_name: string
    role?: string
    department_id?: string
  }) => {
    const response = await client.post<User>('/users', data)
    return response.data
  },

  update: async (id: string, data: Partial<User>) => {
    const response = await client.put<User>(`/users/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    await client.delete(`/users/${id}`)
  },

  activate: async (id: string) => {
    const response = await client.post<User>(`/users/${id}/activate`)
    return response.data
  },

  deactivate: async (id: string) => {
    const response = await client.post<User>(`/users/${id}/deactivate`)
    return response.data
  },

  getStats: async () => {
    const response = await client.get<Stats>('/stats/users/count')
    return response.data
  }
}
