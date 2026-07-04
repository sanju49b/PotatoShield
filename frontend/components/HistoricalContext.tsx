'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface HistoricalContextProps {
  historicalOutbreaks: any[]
  currentWeather: any
  location: string
}

export default function HistoricalContext({ historicalOutbreaks, currentWeather, location }: HistoricalContextProps) {
  const calculateSimilarity = (outbreak: any, current: any) => {
    const tempDiff = Math.abs(outbreak.avg_temp - (current?.temp_avg || 0))
    const humidityDiff = Math.abs(outbreak.avg_humidity - (current?.humidity_avg || 0))
    const similarity = 100 - ((tempDiff + humidityDiff) / 2)
    return Math.max(0, Math.min(100, similarity))
  }

  return (
    <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a] shadow-xl">
      <h2 className="text-2xl font-bold text-[#e8e8e8] mb-6 flex items-center gap-2">
        📚 Historical Context & References
      </h2>

      <div className="space-y-4">
        {historicalOutbreaks.map((outbreak, index) => {
          const similarity = calculateSimilarity(outbreak, currentWeather)

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-[#3a3a3a] rounded-lg p-4 border border-[#4a4a4a]"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-[#e8e8e8]">
                    {outbreak.year} - {outbreak.region}
                  </h3>
                  <p className="text-sm text-[#b8b8b8] mt-1">{outbreak.notes}</p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-[#b8b8b8]">Similarity</div>
                  <div className={`text-2xl font-bold ${
                    similarity > 80 ? 'text-red-400' :
                    similarity > 60 ? 'text-orange-400' :
                    'text-yellow-400'
                  }`}>
                    {Math.round(similarity)}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <div className="text-xs text-[#808080]">Historical Conditions</div>
                  <div className="text-sm text-[#e8e8e8]">
                    {outbreak.avg_temp}°C, {outbreak.avg_humidity}% RH
                  </div>
                </div>
                <div>
                  <div className="text-xs text-[#808080]">Current Conditions</div>
                  <div className="text-sm text-[#e8e8e8]">
                    {Math.round(currentWeather?.temp_avg || 0)}°C, {Math.round(currentWeather?.humidity_avg || 0)}% RH
                  </div>
                </div>
              </div>

              {outbreak.references && outbreak.references.length > 0 && (
                <div className="pt-3 border-t border-[#4a4a4a]">
                  <div className="text-xs text-[#808080] mb-2">References:</div>
                  <div className="flex flex-wrap gap-2">
                    {outbreak.references.map((ref: string, refIndex: number) => (
                      <a
                        key={refIndex}
                        href="#"
                        className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs hover:bg-blue-500/30 transition-colors"
                      >
                        {ref}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )
        })}
      </div>
    </section>
  )
}

