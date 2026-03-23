<template>
  <a-layout style="height: 100vh">
    <AppSider :menus="menus" v-model:collapsed="collapsed" />
    <a-layout>
      <AppHeader />
      <a-layout-content style="padding: 24px; overflow-y: auto">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSider from './AppSider.vue'
import type { MenuItem } from '@/types'

const collapsed = ref(false)

const menus: MenuItem[] = [
  {
    key: 'monitor',
    label: '监控',
    children: [
      {
        key: 'dashboard',
        label: '实时大盘',
        children: [
          { key: 'dashboard-overview', label: '概览' },
          { key: 'dashboard-detail', label: '详情' }
        ]
      },
      {
        key: 'alerts',
        label: '告警中心',
        children: [
          { key: 'alerts-list', label: '告警列表' },
          { key: 'alerts-rules', label: '告警规则' }
        ]
      }
    ]
  },
  {
    key: 'trade',
    label: '交易',
    children: [
      { key: 'transactions', label: '交易记录' },
      { key: 'transactions-new', label: '下单' }
    ]
  },
  {
    key: 'report',
    label: '报表',
    children: [
      {
        key: 'reports',
        label: '报表中心',
        children: [
          { key: 'reports-monthly', label: '月报' },
          { key: 'reports-quarterly', label: '季报' },
          { key: 'reports-yearly', label: '年报' }
        ]
      },
      { key: 'reports-export', label: '导出' }
    ]
  }
]
</script>
