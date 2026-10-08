import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'

interface Exception {
  id: string
  entity_type: string
  entity_id: string
  reason: string
  severity: string
  status: string
  created_at: string
}

export function ExceptionsPage() {
  const [exceptions, setExceptions] = useState<Exception[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchExceptions()
  }, [])

  const fetchExceptions = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/exceptions', {
        params: { status: 'open', skip: 0, limit: 100 },
      })
      setExceptions(response.data)
    } catch {
      setError('Failed to load exceptions')
    } finally {
      setLoading(false)
    }
  }

  const handleResolve = async (exceptionId: string) => {
    try {
      await apiClient.post(`/exceptions/${exceptionId}/resolve`, {
        resolution_notes: 'Resolved by user',
      })
      setExceptions(exceptions.filter(e => e.id !== exceptionId))
    } catch {
      setError('Failed to resolve exception')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Exceptions</h1>

        {error && (
          <div className="p-4 bg-red-100 text-red-700 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center text-gray-600">Loading...</div>
        ) : exceptions.length > 0 ? (
          <div className="space-y-4">
            {exceptions.map((exception) => (
              <div key={exception.id} className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{exception.reason}</h3>
                    <p className="text-sm text-gray-600 mt-2">
                      Entity: {exception.entity_type} ({exception.entity_id})
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(exception.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      exception.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      exception.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {exception.severity}
                    </span>
                    <button
                      onClick={() => handleResolve(exception.id)}
                      className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600">No open exceptions</p>
          </div>
        )}
      </div>
    </div>
  )
}