<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  // Simple mock login - in production this would call the API
  if (username.value === 'admin' && password.value === 'admin123') {
    alert('Login successful! (Demo mode)')
  } else {
    error.value = 'Invalid credentials. Try admin/admin123'
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Login</h1>
      <p class="subtitle">User Management System</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" placeholder="Enter username" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="Enter password" required />
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <button type="submit" class="btn btn-primary btn-block">Login</button>
      </form>

      <div class="hint">
        <p>Demo credentials: admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
}

.login-card h1 {
  text-align: center;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.error {
  background: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.btn-block {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
}

.hint {
  margin-top: 1.5rem;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}
</style>
