import React from 'react'

function ScoreCard({ title, score, maxScore = 100, size = 'md', subtitle }) {
  const percentage = Math.min(Math.max((score / maxScore) * 100, 0), 100)

  const getColor = (pct) => {
    if (pct >= 70) return '#22c55e'
    if (pct >= 50) return '#eab308'
    if (pct >= 30) return '#f97316'
    return '#ef4444'
  }

  const color = getColor(percentage)
  const circumference = 2 * Math.PI * 36
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const sizes = {
    sm: { w: 80, font: 'text-lg' },
    md: { w: 120, font: 'text-2xl' },
    lg: { w: 160, font: 'text-3xl' },
  }

  const { w, font } = sizes[size] || sizes.md

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: w, height: w }}>
        <svg width={w} height={w} viewBox="0 0 80 80" className="transform -rotate-90">
          <circle cx="40" cy="40" r="36" fill="none" stroke="#1e293b" strokeWidth="6" />
          <circle
            cx="40" cy="40" r="36" fill="none"
            stroke={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold ${font}`} style={{ color }}>
            {Math.round(score)}
          </span>
        </div>
      </div>
      <p className="text-sm font-medium text-slate-300 mt-2">{title}</p>
      {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
    </div>
  )
}

export default ScoreCard
