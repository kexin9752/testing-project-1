<template>
  <div style="max-width: 600px">
    <a-card title="新建交易">
      <a-form :model="form" layout="vertical" @finish="handleSubmit">
        <a-form-item label="交易类型" name="type" :rules="[{ required: true, message: '请选择交易类型' }]">
          <a-select v-model:value="form.type" placeholder="请选择">
            <a-select-option value="buy">买入</a-select-option>
            <a-select-option value="sell">卖出</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="资产" name="asset" :rules="[{ required: true, message: '请输入资产' }]">
          <a-select v-model:value="form.asset" placeholder="请选择资产">
            <a-select-option value="BTC">BTC</a-select-option>
            <a-select-option value="ETH">ETH</a-select-option>
            <a-select-option value="USD">USD</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="数量" name="amount" :rules="[{ required: true, message: '请输入数量' }, { type: 'number', min: 0.0001, message: '数量必须大于0' }]">
          <a-input-number v-model:value="form.amount" style="width: 100%" :min="0" :precision="4" />
        </a-form-item>

        <a-form-item label="价格" name="price" :rules="[{ required: true, message: '请输入价格' }, { type: 'number', min: 0, message: '价格必须大于等于0' }]">
          <a-input-number v-model:value="form.price" style="width: 100%" :min="0" :precision="2" prefix="$" />
        </a-form-item>

        <a-form-item label="交易时间" name="trade_time" :rules="[{ required: true, message: '请选择交易时间' }]">
          <a-date-picker v-model:value="form.trade_time" style="width: 100%" show-time format="YYYY-MM-DD HH:mm:ss" />
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button type="primary" html-type="submit" :loading="loading">提交</a-button>
            <a-button @click="router.push('/transactions')">取消</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useTransactionStore } from '@/stores/transaction'
import dayjs from 'dayjs'

const router = useRouter()
const transactionStore = useTransactionStore()
const loading = ref(false)

const form = reactive({
  type: undefined as 'buy' | 'sell' | undefined,
  asset: undefined as string | undefined,
  amount: 0,
  price: 0,
  trade_time: null as dayjs.Dayjs | null
})

async function handleSubmit() {
  if (!form.type || !form.asset || !form.trade_time) {
    message.error('请填写完整信息')
    return
  }
  loading.value = true
  try {
    await transactionStore.createTransaction({
      type: form.type,
      asset: form.asset,
      amount: form.amount,
      price: form.price,
      trade_time: form.trade_time.format('YYYY-MM-DDTHH:mm:ss')
    })
    message.success('创建成功')
    router.push('/transactions')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建失败')
  } finally {
    loading.value = false
  }
}
</script>
