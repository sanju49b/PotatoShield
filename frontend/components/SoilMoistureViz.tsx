'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface SoilMoistureVizProps {
  soilData: any[]
}

export default function SoilMoistureViz({ soilData }: SoilMoistureVizProps) {
  const getStatus = (moisture: number) => {
    if (moisture < 0.3) return { label: 'Dry', color: 'bg-yellow-500', textColor: 'text-yellow-400' }
    if (moisture > 0.7) return { label: 'Wet', color: 'bg-blue-500', textColor: 'text-blue-400' }
    return { label: 'Optimal', color: 'bg-green-500', textColor: 'text-green-400' }
  }

  return (
    <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a] shadow-xl">
      <h2 className="text-2xl font-bold text-[#e8e8e8] mb-6 flex items-center gap-2">
        🌱 Soil Moisture (8-Day Forecast)
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        {soilData.map((day, index) => {
          const moisture = day.soil_moisture_percent || 0
          const status = getStatus(moisture)
          const date = new Date(day.date)
          const dayName = date.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' })

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="text-center"
            >
              <div className="text-xs text-[#b8b8b8] mb-2">{dayName}</div>
              <div className="relative w-20 h-20 mx-auto mb-2">
                <svg className="transform -rotate-90 w-20 h-20">
                  <circle cx="40" cy="40" r="36" stroke="#3a3a3a" strokeWidth="8" fill="none" />
                  <circle
                    cx="40"
                    cy="40"
                    r="36"
                    stroke={status.color.replace('bg-', '')}
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${moisture * 226} 226`}
                    className="transition-all"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-sm font-bold text-[#e8e8e8]">{Math.round(moisture * 100)}%</span>
                </div>
              </div>
              <div className={`text-xs font-medium ${status.textColor}`}>{status.label}</div>
            </motion.div>
          )
        })}
      </div>
    </section>
  )
}

