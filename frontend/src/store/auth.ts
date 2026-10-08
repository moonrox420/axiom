import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      setToken: (token: string) => {
        set({ token, isAuthenticated: true })
        localStorage.setItem('axiom_token', token)
      },
      
      setUser: (user: User) => {
        set({ user })
        localStorage.setItem('axiom_user', JSON.stringify(user))
      },
      
      login: async (email: string, password: string) => {
        try {
          const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          })
          
          if (!response.ok) {
            throw new Error('Login failed')
          }
          
          const data = await response.json()
          set({
            token: data.access_token,
            user: { id: data.user_id, email, full_name: null, is_active: true },
            isAuthenticated: true,
          })
          
          localStorage.setItem('axiom_token', data.access_token)
          localStorage.setItem('axiom_user', JSON.stringify({ id: data.user_id, email }))
        } catch (error) {
          set({ isAuthenticated: false, token: null, user: null })
          throw error
        }
      },
      
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
        localStorage.removeItem('axiom_token')
        localStorage.removeItem('axiom_user')
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)