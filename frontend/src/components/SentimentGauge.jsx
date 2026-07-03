import React from 'react'

function SentimentGauge({ score }) {
  // score is -1 to +1
  const percentage = ((score + 1) / 2) * 100

  const getLabel = (s) => {
    if (s >= 0.5) return { text: 'Very Positive', color: '#22c55e' }
    if (s >= 0.2) return { text: 'Positive', color: '#4ade80' }
    if (s >= -0.2) return { text: 'Neutral', color: '#94a3b8' }
    if (s >= -0.5) return { text: 'Negative', color: '#f97316' }
    return { text: 'Very Negative', color: '#ef4444' }
  }

  const label = getLabel(score)

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-24 overflow-hidden">
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full"
          style={{
            background: `conic-gradient(from 180deg, #ef4444 0deg, #f97316 60deg, #eab308 90deg, #22c55e 120deg, #16a34a 180deg)`,
          }}
        />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-32 h-32 bg-slate-900 rounded-full" />
        <div
          className="absolute bottom-0 left-1/2 w-1 h-20 bg-white origin-bottom transition-transform duration-700"
          style={{ transform: `translateX(-50%) rotate(${(percentage - 50) * 1.8}deg)` }}
        />
        <div className="absolute bottom-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full" />
      </div>
      <div className="text-center mt-2">
        <span className="text-lg font-bold" style={{ color: label.color }}>
          {label.text}
        </span>
        <p className="text-xs text-slate-500">Score: {score.toFixed(2)}</p>
      </div>
    </div>
  )
}

export default SentimentGauge
