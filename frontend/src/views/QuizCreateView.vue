<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">Create Quiz</h1>
      <div class="card">

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <input
                v-model="form.title"
                type="text"
                required
                class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <input
                v-model="form.description"
                type="text"
                class="input-field"
                :placeholder=default_description
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
            {{ loading ? 'Loading...' : 'Create quiz' }}
          </button>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import {ref} from "vue";
import {useRouter} from "vue-router";
import {useAuthStore} from "@/stores/auth";
import {quizApi} from "@/services/api";

const router = useRouter()
const authStore = useAuthStore();

const error = ref('')
let loading = ref(false);

const default_description = ref("A new quiz.");

const form = ref({
  title: '',
  description: ''
})

const handleSubmit = async () => {
  loading.value = true
  error.value = ''

  const description = form.value.description === '' ? default_description.value : form.value.description

  try {
    const response = await quizApi.createQuiz(
      form.value.title,
      description,
      authStore.user.id
    )

    const quiz_id = response.data.id
    // Redirect to quiz page
    router.push(`/quiz/${quiz_id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create quiz'
  } finally {
    loading.value = false
  }
}
</script>
