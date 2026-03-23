import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = !!token.value

  async function login(data: LoginRequest) {
    const response = await authApi.login(data)
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('token', response.data.access_token)
    return response.data
  }

  async function register(data: RegisterRequest) {
    const response = await authApi.register(data)
    return response.data
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await authApi.me()
      user.value = response.data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isAuthenticated, login, register, fetchUser, logout }
})
