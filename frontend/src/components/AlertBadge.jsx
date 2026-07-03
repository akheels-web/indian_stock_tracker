import React from 'react'
import { AlertTriangle, XCircle, AlertOctagon, Info } from 'lucide-react'

function AlertBadge({ severity, count }) {
  const configs = {
    critical: { icon: XCircle, color: 'bg-red-500/20 text-red-400 border-red-500/30', label: 'Critical' },
    high: { icon: AlertOctagon, color: 'bg-orange-500/20 text-orange-400 border-orange-500/30', label: 'High' },
    medium: { icon: AlertTriangle, color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', label: 'Medium' },
    low: { icon: Info, color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', label: 'Low' },
  }

  const config = configs[severity] || configs.low
  const Icon = config.icon

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${config.color} text-xs font-medium`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{count} {config.label}</span>
    </div>
  )
}

export default AlertBadge
