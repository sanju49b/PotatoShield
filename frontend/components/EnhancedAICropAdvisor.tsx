'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface EnhancedAICropAdvisorProps {
  location: string
  sowingDate: string
  growthStage: string
  daysAfterPlanting: number
  currentRisks?: {
    late_blight?: number
    early_blight?: number
    overall?: number
  }
}

export default function EnhancedAICropAdvisor({
  location,
  sowingDate,
  growthStage,
  daysAfterPlanting,
  currentRisks
}: EnhancedAICropAdvisorProps) {
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleQuickQuestion = (question: string) => {
    handleSend(question)
  }

  const handleSend = async (customQuestion?: string) => {
    const questionText = customQuestion || input.trim()
    if (!questionText || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: questionText }])
    setLoading(true)

    try {
      // Call our secure backend API route (uses server-side OPENAI_API_KEY)
      const response = await fetch('/api/ai-advisor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: questionText,
          context: {
            location,
            sowingDate,
            growthStage,
            daysAfterPlanting,
            currentRisks
          }
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      const aiResponse = data.response || 'I apologize, but I couldn\'t generate a response. Please try again.'

      setMessages(prev => [...prev, { role: 'assistant', content: aiResponse }])
    } catch (error) {
      console.error('AI Crop Advisor error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `I'm having trouble connecting right now. Based on your field context (${location}, Day ${daysAfterPlanting}, ${growthStage} stage), here's what I can tell you:\n\n${
          currentRisks && currentRisks.late_blight && currentRisks.late_blight > 75
            ? '⚠️ Your Late Blight risk is critically high. Apply fungicide immediately and monitor daily.'
            : currentRisks && currentRisks.late_blight && currentRisks.late_blight > 50
            ? '🟡 Your Late Blight risk is elevated. Prepare preventive measures and watch weather closely.'
            : '✅ Your disease risk is currently manageable. Continue regular monitoring.'
        }`
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-[#2d2d2d] to-[#1a1a1a] rounded-xl border border-orange-500/30 shadow-2xl">
      {/* Header - Colorful */}
      <div className="p-4 border-b border-orange-500/30 bg-gradient-to-r from-orange-500 to-yellow-500">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2 drop-shadow-lg">
          💬 AI Crop Advisor
        </h2>
        <div className="flex items-center gap-2 mt-2 text-xs text-white/90 bg-white/20 px-2 py-1 rounded-full w-fit backdrop-blur-sm">
          <span>📍 {location}</span>
          <span>•</span>
          <span>🌱 Day {daysAfterPlanting}</span>
          <span>•</span>
          <span>📊 {growthStage}</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '400px' }}>
        {messages.length === 0 ? (
          <div className="text-center text-[#808080] py-8">
            <div className="text-5xl mb-4">🤖</div>
            <p className="text-sm text-[#e8e8e8] mb-2">Hi! I'm your AI Crop Advisor</p>
            <p className="text-xs text-[#b8b8b8]">I have your field context and can provide personalized advice</p>
            <div className="mt-4 text-xs text-[#b8b8b8] bg-blue-500/10 rounded-lg p-3 border border-blue-500/30">
              <p className="text-blue-300">💡 <strong>Context Loaded:</strong></p>
              <p className="mt-1">Location: {location}</p>
              <p>Growth Stage: {growthStage} (Day {daysAfterPlanting})</p>
              {currentRisks && (
                <p className="mt-1 text-orange-300">
                  {currentRisks.late_blight && currentRisks.late_blight > 75 ? '⚠️ High risk detected!' : '✓ Risks monitored'}
                </p>
              )}
            </div>
          </div>
        ) : (
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-lg'
                      : 'bg-[#3a3a3a] text-[#e8e8e8] border border-[#4a4a4a]'
                  }`}
                  style={{
                    fontFamily: 'ui-sans-serif, -apple-system, system-ui',
                    fontSize: '14px',
                    lineHeight: '1.6'
                  }}
                >
                  {msg.content}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#3a3a3a] rounded-lg p-3 border border-[#4a4a4a]">
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
        <div className="p-4 border-t border-orange-500/30 bg-[#2d2d2d]">
          <p className="text-xs text-[#808080] mb-2">Quick Questions:</p>
          <div className="grid grid-cols-2 gap-2">
            {quickQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleQuickQuestion(question)}
                disabled={loading}
                className="px-3 py-2 bg-gradient-to-r from-orange-500/20 to-yellow-500/20 border border-orange-500/30 text-[#e8e8e8] rounded-lg hover:from-orange-500/30 hover:to-yellow-500/30 transition-all text-xs text-left disabled:opacity-50"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="p-4 border-t border-orange-500/30 bg-[#2d2d2d]">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="Ask about your crop..."
            rows={2}
            className="flex-1 px-3 py-2 bg-[#3a3a3a] border border-orange-500/30 rounded-lg focus:outline-none focus:border-orange-500 text-[#e8e8e8] placeholder-[#808080] resize-none text-sm"
            style={{ fontFamily: 'system-ui, sans-serif' }}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:from-orange-600 hover:to-orange-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium shadow-lg"
          >
            💬
          </button>
        </div>
        <p className="text-xs text-[#606060] mt-2 flex items-center gap-1">
          <span>🤖</span>
          <span>Powered by OpenAI GPT-4 • Secure server-side processing</span>
        </p>
      </form>
    </div>
  )
}

