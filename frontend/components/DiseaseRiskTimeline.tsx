'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'

interface DiseaseRiskTimelineProps {
  diseaseRisks: any[]
  selectedIndex?: number
  onSelectDay?: (index: number) => void
}

export default function DiseaseRiskTimeline({ diseaseRisks, selectedIndex = 0, onSelectDay }: DiseaseRiskTimelineProps) {
  // Determine which disease is dominant overall
  const getDominantDisease = () => {
    if (diseaseRisks.length === 0) return { lateBlight: true, earlyBlight: false }
    const avgLate = diseaseRisks.reduce((sum, r) => sum + (r.late_blight_pct || 0), 0) / diseaseRisks.length
    const avgEarly = diseaseRisks.reduce((sum, r) => sum + (r.early_blight_pct || 0), 0) / diseaseRisks.length
    return {
      lateBlight: avgLate >= avgEarly,
      earlyBlight: avgEarly > avgLate
    }
  }
  
  const [visibleSeries, setVisibleSeries] = useState(getDominantDisease())

  const maxRiskRaw = diseaseRisks.length
    ? Math.max(
        ...diseaseRisks.map((r) =>
          Math.max(r.late_blight_pct || 0, r.early_blight_pct || 0)
        )
      )
    : 100
  const maxRisk = Math.max(1, maxRiskRaw)

  return (
    <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a] shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-[#e8e8e8] flex items-center gap-2">
          📈 Disease Risk Timeline
        </h2>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setVisibleSeries({ ...visibleSeries, lateBlight: !visibleSeries.lateBlight })}
            className={`px-4 py-2 rounded-full text-sm font-semibold transition ${
              visibleSeries.lateBlight
                ? 'bg-gradient-to-r from-red-500 to-orange-400 text-white shadow-lg shadow-red-500/30'
                : 'bg-white/10 text-white/70 border border-white/10'
            }`}
          >
            🔴 Late Blight
          </button>
          <button
            type="button"
            onClick={() => setVisibleSeries({ ...visibleSeries, earlyBlight: !visibleSeries.earlyBlight })}
            className={`px-4 py-2 rounded-full text-sm font-semibold transition ${
              visibleSeries.earlyBlight
                ? 'bg-gradient-to-r from-amber-400 to-yellow-300 text-black shadow-lg shadow-yellow-300/30'
                : 'bg-white/10 text-white/70 border border-white/10'
            }`}
          >
            🟡 Early Blight
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {diseaseRisks.map((risk, index) => {
          const date = new Date(risk.date)
          const dayName = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
          const isActive = selectedIndex === index

          return (
            <motion.button
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              type="button"
              aria-pressed={isActive}
              onClick={() => onSelectDay?.(index)}
              className={`flex items-center gap-4 w-full px-3 py-2 rounded-lg transition-colors ${
                isActive ? 'bg-[#3a3a3a]/50 border border-[#ff6b6b]/40' : 'hover:bg-[#3a3a3a]/30'
              }`}
            >
              <div className="w-24 text-xs text-[#b8b8b8]">{dayName}</div>
              <div className="flex-1 flex items-center gap-2">
                {visibleSeries.lateBlight && (
                  <div className="relative flex-1 h-8 bg-[#3a3a3a] rounded overflow-hidden">
                    <div
                      className="h-full bg-red-500"
                      style={{ width: `${((risk.late_blight_pct || 0) / maxRisk) * 100}%` }}
                    />
                    <div className="absolute inset-0 flex items-center px-2 text-xs text-white font-medium">
                      {Math.round(risk.late_blight_pct || 0)}%
                    </div>
                  </div>
                )}
                {visibleSeries.earlyBlight && (
                  <div className="relative flex-1 h-8 bg-[#3a3a3a] rounded overflow-hidden">
                    <div
                      className="h-full bg-yellow-500"
                      style={{ width: `${((risk.early_blight_pct || 0) / maxRisk) * 100}%` }}
                    />
                    <div className="absolute inset-0 flex items-center px-2 text-xs text-white font-medium">
                      {Math.round(risk.early_blight_pct || 0)}%
                    </div>
                  </div>
                )}
              </div>
            </motion.button>
          )
        })}
      </div>
    </section>
  )
}

