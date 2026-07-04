'use client'

import { useState, useRef, useEffect } from 'react'
import { chatAPI } from '@/lib/api'
import MarkdownRenderer from './MarkdownRenderer'
import { motion, AnimatePresence } from 'framer-motion'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function DashboardChatAssistant({ conversationId, dashboardContext, mode, initialQuestion }: { conversationId?: string; dashboardContext?: any; mode?: 'diagnostic' | 'predictive'; initialQuestion?: string }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const quickQuestions = [
    "What should I do today?",
    "When to apply fungicide?",
    "Is my crop at risk?",
    "Explain Late Blight"
  ]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Prefill an initial question when provided (once)
  useEffect(() => {
    if (initialQuestion && messages.length === 0 && !input) {
      setInput(initialQuestion)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuestion])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleQuickQuestion = (question: string) => {
    setInput(question)
    inputRef.current?.focus()
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    // Add assistant message placeholder for streaming
    const assistantMessageIndex = messages.length + 1
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    try {
      // Add context from dashboard if available
      const agentHint = mode ? `[Agent:${mode}] ` : ''
      const contextPrefix = dashboardContext
        ? `Context: Location=${dashboardContext.location}, Day=${dashboardContext.day || 1}, Late=${dashboardContext.late_blight || 0}%, Early=${dashboardContext.early_blight || 0}%, Overall=${dashboardContext.overall || 0}%. `
        : ''
      const contextualizedMessage = `${agentHint}${contextPrefix}${userMessage}`.trim()

      // Use streaming API for multi-agent workflow
      let fullResponse = ''
      for await (const event of chatAPI.chatStream(contextualizedMessage, conversationId, undefined, mode)) {
        if (event.type === 'status' || event.type === 'diagnostic_thinking' || event.type === 'predictive_progress') {
          // Show progress updates (can be displayed in UI if needed)
          continue
        } else if (event.type === 'diagnostic_stream' || event.type === 'stream_char') {
          // Stream character-by-character
          const chunk = event.chunk || event.message || ''
          if (chunk) {
            fullResponse += chunk
            setMessages(prev => {
              const updated = [...prev]
              if (updated[assistantMessageIndex]) {
                updated[assistantMessageIndex] = { role: 'assistant', content: fullResponse }
              }
              return updated
            })
          }
        } else if (event.type === 'report' || event.type === 'final_report') {
          // Final report
          const content = event.content || event.report || event.message || ''
          if (content) {
            fullResponse = content
            setMessages(prev => {
              const updated = [...prev]
              if (updated[assistantMessageIndex]) {
                updated[assistantMessageIndex] = { role: 'assistant', content: fullResponse }
              }
              return updated
            })
          }
        } else if (event.type === 'done') {
          break
        } else if (event.type === 'error') {
          setMessages(prev => {
            const updated = [...prev]
            if (updated[assistantMessageIndex]) {
              updated[assistantMessageIndex] = { role: 'assistant', content: `Error: ${event.message || 'Something went wrong'}` }
            }
            return updated
          })
          break
        }
      }

      // Ensure final message is set
      if (fullResponse) {
        setMessages(prev => {
          const updated = [...prev]
          updated[assistantMessageIndex] = { role: 'assistant', content: fullResponse }
          return updated
        })
      }
    } catch (error: any) {
      console.error('Chat error:', error)
      setMessages(prev => {
        const updated = [...prev]
        updated[assistantMessageIndex] = {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        }
        return updated
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#2d2d2d] rounded-xl border border-[#3a3a3a]">
      {/* Header */}
      <div className="p-4 border-b border-[#3a3a3a]">
        <h2 className="text-xl font-semibold text-[#e8e8e8] flex items-center gap-2">
          💬 AI Crop Advisor
        </h2>
        <p className="text-xs text-[#808080] mt-1">Ask me anything about your crop health</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '400px' }}>
        {messages.length === 0 ? (
          <div className="text-center text-[#808080] py-8">
            <div className="text-4xl mb-4">🤖</div>
            <p className="text-sm">Ask me anything about your crops!</p>
            <p className="text-xs mt-2">Try the quick questions below</p>
          </div>
        ) : (
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-orange-500 text-white'
                      : 'bg-[#3a3a3a] text-[#e8e8e8]'
                  }`}
                  style={{
                    fontFamily: 'ui-sans-serif, -apple-system, system-ui',
                    fontSize: '14px',
                    lineHeight: '1.5'
                  }}
                >
                  {msg.role === 'user' ? (
                    <>{msg.content}</>
                  ) : (
                    <MarkdownRenderer content={msg.content} />
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#3a3a3a] rounded-lg p-3">
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

      {/* Quick Questions */}
      {messages.length === 0 && (
        <div className="p-4 border-t border-[#3a3a3a]">
          <p className="text-xs text-[#808080] mb-2">Quick Questions:</p>
          <div className="grid grid-cols-2 gap-2">
            {quickQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleQuickQuestion(question)}
                className="px-3 py-2 bg-[#3a3a3a] text-[#e8e8e8] rounded-lg hover:bg-[#4a4a4a] transition-colors text-xs text-left"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-[#3a3a3a]">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend(e)
              }
            }}
            placeholder="Ask a question..."
            rows={2}
            className="flex-1 px-3 py-2 bg-[#3a3a3a] border border-[#4a4a4a] rounded-lg focus:outline-none focus:border-orange-500 text-[#e8e8e8] placeholder-[#808080] resize-none text-sm"
            style={{ fontFamily: 'system-ui, sans-serif' }}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            💬
          </button>
        </div>
      </form>
    </div>
  )
}

