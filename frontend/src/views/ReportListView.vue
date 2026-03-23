<template>
  <div>
    <a-row style="margin-bottom: 16px" justify="end">
      <a-col>
        <a-button type="primary" @click="showGenerateModal = true">生成报表</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="reports" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'type'">
          <a-tag>{{ typeText[record.type] }}</a-tag>
        </template>
        <template v-else-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" :href="getDownloadUrl(record.id)" :disabled="!record.file_path">下载</a-button>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="showGenerateModal" title="生成报表" @ok="handleGenerate">
      <a-form :model="generateForm" layout="vertical">
        <a-form-item label="报表名称" name="name" :rules="[{ required: true, message: '请输入报表名称' }]">
          <a-input v-model:value="generateForm.name" placeholder="请输入报表名称" />
        </a-form-item>
        <a-form-item label="报表类型" name="type" :rules="[{ required: true, message: '请选择报表类型' }]">
          <a-select v-model:value="generateForm.type" placeholder="请选择">
            <a-select-option value="daily">日报</a-select-option>
            <a-select-option value="monthly">月报</a-select-option>
            <a-select-option value="quarterly">季报</a-select-option>
            <a-select-option value="yearly">年报</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useReportStore } from '@/stores/report'
import { storeToRefs } from 'pinia'
import dayjs from 'dayjs'

const reportStore = useReportStore()
const { reports, loading } = storeToRefs(reportStore)

const showGenerateModal = ref(false)
const generateLoading = ref(false)

const generateForm = reactive({
  name: '',
  type: undefined as string | undefined
})

const columns = [
  { title: '报表名称', dataIndex: 'name', key: 'name' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '生成时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action' }
]

const typeText: Record<string, string> = {
  daily: '日报',
  monthly: '月报',
  quarterly: '季报',
  yearly: '年报'
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

function getDownloadUrl(id: string) {
  return reportStore.getDownloadUrl(id)
}

onMounted(() => {
  reportStore.fetchReports()
})

async function handleGenerate() {
  if (!generateForm.name || !generateForm.type) {
    message.error('请填写完整信息')
    return
  }
  generateLoading.value = true
  try {
    await reportStore.generateReport({
      name: generateForm.name,
      type: generateForm.type as any
    })
    message.success('生成成功')
    showGenerateModal.value = false
    generateForm.name = ''
    generateForm.type = undefined
    reportStore.fetchReports()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '生成失败')
  } finally {
    generateLoading.value = false
  }
}
</script>
