import client from './client'
import type { Department } from '../types'

export const departmentApi = {
  list: async () => {
    const response = await client.get<Department[]>('/departments')
    return response.data
  },

  get: async (id: string) => {
    const response = await client.get<Department>(`/departments/${id}`)
    return response.data
  },

  create: async (data: { name: string; description?: string }) => {
    const response = await client.post<Department>('/departments', data)
    return response.data
  },

  update: async (id: string, data: { name?: string; description?: string }) => {
    const response = await client.put<Department>(`/departments/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    await client.delete(`/departments/${id}`)
  }
}
