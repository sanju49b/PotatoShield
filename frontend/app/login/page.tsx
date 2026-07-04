'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { authAPI, getApiBaseUrl, setApiBaseUrl, clearApiBaseUrlOverride } from '@/lib/api'

const DEFAULT_BUILD_API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const LOCAL_API = 'http://localhost:8000'

type BackendChoice = 'default' | 'local' | 'custom'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [otp, setOtp] = useState('')
  const [mode, setMode] = useState<'login' | 'register' | 'verify'>('login')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [otpSent, setOtpSent] = useState(false)
  const [displayOtp, setDisplayOtp] = useState<string | null>(null)
  const [backendChoice, setBackendChoice] = useState<BackendChoice>('default')
  const [customApiUrl, setCustomApiUrl] = useState('')
  const [showBackendPicker, setShowBackendPicker] = useState(false)
  const [displayApiUrl, setDisplayApiUrl] = useState(DEFAULT_BUILD_API)
  const router = useRouter()

  // Sync backend choice from localStorage on mount and keep display URL updated
  useEffect(() => {
    const current = getApiBaseUrl()
    setDisplayApiUrl(current)
    if (current === DEFAULT_BUILD_API) setBackendChoice('default')
    else if (current === LOCAL_API) setBackendChoice('local')
    else {
      setBackendChoice('custom')
      setCustomApiUrl(current)
    }
  }, [])

  const applyBackend = (choice: BackendChoice, custom?: string) => {
    if (choice === 'default') {
      clearApiBaseUrlOverride()
      setDisplayApiUrl(DEFAULT_BUILD_API)
    } else if (choice === 'local') {
      setApiBaseUrl(LOCAL_API)
      setDisplayApiUrl(LOCAL_API)
    } else {
      const url = (custom ?? customApiUrl).trim()
      if (url) {
        setApiBaseUrl(url)
        setDisplayApiUrl(url)
      }
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (!email.trim()) {
      setError('Email is required')
      setLoading(false)
      return
    }

    if (!password) {
      setError('Password is required')
      setLoading(false)
      return
    }

    try {
      const response = await authAPI.login(email.trim().toLowerCase(), password)
      if (response.success) {
        // Check if user has existing field data
        try {
          const userResponse = await authAPI.getCurrentUser()
          if (userResponse.success && userResponse.user.fields?.length > 0) {
            const field = userResponse.user.fields[0]
            // If user has complete field data, go to welcome (they can choose any agent)
            // Otherwise, go to welcome to set up field
            router.push('/welcome')
          } else {
            // No fields - go to welcome to set up
            router.push('/welcome')
          }
        } catch {
          // If we can't check, go to welcome anyway
          router.push('/welcome')
        }
      }
    } catch (err: any) {
      // Better error handling
      if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
        setError('Cannot connect to server. Make sure the backend API is running on http://localhost:8000')
      } else if (err.response?.status === 401) {
        setError('Invalid email or password. Please check your credentials.')
      } else if (err.response?.status === 403 && err.response?.data?.detail?.includes('not verified')) {
        // Email not verified - show OTP verification
        setError('')
        setSuccess('Email not verified. Sending OTP...')
        setMode('verify')
        setOtpSent(true)
        // Resend OTP and capture the response
        try {
          const otpResponse = await authAPI.sendOTP(email.trim().toLowerCase())
          if (otpResponse.otp) {
            setDisplayOtp(otpResponse.otp)
            setSuccess('Email not verified. Please use the OTP code shown above.')
          } else {
            setSuccess('Email not verified. Please check your email for the OTP code.')
          }
        } catch (otpErr) {
          console.error('Failed to resend OTP:', otpErr)
          setSuccess('Email not verified. Please use resend OTP button.')
        }
      } else if (err.response?.status === 404) {
        setError('User not found. Please register first.')
      } else {
        setError(err.response?.data?.detail || err.message || 'Login failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    if (!email.trim()) {
      setError('Email is required')
      return
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)

    try {
      const response = await authAPI.register(email.trim().toLowerCase(), password)
      if (response.success) {
        // Check if verification is required
        if (response.requires_verification) {
          // Check if OTP is in response (email failed to send - likely sandbox mode)
          if (response.otp) {
            setDisplayOtp(response.otp)
            setSuccess('Registration successful! Please verify your email.')
          } else {
            setDisplayOtp(null)
            setSuccess('Registration successful! OTP sent to your email. Please verify to continue.')
          }
          setMode('verify')
          setOtpSent(true)
          setError('')
        } else {
          // Auto-login after registration (if no verification needed)
          try {
            const loginResponse = await authAPI.login(email.trim().toLowerCase(), password)
            if (loginResponse.success) {
              router.push('/setup-field')
            }
          } catch (loginErr: any) {
            setError(loginErr.response?.data?.detail || 'Registration successful but login failed. Please try logging in.')
          }
        }
      }
    } catch (err: any) {
      // Better error handling
      if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
        setError('Cannot connect to server. Make sure the backend API is running on http://localhost:8000')
      } else if (err.response?.status === 400) {
        setError(err.response?.data?.detail || 'Invalid email or password. Email may already be registered.')
      } else if (err.response?.status === 409) {
        const detail = err.response?.data?.detail || ''
        if (detail.includes('already registered')) {
          setError('This email is already registered. Please login instead.')
        } else {
          setError(detail || 'This email is already registered.')
        }
      } else {
        setError(err.response?.data?.detail || err.message || 'Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!otp.trim()) {
      setError('OTP is required')
      return
    }

    if (otp.length !== 6) {
      setError('OTP must be 6 digits')
      return
    }

    setLoading(true)

    try {
      const response = await authAPI.verifyOTP(email.trim().toLowerCase(), otp.trim())
      if (response.success) {
        setSuccess('Email verified successfully! Redirecting...')
        // Check if user has fields
        try {
          const userResponse = await authAPI.getCurrentUser()
          if (userResponse.success && userResponse.user.fields?.length > 0) {
            const field = userResponse.user.fields[0]
            if (field.location && field.sowing_date) {
              // User has complete field data - go to production dashboard
              router.push('/production-dashboard')
            } else {
              // Incomplete field data - go to welcome
              router.push('/welcome')
            }
          } else {
            // No fields - go to welcome
            router.push('/welcome')
          }
        } catch (userErr: any) {
          router.push('/welcome')
        }
      }
    } catch (err: any) {
      if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
        setError('Cannot connect to server. Make sure the backend API is running on http://localhost:8000')
      } else if (err.response?.status === 401) {
        setError('Invalid or expired OTP. Please check your email and try again.')
      } else {
        setError(err.response?.data?.detail || err.message || 'OTP verification failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleResendOTP = async () => {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const response = await authAPI.sendOTP(email.trim().toLowerCase())
      if (response.success) {
        // Check if OTP is in response (email failed to send - likely sandbox mode)
        if (response.otp) {
          setDisplayOtp(response.otp)
          setSuccess('OTP resent successfully!')
        } else {
          setDisplayOtp(null)
          setSuccess('OTP resent to your email!')
        }
        setOtp('') // Clear previous OTP
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to resend OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div 
      className="min-h-screen flex"
      style={{
        background: 'linear-gradient(180deg, #FFE5D4 0%, #FFD4B3 50%, #FFC996 100%)',
      }}
    >
      {/* Left side - Branding without image */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden items-center justify-center">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-green-500/5 z-0" />
        <div className="relative z-20 flex items-center justify-center w-full px-12">
          <div className="text-center">
            <div className="text-8xl mb-6">🥔</div>
            <h1 className="text-6xl font-bold mb-6 text-gray-900 tracking-tight" style={{ fontFamily: 'Georgia, serif' }}>
              POTATO<br />SHIELD
            </h1>
            <p className="text-xl text-gray-700 font-medium mb-4" style={{ fontFamily: 'Georgia, serif' }}>
              Advanced Agricultural Intelligence Platform
            </p>
            <p className="text-base text-gray-600 leading-relaxed max-w-md mx-auto" style={{ fontFamily: 'Georgia, serif' }}>
              Leveraging artificial intelligence and machine learning to provide comprehensive disease detection, 
              risk assessment, and preventive recommendations for optimal crop management.
            </p>
          </div>
        </div>
      </div>

      {/* Right side - Login/Register Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white/40 backdrop-blur-sm">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2 text-gray-900" style={{ fontFamily: 'Georgia, serif' }}>
              {mode === 'login' ? 'Authentication Required' : mode === 'register' ? 'Account Registration' : 'Email Verification'}
            </h2>
            <p className="text-gray-700 text-sm" style={{ fontFamily: 'Georgia, serif' }}>
              {mode === 'login' ? 'Please provide your credentials to access the platform' : mode === 'register' ? 'Create a new account to begin monitoring your crops' : 'Enter the verification code sent to your email address'}
            </p>
          </div>

          {/* Backend / API picker - choose which database/API to use (e.g. staging vs local) */}
          {mode === 'login' && (
            <div className="mb-4 p-3 bg-gray-50/80 rounded-lg border border-gray-200">
              <button
                type="button"
                onClick={() => setShowBackendPicker(!showBackendPicker)}
                className="w-full flex items-center justify-between text-left text-sm font-medium text-gray-700"
                style={{ fontFamily: 'Georgia, serif' }}
              >
                <span>Backend / API</span>
                <span className="text-xs text-gray-500 font-normal">
                  Connected to: {displayApiUrl}
                </span>
                <span className="text-gray-400">{showBackendPicker ? '▼' : '▶'}</span>
              </button>
              {showBackendPicker && (
                <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="backend"
                      checked={backendChoice === 'default'}
                      onChange={() => {
                        setBackendChoice('default')
                        applyBackend('default')
                      }}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm">Default (Staging / current deployment)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="backend"
                      checked={backendChoice === 'local'}
                      onChange={() => {
                        setBackendChoice('local')
                        applyBackend('local')
                      }}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm">Local (localhost:8000)</span>
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="backend"
                      checked={backendChoice === 'custom'}
                      onChange={() => setBackendChoice('custom')}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm">Custom URL:</span>
                  </div>
                  {backendChoice === 'custom' && (
                    <div className="pl-6 flex gap-2">
                      <input
                        type="url"
                        value={customApiUrl}
                        onChange={(e) => setCustomApiUrl(e.target.value)}
                        onBlur={() => customApiUrl.trim() && applyBackend('custom', customApiUrl)}
                        placeholder="https://your-api.example.com"
                        className="flex-1 px-2 py-1.5 text-sm border border-gray-300 rounded"
                      />
                      <button
                        type="button"
                        onClick={() => customApiUrl.trim() && applyBackend('custom', customApiUrl)}
                        className="px-2 py-1.5 text-sm bg-gray-200 rounded hover:bg-gray-300"
                      >
                        Use
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Quick Access Links - Only show when logged in or after successful login */}
          {mode === 'login' && (
            <div className="mb-6 p-4 bg-blue-50/50 rounded-lg border border-blue-200/50">
              <p className="text-xs text-gray-600 mb-3 font-medium" style={{ fontFamily: 'Georgia, serif' }}>
                Quick Access After Login:
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                <button
                  onClick={() => router.push('/diagnostic-dashboard')}
                  className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  style={{ fontFamily: 'Georgia, serif' }}
                >
                  🧠 Diagnostic
                </button>
                <button
                  onClick={() => router.push('/chat')}
                  className="px-3 py-1.5 text-xs bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                  style={{ fontFamily: 'Georgia, serif' }}
                >
                  💬 Chat
                </button>
                <button
                  onClick={() => router.push('/production-dashboard')}
                  className="px-3 py-1.5 text-xs bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors"
                  style={{ fontFamily: 'Georgia, serif' }}
                >
                  📊 Dashboard
                </button>
              </div>
            </div>
          )}

          {mode === 'verify' ? (
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              {/* Testing Phase Banner - Show OTP if available */}
              {displayOtp && (
                <div className="bg-gradient-to-r from-orange-500 to-yellow-500 border-2 border-orange-600 rounded-lg p-4 shadow-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">🧪</span>
                    <h3 className="text-lg font-bold text-gray-900" style={{ fontFamily: 'system-ui, sans-serif' }}>
                      TESTING PHASE
                    </h3>
                  </div>
                  <p className="text-sm text-gray-800 mb-3" style={{ fontFamily: 'system-ui, sans-serif' }}>
                    Email service is currently in testing mode. Use the OTP code below:
                  </p>
                  <div className="bg-white/90 backdrop-blur-sm rounded-lg p-4 text-center">
                    <p className="text-xs text-gray-600 mb-1" style={{ fontFamily: 'system-ui, sans-serif' }}>Your OTP Code:</p>
                    <p className="text-4xl font-bold text-gray-900 tracking-widest" style={{ fontFamily: 'monospace' }}>
                      {displayOtp}
                    </p>
                  </div>
                  <p className="text-xs text-gray-700 mt-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                    💡 Copy this code and paste it below to verify your email.
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  EMAIL ADDRESS
                </label>
                <input
                  type="email"
                  value={email}
                  disabled
                  className="w-full px-4 py-3 bg-white/60 backdrop-blur-sm border-2 border-gray-300 rounded text-gray-700 text-sm cursor-not-allowed"
                  style={{ textTransform: 'none' }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  OTP CODE
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  required
                  maxLength={6}
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-900 rounded focus:outline-none focus:border-orange-500 text-gray-900 text-xl font-bold text-center tracking-widest placeholder-gray-400 smooth-transition"
                  placeholder="000000"
                  autoFocus
                  style={{ textTransform: 'none' }}
                />
                <p className="mt-2 text-sm text-gray-600 text-center" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  {displayOtp ? 'Enter the OTP code shown above' : 'Check your email for the 6-digit OTP code'}
                </p>
              </div>

              {success && (
                <div className="p-3 bg-green-500/20 border border-green-500 rounded text-sm text-green-700" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  {success}
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-500/20 border border-red-500 rounded text-sm text-red-700" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed smooth-transition shadow-lg"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                {loading ? 'VERIFYING...' : 'VERIFY OTP'}
              </button>

              <div className="text-center space-y-2">
                <button
                  type="button"
                  onClick={handleResendOTP}
                  disabled={loading}
                  className="robotic-text-small text-orange/60 hover:text-orange transition-colors smooth-transition disabled:opacity-50"
                >
                  RESEND OTP
                </button>
                <div>
                  <button
                    type="button"
                    onClick={() => {
                      setMode('login')
                      setError('')
                      setSuccess('')
                      setOtp('')
                      setOtpSent(false)
                    }}
                    className="robotic-text-small text-orange/60 hover:text-orange transition-colors smooth-transition"
                  >
                    BACK TO LOGIN
                  </button>
                </div>
              </div>
            </form>
          ) : mode === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  EMAIL ADDRESS
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-300 rounded focus:outline-none focus:border-orange-500 text-gray-900 placeholder-gray-400 smooth-transition"
                  placeholder="your.email@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  PASSWORD
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-300 rounded focus:outline-none focus:border-orange-500 text-gray-900 placeholder-gray-400 smooth-transition"
                  placeholder="Enter your password"
                  style={{ textTransform: 'none' }}
                />
              </div>

              {success && (
                <div className="p-3 bg-green-900/20 border border-green-500 rounded robotic-text-small text-green-400">
                  {success}
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-900/20 border border-red-500 rounded robotic-text-small text-red-400">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-orange to-green text-black robotic-text-medium rounded border-2 border-orange hover:glow-orange transition-all disabled:opacity-50 disabled:cursor-not-allowed smooth-transition"
              >
                {loading ? 'LOGGING IN...' : 'LOGIN'}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => {
                    setMode('register')
                    setError('')
                    setPassword('')
                  }}
                  className="robotic-text-small text-orange/60 hover:text-orange transition-colors smooth-transition"
                >
                  DON'T HAVE AN ACCOUNT? REGISTER
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  EMAIL ADDRESS
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-300 rounded focus:outline-none focus:border-orange-500 text-gray-900 placeholder-gray-400 smooth-transition"
                  placeholder="your.email@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  PASSWORD
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-300 rounded focus:outline-none focus:border-orange-500 text-gray-900 placeholder-gray-400 smooth-transition"
                  placeholder="Minimum 6 characters"
                  style={{ textTransform: 'none' }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-800" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  CONFIRM PASSWORD
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border-2 border-gray-300 rounded focus:outline-none focus:border-orange-500 text-gray-900 placeholder-gray-400 smooth-transition"
                  placeholder="Confirm your password"
                  style={{ textTransform: 'none' }}
                />
              </div>

              {success && (
                <div className="p-3 bg-green-900/20 border border-green-500 rounded robotic-text-small text-green-400">
                  {success}
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-900/20 border border-red-500 rounded robotic-text-small text-red-400">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed smooth-transition shadow-lg"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                {loading ? 'REGISTERING...' : 'REGISTER'}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => {
                    setMode('login')
                    setError('')
                    setPassword('')
                    setConfirmPassword('')
                  }}
                  className="robotic-text-small text-orange/60 hover:text-orange transition-colors smooth-transition"
                >
                  ALREADY HAVE AN ACCOUNT? LOGIN
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
