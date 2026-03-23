<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px">
      <a-col :span="4">
        <a-select v-model:value="searchFilters.asset" placeholder="账户" style="width: 100%" allow-clear @change="handleSearch">
          <a-select-option value="BTC">BTC</a-select-option>
          <a-select-option value="ETH">ETH</a-select-option>
          <a-select-option value="USD">USD</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="4">
        <a-select v-model:value="searchFilters.type" placeholder="类型" style="width: 100%" allow-clear @change="handleSearch">
          <a-select-option value="buy">买入</a-select-option>
          <a-select-option value="sell">卖出</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="4">
        <a-select v-model:value="searchFilters.status" placeholder="状态" style="width: 100%" allow-clear @change="handleSearch">
          <a-select-option value="pending">待处理</a-select-option>
          <a-select-option value="completed">已完成</a-select-option>
          <a-select-option value="cancelled">已取消</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="4">
        <a-button type="primary" @click="goToCreate">新建交易</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="transactions" :columns="columns" :loading="loading" :pagination="pagination" @change="handleTableChange" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'type'">
          <a-tag :color="record.type === 'buy' ? 'green' : 'red'">{{ record.type === 'buy' ? '买入' : '卖出' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="statusColor[record.status]">{{ statusText[record.status] }}</a-tag>
        </template>
        <template v-else-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTransactionStore } from '@/stores/transaction'
import { storeToRefs } from 'pinia'
import dayjs from 'dayjs'

const router = useRouter()
const transactionStore = useTransactionStore()
const { transactions, total, page, pageSize, loading } = storeToRefs(transactionStore)

const searchFilters = reactive({
  asset: undefined as string | undefined,
  type: undefined as string | undefined,
  status: undefined as string | undefined
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 200 },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '资产', dataIndex: 'asset', key: 'asset' },
  { title: '数量', dataIndex: 'amount', key: 'amount' },
  { title: '价格', dataIndex: 'price', key: 'price' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '时间', dataIndex: 'created_at', key: 'created_at' }
]

const pagination = reactive({
  current: page,
  pageSize: pageSize,
  total: total,
  showSizeChanger: true,
  showTotal: (t: number) => `共 ${t} 条`
})

const statusColor: Record<string, string> = {
  pending: 'orange',
  completed: 'green',
  cancelled: 'grey'
}

const statusText: Record<string, string> = {
  pending: '待处理',
  completed: '已完成',
  cancelled: '已取消'
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  transactionStore.fetchTransactions()
})

function handleSearch() {
  transactionStore.fetchTransactions({ page: 1, ...searchFilters })
}

function handleTableChange(pag: any) {
  transactionStore.fetchTransactions({ page: pag.current, page_size: pag.pageSize, ...searchFilters })
}

function goToCreate() {
  router.push('/transactions/new')
}
</script>
