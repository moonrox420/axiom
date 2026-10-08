import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { apiClient } from '../api/client'

interface DashboardStats {
  total_invoices: number
  total_assets: number
  open_exceptions: number
}

export function DashboardPage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const user = useAuthStore(state => state.user)
  const logout = useAuthStore(state => state.logout)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      // Mock stats; replace with actual API call when endpoint exists
      setStats({
        total_invoices: 0,
        total_assets: 0,
        open_exceptions: 0,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/auth')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Axiom</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h2>

        {loading ? (
          <div className="text-center text-gray-600">Loading...</div>
        ) : stats ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-600 text-sm font-medium">Total Invoices</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_invoices}</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-600 text-sm font-medium">Assets</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_assets}</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-600 text-sm font-medium">Open Exceptions</h3>
              <p className="text-3xl font-bold text-red-600 mt-2">{stats.open_exceptions}</p>
            </div>
          </div>
        ) : null}

        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <button
            onClick={() => navigate('/invoices')}
            className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold text-gray-900">Invoices</h3>
            <p className="text-gray-600 text-sm mt-2">Manage and generate invoices</p>
          </button>

          <button
            onClick={() => navigate('/assets')}
            className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold text-gray-900">Assets</h3>
            <p className="text-gray-600 text-sm mt-2">Track and locate assets</p>
          </button>

          <button
            onClick={() => navigate('/exceptions')}
            className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold text-gray-900">Exceptions</h3>
            <p className="text-gray-600 text-sm mt-2">Review and resolve exceptions</p>
          </button>
        </div>
      </div>
    </div>
  )
}