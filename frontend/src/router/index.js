import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/quiz/create',
      name: 'quiz-create',
      component: () => import('../views/QuizCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/quiz/:id/edit',
      name: 'quiz-edit',
      component: () => import('../views/QuizEditView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/session/:code/host',
      name: 'session-host',
      component: () => import('../views/SessionHostView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/join',
      name: 'join',
      component: () => import('../views/JoinView.vue')
    },
    {
      path: '/session/:code/play',
      name: 'session-play',
      component: () => import('../views/SessionPlayView.vue')
    },
    {
      path: '/session/:code/results',
      name: 'session-results',
      component: () => import('../views/SessionResultsView.vue')
    }
  ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('accessToken')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
