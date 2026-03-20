import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import SpecificationsView from '../views/SpecificationsView.vue'
import VersionsView from '../views/VersionsView.vue'
import RelationsView from '../views/RelationsView.vue'
import FilesView from '../views/FilesView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/specifications',
      name: 'specifications',
      component: SpecificationsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/versions',
      name: 'versions',
      component: VersionsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/relations',
      name: 'relations',
      component: RelationsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/files',
      name: 'files',
      component: FilesView,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router