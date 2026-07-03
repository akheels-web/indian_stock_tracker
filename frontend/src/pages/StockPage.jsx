import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ArrowLeft, TrendingUp, TrendingDown, AlertTriangle, Newspaper, BarChart3 } from 'lucide-react'
import ScoreCard from '../components/ScoreCard.jsx'
import SentimentGauge from '../components/SentimentGauge.jsx'

const API_BASE = '/api'

function StockPage() {
  const { symbol } = useParams()
  const navigate = useNavigate()
  const [stock, setStock] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStockDetail()
  }, [symbol])

  const fetchStockDetail = async () => {
    try {
      // First get stock ID from watchlist
      const listRes = await axios.get(`${API_BASE}/watchlist/stocks`)
      const found = listRes.data.find(s => s.symbol === symbol.toUpperCase())

      if (found) {
        const detailRes = await axios.get(`${API_BASE}/watchlist/stocks/${found.id}`)
        setStock(detailRes.data)
      } else {
        setStock(null)
      }
    } catch (err) {
      console.error('Stock detail error:', err)
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

  if (!stock) {
    return (
      <div className="text-center py-20">
        <p className="text-slate-400 mb-4">Stock not found in watchlist</p>
        <button
          onClick={() => navigate('/watchlist')}
          className="px-4 py-2 bg-blue-600 rounded-lg text-sm font-medium"
        >
          Go to Watchlist
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/watchlist')}
          className="p-2 rounded-lg bg-slate-800/50 hover:bg-slate-700 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-2xl font-bold">{stock.symbol}</h2>
          <p className="text-slate-400 text-sm">{stock.name} • {stock.sector}</p>
        </div>
        <div className="ml-auto">
          <span className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize ${
            stock.status === 'holding' ? 'bg-green-500/20 text-green-400' :
            stock.status === 'watching' ? 'bg-blue-500/20 text-blue-400' :
            'bg-slate-500/20 text-slate-400'
          }`}>
            {stock.status}
          </span>
        </div>
      </div>

      {/* Price & Scores */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Current Price</h3>
            <BarChart3 className="w-5 h-5 text-slate-500" />
          </div>
          <p className="text-3xl font-bold">₹{stock.current_price?.toFixed(2) || 'N/A'}</p>
          {stock.first_tracked_price && (
            <div className="mt-2">
              <p className="text-sm text-slate-400">
                Entry: ₹{stock.first_tracked_price.toFixed(2)}
              </p>
              {stock.stop_loss_price && (
                <div className="flex gap-2 mt-2">
                  <span className="text-xs px-2 py-1 bg-red-500/10 text-red-400 rounded">
                    SL: ₹{stock.stop_loss_price.toFixed(2)}
                  </span>
                  <span className="text-xs px-2 py-1 bg-green-500/10 text-green-400 rounded">
                    TG: ₹{stock.target_price?.toFixed(2)}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="glass rounded-xl p-6 flex justify-around">
          <ScoreCard score={stock.fundamental_score} title="Fundamental" />
          <ScoreCard score={stock.technical_score} title="Technical" />
        </div>

        <div className="glass rounded-xl p-6 flex justify-center">
          <SentimentGauge score={stock.sentiment_score || 0} />
        </div>
      </div>

      {/* Overall Score */}
      <div className="glass rounded-xl p-6 text-center">
        <h3 className="text-lg font-semibold mb-4">Overall Investment Score</h3>
        <div className="flex justify-center">
          <ScoreCard score={stock.overall_score} size="lg" />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <Metric label="P/E Ratio" value={stock.pe_ratio?.toFixed(1)} />
          <Metric label="ROE" value={stock.roe ? `${stock.roe.toFixed(1)}%` : null} />
          <Metric label="Debt/Equity" value={stock.debt_equity?.toFixed(2)} />
          <Metric label="Volatility" value={stock.volatility ? `${stock.volatility.toFixed(1)}%` : null} />
        </div>
      </div>

      {/* News Section */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Newspaper className="w-5 h-5 text-blue-400" />
          Recent News & Sentiment
        </h3>
        {stock.news_articles?.length === 0 ? (
          <p className="text-slate-500 text-center py-8">No news articles yet. Run daily scan.</p>
        ) : (
          <div className="space-y-3">
            {stock.news_articles?.slice(0, 10).map((article) => (
              <div key={article.id} className="p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <a href={article.url} target="_blank" rel="noopener noreferrer"
                      className="font-medium hover:text-blue-400 transition-colors">
                      {article.title}
                    </a>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs text-slate-500">{article.source}</span>
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        article.sentiment_label === 'positive' ? 'bg-green-500/20 text-green-400' :
                        article.sentiment_label === 'negative' ? 'bg-red-500/20 text-red-400' :
                        'bg-slate-500/20 text-slate-400'
                      }`}>
                        {article.sentiment_label} ({article.sentiment_score?.toFixed(2)})
                      </span>
                      {article.risk_flags?.length > 0 && (
                        <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400">
                          ⚠️ {article.risk_flags.join(', ')}
                        </span>
                      )}
                    </div>
                    {article.summary && (
                      <p className="text-sm text-slate-400 mt-2">{article.summary}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alerts */}
      {stock.alerts?.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            Active Alerts
          </h3>
          <div className="space-y-2">
            {stock.alerts.filter(a => a.is_active).map((alert) => (
              <div key={alert.id} className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="font-medium text-red-400">{alert.title}</p>
                <p className="text-sm text-slate-400">{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div className="text-center">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-lg font-semibold">{value || 'N/A'}</p>
    </div>
  )
}

export default StockPage
