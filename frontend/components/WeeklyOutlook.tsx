'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface WeeklyOutlookProps {
  outlook: {
    risk_persistence: string
    critical_days: string[]
    monitoring_actions: string[]
  }
  onExplain?: () => void
}

export default function WeeklyOutlook({ outlook, onExplain }: WeeklyOutlookProps) {
  return (
    <section id="outlook" className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-xl p-6 border border-purple-500/30 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-[#e8e8e8] flex items-center gap-2">
          📅 Weekly Outlook & Key Findings
        </h2>
        {onExplain && (
          <button
            onClick={onExplain}
            className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg border border-white/20 text-sm transition-colors"
            aria-label="Ask AI to explain the weekly outlook"
          >
            🤖 AI Explanation
          </button>
        )}
      </div>
      
      <div className="space-y-4">
        <div className="bg-[#2d2d2d] rounded-lg p-4 border border-purple-500/30">
          <h3 className="text-lg font-semibold text-purple-400 mb-2">Risk Persistence</h3>
          <p className="text-[#e8e8e8]">{outlook.risk_persistence}</p>
        </div>

        {outlook.critical_days && outlook.critical_days.length > 0 && (
          <div className="bg-[#2d2d2d] rounded-lg p-4 border border-red-500/30">
            <h3 className="text-lg font-semibold text-red-400 mb-2">⚠️ Critical Days</h3>
            <div className="flex flex-wrap gap-2">
              {outlook.critical_days.map((day, index) => (
                <span key={index} className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm font-medium">
                  {day}
                </span>
              ))}
            </div>
          </div>
        )}

        {outlook.monitoring_actions && outlook.monitoring_actions.length > 0 && (
          <div className="bg-[#2d2d2d] rounded-lg p-4 border border-blue-500/30">
            <h3 className="text-lg font-semibold text-blue-400 mb-2">📋 Recommended Monitoring Actions</h3>
            <ul className="space-y-2">
              {outlook.monitoring_actions.map((action, index) => (
                <li key={index} className="flex items-start gap-2 text-[#e8e8e8]">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  )
}

