'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { authAPI, getApiBaseUrl } from '@/lib/api'

interface LocationSelectorProps {
  selectedLocation: { name: string; lat: number; lon: number } | null
  onLocationChange: (location: { name: string; lat: number; lon: number }) => void
}

export default function LocationSelector({ selectedLocation, onLocationChange }: LocationSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loading, setLoading] = useState(false)
  const [manualError, setManualError] = useState<string | null>(null)
  const searchRef = useRef<HTMLInputElement>(null)
  const debounceTimer = useRef<NodeJS.Timeout>()

  const persistLocationSelection = async (name: string, lat: number, lon: number) => {
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem('predict_location', name)
        localStorage.setItem('selected_lat', String(lat))
        localStorage.setItem('selected_lng', String(lon))
      }
    } catch (storageErr) {
      console.warn('Failed to cache location locally:', storageErr)
    }

    try {
      await authAPI.updateFieldData({
        location: name,
        latitude: lat,
        longitude: lon,
      })
    } catch (err) {
      console.warn('Field update failed:', err)
    }
  }

  // CRITICAL FIX: Only update search query when selectedLocation changes externally (from parent)
  // This prevents overwriting user's typed input with geocoded results
  const prevSelectedLocationRef = useRef<{name: string; lat: number; lon: number} | null>(null)
  const isUserTypingRef = useRef(false)
  
  useEffect(() => {
    // Check if selectedLocation actually changed (not just a re-render)
    const locationChanged = 
      !prevSelectedLocationRef.current ||
      prevSelectedLocationRef.current.name !== selectedLocation?.name ||
      prevSelectedLocationRef.current.lat !== selectedLocation?.lat ||
      prevSelectedLocationRef.current.lon !== selectedLocation?.lon
    
    if (selectedLocation && locationChanged && !isUserTypingRef.current) {
      // Only update if user is not actively typing
      setSearchQuery(selectedLocation.name)
      prevSelectedLocationRef.current = { ...selectedLocation }
      console.log('[LOCATION SELECTOR] Updated input from external location change:', selectedLocation.name)
    }
  }, [selectedLocation?.name, selectedLocation?.lat, selectedLocation?.lon])
  
  // Track when user is typing
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchQuery(value)
    setManualError(null)
    isUserTypingRef.current = true
    
    // Clear existing timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }
    
    // Set flag to false after user stops typing (1 second)
    setTimeout(() => {
      isUserTypingRef.current = false
    }, 1000)
    
    // Debounce suggestions fetch
    debounceTimer.current = setTimeout(() => {
      fetchSuggestions(value)
    }, 300)
  }

  const fetchSuggestions = async (query: string) => {
    if (query.length < 3) {
      setSuggestions([])
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=5`)
      const data = await response.json()
      
      if (data.results) {
        setSuggestions(data.results)
        setShowSuggestions(true)
      } else {
        setSuggestions([])
      }
    } catch (error) {
      console.error('Location search error:', error)
      setSuggestions([])
    } finally {
      setLoading(false)
    }
  }

  // handleSearchChange is defined above (line 67)

  const applyLocationSelection = (params: {
    name: string
    latitude: number
    longitude: number
    admin1?: string
    country?: string
  }) => {
    const location = {
      name: params.name,
      lat: params.latitude,
      lon: params.longitude,
    }

    console.log('[LOCATION SELECTOR] Applying location:', location)
    setManualError(null)
    onLocationChange(location)

    const displayName = `${params.name}${params.admin1 ? `, ${params.admin1}` : ''}${params.country ? `, ${params.country}` : ''}`
    setSearchQuery(displayName)
    setShowSuggestions(false)
    setSuggestions([])

    void persistLocationSelection(location.name, location.lat, location.lon)
  }

  const handleSelectLocation = async (suggestion: any) => {
    applyLocationSelection({
      name: suggestion.name,
      latitude: suggestion.latitude,
      longitude: suggestion.longitude,
      admin1: suggestion.admin1,
      country: suggestion.country,
    })
  }

  const geocodeManualLocation = async (query: string) => {
    const trimmed = query.trim()
    if (!trimmed) {
      setManualError('Enter a location name to search')
      return
    }

    try {
      setLoading(true)
      setManualError(null)
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      const response = await fetch(
        `${getApiBaseUrl()}/api/geocode?query=${encodeURIComponent(trimmed)}`,
        {
          headers: {
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      )

      if (!response.ok) {
        throw new Error(`Geocoding failed (${response.status})`)
      }

      const data = await response.json()
      if (data.success && data.location) {
        // CRITICAL: Verify the returned location matches what user typed
        const returnedName = data.location.name || ''
        const userInput = trimmed.toLowerCase()
        const returnedNameLower = returnedName.toLowerCase()
        
        // Check if returned location is similar to user input (allow for minor differences)
        const isSimilar = returnedNameLower.includes(userInput) || userInput.includes(returnedNameLower.split(',')[0])
        
        if (!isSimilar && !returnedNameLower.includes(userInput.split(',')[0])) {
          console.warn('[LOCATION SELECTOR] Geocode returned different location:', {
            userInput: trimmed,
            returned: returnedName
          })
          // Still use it, but log the mismatch
        }
        
        console.log('[LOCATION SELECTOR] Geocode successful:', {
          userInput: trimmed,
          returned: returnedName,
          coordinates: [data.location.latitude, data.location.longitude]
        })
        
        applyLocationSelection({
          name: data.location.name,
          latitude: data.location.latitude,
          longitude: data.location.longitude,
          admin1: data.location.admin1,
          country: data.location.country,
        })
      } else {
        // CRITICAL: If geocoding fails, DO NOT use any default location
        const errorMsg = data.error || 'Could not find that location. Please try a different spelling.'
        console.error('[LOCATION SELECTOR] Geocoding failed:', {
          userInput: trimmed,
          error: errorMsg,
          response: data
        })
        setManualError(errorMsg)
        // DO NOT call onLocationChange with any default - let user try again
      }
    } catch (err: any) {
      console.error('[LOCATION SELECTOR] Manual geocode error:', err)
      setManualError(err.message || 'Failed to lookup that location.')
    } finally {
      setLoading(false)
    }
  }

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (suggestions.length > 0) {
        handleSelectLocation(suggestions[0])
      } else {
        void geocodeManualLocation(searchQuery)
      }
    }
  }

  const handleUseCurrentLocation = () => {
    if (navigator.geolocation) {
      setLoading(true)
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords
          try {
            const response = await fetch(`https://geocoding-api.open-meteo.com/v1/reverse?latitude=${latitude}&longitude=${longitude}`)
            const data = await response.json()
            
            if (data.results && data.results[0]) {
              const result = data.results[0]
              handleSelectLocation({
                ...result,
                latitude,
                longitude
              })
            } else {
              onLocationChange({
                name: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`,
                lat: latitude,
                lon: longitude
              })
            }
          } catch (error) {
            console.error('Reverse geocoding error:', error)
            onLocationChange({
              name: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`,
              lat: latitude,
              lon: longitude
            })
          } finally {
            setLoading(false)
          }
        },
        (error) => {
          console.error('Geolocation error:', error)
          setLoading(false)
        }
      )
    }
  }

  return (
    <div className="relative" ref={searchRef}>
      <div className="flex items-center gap-2">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            onFocus={() => setShowSuggestions(true)}
            onKeyDown={handleSearchKeyDown}
            placeholder="Search location..."
            className="px-4 py-2 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-orange-400 w-64"
            aria-label="Location search"
          />
          {loading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            </div>
          )}
        </div>
        <button
          onClick={handleUseCurrentLocation}
          className="px-3 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/30 rounded-lg text-white transition-colors"
          aria-label="Use current location"
          title="Use current location"
        >
          📍
        </button>
        <button
          onClick={() => void geocodeManualLocation(searchQuery)}
          className="px-3 py-2 bg-black/30 hover:bg-black/40 text-white rounded-lg border border-white/20 transition-colors"
        >
          Apply
        </button>
      </div>
      {manualError && (
        <p className="text-xs text-red-300 mt-2">{manualError}</p>
      )}

      <AnimatePresence>
        {showSuggestions && suggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full mt-2 w-64 bg-[#2d2d2d] border border-[#3a3a3a] rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto"
          >
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSelectLocation(suggestion)}
                className="w-full px-4 py-3 text-left hover:bg-[#3a3a3a] transition-colors border-b border-[#3a3a3a] last:border-b-0"
              >
                <div className="font-medium text-[#e8e8e8]">
                  {suggestion.name}
                </div>
                <div className="text-sm text-[#b8b8b8]">
                  {suggestion.admin1 && `${suggestion.admin1}, `}{suggestion.country}
                </div>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

