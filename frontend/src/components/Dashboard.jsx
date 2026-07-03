import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { TrendingUp, TrendingDown, Eye, Package, LogOut, AlertTriangle, Newspaper } from 'lucide-react'
import ScoreCard from './ScoreCard.jsx'
import AlertBadge from './AlertBadge.jsx'
import { Link } from 'react-router-dom'

const API_BASE = '/api'

function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    try {
      const res = await axios.get(`${API_BASE}/dashboard/full`)
      setData(res.data)
    } catch (err) {
      console.error('Dashboard fetch error:', err)
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

  if (!data) return <div className="text-center text-slate-400">Failed to load dashboard</div>

  const { stats, weekly_picks, recent_alerts, sentiment_overview } = data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text">Dashboard</h2>
          <p className="text-slate-400 text-sm mt-1">Real-time overview of your Indian stock portfolio</p>
        </div>
        <div className="flex gap-2">
          {stats.critical_alerts > 0 && <AlertBadge severity="critical" count={stats.critical_alerts} />}
          {stats.unread_alerts > 0 && (
            <Link to="/alerts" className="px-3 py-1.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-medium">
              {stats.unread_alerts} Unread
            </Link>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Eye} label="Watching" value={stats.watching_count} color="text-blue-400" />
        <StatCard icon={Package} label="Holding" value={stats.holding_count} color="text-green-400" />
        <StatCard icon={LogOut} label="Exited" value={stats.exited_count} color="text-slate-400" />
        <StatCard icon={AlertTriangle} label="Alerts" value={stats.total_alerts} color="text-red-400" />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly Picks */}
        <div className="lg:col-span-2 glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              Weekly Top Picks
            </h3>
            <Link to="/watchlist" className="text-sm text-blue-400 hover:text-blue-300">View All →</Link>
          </div>

          {weekly_picks.length === 0 ? (
            <p className="text-slate-500 text-center py-8">No picks available. Run weekly screening.</p>
          ) : (
            <div className="space-y-3">
              {weekly_picks.map((pick, i) => (
                <div key={i} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg card-hover">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-slate-700 flex items-center justify-center font-bold text-sm">
                      {i + 1}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{pick.stock.symbol}</span>
                        <span className="text-xs text-slate-500">{pick.stock.name}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-1">
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                          pick.recommendation === 'BUY' ? 'bg-green-500/20 text-green-400' :
                          pick.recommendation === 'WATCH' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-slate-500/20 text-slate-400'
                        }`}>
                          {pick.recommendation}
                        </span>
                        <span className="text-xs text-slate-500">{pick.stock.sector}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <ScoreCard score={pick.stock.overall_score} size="sm" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="glass rounded-xl p-6 text-center">
            <h3 className="text-sm font-medium text-slate-400 mb-4">Portfolio Health</h3>
            <ScoreCard score={stats.avg_overall_score} size="lg" subtitle="Avg Overall Score" />
          </div>

          {/* Recent Alerts */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              Recent Alerts
            </h3>
            {recent_alerts.length === 0 ? (
              <p className="text-slate-500 text-sm">No active alerts</p>
            ) : (
              <div className="space-y-3">
                {recent_alerts.slice(0, 5).map((alert) => (
                  <div key={alert.id} className={`p-3 rounded-lg border ${
                    alert.severity === 'critical' ? 'bg-red-500/10 border-red-500/20' :
                    alert.severity === 'high' ? 'bg-orange-500/10 border-orange-500/20' :
                    'bg-slate-800/50 border-slate-700'
                  }`}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`w-2 h-2 rounded-full ${
                        alert.severity === 'critical' ? 'bg-red-400' :
                        alert.severity === 'high' ? 'bg-orange-400' :
                        'bg-yellow-400'
                      }`} />
                      <span className="text-xs font-medium text-slate-300">{alert.stock_symbol}</span>
                    </div>
                    <p className="text-xs text-slate-400">{alert.title}</p>
                  </div>
                ))}
              </div>
            )}
            <Link to="/alerts" className="block text-center text-sm text-blue-400 mt-4 hover:text-blue-300">
              View All Alerts →
            </Link>
          </div>
        </div>
      </div>

      {/* Sentiment Trend */}
      {sentiment_overview.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Newspaper className="w-5 h-5 text-blue-400" />
            News Sentiment Trend (Last 7 Days)
          </h3>
          <div className="h-48 flex items-end gap-2">
            {sentiment_overview.map((day, i) => {
              const height = Math.max(((day.avg_sentiment + 1) / 2) * 100, 5)
              const color = day.avg_sentiment >= 0 ? '#22c55e' : '#ef4444'
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div
                    className="w-full rounded-t transition-all duration-500"
                    style={{ height: `${height}%`, backgroundColor: color, opacity: 0.7 }}
                  />
                  <span className="text-xs text-slate-500">{day.date.slice(5)}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="glass rounded-xl p-4 card-hover">
      <div className="flex items-center justify-between mb-2">
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-slate-400">{label}</p>
    </div>
  )
}

export default Dashboard
