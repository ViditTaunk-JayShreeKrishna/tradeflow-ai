import { useEffect } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'
import Sidebar from './Sidebar'

export default function AppLayout() {
  const { token, user, loadUser } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    if (!user) loadUser()
  }, [token])

  if (!token) return null

  return (
    <div className="flex min-h-screen bg-dark-300">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}