'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { authAPI, getApiBaseUrl } from '@/lib/api'
import LocationSelector from './LocationSelector'
import ForecastCards from './ForecastCards'
import DiseaseRiskSummary from './DiseaseRiskSummary'
import WeatherTrends from './WeatherTrends'
import SoilMoistureViz from './SoilMoistureViz'
import DiseaseRiskTimeline from './DiseaseRiskTimeline'
import RiskFactorContributions from './RiskFactorContributions'
import HistoricalContext from './HistoricalContext'
import ManagementRecommendations from './ManagementRecommendations'
import WeeklyOutlook from './WeeklyOutlook'
import { exportDashboardToPDF } from './PDFExporter'
import DashboardChatAssistant from './DashboardChatAssistant'

interface MLValidation {
  validated: boolean
  adjustment_made: boolean
  disagreement_score: number
  ml_prediction: {
    disease: string
    confidence: number
    late_blight: number
    early_blight: number
  }
  model_accuracy?: number
  model_metrics?: {
    accuracy: number
    precision: number
    recall: number
    f1_score: number
    training_samples: number
    test_samples: number
  }
  recommendation: string
}

interface DashboardData {
  location: string
  latitude: number
  longitude: number
  date_range: string[]
  weather_data: DailyWeather[]
  soil_data: DailySoil[]
  disease_risks: DailyDiseaseRisk[]
  historical_outbreaks: HistoricalOutbreak[]
  recommendations: Recommendations
  weekly_outlook: WeeklyOutlookData
  prediction?: {
    growth_stage?: string
    days_after_planting?: number
    sowing_date?: string
    ml_validation?: MLValidation
  }
}

interface DailyWeather {
  date: string
  temp_min: number
  temp_avg: number
  temp_max: number
  humidity_avg: number
  humidity_min?: number
  humidity_max?: number
  precipitation: number
  precipitation_probability?: number
  precipitation_type?: string
  wind_speed: number
  wind_direction_10m?: number
  wind_gusts_10m?: number
  cloud_cover: number
  dewpoint_2m?: number
  visibility?: number
  uv_index?: number
}

interface DailySoil {
  date: string
  soil_moisture_percent: number
}

interface DailyDiseaseRisk {
  date: string
  late_blight_pct: number
  early_blight_pct: number
  overall_pct: number
  contributions?: {
    late_blight?: RiskFactorBreakdown
    early_blight?: RiskFactorBreakdown
  }
}

interface RiskFactorBreakdown {
  temperature: number
  humidity: number
  precipitation: number
  wind: number
  cloud_cover: number
}

interface HistoricalOutbreak {
  year: number
  region: string
  avg_temp: number
  avg_humidity: number
  notes: string
  references: string[]
}

interface Recommendations {
  immediate_actions: string[]
  preventive_measures: string[]
  cultural_practices: string[]
}

interface WeeklyOutlookData {
  risk_persistence: string
  critical_days: string[]
  monitoring_actions: string[]
}

