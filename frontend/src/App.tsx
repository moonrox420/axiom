import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { InvoicesPage } from './pages/InvoicesPage'
import { AssetsPage } from './pages/AssetsPage'
import { ExceptionsPage } from './pages/ExceptionsPage'
import { PrivateRoute } from './components/PrivateRoute'
import { useAuthStore } from './store/auth'

export default function App() {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated)

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route
          path="/"
          element={
            isAuthenticated ? <DashboardPage /> : <Navigate to="/auth" replace />
          }
        />
        <Route
          path="/invoices"
          element={
            <PrivateRoute>
              <InvoicesPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/assets"
          element={
            <PrivateRoute>
              <AssetsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/exceptions"
          element={
            <PrivateRoute>
              <ExceptionsPage />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}