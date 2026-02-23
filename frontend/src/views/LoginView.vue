<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="card max-w-md w-full">
      <h2 class="text-3xl font-bold text-center mb-8">
        {{ isLogin ? 'Login' : 'Register' }}
      </h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div v-if="!isLogin">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            class="input-field"
            placeholder="your@email.com"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <input
            v-model="form.username"
            type="text"
            required
            class="input-field"
            placeholder="username"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            v-model="form.password"
            type="password"
            required
            class="input-field"
            placeholder="••••••••"
          />
        </div>
        
        <div v-if="error" class="text-red-600 text-sm">
          {{ error }}
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="btn-primary w-full"
        >
          {{ loading ? 'Loading...' : (isLogin ? 'Login' : 'Register') }}
        </button>
      </form>
      
      <div class="mt-6 text-center">
        <button
          @click="isLogin = !isLogin"
          class="text-primary-600 hover:text-primary-700 text-sm"
        >
          {{ isLogin ? "Don't have an account? Register" : "Already have an account? Login" }}
        </button>
      </div>
      
      <div class="mt-4 text-center">
        <router-link
          to="/"
          class="text-gray-600 hover:text-gray-700 text-sm"
        >
          ← Back to home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')

const form = ref({
  username: '',
  email: '',
  password: ''
})

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  
  try {
    if (isLogin.value) {
      await authStore.login(form.value.username, form.value.password)
    } else {
      await authStore.register(form.value.username, form.value.email, form.value.password)
    }
    
    // Redirect to original destination or dashboard
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Authentication failed'
  } finally {
    loading.value = false
  }
}
</script>
