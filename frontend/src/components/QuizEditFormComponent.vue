
<template>
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
          :placeholder=quizDescription
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
      {{ loading ? 'Loading...' : props.buttonText }}
    </button>
  </form>
</template>

<script setup>
import {ref} from "vue";

const props = defineProps(['handleSubmit', 'buttonText', 'defaultErrorMessage', 'quizTitle', 'quizDescription'])

const error = ref('')
let loading = ref(false);

const form = ref({
  title: props.quizTitle ? props.quizTitle : '',
  description: props.quizDescription ? props.quizDescription : '',
})

const handleSubmit = async () => {
  loading.value = true
  error.value = ''

  console.log("Handling submit")

  try {
    props.handleSubmit(form)
  } catch (err) {
    error.value = (err.response?.data?.detail || props.defaultErrorMessage) || 'Unknown error'
  } finally {
    loading.value = false
  }
}

</script>
