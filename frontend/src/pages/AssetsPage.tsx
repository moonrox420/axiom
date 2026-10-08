import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'

interface Asset {
  id: string
  name: string
  category: string
  current_location: string
  status: string
  confidence: number
}

export function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/assets', {
        params: { skip: 0, limit: 100 },
      })
      setAssets(response.data)
    } catch (err) {
      setError('Failed to load assets')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Assets</h1>

        {error && (
          <div className="p-4 bg-red-100 text-red-700 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center text-gray-600">Loading...</div>
        ) : assets.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assets.map((asset) => (
              <div key={asset.id} className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">{asset.name}</h3>
                <p className="text-sm text-gray-600 mt-2">Category: {asset.category}</p>
                <p className="text-sm text-gray-600">Location: {asset.current_location}</p>
                <div className="mt-4">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    asset.status === 'in_service' ? 'bg-green-100 text-green-800' :
                    asset.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {asset.status}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Confidence: {(asset.confidence * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600">No assets found</p>
          </div>
        )}
      </div>
    </div>
  )
}