import { defineStore } from 'pinia'
import { ref } from 'vue'
import { transactionApi } from '@/api'
import type { Transaction, TransactionCreate } from '@/types'

export const useTransactionStore = defineStore('transaction', () => {
  const transactions = ref<Transaction[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)

  async function fetchTransactions(params?: {
    page?: number
    page_size?: number
    asset?: string
    type?: string
    status?: string
  }) {
    loading.value = true
    try {
      const response = await transactionApi.list({
        page: params?.page ?? page.value,
        page_size: params?.page_size ?? pageSize.value,
        ...params
      })
      transactions.value = response.data.items
      total.value = response.data.total
      page.value = response.data.page
      pageSize.value = response.data.page_size
    } finally {
      loading.value = false
    }
  }

  async function createTransaction(data: TransactionCreate) {
    const response = await transactionApi.create(data)
    return response.data
  }

  return { transactions, total, page, pageSize, loading, fetchTransactions, createTransaction }
})
