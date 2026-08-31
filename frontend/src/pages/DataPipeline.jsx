import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import api from '../services/api'

const STATUS_COLORS = {
  PENDING: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  STARTED: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  SUCCESS: 'text-green-400 bg-green-500/10 border-green-500/30',
  FAILURE: 'text-red-400 bg-red-500/10 border-red-500/30',
  RETRY: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
}

const STATUS_ICONS = {
  PENDING: '⏳',
  STARTED: '🔄',
  SUCCESS: '✅',
  FAILURE: '❌',
  RETRY: '🔁',
}

function TaskCard({ title, description, icon, endpoint, schedule }) {
  const [taskId, setTaskId] = useState(null)
  const [status, setStatus] = useState(null)
  const [result, setResult] = useState(null)
  const [triggering, setTriggering] = useState(false)
  const pollRef = useRef(null)

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  const pollStatus = (id) => {
    stopPolling()

    pollRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/tasks/status/${id}`)

        setStatus(res.data.status)

        if (res.data.result) {
          setResult(res.data.result)
        }

        if (['SUCCESS', 'FAILURE'].includes(res.data.status)) {
          stopPolling()
        }
      } catch {
        stopPolling()
      }
    }, 2000)
  }

  useEffect(() => {
    return () => stopPolling()
  }, [])

  const handleTrigger = async () => {
    setTriggering(true)
    setResult(null)
    setStatus('PENDING')

    try {
      const res = await api.post(endpoint)

      setTaskId(res.data.task_id)
      setStatus('PENDING')
      pollStatus(res.data.task_id)
    } catch (err) {
      setStatus('FAILURE')
      setResult(
        err.response?.data?.detail || 'Failed to queue task'
      )
    } finally {
      setTriggering(false)
    }
  }

  return (
    <div className="bg-dark-200 rounded-2xl p-6 border border-slate-700/50">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{icon}</span>

          <div>
            <h3 className="text-white font-semibold">
              {title}
            </h3>

            <p className="text-slate-400 text-sm">
              {description}
            </p>
          </div>
        </div>

        <button
          onClick={handleTrigger}
          disabled={
            triggering ||
            status === 'STARTED' ||
            status === 'PENDING'
          }
          className="shrink-0 bg-primary-600 hover:bg-primary-500 disabled:bg-primary-900 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-all flex items-center gap-2"
        >
          {triggering ? (
            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            '▶ Run Now'
          )}
        </button>
      </div>

      <div className="flex items-center gap-2 text-xs text-slate-500 mb-4">
        <span>🕐</span>
        <span>Scheduled: {schedule}</span>
      </div>

      <AnimatePresence>
        {status && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div
              className={`border rounded-lg px-4 py-3 text-sm ${
                STATUS_COLORS[status] ||
                STATUS_COLORS.PENDING
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span>
                  {STATUS_ICONS[status] || '⏳'}
                </span>

                <span className="font-medium">
                  {status}
                </span>

                {taskId && (
                  <span className="text-xs opacity-60 font-mono ml-auto">
                    {taskId.slice(0, 8)}...
                  </span>
                )}
              </div>

              {result && (
                <p className="text-xs opacity-80 mt-1 font-mono">
                  {result}
                </p>
              )}

              {['PENDING', 'STARTED'].includes(status) && (
                <div className="mt-2 w-full bg-black/20 rounded-full h-1">
                  <div className="bg-current h-1 rounded-full animate-pulse w-1/2" />
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function DataPipeline() {
  const tasks = [
    {
      title: 'Forex Rate Updater',
      description:
        'Fetches latest USD exchange rates for all supported currencies from ExchangeRate-API and updates the database.',
      icon: '💱',
      endpoint: '/tasks/trigger/forex',
      schedule: 'Every hour (top of hour)',
    },
    {
      title: 'Trade Statistics Fetch',
      description:
        'Pulls import/export statistics from UN Comtrade API for tracked HS code chapters and logs the data.',
      icon: '📊',
      endpoint: '/tasks/trigger/trade-stats',
      schedule: 'Every Monday at 2:00 AM UTC',
    },
  ]

  return (
    <div className="min-h-screen bg-dark-300 p-6">
      <div className="max-w-4xl mx-auto">

        <div className="flex items-center gap-4 mb-8">
          <Link
            to="/dashboard"
            className="text-slate-400 hover:text-white transition-colors text-sm"
          >
            ← Dashboard
          </Link>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold text-white mb-2">
            Data Pipeline
          </h1>

          <p className="text-slate-400 mb-4">
            Background ETL tasks that keep TradeFlow AI data fresh automatically.
          </p>

          <a
            href="http://localhost:5555"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 text-sm text-primary-400 hover:text-primary-300 mb-8 transition-colors"
          >
            {'🌸 Open Flower monitoring dashboard →'}
          </a>

          <div className="bg-dark-200 rounded-xl p-4 border border-slate-700/30 mb-8">
            <p className="text-xs text-slate-500 leading-relaxed">
              <span className="text-slate-300 font-medium">
                How it works:{' '}
              </span>

              Celery Beat sends tasks to a Redis queue on schedule.
              The Celery Worker picks them up, executes the ETL logic,
              and stores results back in Redis. You can also trigger
              any task manually using the buttons below.
            </p>
          </div>

          <div className="grid gap-6">
            {tasks.map((task) => (
              <TaskCard
                key={task.title}
                {...task}
              />
            ))}
          </div>

          <div className="mt-8 bg-dark-200 rounded-xl p-6 border border-slate-700/30">
            <p className="text-sm font-medium text-slate-300 mb-4">
              Pipeline Flow
            </p>

            <div className="flex items-center justify-between text-center text-xs">
              {[
                'Beat Scheduler',
                '→',
                'Redis Queue',
                '→',
                'Celery Worker',
                '→',
                'PostgreSQL DB',
              ].map((item, i) =>
                item === '→' ? (
                  <span
                    key={i}
                    className="text-slate-600 text-lg"
                  >
                    →
                  </span>
                ) : (
                  <div
                    key={i}
                    className="bg-dark-100 rounded-lg px-3 py-2 border border-slate-700/50"
                  >
                    <span className="text-slate-300">
                      {item}
                    </span>
                  </div>
                )
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}