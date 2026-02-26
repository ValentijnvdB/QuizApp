import axios from 'axios'
import {useAuthStore} from '../stores/auth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const authStore = useAuthStore()

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})
axios.defaults.withCredentials = true;


// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (error.response.config.url === `${API_URL}/auth/refresh` ||
          error.config.url === `${API_URL}/auth/refresh`) {
        console.log("refresh failed... logging out!")
        // Refresh token has expired or is invalid
        // Log the user out
        authStore.logout().then(() => {
          window.location.href = '/'
        })
        return
      } else {
        // Access token has expired or is invalid
        // Request a new token
        localStorage.removeItem('accessToken')
        return authStore.refreshAccessToken().then((newToken) => {
          // Retry the original request with the new token
          const originalRequest = error.config
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`
          return api(originalRequest)
        })
      }
    }
    return Promise.reject(error)
  }
)

// Quiz API
export const quizApi = {
  // Get all quizzes for current user
  getQuizzes() {
    return api.get('/quizzes/from-user')
  },
  
  // Get a specific quiz
  getQuiz(quiz_id) {
    return api.get(`/quizzes/${quiz_id}`)
  },
  
  // Create a new quiz
  createQuiz(title, description, creator_id) {
    return api.post('/quizzes/create', {
      title,
      description,
      creator_id
    })
  },
  
  // Update a quiz
  updateQuiz(quiz_id, title, description, is_published) {
    return api.put(`/quizzes/${quiz_id}`, {
      title,
      description,
      is_published
    })
  },
  
  // Delete a quiz
  deleteQuiz(id) {
    return api.delete(`/quizzes/${id}`)
  },
  
  // Add a question to a quiz
  addQuestion(quizId, questionData) {
    return api.post(`/quizzes/${quizId}/questions`, questionData)
  },
  
  // Update a question
  updateQuestion(quizId, questionId, questionData) {
    return api.put(`/quizzes/${quizId}/questions/${questionId}`, questionData)
  },
  
  // Delete a question
  deleteQuestion(quizId, questionId) {
    return api.delete(`/quizzes/${quizId}/questions/${questionId}`)
  }
}

// Session API
export const sessionApi = {
  // Create a new session
  createSession(quizId) {
    return api.post('/sessions', { quiz_id: quizId })
  },
  
  // Get session details
  getSession(code) {
    return api.get(`/sessions/${code}`)
  },
  
  // Join a session (participant)
  joinSession(code, name) {
    return api.post(`/sessions/${code}/join`, { name })
  },
  
  // Get session results
  getResults(code) {
    return api.get(`/sessions/${code}/results`)
  }
}

// Media API
export const mediaApi = {
  // Upload media file
  uploadMedia(file, onUploadProgress) {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress
    })
  },
  
  // Get media URL
  getMediaUrl(filename) {
    return `${API_URL}/media/${filename}`
  }
}

export default api
