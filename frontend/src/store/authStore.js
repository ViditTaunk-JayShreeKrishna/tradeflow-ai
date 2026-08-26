import { create } from 'zustand'
import { authAPI } from '../services/api'

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authAPI.login({ email, password })
      const { access_token } = response.data
      localStorage.setItem('access_token', access_token)
      const userResponse = await authAPI.me()
      set({ token: access_token, user: userResponse.data, isLoading: false })
      return true
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Login failed', isLoading: false })
      return false
    }
  },

  register: async (email, fullName, password) => {
    set({ isLoading: true, error: null })
    try {
      await authAPI.register({ email, full_name: fullName, password })
      set({ isLoading: false })
      return true
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Registration failed', isLoading: false })
      return false
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    set({ user: null, token: null })
  },

  clearError: () => set({ error: null }),
}))

export default useAuthStore