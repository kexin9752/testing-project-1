import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reportApi } from '@/api'
import type { Report, ReportGenerateRequest } from '@/types'

export const useReportStore = defineStore('report', () => {
  const reports = ref<Report[]>([])
  const loading = ref(false)

  async function fetchReports() {
    loading.value = true
    try {
      const response = await reportApi.list()
      reports.value = response.data.items
    } finally {
      loading.value = false
    }
  }

  async function generateReport(data: ReportGenerateRequest) {
    const response = await reportApi.generate(data)
    return response.data
  }

  function getDownloadUrl(id: string) {
    return reportApi.download(id)
  }

  return { reports, loading, fetchReports, generateReport, getDownloadUrl }
})
