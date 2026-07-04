'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { fieldAPI, authAPI } from '@/lib/api'
import { getCurrentLocation, isGeolocationAvailable, LocationResult } from '@/lib/geolocation'
import PotatoAnimation from '@/components/PotatoAnimation'

export default function SetupFieldPage() {
  const [location, setLocation] = useState('')
  const [sowingDate, setSowingDate] = useState('')
  const [areaHectares, setAreaHectares] = useState('')
  const [error, setError] = useState('')
  const [locationError, setLocationError] = useState('')
  const [loading, setLoading] = useState(false)
  const [locationLoading, setLocationLoading] = useState(false)
  const [locationStatus, setLocationStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [checkingAuth, setCheckingAuth] = useState(true)
  const router = useRouter()
  const locationAttempted = useRef(false)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userResponse = await authAPI.getCurrentUser()
        if (userResponse.success && userResponse.user.fields?.length > 0) {
          const field = userResponse.user.fields[0]
          // Only redirect to chat if BOTH location and sowing_date are complete
          if (field.location && field.sowing_date) {
            router.push('/chat')
            return
          }
          // Fields exist but incomplete - stay on setup page to complete them
        }
        setCheckingAuth(false)
      } catch {
        router.push('/login')
        return
      }
    }
    checkAuth()
  }, [router])

  // Auto-detect location on page load (only once)
  useEffect(() => {
    if (!checkingAuth && !locationAttempted.current && isGeolocationAvailable() && !location) {
      locationAttempted.current = true
      handleGetLocation(true)
    }
  }, [checkingAuth, location])

  const handleGetLocation = async (silent = false) => {
    if (!isGeolocationAvailable()) {
      setLocationError('Geolocation is not supported by your browser')
      setLocationStatus('error')
      return
    }

    setLocationLoading(true)
    setLocationStatus('loading')
    setLocationError('')

    try {
      const result: LocationResult = await getCurrentLocation()

      if (result.success && result.location) {
        setLocation(result.location)
        setLocationStatus('success')
        setLocationError('')
        
        // Clear success indicator after 3 seconds
        setTimeout(() => {
          setLocationStatus('idle')
        }, 3000)
      } else {
        setLocationError(result.error || 'Failed to get location')
        setLocationStatus('error')
      }
    } catch (err: any) {
      setLocationError(err.message || 'An error occurred while getting location')
      setLocationStatus('error')
    } finally {
      setLocationLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLocationError('')

    if (!location.trim()) {
      setError('Location is required')
      return
    }

    if (!sowingDate) {
      setError('Sowing date is required')
      return
    }

    setLoading(true)

    try {
      const response = await fieldAPI.create(
        location.trim(),
        sowingDate,
        areaHectares ? parseFloat(areaHectares) : undefined
      )
      if (response.success) {
        // Successfully saved, now navigate to chat
        router.push('/chat')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create field')
    } finally {
      setLoading(false)
    }
  }

  const today = new Date().toISOString().split('T')[0]

  if (checkingAuth) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{
          background: 'linear-gradient(180deg, #FFE5D4 0%, #FFD4B3 50%, #FFC996 100%)',
        }}
      >
        <div className="text-xl font-medium text-gray-900" style={{ fontFamily: 'system-ui, sans-serif' }}>Loading...</div>
      </div>
    )
  }

  return (
    <div 
      className="min-h-screen flex"
      style={{
        background: 'linear-gradient(180deg, #FFE5D4 0%, #FFD4B3 50%, #FFC996 100%)',
      }}
    >
      {/* Left side - Animation */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 z-0">
          <PotatoAnimation />
        </div>
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/20 to-transparent z-10" />
        <div className="relative z-20 flex items-center justify-center w-full">
          <div className="text-center px-8">
            <h1 className="text-5xl font-bold mb-4 text-gray-900" style={{ fontFamily: 'system-ui, sans-serif' }}>
              Setup Field
            </h1>
            <p className="text-lg text-gray-700" style={{ fontFamily: 'system-ui, sans-serif' }}>
              Configure Your Potato Field
            </p>
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white/40 backdrop-blur-sm">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2 text-gray-900" style={{ fontFamily: 'system-ui, sans-serif' }}>
              Field Information
            </h2>
            <p className="text-gray-700" style={{ fontFamily: 'system-ui, sans-serif' }}>
              Provide your field details
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  Location <span className="text-red-500">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => handleGetLocation(false)}
                  disabled={locationLoading}
                  className="px-3 py-1.5 text-xs bg-white border-2 border-gray-300 text-gray-900 rounded-full hover:border-gray-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed smooth-transition font-medium"
                  style={{ fontFamily: 'system-ui, sans-serif' }}
                >
                  {locationLoading ? (
                    <span className="flex items-center gap-1">
                      <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Getting...
                    </span>
                  ) : (
                    'Get Location'
                  )}
                </button>
              </div>
              
              <div className="relative">
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  required
                  className={`w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 rounded-full focus:outline-none text-gray-900 placeholder-gray-400 smooth-transition ${
                    locationStatus === 'success'
                      ? 'border-green-500'
                      : locationStatus === 'error'
                      ? 'border-red-500'
                      : 'border-gray-300 focus:border-gray-900'
                  }`}
                  placeholder="City, State or Coordinates"
                  style={{ fontFamily: 'system-ui, sans-serif' }}
                />
                {locationStatus === 'success' && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </div>

              {locationError && (
                <div className="mt-2 p-2 bg-red-50 border border-red-300 rounded-lg text-red-700 text-xs">
                  {locationError}
                </div>
              )}

              {locationStatus === 'success' && !locationError && (
                <div className="mt-2 p-2 bg-green-50 border border-green-300 rounded-lg text-green-700 text-xs">
                  Location detected successfully
                </div>
              )}

              <p className="mt-1 text-gray-600 text-xs" style={{ fontFamily: 'system-ui, sans-serif' }}>
                Enter city name, state, or GPS coordinates
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-800 mb-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                Sowing Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={sowingDate}
                onChange={(e) => setSowingDate(e.target.value)}
                required
                max={today}
                className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-300 rounded-full focus:outline-none focus:border-gray-900 text-gray-900 smooth-transition"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-800 mb-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                Area (Hectares)
              </label>
              <input
                type="number"
                value={areaHectares}
                onChange={(e) => setAreaHectares(e.target.value)}
                min="0"
                step="0.1"
                className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-300 rounded-full focus:outline-none focus:border-gray-900 text-gray-900 placeholder-gray-400 smooth-transition"
                placeholder="Optional"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              />
              <p className="mt-1 text-gray-600 text-xs" style={{ fontFamily: 'system-ui, sans-serif' }}>
                Optional field
              </p>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-300 rounded-lg text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || locationLoading}
              className="w-full py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed smooth-transition shadow-lg"
              style={{ fontFamily: 'system-ui, sans-serif' }}
            >
              {loading ? 'Saving...' : 'Continue to Chat'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
