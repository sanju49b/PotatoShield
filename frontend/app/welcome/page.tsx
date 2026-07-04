'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { authAPI } from '@/lib/api'
import { motion } from 'framer-motion'

export default function WelcomePage() {
  const router = useRouter()
  const [location, setLocation] = useState('')
  const [dos, setDos] = useState('')
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [gettingLocation, setGettingLocation] = useState(false)
  const [checkingExisting, setCheckingExisting] = useState(true)
  const debounceTimer = useRef<NodeJS.Timeout>()

  // Load existing field data if available (but still ask user to confirm/update)
  useEffect(() => {
    const loadExistingData = async () => {
      try {
        const response = await authAPI.getCurrentUser()
        if (response.success && response.user.fields?.length > 0) {
          const sortedFields = [...response.user.fields].sort((a: any, b: any) => {
            const aDate = new Date(a.updated_at || a.created_at || 0).getTime()
            const bDate = new Date(b.updated_at || b.created_at || 0).getTime()
            return bDate - aDate
          })
          const field = sortedFields[0]
          if (field.location) {
            setLocation(field.location)
            // Store coordinates if available
            if (field.latitude && field.longitude) {
              localStorage.setItem('selected_lat', field.latitude.toString())
              localStorage.setItem('selected_lng', field.longitude.toString())
            }
          }
          if (field.sowing_date) {
            setDos(field.sowing_date)
          }
        }
      } catch (error) {
        console.error('Error loading existing data:', error)
      } finally {
        setCheckingExisting(false)
      }
    }
    loadExistingData()
  }, [])

  // Fetch location suggestions
  const fetchLocationSuggestions = async (query: string) => {
    if (!query || query.length < 3) {
      setSuggestions([])
      return
    }

    try {
      const response = await fetch(
        `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=5&language=en&format=json`
      )
      const data = await response.json()
      
      if (data.results) {
        setSuggestions(data.results)
      } else {
        setSuggestions([])
      }
    } catch (error) {
      console.error('Error fetching location suggestions:', error)
      setSuggestions([])
    }
  }

  // Debounced location search
  const handleLocationChange = (value: string) => {
    setLocation(value)
    
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }

    debounceTimer.current = setTimeout(() => {
      fetchLocationSuggestions(value)
    }, 300)
  }

  // Select location from suggestions
  const selectLocation = (result: any) => {
    // Use just the simple city name for API compatibility
    // The exact location name the user sees is what will be used in all predictions
    setLocation(result.name) // Just "London", not "London, England, United Kingdom"
    setSuggestions([])
    // Store coordinates for later use
    if (result.latitude && result.longitude) {
      localStorage.setItem('selected_lat', result.latitude.toString())
      localStorage.setItem('selected_lng', result.longitude.toString())
    }
  }

  // Get device location
  const handleGetDeviceLocation = () => {
    setGettingLocation(true)
    
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser')
      setGettingLocation(false)
      return
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords
        
        // Store coordinates
        localStorage.setItem('selected_lat', latitude.toString())
        localStorage.setItem('selected_lng', longitude.toString())
        
        // Reverse geocode to get location name
        try {
          const response = await fetch(
            `https://geocoding-api.open-meteo.com/v1/search?latitude=${latitude}&longitude=${longitude}&count=1&language=en&format=json`
          )
          const data = await response.json()
          
          if (data.results && data.results[0]) {
            const result = data.results[0]
            const fullLocation = result.admin1 
              ? `${result.name}, ${result.admin1}, ${result.country}`
              : `${result.name}, ${result.country}`
            setLocation(fullLocation)
          } else {
            setLocation(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`)
          }
        } catch (error) {
          console.error('Error reverse geocoding:', error)
          setLocation(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`)
        }
        
        setGettingLocation(false)
      },
      (error) => {
        console.error('Error getting location:', error)
        alert('Unable to get your location. Please enter it manually.')
        setGettingLocation(false)
      }
    )
  }

  // Save field and start prediction
  const handlePredictAgent = async () => {
    if (!location || !dos) {
      alert('Please enter both location and sowing date')
      return
    }

    setLoading(true)

    try {
      // Get coordinates if available
      const lat = localStorage.getItem('selected_lat')
      const lng = localStorage.getItem('selected_lng')
      
      // Save field data with coordinates
      const fieldData: any = {
        location,
        sowing_date: dos,
        area_hectares: 1.0
      }
      
      if (lat && lng) {
        fieldData.latitude = parseFloat(lat)
        fieldData.longitude = parseFloat(lng)
      }

      const response = await authAPI.updateFieldData(fieldData)

      if (response.success) {
        console.log('[WELCOME] Field saved successfully:', response)
        
        // Store flag to auto-trigger prediction
        localStorage.setItem('auto_predict', 'true')
        localStorage.setItem('predict_location', location)
        localStorage.setItem('predict_dos', dos)
        
        // Keep coordinates in localStorage - dashboard will clear them after using
        // This ensures dashboard can use them even if profile hasn't updated yet
        
        // Small delay to ensure data is saved
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Redirect to production dashboard (it will auto-trigger prediction)
        router.push('/production-dashboard')
      } else {
        console.error('[WELCOME] Failed to save field:', response)
        alert(`Failed to save field data: ${response.message || 'Unknown error'}. Please try again.`)
        setLoading(false)
      }
    } catch (error: any) {
      console.error('[WELCOME] Error saving field:', error)
      alert(`An error occurred: ${error.message || 'Unknown error'}. Please try again.`)
      setLoading(false)
    }
  }

  // Continue to chat without prediction
  const handleContinueToChat = () => {
    router.push('/chat')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#2d2d2d] to-[#1a1a1a] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl w-full"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🥔</div>
          <h1 className="text-4xl font-bold text-[#e8e8e8] mb-2">
            Welcome to Potato Shield
          </h1>
          <p className="text-[#b8b8b8]">
            Get started by configuring your field information to enable accurate disease risk predictions
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-[#2d2d2d] rounded-2xl p-8 border border-[#3a3a3a] shadow-2xl">
          {/* Location Input */}
          <div className="mb-6">
            <label className="block text-[#e8e8e8] font-medium mb-2">
              📍 Field Location
            </label>
            <div className="relative">
              <input
                type="text"
                value={location}
                onChange={(e) => handleLocationChange(e.target.value)}
                placeholder="Enter a city name..."
                className="w-full px-4 py-3 bg-[#3a3a3a] border border-[#4a4a4a] rounded-lg focus:outline-none focus:border-orange-500 text-[#e8e8e8] placeholder-[#808080]"
              />
              
              {/* Suggestions Dropdown */}
              {suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-2 bg-[#3a3a3a] border border-[#4a4a4a] rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {suggestions.map((result, idx) => (
                    <button
                      key={idx}
                      onClick={() => selectLocation(result)}
                      className="w-full px-4 py-3 text-left hover:bg-[#4a4a4a] transition-colors text-[#e8e8e8] border-b border-[#4a4a4a] last:border-b-0"
                    >
                      <div className="font-medium">{result.name}</div>
                      <div className="text-xs text-[#b8b8b8]">
                        {result.admin1 && `${result.admin1}, `}{result.country}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <button
              onClick={handleGetDeviceLocation}
              disabled={gettingLocation}
              className="mt-3 text-sm text-orange-400 hover:text-orange-300 transition-colors flex items-center gap-2"
            >
              {gettingLocation ? (
                <>
                  <div className="w-4 h-4 border-2 border-orange-400 border-t-transparent rounded-full animate-spin"></div>
                  Getting your location...
                </>
              ) : (
                <>
                  📱 Use device location
                </>
              )}
            </button>
          </div>

          {/* Date of Sowing Input */}
          <div className="mb-8">
            <label className="block text-[#e8e8e8] font-medium mb-2">
              🌱 Date of Sowing
            </label>
            <input
              type="date"
              value={dos}
              onChange={(e) => setDos(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-3 bg-[#3a3a3a] border border-[#4a4a4a] rounded-lg focus:outline-none focus:border-orange-500 text-[#e8e8e8]"
            />
            <p className="mt-2 text-xs text-[#808080]">
              When did you plant your potato crop?
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            {/* Quick Navigation Note */}
            <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <p className="text-xs text-blue-300 text-center">
                💡 <strong>Tip:</strong> You can access any agent directly. All agents work independently and can be used in separate browser tabs simultaneously.
              </p>
            </div>

            {/* Diagnostic Agent Button */}
            <motion.button
              onClick={() => router.push('/diagnostic-dashboard')}
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full px-6 py-5 bg-blue-600 text-white rounded-xl font-semibold text-lg hover:bg-blue-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-start gap-2 border border-blue-500/30"
            >
              <div className="flex items-center gap-3 w-full">
                <span className="text-2xl">🧠</span>
                <div className="flex-1 text-left">
                  <div className="font-bold">Diagnostic Agent</div>
                  <div className="text-sm font-normal opacity-90">Upload leaf images to receive instant disease identification and treatment recommendations. No location required.</div>
                </div>
              </div>
            </motion.button>

            {/* Multi-Agent Chat Button */}
            <motion.button
              onClick={handleContinueToChat}
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full px-6 py-5 bg-gray-600 text-white rounded-xl font-medium hover:bg-gray-700 transition-colors border border-gray-500/30 flex flex-col items-start gap-2"
            >
              <div className="flex items-center gap-3 w-full">
                <span className="text-2xl">💬</span>
                <div className="flex-1 text-left">
                  <div className="font-semibold">Multi-Agent Chat Framework</div>
                  <div className="text-sm font-normal opacity-90">Engage with our intelligent system that automatically routes your queries to the most appropriate agent: diagnostic, predictive, or general assistance. No location required.</div>
                </div>
              </div>
            </motion.button>

            {/* Prediction Agent Button */}
            <motion.button
              onClick={handlePredictAgent}
              disabled={loading || !location || !dos}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full px-6 py-5 bg-orange-500 text-white rounded-xl font-semibold text-lg hover:bg-orange-600 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-start gap-2 border border-orange-400/30"
            >
              {loading ? (
                <div className="flex items-center gap-3 w-full">
                  <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                  <div className="flex-1 text-left">
                    <div className="font-bold">Building Your Dashboard...</div>
                    <div className="text-sm font-normal opacity-90">Analyzing weather patterns and calculating risks</div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 w-full">
                  <span className="text-2xl">🚀</span>
                <div className="flex-1 text-left">
                  <div className="font-bold">Prediction Agent</div>
                  <div className="text-sm font-normal opacity-90">Access weather-based forecasting and comprehensive disease risk assessment through an interactive dashboard. Requires location and sowing date above.</div>
                </div>
                </div>
              )}
            </motion.button>
          </div>

          {/* Help Text */}
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-300">
              💡 <strong>Tip:</strong> The Prediction Agent analyzes weather patterns, 
              calculates disease risks, and generates a personalized dashboard tailored to your field's specific conditions.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-[#808080]">
          Powered by AI-driven crop health monitoring
        </div>
      </motion.div>
    </div>
  )
}

