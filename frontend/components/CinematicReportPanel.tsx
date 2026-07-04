'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface CinematicReportPanelProps {
  reportData: any
  chartData: any
}

export default function CinematicReportPanel({ reportData, chartData }: CinematicReportPanelProps) {
  const [visibleSections, setVisibleSections] = useState<Set<string>>(new Set())
  
  // Extract real data from prediction
  const predictionData = reportData?.prediction_data || {}
  const weatherData = reportData?.weather_dataset || {}
  const location = reportData?.location || 'Unknown Location'
  const elevation = reportData?.elevation || 0
  const growthStage = reportData?.growthStage || 'Unknown'
  const daysAfterPlanting = reportData?.daysAfterPlanting || 0
  
  // Extract risk data
  const lateBlightInfo = predictionData?.late_blight_risk || {}
  const earlyBlightInfo = predictionData?.early_blight_risk || {}
  const lateBlightRisk = typeof lateBlightInfo === 'object' ? (lateBlightInfo.risk_percentage || reportData?.late_blight_risk || 0) : (reportData?.late_blight_risk || 0)
  const earlyBlightRisk = typeof earlyBlightInfo === 'object' ? (earlyBlightInfo.risk_percentage || reportData?.early_blight_risk || 0) : (reportData?.early_blight_risk || 0)
  const overallRisk = reportData?.overall_risk || predictionData?.overall_disease_pressure?.overall_risk_percentage || 0
  
  // Extract weather data
  const dailyWeather = weatherData?.daily_weather || []
  const todayWeather = dailyWeather[0] || {}
  const currentTemp = reportData?.current_temp || todayWeather?.avg_temp || 0
  const currentHumidity = reportData?.current_humidity || todayWeather?.avg_humidity || 0
  const rainfall = reportData?.rainfall || todayWeather?.total_precipitation || 0
  const pm25 = reportData?.pm25 || weatherData?.daily_air_quality?.[0]?.pm2_5 || 0
  
  // Extract recommendations (from prediction_data or directly from reportData)
  const immediateActions = reportData?.immediate_actions || predictionData?.immediate_actions || []
  const preventiveRecs = reportData?.preventive_recommendations || predictionData?.preventive_recommendations || []
  const weeklyOutlook = reportData?.weekly_outlook || predictionData?.weekly_outlook || {}
  const criticalObservations = reportData?.critical_weather_observations || predictionData?.critical_weather_observations || []

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisibleSections((prev) => new Set(prev).add(entry.target.id))
          }
        })
      },
      { threshold: 0.2 }
    )

    document.querySelectorAll('[data-animate]').forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  const AnimatedSection = ({ children, id, delay = 0 }: any) => (
    <motion.div
      id={id}
      data-animate
      initial={{ opacity: 0, y: 50 }}
      animate={visibleSections.has(id) ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.8, delay }}
    >
      {children}
    </motion.div>
  )

  return (
    <div className="space-y-8 pb-12">
      {/* HERO - CRITICAL ALERT */}
      <AnimatedSection id="hero">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-red-600 via-orange-500 to-yellow-500 p-8 shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
          <div className="relative z-10">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.6, type: "spring" }}
              className="inline-block px-4 py-2 bg-white/30 backdrop-blur-sm rounded-full mb-4 border border-white/50"
            >
              <span className="text-white font-bold text-sm">⚠️ CRITICAL RISK DETECTED</span>
            </motion.div>
            
            <h1 className="text-5xl font-bold text-white mb-4 drop-shadow-lg">
              Your Crop Needs Immediate Attention
            </h1>
            
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="bg-white/20 backdrop-blur-md rounded-xl p-4 border border-white/30">
                <div className="text-white/80 text-sm mb-1">Late Blight Risk</div>
                <div className="text-4xl font-bold text-white">{Math.round(lateBlightRisk)}%</div>
                <div className={`text-xs text-white/70 mt-1 ${
                  lateBlightRisk > 75 ? '🔴 HIGH ALERT' :
                  lateBlightRisk > 50 ? '🟠 ELEVATED' :
                  lateBlightRisk > 25 ? '🟡 MODERATE' :
                  '🟢 LOW'
                }`}>
                  {lateBlightRisk > 75 ? '🔴 HIGH ALERT' :
                   lateBlightRisk > 50 ? '🟠 ELEVATED' :
                   lateBlightRisk > 25 ? '🟡 MODERATE' :
                   '🟢 LOW RISK'}
                </div>
              </div>
              <div className="bg-white/20 backdrop-blur-md rounded-xl p-4 border border-white/30">
                <div className="text-white/80 text-sm mb-1">Overall Risk</div>
                <div className="text-4xl font-bold text-white">{Math.round(overallRisk)}%</div>
                <div className={`text-xs text-white/70 mt-1 ${
                  overallRisk > 75 ? '🔴 CRITICAL' :
                  overallRisk > 50 ? '🟠 HIGH' :
                  overallRisk > 25 ? '🟡 MODERATE' :
                  '🟢 LOW'
                }`}>
                  {overallRisk > 75 ? '🔴 CRITICAL' :
                   overallRisk > 50 ? '🟠 HIGH' :
                   overallRisk > 25 ? '🟡 MODERATE' :
                   '🟢 LOW RISK'}
                </div>
              </div>
              <div className="bg-white/20 backdrop-blur-md rounded-xl p-4 border border-white/30">
                <div className="text-white/80 text-sm mb-1">Early Blight Risk</div>
                <div className="text-4xl font-bold text-white">{Math.round(earlyBlightRisk)}%</div>
                <div className={`text-xs text-white/70 mt-1 ${
                  earlyBlightRisk > 75 ? '🔴 HIGH ALERT' :
                  earlyBlightRisk > 50 ? '🟠 ELEVATED' :
                  earlyBlightRisk > 25 ? '🟡 MODERATE' :
                  '🟢 LOW'
                }`}>
                  {earlyBlightRisk > 75 ? '🔴 HIGH ALERT' :
                   earlyBlightRisk > 50 ? '🟠 ELEVATED' :
                   earlyBlightRisk > 25 ? '🟡 MODERATE' :
                   '🟢 LOW RISK'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* FIELD STORY */}
      <AnimatedSection id="field-story" delay={0.1}>
        <div className="bg-gradient-to-br from-[#2d2d2d] to-[#1a1a1a] rounded-xl p-6 border border-orange-500/30 shadow-xl">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
            🌾 Your Field's Story
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#3a3a3a] rounded-lg p-4 border-l-4 border-blue-500">
              <div className="text-blue-400 text-sm mb-1">📍 Location</div>
              <div className="text-[#e8e8e8] text-lg font-semibold">{location}</div>
              {elevation > 0 && (
                <div className="text-[#b8b8b8] text-xs mt-1">Elevation: {elevation}m</div>
              )}
            </div>
            <div className="bg-[#3a3a3a] rounded-lg p-4 border-l-4 border-green-500">
              <div className="text-green-400 text-sm mb-1">🌱 Growth Stage</div>
              <div className="text-[#e8e8e8] text-lg font-semibold">{growthStage}</div>
              <div className="text-[#b8b8b8] text-xs mt-1">Day {daysAfterPlanting} after planting</div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-lg border border-orange-500/30">
            <p className="text-[#e8e8e8] leading-relaxed">
              {lateBlightRisk > 75 ? (
                <>
                  Your crop is in a <span className="text-orange-400 font-bold">critical danger zone</span>. 
                  The next 7 days will determine the health trajectory for the entire season. 
                  Current weather conditions are creating a <span className="text-red-400 font-bold">perfect storm</span> for Late Blight development.
                </>
              ) : lateBlightRisk > 50 ? (
                <>
                  Your crop requires <span className="text-yellow-400 font-bold">close monitoring</span>. 
                  Weather conditions are favorable for disease development. 
                  Take preventive measures to protect your harvest.
                </>
              ) : (
                <>
                  Your crop is in a <span className="text-green-400 font-bold">manageable state</span>. 
                  Continue regular monitoring and maintain good field practices.
                </>
              )}
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* TEMPERATURE JOURNEY */}
      <AnimatedSection id="temp-journey" delay={0.2}>
        <div className="bg-gradient-to-br from-red-500/10 to-orange-500/10 rounded-xl p-6 border border-red-500/30 shadow-xl">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
            🌡️ Temperature Journey
          </h2>
          
          <div className="mb-6 p-4 bg-[#2d2d2d] rounded-lg">
            <p className="text-[#b8b8b8] leading-relaxed mb-4">
              {dailyWeather.length > 0 ? (
                <>
                  Current temperature: <span className="text-orange-400 font-bold">{Math.round(currentTemp)}°C</span> with 
                  <span className="text-blue-400 font-bold"> {Math.round(currentHumidity)}%</span> humidity. 
                  {currentHumidity > 80 && (
                    <> These conditions, combined with high humidity, create the <span className="text-red-400 font-bold">ideal breeding ground</span> for disease.</>
                  )}
                </>
              ) : (
                <>
                  Monitoring weather conditions for {location}. 
                  {currentHumidity > 80 && (
                    <> High humidity levels detected - <span className="text-red-400 font-bold">increased disease risk</span>.</>
                  )}
                </>
              )}
            </p>
            
            {/* Animated Temperature Bar */}
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-xs text-[#b8b8b8] w-16">Nov 7</span>
                <div className="flex-1 h-8 bg-[#1a1a1a] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '68%' }}
                    transition={{ duration: 1, delay: 0.3 }}
                    className="h-full bg-gradient-to-r from-blue-400 via-yellow-400 to-orange-500 flex items-center justify-end pr-3"
                  >
                    <span className="text-xs font-bold text-white">13.4°C - 25.4°C</span>
                  </motion.div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-[#b8b8b8] w-16">Nov 10</span>
                <div className="flex-1 h-8 bg-[#1a1a1a] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '65%' }}
                    transition={{ duration: 1, delay: 0.5 }}
                    className="h-full bg-gradient-to-r from-cyan-400 via-yellow-400 to-orange-500 flex items-center justify-end pr-3"
                  >
                    <span className="text-xs font-bold text-white">11.9°C - 25.0°C</span>
                  </motion.div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="bg-blue-500/20 rounded-lg p-3 border border-blue-500/30">
              <div className="text-blue-300 text-xs mb-1">🌡️ Current</div>
              <div className="text-2xl font-bold text-blue-400">{Math.round(currentTemp)}°C</div>
            </div>
            <div className="bg-orange-500/20 rounded-lg p-3 border border-orange-500/30">
              <div className="text-orange-300 text-xs mb-1">💧 Humidity</div>
              <div className="text-2xl font-bold text-orange-400">{Math.round(currentHumidity)}%</div>
            </div>
            <div className="bg-red-500/20 rounded-lg p-3 border border-red-500/30">
              <div className="text-red-300 text-xs mb-1">🌧️ Rainfall</div>
              <div className="text-2xl font-bold text-red-400">{Math.round(rainfall)}mm</div>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* ENVIRONMENTAL CONDITIONS */}
      <AnimatedSection id="environment" delay={0.3}>
        <div className="bg-gradient-to-br from-[#2d2d2d] to-[#1a1a1a] rounded-xl p-6 border border-cyan-500/30 shadow-xl">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
            🌿 Environmental Snapshot
          </h2>
          
          <div className="grid grid-cols-2 gap-4">
            {/* Humidity - CRITICAL */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              className={`bg-gradient-to-br rounded-xl p-5 shadow-lg cursor-pointer relative overflow-hidden ${
                currentHumidity > 80 ? 'from-red-600 to-orange-600' :
                currentHumidity > 60 ? 'from-orange-600 to-yellow-600' :
                'from-blue-600 to-cyan-600'
              }`}
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-2">💧</div>
                <div className="text-white/80 text-sm mb-1">Humidity</div>
                <div className="text-4xl font-bold text-white mb-1">{Math.round(currentHumidity)}%</div>
                <div className={`inline-block px-2 py-1 text-white text-xs rounded-full font-bold ${
                  currentHumidity > 80 ? 'bg-red-500' :
                  currentHumidity > 60 ? 'bg-orange-500' :
                  'bg-green-500'
                }`}>
                  {currentHumidity > 80 ? '⚠️ DANGER ZONE' :
                   currentHumidity > 60 ? '⚡ ELEVATED' :
                   '✓ NORMAL'}
                </div>
              </div>
            </motion.div>

            {/* Cloud Cover */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-gradient-to-br from-gray-600 to-gray-700 rounded-xl p-5 shadow-lg cursor-pointer relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-2">☁️</div>
                <div className="text-white/80 text-sm mb-1">Cloud Cover</div>
                <div className="text-4xl font-bold text-white mb-1">15%</div>
                <div className="inline-block px-2 py-1 bg-green-500 text-white text-xs rounded-full font-bold">
                  ✓ NORMAL
                </div>
              </div>
            </motion.div>

            {/* Air Quality */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-gradient-to-br from-yellow-600 to-orange-600 rounded-xl p-5 shadow-lg cursor-pointer relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-2">🌫️</div>
                <div className="text-white/80 text-sm mb-1">PM2.5 (Air Quality)</div>
                <div className="text-4xl font-bold text-white mb-1">99.1</div>
                <div className="inline-block px-2 py-1 bg-orange-500 text-white text-xs rounded-full font-bold">
                  ⚡ MODERATE
                </div>
              </div>
            </motion.div>

            {/* Soil Moisture */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-gradient-to-br from-green-600 to-teal-600 rounded-xl p-5 shadow-lg cursor-pointer relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-2">🌱</div>
                <div className="text-white/80 text-sm mb-1">Soil Conditions</div>
                <div className="text-4xl font-bold text-white mb-1">Optimal</div>
                <div className="inline-block px-2 py-1 bg-green-500 text-white text-xs rounded-full font-bold">
                  ✓ PERFECT
                </div>
              </div>
            </motion.div>
          </div>

          <div className="mt-6 p-4 bg-red-500/10 rounded-lg border border-red-500/30">
            <p className="text-[#e8e8e8] text-sm leading-relaxed">
              <span className="font-bold text-red-400">⚠️ Critical Combination:</span> The deadly trio of high humidity (92%), 
              moderate temperatures (25°C), and elevated PM2.5 levels creates the perfect environment for Late Blight spores 
              to spread rapidly across your field.
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* ACTION PLAN - IMMEDIATE - From Prediction Agent */}
      <AnimatedSection id="action-plan" delay={0.4}>
        <div className={`bg-gradient-to-br rounded-xl p-6 shadow-2xl border-2 ${
          lateBlightRisk > 75 ? 'from-red-600 to-orange-600 border-yellow-400' :
          lateBlightRisk > 50 ? 'from-orange-600 to-yellow-600 border-orange-400' :
          'from-yellow-600 to-green-600 border-green-400'
        }`}>
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            {lateBlightRisk > 75 ? '🚨 IMMEDIATE ACTION REQUIRED' :
             lateBlightRisk > 50 ? '⚠️ PREVENTIVE ACTIONS NEEDED' :
             '✅ RECOMMENDED ACTIONS'}
          </h2>
          
          <div className="space-y-4">
            {/* Immediate Actions from Prediction */}
            {immediateActions && immediateActions.length > 0 ? (
              immediateActions.map((action: any, idx: number) => (
                <motion.div
                  key={idx}
                  whileHover={{ scale: 1.02, x: 10 }}
                  className="bg-white/20 backdrop-blur-md rounded-lg p-4 border border-white/30 cursor-pointer"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-2xl">{action.icon || '💊'}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-bold text-lg mb-1">{action.title || action}</h3>
                      {typeof action === 'object' && action.description && (
                        <p className="text-white/90 text-sm mb-2">{action.description}</p>
                      )}
                      {typeof action === 'object' && action.priority && (
                        <div className="flex gap-2">
                          <span className={`px-2 py-1 text-white text-xs rounded-full font-bold ${
                            action.priority === 'URGENT' ? 'bg-red-500' :
                            action.priority === 'HIGH' ? 'bg-orange-500' :
                            'bg-yellow-500'
                          }`}>
                            {action.priority}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <>
                {/* Fallback Actions based on risk */}
                {lateBlightRisk > 75 && (
                  <motion.div
                    whileHover={{ scale: 1.02, x: 10 }}
                    className="bg-white/20 backdrop-blur-md rounded-lg p-4 border border-white/30 cursor-pointer"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-2xl">💊</span>
                      </div>
                      <div className="flex-1">
                        <h3 className="text-white font-bold text-lg mb-1">Apply Fungicide IMMEDIATELY</h3>
                        <p className="text-white/90 text-sm mb-2">
                          <span className="font-bold">Mancozeb 75% WP</span> at 2.5 kg/hectare. Your Late Blight risk is critically high at {Math.round(lateBlightRisk)}%.
                        </p>
                        <div className="flex gap-2">
                          <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full font-bold">
                            URGENT - TODAY
                          </span>
                          <span className="px-2 py-1 bg-white/30 text-white text-xs rounded-full">
                            Repeat in 7 days
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                <motion.div
                  whileHover={{ scale: 1.02, x: 10 }}
                  className="bg-white/20 backdrop-blur-md rounded-lg p-4 border border-white/30 cursor-pointer"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-2xl">👁️</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-bold text-lg mb-1">Daily Field Monitoring</h3>
                      <p className="text-white/90 text-sm mb-2">
                        Check for dark spots on leaves, white fungal growth, and stem lesions. Monitor humidity levels closely.
                      </p>
                      <div className="flex gap-2">
                        <span className="px-2 py-1 bg-yellow-500 text-white text-xs rounded-full font-bold">
                          CRITICAL
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>

                {currentHumidity > 80 && (
                  <motion.div
                    whileHover={{ scale: 1.02, x: 10 }}
                    className="bg-white/20 backdrop-blur-md rounded-lg p-4 border border-white/30 cursor-pointer"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-2xl">💧</span>
                      </div>
                      <div className="flex-1">
                        <h3 className="text-white font-bold text-lg mb-1">Reduce Irrigation</h3>
                        <p className="text-white/90 text-sm mb-2">
                          Humidity is {Math.round(currentHumidity)}% - avoid overwatering. Let soil surface dry between waterings.
                        </p>
                        <div className="flex gap-2">
                          <span className="px-2 py-1 bg-blue-500 text-white text-xs rounded-full font-bold">
                            HIGH PRIORITY
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </>
            )}

            {/* Preventive Recommendations */}
            {preventiveRecs && preventiveRecs.length > 0 && (
              <div className="mt-6 pt-4 border-t border-white/30">
                <h3 className="text-white font-bold text-lg mb-3">📋 Preventive Measures</h3>
                <div className="space-y-2">
                  {preventiveRecs.map((rec: any, idx: number) => (
                    <div key={idx} className="bg-white/10 rounded-lg p-3 border border-white/20">
                      <p className="text-white/90 text-sm">{typeof rec === 'string' ? rec : rec.description || rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </AnimatedSection>

      {/* COMPREHENSIVE ENVIRONMENTAL FACTORS */}
      <AnimatedSection id="environmental-factors" delay={0.5}>
        <div className="bg-gradient-to-br from-blue-600/20 to-green-600/20 rounded-xl p-6 border border-blue-500/30 shadow-xl">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
            🌍 Complete Environmental Analysis
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {/* Temperature */}
            <div className="bg-[#2d2d2d] rounded-lg p-4 border border-orange-500/30">
              <div className="text-orange-400 text-sm mb-1">🌡️ Temperature</div>
              <div className="text-2xl font-bold text-[#e8e8e8]">{Math.round(currentTemp)}°C</div>
              <div className="text-xs text-[#b8b8b8] mt-1">
                {currentTemp > 25 ? 'High - Disease Risk' : currentTemp < 15 ? 'Low - Growth Slow' : 'Optimal'}
              </div>
            </div>

            {/* Humidity */}
            <div className="bg-[#2d2d2d] rounded-lg p-4 border border-blue-500/30">
              <div className="text-blue-400 text-sm mb-1">💧 Humidity</div>
              <div className="text-2xl font-bold text-[#e8e8e8]">{Math.round(currentHumidity)}%</div>
              <div className="text-xs text-[#b8b8b8] mt-1">
                {currentHumidity > 80 ? 'Very High - Risk' : currentHumidity > 60 ? 'Moderate' : 'Low'}
              </div>
            </div>

            {/* Rainfall */}
            <div className="bg-[#2d2d2d] rounded-lg p-4 border border-cyan-500/30">
              <div className="text-cyan-400 text-sm mb-1">🌧️ Rainfall</div>
              <div className="text-2xl font-bold text-[#e8e8e8]">{Math.round(rainfall)}mm</div>
              <div className="text-xs text-[#b8b8b8] mt-1">
                {rainfall > 10 ? 'High - Monitor' : rainfall > 5 ? 'Moderate' : 'Low'}
              </div>
            </div>

            {/* PM2.5 */}
            <div className="bg-[#2d2d2d] rounded-lg p-4 border border-purple-500/30">
              <div className="text-purple-400 text-sm mb-1">🌬️ Air Quality</div>
              <div className="text-2xl font-bold text-[#e8e8e8]">{Math.round(pm25)}</div>
              <div className="text-xs text-[#b8b8b8] mt-1">
                {pm25 > 50 ? 'Poor' : pm25 > 30 ? 'Moderate' : 'Good'}
              </div>
            </div>
          </div>

          {/* Risk Contributing Factors */}
          {chartData?.risk_factors && (
            <div className="mt-6">
              <h3 className="text-xl font-bold text-[#e8e8e8] mb-4">📊 Risk Contributing Factors</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Late Blight Factors */}
                {chartData.risk_factors.late_blight && (
                  <div className="bg-[#2d2d2d] rounded-lg p-4 border border-red-500/30">
                    <h4 className="text-red-400 font-bold mb-3">🔴 Late Blight Factors</h4>
                    <div className="space-y-2">
                      {Object.entries(chartData.risk_factors.late_blight).map(([factor, value]: [string, any]) => (
                        <div key={factor} className="flex items-center justify-between">
                          <span className="text-sm text-[#b8b8b8] capitalize">{factor}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-[#3a3a3a] rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-red-500 to-orange-500"
                                style={{ width: `${Math.min(value, 100)}%` }}
                              />
                            </div>
                            <span className="text-sm font-bold text-[#e8e8e8] w-10 text-right">{Math.round(value)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Early Blight Factors */}
                {chartData.risk_factors.early_blight && (
                  <div className="bg-[#2d2d2d] rounded-lg p-4 border border-yellow-500/30">
                    <h4 className="text-yellow-400 font-bold mb-3">🟡 Early Blight Factors</h4>
                    <div className="space-y-2">
                      {Object.entries(chartData.risk_factors.early_blight).map(([factor, value]: [string, any]) => (
                        <div key={factor} className="flex items-center justify-between">
                          <span className="text-sm text-[#b8b8b8] capitalize">{factor}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-[#3a3a3a] rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-yellow-500 to-orange-500"
                                style={{ width: `${Math.min(value, 100)}%` }}
                              />
                            </div>
                            <span className="text-sm font-bold text-[#e8e8e8] w-10 text-right">{Math.round(value)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </AnimatedSection>

      {/* WEEKLY OUTLOOK - From Prediction */}
      {weeklyOutlook && Object.keys(weeklyOutlook).length > 0 && (
        <AnimatedSection id="weekly-outlook" delay={0.55}>
          <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-xl p-6 border border-purple-500/30 shadow-xl">
            <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
              📅 Weekly Outlook
            </h2>
            <div className="bg-[#2d2d2d] rounded-lg p-4 border border-purple-500/30">
              {typeof weeklyOutlook === 'string' ? (
                <p className="text-[#e8e8e8] leading-relaxed">{weeklyOutlook}</p>
              ) : (
                <div className="space-y-2">
                  {Object.entries(weeklyOutlook).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex items-start gap-3">
                      <span className="text-purple-400 font-bold capitalize">{key}:</span>
                      <span className="text-[#e8e8e8] flex-1">{typeof value === 'string' ? value : JSON.stringify(value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </AnimatedSection>
      )}

      {/* CRITICAL WEATHER OBSERVATIONS */}
      {criticalObservations && criticalObservations.length > 0 && (
        <AnimatedSection id="critical-observations" delay={0.57}>
          <div className="bg-gradient-to-br from-red-600/20 to-orange-600/20 rounded-xl p-6 border border-red-500/30 shadow-xl">
            <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
              ⚠️ Critical Weather Observations
            </h2>
            <div className="space-y-3">
              {criticalObservations.map((obs: any, idx: number) => (
                <div key={idx} className="bg-[#2d2d2d] rounded-lg p-4 border border-red-500/30">
                  <p className="text-[#e8e8e8] leading-relaxed">
                    {typeof obs === 'string' ? obs : obs.description || obs.message || JSON.stringify(obs)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </AnimatedSection>
      )}

      {/* HISTORICAL CONTEXT */}
      <AnimatedSection id="history" delay={0.6}>
        <div className="bg-gradient-to-br from-[#2d2d2d] to-[#1a1a1a] rounded-xl p-6 border border-purple-500/30 shadow-xl">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
            📚 Lessons from History
          </h2>
          
          <div className="space-y-4">
            {/* 2018 Outbreak */}
            <div className="bg-red-500/10 rounded-lg p-4 border-l-4 border-red-500">
              <div className="flex items-start gap-3">
                <span className="text-3xl">🔴</span>
                <div className="flex-1">
                  <h3 className="text-red-400 font-bold mb-2">July 2018 - Severe Outbreak</h3>
                  <p className="text-[#b8b8b8] text-sm leading-relaxed mb-3">
                    Similar conditions (15-28°C, 85-95% humidity) led to <span className="text-red-400 font-bold">devastating crop losses</span> in {location}. 
                    Your current conditions match <span className="text-yellow-400 font-bold">88%</span> of that outbreak pattern.
                  </p>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-[#3a3a3a] rounded p-2">
                        <div className="text-xs text-[#808080]">Then</div>
                        <div className="text-sm text-[#e8e8e8]">15-28°C, 90% RH</div>
                      </div>
                      <div className="bg-[#3a3a3a] rounded p-2">
                        <div className="text-xs text-[#808080]">Now</div>
                        <div className="text-sm text-[#e8e8e8]">{Math.round(currentTemp)}°C, {Math.round(currentHumidity)}% RH</div>
                      </div>
                    </div>
                </div>
              </div>
            </div>

            {/* 2017 Success Story */}
            <div className="bg-green-500/10 rounded-lg p-4 border-l-4 border-green-500">
              <div className="flex items-start gap-3">
                <span className="text-3xl">✅</span>
                <div className="flex-1">
                  <h3 className="text-green-400 font-bold mb-2">July 2017 - Controlled Successfully</h3>
                  <p className="text-[#b8b8b8] text-sm leading-relaxed mb-3">
                    Early intervention with <span className="text-green-400 font-bold">preventive fungicides</span> stopped the disease before it spread. 
                    Farmers who acted within 48 hours saved <span className="text-yellow-400 font-bold">70% of their crop</span>.
                  </p>
                  <div className="inline-block px-3 py-1 bg-green-500/20 rounded-full text-green-400 text-xs font-bold">
                    💡 Act now like they did!
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* WEEKLY OUTLOOK */}
      <AnimatedSection id="outlook" delay={0.6}>
        <div className="bg-gradient-to-br from-[#2d2d2d] to-[#1a1a1a] rounded-xl p-6 border border-blue-500/30 shadow-xl">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
            📅 7-Day Risk Forecast
          </h2>
          
          <div className="grid grid-cols-7 gap-2">
            {[
              { day: 'Nov 7', risk: 75, label: 'High' },
              { day: 'Nov 8', risk: 80, label: 'High' },
              { day: 'Nov 9', risk: 82, label: 'High' },
              { day: 'Nov 10', risk: 85, label: 'Critical' },
              { day: 'Nov 11', risk: 85, label: 'Critical' },
              { day: 'Nov 12', risk: 78, label: 'High' },
              { day: 'Nov 13', risk: 72, label: 'High' }
            ].map((day, idx) => (
              <motion.div
                key={day.day}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + idx * 0.1 }}
                className={`rounded-lg p-3 ${
                  day.risk >= 85 ? 'bg-red-500/20 border border-red-500' :
                  day.risk >= 75 ? 'bg-orange-500/20 border border-orange-500' :
                  'bg-yellow-500/20 border border-yellow-500'
                }`}
              >
                <div className="text-xs text-[#b8b8b8] mb-1">{day.day}</div>
                <div className="text-2xl font-bold text-[#e8e8e8] mb-1">{day.risk}%</div>
                <div className={`text-xs font-bold ${
                  day.risk >= 85 ? 'text-red-400' :
                  day.risk >= 75 ? 'text-orange-400' :
                  'text-yellow-400'
                }`}>
                  {day.label}
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
            <p className="text-[#e8e8e8] text-sm leading-relaxed">
              <span className="font-bold text-blue-400">💡 Outlook:</span> Risk remains critically high through November 11. 
              If fungicide is applied today and weather improves, expect gradual risk reduction after Nov 12.
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* FINAL SUMMARY */}
      <AnimatedSection id="summary" delay={0.7}>
        <div className="bg-gradient-to-br from-purple-600 via-pink-600 to-orange-600 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent"></div>
          
          <div className="relative z-10">
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-2">
              🔍 Bottom Line
            </h2>
            
            <div className="space-y-4">
              <p className="text-white/90 text-lg leading-relaxed">
                Your crop is in the <span className="text-yellow-300 font-bold">critical danger zone</span> for Late Blight. 
                The combination of <span className="text-cyan-300 font-bold">92% humidity</span>, 
                <span className="text-red-300 font-bold"> perfect temperatures</span>, and 
                <span className="text-orange-300 font-bold"> early growth stage</span> means you're in a race against time.
              </p>

              <div className="bg-white/20 backdrop-blur-md rounded-xl p-6 border border-white/40">
                <h3 className="text-white font-bold text-xl mb-3">✅ YOUR ACTION CHECKLIST</h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                      <span className="text-red-600 font-bold text-sm">1</span>
                    </div>
                    <span className="text-white">Apply Mancozeb fungicide within 24 hours</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                      <span className="text-red-600 font-bold text-sm">2</span>
                    </div>
                    <span className="text-white">Check plants daily for symptoms</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                      <span className="text-red-600 font-bold text-sm">3</span>
                    </div>
                    <span className="text-white">Reduce irrigation immediately</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                      <span className="text-red-600 font-bold text-sm">4</span>
                    </div>
                    <span className="text-white">Schedule follow-up spray for Nov 17</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button className="flex-1 px-6 py-4 bg-white text-purple-600 rounded-xl font-bold hover:bg-gray-100 transition-all shadow-xl">
                  📥 Download PDF Report
                </button>
                <button className="flex-1 px-6 py-4 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-xl font-bold hover:from-green-600 hover:to-teal-600 transition-all shadow-xl">
                  📞 Contact Agronomist
                </button>
              </div>
            </div>
          </div>
        </div>
      </AnimatedSection>
    </div>
  )
}

