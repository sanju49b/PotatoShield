'use client'

import React, { useMemo } from 'react'
import { motion } from 'framer-motion'

interface ChartData {
  risk_timeline?: {
    dates: string[]
    late_blight_risk: number[]
    early_blight_risk: number[]
    overall_risk: number[]
  }
  temperature_trend?: {
    dates: string[]
    min_temp: number[]
    max_temp: number[]
    avg_temp: number[]
  }
  humidity_trend?: {
    dates: string[]
    min_humidity: number[]
    max_humidity: number[]
    avg_humidity: number[]
  }
  risk_factor_contributions?: {
    late_blight: {
      temperature: number
      humidity: number
      precipitation: number
      wind: number
      cloud_cover: number
    }
    early_blight: {
      temperature: number
      humidity: number
      precipitation: number
      wind: number
      cloud_cover: number
    }
  }
  risk_matrix?: {
    probability: number
    impact: string
    risk_score: number
  }
  final_risk_percentage?: {
    late_blight: number
    early_blight: number
    overall: number
  }
  calculation_methodology?: string
}

interface ChartAgentProps {
  chartData: ChartData | null
}

export default function ChartAgent({ chartData }: ChartAgentProps) {
  // Debug: Log chart data when it changes
  React.useEffect(() => {
    if (chartData) {
      console.log('[ChartAgent] Chart data received:', {
        has_risk_timeline: !!chartData.risk_timeline,
        has_temperature_trend: !!chartData.temperature_trend,
        has_humidity_trend: !!chartData.humidity_trend,
        risk_timeline: chartData.risk_timeline ? {
          dates_count: chartData.risk_timeline.dates?.length || 0,
          late_blight_count: chartData.risk_timeline.late_blight_risk?.length || 0,
          early_blight_count: chartData.risk_timeline.early_blight_risk?.length || 0,
          overall_risk_count: chartData.risk_timeline.overall_risk?.length || 0,
          late_blight_sample: chartData.risk_timeline.late_blight_risk?.slice(0, 3),
          early_blight_sample: chartData.risk_timeline.early_blight_risk?.slice(0, 3),
          overall_risk_sample: chartData.risk_timeline.overall_risk?.slice(0, 3),
        } : null,
      })
    }
  }, [chartData])

  if (!chartData) return null

  // Risk Matrix Visualization
  const RiskMatrix = () => {
    if (!chartData.risk_matrix) return null

    const { probability, impact, risk_score } = chartData.risk_matrix
    const impactLevels = { low: 1, medium: 2, high: 3, critical: 4 }
    const impactValue = impactLevels[impact.toLowerCase() as keyof typeof impactLevels] || 2

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-[#2d2d2d] border border-[#3a3a3a] rounded-2xl p-6 shadow-lg mb-6"
      >
        <h3 className="text-xl font-semibold text-[#e8e8e8] mb-4" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
          Risk Matrix: Probability vs Impact
        </h3>
        <div className="relative w-full h-64 bg-[#1a1a1a] rounded-lg border border-[#3a3a3a] p-4">
          {/* Grid lines */}
          <div className="absolute inset-0 flex flex-col justify-between">
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} className="border-t border-[#3a3a3a] opacity-30" style={{ height: '20%' }} />
            ))}
          </div>
          <div className="absolute inset-0 flex justify-between">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="border-l border-[#3a3a3a] opacity-30" style={{ width: '16.66%' }} />
            ))}
          </div>

          {/* Risk zones */}
          <div className="absolute inset-0">
            {/* Low risk zone (green) */}
            <div className="absolute bottom-0 left-0 w-1/3 h-1/3 bg-green-500/20 rounded-tl-lg" />
            {/* Medium risk zone (yellow) */}
            <div className="absolute bottom-0 left-0 w-2/3 h-2/3 bg-yellow-500/20 rounded-tl-lg" />
            {/* High risk zone (red) */}
            <div className="absolute bottom-0 left-0 w-full h-full bg-red-500/20 rounded-lg" />
          </div>

          {/* Risk point */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: 'spring' }}
            className="absolute"
            style={{
              left: `${probability}%`,
              bottom: `${(impactValue / 4) * 100}%`,
              transform: 'translate(-50%, 50%)',
            }}
          >
            <div className="w-6 h-6 bg-red-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-white rounded-full" />
            </div>
            <div className="absolute top-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap bg-[#1a1a1a] border border-[#3a3a3a] rounded px-2 py-1 text-xs text-[#e8e8e8]">
              Risk: {risk_score}%
            </div>
          </motion.div>

          {/* Labels */}
          <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-xs text-[#b8b8b8]">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
          <div className="absolute -left-12 top-0 bottom-0 flex flex-col justify-between text-xs text-[#b8b8b8]">
            <span>Critical</span>
            <span>High</span>
            <span>Medium</span>
            <span>Low</span>
          </div>
        </div>
        <div className="mt-4 text-sm text-[#b8b8b8]">
          <p>Probability: {probability}% | Impact: {impact.toUpperCase()} | Risk Score: {risk_score}%</p>
        </div>
      </motion.div>
    )
  }

  // Timeline Chart
  const TimelineChart = () => {
    if (!chartData.risk_timeline) return null

    const { dates, late_blight_risk, early_blight_risk, overall_risk } = chartData.risk_timeline
    const maxRisk = Math.max(...overall_risk, ...late_blight_risk, ...early_blight_risk, 100)

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-[#2d2d2d] border border-[#3a3a3a] rounded-2xl p-6 shadow-lg mb-6"
      >
        <h3 className="text-xl font-semibold text-[#e8e8e8] mb-6" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
          Disease Risk Timeline (8-Day Forecast)
        </h3>
        <div className="relative h-80 pt-2 pb-16">
          {/* Y-axis labels - improved positioning and styling */}
          <div className="absolute -left-2 top-2 bottom-16 flex flex-col justify-between text-sm font-medium text-[#d8d8d8]">
            <span className="bg-[#2d2d2d] pr-2">{maxRisk.toFixed(0)}%</span>
            <span className="bg-[#2d2d2d] pr-2">{Math.round(maxRisk * 0.75)}%</span>
            <span className="bg-[#2d2d2d] pr-2">{Math.round(maxRisk / 2)}%</span>
            <span className="bg-[#2d2d2d] pr-2">{Math.round(maxRisk * 0.25)}%</span>
            <span className="bg-[#2d2d2d] pr-2">0%</span>
          </div>
          
          {/* Y-axis title */}
          <div className="absolute -left-2 top-1/2 -translate-y-1/2 -rotate-90 text-sm font-semibold text-[#b8b8b8] whitespace-nowrap">
            Risk Level (%)
          </div>

          {/* Grid lines for better readability */}
          <div className="absolute inset-0 ml-8 mb-16">
            {[0, 1, 2, 3, 4].map((i) => (
              <div 
                key={i} 
                className="absolute w-full border-t border-[#3a3a3a] opacity-30" 
                style={{ bottom: `${i * 25}%` }}
              />
            ))}
          </div>

          {/* Chart area - FIXED: Use full height without double padding */}
          <div className="ml-12 mr-4 absolute inset-0 top-2 bottom-16 flex items-end gap-3">
            {dates.map((date, index) => {
              // Get actual values
              const lbValue = late_blight_risk[index] || 0
              const ebValue = early_blight_risk[index] || 0
              const overallValue = overall_risk[index] || 0
              
              // CRITICAL FIX: Scale to maxRisk properly - this ensures 47% shows as 47% of max
              // If maxRisk is 100, then 47% should be 47% of chart height
              // If maxRisk is 85, then 47% should be (47/85) * 100 = 55.3% of chart height
              const lbHeight = maxRisk > 0 ? (lbValue / maxRisk) * 100 : 0
              const ebHeight = maxRisk > 0 ? (ebValue / maxRisk) * 100 : 0
              const overallHeight = maxRisk > 0 ? (overallValue / maxRisk) * 100 : 0
              
              // No minimum height override - let the actual percentage show
              // Only ensure it's within bounds
              const finalLbHeight = Math.max(0, Math.min(100, lbHeight))
              const finalEbHeight = Math.max(0, Math.min(100, ebHeight))
              const finalOverallHeight = Math.max(0, Math.min(100, overallHeight))

              return (
                <div key={date} className="flex-1 flex flex-col items-center group relative h-full">
                  <div className="relative w-full h-full flex items-end justify-center gap-1">
                    {/* Overall risk bar - full width, shows actual percentage */}
                    {overallValue > 0 && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${finalOverallHeight}%` }}
                        transition={{ delay: index * 0.05, duration: 0.4, ease: "easeOut" }}
                        className="w-full rounded-t-lg shadow-lg"
                        style={{ 
                          background: 'linear-gradient(to top, #dc2626, #ea580c)',
                          opacity: 0.85,
                          boxShadow: '0 -2px 8px rgba(234, 88, 12, 0.3)'
                        }}
                      />
                    )}
                    {/* Late blight bar - shown side by side */}
                    {lbValue > 0 && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${finalLbHeight}%` }}
                        transition={{ delay: index * 0.05 + 0.05, duration: 0.4, ease: "easeOut" }}
                        className="w-1/3 rounded-t-md shadow-md"
                        style={{ 
                          backgroundColor: '#ef4444',
                          opacity: 1,
                          boxShadow: '0 -2px 6px rgba(239, 68, 68, 0.4)'
                        }}
                      />
                    )}
                    {/* Early blight bar - shown side by side */}
                    {ebValue > 0 && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${finalEbHeight}%` }}
                        transition={{ delay: index * 0.05 + 0.1, duration: 0.4, ease: "easeOut" }}
                        className="w-1/3 rounded-t-md shadow-md"
                        style={{ 
                          backgroundColor: '#f97316',
                          opacity: 1,
                          boxShadow: '0 -2px 6px rgba(249, 115, 22, 0.4)'
                        }}
                      />
                    )}
                  </div>
                  {/* Date label - better positioning and styling */}
                  <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 text-xs font-medium text-[#c8c8c8] whitespace-nowrap">
                    {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </div>
                  {/* Tooltip on hover - enhanced styling */}
                  <div className="absolute bottom-full mb-3 hidden group-hover:block bg-gradient-to-br from-[#1a1a1a] to-[#2a2a2a] border border-[#4a4a4a] rounded-lg px-4 py-3 text-sm text-[#e8e8e8] z-20 whitespace-nowrap shadow-2xl">
                    <div className="font-semibold mb-2 text-orange-400">{new Date(date).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}</div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
                        <span>Late Blight: <strong>{lbValue.toFixed(1)}%</strong></span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-orange-500 rounded-sm"></div>
                        <span>Early Blight: <strong>{ebValue.toFixed(1)}%</strong></span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-gradient-to-r from-red-600 to-orange-500 rounded-sm"></div>
                        <span>Overall: <strong>{overallValue.toFixed(1)}%</strong></span>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
          
          {/* X-axis title */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-sm font-semibold text-[#b8b8b8] whitespace-nowrap">
            Date
          </div>
        </div>
        
        {/* Legend - improved styling */}
        <div className="mt-6 pt-4 border-t border-[#3a3a3a] flex flex-wrap gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-red-500 rounded shadow-md" />
            <span className="text-[#c8c8c8] font-medium">Late Blight</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-orange-500 rounded shadow-md" />
            <span className="text-[#c8c8c8] font-medium">Early Blight</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-gradient-to-r from-red-600 to-orange-500 rounded shadow-md" />
            <span className="text-[#c8c8c8] font-medium">Overall Risk</span>
          </div>
        </div>
      </motion.div>
    )
  }

  // Temperature & Humidity Trends
  const WeatherTrends = () => {
    if (!chartData.temperature_trend || !chartData.humidity_trend) return null

    const tempData = chartData.temperature_trend
    const humData = chartData.humidity_trend
    const dates = tempData.dates || []

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-[#2d2d2d] border border-[#3a3a3a] rounded-2xl p-6 shadow-lg mb-6"
      >
        <h3 className="text-xl font-semibold text-[#e8e8e8] mb-4" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
          Weather Trends: Temperature & Humidity
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          {/* Temperature Chart */}
          <div>
            <h4 className="text-sm font-medium text-[#b8b8b8] mb-3">Temperature (°C)</h4>
            <div className="relative h-56 pl-12 pr-4 pb-12">
              {/* Y-axis labels - FIXED: Better positioning to avoid overlap */}
              {(() => {
                // Calculate range for better scaling
                const allTemps = [...(tempData.max_temp || []), ...(tempData.min_temp || []), ...(tempData.avg_temp || [])].filter(v => v != null && v !== undefined)
                const dataMin = allTemps.length > 0 ? Math.min(...allTemps) : 0
                const dataMax = allTemps.length > 0 ? Math.max(...allTemps) : 35
                const range = dataMax - dataMin
                // For small ranges, use more padding to make bars more visible
                const padding = range > 0 ? Math.max(range * 0.15, 2) : 5 // At least 15% padding or 2°C, minimum 5 if no range
                const scaleMin = Math.max(0, dataMin - padding)
                const scaleMax = dataMax + padding
                // Ensure minimum range for visibility
                const scaleRange = Math.max(scaleMax - scaleMin, 10) || 1 // At least 10°C range for better visibility
                
                return (
                  <>
                    {/* Y-axis labels - positioned inside chart area */}
                    <div className="absolute left-0 top-0 bottom-12 flex flex-col justify-between text-xs font-medium text-[#d8d8d8]">
                      <span className="bg-[#2d2d2d] pr-1">{scaleMax.toFixed(0)}°C</span>
                      <span className="bg-[#2d2d2d] pr-1">{((scaleMin + scaleMax) / 2).toFixed(0)}°C</span>
                      <span className="bg-[#2d2d2d] pr-1">{scaleMin.toFixed(0)}°C</span>
                    </div>
                    
                    {/* Y-axis title */}
                    <div className="absolute -left-8 top-1/2 -translate-y-1/2 -rotate-90 text-xs font-semibold text-[#b8b8b8] whitespace-nowrap">
                      Temperature (°C)
                    </div>
                    
                    {/* Chart area - FIXED: Use absolute positioning for proper layout */}
                    <div className="absolute left-12 right-4 top-0 bottom-12 flex items-end gap-2">
                      {dates.map((date, index) => {
                        const min = tempData.min_temp?.[index] ?? 0
                        const max = tempData.max_temp?.[index] ?? 0
                        const avg = tempData.avg_temp?.[index] ?? 0
                        
                        // CRITICAL FIX: Scale values to chart height correctly
                        // Formula: ((value - scaleMin) / scaleRange) * 100
                        const minHeight = scaleRange > 0 ? ((min - scaleMin) / scaleRange) * 100 : 0
                        const avgHeight = scaleRange > 0 ? ((avg - scaleMin) / scaleRange) * 100 : 0
                        const maxHeight = scaleRange > 0 ? ((max - scaleMin) / scaleRange) * 100 : 0
                        
                        // Ensure values are within 0-100% bounds
                        const finalMinHeight = Math.max(0, Math.min(100, minHeight))
                        const finalAvgHeight = Math.max(0, Math.min(100, avgHeight))
                        const finalMaxHeight = Math.max(0, Math.min(100, maxHeight))

                        return (
                          <div key={date} className="flex-1 flex flex-col items-center group relative h-full">
                            <div className="relative w-full h-full flex items-end">
                              <div className="w-full flex flex-col justify-end gap-0.5" style={{ height: '100%' }}>
                                {/* Max temp bar (top) - FIXED: Show even if value is 0 or small */}
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${finalMaxHeight}%` }}
                                  transition={{ delay: index * 0.1, duration: 0.5 }}
                                  className="w-full rounded-t"
                                  style={{ 
                                    backgroundColor: '#60a5fa',
                                    opacity: max > 0 ? 0.85 : 0,
                                    minHeight: max > 0 && finalMaxHeight < 2 ? '2px' : '0px'
                                  }}
                                />
                                {/* Avg temp bar (middle) */}
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${finalAvgHeight}%` }}
                                  transition={{ delay: index * 0.1 + 0.05, duration: 0.5 }}
                                  className="w-full rounded-t"
                                  style={{ 
                                    backgroundColor: '#3b82f6',
                                    opacity: avg > 0 ? 1 : 0,
                                    minHeight: avg > 0 && finalAvgHeight < 2 ? '2px' : '0px'
                                  }}
                                />
                                {/* Min temp bar (bottom) */}
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${finalMinHeight}%` }}
                                  transition={{ delay: index * 0.1 + 0.1, duration: 0.5 }}
                                  className="w-full rounded-t"
                                  style={{ 
                                    backgroundColor: '#2563eb',
                                    opacity: min > 0 ? 0.9 : 0,
                                    minHeight: min > 0 && finalMinHeight < 2 ? '2px' : '0px'
                                  }}
                                />
                              </div>
                            </div>
                            {/* Date label - positioned below chart */}
                            <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 text-xs font-medium text-[#c8c8c8] whitespace-nowrap">
                              {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            </div>
                            {/* Tooltip on hover */}
                            <div className="absolute bottom-full mb-3 hidden group-hover:block bg-gradient-to-br from-[#1a1a1a] to-[#2a2a2a] border border-[#4a4a4a] rounded-lg px-4 py-3 text-sm text-[#e8e8e8] z-20 whitespace-nowrap shadow-2xl">
                              <div className="font-semibold mb-2 text-blue-400">{new Date(date).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}</div>
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-blue-400 rounded-sm"></div>
                                  <span>Max: <strong>{max.toFixed(1)}°C</strong></span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-blue-600 rounded-sm"></div>
                                  <span>Avg: <strong>{avg.toFixed(1)}°C</strong></span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-blue-700 rounded-sm"></div>
                                  <span>Min: <strong>{min.toFixed(1)}°C</strong></span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    
                    {/* X-axis title */}
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-xs font-semibold text-[#b8b8b8] whitespace-nowrap">
                      Date
                    </div>
                  </>
                )
              })()}
            </div>
          </div>

          {/* Humidity Chart */}
          <div>
            <h4 className="text-sm font-medium text-[#b8b8b8] mb-3">Humidity (%)</h4>
            <div className="relative h-56 pl-12 pr-4 pb-12">
              {/* Y-axis labels - FIXED: Better positioning to avoid overlap */}
              {(() => {
                // Calculate range for better scaling
                const allHumidity = [...(humData.max_humidity || []), ...(humData.min_humidity || []), ...(humData.avg_humidity || [])].filter(v => v != null && v !== undefined)
                const dataMin = allHumidity.length > 0 ? Math.min(...allHumidity) : 0
                const dataMax = allHumidity.length > 0 ? Math.max(...allHumidity) : 100
                const range = dataMax - dataMin
                // For small ranges, use more padding to make bars more visible
                const padding = range > 0 ? Math.max(range * 0.15, 5) : 10 // At least 15% padding or 5 units, minimum 10 if no range
                const scaleMin = Math.max(0, dataMin - padding)
                const scaleMax = Math.min(100, dataMax + padding)
                // Ensure minimum range for visibility
                const scaleRange = Math.max(scaleMax - scaleMin, 20) || 1 // At least 20% range for better visibility
                
                return (
                  <>
                    {/* Y-axis labels - positioned inside chart area */}
                    <div className="absolute left-0 top-0 bottom-12 flex flex-col justify-between text-xs font-medium text-[#d8d8d8]">
                      <span className="bg-[#2d2d2d] pr-1">{scaleMax.toFixed(0)}%</span>
                      <span className="bg-[#2d2d2d] pr-1">{((scaleMin + scaleMax) / 2).toFixed(0)}%</span>
                      <span className="bg-[#2d2d2d] pr-1">{scaleMin.toFixed(0)}%</span>
                    </div>
                    
                    {/* Y-axis title */}
                    <div className="absolute -left-8 top-1/2 -translate-y-1/2 -rotate-90 text-xs font-semibold text-[#b8b8b8] whitespace-nowrap">
                      Humidity (%)
                    </div>
                    
                    {/* Chart area - FIXED: Use absolute positioning for proper layout */}
                    <div className="absolute left-12 right-4 top-0 bottom-12 flex items-end gap-2">
                      {dates.map((date, index) => {
                        const min = humData.min_humidity?.[index] ?? 0
                        const max = humData.max_humidity?.[index] ?? 0
                        const avg = humData.avg_humidity?.[index] ?? 0
                        
                        // CRITICAL FIX: Scale values to chart height correctly
                        // Formula: ((value - scaleMin) / scaleRange) * 100
                        const minHeight = scaleRange > 0 ? ((min - scaleMin) / scaleRange) * 100 : 0
                        const avgHeight = scaleRange > 0 ? ((avg - scaleMin) / scaleRange) * 100 : 0
                        const maxHeight = scaleRange > 0 ? ((max - scaleMin) / scaleRange) * 100 : 0
                        
                        // Ensure values are within 0-100% bounds
                        const finalMinHeight = Math.max(0, Math.min(100, minHeight))
                        const finalAvgHeight = Math.max(0, Math.min(100, avgHeight))
                        const finalMaxHeight = Math.max(0, Math.min(100, maxHeight))

                        return (
                          <div key={date} className="flex-1 flex flex-col items-center group relative h-full">
                            <div className="relative w-full h-full flex items-end">
                              <div className="w-full flex flex-col justify-end gap-0.5" style={{ height: '100%' }}>
                                {/* Max humidity bar (top) - FIXED: Show even if value is 0 or small */}
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${finalMaxHeight}%` }}
                                  transition={{ delay: index * 0.1, duration: 0.5 }}
                                  className="w-full rounded-t"
                                  style={{ 
                                    backgroundColor: '#4ade80',
                                    opacity: max > 0 ? 0.85 : 0,
                                    minHeight: max > 0 && finalMaxHeight < 2 ? '2px' : '0px'
                                  }}
                                />
                                {/* Avg humidity bar (middle) */}
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${finalAvgHeight}%` }}
                                  transition={{ delay: index * 0.1 + 0.05, duration: 0.5 }}
                                  className="w-full rounded-t"
                                  style={{ 
                                    backgroundColor: '#22c55e',
                                    opacity: avg > 0 ? 1 : 0,
                                    minHeight: avg > 0 && finalAvgHeight < 2 ? '2px' : '0px'
                                  }}
                                />
                                {/* Min humidity bar (bottom) */}
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${finalMinHeight}%` }}
                                  transition={{ delay: index * 0.1 + 0.1, duration: 0.5 }}
                                  className="w-full rounded-t"
                                  style={{ 
                                    backgroundColor: '#16a34a',
                                    opacity: min > 0 ? 0.9 : 0,
                                    minHeight: min > 0 && finalMinHeight < 2 ? '2px' : '0px'
                                  }}
                                />
                              </div>
                            </div>
                            {/* Date label - positioned below chart */}
                            <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 text-xs font-medium text-[#c8c8c8] whitespace-nowrap">
                              {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            </div>
                            {/* Tooltip on hover */}
                            <div className="absolute bottom-full mb-3 hidden group-hover:block bg-gradient-to-br from-[#1a1a1a] to-[#2a2a2a] border border-[#4a4a4a] rounded-lg px-4 py-3 text-sm text-[#e8e8e8] z-20 whitespace-nowrap shadow-2xl">
                              <div className="font-semibold mb-2 text-green-400">{new Date(date).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}</div>
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-green-400 rounded-sm"></div>
                                  <span>Max: <strong>{max.toFixed(0)}%</strong></span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-green-500 rounded-sm"></div>
                                  <span>Avg: <strong>{avg.toFixed(0)}%</strong></span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-green-600 rounded-sm"></div>
                                  <span>Min: <strong>{min.toFixed(0)}%</strong></span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    
                    {/* X-axis title */}
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-xs font-semibold text-[#b8b8b8] whitespace-nowrap">
                      Date
                    </div>
                  </>
                )
              })()}
            </div>
          </div>
        </div>
      </motion.div>
    )
  }

  // Risk Factor Contributions (Enhanced)
  const RiskFactorContributions = () => {
    if (!chartData.risk_factor_contributions) return null

    const { late_blight, early_blight } = chartData.risk_factor_contributions

    const renderFactorBar = (factor: string, value: number, disease: 'late_blight' | 'early_blight') => {
      const factorName = factor.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
      const color = value >= 70 ? 'bg-red-500' : value >= 50 ? 'bg-orange-500' : 'bg-yellow-500'

      return (
        <div key={factor} className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-[#b8b8b8] capitalize" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
              {factorName}
            </span>
            <span className="text-sm font-bold text-[#e8e8e8]" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
              {value}%
            </span>
          </div>
          <div className="w-full bg-[#1a1a1a] rounded-full h-4 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${value}%` }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className={`h-4 rounded-full ${color} shadow-lg`}
            />
          </div>
        </div>
      )
    }

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-[#2d2d2d] border border-[#3a3a3a] rounded-2xl p-6 shadow-lg mb-6"
      >
        <h3 className="text-xl font-semibold text-[#e8e8e8] mb-4" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
          Risk Factor Contributions
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          {/* Late Blight Factors */}
          <div>
            <h4 className="text-lg font-semibold text-red-400 mb-4" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
              Late Blight Risk Factors
            </h4>
            {Object.entries(late_blight).map(([factor, value]) => renderFactorBar(factor, value, 'late_blight'))}
          </div>

          {/* Early Blight Factors */}
          <div>
            <h4 className="text-lg font-semibold text-orange-400 mb-4" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
              Early Blight Risk Factors
            </h4>
            {Object.entries(early_blight).map(([factor, value]) => renderFactorBar(factor, value, 'early_blight'))}
          </div>
        </div>

        {/* Calculation Methodology */}
        {chartData.calculation_methodology && (
          <div className="mt-6 pt-6 border-t border-[#3a3a3a]">
            <h4 className="text-sm font-semibold text-[#b8b8b8] mb-2">Calculation Methodology</h4>
            <p className="text-xs text-[#808080] leading-relaxed">{chartData.calculation_methodology}</p>
          </div>
        )}
      </motion.div>
    )
  }

  return (
    <div className="w-full space-y-6">
      <RiskMatrix />
      <TimelineChart />
      <WeatherTrends />
      <RiskFactorContributions />
    </div>
  )
}

