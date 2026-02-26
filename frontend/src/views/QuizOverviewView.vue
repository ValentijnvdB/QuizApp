<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">Edit Quiz</h1>
      <div class="card">
        <button
            v-if="isOwner&&!isEditing"
            type="button"
            class="btn-primary w-full"
            @mouseup="handleEditButtonClick"
          >Edit</button>
          <QuizEditFormComponent
              v-if="isEditing"
              :handleSubmit=handleSubmit
              buttonText="Update Quiz"
              defaultErrorMessage="Failed to update Quiz"
              :quizTitle=title
              :quizDescription=description />
          <div v-else>
            <p>Quiz ID: {{ quizId }}</p>
            <p>title: {{title}}</p>
            <p>description: {{description}}</p>
            <p v-if="error" class="text-red-600 text-sm">{{error}}</p>
          </div>

      </div>
    </div>
  </div>
</template>


<script setup>
import {ref} from "vue";
import {useRouter} from "vue-router";
import {useAuthStore} from "@/stores/auth";
import {quizApi} from "@/services/api";
import QuizEditFormComponent from "@/components/QuizEditFormComponent.vue";

const router = useRouter()
const authStore = useAuthStore();

const error = ref('')
let isEditing = ref(false);

const path = window.location.pathname;
const parts = path.split("/");

let creatorId = null;
let isOwner = ref(false);

let quizId = ref(parts[2]);
let title = ref("");
let description = ref("");
let isPublished = ref(false);


const default_description = ref("A new quiz.");


const getQuiz = async () => {
  error.value = ''
  try {
    const response = await quizApi.getQuiz(quizId.value)

    title.value = response.data.title;
    description.value = response.data.description;
    isPublished.value = response.data.is_published;

    creatorId = response.data.creator_id;
    isOwner = creatorId === response.data.creator_id;

  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to retrieve quiz info.'
  } finally {
  }
}

const handleEditButtonClick = () => {
  isEditing.value = true
}

const handleSubmit = async (form) => {
  try {
    const response = await quizApi.updateQuiz(
        quizId.value,
        form.value.title,
        form.value.description,
        isPublished.value
    )
    isEditing.value = false
    await getQuiz()
  } catch (err) {
    throw err;
  }
}

getQuiz();
</script>