import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const features = [
  { name: 'HS Classifier',  description: 'AI-powered HS code prediction',   href: '/hs-classifier', ready: true  },
  { name: 'Landed Cost',    description: 'Full import cost breakdown',        href: '/landed-cost',   ready: true  },
  { name: 'Analytics',      description: 'Trade flows and rate insights',     href: '/analytics',     ready: true  },
  { name: 'Data Pipeline',  description: 'ETL tasks and live data updates',   href: '/data-pipeline', ready: true  },
  { name: 'Documents',      description: 'Generate trade documents',          href: '#',              ready: false },
  { name: 'Compliance',     description: 'Check trade rules and restrictions',href: '#',              ready: false },
]

export default function Dashboard() {
  const { user } = useAuthStore()

  return (
    <div className="min-h-screen bg-dark-300 p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="max-w-4xl mx-auto">

          <div className="bg-dark-200 rounded-2xl p-8 border border-slate-700/50 mb-6">
            <h2 className="text-2xl font-semibold text-white mb-1">
              Welcome back{user ? `, ${user.full_name}` : ''} 👋
            </h2>
            <p className="text-slate-400">
              Your AI-powered import/export intelligence platform. What would you like to do today?
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {features.map(feature => (
              feature.ready ? (
                <Link key={feature.name} to={feature.href}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="bg-dark-200 rounded-xl p-6 border border-primary-500/20 hover:border-primary-400/50 cursor-pointer transition-all h-full"
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
                  className="bg-dark-200 rounded-xl p-6 border border-slate-700/30 opacity-50 h-full"
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