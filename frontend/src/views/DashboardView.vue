<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">Quiz Dashboard</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-700">{{ authStore.user?.username }}</span>
            <button @click="handleLogout" class="btn-secondary text-sm">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6">
        <router-link to="/quiz/create" class="btn-primary">
          + Create New Quiz
        </router-link>
      </div>
      
      <div class="card">
        <h2 class="text-2xl font-bold mb-4">Your Quizzes</h2>
        <p class="text-gray-600" v-if="quizzes===null">
          Loading quizzes...
        </p>
        <p class="text-gray-600" v-else-if="quizzes.length===0">
          You have not created any quizzes yet. Create your first one with the button above!
        </p>
        <ol v-else>
          <li v-for="quiz in quizzes" :key="quiz.id">
            {{quiz.id}} - {{ quiz.title }} - {{ quiz.description }} - {{quiz.created_at}}
          </li>
        </ol>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {quizApi} from '@/services/api'
import {ref} from "vue";

const router = useRouter()
const authStore = useAuthStore()

let quizzes = ref(null)

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const requestQuizzes = () => {
  quizApi.getQuizzes().then((response) => {quizzes.value = response.data})
}
requestQuizzes()
</script>
