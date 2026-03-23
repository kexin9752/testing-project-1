<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px">
      <a-col :span="6">
        <a-select v-model:value="filters.asset" placeholder="选择账户" style="width: 100%" allow-clear @change="handleFilterChange">
          <a-select-option value="BTC">BTC</a-select-option>
          <a-select-option value="ETH">ETH</a-select-option>
          <a-select-option value="USD">USD</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="6">
        <a-select v-model:value="filters.type" placeholder="交易类型" style="width: 100%" allow-clear @change="handleFilterChange">
          <a-select-option value="buy">买入</a-select-option>
          <a-select-option value="sell">卖出</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="12">
        <a-range-picker v-model:value="filters.dateRange" style="width: 100%" @change="handleFilterChange" />
      </a-col>
    </a-row>

    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card>
          <a-statistic title="总交易笔数" :value="stats.totalTransactions" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="总买入" :value="stats.totalBuy" suffix="笔" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="总卖出" :value="stats.totalSell" suffix="笔" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="累计交易额" :value="stats.totalAmount" prefix="$" />
        </a-card>
      </a-col>
    </a-row>

    <a-card title="交易趋势">
      <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999">
        图表区域 (ECharts)
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, computed } from 'vue'
import { useTransactionStore } from '@/stores/transaction'
import { storeToRefs } from 'pinia'
import type { Dayjs } from 'dayjs'

const transactionStore = useTransactionStore()
const { transactions, total } = storeToRefs(transactionStore)

const filters = reactive({
  asset: undefined as string | undefined,
  type: undefined as string | undefined,
  dateRange: null as [Dayjs, Dayjs] | null
})

onMounted(() => {
  transactionStore.fetchTransactions({ page_size: 100 })
})

function handleFilterChange() {
  transactionStore.fetchTransactions({
    page: 1,
    asset: filters.asset,
    type: filters.type
  })
}

const stats = computed(() => {
  const txs = transactions.value
  return {
    totalTransactions: txs.length,
    totalBuy: txs.filter((t) => t.type === 'buy').length,
    totalSell: txs.filter((t) => t.type === 'sell').length,
    totalAmount: txs.reduce((sum, t) => sum + t.amount * t.price, 0)
  }
})
</script>
