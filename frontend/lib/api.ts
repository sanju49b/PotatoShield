import axios from 'axios'

const STORAGE_KEY_API_BASE = 'potato_api_base_url'
const DEFAULT_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/** Get API base URL: localStorage override (when user picked a backend) or build default. */
export function getApiBaseUrl(): string {
  if (typeof window === 'undefined') return DEFAULT_API_URL
  const stored = localStorage.getItem(STORAGE_KEY_API_BASE)
  if (stored && stored.trim()) return stored.trim()
  return DEFAULT_API_URL
}

/** Set API base URL (e.g. when user picks Local vs Staging). Persists in localStorage. */
export function setApiBaseUrl(url: string): void {
  if (typeof window === 'undefined') return
  const value = url.trim() || DEFAULT_API_URL
  if (value) localStorage.setItem(STORAGE_KEY_API_BASE, value)
  else localStorage.removeItem(STORAGE_KEY_API_BASE)
}

/** Clear user's backend override so app uses default (e.g. current deployment's API). */
export function clearApiBaseUrlOverride(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(STORAGE_KEY_API_BASE)
}

const api = axios.create({
  baseURL: DEFAULT_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Use chosen API URL per request and add token
api.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl()
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

export interface User {
  user_id: string
  email: string
  username?: string
  created_at: string
  fields?: Field[]
}

export interface Field {
  field_id: string
  user_id: string
  location: string
  crop_type: string
  sowing_date: string
  area_hectares?: number
  latitude?: number
  longitude?: number
  is_active: boolean
  created_at: string
}

export interface Message {
  message_id: string
  conversation_id: string
  role: string
  content: string
  metadata?: Record<string, any>
  created_at: string
}

export interface Conversation {
  conversation_id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
}

export interface ConversationsResponse {
  success: boolean
  conversations: Conversation[]
}

export interface MessagesResponse {
  success: boolean
  messages: Message[]
}

export const authAPI = {
  register: async (email: string, password: string, username?: string) => {
    const response = await api.post('/api/auth/register', { email, password, username })
    return response.data
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password })
    if (response.data.success && typeof window !== 'undefined') {
      localStorage.setItem('auth_token', response.data.token)
      localStorage.setItem('user_id', response.data.user_id)
      localStorage.setItem('email', response.data.email)
    }
    return response.data
  },

  sendOTP: async (email: string) => {
    const response = await api.post('/api/auth/send-otp', { email })
    return response.data
  },

  verifyOTP: async (email: string, otp_code: string) => {
    const response = await api.post('/api/auth/verify-otp', { email, otp_code })
    if (response.data.success && typeof window !== 'undefined') {
      localStorage.setItem('auth_token', response.data.token)
      localStorage.setItem('user_id', response.data.user_id)
      localStorage.setItem('email', response.data.email)
    }
    return response.data
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('email')
    }
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },

  createField: async (fieldData: {
    location: string
    sowing_date: string
    area_hectares?: number
    latitude?: number
    longitude?: number
  }) => {
    const response = await api.post('/api/fields', fieldData)
    return response.data
  },

  updateFieldData: async (fieldData: {
    field_id?: string
    location?: string
    sowing_date?: string
    area_hectares?: number
    latitude?: number
    longitude?: number
  }) => {
    const response = await api.put('/api/fields', fieldData)
    return response.data
  },
}

export const fieldAPI = {
  create: async (
    location: string,
    sowing_date: string,
    area_hectares?: number,
    latitude?: number,
    longitude?: number
  ) => {
    const response = await api.post('/api/fields', {
      location,
      sowing_date,
      area_hectares,
      latitude,
      longitude,
    })
    return response.data
  },
}

