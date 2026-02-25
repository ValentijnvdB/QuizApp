import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'


export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)

  function setAccessToken(token) {
    accessToken.value = token
    localStorage.setItem('accessToken', accessToken.value)
    // Set default Authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
  }

  async function login(username, password) {
    let cred = {
      username,
      password
    };
    try {
      const response = await axios.post(`${API_URL}/auth/login`, cred, {
        withCredentials: true
      })
      console.log(response.data)

      setAccessToken(response.data.access_token)

      user.value = response.data.user
      localStorage.setItem('user', JSON.stringify(user))

      
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

  async function logout() {
    console.log("Logging out")
    try {
      const response = await axios.post(`${API_URL}/auth/logout`, {})
    } catch (error) {
      console.error('Logout failed:', error)
      throw error
    }

    accessToken.value = null
    user.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  async function refreshAccessToken() {
    console.log("Refreshing access token")
    try {
      const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
        withCredentials: true
      })
      setAccessToken(response.data.access_token)

    } catch (error) {
      console.error('Refresh access token failed:', error)
      throw error
    }
  }

  // Initialize axios header if token exists
  if (accessToken.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
  }

  return {
    accessToken: accessToken,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    refreshAccessToken
  }
})
