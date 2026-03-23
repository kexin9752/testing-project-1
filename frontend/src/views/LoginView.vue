<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5">
    <a-card style="width: 400px">
      <template #title>
        <div style="text-align: center; font-size: 20px">金融交易监控系统</div>
      </template>
      <a-form :model="form" @finish="handleLogin">
        <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="用户名" size="large">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
          <a-input-password v-model:value="form.password" placeholder="密码" size="large">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">登录</a-button>
        </a-form-item>
        <div style="text-align: center">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </div>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(form)
    message.success('登录成功')
    router.push('/dashboard')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
