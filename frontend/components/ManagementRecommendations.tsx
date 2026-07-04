'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'

interface ManagementRecommendationsProps {
  recommendations: {
    immediate_actions: string[]
    preventive_measures: string[]
    cultural_practices: string[]
  }
  criticalDays: string[]
  lateBlightRisk?: number
  earlyBlightRisk?: number
}

export default function ManagementRecommendations({ recommendations, criticalDays, lateBlightRisk = 0, earlyBlightRisk = 0 }: ManagementRecommendationsProps) {
  const [expanded, setExpanded] = useState(true)
  
  // Determine which disease has the highest risk
  const highestRisk = Math.max(lateBlightRisk, earlyBlightRisk)
  const isLateBlightHighest = lateBlightRisk >= earlyBlightRisk
  const dominantDisease = isLateBlightHighest ? 'Late Blight' : 'Early Blight'

  return (
    <section id="recommendations" className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a] shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-[#e8e8e8] flex items-center gap-2">
            💊 Management Recommendations
          </h2>
          <p className="text-sm text-[#b8b8b8] mt-1">
            Focused on {dominantDisease} ({Math.round(highestRisk)}% risk)
          </p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="px-4 py-2 bg-[#3a3a3a] hover:bg-[#4a4a4a] rounded-lg text-[#e8e8e8] transition-colors"
        >
          {expanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      {expanded && (
        <div className="space-y-6">
          {/* Immediate Actions */}
          {recommendations.immediate_actions && recommendations.immediate_actions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border-l-4 border-red-500 rounded-lg p-4"
            >
              <h3 className="text-lg font-semibold text-red-400 mb-3">🚨 Immediate Actions</h3>
              <ul className="space-y-2">
                {recommendations.immediate_actions.map((action, index) => (
                  <li key={index} className="flex items-start gap-2 text-[#e8e8e8]">
                    <span className="text-red-400 mt-1">•</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
              {criticalDays.length > 0 && (
                <div className="mt-3 text-sm text-red-400 font-medium">
                  Critical Days: {criticalDays.join(', ')}
                </div>
              )}
            </motion.div>
          )}

          {/* Preventive Measures */}
          {recommendations.preventive_measures && recommendations.preventive_measures.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-yellow-500/10 border-l-4 border-yellow-500 rounded-lg p-4"
            >
              <h3 className="text-lg font-semibold text-yellow-400 mb-3">🛡️ Preventive Measures</h3>
              <ul className="space-y-2">
                {recommendations.preventive_measures.map((measure, index) => (
                  <li key={index} className="flex items-start gap-2 text-[#e8e8e8]">
                    <span className="text-yellow-400 mt-1">•</span>
                    <span>{measure}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          )}

          {/* Cultural Practices */}
          {recommendations.cultural_practices && recommendations.cultural_practices.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-green-500/10 border-l-4 border-green-500 rounded-lg p-4"
            >
              <h3 className="text-lg font-semibold text-green-400 mb-3">🌾 Cultural Practices</h3>
              <ul className="space-y-2">
                {recommendations.cultural_practices.map((practice, index) => (
                  <li key={index} className="flex items-start gap-2 text-[#e8e8e8]">
                    <span className="text-green-400 mt-1">•</span>
                    <span>{practice}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>
      )}
    </section>
  )
}

