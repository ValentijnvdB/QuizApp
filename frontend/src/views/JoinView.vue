<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-500 to-green-700 p-4">
    <div class="card max-w-md w-full">
      <h2 class="text-3xl font-bold text-center mb-8">
        Join Quiz
      </h2>
      
      <form @submit.prevent="handleJoin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Session Code
          </label>
          <input
            v-model="sessionCode"
            type="text"
            required
            class="input-field text-center text-2xl font-bold uppercase tracking-wider"
            placeholder="ABCD1234"
            maxlength="8"
            @input="sessionCode = sessionCode.toUpperCase()"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Your Name
          </label>
          <input
            v-model="playerName"
            type="text"
            required
            class="input-field"
            placeholder="Enter your name"
            maxlength="30"
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
          {{ loading ? 'Joining...' : 'Join Quiz' }}
        </button>
      </form>
      
      <div class="mt-6 text-center">
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
import { useRouter } from 'vue-router'
import { sessionApi } from '@/services/api'

const router = useRouter()

const sessionCode = ref('')
const playerName = ref('')
const loading = ref(false)
const error = ref('')

const handleJoin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // Verify session exists and join
    await sessionApi.joinSession(sessionCode.value, playerName.value)
    
    // Redirect to play view
    router.push({
      name: 'session-play',
      params: { code: sessionCode.value }
    })
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'Session not found. Please check the code.'
    } else if (err.response?.status === 400) {
      error.value = err.response.data.detail || 'Cannot join this session.'
    } else {
      error.value = 'Failed to join session. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
