import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import useAuthStore from '../store/authStore'

export default function Dashboard() {
  const { user, logout, token } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!token) navigate('/login')
  }, [token, navigate])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-dark-300 p-8">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-2xl font-bold text-primary-400">TradeFlow AI</h1>
            <button
              onClick={handleLogout}
              className="text-slate-400 hover:text-white text-sm transition-colors"
            >
              Sign out
            </button>
          </div>

          <div className="bg-dark-200 rounded-2xl p-8 border border-slate-700/50">
            <h2 className="text-xl font-semibold text-white mb-2">
              Welcome back{user ? `, ${user.full_name}` : ''} 👋
            </h2>
            <p className="text-slate-400">
              Your TradeFlow AI dashboard is being built. More features coming soon.
            </p>

            <div className="grid grid-cols-3 gap-4 mt-8">
              {['HS Classifier', 'Landed Cost', 'Documents'].map((feature) => (
                <div
                  key={feature}
                  className="bg-dark-100 rounded-xl p-6 border border-slate-700/30 text-center"
                >
                  <p className="text-slate-300 font-medium">{feature}</p>
                  <p className="text-slate-500 text-sm mt-1">Coming soon</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}