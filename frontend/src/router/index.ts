import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import UserList from '../views/UserList.vue'
import Login from '../views/Login.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/users',
      name: 'users',
      component: UserList
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    }
  ]
})

export default router
