import { defineStore } from 'pinia'
import { jwtDecode } from 'jwt-decode'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
      this.setUserFromToken(token)
    },
    removeToken() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },
    setUserFromToken(token) {
      try {
        const decoded = jwtDecode(token)
        this.user = decoded
      } catch (error) {
        console.error('Failed to decode token:', error)
        this.user = null
      }
    },
    initialize() {
      if (this.token) {
        this.setUserFromToken(this.token)
      }
    }
  }
})