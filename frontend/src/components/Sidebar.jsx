import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, List, Bell, FileText, Settings, TrendingUp, ShieldAlert } from 'lucide-react'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/watchlist', icon: List, label: 'Watchlist' },
  { path: '/alerts', icon: Bell, label: 'Alerts' },
  { path: '/reports', icon: FileText, label: 'Reports' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 glass flex flex-col border-r border-slate-800">
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight">Stock Tracker</h1>
            <p className="text-xs text-slate-400">Indian Markets</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="glass rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            <span className="text-xs font-semibold text-red-400">Risk Disclaimer</span>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            This tool is for analysis only. Not financial advice. Always do your own research before investing.
          </p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
