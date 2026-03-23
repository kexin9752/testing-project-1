<template>
  <a-layout-sider v-model:collapsed="collapsed" :trigger="null" collapsible style="overflow: auto">
    <div v-if="!collapsed" style="height: 64px; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: bold; border-bottom: 1px solid #ffffff20">
      FinanceTrade
    </div>
    <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline" :items="menuItems" @click="handleMenuClick" />
  </a-layout-sider>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuProps } from 'ant-design-vue'
import type { MenuItem } from '@/types'

const props = defineProps<{
  menus: MenuItem[]
  collapsed: boolean
}>()

const router = useRouter()
const route = useRoute()
const selectedKeys = ref<string[]>([route.name as string])

function buildMenuItems(menus: MenuItem[]): MenuProps['items'] {
  return menus.map((menu) => {
    if (menu.children) {
      return {
        key: menu.key,
        label: menu.label,
        children: buildMenuItems(menu.children)
      }
    }
    return {
      key: menu.key,
      label: menu.label
    }
  })
}

const menuItems = ref<MenuProps['items']>([])

watch(
  () => props.menus,
  (newMenus) => {
    menuItems.value = buildMenuItems(newMenus)
  },
  { immediate: true }
)

function handleMenuClick({ key }: { key: string }) {
  const routeMap: Record<string, string> = {
    'dashboard-overview': '/dashboard',
    'dashboard-detail': '/dashboard',
    'dashboard': '/dashboard',
    'transactions': '/transactions',
    'transactions-new': '/transactions/new',
    'reports': '/reports',
    'reports-monthly': '/reports',
    'reports-quarterly': '/reports',
    'reports-yearly': '/reports',
    'reports-export': '/reports',
    'alerts-list': '/dashboard',
    'alerts-rules': '/dashboard'
  }
  const path = routeMap[key]
  if (path) {
    router.push(path)
  }
}
</script>
