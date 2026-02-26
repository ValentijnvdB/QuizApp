<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">Create Quiz</h1>
      <div class="card">

        <QuizEditFormComponent
          :handleSubmit=handleSubmit
          buttonText="Create Quiz"
          defaultErrorMessage="Failed to create Quiz"
          quizTitle=""
          quizDescription="A new quiz" />

      </div>
    </div>
  </div>
</template>

<script setup>
import {useRouter} from "vue-router";
import {useAuthStore} from "@/stores/auth";
import {quizApi} from "@/services/api";
import QuizEditFormComponent from "@/components/QuizEditFormComponent.vue";

const router = useRouter()
const authStore = useAuthStore();


const handleSubmit = async (form) => {
  const response = await quizApi.createQuiz(
    form.value.title,
    form.value.description,
    authStore.user.id
  )
  const quiz_id = response.data.id
  // Redirect to quiz page
  router.push(`/quiz/${quiz_id}`)
}
</script>
