import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'
import { Search, Plus, Filter, ArrowUpDown, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import ScoreCard from '../components/ScoreCard.jsx'

const API_BASE = '/api'

function WatchlistPage() {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [newSymbol, setNewSymbol] = useState('')

  useEffect(() => {
    fetchStocks()
  }, [filter])

  const fetchStocks = async () => {
    try {
      const params = {}
      if (filter !== 'all') params.status = filter

      const res = await axios.get(`${API_BASE}/watchlist/stocks`, { params })
      setStocks(res.data)
    } catch (err) {
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const addStock = async () => {
    if (!newSymbol) return
    try {
      await axios.post(`${API_BASE}/watchlist/stocks?symbol=${newSymbol.toUpperCase()}`)
      setNewSymbol('')
      fetchStocks()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add stock')
    }
  }

  const filteredStocks = stocks.filter(s =>
    s.symbol.toLowerCase().includes(search.toLowerCase()) ||
    (s.name && s.name.toLowerCase().includes(search.toLowerCase()))
  )

  const getStatusColor = (status) => {
    const colors = {
      watching: 'bg-blue-500/20 text-blue-400',
      holding: 'bg-green-500/20 text-green-400',
      exited: 'bg-slate-500/20 text-slate-400',
      rejected: 'bg-red-500/20 text-red-400',
    }
    return colors[status] || colors.watching
  }

  const getTrendIcon = (score) => {
    if (score >= 70) return <TrendingUp className="w-4 h-4 text-green-400" />
    if (score <= 40) return <TrendingDown className="w-4 h-4 text-red-400" />
    return <Minus className="w-4 h-4 text-yellow-400" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text">Watchlist</h2>
          <p className="text-slate-400 text-sm mt-1">Track and manage your Indian stock universe</p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search stocks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex gap-2">
          {['all', 'watching', 'holding', 'exited'].map((f) => (
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
      </div>

      {/* Add Stock */}
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Enter symbol (e.g., RELIANCE.NS)"
          value={newSymbol}
          onChange={(e) => setNewSymbol(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addStock()}
          className="flex-1 px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={addStock}
          className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Stock
        </button>
      </div>

      {/* Stock Grid */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
        </div>
      ) : filteredStocks.length === 0 ? (
        <div className="text-center py-20 text-slate-500">
          <Filter className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No stocks found. Add stocks to start tracking.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredStocks.map((stock) => (
            <div key={stock.id} className="glass rounded-xl p-5 card-hover">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <Link to={`/stock/${stock.symbol}`} className="text-lg font-bold hover:text-blue-400 transition-colors">
                    {stock.symbol}
                  </Link>
                  <p className="text-xs text-slate-500 mt-0.5">{stock.name}</p>
                </div>
                <div className="flex items-center gap-2">
                  {getTrendIcon(stock.overall_score)}
                  <span className={`text-xs px-2 py-1 rounded-full font-medium capitalize ${getStatusColor(stock.status)}`}>
                    {stock.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <ScoreCard score={stock.fundamental_score} size="sm" title="Fundamental" />
                </div>
                <div className="text-center">
                  <ScoreCard score={stock.technical_score} size="sm" title="Technical" />
                </div>
                <div className="text-center">
                  <ScoreCard score={(stock.sentiment_score + 1) * 50} size="sm" title="Sentiment" />
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                <div>
                  <p className="text-xs text-slate-500">Overall Score</p>
                  <p className={`text-xl font-bold ${
                    stock.overall_score >= 70 ? 'text-green-400' :
                    stock.overall_score >= 50 ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {stock.overall_score}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500">Price</p>
                  <p className="text-sm font-medium">₹{stock.current_price?.toFixed(2) || 'N/A'}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500">P/E</p>
                  <p className="text-sm font-medium">{stock.pe_ratio?.toFixed(1) || 'N/A'}</p>
                </div>
              </div>

              {stock.stop_loss_price && (
                <div className="mt-3 flex gap-2 text-xs">
                  <span className="px-2 py-1 bg-red-500/10 text-red-400 rounded">
                    SL: ₹{stock.stop_loss_price.toFixed(2)}
                  </span>
                  <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded">
                    TG: ₹{stock.target_price?.toFixed(2)}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default WatchlistPage
