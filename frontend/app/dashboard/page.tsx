'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { authAPI, chatAPI, getApiBaseUrl } from '@/lib/api'
import { motion } from 'framer-motion'
import EnhancedAICropAdvisor from '@/components/EnhancedAICropAdvisor'
import ChartAgent from '@/components/ChartAgent'
import CinematicReportPanel from '@/components/CinematicReportPanel'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState<any>(null)

  useEffect(() => {
    checkAuthAndLoadData()
  }, [])

  // Auto-trigger prediction is now handled in loadDashboardData

  // Implement real-time polling (refresh every 15 minutes)
  useEffect(() => {
    if (!user || !dashboardData) return

    const POLL_INTERVAL = 15 * 60 * 1000 // 15 minutes in milliseconds

    const pollData = async () => {
      console.log('[DASHBOARD] Polling for new data...')
      await loadDashboardData(user)
    }

    const intervalId = setInterval(pollData, POLL_INTERVAL)

    // Cleanup interval on unmount
    return () => clearInterval(intervalId)
  }, [user, dashboardData])

  const checkAuthAndLoadData = async () => {
    try {
      const response = await authAPI.getCurrentUser()
      if (response.success) {
        setUser(response.user)
        // Check if user has fields
        if (!response.user.fields || response.user.fields.length === 0) {
          router.push('/setup-field')
          return
        }
        // Load dashboard data based on user's location and DOS
        await loadDashboardData(response.user)
      } else {
        router.push('/login')
      }
    } catch {
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  const loadDashboardData = async (userData: any) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      // Extract field data first (always available)
      const field = userData.fields?.[0]
      if (!field) {
        console.error('[DASHBOARD] No field data found')
        return
      }

      // Set basic data immediately (so UI can render)
      const basicData = {
        location: field.location || 'Unknown Location',
        sowingDate: field.sowing_date || new Date().toISOString().split('T')[0],
        growthStage: calculateGrowthStage(field.sowing_date),
        daysAfterPlanting: calculateDaysAfterPlanting(field.sowing_date),
        latitude: field.latitude,
        longitude: field.longitude,
        elevation: field.elevation
      }
      setDashboardData(basicData)
      console.log('[DASHBOARD] Basic data loaded:', basicData)

      // Check if we should auto-trigger prediction
      const autoPredict = localStorage.getItem('auto_predict')
      if (autoPredict === 'true') {
        console.log('[DASHBOARD] Auto-predict flag detected, triggering prediction...')
        localStorage.removeItem('auto_predict')
        
        // Trigger prediction via chat API
        try {
          const predictResponse = await fetch(`${getApiBaseUrl()}/api/chat/stream`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              message: `What is the disease risk for my crop? Location: ${field.location}, Date of Sowing: ${field.sowing_date}`,
              agent: 'predictive'
            })
          })
          
          if (predictResponse.ok) {
            console.log('[DASHBOARD] Prediction triggered successfully')
            // Prediction will update dashboard data via polling
          }
        } catch (err) {
          console.error('[DASHBOARD] Error triggering prediction:', err)
        }
      }

      // Call the dashboard API endpoint for real-time data
      const response = await fetch(`${getApiBaseUrl()}/api/dashboard`, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          // Merge API data with basic field data
          setDashboardData({
            ...basicData,
            ...data.data,
            // Ensure location and DOS are always from field (most reliable)
            location: field.location || data.data.location,
            sowingDate: field.sowing_date || data.data.sowingDate
          })
          console.log('[DASHBOARD] Full data loaded from API')
          return
        }
      }
      
      // If API fails, we already have basic data set above
      console.log('[DASHBOARD] Using basic field data (API unavailable)')
    } catch (error) {
      console.error('[DASHBOARD] Error loading data:', error)
      // Ensure we at least have basic data
      if (userData?.fields?.[0]) {
        const field = userData.fields[0]
        setDashboardData({
          location: field.location || 'Unknown Location',
          sowingDate: field.sowing_date || new Date().toISOString().split('T')[0],
          growthStage: calculateGrowthStage(field.sowing_date),
          daysAfterPlanting: calculateDaysAfterPlanting(field.sowing_date)
        })
      }
    }
  }

  const calculateDaysAfterPlanting = (sowingDate: string): number => {
    const sowing = new Date(sowingDate)
    const today = new Date()
    const diffTime = Math.abs(today.getTime() - sowing.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const calculateGrowthStage = (sowingDate: string): string => {
    const days = calculateDaysAfterPlanting(sowingDate)
    if (days < 15) return 'Emergence'
    if (days < 30) return 'Vegetative Growth'
    if (days < 50) return 'Tuber Initiation'
    if (days < 80) return 'Tuber Bulking'
    if (days < 110) return 'Maturation'
    return 'Harvest Ready'
  }

  const handleLogout = () => {
    authAPI.logout()
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#1a1a1a]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-[#e8e8e8] text-lg">Loading Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-[#1a1a1a] overflow-hidden">
      {/* Header - Colorful Gradient */}
      <div className="h-16 border-b border-orange-500/30 flex items-center justify-between px-6 bg-gradient-to-r from-orange-600 via-orange-500 to-yellow-500 shadow-lg">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-white drop-shadow-lg" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
            🥔 Potato Crop Health Dashboard
          </h1>
          <div className="flex items-center gap-2 text-sm text-white/90 bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm">
            <span>📍 {dashboardData?.location || user?.fields?.[0]?.location || 'Unknown Location'}</span>
            <span>•</span>
            <span>🌱 Day {dashboardData?.daysAfterPlanting || (user?.fields?.[0]?.sowing_date ? calculateDaysAfterPlanting(user.fields[0].sowing_date) : 0)} ({dashboardData?.growthStage || (user?.fields?.[0]?.sowing_date ? calculateGrowthStage(user.fields[0].sowing_date) : 'Unknown')})</span>
            {user?.fields?.[0]?.sowing_date && (
              <>
                <span>•</span>
                <span>📅 Sown: {new Date(user.fields[0].sowing_date).toLocaleDateString()}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/chat')}
            className="px-4 py-2 bg-white/20 text-white rounded-full hover:bg-white/30 transition-colors text-sm font-medium backdrop-blur-sm border border-white/30"
          >
            💬 Chat
          </button>
          <div className="text-sm text-white/90">{user?.email}</div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-white/20 text-white rounded-full hover:bg-white/30 transition-colors text-sm backdrop-blur-sm border border-white/30"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Dashboard Grid - 3 Panels (Responsive) */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* LEFT PANEL - 25% on desktop, full width on mobile */}
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full lg:w-1/4 border-b lg:border-b-0 lg:border-r border-[#3a3a3a] overflow-y-auto bg-[#1a1a1a]"
        >
          <LeftPanel dashboardData={dashboardData} />
        </motion.div>

        {/* CENTER PANEL - 50% on desktop, full width on mobile */}
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full lg:w-1/2 border-b lg:border-b-0 overflow-y-auto bg-[#1a1a1a]"
        >
          <CenterPanel dashboardData={dashboardData} user={user} />
        </motion.div>

        {/* RIGHT PANEL - 25% on desktop, full width on mobile */}
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="w-full lg:w-1/4 lg:border-l border-[#3a3a3a] overflow-y-auto bg-[#1a1a1a]"
        >
          <RightPanel dashboardData={dashboardData} />
        </motion.div>
      </div>
    </div>
  )
}

// ============================================================================
// LEFT PANEL COMPONENT - Diagnostic Agent & Recommendations
// ============================================================================
function LeftPanel({ dashboardData }: { dashboardData: any }) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [diagnosing, setDiagnosing] = useState(false)
  const [diagnosis, setDiagnosis] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const handleImageSelect = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target?.result as string
      setSelectedImage(base64)
      // Automatically start diagnosis
      analyzImage(base64)
    }
    reader.readAsDataURL(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      handleImageSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const analyzImage = async (imageData: string) => {
    setDiagnosing(true)
    setDiagnosis(null)

    try {
      // Call diagnostic agent through chat API
      // For now, use a simplified version - you can enhance this
      // to call a dedicated diagnostic endpoint
      
      // Simulated diagnosis result (replace with actual API call)
      setTimeout(() => {
        setDiagnosis({
          disease_type: 'Late Blight',
          confidence: 92,
          severity: 'High',
          affected_areas: ['Upper leaf surface (60%)', 'Stem junction (30%)'],
          environmental_factors: [
            'High humidity (87%)',
            'Temperature range: 12-18°C',
            'Recent rainfall: 15mm'
          ],
          risk_level: 'CRITICAL',
          recommendations: [
            {
              priority: 'IMMEDIATE',
              actions: [
                'Apply Mancozeb fungicide - Dosage: 2.5kg/hectare',
                'Remove infected leaves and destroy away from field'
              ]
            },
            {
              priority: 'NEXT 7 DAYS',
              actions: [
                'Monitor humidity levels',
                'Reduce irrigation frequency',
                'Apply preventive spray on Day 7 if humidity >80%'
              ]
            }
          ]
        })
        setDiagnosing(false)
      }, 3000)
    } catch (error) {
      console.error('Diagnosis error:', error)
      setDiagnosing(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Image Upload Section */}
      <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a]">
        <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
          📸 Upload Crop Image
        </h2>
        
        {!selectedImage ? (
          <>
            <div 
              className="border-2 border-dashed border-[#4a4a4a] rounded-lg p-8 text-center hover:border-orange-500 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <div className="text-5xl mb-4">📷</div>
              <p className="text-[#b8b8b8] mb-2">Drag & Drop Image</p>
              <p className="text-sm text-[#808080]">or Click to Upload</p>
              <p className="text-xs text-[#606060] mt-2">JPG, PNG, HEIC • Max 10MB</p>
            </div>
            <div className="flex gap-2 mt-4">
              <button 
                onClick={() => cameraInputRef.current?.click()}
                className="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
              >
                📷 Take Photo
              </button>
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="flex-1 px-4 py-2 bg-[#3a3a3a] text-[#e8e8e8] rounded-lg hover:bg-[#4a4a4a] transition-colors"
              >
                📁 Upload
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => e.target.files && handleImageSelect(e.target.files[0])}
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={(e) => e.target.files && handleImageSelect(e.target.files[0])}
            />
          </>
        ) : (
          <div>
            <img
              src={selectedImage}
              alt="Uploaded crop"
              className="w-full rounded-lg mb-4"
            />
            <button
              onClick={() => {
                setSelectedImage(null)
                setDiagnosis(null)
              }}
              className="w-full px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              🗑️ Remove Image
            </button>
          </div>
        )}
      </section>

      {/* AI Diagnosis Results */}
      <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a]">
        <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
          🧬 AI Diagnosis
        </h2>
        
        {diagnosing ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-[#b8b8b8]">Analyzing image...</p>
          </div>
        ) : diagnosis ? (
          <div className="space-y-4">
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
              <h3 className="text-lg font-bold text-red-400 mb-2">🔴 {diagnosis.disease_type} Detected</h3>
              <p className="text-sm text-[#e8e8e8]">Confidence: <span className="font-bold">{diagnosis.confidence}%</span></p>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-[#e8e8e8] mb-2">📍 Affected Areas:</h4>
              <ul className="text-sm text-[#b8b8b8] space-y-1">
                {diagnosis.affected_areas.map((area: string, idx: number) => (
                  <li key={idx}>• {area}</li>
                ))}
              </ul>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-[#e8e8e8] mb-2">🌡️ Environmental Factors:</h4>
              <ul className="text-sm text-[#b8b8b8] space-y-1">
                {diagnosis.environmental_factors.map((factor: string, idx: number) => (
                  <li key={idx}>• {factor}</li>
                ))}
              </ul>
            </div>
            
            <div className="bg-red-500/10 rounded-lg p-3">
              <p className="text-sm font-bold text-red-400">⚠️ Risk Level: {diagnosis.risk_level}</p>
            </div>
          </div>
        ) : (
          <div className="text-center text-[#808080] py-8">
            <div className="text-4xl mb-4">🔍</div>
            <p>Upload an image to get AI-powered</p>
            <p>disease diagnosis</p>
          </div>
        )}
      </section>

      {/* Historical Outbreaks Comparison */}
      <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a]">
        <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
          📚 Historical Context
        </h2>
        {dashboardData && (
          <div className="space-y-4">
            <div className="bg-[#3a3a3a] rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#e8e8e8]">🔴 Similar Outbreak - 2021</h3>
                <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded">88% Match</span>
              </div>
              <p className="text-xs text-[#b8b8b8] mb-2">
                Weather patterns match severe late blight outbreak in South India
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[#808080]">Then:</span>
                  <span className="text-[#e8e8e8] ml-1">27°C, 87% RH</span>
                </div>
                <div>
                  <span className="text-[#808080]">Now:</span>
                  <span className="text-[#e8e8e8] ml-1">{dashboardData.current_temp || '–'}°C, {dashboardData.current_humidity || '–'}% RH</span>
                </div>
              </div>
            </div>

            <div className="bg-[#3a3a3a] rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#e8e8e8]">🟡 Similar Conditions - 2018</h3>
                <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded">67% Match</span>
              </div>
              <p className="text-xs text-[#b8b8b8] mb-2">
                Moderate risk period with controlled outbreak via early intervention
              </p>
              <div className="text-xs text-green-400">
                ✅ Success: Early fungicide application prevented spread
              </div>
            </div>

            <div className="bg-[#3a3a3a] rounded-lg p-4">
              <h4 className="text-xs font-semibold text-[#e8e8e8] mb-2">📊 Regional Statistics</h4>
              <div className="space-y-1 text-xs text-[#b8b8b8]">
                <p>• Last outbreak: <span className="text-[#e8e8e8]">18 months ago</span></p>
                <p>• Avg. loss: <span className="text-red-400">32% yield</span></p>
                <p>• Recovery time: <span className="text-[#e8e8e8]">2-3 weeks</span></p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Treatment Recommendations */}
      <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a]">
        <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
          💊 Recommended Actions
        </h2>
        {diagnosis && diagnosis.recommendations ? (
          <div className="space-y-4">
            {diagnosis.recommendations.map((rec: any, idx: number) => (
              <div key={idx} className="bg-[#3a3a3a] rounded-lg p-4">
                <div className={`text-sm font-medium mb-2 ${
                  rec.priority === 'IMMEDIATE' ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  {rec.priority === 'IMMEDIATE' ? '🚨' : '📅'} {rec.priority}
                </div>
                <ul className="space-y-2">
                  {rec.actions.map((action: string, aidx: number) => (
                    <li key={aidx} className="text-sm text-[#e8e8e8]">
                      • {action}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
            <div className="flex gap-2">
              <button className="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm">
                🛒 Buy Fungicide
              </button>
              <button className="flex-1 px-4 py-2 bg-[#3a3a3a] text-[#e8e8e8] rounded-lg hover:bg-[#4a4a4a] transition-colors text-sm">
                📞 Contact Expert
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="bg-[#3a3a3a] rounded-lg p-4">
              <div className="text-sm text-orange-400 font-medium mb-1">🚨 IMMEDIATE</div>
              <p className="text-[#e8e8e8] text-sm">Monitor humidity levels closely</p>
            </div>
            <div className="bg-[#3a3a3a] rounded-lg p-4">
              <div className="text-sm text-yellow-400 font-medium mb-1">📅 NEXT 7 DAYS</div>
              <p className="text-[#e8e8e8] text-sm">Prepare fungicide application if risk increases</p>
            </div>
          </div>
        )}
      </section>

      {/* Historical Outbreaks Placeholder */}
      <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a]">
        <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
          📚 Historical Context
        </h2>
        <div className="text-sm text-[#b8b8b8]">
          <p className="mb-2">🗓️ <span className="text-[#e8e8e8] font-medium">Last Outbreak:</span> Nov 2023</p>
          <p className="text-xs text-[#808080]">Weather conditions were similar to current patterns</p>
        </div>
      </section>
    </div>
  )
}

// ============================================================================
// CENTER PANEL COMPONENT - Location & Cinematic Report
// ============================================================================
function CenterPanel({ dashboardData, user }: { dashboardData: any; user: any }) {
  // Get location from dashboardData or user profile
  const location = dashboardData?.location || user?.fields?.[0]?.location
  let latitude = dashboardData?.latitude || user?.fields?.[0]?.latitude
  let longitude = dashboardData?.longitude || user?.fields?.[0]?.longitude
  const elevation = dashboardData?.elevation || user?.fields?.[0]?.elevation
  
  // Validate coordinates
  if (latitude && (isNaN(latitude) || latitude < -90 || latitude > 90)) {
    console.warn('[DASHBOARD] Invalid latitude:', latitude)
    latitude = undefined
  }
  if (longitude && (isNaN(longitude) || longitude < -180 || longitude > 180)) {
    console.warn('[DASHBOARD] Invalid longitude:', longitude)
    longitude = undefined
  }

  const formatCoordinate = (value: any) => {
    if (value === undefined || value === null || value === '') return '--'
    const num = typeof value === 'number' ? value : parseFloat(value)
    return Number.isFinite(num) ? num.toFixed(3) : '--'
  }
  const formatElevation = (value: any) => {
    if (value === undefined || value === null || value === '') return '--'
    const num = typeof value === 'number' ? value : parseFloat(value)
    return Number.isFinite(num) ? `${Math.round(num)} m` : '--'
  }

  const currentRisk = dashboardData?.disease_risks?.[0]
  const currentWeather = dashboardData?.weather_data?.[0]
  const lateRiskValue = currentRisk?.late_blight_pct
  const earlyRiskValue = currentRisk?.early_blight_pct
  const isLateRiskFinite = Number.isFinite(lateRiskValue ?? NaN)
  const isEarlyRiskFinite = Number.isFinite(earlyRiskValue ?? NaN)

  return (
    <div className="p-6 space-y-6">
      {location && (
        <section className="bg-[#2d2d2d] rounded-xl p-6 border border-orange-500/30 shadow-xl">
          <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
            📍 Active Field Location
          </h2>
          <p className="text-sm text-[#b8b8b8] mb-4">
            Every agent, insight, and visualization on this dashboard is running against <span className="text-white font-semibold">{location}</span> exactly as you entered it. No map is rendered, but the coordinates stay locked to your selection.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="bg-[#1a1a1a] rounded-lg p-4 border border-white/10">
              <div className="text-xs uppercase tracking-[0.3em] text-white/50 mb-2">Exact Input</div>
              <div className="text-2xl font-semibold text-white">{location}</div>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-4 border border-white/10">
              <div className="text-xs uppercase tracking-[0.3em] text-white/50 mb-2">Latitude</div>
              <div className="text-2xl font-semibold text-white">{formatCoordinate(latitude)}</div>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-4 border border-white/10">
              <div className="text-xs uppercase tracking-[0.3em] text-white/50 mb-2">Longitude</div>
              <div className="text-2xl font-semibold text-white">{formatCoordinate(longitude)}</div>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-4 border border-white/10">
              <div className="text-xs uppercase tracking-[0.3em] text-white/50 mb-2">Elevation</div>
              <div className="text-2xl font-semibold text-white">{formatElevation(elevation)}</div>
            </div>
          </div>
          {(currentRisk || currentWeather) && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[#3a3a3a]">
                <div className="text-sm text-[#b8b8b8] mb-1">Late Blight Risk</div>
                <div className="text-3xl font-bold text-red-400">
                  {isLateRiskFinite ? Math.round(lateRiskValue!) : '—'}%
                </div>
              </div>
              <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[#3a3a3a]">
                <div className="text-sm text-[#b8b8b8] mb-1">Early Blight Risk</div>
                <div className="text-3xl font-bold text-yellow-300">
                  {isEarlyRiskFinite ? Math.round(earlyRiskValue!) : '—'}%
                </div>
              </div>
              <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[#3a3a3a]">
                <div className="text-sm text-[#b8b8b8] mb-1">Temp / Humidity</div>
                <div className="text-lg font-semibold">
                  {currentWeather
                    ? `${Math.round(currentWeather?.temp_avg ?? 0)}°C • ${Math.round(currentWeather?.humidity_avg ?? 0)}%`
                    : '—'}
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* CINEMATIC REPORT - The Story Unfolds with Real Prediction Data */}
      {dashboardData && (
        <CinematicReportPanel 
          reportData={dashboardData}
          chartData={dashboardData.chart_data}
        />
      )}

      {/* Charts Section - For Data Visualization */}
      {dashboardData?.chart_data && (
        <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a] shadow-xl">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-6 flex items-center gap-2">
            📊 Detailed Analytics
          </h2>
          <ChartAgent chartData={dashboardData.chart_data} />
        </section>
      )}
    </div>
  )
}

// ============================================================================
// RIGHT PANEL COMPONENT - Charts & Analytics
// ============================================================================
function RightPanel({ dashboardData }: { dashboardData: any }) {
  // Always show AI Advisor, even with minimal data
  const location = dashboardData?.location || 'Unknown Location'
  const sowingDate = dashboardData?.sowingDate || dashboardData?.sowing_date || new Date().toISOString().split('T')[0]
  const growthStage = dashboardData?.growthStage || 'Unknown'
  const daysAfterPlanting = dashboardData?.daysAfterPlanting || 0

  return (
    <div className="p-6 space-y-6">
      {/* Enhanced AI Crop Advisor - OpenAI Powered - ALWAYS VISIBLE */}
      <section>
        <EnhancedAICropAdvisor
          location={location}
          sowingDate={sowingDate}
          growthStage={growthStage}
          daysAfterPlanting={daysAfterPlanting}
          currentRisks={{
            late_blight: dashboardData?.late_blight_risk || 0,
            early_blight: dashboardData?.early_blight_risk || 0,
            overall: dashboardData?.overall_risk || 0
          }}
        />
      </section>

      {/* Disease Risk & Weather Charts */}
      {dashboardData?.chart_data && (
        <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a]">
          <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
            📊 Risk & Weather Analytics
          </h2>
          <ChartAgent chartData={dashboardData.chart_data} />
        </section>
      )}

      {/* Quick Stats */}
      <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a]">
        <h2 className="text-xl font-semibold text-[#e8e8e8] mb-4 flex items-center gap-2">
          ⚡ Quick Stats
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#3a3a3a] rounded-lg p-4">
            <div className="text-2xl font-bold text-orange-400">
              {dashboardData?.late_blight_risk || '0'}%
            </div>
            <div className="text-xs text-[#b8b8b8] mt-1">Late Blight Risk</div>
          </div>
          <div className="bg-[#3a3a3a] rounded-lg p-4">
            <div className="text-2xl font-bold text-yellow-400">
              {dashboardData?.early_blight_risk || '0'}%
            </div>
            <div className="text-xs text-[#b8b8b8] mt-1">Early Blight Risk</div>
          </div>
          <div className="bg-[#3a3a3a] rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-400">
              {dashboardData?.current_temp || '–'}°C
            </div>
            <div className="text-xs text-[#b8b8b8] mt-1">Current Temp</div>
          </div>
          <div className="bg-[#3a3a3a] rounded-lg p-4">
            <div className="text-2xl font-bold text-green-400">
              {dashboardData?.current_humidity || '–'}%
            </div>
            <div className="text-xs text-[#b8b8b8] mt-1">Humidity</div>
          </div>
        </div>
      </section>
    </div>
  )
}
