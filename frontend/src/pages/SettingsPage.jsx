import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Settings, Shield, Database, Bell, RefreshCw } from 'lucide-react'

const API_BASE = '/api'

function SettingsPage() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      const res = await axios.get(`${API_BASE}/settings/`)
      setConfig(res.data)
    } catch (err) {
      console.error('Config error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold gradient-text">Settings</h2>
        <p className="text-slate-400 text-sm mt-1">Configure screening criteria and alert thresholds</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Screening Criteria */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Screening Criteria
          </h3>
          <div className="space-y-4">
            <SettingRow label="Minimum ROE" value={`${config.screening_criteria.min_roe}%`} />
            <SettingRow label="Max Debt/Equity" value={config.screening_criteria.max_debt_equity} />
            <SettingRow label="Min EPS Growth" value={`${config.screening_criteria.min_eps_growth}%`} />
            <SettingRow label="Max P/E Ratio" value={config.screening_criteria.max_pe} />
          </div>
          <p className="text-xs text-slate-500 mt-4">
            These criteria are used during weekly screening to filter stocks with good potential.
          </p>
        </div>

        {/* Alert Thresholds */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-red-400" />
            Alert Thresholds
          </h3>
          <div className="space-y-4">
            <SettingRow label="Sentiment Exit" value={`${config.alert_thresholds.sentiment_exit}`} />
            <SettingRow label="Stop Loss" value={`${config.alert_thresholds.stop_loss_pct}%`} />
            <SettingRow label="Target Gain" value={`${config.alert_thresholds.target_gain_pct}%`} />
          </div>
          <p className="text-xs text-slate-500 mt-4">
            When these thresholds are breached, you'll receive exit alerts via Telegram and the dashboard.
          </p>
        </div>

        {/* News Sources */}
        <div className="glass rounded-xl p-6 md:col-span-2">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-green-400" />
            News Sources
          </h3>
          <div className="flex flex-wrap gap-2">
            {config.news_sources.map((source, i) => (
              <span key={i} className="px-3 py-1.5 bg-slate-800/50 rounded-lg text-sm text-slate-300">
                {source}
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-4">
            Daily news scans pull from these sources. Sentiment is calculated from all articles found.
          </p>
        </div>

        {/* Universe */}
        <div className="glass rounded-xl p-6 md:col-span-2">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-purple-400" />
            Stock Universe
          </h3>
          <p className="text-sm text-slate-400 mb-4">
            {config.default_universe_size} stocks in the default screening universe (Nifty 50 + selected stocks).
          </p>
          <div className="p-4 bg-slate-800/50 rounded-lg">
            <p className="text-xs text-slate-500">
              The weekly screener evaluates all stocks in this universe and ranks them by overall score.
              You can add individual stocks to your watchlist for closer tracking.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function SettingRow({ label, value }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-800">
      <span className="text-sm text-slate-400">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  )
}

export default SettingsPage
