<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { userApi } from '../api/userApi'
import { departmentApi } from '../api/departmentApi'
import type { User, Department } from '../types'

const users = ref<User[]>([])
const departments = ref<Department[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingUser = ref<User | null>(null)

const formData = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  role: 'user',
  department_id: ''
})

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await userApi.list({ page_size: 100 })
    users.value = response.items
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    departments.value = await departmentApi.list()
  } catch (error) {
    console.error('Failed to load departments:', error)
  }
}

const openCreateModal = () => {
  editingUser.value = null
  formData.value = {
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'user',
    department_id: ''
  }
  showModal.value = true
}

const openEditModal = (user: User) => {
  editingUser.value = user
  formData.value = {
    username: user.username,
    email: user.email,
    password: '',
    full_name: user.full_name,
    role: user.role,
    department_id: user.department_id || ''
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
}

const saveUser = async () => {
  try {
    if (editingUser.value) {
      await userApi.update(editingUser.value.id, {
        email: formData.value.email,
        full_name: formData.value.full_name,
        role: formData.value.role as any,
        department_id: formData.value.department_id || null
      })
    } else {
      await userApi.create({
        username: formData.value.username,
        email: formData.value.email,
        password: formData.value.password,
        full_name: formData.value.full_name,
        role: formData.value.role,
        department_id: formData.value.department_id || undefined
      })
    }
    closeModal()
    loadUsers()
  } catch (error) {
    console.error('Failed to save user:', error)
    alert('Failed to save user. Please check your input.')
  }
}

const deleteUser = async (id: string) => {
  if (confirm('Are you sure you want to delete this user?')) {
    try {
      await userApi.delete(id)
      loadUsers()
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }
}

const toggleActive = async (user: User) => {
  try {
    if (user.is_active) {
      await userApi.deactivate(user.id)
    } else {
      await userApi.activate(user.id)
    }
    loadUsers()
  } catch (error) {
    console.error('Failed to toggle user status:', error)
  }
}

const getDeptName = (deptId: string | null) => {
  if (!deptId) return '-'
  const dept = departments.value.find(d => d.id === deptId)
  return dept?.name || '-'
}

onMounted(() => {
  loadUsers()
  loadDepartments()
})
</script>

<template>
  <div class="user-list">
    <div class="header">
      <h1>User Management</h1>
      <button class="btn btn-primary" @click="openCreateModal">Add User</button>
    </div>

    <div v-if="loading" class="card">Loading...</div>

    <div v-else class="card">
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Full Name</th>
            <th>Role</th>
            <th>Department</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.full_name }}</td>
            <td>{{ user.role }}</td>
            <td>{{ getDeptName(user.department_id) }}</td>
            <td>
              <span :class="['status', user.is_active ? 'active' : 'inactive']">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm" @click="openEditModal(user)">Edit</button>
              <button class="btn btn-sm" @click="toggleActive(user)">
                {{ user.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button class="btn btn-danger btn-sm" @click="deleteUser(user.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingUser ? 'Edit User' : 'Create User' }}</h2>
        <form @submit.prevent="saveUser">
          <div class="form-group" v-if="!editingUser">
            <label>Username</label>
            <input v-model="formData.username" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="formData.email" type="email" required />
          </div>
          <div class="form-group" v-if="!editingUser">
            <label>Password</label>
            <input v-model="formData.password" type="password" required />
          </div>
          <div class="form-group">
            <label>Full Name</label>
            <input v-model="formData.full_name" required />
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="formData.role">
              <option value="admin">Admin</option>
              <option value="user">User</option>
              <option value="guest">Guest</option>
            </select>
          </div>
          <div class="form-group">
            <label>Department</label>
            <select v-model="formData.department_id">
              <option value="">-- Select Department --</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  margin-right: 0.5rem;
}

.status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.status.active {
  background: #d4edda;
  color: #155724;
}

.status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.modal h2 {
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
