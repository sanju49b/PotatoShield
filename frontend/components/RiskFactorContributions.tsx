'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface RiskFactorContributionsProps {
  diseaseRisks: any[]
  selectedDayIndex?: number
}

type ContributionSnapshot = {
  temperature: number
  humidity: number
  precipitation: number
  wind: number
  cloud_cover: number
}

const emptySnapshot: ContributionSnapshot = {
  temperature: 0,
  humidity: 0,
  precipitation: 0,
  wind: 0,
  cloud_cover: 0,
}

export default function RiskFactorContributions({ diseaseRisks, selectedDayIndex = 0 }: RiskFactorContributionsProps) {
  const targetIndex = diseaseRisks?.length ? Math.min(selectedDayIndex, diseaseRisks.length - 1) : 0
  const targetRisk = diseaseRisks?.[targetIndex]
  const contributionPayload = targetRisk?.contributions

  const lateContributions: ContributionSnapshot =
    contributionPayload?.late_blight ??
    (contributionPayload && 'temperature' in contributionPayload ? (contributionPayload as ContributionSnapshot) : emptySnapshot)

  const earlyContributions: ContributionSnapshot =
    contributionPayload?.early_blight ??
    (contributionPayload && 'temperature' in contributionPayload ? (contributionPayload as ContributionSnapshot) : emptySnapshot)

  const chartData = (targetRisk as any)?.chart_data || {}

  const dayLabel = targetRisk?.date
    ? new Date(targetRisk.date).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })
    : 'Selected day'

  const factors = ['temperature', 'humidity', 'precipitation', 'wind', 'cloud_cover']

  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#1a1b24]/95 via-[#11111a]/95 to-[#07070c]/95 p-6 sm:p-8 shadow-[0_40px_70px_rgba(0,0,0,0.6)]">
      <div className="pointer-events-none absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_20%_20%,rgba(248,113,113,0.35),transparent_55%),radial-gradient(circle_at_85%_0%,rgba(251,191,36,0.25),transparent_50%)]" />
      <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-8">
        <div>
          <p className="text-xs uppercase tracking-[0.4em] text-white/50">Factor Pulse</p>
          <h2 className="text-2xl md:text-3xl font-bold text-white flex items-center gap-2">
            📊 Risk Factor Contributions
          </h2>
        </div>
        <p className="text-sm text-white/80 bg-white/5 border border-white/10 rounded-full px-4 py-1">{dayLabel}</p>
      </div>
      
      <div className="relative grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Late Blight Factors */}
        <div className="relative">
          <h3 className="text-lg font-semibold text-red-300 mb-4 flex items-center gap-2">
            <span className="inline-flex h-2 w-2 rounded-full bg-red-400 animate-pulse"></span>
            Late Blight Pressure
          </h3>
          <div className="space-y-3">
            {factors.map((factor, index) => {
              const value = Math.round(lateContributions[factor] || 0)
              return (
                <motion.div
                  key={factor}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-white/80 capitalize tracking-wide">{factor.replace('_', ' ')}</span>
                    <span className="text-sm font-bold text-white">{Math.round(value)}%</span>
                  </div>
                  <div className="h-3.5 bg-white/10 rounded-full overflow-hidden border border-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${value}%` }}
                      transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                      className="h-full bg-gradient-to-r from-red-500 via-pink-500 to-orange-400 shadow-[0_0_15px_rgba(248,113,113,0.55)]"
                    />
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>

        {/* Early Blight Factors */}
        <div className="relative">
          <h3 className="text-lg font-semibold text-amber-200 mb-4 flex items-center gap-2">
            <span className="inline-flex h-2 w-2 rounded-full bg-yellow-300 animate-pulse"></span>
            Early Blight Pulse
          </h3>
          <div className="space-y-3">
            {factors.map((factor, index) => {
              const value = Math.round(earlyContributions[factor] || 0)
              return (
                <motion.div
                  key={factor}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-white/80 capitalize tracking-wide">{factor.replace('_', ' ')}</span>
                    <span className="text-sm font-bold text-white">{Math.round(value)}%</span>
                  </div>
                  <div className="h-3.5 bg-white/10 rounded-full overflow-hidden border border-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${value}%` }}
                      transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                      className="h-full bg-gradient-to-r from-yellow-400 via-amber-300 to-orange-400 shadow-[0_0_12px_rgba(251,191,36,0.55)]"
                    />
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>

      {chartData?.calculation_methodology && (
        <div className="relative mt-8 pt-6 border-t border-white/10">
          <h4 className="text-sm font-semibold text-white/70 mb-2 uppercase tracking-[0.35em]">How it’s computed</h4>
          <p className="text-xs text-white/60 leading-relaxed">{chartData.calculation_methodology}</p>
        </div>
      )}
    </section>
  )
}