export default function ProductionDashboard() {
  const [selectedLocation, setSelectedLocation] = useState<{ name: string; lat: number; lon: number } | null>(null)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [chatTab, setChatTab] = useState<'diagnostic' | 'predictive'>('predictive')
  const [initialChatQuestion, setInitialChatQuestion] = useState<string>('')
  const [scrollY, setScrollY] = useState(0)
  const [selectedDayIndex, setSelectedDayIndex] = useState<number>(0)
  const riskEntries = dashboardData?.disease_risks
  const safeRiskIndex = riskEntries && riskEntries.length ? Math.min(selectedDayIndex, riskEntries.length - 1) : 0
  const selectedRiskEntry = riskEntries && riskEntries.length ? riskEntries[safeRiskIndex] : undefined
  const selectedWeatherEntry = dashboardData?.weather_data?.[safeRiskIndex]
  const selectedSoilEntry = dashboardData?.soil_data?.[safeRiskIndex]
  const latDisplay = selectedLocation ? selectedLocation.lat.toFixed(3) : '--'
  const lonDisplay = selectedLocation ? selectedLocation.lon.toFixed(3) : '--'

  // Helper function to extract simple city name from verbose location string
  // e.g., "Coventry, West Midlands, England, United Kingdom" -> "Coventry"
  const extractSimpleCityName = (locationStr: string): string => {
    if (!locationStr) return locationStr
    // Take just the first part before the first comma
    const parts = locationStr.split(',')
    return parts[0].trim()
  }

  // Load user's default location on mount - Check localStorage first (from welcome page or LocationSelector)
  useEffect(() => {
    const loadUserLocation = async () => {
      console.log('[DASHBOARD] Loading user location...')
      
      // PRIORITY 1: Check localStorage for location (from welcome page OR LocationSelector updates)
      const predictLocation = localStorage.getItem('predict_location')
      const selectedLat = localStorage.getItem('selected_lat')
      const selectedLng = localStorage.getItem('selected_lng')
      
      if (predictLocation && selectedLat && selectedLng) {
        const lat = parseFloat(selectedLat)
        const lon = parseFloat(selectedLng)
        if (!isNaN(lat) && !isNaN(lon)) {
          // Clean up verbose location name (in case old format was cached)
          const simpleName = extractSimpleCityName(predictLocation)
          console.log('[DASHBOARD] Using coordinates from localStorage:', lat, lon, '- cleaned name:', simpleName)
          setSelectedLocation({
            name: simpleName,
            lat: lat,
            lon: lon
          })
          // Only clear auto_predict flag if it exists (don't clear user's manual selection)
          if (localStorage.getItem('auto_predict') === 'true') {
            localStorage.removeItem('auto_predict')
            localStorage.removeItem('predict_dos')
          }
          return
        }
      }
      
      // If localStorage has location name but no coordinates, geocode it
      if (predictLocation && (!selectedLat || !selectedLng)) {
        const token = localStorage.getItem('auth_token')
        try {
          console.log('[DASHBOARD] Geocoding location from localStorage:', predictLocation)
          const geoResponse = await fetch(
            `${getApiBaseUrl()}/api/geocode?query=${encodeURIComponent(predictLocation)}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
          )
          
          if (geoResponse.ok) {
            const geoData = await geoResponse.json()
            if (geoData.success && geoData.location) {
              const location = {
                name: geoData.location.name,
                lat: geoData.location.latitude,
                lon: geoData.location.longitude
              }
              console.log('[DASHBOARD] Setting location from localStorage geocoding:', location)
              // Save coordinates to localStorage for future use
              localStorage.setItem('selected_lat', String(location.lat))
              localStorage.setItem('selected_lng', String(location.lon))
              setSelectedLocation(location)
              // Only clear auto_predict flag if it exists
              if (localStorage.getItem('auto_predict') === 'true') {
                localStorage.removeItem('auto_predict')
                localStorage.removeItem('predict_dos')
              }
              return
            }
          }
        } catch (geoErr) {
          console.error('[DASHBOARD] Geocoding error:', geoErr)
        }
      }
      
      // PRIORITY 2: Load from user profile (only if localStorage doesn't have location)
      try {
        const userResponse = await authAPI.getCurrentUser()
        console.log('[DASHBOARD] User response:', userResponse)
        
        if (userResponse.success && userResponse.user.fields?.length > 0) {
          const sortedFields = [...userResponse.user.fields].sort((a, b) => {
            const aDate = new Date(a.updated_at || a.created_at || 0).getTime()
            const bDate = new Date(b.updated_at || b.created_at || 0).getTime()
            return bDate - aDate
          })
          const field = sortedFields[0]
          console.log('[DASHBOARD] User field:', field)
          
          if (field.location) {
            // Use stored coordinates if available and valid (NO AUTO-GEOCODING)
            if (field.latitude && field.longitude && 
                !isNaN(field.latitude) && !isNaN(field.longitude) &&
                field.latitude >= -90 && field.latitude <= 90 &&
                field.longitude >= -180 && field.longitude <= 180) {
              // Clean up verbose location name (e.g., "Coventry, West Midlands, England, United Kingdom" -> "Coventry")
              const simpleName = extractSimpleCityName(field.location)
              const location = {
                name: simpleName,
                lat: field.latitude,
                lon: field.longitude
              }
              console.log('[DASHBOARD] Setting location from profile coordinates (cleaned):', location)
              // Save to localStorage so future loads use this instead of profile
              localStorage.setItem('predict_location', simpleName)
              localStorage.setItem('selected_lat', String(location.lat))
              localStorage.setItem('selected_lng', String(location.lon))
              setSelectedLocation(location)
            } else {
              console.warn('[DASHBOARD] No valid coordinates found in profile, location will need to be selected')
              // DO NOT auto-geocode - let user select location manually
            }
          } else {
            console.log('[DASHBOARD] No location in field data')
          }
        } else {
          console.log('[DASHBOARD] No user fields found')
        }
      } catch (err) {
        console.error('[DASHBOARD] Error loading user location:', err)
      }
    }
    loadUserLocation()
  }, [])

  // Fetch dashboard data when location changes
  useEffect(() => {
    if (!selectedLocation) {
      console.log('[DASHBOARD] No location selected, skipping fetch')
      return
    }

    console.log('[DASHBOARD] Location changed, fetching data for:', selectedLocation)
    console.log('[DASHBOARD] Location details - name:', selectedLocation.name, 'lat:', selectedLocation.lat, 'lon:', selectedLocation.lon)

    // Create abort controller to cancel in-flight requests
    const abortController = new AbortController()
    let isCancelled = false

    const fetchDashboardData = async () => {
      // Clear old data immediately when location changes
      setDashboardData(null)
      setLoading(true)
      setError(null)
      setSelectedDayIndex(0)
      
      // Create a unique key for this request to prevent race conditions
      const requestKey = `${selectedLocation.name}-${selectedLocation.lat}-${selectedLocation.lon}-${Date.now()}`
      console.log('[DASHBOARD] Request key:', requestKey)

      try {
        const token = localStorage.getItem('auth_token')
        if (!token) {
          throw new Error('No authentication token found')
        }

        const requestBody = {
          location: selectedLocation.name,
          latitude: selectedLocation.lat,
          longitude: selectedLocation.lon,
          date_range: '8-day'
        }
        
        console.log('[DASHBOARD] Request body:', requestBody)
        
        const response = await fetch(`${getApiBaseUrl()}/api/dashboard/advanced`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(requestBody),
          signal: abortController.signal
        })
        
        console.log('[DASHBOARD] Response status:', response.status, response.statusText)

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        // Check if request was cancelled
        if (isCancelled) {
          console.log('[DASHBOARD] Request was cancelled, ignoring response')
          return
        }

        const data = await response.json()
        console.log('[DASHBOARD] API Response received')
        console.log('[DASHBOARD] Response location:', data.data?.location)
        console.log('[DASHBOARD] Response coordinates:', data.data?.latitude, data.data?.longitude)
        
        // Check again after async operation
        if (isCancelled) {
          console.log('[DASHBOARD] Request was cancelled after response, ignoring data')
          return
        }
        
        if (data.success && data.data) {
          // Verify the response matches our request
          const responseLocation = data.data.location
          const responseLat = data.data.latitude
          const responseLon = data.data.longitude
          
          console.log('[DASHBOARD] Request was for:', selectedLocation.name, selectedLocation.lat, selectedLocation.lon)
          console.log('[DASHBOARD] Response is for:', responseLocation, responseLat, responseLon)
          
          // Check if response matches request (allow small coordinate differences)
          const latMatch = Math.abs(selectedLocation.lat - responseLat) < 0.01
          const lonMatch = Math.abs(selectedLocation.lon - responseLon) < 0.01
          
          if (!latMatch || !lonMatch) {
            console.warn('[DASHBOARD] WARNING: Response location does not match request!')
            console.warn('[DASHBOARD] Request:', selectedLocation)
            console.warn('[DASHBOARD] Response:', { name: responseLocation, lat: responseLat, lon: responseLon })
          }
          
          console.log('[DASHBOARD] Setting dashboard data for:', responseLocation)
          setDashboardData(data.data)
          setSelectedDayIndex(0)
          setLastUpdated(new Date())
          
          // Only update selectedLocation if it's different (to avoid infinite loops)
          // But use the response location to ensure consistency
          if (responseLocation && responseLat && responseLon) {
            const apiLocation = {
              name: responseLocation,
              lat: responseLat,
              lon: responseLon,
            }
            
            setSelectedLocation((prev) => {
              if (
                prev &&
                Math.abs(prev.lat - apiLocation.lat) < 0.0001 &&
                Math.abs(prev.lon - apiLocation.lon) < 0.0001 &&
                extractSimpleCityName(prev.name).toLowerCase() === extractSimpleCityName(apiLocation.name).toLowerCase()
              ) {
                console.log('[DASHBOARD] Location unchanged, keeping current selection')
                return prev
              }
              console.log('[DASHBOARD] Updating selectedLocation to match API response:', apiLocation)
              return apiLocation
            })
          }
        } else {
          console.error('[DASHBOARD] API returned error:', data)
          throw new Error(data.message || data.detail || 'Failed to load dashboard data')
        }
      } catch (err: any) {
        // Don't set error if request was cancelled
        if (err.name === 'AbortError' || isCancelled) {
          console.log('[DASHBOARD] Request was cancelled')
          return
        }
        console.error('[DASHBOARD] Fetch error:', err)
        console.error('[DASHBOARD] Error details:', {
          message: err.message,
          stack: err.stack,
          response: err.response
        })
        if (!isCancelled) {
          setError(err.message || 'Failed to load dashboard data. Please try again.')
        }
      } finally {
        if (!isCancelled) {
          setLoading(false)
        }
      }
    }

    fetchDashboardData()
    
    // Cleanup function to cancel request if location changes
    return () => {
      console.log('[DASHBOARD] Cleaning up - cancelling in-flight request')
      isCancelled = true
      abortController.abort()
    }
  }, [selectedLocation?.name, selectedLocation?.lat, selectedLocation?.lon])

  const handleLocationChange = (location: { name: string; lat: number; lon: number }) => {
    console.log('[DASHBOARD] Location changed via LocationSelector:', location)
    // Save to localStorage immediately so it persists across page refreshes
    localStorage.setItem('predict_location', location.name)
    localStorage.setItem('selected_lat', String(location.lat))
    localStorage.setItem('selected_lng', String(location.lon))
    setSelectedLocation(location)
    setDashboardData(null) // Clear old data for smooth transition
    setSelectedDayIndex(0)
  }

  const handleExportPDF = () => {
    if (dashboardData) {
      exportDashboardToPDF(dashboardData, selectedLocation?.name || 'Unknown Location')
    }
  }

  const openChatWith = (tab: 'diagnostic' | 'predictive', question?: string) => {
    setChatTab(tab)
    setInitialChatQuestion(question || '')
    setIsChatOpen(true)
  }

  const todayRisk = useMemo(() => {
    return {
      late: Math.round(selectedRiskEntry?.late_blight_pct || 0),
      early: Math.round(selectedRiskEntry?.early_blight_pct || 0),
      overall: Math.max(
        Math.round(selectedRiskEntry?.late_blight_pct || 0),
        Math.round(selectedRiskEntry?.early_blight_pct || 0)
      ),
    }
  }, [selectedRiskEntry])

  const dashboardContext = useMemo(() => {
    if (!dashboardData) return undefined
    return {
      location: dashboardData.location || selectedLocation?.name,
      day: safeRiskIndex + 1,
      late_blight: todayRisk.late,
      early_blight: todayRisk.early,
      overall: todayRisk.overall,
    }
  }, [dashboardData, selectedLocation, todayRisk, safeRiskIndex])

  const heroStats = useMemo(() => {
    if (!selectedWeatherEntry) return []
    return [
      {
        label: 'Temperature',
        value: `${Math.round(selectedWeatherEntry.temp_avg || 0)}°C`,
        helper: `Range: ${Math.round(selectedWeatherEntry.temp_min || 0)}° - ${Math.round(selectedWeatherEntry.temp_max || 0)}°C`,
      },
      {
        label: 'Humidity',
        value: `${Math.round(selectedWeatherEntry.humidity_avg || 0)}%`,
        helper: 'Average moisture level',
      },
      {
        label: 'Precipitation',
        value: `${Math.round(selectedWeatherEntry.precipitation || 0)} mm`,
        helper: 'Forecasted rainfall',
      },
      {
        label: 'Wind Speed',
        value: `${Math.round(selectedWeatherEntry.wind_speed || 0)} km/h`,
        helper: 'Spore dispersal factor',
      },
      {
        label: 'Soil Moisture',
        value: `${Math.round((selectedSoilEntry?.soil_moisture_percent || 0) * 100)}%`,
        helper: 'Root zone saturation',
      },
      {
        label: 'Cloud Cover',
        value: `${Math.round(selectedWeatherEntry.cloud_cover || 0)}%`,
        helper: 'Radiation potential',
      },
    ]
  }, [selectedWeatherEntry, selectedSoilEntry])

  // Parallax scroll effect for background blobs
  useEffect(() => {
    let raf = 0
    const onScroll = () => {
      if (raf) return
      raf = requestAnimationFrame(() => {
        setScrollY(window.scrollY || window.pageYOffset || 0)
        raf = 0
      })
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (raf) cancelAnimationFrame(raf)
    }
  }, [])

  return (
    <div className="min-h-screen bg-[#0e0e0f] text-[#e8e8e8] relative overflow-hidden">
      {/* Animated background gradient blobs */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div
          className="absolute -top-24 -left-24 w-[420px] h-[420px] bg-gradient-to-br from-rose-600/25 via-fuchsia-500/15 to-cyan-500/20 blur-3xl rounded-full animate-float-slow will-change-transform"
          style={{ transform: `translate3d(0, ${-scrollY * 0.08}px, 0)` }}
        ></div>
        <div
          className="absolute bottom-[-120px] left-1/2 -translate-x-1/2 w-[520px] h-[520px] bg-gradient-to-tr from-emerald-500/15 via-sky-500/20 to-purple-600/15 blur-3xl rounded-full animate-orbit will-change-transform"
          style={{ transform: `translate3d(-50%, ${-scrollY * 0.03}px, 0)` }}
        ></div>
        <div
          className="absolute -right-24 top-1/3 w-[420px] h-[420px] bg-gradient-to-tr from-amber-500/20 via-pink-500/15 to-red-600/20 blur-3xl rounded-full animate-float-slower will-change-transform"
          style={{ transform: `translate3d(0, ${-scrollY * 0.06}px, 0)` }}
        ></div>
      </div>

      {/* Header */}
      <header className="bg-gradient-to-r from-orange-600 via-orange-500 to-yellow-500 shadow-lg border-b border-orange-400/30">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">🥔 Potato Disease Risk & Climate Dashboard</h1>
              <div className="mt-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 border border-white/30 text-white/90 text-xs backdrop-blur-md">
                  <span className="animate-pulse inline-block w-2 h-2 rounded-full bg-lime-300"></span>
                  <span>Diagnostic Agent</span>
                  <span className="text-white/60">on</span>
                  <span className="px-2 py-0.5 rounded bg-black/20 border border-white/20">Predictive</span>
                </div>
              </div>
              {lastUpdated && (
                <p className="text-sm text-white/80 mt-1">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </p>
              )}
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <LocationSelector
                selectedLocation={selectedLocation}
                onLocationChange={handleLocationChange}
              />
              <button
                onClick={() => window.open('/diagnostic-dashboard', '_blank')}
                className="px-4 py-2 bg-black/20 hover:bg-black/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30 text-sm"
                title="Open Diagnostic Agent in new tab"
              >
                🧠 Diagnostic
              </button>
              <button
                onClick={() => window.open('/chat', '_blank')}
                className="px-4 py-2 bg-black/20 hover:bg-black/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30 text-sm"
                title="Open Multi-Agent Chat in new tab"
              >
                💬 Chat
              </button>
              <button
                aria-label="Chat with AI"
                onClick={() => openChatWith('predictive')}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30 text-sm"
              >
                🤖 Ask AI
              </button>
              {dashboardData && (
                <button
                  onClick={handleExportPDF}
                  className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30 text-sm"
                >
                  📄 Export PDF
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        {loading && !dashboardData && (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-[#b8b8b8]">Loading dashboard data...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-6">
            <p className="text-red-400 font-semibold mb-2">⚠️ Error Loading Dashboard</p>
            <p className="text-red-300 text-sm mb-4">{error}</p>
            <button
              onClick={() => selectedLocation && setSelectedLocation({ ...selectedLocation })}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
            >
              🔄 Retry
            </button>
          </div>
        )}

        {!loading && !error && !dashboardData && selectedLocation && (
          <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-6 mb-6 text-center">
            <p className="text-yellow-400 font-semibold mb-2">📊 No Data Available</p>
            <p className="text-yellow-300 text-sm">
              Dashboard data is loading for <strong>{selectedLocation.name}</strong>.
              <br />
              Please wait or try selecting a different location.
            </p>
          </div>
        )}

        {!loading && !error && !dashboardData && !selectedLocation && (
          <div className="flex items-center justify-center min-h-[500px]">
            <div className="text-center max-w-md">
              <div className="text-6xl mb-4">🗺️</div>
              <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4">Select a Location</h2>
              <p className="text-[#b8b8b8] mb-6">
                To view your dashboard, please select a location using the search bar above.
                <br />
                <br />
                You can search for a city or use your current location.
              </p>
              <div className="bg-[#2d2d2d] rounded-lg p-4 border border-[#3a3a3a]">
                <p className="text-sm text-[#b8b8b8]">
                  💡 <strong>Tip:</strong> If you've saved a location before, it should load automatically.
                  <br />
                  If not, use the location selector in the header.
                </p>
              </div>
            </div>
          </div>
        )}

        <AnimatePresence mode="wait">
          {dashboardData && (
            <motion.div
              key={selectedLocation?.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              {/* Hero Overview */}
              <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#141316]/90 via-[#10121b]/95 to-[#09090d]/90 shadow-[0_40px_80px_rgba(0,0,0,0.55)] overflow-hidden">
                <div className="grid gap-6 lg:grid-cols-[1.3fr_0.9fr]">
                  <div className="p-6 lg:p-8">
                    <div className="flex flex-col gap-4">
                      <div>
                        <p className="text-sm uppercase tracking-[0.3em] text-white/50">Active Field</p>
                        <h2 className="text-3xl md:text-4xl font-black text-white mt-1">{selectedLocation?.name}</h2>
                        {selectedRiskEntry?.date && (
                          <p className="text-white/70 text-sm mt-1">
                            {new Date(selectedRiskEntry.date).toLocaleDateString('en-US', {
                              weekday: 'long',
                              month: 'long',
                              day: 'numeric',
                            })}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-4 text-sm text-white/70">
                        <div className="flex items-center gap-1 bg-white/5 px-3 py-1 rounded-full border border-white/10">
                          <span className="text-white/60">LAT</span>
                          <span className="font-semibold">{latDisplay}</span>
                        </div>
                        <div className="flex items-center gap-1 bg-white/5 px-3 py-1 rounded-full border border-white/10">
                          <span className="text-white/60">LON</span>
                          <span className="font-semibold">{lonDisplay}</span>
                        </div>
                        <div className="flex items-center gap-1 bg-white/5 px-3 py-1 rounded-full border border-white/10">
                          <span className="text-white/60">FOCUS DAY</span>
                          <span className="font-semibold">D{safeRiskIndex + 1}</span>
                        </div>
                      </div>
                    </div>
                    {/* Enhanced Crop Stage Information */}
                    {dashboardData?.prediction?.growth_stage && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-6 mb-4 p-6 bg-gradient-to-br from-emerald-500/15 via-teal-500/10 to-cyan-500/15 rounded-xl border border-emerald-500/30 shadow-lg"
                      >
                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-3">
                              <div className="text-5xl">🌱</div>
                              <div>
                                <p className="text-xs uppercase tracking-wider text-emerald-300/80 mb-1 font-semibold">Crop Growth Stage</p>
                                <p className="text-2xl font-bold text-white">{dashboardData.prediction.growth_stage}</p>
                              </div>
                            </div>
                            {dashboardData.prediction.days_after_planting !== undefined && (
                              <div className="flex items-center gap-4 text-sm">
                                <div className="flex items-center gap-2">
                                  <span className="text-emerald-400">📅</span>
                                  <span className="text-white/80">
                                    <strong className="text-white">{dashboardData.prediction.days_after_planting}</strong> days after planting
                                  </span>
                                </div>
                                {dashboardData.prediction.sowing_date && (
                                  <div className="flex items-center gap-2">
                                    <span className="text-emerald-400">🌾</span>
                                    <span className="text-white/70">
                                      Sown: {new Date(dashboardData.prediction.sowing_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                                    </span>
                                  </div>
                                )}
                              </div>
                            )}
                            {/* Stage-specific risk context */}
                            <div className="mt-4 p-3 bg-black/20 rounded-lg border border-emerald-500/20">
                              <p className="text-xs text-emerald-200/90 leading-relaxed">
                                <strong>Stage Impact:</strong> Your crop is in the <strong>{dashboardData.prediction.growth_stage}</strong> stage. 
                                Disease susceptibility varies by growth stage - this information is factored into risk assessments and recommendations.
                              </p>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Sliding Window Methodology Explanation */}
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="mb-6 p-5 bg-gradient-to-br from-purple-500/10 via-indigo-500/10 to-blue-500/10 rounded-xl border border-purple-500/20 shadow-lg"
                    >
                      <div className="flex items-start gap-4">
                        <div className="text-3xl">📊</div>
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                            <span>Sliding Window Risk Calculation</span>
                            <span className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">Advanced Algorithm</span>
                          </h3>
                          <p className="text-sm text-white/80 mb-3 leading-relaxed">
                            Each day's risk is calculated using a <strong className="text-purple-300">7-day sliding window</strong> (3 days before + current day + 3 days after). 
                            This approach provides more stable and context-aware risk assessments by considering weather trends, not just single-day conditions.
                          </p>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
                            <div className="p-3 bg-black/20 rounded-lg border border-purple-500/10">
                              <div className="text-xs text-purple-300 mb-1 font-semibold">Current Day Weight</div>
                              <div className="text-lg font-bold text-white">40%</div>
                              <div className="text-xs text-white/60 mt-1">Primary importance</div>
                            </div>
                            <div className="p-3 bg-black/20 rounded-lg border border-purple-500/10">
                              <div className="text-xs text-purple-300 mb-1 font-semibold">Window Size</div>
                              <div className="text-lg font-bold text-white">7 Days</div>
                              <div className="text-xs text-white/60 mt-1">3 before + current + 3 after</div>
                            </div>
                            <div className="p-3 bg-black/20 rounded-lg border border-purple-500/10">
                              <div className="text-xs text-purple-300 mb-1 font-semibold">Calculation Method</div>
                              <div className="text-lg font-bold text-white">Deterministic</div>
                              <div className="text-xs text-white/60 mt-1">Consistent, reproducible</div>
                            </div>
                          </div>
                          {/* Visual representation of sliding window */}
                          <div className="mt-4 p-4 bg-black/30 rounded-lg border border-purple-500/10">
                            <div className="text-xs text-purple-200 mb-3 font-semibold">How It Works:</div>
                            <div className="flex items-center gap-2 flex-wrap">
                              {dashboardData.date_range && dashboardData.date_range.slice(0, 7).map((date, idx) => {
                                const isCurrent = idx === 3
                                const isInWindow = idx >= 0 && idx <= 6
                                return (
                                  <div
                                    key={idx}
                                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                                      isCurrent
                                        ? 'bg-purple-500/40 border-2 border-purple-400 text-white shadow-lg scale-110'
                                        : isInWindow
                                        ? 'bg-purple-500/20 border border-purple-500/30 text-purple-200'
                                        : 'bg-black/40 border border-white/10 text-white/40'
                                    }`}
                                  >
                                    <div className="text-[10px] opacity-70">{date.split(' ')[0]}</div>
                                    <div className="font-bold">{isCurrent ? 'Today' : idx < 3 ? 'Past' : 'Future'}</div>
                                    {isCurrent && <div className="text-[9px] mt-1 opacity-80">40% weight</div>}
                                  </div>
                                )
                              })}
                            </div>
                            <p className="text-xs text-white/60 mt-3 italic">
                              The highlighted day represents today's risk calculation, which considers weather conditions from the surrounding 7-day window.
                            </p>
                          </div>
                        </div>
                      </div>
                    </motion.div>

                    {/* Enhanced Weather Cards - Larger Rectangles */}
                    <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      {heroStats.map((stat, idx) => {
                        // Get additional details for each stat
                        const getAdditionalDetails = () => {
                          if (!selectedWeatherEntry) return null
                          switch(stat.label) {
                            case 'Temperature':
                              return {
                                feelsLike: selectedWeatherEntry.temp_avg ? Math.round(selectedWeatherEntry.temp_avg) : null,
                                dewPoint: selectedWeatherEntry.dewpoint_2m ? Math.round(selectedWeatherEntry.dewpoint_2m) : null,
                                trend: 'Stable'
                              }
                            case 'Humidity':
                              return {
                                min: selectedWeatherEntry.humidity_min ? Math.round(selectedWeatherEntry.humidity_min) : null,
                                max: selectedWeatherEntry.humidity_max ? Math.round(selectedWeatherEntry.humidity_max) : null,
                                trend: 'Moderate'
                              }
                            case 'Precipitation':
                              return {
                                probability: selectedWeatherEntry.precipitation_probability ? Math.round(selectedWeatherEntry.precipitation_probability) : null,
                                type: selectedWeatherEntry.precipitation_type || 'None',
                                trend: 'Clear'
                              }
                            case 'Wind Speed':
                              return {
                                direction: selectedWeatherEntry.wind_direction_10m ? Math.round(selectedWeatherEntry.wind_direction_10m) : null,
                                gusts: selectedWeatherEntry.wind_gusts_10m ? Math.round(selectedWeatherEntry.wind_gusts_10m) : null,
                                trend: 'Calm'
                              }
                            case 'Soil Moisture':
                              return {
                                status: (selectedSoilEntry?.soil_moisture_percent || 0) < 0.3 ? 'Dry' : (selectedSoilEntry?.soil_moisture_percent || 0) > 0.7 ? 'Wet' : 'Optimal',
                                trend: 'Stable'
                              }
                            case 'Cloud Cover':
                              return {
                                visibility: selectedWeatherEntry.visibility ? Math.round(selectedWeatherEntry.visibility / 1000) : null,
                                uvIndex: selectedWeatherEntry.uv_index ? Math.round(selectedWeatherEntry.uv_index) : null,
                                trend: 'Clear'
                              }
                            default:
                              return null
                          }
                        }
                        const details = getAdditionalDetails()
                        
                        return (
                          <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            whileHover={{ scale: 1.02, y: -4 }}
                            className="rounded-xl border border-white/10 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl px-6 py-6 shadow-lg hover:shadow-xl transition-all duration-300 hover:border-white/20 min-h-[160px] flex flex-col justify-between"
                          >
                            <div>
                              <p className="text-xs uppercase tracking-wider text-white/60 mb-3 font-medium">{stat.label}</p>
                              <p className="text-4xl font-bold text-white mb-3">{stat.value}</p>
                              <p className="text-sm text-white/70 mb-3 leading-relaxed">{stat.helper}</p>
                            </div>
                            {details && (
                              <div className="mt-auto pt-3 border-t border-white/10">
                                <div className="grid grid-cols-2 gap-2 text-xs">
                                  {details.feelsLike && (
                                    <div>
                                      <span className="text-white/50">Feels like:</span>
                                      <span className="text-white/80 ml-1 font-medium">{details.feelsLike}°C</span>
                                    </div>
                                  )}
                                  {details.dewPoint && (
                                    <div>
                                      <span className="text-white/50">Dew point:</span>
                                      <span className="text-white/80 ml-1 font-medium">{details.dewPoint}°C</span>
                                    </div>
                                  )}
                                  {details.min !== null && details.max !== null && (
                                    <>
                                      <div>
                                        <span className="text-white/50">Min:</span>
                                        <span className="text-white/80 ml-1 font-medium">{details.min}%</span>
                                      </div>
                                      <div>
                                        <span className="text-white/50">Max:</span>
                                        <span className="text-white/80 ml-1 font-medium">{details.max}%</span>
                                      </div>
                                    </>
                                  )}
                                  {details.probability !== null && (
                                    <div className="col-span-2">
                                      <span className="text-white/50">Precipitation probability:</span>
                                      <span className="text-white/80 ml-1 font-medium">{details.probability}%</span>
                                    </div>
                                  )}
                                  {details.direction !== null && (
                                    <div>
                                      <span className="text-white/50">Direction:</span>
                                      <span className="text-white/80 ml-1 font-medium">{details.direction}°</span>
                                    </div>
                                  )}
                                  {details.gusts !== null && (
                                    <div>
                                      <span className="text-white/50">Gusts:</span>
                                      <span className="text-white/80 ml-1 font-medium">{details.gusts} km/h</span>
                                    </div>
                                  )}
                                  {details.status && (
                                    <div className="col-span-2">
                                      <span className="text-white/50">Status:</span>
                                      <span className={`ml-1 font-medium ${
                                        details.status === 'Optimal' ? 'text-green-400' : 
                                        details.status === 'Dry' ? 'text-yellow-400' : 'text-blue-400'
                                      }`}>{details.status}</span>
                                    </div>
                                  )}
                                  {details.visibility !== null && (
                                    <div>
                                      <span className="text-white/50">Visibility:</span>
                                      <span className="text-white/80 ml-1 font-medium">{details.visibility} km</span>
                                    </div>
                                  )}
                                  {details.uvIndex !== null && (
                                    <div>
                                      <span className="text-white/50">UV Index:</span>
                                      <span className="text-white/80 ml-1 font-medium">{details.uvIndex}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </motion.div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="relative p-6 lg:p-8 border-t lg:border-l border-white/5 flex flex-col items-center justify-center">
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.08),_transparent_65%)] pointer-events-none"></div>
                    <div className="relative w-48 h-48 md:w-56 md:h-56 rounded-full flex items-center justify-center">
                      <div
                        className="absolute inset-0 rounded-full blur-3xl opacity-70"
                        style={{
                          background: 'conic-gradient(from 90deg, rgba(255,68,68,0.45), rgba(249,115,22,0.25), transparent 70%)',
                        }}
                      ></div>
                      <div
                        className="relative w-full h-full rounded-full border border-white/10 p-3"
                        style={{
                          background:
                            'radial-gradient(circle at 20% 20%, rgba(255,255,255,0.15), rgba(0,0,0,0.35))',
                        }}
                      >
                        <div
                          className="w-full h-full rounded-full flex items-center justify-center relative"
                          style={{
                            background: '#08090c',
                          }}
                        >
                          <div
                            className="absolute inset-0 rounded-full"
                            style={{
                              background: `conic-gradient(#f87171 ${todayRisk.overall}%, rgba(255,255,255,0.08) ${todayRisk.overall}% 100%)`,
                              filter: 'drop-shadow(0 0 24px rgba(248,113,113,0.45))',
                              maskImage: 'radial-gradient(circle, transparent 58%, black 61%)',
                              WebkitMaskImage: 'radial-gradient(circle, transparent 58%, black 61%)',
                            }}
                          ></div>
                          <div className="relative z-10 text-center">
                            {(() => {
                              const highestRisk = Math.max(todayRisk.late, todayRisk.early)
                              const isLateBlightHighest = todayRisk.late >= todayRisk.early
                              const dominantDisease = isLateBlightHighest ? 'Late Blight' : 'Early Blight'
                              const dominantIcon = isLateBlightHighest ? '🔴' : '🟡'
                              
                              return (
                                <>
                                  <p className="text-white/60 text-xs uppercase tracking-[0.3em] mb-1">{dominantDisease} Risk</p>
                                  <p className="text-5xl md:text-6xl font-black text-white">{highestRisk}%</p>
                                  <div className="mt-2 flex items-center justify-center gap-2 text-xs text-white/80">
                                    <span className="text-lg">{dominantIcon}</span>
                                    <span className="font-semibold">{dominantDisease}</span>
                                  </div>
                                  <div className="mt-1 text-[10px] text-white/60">
                                    {isLateBlightHighest 
                                      ? `Early Blight: ${todayRisk.early}%`
                                      : `Late Blight: ${todayRisk.late}%`
                                    }
                                  </div>
                                </>
                              )
                            })()}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="text-center mt-4 space-y-2">
                      <p className="text-white/70 text-sm max-w-xs mx-auto">
                        Blending current weather, soil moisture, and historical outbreaks using a <strong className="text-white">sliding window algorithm</strong> to surface a confident threat posture.
                      </p>
                      {dashboardData?.prediction?.growth_stage && (
                        <p className="text-white/60 text-xs max-w-xs mx-auto">
                          Risk assessment considers your crop's current growth stage: <strong className="text-emerald-300">{dashboardData.prediction.growth_stage}</strong>
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </section>

              {/* Diagnostic Agent Quick Panel */}
              <section className="bg-gradient-to-br from-rose-500/20 via-fuchsia-500/10 to-cyan-500/20 rounded-2xl p-6 border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.35)] backdrop-blur-sm">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                      🧠 Diagnostic Agent
                    </h2>
                    <p className="text-white/80 text-sm mt-1">
                      Analyze leaf images and get symptom-driven diagnosis. Powered by the multi-agent brain.
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => openChatWith('diagnostic', 'I want to diagnose disease symptoms in my field today.')}
                      className="px-4 py-2 rounded-xl bg-white text-black font-semibold hover:bg-gray-100 transition-colors"
                    >
                      Open Diagnostic Chat
                    </button>
                    <button
                      onClick={() => openChatWith('predictive', 'What is the disease risk for my crop today and this week?')}
                      className="px-4 py-2 rounded-xl bg-black/40 text-white border border-white/20 hover:bg-black/60 transition-colors"
                    >
                      Predictive Insights
                    </button>
                  </div>
                </div>
              </section>

              {/* Disease Risk Summary Cards */}
              {dashboardData.disease_risks && dashboardData.disease_risks.length > 0 && (
                <DiseaseRiskSummary
                  lateBlightRisk={todayRisk.late}
                  earlyBlightRisk={todayRisk.early}
                  mlValidation={dashboardData.prediction?.ml_validation}
                  onExplain={(type) => {
                    const label = type === 'late' ? 'Late Blight' : 'Early Blight'
                    const date = selectedWeatherEntry?.date
                    openChatWith('predictive', `Why is ${label} risk ${type === 'late' ? todayRisk.late : todayRisk.early}% on ${date ? new Date(date).toDateString() : 'this day'} at ${selectedLocation?.name}? What factors contributed most and how confident is the model?`)
                  }}
                />
              )}

              {/* Location Assurance Panel (Map-less) */}
              {selectedLocation && (
                <section className="bg-[#151515]/90 rounded-xl p-6 border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.45)] backdrop-blur-md">
                  <div className="flex flex-col xl:flex-row gap-6">
                    <div className="flex-1 space-y-4">
                      <div>
                        <p className="text-sm uppercase tracking-[0.3em] text-white/50 mb-2">Active Field Location</p>
                        <div className="flex flex-wrap items-center gap-3">
                          <h2 className="text-3xl font-bold text-white">{selectedLocation.name}</h2>
                          <span className="px-3 py-1 bg-white/10 text-white/80 text-xs rounded-full border border-white/20">
                            Exact user input
                          </span>
                        </div>
                        <p className="text-white/70 text-sm mt-2 max-w-xl">
                          Every prediction, recommendation, and chart on this dashboard is anchored to the precise location you entered previously. Nothing is auto-corrected, inferred, or substituted.
                        </p>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-[#1f1f1f] rounded-lg p-4 border border-white/5">
                          <div className="text-xs text-white/60 uppercase tracking-[0.2em] mb-1">Latitude</div>
                          <div className="text-2xl font-semibold text-white">{latDisplay}</div>
                        </div>
                        <div className="bg-[#1f1f1f] rounded-lg p-4 border border-white/5">
                          <div className="text-xs text-white/60 uppercase tracking-[0.2em] mb-1">Longitude</div>
                          <div className="text-2xl font-semibold text-white">{lonDisplay}</div>
                        </div>
                      </div>
                      <p className="text-white/60 text-xs">
                        Need to adjust the location? Use the location selector above—then rerun a prediction and the dashboard will instantly lock to the new coordinates without ever showing a map.
                      </p>
                    </div>
                    <div className="flex-1 space-y-4">
                      {/* Show only highest risk disease */}
                      {(() => {
                        const highestRisk = Math.max(todayRisk.late, todayRisk.early)
                        const isLateBlightHighest = todayRisk.late >= todayRisk.early
                        const dominantDisease = isLateBlightHighest ? 'Late Blight' : 'Early Blight'
                        const dominantRisk = isLateBlightHighest ? todayRisk.late : todayRisk.early
                        const dominantColor = isLateBlightHighest ? 'text-red-400' : 'text-yellow-400'
                        const dominantIcon = isLateBlightHighest ? '🔴' : '🟡'
                        
                        return (
                          <>
                            <div className="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] rounded-xl p-6 border-2 border-white/10">
                              <div className="flex items-center justify-between mb-3">
                                <div className="text-sm text-[#b8b8b8] uppercase tracking-wider">Primary Disease Risk</div>
                                <span className="text-2xl">{dominantIcon}</span>
                              </div>
                              <div className={`text-5xl font-black ${dominantColor} mb-2`}>{Math.round(dominantRisk)}%</div>
                              <div className="text-lg font-semibold text-[#e8e8e8] mb-4">{dominantDisease}</div>
                              <div className="text-xs text-[#b8b8b8]">
                                {isLateBlightHighest 
                                  ? `Early Blight: ${Math.round(todayRisk.early)}%`
                                  : `Late Blight: ${Math.round(todayRisk.late)}%`
                                }
                              </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div className="bg-[#1f1f1f] rounded-lg p-4 border border-[#3a3a3a]">
                                <div className="text-xs text-[#b8b8b8] mb-1 uppercase tracking-wider">Temperature</div>
                                <div className="text-xl font-bold text-[#e8e8e8]">{Math.round(selectedWeatherEntry?.temp_avg || 0)}°C</div>
                                <div className="text-xs text-[#808080] mt-1">
                                  {Math.round(selectedWeatherEntry?.temp_min || 0)}° - {Math.round(selectedWeatherEntry?.temp_max || 0)}°C
                                </div>
                              </div>
                              <div className="bg-[#1f1f1f] rounded-lg p-4 border border-[#3a3a3a]">
                                <div className="text-xs text-[#b8b8b8] mb-1 uppercase tracking-wider">Humidity</div>
                                <div className="text-xl font-bold text-[#e8e8e8]">{Math.round(selectedWeatherEntry?.humidity_avg || 0)}%</div>
                              </div>
                              <div className="bg-[#1f1f1f] rounded-lg p-4 border border-[#3a3a3a]">
                                <div className="text-xs text-[#b8b8b8] mb-1 uppercase tracking-wider">Soil Moisture</div>
                                <div className="text-xl font-bold text-[#e8e8e8]">{Math.round((selectedSoilEntry?.soil_moisture_percent || 0) * 100)}%</div>
                              </div>
                            </div>
                            <button
                              onClick={() => {
                                const date = selectedWeatherEntry?.date
                                const dateStr = date ? new Date(date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) : 'today'
                                openChatWith('predictive', `Explain why ${dominantDisease} risk is ${Math.round(dominantRisk)}% on ${dateStr} at ${selectedLocation?.name}. What weather and environmental factors contributed most to this risk level, and how confident is the prediction model?`)
                              }}
                              className="w-full px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-xl font-semibold border border-white/20 transition-all shadow-lg hover:shadow-orange-500/50 flex items-center justify-center gap-2"
                            >
                              <span>🤖</span>
                              <span>Ask AI to Explain {dominantDisease} Risk</span>
                            </button>
                          </>
                        )
                      })()}
                    </div>
                  </div>
                </section>
              )}

              {/* 8-Day Forecast Cards */}
              {dashboardData.weather_data && dashboardData.weather_data.length > 0 && (
                <div>
                  <div className="mb-4 flex items-center justify-between flex-wrap gap-3">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-1">📅 8-Day Forecast</h2>
                      <p className="text-sm text-white/70">
                        Each day's risk is calculated using a <strong className="text-purple-300">sliding window</strong> for context-aware predictions
                      </p>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                      <span className="text-xs text-purple-300">📊</span>
                      <span className="text-xs text-purple-200">7-Day Window Algorithm</span>
                    </div>
                  </div>
                  <ForecastCards
                    weatherData={dashboardData.weather_data}
                    soilData={dashboardData.soil_data || []}
                    diseaseRisks={dashboardData.disease_risks || []}
                    activeIndex={safeRiskIndex}
                    onExplainDay={(payload) => {
                      openChatWith(
                        'predictive',
                        `Explain the risk on ${new Date(payload.date).toDateString()} at ${selectedLocation?.name}. Late: ${payload.risk.late}%, Early: ${payload.risk.early}%. What weather/soil factors drive this and how confident are you?`
                      )
                    }}
                    onHoverDay={(index) => {
                      if (typeof index === 'number') {
                        setSelectedDayIndex(index)
                      }
                    }}
                    onSelectDay={(index) => setSelectedDayIndex(index)}
                  />
                </div>
              )}

              {/* Weather Trends */}
              {dashboardData.weather_data && dashboardData.weather_data.length > 0 && (
                <WeatherTrends
                  weatherData={dashboardData.weather_data}
                />
              )}

              {/* Soil Moisture Visualization */}
              {dashboardData.soil_data && dashboardData.soil_data.length > 0 && (
                <SoilMoistureViz
                  soilData={dashboardData.soil_data}
                />
              )}

              {/* Disease Risk Timeline */}
              {dashboardData.disease_risks && dashboardData.disease_risks.length > 0 && (
                <div>
                  <div className="mb-4 p-3 bg-purple-500/5 border border-purple-500/20 rounded-lg">
                    <p className="text-xs text-purple-300/80 leading-relaxed">
                      <strong className="text-purple-300">💡 Sliding Window Applied:</strong> Each day's risk percentage is calculated using a 7-day window centered on that day. 
                      This ensures each forecast day considers surrounding weather trends for more accurate and stable risk assessments.
                    </p>
                  </div>
                  <DiseaseRiskTimeline
                    diseaseRisks={dashboardData.disease_risks}
                    selectedIndex={safeRiskIndex}
                    onSelectDay={(index) => setSelectedDayIndex(index)}
                  />
                </div>
              )}

              {/* Risk Factor Contributions */}
              {dashboardData.disease_risks && dashboardData.disease_risks.length > 0 && (
                <RiskFactorContributions
                  diseaseRisks={dashboardData.disease_risks}
                  selectedDayIndex={safeRiskIndex}
                />
              )}

              {/* Management Recommendations */}
              {dashboardData.recommendations && (
                <ManagementRecommendations
                  recommendations={dashboardData.recommendations}
                  criticalDays={dashboardData.weekly_outlook?.critical_days || []}
                  lateBlightRisk={todayRisk.late}
                  earlyBlightRisk={todayRisk.early}
                />
              )}

              {/* Weekly Outlook */}
              {dashboardData.weekly_outlook && (
                <WeeklyOutlook
                  outlook={dashboardData.weekly_outlook}
                  onExplain={() => openChatWith('predictive', `Explain the weekly outlook for ${selectedLocation?.name}. Why are these days marked critical: ${dashboardData.weekly_outlook.critical_days?.join(', ')}?`)}
                />
              )}

              {/* Historical Context */}
              {dashboardData.historical_outbreaks && dashboardData.historical_outbreaks.length > 0 && (
                <HistoricalContext
                  historicalOutbreaks={dashboardData.historical_outbreaks}
                  currentWeather={dashboardData.weather_data?.[0]}
                  location={selectedLocation?.name || ''}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Floating Chat Drawer */}
      <AnimatePresence>
        {isChatOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50"
            aria-modal="true"
            role="dialog"
          >
            <div className="absolute top-0 right-0 h-full w-full max-w-xl bg-[#1f1f1f] border-l border-[#3a3a3a] shadow-2xl flex flex-col">
              <div className="p-4 border-b border-[#3a3a3a] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setChatTab('diagnostic')}
                    className={`px-3 py-2 rounded-lg text-sm ${chatTab === 'diagnostic' ? 'bg-orange-500 text-white' : 'bg-[#2a2a2a] text-[#e8e8e8]'}`}
                    aria-pressed={chatTab === 'diagnostic'}
                  >
                    🧠 Diagnostic
                  </button>
                  <button
                    onClick={() => setChatTab('predictive')}
                    className={`px-3 py-2 rounded-lg text-sm ${chatTab === 'predictive' ? 'bg-orange-500 text-white' : 'bg-[#2a2a2a] text-[#e8e8e8]'}`}
                    aria-pressed={chatTab === 'predictive'}
                  >
                    📊 Predictive
                  </button>
                </div>
                <button
                  onClick={() => setIsChatOpen(false)}
                  aria-label="Close chat"
                  className="text-[#b8b8b8] hover:text-[#e8e8e8]"
                >
                  ✖
                </button>
              </div>
              <div className="flex-1 p-4">
                <DashboardChatAssistant
                  dashboardContext={dashboardContext}
                  conversationId={undefined}
                  mode={chatTab}
                  initialQuestion={initialChatQuestion}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Animated style helpers */}
      <style jsx global>{`
        @keyframes float-slow { 
          0%, 100% { transform: translateY(0px); } 
          50% { transform: translateY(-20px); } 
        }
        .animate-float-slow { animation: float-slow 10s ease-in-out infinite; }
        @keyframes float-slower { 
          0%, 100% { transform: translateY(0px) scale(1); } 
          50% { transform: translateY(18px) scale(1.05); } 
        }
        .animate-float-slower { animation: float-slower 14s ease-in-out infinite; }
        @keyframes orbit {
          0% { transform: translate(-50%, 0) rotate(0deg); }
          50% { transform: translate(-50%, -10px) rotate(180deg); }
          100% { transform: translate(-50%, 0) rotate(360deg); }
        }
        .animate-orbit { animation: orbit 36s linear infinite; }
        @keyframes spin-slower { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .animate-spin-slower { animation: spin-slower 18s linear infinite; }
      `}</style>
    </div>
  )
}

