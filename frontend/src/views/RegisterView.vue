<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5">
    <a-card style="width: 400px">
      <template #title>
        <div style="text-align: center; font-size: 20px">用户注册</div>
      </template>
      <a-form :model="form" @finish="handleRegister">
        <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="用户名" size="large">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="email" :rules="[{ required: true, type: 'email', message: '请输入有效邮箱' }]">
          <a-input v-model:value="form.email" placeholder="邮箱" size="large">
            <template #prefix><MailOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="full_name" :rules="[{ required: true, message: '请输入姓名' }]">
          <a-input v-model:value="form.full_name" placeholder="姓名" size="large">
            <template #prefix><IdcardOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="password" :rules="[{ required: true, min: 8, message: '密码至少8位' }]">
          <a-input-password v-model:value="form.password" placeholder="密码" size="large">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">注册</a-button>
        </a-form-item>
        <div style="text-align: center">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, MailOutlined, IdcardOutlined } from '@ant-design/icons-vue'
import { authApi } from '@/api'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  full_name: '',
  password: ''
})

async function handleRegister() {
  loading.value = true
  try {
    await authApi.register(form)
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>
