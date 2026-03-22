<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi } from '../api/userApi'
import type { Stats } from '../types'

const stats = ref<Stats | null>(null)

const loadStats = async () => {
  try {
    stats.value = await userApi.getStats()
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div class="dashboard">
    <h1>Dashboard</h1>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Users</h3>
        <div class="value">{{ stats?.total ?? '-' }}</div>
      </div>
      <div class="stat-card">
        <h3>Active Users</h3>
        <div class="value">{{ stats?.active ?? '-' }}</div>
      </div>
      <div class="stat-card">
        <h3>Inactive Users</h3>
        <div class="value">{{ stats?.inactive ?? '-' }}</div>
      </div>
    </div>

    <div class="card">
      <h2>Welcome to User Management System</h2>
      <p>This system provides complete user management functionality including:</p>
      <ul style="margin-top: 1rem; margin-left: 1.5rem;">
        <li>User CRUD operations</li>
        <li>Department management</li>
        <li>User activation/deactivation</li>
        <li>Search and filtering</li>
        <li>RESTful API with OpenAPI documentation</li>
      </ul>
    </div>
  </div>
</template>
