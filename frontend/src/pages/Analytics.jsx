import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, Legend
} from 'recharts'
import api from '../services/api'

const CHART_COLORS = ['#0ea5e9', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#ec4899']

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-dark-100 border border-slate-600 rounded-lg p-3 text-xs shadow-xl">
        <p className="text-slate-300 font-medium mb-1">{label}</p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color || entry.fill }}>
            {entry.name}: <span className="font-semibold">{entry.value}</span>
          </p>
        ))}
      </div>
    )
  }
  return null
}

function StatCard({ label, value, icon, sub }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-dark-200 rounded-xl p-5 border border-slate-700/50"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </motion.div>
  )
}

function ChartCard({ title, subtitle, children, loading }) {
  return (
    <div className="bg-dark-200 rounded-2xl p-6 border border-slate-700/50">
      <h3 className="text-white font-semibold mb-1">{title}</h3>
      <p className="text-slate-400 text-xs mb-5">{subtitle}</p>
      {loading ? (
        <div className="h-48 flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-slate-600 border-t-primary-400 rounded-full animate-spin" />
        </div>
      ) : children}
    </div>
  )
}

export default function Analytics() {
  const [overview, setOverview] = useState(null)
  const [freightRates, setFreightRates] = useState([])
  const [exchangeRates, setExchangeRates] = useState([])
  const [dutyRates, setDutyRates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [ov, fr, ex, dr] = await Promise.all([
          api.get('/analytics/overview'),
          api.get('/analytics/freight-rates'),
          api.get('/analytics/exchange-rates'),
          api.get('/analytics/duty-rates'),
        ])
        setOverview(ov.data)
        setFreightRates(fr.data)
        setExchangeRates(ex.data)
        setDutyRates(dr.data)
      } catch (err) {
        console.error('Analytics fetch failed:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  const seaRates = freightRates.filter(r => r.mode === 'sea')
  const airRates = freightRates.filter(r => r.mode === 'air')

  // Exchange rates: exclude very high values (JPY, KRW) for chart clarity
  const fxChartData = exchangeRates
    .filter(r => r.rate < 100)
    .map(r => ({ currency: r.currency, rate: r.rate }))

  const fxHighData = exchangeRates
    .filter(r => r.rate >= 100)
    .map(r => ({ currency: r.currency, rate: r.rate }))

  return (
    <div className="min-h-screen bg-dark-300 p-6">
      <div className="max-w-6xl mx-auto">

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white mb-2">Analytics</h1>
          <p className="text-slate-400 mb-8">
            Live insights from TradeFlow AI's trade data — rates, duties, and market data.
          </p>

          {/* Stat Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
            <StatCard label="Countries"       value={overview?.total_countries ?? '—'}       icon="🌍" />
            <StatCard label="HS Codes"        value={overview?.total_hs_codes ?? '—'}        icon="📋" />
            <StatCard label="Duty Rates"      value={overview?.total_duty_rates ?? '—'}      icon="💰" />
            <StatCard label="Freight Routes"  value={overview?.total_freight_routes ?? '—'}  icon="🚢" />
            <StatCard
              label="Currencies"
              value={overview?.supported_currencies ?? '—'}
              icon="💱"
              sub={overview?.last_forex_update ? `Updated ${overview.last_forex_update}` : null}
            />
          </div>

          {/* Row 1: Sea freight + Air freight */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

            <ChartCard
              title="Sea Freight Rates"
              subtitle="USD per 20GP container by trade route"
              loading={loading}
            >
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={seaRates} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2433" />
                  <XAxis
                    dataKey="route"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={{ stroke: '#334155' }}
                  />
                  <YAxis
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={{ stroke: '#334155' }}
                    tickFormatter={v => `$${v.toLocaleString()}`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="rate_usd" name="Rate (USD)" radius={[4, 4, 0, 0]}>
                    {seaRates.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard
              title="Air Freight Rates"
              subtitle="USD per kg by trade route"
              loading={loading}
            >
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={airRates} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2433" />
                  <XAxis
                    dataKey="route"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={{ stroke: '#334155' }}
                  />
                  <YAxis
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={{ stroke: '#334155' }}
                    tickFormatter={v => `$${v}`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="rate_usd" name="Rate ($/kg)" radius={[4, 4, 0, 0]}>
                    {airRates.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[(i + 2) % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Row 2: Exchange rates + Duty rates */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

            <ChartCard
              title="USD Exchange Rates"
              subtitle="Currencies under 100 per USD (latest rates)"
              loading={loading}
            >
              <ResponsiveContainer width="100%" height={240}>
                <BarChart
                  data={fxChartData}
                  layout="vertical"
                  margin={{ top: 5, right: 40, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2433" horizontal={false} />
                  <XAxis
                    type="number"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={{ stroke: '#334155' }}
                  />
                  <YAxis
                    dataKey="currency"
                    type="category"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={{ stroke: '#334155' }}
                    width={35}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="rate" name="Rate per USD" radius={[0, 4, 4, 0]} fill="#0ea5e9" />
                </BarChart>
              </ResponsiveContainer>

              {fxHighData.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-700/50">
                  <p className="text-xs text-slate-500 mb-2">High-value currencies (excluded from chart):</p>
                  <div className="flex flex-wrap gap-2">
                    {fxHighData.map(r => (
                      <span key={r.currency} className="text-xs bg-dark-100 border border-slate-700 px-2 py-1 rounded text-slate-300">
                        {r.currency}: {r.rate.toLocaleString()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </ChartCard>

            <ChartCard
              title="Duty Rates by HS Code"
              subtitle="Basic duty + IGST breakdown per HS code (import to India)"
              loading={loading}
            >
              <ResponsiveContainer width="100%" height={240}>
                <BarChart
                  data={dutyRates.filter(d => d.country_code === 'IN')}
                  margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2433" />
                  <XAxis
                    dataKey="hs_code"
                    tick={{ fill: '#94a3b8', fontSize: 10 }}
                    axisLine={{ stroke: '#334155' }}
                  />
                  <YAxis
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    axisLine={{ stroke: '#334155' }}
                    tickFormatter={v => `${v}%`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }}
                  />
                  <Bar dataKey="basic_duty" name="Basic Duty %" stackId="a" fill="#0ea5e9" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="igst" name="IGST %" stackId="a" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Freight rates table */}
          <div className="bg-dark-200 rounded-2xl p-6 border border-slate-700/50">
            <h3 className="text-white font-semibold mb-1">All Freight Rates</h3>
            <p className="text-slate-400 text-xs mb-5">Complete rate card from database</p>
            {loading ? (
              <div className="h-24 flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-slate-600 border-t-primary-400 rounded-full animate-spin" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700/50">
                      <th className="text-left text-slate-400 font-medium pb-3 pr-4">Route</th>
                      <th className="text-left text-slate-400 font-medium pb-3 pr-4">Mode</th>
                      <th className="text-left text-slate-400 font-medium pb-3 pr-4">Container</th>
                      <th className="text-right text-slate-400 font-medium pb-3">Rate (USD)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {freightRates.map((r, i) => (
                      <tr key={i} className="border-b border-slate-700/20 hover:bg-slate-700/10 transition-colors">
                        <td className="py-2.5 pr-4 text-white">{r.route_full}</td>
                        <td className="py-2.5 pr-4">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            r.mode === 'sea'
                              ? 'bg-blue-500/10 text-blue-400'
                              : 'bg-violet-500/10 text-violet-400'
                          }`}>
                            {r.mode === 'sea' ? '🚢 Sea' : '✈️ Air'}
                          </span>
                        </td>
                        <td className="py-2.5 pr-4 text-slate-400 text-xs">
                          {r.container_type || '—'}
                        </td>
                        <td className="py-2.5 text-right text-primary-400 font-medium">
                          ${r.rate_usd.toLocaleString()}
                          <span className="text-slate-500 text-xs ml-1">/{r.unit}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </motion.div>
      </div>
    </div>
  )
}