'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'

interface ForecastCardsProps {
  weatherData: any[]
  soilData: any[]
  diseaseRisks: any[]
  onExplainDay?: (payload: { date: string; risk: { late: number; early: number } }) => void
  onHoverDay?: (index: number | null) => void
  onSelectDay?: (index: number) => void
  activeIndex?: number
}

export default function ForecastCards({
  weatherData,
  soilData,
  diseaseRisks,
  onExplainDay,
  onHoverDay,
  onSelectDay,
  activeIndex = 0,
}: ForecastCardsProps) {
  const getRiskColor = (risk: number) => {
    if (risk > 75) return 'from-red-600 to-red-800'
    if (risk > 50) return 'from-orange-500 to-orange-700'
    if (risk > 25) return 'from-yellow-500 to-yellow-700'
    return 'from-green-500 to-green-700'
  }

  const getRiskLabel = (risk: number) => {
    if (risk > 75) return 'Critical'
    if (risk > 50) return 'High'
    if (risk > 25) return 'Moderate'
    return 'Low'
  }

  const getSoilStatus = (moisture: number) => {
    if (moisture < 0.3) return { label: 'Dry', color: 'text-yellow-400' }
    if (moisture > 0.7) return { label: 'Wet', color: 'text-blue-400' }
    return { label: 'Optimal', color: 'text-green-400' }
  }

  const getRiskHex = (risk: number) => {
    if (risk > 75) return '#ef4444' // red-500
    if (risk > 50) return '#f97316' // orange-500
    if (risk > 25) return '#eab308' // yellow-500
    return '#22c55e' // green-500
  }

  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)

  return (
    <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a] shadow-xl">
      <h2 className="text-2xl font-bold text-[#e8e8e8] mb-6 flex items-center gap-2">
        📅 8-Day Forecast
      </h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        {weatherData.slice(0, 8).map((day, index) => {
          const lb = diseaseRisks[index]?.late_blight_pct || 0
          const eb = diseaseRisks[index]?.early_blight_pct || 0
          const risk = Math.max(lb, eb)
          const soil = soilData[index]?.soil_moisture_percent || 0
          const date = new Date(day.date)
          const dayName = date.toLocaleDateString('en-US', { weekday: 'short' })
          const dayLabel = date.toLocaleDateString('en-US', { day: '2-digit' })
          const month = date.toLocaleDateString('en-US', { month: 'short' })
          const ringColor = getRiskHex(risk)
          const isActive = activeIndex === index
          
          const soilStatus = getSoilStatus(soil)

          return (
            <motion.button
              key={index}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              type="button"
              aria-pressed={isActive}
              title={`Forecast for ${dayName} ${dayLabel} ${month}`}
              className="relative group focus:outline-none"
              onClick={() => {
                setSelectedIndex(index)
                onSelectDay?.(index)
              }}
              onMouseEnter={() => onHoverDay && onHoverDay(index)}
              onMouseLeave={() => onHoverDay && onHoverDay(null)}
            >
              <div
                className={`relative w-32 h-32 rounded-full bg-gradient-to-br ${getRiskColor(risk)} p-1 transition-transform duration-300 ${
                  isActive ? 'scale-105 shadow-[0_0_30px_rgba(239,68,68,0.35)]' : 'hover:scale-105 shadow-[0_0_25px_rgba(255,255,255,0.08)]'
                }`}
              >
                {/* Animated conic progress ring */}
                <div
                  className="absolute inset-0 rounded-full animate-spin-slower"
                  style={{
                    backgroundImage: `conic-gradient(${ringColor} ${Math.max(6, Math.min(100, risk))}%, rgba(0,0,0,0) 0)`,
                    WebkitMaskImage: 'radial-gradient(circle, transparent 62%, black 66%)',
                    maskImage: 'radial-gradient(circle, transparent 62%, black 66%)',
                    opacity: 0.9,
                  }}
                />
                <div className="w-full h-full rounded-full bg-[#0f0f10] p-3 flex flex-col items-center justify-center ring-1 ring-white/10 relative overflow-hidden">
                  <div className="absolute inset-0 rounded-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/5 via-transparent to-transparent pointer-events-none"></div>
                  {/* Date */}
                  <div className="flex flex-col items-center mb-1">
                    <div className="text-[11px] font-semibold text-[#f8fafc] uppercase tracking-wide">{dayName}</div>
                    <div className="text-[11px] text-[#a0a0a0]">{dayLabel} {month}</div>
                  </div>

                  <div className="text-[10px] text-[#fca5a5] font-semibold mb-1">{getRiskLabel(risk)}</div>

                  {/* Temperature - cleaner display */}
                  <div className="text-[12px] text-[#ffcf7a] mb-1 font-semibold">
                    🌡️ {Math.round(day.temp_avg)}°C
                  </div>
                  <div className="text-[9px] text-[#808080] mb-1">
                    {Math.round(day.temp_min)}°-{Math.round(day.temp_max)}°
                  </div>

                  {/* Humidity */}
                  <div className="text-[11px] text-[#7ad0ff] mb-1">
                    💧 {Math.round(day.humidity_avg)}%
                  </div>

                  {/* Soil Moisture */}
                  <div className={`text-[11px] ${soilStatus.color} mb-1`}>
                    🌱 {Math.round(soil * 100)}% <span className="text-[#9f9f9f]">({soilStatus.label})</span>
                  </div>

                  {/* Show only highest risk disease */}
                  {(() => {
                    const highestRisk = Math.max(lb, eb)
                    const isLateBlightHighest = lb >= eb
                    return (
                      <div className="mt-1">
                        <div className={`px-2 py-1 rounded text-[10px] font-bold text-center ${
                          isLateBlightHighest 
                            ? 'bg-red-500/20 text-red-300 border border-red-500/40' 
                            : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40'
                        }`}>
                          {isLateBlightHighest ? '🔴' : '🟡'} {isLateBlightHighest ? 'LB' : 'EB'} {Math.round(highestRisk)}%
                        </div>
                      </div>
                    )
                  })()}
                </div>

                {/* Risk Fill Overlay */}
                <div
                  className={`absolute inset-0 rounded-full pointer-events-none`}
                  style={{ boxShadow: `0 0 ${8 + Math.round(risk / 10)}px ${risk > 75 ? 'rgba(239,68,68,0.35)' : risk > 50 ? 'rgba(249,115,22,0.35)' : risk > 25 ? 'rgba(234,179,8,0.3)' : 'rgba(34,197,94,0.25)'}` }}
                />
              </div>

              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                <div className="bg-[#1a1a1a] border border-[#3a3a3a] rounded-lg p-3 shadow-xl min-w-[200px]">
                  <div className="text-sm font-bold text-[#e8e8e8] mb-2">{dayName}, {dayLabel} {month}</div>
                  <div className="space-y-1 text-xs">
                    <div>🌡️ Temp: {Math.round(day.temp_min)}° - {Math.round(day.temp_max)}°C (Avg: {Math.round(day.temp_avg)}°C)</div>
                    <div>💧 Humidity: {Math.round(day.humidity_avg)}%</div>
                    <div>🌧️ Precipitation: {Math.round(day.precipitation)}mm</div>
                    <div>💨 Wind: {Math.round(day.wind_speed)} km/h</div>
                    <div>🌱 Soil: {Math.round(soil * 100)}% ({soilStatus.label})</div>
                    <div className="pt-2 border-t border-[#3a3a3a]">
                      {(() => {
                        const lb = Math.round(diseaseRisks[index]?.late_blight_pct || 0)
                        const eb = Math.round(diseaseRisks[index]?.early_blight_pct || 0)
                        const highest = Math.max(lb, eb)
                        const isLateBlightHighest = lb >= eb
                        return (
                          <>
                            <div className={`font-bold ${isLateBlightHighest ? 'text-red-400' : 'text-yellow-400'}`}>
                              {isLateBlightHighest ? '🔴' : '🟡'} {isLateBlightHighest ? 'Late' : 'Early'} Blight: {highest}%
                            </div>
                            <div className="text-xs text-[#808080] mt-1">
                              {isLateBlightHighest ? `Early Blight: ${eb}%` : `Late Blight: ${lb}%`}
                            </div>
                            <div className="text-[10px] text-purple-300/70 mt-2 pt-2 border-t border-[#3a3a3a]">
                              📊 Calculated using 7-day sliding window
                            </div>
                          </>
                        )
                      })()}
                    </div>
                  </div>
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>

      {/* Expanded Detail Modal */}
      {selectedIndex !== null && weatherData[selectedIndex] && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
          <div className="bg-[#1f1f1f] rounded-2xl border border-[#3a3a3a] shadow-2xl w-full max-w-lg">
            <div className="p-4 border-b border-[#3a3a3a] flex items-center justify-between">
              <div className="text-lg font-semibold text-[#e8e8e8]">
                {new Date(weatherData[selectedIndex].date).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
              </div>
              <button
                onClick={() => setSelectedIndex(null)}
                className="text-[#b8b8b8] hover:text-[#e8e8e8]"
                aria-label="Close"
              >
                ✖
              </button>
            </div>
            <div className="p-4 space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-[#2a2a2a] rounded-lg p-3 border border-[#3a3a3a]">
                  <div className="text-xs text-[#b8b8b8]">Temp (min/avg/max)</div>
                  <div className="text-sm font-semibold text-[#e8e8e8]">
                    {Math.round(weatherData[selectedIndex].temp_min)}° / {Math.round(weatherData[selectedIndex].temp_avg)}° / {Math.round(weatherData[selectedIndex].temp_max)}°C
                  </div>
                </div>
                <div className="bg-[#2a2a2a] rounded-lg p-3 border border-[#3a3a3a]">
                  <div className="text-xs text-[#b8b8b8]">Humidity</div>
                  <div className="text-sm font-semibold text-[#e8e8e8]">
                    {Math.round(weatherData[selectedIndex].humidity_avg)}%
                  </div>
                </div>
                <div className="bg-[#2a2a2a] rounded-lg p-3 border border-[#3a3a3a]">
                  <div className="text-xs text-[#b8b8b8]">Soil Moisture</div>
                  <div className="text-sm font-semibold text-[#e8e8e8]">
                    {Math.round((soilData[selectedIndex]?.soil_moisture_percent || 0) * 100)}%
                  </div>
                </div>
              </div>
              {(() => {
                const lb = Math.round(diseaseRisks[selectedIndex]?.late_blight_pct || 0)
                const eb = Math.round(diseaseRisks[selectedIndex]?.early_blight_pct || 0)
                const highest = Math.max(lb, eb)
                const isLateBlightHighest = lb >= eb
                return (
                  <div className="bg-gradient-to-br from-[#2a2a2a] to-[#1f1f1f] rounded-lg p-4 border-2 border-white/10">
                    <div className="text-xs text-[#b8b8b8] mb-2 uppercase tracking-wider">Primary Disease Risk</div>
                    <div className={`text-4xl font-black mb-2 ${isLateBlightHighest ? 'text-red-400' : 'text-yellow-400'}`}>
                      {highest}%
                    </div>
                    <div className="text-lg font-semibold text-[#e8e8e8] mb-2">
                      {isLateBlightHighest ? '🔴 Late Blight' : '🟡 Early Blight'}
                    </div>
                    <div className="text-xs text-[#808080]">
                      {isLateBlightHighest ? `Early Blight: ${eb}%` : `Late Blight: ${lb}%`}
                    </div>
                  </div>
                )
              })()}
            </div>
            <div className="p-4 border-t border-[#3a3a3a] flex items-center justify-end gap-2">
              {onExplainDay && (
                <button
                    onClick={() => {
                    const day = weatherData[selectedIndex]
                    onExplainDay({
                      date: day.date,
                      risk: {
                        late: Math.round(diseaseRisks[selectedIndex]?.late_blight_pct || 0),
                          early: Math.round(diseaseRisks[selectedIndex]?.early_blight_pct || 0)
                      }
                    })
                  }}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg border border-white/20 transition-colors"
                >
                  🤖 Ask AI
                </button>
              )}
              <button
                onClick={() => setSelectedIndex(null)}
                className="px-4 py-2 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-[#e8e8e8] rounded-lg border border-[#3a3a3a] transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

