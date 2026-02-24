import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// TODO: request refresh if access access token expires
// TODO: logout if refresh token expires

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(username, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        username,
        password
      })
      console.log(response.data)

      accessToken.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      user.value = response.data.user

      localStorage.setItem('accessToken', accessToken.value)
      localStorage.setItem('refreshToken', refreshToken.value)
      localStorage.setItem('user', JSON.stringify(user))
      
      // Set default Authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  async function register(username, email, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        username,
        email,
        password
      })
      
      // Automatically log in after registration
      return await login(username, password)
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  }

  async function logout(refresh_token) {
    try {
      const response = await axios.post(`${API_URL}/auth/logout`, {refresh_token})
    } catch (error) {
      console.error('Logout failed:', error)
      throw error
    }

    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  // Initialize axios header if token exists
  if (accessToken.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
  }

  return {
    accessToken: accessToken,
    refreshToken: refreshToken,
    user,
    isAuthenticated,
    login,
    register,
    logout
  }
})
