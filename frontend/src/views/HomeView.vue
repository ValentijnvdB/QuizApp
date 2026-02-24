<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 p-4">
    <div class="text-center">
      <h1 class="text-5xl md:text-6xl font-bold text-white mb-4">
        Quiz App
      </h1>
      <p class="text-xl text-primary-100 mb-12">
        Create engaging quizzes and play with friends
      </p>
      
      <div class="space-y-4 max-w-sm mx-auto">
        <router-link
          to="/join"
          class="block w-full bg-white hover:bg-gray-100 text-primary-600 font-bold py-4 px-8 rounded-lg text-lg transition-colors shadow-lg"
        >
          Join Quiz
        </router-link>
        
        <router-link
          to="/dashboard"
          class="block w-full bg-primary-800 hover:bg-primary-900 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors"
        >
          Create Quiz
        </router-link>
      </div>
    </div>
    
    <div class="mt-16 text-center text-primary-100">
      <p class="text-sm">
        Powered by Vue 3 + FastAPI + WebSockets
      </p>
    </div>
  </div>
</template>

<script setup>
// Home view - Landing page
</script>
