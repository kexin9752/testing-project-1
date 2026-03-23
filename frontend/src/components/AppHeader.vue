<template>
  <a-layout-header style="background: #001529; padding: 0 24px; display: flex; align-items: center; justify-content: space-between">
    <div style="color: white; font-size: 18px; font-weight: bold">金融交易监控系统</div>
    <a-dropdown>
      <a-avatar style="cursor: pointer">{{ user?.username?.[0]?.toUpperCase() }}</a-avatar>
      <template #overlay>
        <a-menu>
          <a-menu-item key="profile">
            <a-space direction="vertical" style="width: 100%">
              <div>{{ user?.username }}</div>
              <div style="font-size: 12px; color: #999">{{ user?.email }}</div>
            </a-space>
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item key="logout" @click="handleLogout">退出登录</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </a-layout-header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
