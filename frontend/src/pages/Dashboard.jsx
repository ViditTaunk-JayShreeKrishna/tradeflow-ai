import { useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
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

  const features = [
  { name: 'HS Classifier',     description: 'AI-powered HS code prediction',  href: '/hs-classifier', ready: true },
  { name: 'Landed Cost',       description: 'Full import cost breakdown',       href: '/landed-cost',   ready: true },
  { name: 'Documents',         description: 'Generate trade documents',         href: '#',              ready: false },
  { name: 'Compliance',        description: 'Check trade rules & restrictions', href: '#',              ready: false },
  { name: 'Analytics',         description: 'Trade flow insights',              href: '#',              ready: false },
  { name: 'Freight Rates',     description: 'Live shipping rates',              href: '#',              ready: false },
]

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

          <div className="bg-dark-200 rounded-2xl p-8 border border-slate-700/50 mb-6">
            <h2 className="text-xl font-semibold text-white mb-1">
              Welcome back{user ? `, ${user.full_name}` : ''} 👋
            </h2>
            <p className="text-slate-400 text-sm">
              Your AI-powered import/export intelligence platform.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {features.map((feature) => (
              feature.ready ? (
                <Link key={feature.name} to={feature.href}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="bg-dark-200 rounded-xl p-6 border border-primary-500/30 cursor-pointer hover:border-primary-400/60 transition-all"
                  >
                    <p className="text-white font-medium">{feature.name}</p>
                    <p className="text-slate-400 text-sm mt-1">{feature.description}</p>
                    <span className="inline-block mt-3 text-xs text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded-full">
                      Ready
                    </span>
                  </motion.div>
                </Link>
              ) : (
                <div
                  key={feature.name}
                  className="bg-dark-200 rounded-xl p-6 border border-slate-700/30 opacity-60"
                >
                  <p className="text-slate-300 font-medium">{feature.name}</p>
                  <p className="text-slate-500 text-sm mt-1">{feature.description}</p>
                  <span className="inline-block mt-3 text-xs text-slate-500 bg-slate-700/30 px-2 py-0.5 rounded-full">
                    Coming soon
                  </span>
                </div>
              )
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  )
}