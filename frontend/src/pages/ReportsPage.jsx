import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { FileText, TrendingUp, TrendingDown, Calendar } from 'lucide-react'
import ScoreCard from '../components/ScoreCard.jsx'

const API_BASE = '/api'

function ReportsPage() {
  const [reports, setReports] = useState([])
  const [performance, setPerformance] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchReports()
    fetchPerformance()
  }, [])

  const fetchReports = async () => {
    try {
      const res = await axios.get(`${API_BASE}/reports/weekly`)
      setReports(res.data)
    } catch (err) {
      console.error('Reports error:', err)
    }
  }

  const fetchPerformance = async () => {
    try {
      const res = await axios.get(`${API_BASE}/reports/performance`)
      setPerformance(res.data)
    } catch (err) {
      console.error('Performance error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold gradient-text">Reports</h2>
        <p className="text-slate-400 text-sm mt-1">Weekly screening reports and portfolio performance</p>
      </div>

      {/* Performance Summary */}
      {performance && performance.holdings.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Portfolio Performance</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-xs text-slate-500">Total Invested</p>
              <p className="text-xl font-bold">₹{performance.total_invested.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Current Value</p>
              <p className="text-xl font-bold">₹{performance.total_current.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Unrealized P&L</p>
              <p className={`text-xl font-bold ${performance.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ₹{performance.unrealized_pnl.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500">P&L %</p>
              <p className={`text-xl font-bold ${performance.unrealized_pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {performance.unrealized_pnl_pct >= 0 ? '+' : ''}{performance.unrealized_pnl_pct}%
              </p>
            </div>
          </div>
          <div className="space-y-2">
            {performance.holdings.map((h) => (
              <div key={h.symbol} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <span className="font-medium">{h.symbol}</span>
                  <span className="text-xs text-slate-500 ml-2">
                    ₹{h.entry} → ₹{h.current}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500">SL: ₹{h.stop_loss} | TG: ₹{h.target}</span>
                  <span className={`font-semibold ${h.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {h.pnl_pct >= 0 ? '+' : ''}{h.pnl_pct}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weekly Reports */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-400" />
          Weekly Screening Reports
        </h3>
        {reports.length === 0 ? (
          <p className="text-slate-500 text-center py-8">No reports yet. Run weekly screening first.</p>
        ) : (
          <div className="space-y-3">
            {reports.slice(0, 20).map((report) => (
              <div key={report.id} className="p-4 bg-slate-800/50 rounded-lg card-hover">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center">
                      <ScoreCard score={report.weekly_overall_score} size="sm" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{report.stock_symbol}</span>
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                          report.recommendation === 'BUY' ? 'bg-green-500/20 text-green-400' :
                          report.recommendation === 'WATCH' ? 'bg-yellow-500/20 text-yellow-400' :
                          report.recommendation === 'SELL' ? 'bg-red-500/20 text-red-400' :
                          'bg-slate-500/20 text-slate-400'
                        }`}>
                          {report.recommendation}
                        </span>
                      </div>
                      <p className="text-sm text-slate-400 mt-1">{report.reasoning}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(report.week_start).toLocaleDateString()}
                        </span>
                        <span>Confidence: {(report.confidence * 100).toFixed(0)}%</span>
                        <span className="text-green-400">+{report.positive_news} news</span>
                        <span className="text-red-400">-{report.negative_news} news</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ReportsPage
