import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import api from '../services/api'

const COLORS = [
  'bg-blue-500', 'bg-indigo-500', 'bg-violet-500',
  'bg-amber-500', 'bg-orange-500', 'bg-rose-500', 'bg-pink-500'
]

export default function LandedCost() {
  const [countries, setCountries] = useState([])
  const [form, setForm] = useState({
    hs_code: '',
    origin_country_code: 'CN',
    destination_country_code: 'IN',
    fob_value_usd: '',
    quantity: '',
    transport_mode: 'sea',
    weight_kg: '',
    num_containers: 1,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get('/countries/').then(r => setCountries(r.data)).catch(() => {})
  }, [])

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleCalculate = async () => {
    if (!form.hs_code || !form.fob_value_usd || !form.quantity) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await api.post('/landed-cost/calculate', {
        ...form,
        fob_value_usd: parseFloat(form.fob_value_usd),
        quantity: parseFloat(form.quantity),
        weight_kg: form.weight_kg ? parseFloat(form.weight_kg) : null,
        num_containers: parseInt(form.num_containers),
      })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Calculation failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark-300 p-6">
      <div className="max-w-5xl mx-auto">

        <div className="flex items-center gap-4 mb-8">
          <Link to="/dashboard" className="text-slate-400 hover:text-white transition-colors text-sm">
            ← Dashboard
          </Link>
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white mb-2">Landed Cost Calculator</h1>
          <p className="text-slate-400 mb-8">
            Full cost breakdown for your import — duties, freight, taxes, and total landed cost.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* ── Form ── */}
            <div className="bg-dark-200 rounded-2xl p-6 border border-slate-700/50 h-fit">
              <h2 className="text-lg font-semibold text-white mb-5">Shipment Details</h2>
              <div className="space-y-4">

                {/* HS Code */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">HS Code</label>
                  <input
                    name="hs_code"
                    value={form.hs_code}
                    onChange={handleChange}
                    placeholder="e.g. 6109.10"
                    className="w-full bg-dark-100 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 transition-colors"
                  />
                </div>

                {/* Countries */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Origin</label>
                    <select
                      name="origin_country_code"
                      value={form.origin_country_code}
                      onChange={handleChange}
                      className="w-full bg-dark-100 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-primary-500 transition-colors"
                    >
                      {countries.map(c => (
                        <option key={c.code} value={c.code}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Destination</label>
                    <select
                      name="destination_country_code"
                      value={form.destination_country_code}
                      onChange={handleChange}
                      className="w-full bg-dark-100 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-primary-500 transition-colors"
                    >
                      {countries.map(c => (
                        <option key={c.code} value={c.code}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* FOB + Quantity */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">FOB Value (USD)</label>
                    <input
                      name="fob_value_usd"
                      type="number"
                      value={form.fob_value_usd}
                      onChange={handleChange}
                      placeholder="e.g. 5000"
                      className="w-full bg-dark-100 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Quantity</label>
                    <input
                      name="quantity"
                      type="number"
                      value={form.quantity}
                      onChange={handleChange}
                      placeholder="e.g. 500"
                      className="w-full bg-dark-100 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 transition-colors"
                    />
                  </div>
                </div>

                {/* Transport mode toggle */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Transport Mode</label>
                  <div className="flex gap-2">
                    {['sea', 'air'].map(mode => (
                      <button
                        key={mode}
                        onClick={() => setForm({ ...form, transport_mode: mode })}
                        className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                          form.transport_mode === mode
                            ? 'bg-primary-600 text-white'
                            : 'bg-dark-100 text-slate-400 border border-slate-600 hover:border-slate-400'
                        }`}
                      >
                        {mode === 'sea' ? '🚢 Sea Freight' : '✈️ Air Freight'}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Conditional: containers or weight */}
                {form.transport_mode === 'sea' ? (
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Number of Containers (20GP)
                    </label>
                    <input
                      name="num_containers"
                      type="number"
                      min="1"
                      value={form.num_containers}
                      onChange={handleChange}
                      className="w-full bg-dark-100 border border-slate-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary-500 transition-colors"
                    />
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Total Weight (kg)
                    </label>
                    <input
                      name="weight_kg"
                      type="number"
                      value={form.weight_kg}
                      onChange={handleChange}
                      placeholder="e.g. 200"
                      className="w-full bg-dark-100 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 transition-colors"
                    />
                  </div>
                )}

                <button
                  onClick={handleCalculate}
                  disabled={loading || !form.hs_code || !form.fob_value_usd || !form.quantity}
                  className="w-full bg-primary-600 hover:bg-primary-500 disabled:bg-primary-900 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Calculating...
                    </>
                  ) : 'Calculate Landed Cost'}
                </button>
              </div>
            </div>

            {/* ── Results ── */}
            <div>
              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm"
                >
                  {error}
                </motion.div>
              )}

              <AnimatePresence>
                {result && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    className="space-y-4"
                  >
                    {/* Total */}
                    <div className="bg-dark-200 rounded-2xl p-6 border border-primary-500/30">
                      <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">
                        Total Landed Cost
                      </p>
                      <p className="text-4xl font-bold text-primary-400">
                        ${result.total_landed_cost_usd.toLocaleString()}
                      </p>
                      <p className="text-slate-400 text-sm mt-1">
                        {result.local_currency_code} {result.total_landed_cost_local.toLocaleString()}
                      </p>

                      <div className="border-t border-slate-700/50 mt-4 pt-4 grid grid-cols-3 gap-3">
                        <div>
                          <p className="text-xs text-slate-500">Per Unit (USD)</p>
                          <p className="text-lg font-semibold text-white">
                            ${result.per_unit_landed_cost_usd.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">CIF Value</p>
                          <p className="text-lg font-semibold text-white">
                            ${result.cif_value_usd.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">Route</p>
                          <p className="text-sm font-semibold text-white">
                            {result.origin_country.split(' ')[0]} → {result.destination_country.split(' ')[0]}
                          </p>
                        </div>
                      </div>

                      {!result.duty_rate_found && (
                        <p className="text-amber-400 text-xs mt-3 bg-amber-500/10 px-3 py-2 rounded-lg">
                          ⚠️ No duty rate found for this HS + country. Showing 0% duty.
                        </p>
                      )}
                      {!result.freight_rate_found && (
                        <p className="text-amber-400 text-xs mt-2 bg-amber-500/10 px-3 py-2 rounded-lg">
                          ⚠️ No freight rate on file. Using estimated default.
                        </p>
                      )}
                    </div>

                    {/* Breakdown bars */}
                    <div className="bg-dark-200 rounded-2xl p-6 border border-slate-700/50">
                      <p className="text-sm font-medium text-slate-300 mb-5">Cost Breakdown</p>
                      <div className="space-y-4">
                        {result.breakdown.map((item, idx) => (
                          item.amount_usd > 0 && (
                            <div key={item.label}>
                              <div className="flex justify-between text-sm mb-1.5">
                                <span className="text-slate-300">{item.label}</span>
                                <div className="text-right">
                                  <span className="text-white font-medium">
                                    ${item.amount_usd.toLocaleString()}
                                  </span>
                                  <span className="text-slate-500 text-xs ml-2">
                                    ({item.percentage_of_total}%)
                                  </span>
                                </div>
                              </div>
                              <div className="w-full bg-dark-100 rounded-full h-2">
                                <motion.div
                                  className={`${COLORS[idx % COLORS.length]} h-2 rounded-full`}
                                  initial={{ width: 0 }}
                                  animate={{ width: `${item.percentage_of_total}%` }}
                                  transition={{ duration: 0.6, delay: idx * 0.08 }}
                                />
                              </div>
                              <p className="text-xs text-slate-500 mt-1">{item.description}</p>
                            </div>
                          )
                        ))}
                      </div>
                    </div>

                    {/* Applied rates */}
                    <div className="bg-dark-200 rounded-xl p-4 border border-slate-700/30">
                      <p className="text-xs text-slate-500 mb-3 font-medium uppercase tracking-wider">
                        Applied Rates
                      </p>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                        <span className="text-slate-400">Basic Duty</span>
                        <span className="text-white">{result.basic_duty_rate}%</span>
                        <span className="text-slate-400">IGST / VAT</span>
                        <span className="text-white">{result.igst_rate}%</span>
                        <span className="text-slate-400">Additional Duty</span>
                        <span className="text-white">{result.additional_duty_rate}%</span>
                        <span className="text-slate-400">Exchange Rate</span>
                        <span className="text-white">
                          1 USD = {result.exchange_rate_to_usd} {result.local_currency_code}
                        </span>
                        <span className="text-slate-400">Duty Source</span>
                        <span className="text-white capitalize">
                          {result.duty_source.replace(/_/g, ' ')}
                        </span>
                        <span className="text-slate-400">Freight Source</span>
                        <span className="text-white capitalize">
                          {result.freight_source.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {!result && !error && !loading && (
                <div className="bg-dark-200 rounded-2xl p-10 border border-slate-700/30 text-center text-slate-500">
                  <p className="text-5xl mb-4">🧮</p>
                  <p className="text-sm">
                    Fill in the shipment details and calculate to see your complete cost breakdown.
                  </p>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}