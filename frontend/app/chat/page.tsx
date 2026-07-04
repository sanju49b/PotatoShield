'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { authAPI, conversationAPI, chatAPI, getApiBaseUrl, Conversation, Message } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import ChartAgent from '@/components/ChartAgent'
import MarkdownRenderer from '@/components/MarkdownRenderer'

export default function ChatPage() {
  const router = useRouter()
  const languageOptions = [
    { code: 'english', label: 'English', native: 'English' },
    { code: 'hindi', label: 'Hindi', native: 'हिंदी' },
    { code: 'telugu', label: 'Telugu', native: 'తెలుగు' },
    { code: 'tamil', label: 'Tamil', native: 'தமிழ்' },
  ]
  const [preferredLanguage, setPreferredLanguage] = useState<string>('english')
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [user, setUser] = useState<any>(null)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [showImageOptions, setShowImageOptions] = useState(false)
  const [streamingResponse, setStreamingResponse] = useState('')
  const [streamingStage, setStreamingStage] = useState<string | null>(null)
  const [currentProgress, setCurrentProgress] = useState<{message: string, stage: string} | null>(null)
  const [chartData, setChartData] = useState<any>(null)
  const [finalRiskPercentage, setFinalRiskPercentage] = useState<{late_blight: number, early_blight: number, overall: number} | null>(null)
  const [showRiskAlert, setShowRiskAlert] = useState<{late_blight: number, early_blight: number, overall: number, late_blight_level: string, early_blight_level: string} | null>(null)
  const [currentStreamingMessageId, setCurrentStreamingMessageId] = useState<string | null>(null)
  const [isSimulatingProgress, setIsSimulatingProgress] = useState(false)
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const [showWelcomeScreen, setShowWelcomeScreen] = useState(false)
  const [welcomeScreenData, setWelcomeScreenData] = useState<any>(null)
  const [welcomeLocation, setWelcomeLocation] = useState('')
  const [welcomeSowingDate, setWelcomeSowingDate] = useState('')
  const [locationSuggestions, setLocationSuggestions] = useState<any[]>([])
  const [showLocationSuggestions, setShowLocationSuggestions] = useState(false)
  const [locationSearchTimeout, setLocationSearchTimeout] = useState<NodeJS.Timeout | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    checkAuth()
    loadConversations()
  }, [])
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedLang = window.sessionStorage.getItem('chat_language_preference')
      if (storedLang && languageOptions.some((lang) => lang.code === storedLang)) {
        setPreferredLanguage(storedLang)
      }
    }
  }, [])

  // Refresh user data when component mounts or when navigating from setup
  useEffect(() => {
    const refreshUser = async () => {
      try {
        const response = await authAPI.getCurrentUser()
        if (response.success) {
          setUser(response.user)
        }
      } catch (error) {
        console.error('Failed to refresh user:', error)
      }
    }
    refreshUser()
  }, [])

  useEffect(() => {
    if (currentConversation) {
      loadMessages(currentConversation)
    }
  }, [currentConversation])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const checkAuth = async () => {
    try {
      const response = await authAPI.getCurrentUser()
      if (response.success) {
        setUser(response.user)
        // No longer redirecting if no fields - chat works without field data
        // Users can use chat, diagnostic, or prediction agents independently
      } else {
        router.push('/login')
      }
    } catch {
      router.push('/login')
    }
  }

  const handleLanguageSelect = (languageCode: string) => {
    setPreferredLanguage(languageCode)
    if (typeof window !== 'undefined') {
      window.sessionStorage.setItem('chat_language_preference', languageCode)
    }
  }

  const loadConversations = async () => {
    try {
      const response = await conversationAPI.getAll()
      if (response.success) {
        setConversations(response.conversations)
        if (response.conversations.length > 0 && !currentConversation) {
          setCurrentConversation(response.conversations[0].conversation_id)
        }
      }
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }

  const loadMessages = async (conversationId: string) => {
    try {
      const response = await conversationAPI.getMessages(conversationId)
      if (response.success) {
        setMessages(response.messages)
        
        // Check for welcome screen data
        if (response.welcome_screen && response.welcome_screen.show) {
          setWelcomeScreenData(response.welcome_screen)
          setWelcomeLocation(response.welcome_screen.location || '')
          setWelcomeSowingDate(response.welcome_screen.sowing_date || '')
          setShowWelcomeScreen(true)
        } else {
          setShowWelcomeScreen(false)
        }
      }
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }

  const createNewChat = async () => {
    try {
      // Clear current state first
      setMessages([])
      setCurrentConversation(null)
      setInput('')
      setSelectedImage(null)
      setImagePreview(null)
      setStreamingResponse('')
      setStreamingStage(null)
      setShowWelcomeScreen(false)
      
      // Create new conversation
      const response = await conversationAPI.create()
      if (response.success) {
        await loadConversations()
        setCurrentConversation(response.conversation_id)
        // Ensure messages are cleared
        setMessages([])
        
        // Check for welcome screen data in response
        if (response.welcome_screen && response.welcome_screen.show) {
          setWelcomeScreenData(response.welcome_screen)
          setWelcomeLocation(response.welcome_screen.location || '')
          setWelcomeSowingDate(response.welcome_screen.sowing_date || '')
          setShowWelcomeScreen(true)
        }
      }
    } catch (error) {
      console.error('Failed to create conversation:', error)
      // Still clear the UI even if API call fails
      setMessages([])
      setCurrentConversation(null)
    }
  }

  const handleImageSelect = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target?.result as string
      setSelectedImage(base64)
      setImagePreview(base64)
      setShowImageOptions(false)
    }
    reader.readAsDataURL(file)
  }

  const handleCameraCapture = async () => {
    // Try using MediaDevices API first (works on desktop and mobile)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        const video = document.createElement('video')
        video.srcObject = stream
        video.play()
        
        // Create a canvas to capture the photo
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        
        video.addEventListener('loadedmetadata', () => {
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
          
          // Show a simple modal to take the photo
          const modal = document.createElement('div')
          modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center;'
          
          const videoContainer = document.createElement('div')
          videoContainer.appendChild(video)
          video.style.cssText = 'max-width: 90vw; max-height: 70vh; border-radius: 8px;'
          
          const buttonContainer = document.createElement('div')
          buttonContainer.style.cssText = 'margin-top: 20px; display: flex; gap: 10px;'
          
          const captureButton = document.createElement('button')
          captureButton.textContent = '📷 Capture Photo'
          captureButton.style.cssText = 'padding: 12px 24px; background: #1f2937; color: white; border: none; border-radius: 9999px; font-size: 16px; cursor: pointer;'
          
          const cancelButton = document.createElement('button')
          cancelButton.textContent = 'Cancel'
          cancelButton.style.cssText = 'padding: 12px 24px; background: #6b7280; color: white; border: none; border-radius: 9999px; font-size: 16px; cursor: pointer;'
          
          captureButton.onclick = () => {
            ctx?.drawImage(video, 0, 0)
            const base64 = canvas.toDataURL('image/jpeg', 0.8)
            setSelectedImage(base64)
            setImagePreview(base64)
            stream.getTracks().forEach(track => track.stop())
            document.body.removeChild(modal)
          }
          
          cancelButton.onclick = () => {
            stream.getTracks().forEach(track => track.stop())
            document.body.removeChild(modal)
          }
          
          buttonContainer.appendChild(captureButton)
          buttonContainer.appendChild(cancelButton)
          modal.appendChild(videoContainer)
          modal.appendChild(buttonContainer)
          document.body.appendChild(modal)
        })
      } catch (error) {
        console.error('MediaDevices API failed, falling back to file input:', error)
        // Fallback to file input with capture attribute
        cameraInputRef.current?.click()
      }
    } else {
      // Fallback to file input with capture attribute
      cameraInputRef.current?.click()
    }
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  const handleRemoveImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if ((!input.trim() && !selectedImage) || loading) return

    const userMessage = input.trim() || (selectedImage ? 'Please analyze this image' : '')
    setInput('')
    const imageToSend = selectedImage
    setSelectedImage(null)
    setImagePreview(null)

    // Create conversation if none exists
    let convId = currentConversation
    if (!convId) {
      const response = await conversationAPI.create()
      if (response.success) {
        convId = response.conversation_id
        setCurrentConversation(convId)
        await loadConversations()
      }
    }

    if (!convId) return

    // Add user message (with image indicator if image was sent)
    const userMsg: Message = {
      message_id: `temp-${Date.now()}`,
      conversation_id: convId,
      role: 'user',
      content: userMessage + (imageToSend ? ' [Image attached]' : ''),
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])

    // Save user message
    try {
      await conversationAPI.addMessage(convId, 'user', userMessage, {
        has_image: !!imageToSend,
      })
    } catch (error) {
      console.error('Failed to save user message:', error)
    }

    // Generate intelligent response using workflow
    setLoading(true)
    setStreamingResponse('')
    setStreamingStage(null)
    setCurrentProgress(null)
    setChartData(null)
    setFinalRiskPercentage(null)
    setIsSimulatingProgress(false)
    
    // Clear any existing progress interval
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current)
      progressIntervalRef.current = null
    }

    try {
      // Use streaming API
      const assistantMsgId = `temp-${Date.now() + 1}`
      setCurrentStreamingMessageId(assistantMsgId) // Track which message is currently streaming
      let assistantContent = ''
      let routingInfo: any = null
      let diagnosticData: any = null
      let eventCount = 0

      // Create placeholder assistant message
      const assistantMsg: Message = {
        message_id: assistantMsgId,
        conversation_id: convId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMsg])

      // Stream response with real-time updates
      console.log('[FRONTEND] Starting to stream response...')
      for await (const event of chatAPI.chatStream(
        userMessage,
        convId,
        imageToSend || undefined,
        undefined,
        preferredLanguage
      )) {
        eventCount++
        console.log(`[FRONTEND] Event #${eventCount} received:`, event.type, event)
        
        if (event.type === 'status') {
          setStreamingStage(event.stage)
          
          // Debug logging
          console.log('[FRONTEND] Status event received:', {
            message: event.message,
            stage: event.stage
          })
          
          // ONLY update progress for predictive agent stages
          const isPredictiveStage = event.stage === 'predicting' || 
                                   event.stage === 'initialization' ||
                                   event.stage === 'extract_data' ||
                                   event.stage === 'collect_weather' ||
                                   event.stage === 'analyze_temperature' ||
                                   event.stage === 'analyze_humidity' ||
                                   event.stage === 'hutton_check' ||
                                   event.stage === 'growth_stage' ||
                                   event.stage === 'analyze_precipitation' ||
                                   event.stage === 'analyze_wind_air' ||
                                   event.stage === 'late_blight' ||
                                   event.stage === 'early_blight' ||
                                   event.stage === 'generate_charts' ||
                                   event.stage === 'final_report' ||
                                   event.stage === 'complete'
          
          // ONLY show progress bar for predictive agent
          if (isPredictiveStage) {
            // Stop simulation if running
            if (progressIntervalRef.current) {
              clearInterval(progressIntervalRef.current)
              progressIntervalRef.current = null
              setIsSimulatingProgress(false)
            }
            
            // Show natural language status message in progress display
            // BUT: Don't overwrite during collect_weather stage - let data_collection_progress events show
            if (event.message && event.stage !== 'collect_weather') {
              setCurrentProgress({
                message: event.message,
                stage: event.stage || 'processing'
              })
              
              // DON'T add to assistantContent - AI narrator will handle user-facing messages
              console.log('[FRONTEND] Status update shown in progress bar only (hidden from chat)')
            }
          } else {
            // Clear progress bar for non-predictive stages
            if (currentProgress) {
              setCurrentProgress(null)
            }
            if (progressIntervalRef.current) {
              clearInterval(progressIntervalRef.current)
              progressIntervalRef.current = null
              setIsSimulatingProgress(false)
            }
          }
        }
        else if (event.type === 'data_collection_progress') {
          // Stream data collection progress messages in real-time
          const progressMessage = event.message || ''
          console.log('[FRONTEND] data_collection_progress event received:', {
            message: progressMessage.substring(0, 50),
            stage: event.stage,
            fullEvent: event
          })
          if (progressMessage.trim()) {
            // Show in progress display ONLY (not in main content - AI narration will handle that)
            setCurrentProgress({
              message: progressMessage,
              stage: event.stage || 'collect_weather'
            })
            
            // DON'T add to assistantContent - AI narration will provide user-friendly commentary
            console.log('[FRONTEND] Updated progress display (technical message hidden from chat)')
          }
        }
        else if (event.type === 'ai_narration') {
          // AI-powered narration of what's happening - THIS IS WHAT USERS SEE DURING PROCESSING
          const narrationChunk = event.chunk || ''
          console.log('[FRONTEND] AI narration received:', narrationChunk.substring(0, 30))
          
          // Append AI narration to content - this is temporary and will be replaced by final report
          assistantContent += narrationChunk
          setStreamingResponse(assistantContent)
          setMessages((prev) => prev.map((msg) => 
            msg.message_id === assistantMsgId 
              ? { ...msg, content: assistantContent }
              : msg
          ))
        }
        else if (event.type === 'stream_char') {
          // Character-by-character streaming for smooth typing effect
          const char = event.char || event.chunk || ''
          
          // When final report starts (detected by emoji markers), CLEAR ALL AI NARRATION and start fresh
          if ((char.includes('🌦️') || char.includes('🌡️') || char.includes('🧬')) && assistantContent.length > 0) {
            console.log('[FRONTEND] Final report starting - clearing AI narration drafts')
            // Clear ALL previous content (AI narration drafts) and start with final report
            assistantContent = char
          } else {
            assistantContent += char
          }
          
          setStreamingResponse(assistantContent)
          // Update message in real-time so it shows up immediately
          setMessages((prev) => prev.map((msg) => 
            msg.message_id === assistantMsgId 
              ? { ...msg, content: assistantContent }
              : msg
          ))
        }
        else if (event.type === 'chat_stream') {
          // General chat agent streaming
          assistantContent += event.chunk || ''
          setStreamingResponse(assistantContent)
        }
        else if (event.type === 'routing') {
          // Skip routing information - internal system process
        }
        else if (event.type === 'content_chunk') {
          // Stream actual content chunks incrementally - this is the real-time content!
          if (event.content) {
            // When final content starts arriving, clear progress messages and show clean content
            // Check if this is the start of the final report (contains emoji or structured content)
            const isFinalReport = event.content.includes('🌦️') || event.content.includes('🌡️') || event.content.includes('🧬')
            
            if (isFinalReport && assistantContent.includes('📊')) {
              // Clear progress messages and start fresh with final report
              assistantContent = event.content
            } else {
              // Append to existing content
              assistantContent += event.content
            }
            
            setStreamingResponse(assistantContent)
            // Update the assistant message in real-time
            setMessages((prev) => prev.map((msg) => 
              msg.message_id === assistantMsgId 
                ? { ...msg, content: assistantContent }
                : msg
            ))
          }
        }
        // Diagnostic agent streaming
        else if (event.type === 'diagnostic_start') {
          assistantContent += `${event.message}\n`
          setStreamingResponse(assistantContent)
        }
        else if (event.type === 'diagnostic_thinking') {
          assistantContent += `${event.message}\n`
          setStreamingResponse(assistantContent)
        }
        else if (event.type === 'diagnostic_stream') {
          // Append streaming chunks from diagnostic agent
          assistantContent += event.chunk || ''
          setStreamingResponse(assistantContent)
        }
        else if (event.type === 'diagnostic_progress') {
          // Show intermediate diagnostic progress
          if (event.stage === 'identified') {
            assistantContent += `\n${event.message}\n`
          } else if (event.stage === 'confidence') {
            assistantContent += `${event.message}\n`
          } else if (event.stage === 'severity') {
            assistantContent += `${event.message}\n\n`
          }
          setStreamingResponse(assistantContent)
        }
        else if (event.type === 'diagnostic') {
          diagnosticData = event.data
          // Clear status message when diagnostic result is received
          setTimeout(() => {
            setCurrentProgress(null)
          }, 1000)
          
          // CLEAR ALL AI NARRATION and start with fresh diagnostic result
          console.log('[FRONTEND] Diagnostic result received - clearing AI narration drafts')
          
          const diag = event.data
          assistantContent = `\n🔍 **DISEASE ANALYSIS COMPLETE**\n\n`
          assistantContent += `**DISEASE TYPE:** ${diag.disease_type}\n`
          assistantContent += `**CONFIDENCE:** ${diag.confidence_percentage || diag.confidence}% (${diag.confidence?.toUpperCase() || 'HIGH'})\n`
          assistantContent += `**SEVERITY:** ${diag.severity?.toUpperCase() || 'UNKNOWN'}\n\n`
          assistantContent += `**SUMMARY:**\n${diag.summary}\n\n`
          if (diag.key_visual_indicators && diag.key_visual_indicators.length > 0) {
            assistantContent += `**KEY VISUAL INDICATORS:**\n`
            diag.key_visual_indicators.forEach((indicator: string) => {
              assistantContent += `• ${indicator}\n`
            })
            assistantContent += `\n`
          }
          assistantContent += `**RECOMMENDATIONS:**\n${diag.recommendations}\n`
          setStreamingResponse(assistantContent)
        }
        // Predictive agent progress and charts
        else if (event.type === 'predictive_progress') {
          if (event.message) {
            assistantContent += `${event.message}\n`
            setStreamingResponse(assistantContent)
          }
        }
        else if (event.type === 'chart_data') {
          // Store chart data for visualization
          console.log('[FRONTEND] Chart data received:', event.data)
          if (event.data) {
            // Debug: Log risk timeline data
            if (event.data.risk_timeline) {
              console.log('[FRONTEND] Risk timeline data:', {
                dates: event.data.risk_timeline.dates,
                late_blight_risk: event.data.risk_timeline.late_blight_risk,
                early_blight_risk: event.data.risk_timeline.early_blight_risk,
                overall_risk: event.data.risk_timeline.overall_risk,
                late_blight_range: event.data.risk_timeline.late_blight_risk.length > 0 
                  ? `[${Math.min(...event.data.risk_timeline.late_blight_risk).toFixed(1)}% - ${Math.max(...event.data.risk_timeline.late_blight_risk).toFixed(1)}%]`
                  : 'No data',
                early_blight_range: event.data.risk_timeline.early_blight_risk.length > 0
                  ? `[${Math.min(...event.data.risk_timeline.early_blight_risk).toFixed(1)}% - ${Math.max(...event.data.risk_timeline.early_blight_risk).toFixed(1)}%]`
                  : 'No data',
              })
            }
            setChartData(event.data)
            // Extract final risk percentage if available
            if (event.data.final_risk_percentage) {
              console.log('[FRONTEND] Final risk percentage:', event.data.final_risk_percentage)
              setFinalRiskPercentage(event.data.final_risk_percentage)
            }
          }
        }
        else if (event.type === 'final_risk') {
          // Direct final risk percentage event
          console.log('Final risk event received:', event.data)
          if (event.data) {
            setFinalRiskPercentage(event.data)
            // Show prominent alert for 3 seconds
            setShowRiskAlert({
              late_blight: event.data.late_blight || 0,
              early_blight: event.data.early_blight || 0,
              overall: event.data.overall || 0,
              late_blight_level: 'Unknown',
              early_blight_level: 'Unknown'
            })
            setTimeout(() => setShowRiskAlert(null), 3000)
          }
        }
        else if (event.type === 'predictive_result') {
          // Stop simulated progress and set to 100%
          if (progressIntervalRef.current) {
            clearInterval(progressIntervalRef.current)
            progressIntervalRef.current = null
            setIsSimulatingProgress(false)
          }
          // Show completion message briefly, then clear
          setCurrentProgress({
            message: 'Analysis complete!',
            stage: 'complete'
          })
          // Clear after 2 seconds
          setTimeout(() => {
            setCurrentProgress(null)
          }, 2000)
          
          // Store prediction result data
          console.log('Predictive result received:', event.data)
          if (event.data) {
            if (event.data.chart_data) {
              setChartData(event.data.chart_data)
              if (event.data.chart_data.final_risk_percentage) {
                setFinalRiskPercentage(event.data.chart_data.final_risk_percentage)
                // Show prominent alert for 3 seconds
                const lb = event.data.late_blight_risk || {}
                const eb = event.data.early_blight_risk || {}
                setShowRiskAlert({
                  late_blight: event.data.chart_data.final_risk_percentage.late_blight || 0,
                  early_blight: event.data.chart_data.final_risk_percentage.early_blight || 0,
                  overall: event.data.chart_data.final_risk_percentage.overall || 0,
                  late_blight_level: lb.risk_level || 'Unknown',
                  early_blight_level: eb.risk_level || 'Unknown'
                })
                setTimeout(() => setShowRiskAlert(null), 3000)
              }
            }
            // Also check for chart_data at root level
            if (event.chart_data) {
              setChartData(event.chart_data)
              if (event.chart_data.final_risk_percentage) {
                setFinalRiskPercentage(event.chart_data.final_risk_percentage)
                const lb = event.data.late_blight_risk || {}
                const eb = event.data.early_blight_risk || {}
                setShowRiskAlert({
                  late_blight: event.chart_data.final_risk_percentage.late_blight || 0,
                  early_blight: event.chart_data.final_risk_percentage.early_blight || 0,
                  overall: event.chart_data.final_risk_percentage.overall || 0,
                  late_blight_level: lb.risk_level || 'Unknown',
                  early_blight_level: eb.risk_level || 'Unknown'
                })
                setTimeout(() => setShowRiskAlert(null), 3000)
              }
            }
            // Don't add summary here - it's already in the streamed content
            // Just update the streaming response state
            setStreamingResponse(assistantContent)
          }
        }
        else if (event.type === 'report') {
          // Append or replace with final report
          if (event.content) {
            assistantContent = `${assistantContent}\n\n${event.content}`
            setStreamingResponse(assistantContent)
          }
          // Clear status message when final report is received
          setTimeout(() => {
            setCurrentProgress(null)
          }, 1000)
        }
        else if (event.type === 'diagnostic' || event.type === 'diagnostic_result') {
          // Clear status message when diagnostic result is received
          setTimeout(() => {
            setCurrentProgress(null)
          }, 1000)
        }
        else if (event.type === 'error') {
          assistantContent += `\n❌ Error: ${event.message}\n`
          setStreamingResponse(assistantContent)
        }
        else if (event.type === 'rai_validation_warning') {
          // RAI output validation warning (non-blocking)
          console.warn('[RAI] Output validation warning:', event.checks)
          // Optionally show a subtle warning to user
          // assistantContent += `\n⚠️ Note: Response validated for safety\n`
        }
        else if (event.type === 'rai_validation_success') {
          // RAI validation passed successfully
          console.log('[RAI] Output validation passed:', event.checks)
        }
        else if (event.type === 'translations') {
          const translations = event.data || event.translations || {}
          if (preferredLanguage && preferredLanguage !== 'english') {
            const localized = translations[preferredLanguage]
            if (localized) {
              assistantContent = localized
              setStreamingResponse(localized)
            }
          }
        }
        else if (event.type === 'done') {
          // Clear status message when streaming is complete
          setCurrentProgress(null)
          console.log(`[FRONTEND] Streaming complete. Total events received: ${eventCount}`)
          break
        }
        else {
          // Log any unhandled event types
          console.warn(`[FRONTEND] Unhandled event type: ${event.type}`, event)
        }
      }
      console.log(`[FRONTEND] Stream loop ended. Total events: ${eventCount}`)

      // Update final message - ONLY the current streaming message
      setMessages((prev) =>
        prev.map((msg) =>
          msg.message_id === assistantMsgId
            ? { ...msg, content: assistantContent || streamingResponse }
            : msg // Keep all other messages unchanged
        )
      )

      // Save assistant message
      await conversationAPI.addMessage(convId, 'assistant', assistantContent || streamingResponse, {
        routing_info: routingInfo,
        diagnostic_data: diagnosticData,
      })
    } catch (error: any) {
      console.error('[FRONTEND] Chat error:', error)
      console.error('[FRONTEND] Error details:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      })
      const errorMsg: Message = {
        message_id: `temp-${Date.now() + 2}`,
        conversation_id: convId,
        role: 'assistant',
        content: `Error: ${error.message || 'Failed to process request. Please try again.'}\n\nIf streaming is not working, check the browser console for details.`,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
      setStreamingResponse('')
      setStreamingStage(null)
      setCurrentStreamingMessageId(null) // Clear streaming message ID
      // Keep progress and charts visible after completion
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleLogout = () => {
    authAPI.logout()
    router.push('/login')
  }

  const searchLocationSuggestions = async (query: string) => {
    if (query.length < 3) {
      setLocationSuggestions([])
      setShowLocationSuggestions(false)
      return
    }

    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      const response = await fetch(`${getApiBaseUrl()}/api/location/search?query=${encodeURIComponent(query)}`, {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      })

      const data = await response.json()
      if (data.success && data.suggestions) {
        setLocationSuggestions(data.suggestions)
        setShowLocationSuggestions(true)
      } else {
        setLocationSuggestions([])
        setShowLocationSuggestions(false)
      }
    } catch (error) {
      console.error('Failed to search locations:', error)
      setLocationSuggestions([])
      setShowLocationSuggestions(false)
    }
  }

  const handleLocationInputChange = (value: string) => {
    setWelcomeLocation(value)
    
    // Clear existing timeout
    if (locationSearchTimeout) {
      clearTimeout(locationSearchTimeout)
    }
    
    // Debounce search - wait 300ms after user stops typing
    const timeout = setTimeout(() => {
      searchLocationSuggestions(value)
    }, 300)
    
    setLocationSearchTimeout(timeout)
  }

  const handleLocationSelect = (suggestion: any) => {
    setWelcomeLocation(suggestion.name)
    setLocationSuggestions([])
    setShowLocationSuggestions(false)
  }

  const handleWelcomeScreenUpdate = async (action: 'predict' | 'chat') => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      const response = await fetch(`${getApiBaseUrl()}/api/welcome/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          location: welcomeLocation,
          sowing_date: welcomeSowingDate,
          action: action,
        }),
      })

      const data = await response.json()
      if (data.success) {
        setShowWelcomeScreen(false)
        // Refresh user data
        const userResponse = await authAPI.getCurrentUser()
        if (userResponse.success) {
          setUser(userResponse.user)
        }
        
        // If action is predict, automatically trigger prediction
        if (action === 'predict') {
          // Wait a moment for the modal to close, then automatically send prediction query
          setTimeout(async () => {
            const predictMessage = 'What is the disease risk for my crop?'
            setInput('')
            
            // Create conversation if none exists
            let convId = currentConversation
            if (!convId) {
              const convResponse = await conversationAPI.create()
              if (convResponse.success) {
                convId = convResponse.conversation_id
                setCurrentConversation(convId)
                await loadConversations()
              }
            }

            if (!convId) return

            // Add user message
            const userMsg: Message = {
              message_id: `temp-${Date.now()}`,
              conversation_id: convId,
              role: 'user',
              content: predictMessage,
              created_at: new Date().toISOString(),
            }
            setMessages((prev) => [...prev, userMsg])

            // Save user message
            try {
              await conversationAPI.addMessage(convId, 'user', predictMessage, {})
            } catch (error) {
              console.error('Failed to save user message:', error)
            }

            // Generate prediction using workflow
            setLoading(true)
            setStreamingResponse('')
            setStreamingStage(null)
            setCurrentProgress(null)
            setChartData(null)
            setFinalRiskPercentage(null)

            try {
              // Use streaming API
              const assistantMsgId = `temp-${Date.now() + 1}`
              setCurrentStreamingMessageId(assistantMsgId) // Track which message is currently streaming
              let assistantContent = ''
              let routingInfo: any = null

              // Create placeholder assistant message
              const assistantMsg: Message = {
                message_id: assistantMsgId,
                conversation_id: convId,
                role: 'assistant',
                content: '',
                created_at: new Date().toISOString(),
              }
              setMessages((prev) => [...prev, assistantMsg])

              // Stream response with real-time updates
              for await (const event of chatAPI.chatStream(predictMessage, convId)) {
                if (event.type === 'status') {
                  setStreamingStage(event.stage)
                  // Update progress if available - handle both explicit progress and step-based calculation
                  // No step/progress tracking - just show natural language messages
                  
                  // Debug logging
                  console.log('[FRONTEND] Status event received (auto-predict):', {
                    message: event.message,
                    stage: event.stage
                  })
                  
                  // Always show status for predictive stages
                  const isPredictiveStage = event.stage === 'predicting' || 
                                           event.stage === 'initialization' ||
                                           event.stage === 'extract_data' ||
                                           event.stage === 'collect_weather' ||
                                           event.stage === 'analyze_temperature' ||
                                           event.stage === 'analyze_humidity' ||
                                           event.stage === 'hutton_check' ||
                                           event.stage === 'growth_stage' ||
                                           event.stage === 'analyze_precipitation' ||
                                           event.stage === 'analyze_wind_air' ||
                                           event.stage === 'late_blight' ||
                                           event.stage === 'early_blight' ||
                                           event.stage === 'generate_charts' ||
                                           event.stage === 'final_report' ||
                                           event.stage === 'complete'
                  
                  // Skip only pure routing events
                  const isPureRouting = event.stage === 'routing' && 
                                       !event.message?.includes('predict')
                  
                  if (isPredictiveStage || !isPureRouting) {
                    // Show natural language status message
                    // BUT: Don't overwrite during collect_weather stage - let data_collection_progress events show
                    if (event.message && event.stage !== 'collect_weather') {
                      setCurrentProgress({
                        message: event.message,
                        stage: event.stage || 'processing'
                      })
                      
                      // DON'T add to assistantContent - AI narrator will handle user-facing messages
                      console.log('[FRONTEND] Status update shown in progress bar only (hidden from chat, auto-predict)')
                    }
                  }
                }
                else if (event.type === 'data_collection_progress') {
                  // Stream data collection progress messages in real-time
                  const progressMessage = event.message || ''
                  console.log('[FRONTEND] data_collection_progress event received (auto-predict):', {
                    message: progressMessage.substring(0, 50),
                    stage: event.stage
                  })
                  if (progressMessage.trim()) {
                    // Show in progress display ONLY (not in main content - AI narration will handle that)
                    setCurrentProgress({
                      message: progressMessage,
                      stage: event.stage || 'collect_weather'
                    })
                    
                    // DON'T add to assistantContent - AI narration will provide user-friendly commentary
                    console.log('[FRONTEND] Updated progress display (technical message hidden from chat)')
                  }
                }
                else if (event.type === 'ai_narration') {
                  // AI-powered narration of what's happening - THIS IS WHAT USERS SEE DURING PROCESSING (auto-predict)
                  const narrationChunk = event.chunk || ''
                  console.log('[FRONTEND] AI narration received (auto-predict):', narrationChunk.substring(0, 30))
                  
                  // Append AI narration to content - this is temporary and will be replaced by final report
                  assistantContent += narrationChunk
                  setStreamingResponse(assistantContent)
                  setMessages((prev) => prev.map((msg) => 
                    msg.message_id === assistantMsgId 
                      ? { ...msg, content: assistantContent }
                      : msg
                  ))
                }
                else if (event.type === 'stream_char') {
                  const char = event.char || ''
                  
                  // When final report starts, CLEAR ALL AI NARRATION and start fresh
                  if ((char.includes('🌦️') || char.includes('🌡️') || char.includes('🧬')) && assistantContent.length > 0) {
                    console.log('[FRONTEND] Final report starting - clearing AI narration drafts (auto-predict)')
                    assistantContent = char
                  } else {
                    assistantContent += char
                  }
                  
                  setStreamingResponse(assistantContent)
                }
                else if (event.type === 'chat_stream') {
                  assistantContent += event.chunk || ''
                  setStreamingResponse(assistantContent)
                }
                else if (event.type === 'routing') {
                  // Skip routing information - internal system process
                }
                else if (event.type === 'predictive_progress') {
                  if (event.message) {
                    assistantContent += `${event.message}\n`
                    setStreamingResponse(assistantContent)
                  }
                }
                else if (event.type === 'predictive_result') {
                  // Stop simulated progress and set to 100%
                  if (progressIntervalRef.current) {
                    clearInterval(progressIntervalRef.current)
                    progressIntervalRef.current = null
                    setIsSimulatingProgress(false)
                  }
                  // Show completion message briefly, then clear
                  setCurrentProgress({
                    message: 'Analysis complete!',
                    stage: 'complete'
                  })
                  // Clear after 2 seconds
                  setTimeout(() => {
                    setCurrentProgress(null)
                  }, 2000)
                  
                  // Store prediction result data
                  if (event.data) {
                    if (event.data.chart_data) {
                      setChartData(event.data.chart_data)
                      if (event.data.chart_data.final_risk_percentage) {
                        setFinalRiskPercentage(event.data.chart_data.final_risk_percentage)
                      }
                    }
                    assistantContent += `\n✅ Prediction Complete\n\n`
                    setStreamingResponse(assistantContent)
                  }
                }
                else if (event.type === 'chart_data') {
                  // Store chart data for visualization
                  if (event.data) {
                    setChartData(event.data)
                    // Extract final risk percentage if available
                    if (event.data.final_risk_percentage) {
                      setFinalRiskPercentage(event.data.final_risk_percentage)
                    }
                  }
                }
                else if (event.type === 'report') {
                  if (event.content) {
                    assistantContent = `${assistantContent}\n\n${event.content}`
                    setStreamingResponse(assistantContent)
                  }
                  // Clear status message when final report is received
                  setTimeout(() => {
                    setCurrentProgress(null)
                  }, 1000)
                }
                else if (event.type === 'diagnostic' || event.type === 'diagnostic_result') {
                  // Clear status message when diagnostic result is received
                  setTimeout(() => {
                    setCurrentProgress(null)
                  }, 1000)
                }
                else if (event.type === 'error') {
                  assistantContent += `\n❌ Error: ${event.message}\n`
                  setStreamingResponse(assistantContent)
                }
                else if (event.type === 'done') {
                  // Clear status message when streaming is complete
                  setCurrentProgress(null)
                  break
                }
              }

              // Update final message - ONLY the current streaming message
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === assistantMsgId
                    ? { ...msg, content: assistantContent || streamingResponse }
                    : msg // Keep all other messages unchanged
                )
              )

              // Save assistant message
              await conversationAPI.addMessage(convId, 'assistant', assistantContent || streamingResponse, {
                routing_info: routingInfo,
              })
            } catch (error: any) {
              console.error('Chat error:', error)
              const errorMsg: Message = {
                message_id: `temp-${Date.now() + 2}`,
                conversation_id: convId,
                role: 'assistant',
                content: `Error: ${error.message || 'Failed to process request. Please try again.'}`,
                created_at: new Date().toISOString(),
              }
              setMessages((prev) => [...prev, errorMsg])
            } finally {
              setLoading(false)
              setStreamingResponse('')
              setStreamingStage(null)
              setCurrentStreamingMessageId(null) // Clear streaming message ID
            }
          }, 300) // Small delay to allow modal to close smoothly
        }
      }
    } catch (error) {
      console.error('Failed to update welcome screen:', error)
    }
  }

  return (
    <div 
      className="flex h-screen overflow-hidden bg-[#1a1a1a]"
    >
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-64 bg-[#2d2d2d] border-r border-[#3a3a3a] flex flex-col shadow-lg"
          >
            {/* Sidebar Header */}
            <div className="p-4 border-b border-[#3a3a3a]">
              <button
                onClick={createNewChat}
                className="w-full px-4 py-2 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all smooth-transition shadow-md"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                + NEW CHAT
              </button>
            </div>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-2 space-y-1">
                {conversations.map((conv) => (
                  <button
                    key={conv.conversation_id}
                    onClick={() => setCurrentConversation(conv.conversation_id)}
                    className={`w-full text-left px-3 py-2 rounded text-sm smooth-transition ${
                      currentConversation === conv.conversation_id
                        ? 'bg-[#3a3a3a] border border-[#4a4a4a] text-[#e8e8e8] font-medium'
                        : 'text-[#b8b8b8] hover:text-[#e8e8e8] hover:bg-[#3a3a3a] border border-transparent'
                    }`}
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  >
                    <div className="truncate">{conv.title}</div>
                    <div className="text-xs text-[#808080] mt-1">
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* User Info */}
            <div className="p-4 border-t border-[#3a3a3a]">
              <div className="text-sm text-[#e8e8e8] mb-2 font-medium" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                {user?.email || 'User'}
              </div>
              <button
                onClick={handleLogout}
                className="w-full px-3 py-2 text-sm text-[#b8b8b8] hover:text-[#e8e8e8] border border-[#3a3a3a] rounded-full hover:border-[#4a4a4a] transition-colors smooth-transition bg-[#2d2d2d]"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                Logout
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 border-b border-[#3a3a3a] flex items-center justify-between px-4 bg-[#1a1a1a]">
          <div className="flex items-center">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-[#b8b8b8] hover:text-[#e8e8e8] transition-colors smooth-transition"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="ml-4">
              <h1 className="text-xl font-semibold text-[#e8e8e8]" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>POTATO SHIELD</h1>
            </div>
          </div>
          <button
            onClick={() => router.push('/production-dashboard')}
            className="px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-full hover:from-orange-600 hover:to-orange-700 transition-all font-medium text-sm flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
            </svg>
            Dashboard
          </button>
        </div>

        {/* Welcome Screen Modal */}
        <AnimatePresence>
          {showWelcomeScreen && welcomeScreenData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => {}} // Prevent closing on backdrop click
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-8 max-h-[90vh] overflow-y-auto"
              >
                <h2 className="text-3xl font-bold mb-2 text-gray-900" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  Welcome to Potato Shield
                </h2>
                <p className="text-[#c4c4c4] mb-6" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                  Please provide your field information to get started
                </p>

                {/* Location Input with Autocomplete */}
                <div className="mb-4 relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                    Location
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={welcomeLocation}
                      onChange={(e) => handleLocationInputChange(e.target.value)}
                      onFocus={() => {
                        if (welcomeLocation.length >= 3 && locationSuggestions.length > 0) {
                          setShowLocationSuggestions(true)
                        }
                      }}
                      onBlur={() => {
                        // Delay hiding to allow click on suggestion
                        setTimeout(() => setShowLocationSuggestions(false), 200)
                      }}
                      placeholder="e.g., Coventry, UK or Hyderabad, India"
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 text-gray-900"
                      style={{ fontFamily: 'system-ui, sans-serif' }}
                    />
                    {/* Suggestions Dropdown */}
                    {showLocationSuggestions && locationSuggestions.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {locationSuggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            type="button"
                            onClick={() => handleLocationSelect(suggestion)}
                            className="w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors border-b border-gray-200 last:border-b-0"
                            style={{ fontFamily: 'system-ui, sans-serif' }}
                          >
                            <div className="font-medium text-gray-900">{suggestion.name}</div>
                            {suggestion.country && (
                              <div className="text-sm text-gray-500">{suggestion.country}</div>
                            )}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Sowing Date Input */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                    Date of Sowing
                  </label>
                  <input
                    type="date"
                    value={welcomeSowingDate}
                    onChange={(e) => setWelcomeSowingDate(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 text-gray-900"
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  />
                </div>

                {/* Action Buttons */}
                <div className="space-y-4">
                  {/* Predict Agent Button */}
                  <button
                    onClick={() => handleWelcomeScreenUpdate('predict')}
                    className="w-full p-6 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg hover:shadow-xl"
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  >
                    <div className="text-left">
                      <div className="text-xl font-bold mb-2">Continue to Predict Agent</div>
                      <div className="text-sm opacity-90">
                        Get AI-powered disease risk predictions based on weather conditions. The system analyzes temperature, humidity, precipitation, and other environmental factors to forecast the likelihood of Late Blight and Early Blight in your potato crop. Receive actionable recommendations and preventive measures tailored to your location and crop stage.
                      </div>
                    </div>
                  </button>

                  {/* Continue to Chat Button */}
                  <button
                    onClick={() => handleWelcomeScreenUpdate('chat')}
                    className="w-full p-6 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-xl hover:from-gray-900 hover:to-black transition-all shadow-lg hover:shadow-xl"
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  >
                    <div className="text-left">
                      <div className="text-xl font-bold mb-2">Continue to Chat</div>
                      <div className="text-sm opacity-90">
                        Start a conversation with our agricultural assistant. Ask questions about potato farming, get advice on crop management, discuss disease symptoms, or update your field information. The AI assistant can help with general queries, diagnose diseases from images using advanced picture prediction capabilities, or guide you through various farming challenges.
                      </div>
                    </div>
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Language Preference Selector */}
        <div className="border-b border-[#3a3a3a] px-4 py-3 bg-[#1a1a1a] flex flex-wrap items-center gap-2">
          <span className="text-xs uppercase tracking-wide text-[#808080]">Chat language</span>
          <div className="flex flex-wrap gap-2">
            {languageOptions.map((lang) => (
              <button
                key={lang.code}
                type="button"
                onClick={() => handleLanguageSelect(lang.code)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                  preferredLanguage === lang.code
                    ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/30'
                    : 'bg-[#2d2d2d] text-[#e8e8e8] hover:bg-[#3a3a3a]'
                }`}
              >
                {lang.label} <span className="opacity-70">({lang.native})</span>
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && !showWelcomeScreen ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <h2 className="text-4xl font-normal mb-4 text-white" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                  Start a Conversation
                </h2>
                <p className="text-lg text-[#c4c4c4]" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                  Ask about disease diagnosis, predictions, or field management
                </p>
              </div>
            </div>
          ) : (
            <AnimatePresence>
              {messages.map((msg) => {
                // Only show streaming for the CURRENT streaming message, not previous ones
                const isStreaming = loading && 
                                  msg.role === 'assistant' && 
                                  msg.message_id === currentStreamingMessageId && 
                                  streamingResponse
                // Use streaming response only for the current message, otherwise use saved content
                const displayContent = isStreaming ? streamingResponse : msg.content
                
                return (
                  <motion.div
                    key={msg.message_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                    className={`max-w-3xl p-4 ${
                      msg.role === 'user'
                        ? 'bg-[#2d2d2d] text-[#e8e8e8] rounded-3xl px-4 py-3 whitespace-pre-wrap'
                        : 'text-[#e8e8e8]'
                    }`}
                    style={{ 
                      fontFamily: 'ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif',
                      fontSize: '16px',
                      lineHeight: '1.6'
                    }}
                    >
                      {msg.role === 'user' ? (
                        <>{displayContent || (isStreaming ? '...' : '')}</>
                      ) : (
                        <MarkdownRenderer content={displayContent || (isStreaming ? '...' : '')} />
                      )}
                      {isStreaming && (
                        <span className="inline-block w-2 h-4 bg-orange-500 ml-1 animate-pulse" />
                      )}
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          )}
          
          {/* Prominent Risk Alert (3 seconds) */}
          {showRiskAlert && (
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                className="bg-gradient-to-br from-red-600 via-orange-500 to-yellow-500 rounded-3xl p-8 shadow-2xl max-w-2xl w-full text-white"
              >
                <h2 className="text-4xl font-bold mb-6 text-center" style={{ fontFamily: 'system-ui, sans-serif' }}>
                  DISEASE RISK ASSESSMENT
                </h2>
                <div className="grid grid-cols-3 gap-6 mb-6">
                  <div className="text-center bg-white/20 rounded-2xl p-4 backdrop-blur-sm">
                    <div className="text-5xl font-bold mb-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                      {showRiskAlert.late_blight.toFixed(0)}%
                    </div>
                    <div className="text-lg font-semibold mb-1" style={{ fontFamily: 'system-ui, sans-serif' }}>Late Blight</div>
                    <div className="text-sm opacity-90" style={{ fontFamily: 'system-ui, sans-serif' }}>
                      {showRiskAlert.late_blight_level.toUpperCase()}
                    </div>
                  </div>
                  <div className="text-center bg-white/20 rounded-2xl p-4 backdrop-blur-sm">
                    <div className="text-5xl font-bold mb-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                      {showRiskAlert.early_blight.toFixed(0)}%
                    </div>
                    <div className="text-lg font-semibold mb-1" style={{ fontFamily: 'system-ui, sans-serif' }}>Early Blight</div>
                    <div className="text-sm opacity-90" style={{ fontFamily: 'system-ui, sans-serif' }}>
                      {showRiskAlert.early_blight_level.toUpperCase()}
                    </div>
                  </div>
                  <div className="text-center bg-white/20 rounded-2xl p-4 backdrop-blur-sm">
                    <div className="text-5xl font-bold mb-2" style={{ fontFamily: 'system-ui, sans-serif' }}>
                      {showRiskAlert.overall.toFixed(0)}%
                    </div>
                    <div className="text-lg font-semibold mb-1" style={{ fontFamily: 'system-ui, sans-serif' }}>Overall Risk</div>
                    <div className="text-sm opacity-90" style={{ fontFamily: 'system-ui, sans-serif' }}>
                      {showRiskAlert.overall >= 70 ? 'HIGH' : showRiskAlert.overall >= 40 ? 'MODERATE' : 'LOW'}
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
          
          {/* Status Message - Show natural language updates without progress bar */}
          {currentProgress && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="flex justify-start mb-4"
            >
              <div className="bg-gradient-to-r from-[#2d2d2d] to-[#353535] border border-[#4a4a4a] rounded-2xl p-6 shadow-2xl max-w-2xl w-full">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className="relative">
                      <div className="w-3 h-3 bg-orange-400 rounded-full animate-pulse"></div>
                      <div className="absolute inset-0 w-3 h-3 bg-orange-400 rounded-full animate-ping opacity-75"></div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-[#e8e8e8] font-normal text-base leading-relaxed" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                      {currentProgress.message}
                    </div>
                    {currentProgress.stage === 'collect_weather' && (
                      <div className="text-[#a8a8a8] text-sm mt-1" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                        🌍 Collecting weather data...
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          
          {/* Final Risk Percentage Display */}
          {finalRiskPercentage && (
            <div className="flex justify-start mb-4">
              <div className="bg-[#2d2d2d] border border-[#3a3a3a] rounded-2xl p-6 shadow-xl max-w-2xl w-full">
                <h3 className="text-2xl font-semibold text-[#e8e8e8] mb-4" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                  FINAL RISK ASSESSMENT
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-red-400 mb-2" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                      {finalRiskPercentage.late_blight.toFixed(0)}%
                    </div>
                    <div className="text-sm text-[#b8b8b8]" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>Late Blight Risk</div>
                  </div>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-orange-400 mb-2" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                      {finalRiskPercentage.early_blight.toFixed(0)}%
                    </div>
                    <div className="text-sm text-[#b8b8b8]" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>Early Blight Risk</div>
                  </div>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-[#e8e8e8] mb-2" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                      {finalRiskPercentage.overall.toFixed(0)}%
                    </div>
                    <div className="text-sm text-[#b8b8b8]" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>Overall Risk</div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Chart Agent - Comprehensive Visualizations */}
          {chartData && (
            <div className="flex justify-start mb-4">
              <div className="w-full max-w-6xl">
                <ChartAgent chartData={chartData} />
              </div>
            </div>
          )}
          
          {loading && !currentProgress && (
            <div className="flex justify-start">
              <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl p-4 shadow-md">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-[#3a3a3a] p-4 bg-[#1a1a1a]">
          {/* Image Preview */}
          {imagePreview && (
            <div className="mb-4 relative inline-block">
              <img
                src={imagePreview}
                alt="Preview"
                className="max-w-xs max-h-48 rounded border-2 border-orange/30"
              />
              <button
                onClick={handleRemoveImage}
                className="absolute top-0 right-0 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600"
              >
                ×
              </button>
            </div>
          )}

          {/* Image Upload Options */}
          <AnimatePresence>
            {showImageOptions && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="mb-4 p-4 bg-white/80 backdrop-blur-sm border border-gray-300 rounded-2xl shadow-lg"
              >
                <div className="flex gap-4">
                  <button
                    onClick={handleCameraCapture}
                    className="flex-1 px-4 py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all shadow-md"
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  >
                    📷 Take Photo
                  </button>
                  <button
                    onClick={handleFileUpload}
                    className="flex-1 px-4 py-3 bg-white border-2 border-gray-900 text-gray-900 rounded-full font-medium hover:bg-gray-50 transition-all shadow-md"
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  >
                    📁 Import from Files
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Hidden file inputs */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleImageSelect(file)
            }}
          />
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleImageSelect(file)
            }}
          />

          <form onSubmit={handleSend} className="flex gap-2">
            <div className="flex-1 flex flex-col gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value)
                  e.target.style.height = 'auto'
                  e.target.style.height = `${e.target.scrollHeight}px`
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend(e)
                  }
                }}
                placeholder={selectedImage ? "Add a message (optional)..." : "Type your message..."}
                rows={1}
                className="px-4 py-3 bg-[#2d2d2d] border-2 border-[#3a3a3a] rounded-full focus:outline-none focus:border-[#4a4a4a] text-[#e8e8e8] placeholder-[#808080] resize-none smooth-transition shadow-sm"
              style={{ fontFamily: 'system-ui, sans-serif' }}
              />
              {streamingStage && (
                <div className="text-xs text-[#c4c4c4]" style={{ fontFamily: 'ui-sans-serif, -apple-system, system-ui' }}>
                  {streamingStage === 'loading_context' && 'Loading context...'}
                  {streamingStage === 'routing' && 'Routing to agent...'}
                  {streamingStage === 'diagnosing' && 'Analyzing image...'}
                  {streamingStage === 'predicting' && 'Generating prediction...'}
                </div>
              )}
            </div>
            <div className="flex flex-col gap-2">
              <button
                type="button"
                onClick={() => setShowImageOptions(!showImageOptions)}
                className="px-4 py-3 bg-[#2d2d2d] border-2 border-[#3a3a3a] rounded-full hover:border-[#4a4a4a] transition-all text-[#e8e8e8] shadow-sm"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                📷
              </button>
              <button
                type="submit"
                disabled={(!input.trim() && !selectedImage) || loading}
                className="px-6 py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed smooth-transition shadow-lg"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

