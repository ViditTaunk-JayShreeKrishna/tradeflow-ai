import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import api from '../services/api'

export default function HSClassifier() {
  const [description, setDescription] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleClassify = async () => {
    if (!description.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await api.post('/hs-classifier/classify', { description })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Classification failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const examples = [
    "100% cotton men's round neck t-shirt",
    "portable laptop computer 15 inch intel",
    "android smartphone 5g dual camera",
    "vitamin C tablet 500mg supplement",
    "22 carat gold necklace handmade",
  ]

  return (
    <div className="min-h-screen bg-dark-300 p-6">
      <div className="max-w-3xl mx-auto">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/dashboard" className="text-slate-400 hover:text-white transition-colors text-sm">
            ← Dashboard
          </Link>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-3xl font-bold text-white mb-2">HS Code Classifier</h1>
          <p className="text-slate-400 mb-8">
            Describe your product in plain English and our AI predicts the correct HS code.
          </p>

          {/* Input Card */}
          <div className="bg-dark-200 rounded-2xl p-6 border border-slate-700/50 mb-6">
            <label className="block text-sm font-medium text-slate-300 mb-3">
              Product Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              placeholder="e.g. 100% cotton round neck t-shirt for men, short sleeve..."
              className="w-full bg-dark-100 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors resize-none"
            />

            {/* Example chips */}
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="text-xs text-slate-500 self-center">Try:</span>
              {examples.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setDescription(ex)}
                  className="text-xs bg-dark-100 hover:bg-slate-700 border border-slate-600 text-slate-300 px-3 py-1 rounded-full transition-colors"
                >
                  {ex.length > 35 ? ex.substring(0, 35) + '...' : ex}
                </button>
              ))}
            </div>

            <button
              onClick={handleClassify}
              disabled={loading || !description.trim()}
              className="mt-4 w-full bg-primary-600 hover:bg-primary-500 disabled:bg-primary-900 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Classifying...
                </>
              ) : 'Classify Product'}
            </button>
          </div>

          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm"
            >
              {error}
            </motion.div>
          )}

          {/* Results */}
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.4 }}
              >
                {/* Main prediction */}
                <div className="bg-dark-200 rounded-2xl p-6 border border-primary-500/30 mb-4">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">
                        Predicted HS Code
                      </p>
                      <p className="text-4xl font-bold text-primary-400">
                        {result.predicted_hs_code}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">
                        Confidence
                      </p>
                      <p className="text-2xl font-bold text-green-400">
                        {result.confidence_pct}
                      </p>
                    </div>
                  </div>

                  <p className="text-slate-300 text-sm mb-4">{result.description}</p>

                  {/* Confidence bar */}
                  <div className="w-full bg-dark-100 rounded-full h-2">
                    <motion.div
                      className="bg-gradient-to-r from-primary-600 to-green-500 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${result.confidence * 100}%` }}
                      transition={{ duration: 0.8, delay: 0.2 }}
                    />
                  </div>
                </div>

                {/* Top 3 */}
                <div className="bg-dark-200 rounded-2xl p-6 border border-slate-700/50">
                  <p className="text-sm font-medium text-slate-300 mb-4">
                    Top 3 Predictions
                  </p>
                  <div className="space-y-3">
                    {result.top_3.map((pred, idx) => (
                      <div key={pred.hs_code} className="flex items-center gap-4">
                        <span className="text-xs text-slate-500 w-4">{idx + 1}</span>
                        <span className="text-primary-400 font-mono font-semibold w-20">
                          {pred.hs_code}
                        </span>
                        <div className="flex-1">
                          <div className="flex justify-between text-xs text-slate-400 mb-1">
                            <span className="truncate mr-4">{pred.description}</span>
                            <span className="shrink-0">{pred.confidence_pct}</span>
                          </div>
                          <div className="w-full bg-dark-100 rounded-full h-1.5">
                            <motion.div
                              className="bg-primary-600 h-1.5 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${pred.confidence * 100}%` }}
                              transition={{ duration: 0.6, delay: 0.3 + idx * 0.1 }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 mt-4">
                    Model version: {result.model_version}
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  )
}