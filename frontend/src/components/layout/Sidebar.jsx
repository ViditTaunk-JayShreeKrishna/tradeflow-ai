import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import useAuthStore from '../../store/authStore'

const NAV_ITEMS = [
  { icon: '🏠', label: 'Dashboard',    href: '/dashboard',      ready: true  },
  { icon: '🔍', label: 'HS Classifier', href: '/hs-classifier',  ready: true  },
  { icon: '🧮', label: 'Landed Cost',   href: '/landed-cost',    ready: true  },
  { icon: '📊', label: 'Analytics',     href: '/analytics',      ready: true  },
  { icon: '⚙️', label: 'Data Pipeline', href: '/data-pipeline',  ready: true  },
  { icon: '📄', label: 'Documents',     href: '#',               ready: false },
  { icon: '✅', label: 'Compliance',    href: '#',               ready: false },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U'

  return (
    <aside className="w-64 bg-dark-200 border-r border-slate-700/50 flex flex-col min-h-screen shrink-0">

      {/* Logo */}
      <div className="p-6 border-b border-slate-700/50">
        <h1 className="text-xl font-bold text-primary-400">TradeFlow AI</h1>
        <p className="text-xs text-slate-500 mt-0.5">Import/Export Intelligence</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(item => {
          const isActive = location.pathname === item.href
          if (!item.ready) {
            return (
              <div
                key={item.label}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-600 cursor-not-allowed select-none"
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
                <span className="ml-auto text-xs bg-slate-800 px-1.5 py-0.5 rounded text-slate-600">
                  Soon
                </span>
              </div>
            )
          }
          return (
            <Link key={item.label} to={item.href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                  isActive
                    ? 'bg-primary-600/20 text-primary-400 border border-primary-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700/40'
                }`}
              >
                <span>{item.icon}</span>
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400" />
                )}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-slate-700/50">
        <div className="flex items-center gap-3 mb-3 px-1">
          <div className="w-8 h-8 bg-primary-600/20 border border-primary-500/30 rounded-full flex items-center justify-center text-primary-400 text-xs font-bold shrink-0">
            {initials}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {user?.full_name || 'User'}
            </p>
            <p className="text-xs text-slate-500 truncate">
              {user?.email || ''}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full text-sm text-slate-400 hover:text-red-400 hover:bg-red-500/10 py-2 rounded-lg transition-all text-left px-3"
        >
          Sign out
        </button>
      </div>
    </aside>
  )
}