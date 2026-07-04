'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface WeatherTrendsProps {
  weatherData: any[]
}

export default function WeatherTrends({ weatherData }: WeatherTrendsProps) {
  const temps = weatherData.map(d => d?.temp_avg || 0)
  const tempMin = Math.min(...temps)
  const tempMax = Math.max(...temps)
  const hums = weatherData.map(d => d?.humidity_avg || 0)
  const humMin = Math.min(...hums, 0)
  const humMax = Math.max(...hums, 100)

  const width = 560
  const height = 160
  const padding = 24
  const stepX = (width - padding * 2) / Math.max(1, weatherData.length - 1)

  const toPoints = (arr: number[], min: number, max: number) =>
    arr.map((v, i) => {
      const x = padding + i * stepX
      const t = max - min === 0 ? 0 : (v - min) / (max - min)
      const y = padding + (1 - t) * (height - padding * 2)
      return [x, y] as [number, number]
    })

  const tempPts = toPoints(temps, tempMin, tempMax)
  const humPts = toPoints(hums, humMin, humMax)

  const toPath = (pts: [number, number][]) =>
    pts.reduce((p, [x, y], i) => (i === 0 ? `M ${x},${y}` : `${p} L ${x},${y}`), '')

  const tempPath = toPath(tempPts)
  const humPath = toPath(humPts)

  return (
    <section className="bg-[#151515]/90 rounded-xl p-6 border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.45)] backdrop-blur-md">
      <h2 className="text-2xl font-bold text-[#e8e8e8] mb-6 flex items-center gap-2">
        📊 Weather Trends (8-Day Forecast)
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temperature Line */}
        <div className="bg-[#0f0f0f] rounded-xl p-4 border border-[#2a2a2a]">
          <h3 className="text-lg font-semibold text-[#e8e8e8] mb-4">🌡️ Avg Temperature (°C)</h3>
          <div className="relative">
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40">
              <defs>
                <linearGradient id="tempStroke" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#60a5fa" />
                  <stop offset="50%" stopColor="#f59e0b" />
                  <stop offset="100%" stopColor="#ef4444" />
                </linearGradient>
                <linearGradient id="tempFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="rgba(245,158,11,0.35)" />
                  <stop offset="100%" stopColor="rgba(245,158,11,0.05)" />
                </linearGradient>
              </defs>
              <motion.path
                d={tempPath}
                fill="none"
                stroke="url(#tempStroke)"
                strokeWidth="3"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1.2, ease: 'easeInOut' }}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {/* Area fill */}
              <path
                d={`${tempPath} L ${padding + stepX * (weatherData.length - 1)},${height - padding} L ${padding},${height - padding} Z`}
                fill="url(#tempFill)"
                opacity="0.6"
              />
            </svg>
            <div className="flex justify-between text-xs text-[#b8b8b8] mt-1">
              {weatherData.map((d, i) => (
                <span key={i}>{new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' })}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Humidity Line */}
        <div className="bg-[#0f0f0f] rounded-xl p-4 border border-[#2a2a2a]">
          <h3 className="text-lg font-semibold text-[#e8e8e8] mb-4">💧 Avg Humidity (%)</h3>
          <div className="relative">
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40">
              <defs>
                <linearGradient id="humStroke" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#22c55e" />
                  <stop offset="50%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#ef4444" />
                </linearGradient>
                <linearGradient id="humFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="rgba(59,130,246,0.30)" />
                  <stop offset="100%" stopColor="rgba(59,130,246,0.05)" />
                </linearGradient>
              </defs>
              <motion.path
                d={humPath}
                fill="none"
                stroke="url(#humStroke)"
                strokeWidth="3"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1.2, ease: 'easeInOut' }}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d={`${humPath} L ${padding + stepX * (weatherData.length - 1)},${height - padding} L ${padding},${height - padding} Z`}
                fill="url(#humFill)"
                opacity="0.6"
              />
            </svg>
            <div className="flex justify-between text-xs text-[#b8b8b8] mt-1">
              {weatherData.map((d, i) => (
                <span key={i}>{new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' })}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

