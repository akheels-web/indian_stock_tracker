import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { AlertTriangle, Check, X, Bell, Filter } from 'lucide-react'
import AlertBadge from '../components/AlertBadge.jsx'

const API_BASE = '/api'

function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAlerts()
    fetchStats()
  }, [filter])

  const fetchAlerts = async () => {
    try {
      const params = { limit: 100 }
      if (filter !== 'all') params.severity = filter

      const res = await axios.get(`${API_BASE}/alerts/`, { params })
      setAlerts(res.data)
    } catch (err) {
      console.error('Alerts fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_BASE}/alerts/stats`)
      setStats(res.data)
    } catch (err) {
      console.error('Stats fetch error:', err)
    }
  }

  const acknowledgeAlert = async (id) => {
    try {
      await axios.post(`${API_BASE}/alerts/${id}/acknowledge`)
      fetchAlerts()
      fetchStats()
    } catch (err) {
      console.error('Acknowledge error:', err)
    }
  }

  const getSeverityIcon = (severity) => {
    const colors = {
      critical: 'text-red-400',
      high: 'text-orange-400',
      medium: 'text-yellow-400',
      low: 'text-blue-400',
    }
    return <AlertTriangle className={`w-5 h-5 ${colors[severity] || colors.low}`} />
  }

  const getSeverityBg = (severity) => {
    const colors = {
      critical: 'bg-red-500/10 border-red-500/20',
      high: 'bg-orange-500/10 border-orange-500/20',
      medium: 'bg-yellow-500/10 border-yellow-500/20',
      low: 'bg-blue-500/10 border-blue-500/20',
    }
    return colors[severity] || colors.low
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text">Alerts</h2>
          <p className="text-slate-400 text-sm mt-1">Exit signals, risk warnings, and notifications</p>
        </div>
        {stats && (
          <div className="flex gap-2">
            {stats.critical_count > 0 && <AlertBadge severity="critical" count={stats.critical_count} />}
            {stats.high_count > 0 && <AlertBadge severity="high" count={stats.high_count} />}
          </div>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {['all', 'critical', 'high', 'medium', 'low'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Alerts List */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
        </div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-20 text-slate-500">
          <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No alerts found. Your portfolio looks safe!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`glass rounded-xl p-5 border ${getSeverityBg(alert.severity)} ${
                !alert.is_read ? 'ring-1 ring-blue-500/30' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  {getSeverityIcon(alert.severity)}
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold">{alert.stock_symbol}</span>
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                        alert.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                        alert.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {alert.severity.toUpperCase()}
                      </span>
                      <span className="text-xs text-slate-500 capitalize">{alert.alert_type.replace(/_/g, ' ')}</span>
                    </div>
                    <h3 className="font-medium text-slate-200">{alert.title}</h3>
                    <p className="text-sm text-slate-400 mt-1">{alert.message}</p>
                    {alert.trigger_price && (
                      <p className="text-xs text-slate-500 mt-2">
                        Trigger Price: ₹{alert.trigger_price.toFixed(2)}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {!alert.is_read && (
                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="p-2 rounded-lg bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition-colors"
                      title="Mark as read"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AlertsPage