export const conversationAPI = {
  create: async (title?: string): Promise<{ success: boolean; conversation_id: string }> => {
    const response = await api.post('/api/conversations', { title })
    return response.data
  },

  getAll: async (): Promise<ConversationsResponse> => {
    const response = await api.get('/api/conversations')
    return response.data
  },

  getMessages: async (conversation_id: string): Promise<MessagesResponse> => {
    const response = await api.get(`/api/conversations/${conversation_id}/messages`)
    return response.data
  },

  addMessage: async (
    conversation_id: string,
    role: string,
    content: string,
    metadata?: Record<string, any>
  ) => {
    const response = await api.post(`/api/conversations/${conversation_id}/messages`, {
      role,
      content,
      metadata,
    })
    return response.data
  },
}

export const chatAPI = {
  chat: async (
    message: string,
    conversation_id?: string,
    image_data?: string,
    agent?: 'diagnostic' | 'predictive',
    preferred_language?: string
  ) => {
    const response = await api.post('/api/chat', {
      message,
      conversation_id,
      image_data,
      agent,
      preferred_language,
    })
    return response.data
  },

  chatStream: async function* (
    message: string,
    conversation_id?: string,
    image_data?: string,
    agent?: 'diagnostic' | 'predictive',
    preferred_language?: string
  ): AsyncGenerator<any, void, unknown> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    
    console.log('[FRONTEND API] Starting SSE stream request...')
    
    const response = await fetch(`${getApiBaseUrl()}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        message,
        conversation_id,
        image_data,
        agent,
        preferred_language,
      }),
    })

    if (!response.ok) {
      console.error('[FRONTEND API] Stream request failed:', response.status, response.statusText)
      throw new Error(`Chat stream failed: ${response.statusText}`)
    }

    console.log('[FRONTEND API] Stream response received, status:', response.status)
    console.log('[FRONTEND API] Content-Type:', response.headers.get('Content-Type'))

    const reader = response.body?.getReader()
    const decoder = new TextDecoder('utf-8')

    if (!reader) {
      throw new Error('No response body reader available')
    }

    let buffer = ''
    let eventCount = 0
    
    console.log('[FRONTEND API] Starting to read stream...')
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        console.log('[FRONTEND API] Stream ended. Total events:', eventCount)
        break
      }

      // Decode chunk and add to buffer
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      
      // Process complete lines
      const lines = buffer.split('\n')
      // Keep the last incomplete line in buffer
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmedLine = line.trim()
        
        // Skip empty lines
        if (trimmedLine === '') continue
        
        // Process SSE data lines
        if (trimmedLine.startsWith('data: ')) {
          try {
            const jsonStr = trimmedLine.slice(6).trim()
            if (jsonStr) {
              const data = JSON.parse(jsonStr)
              eventCount++
              
              // Debug log for data_collection_progress events
              if (data.type === 'data_collection_progress') {
                console.log(`[FRONTEND API] Event #${eventCount} - data_collection_progress:`, {
                  message: data.message?.substring(0, 50),
                  stage: data.stage,
                  fullData: data
                })
              } else if (eventCount <= 5) {
                console.log(`[FRONTEND API] Event #${eventCount}:`, data.type, data)
              }
              
              yield data
            }
          } catch (e) {
            console.error('[FRONTEND API] Failed to parse SSE data:', e, 'Line:', trimmedLine)
          }
        } else if (trimmedLine.startsWith('event: ')) {
          // Handle event type (optional SSE field)
          console.log('[FRONTEND API] SSE event type:', trimmedLine.slice(7))
        } else if (trimmedLine.startsWith('id: ')) {
          // Handle event ID (optional SSE field)
          console.log('[FRONTEND API] SSE event ID:', trimmedLine.slice(4))
        } else {
          // Log unexpected lines for debugging
          if (trimmedLine.length > 0) {
            console.warn('[FRONTEND API] Unexpected SSE line:', trimmedLine.substring(0, 100))
          }
        }
      }
    }
    
    // Process any remaining buffer
    if (buffer.trim()) {
      console.warn('[FRONTEND API] Unprocessed buffer at end:', buffer.substring(0, 100))
    }
  },
}

export default api
