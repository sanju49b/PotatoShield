'use client'

import React, { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { chatAPI } from '@/lib/api'

export default function DiagnosticDashboardPage() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [streamingStage, setStreamingStage] = useState<string | null>(null)
  const [currentProgress, setCurrentProgress] = useState<{ message: string; stage: string } | null>(null)
  const [assistantContent, setAssistantContent] = useState<string>('')
  const [diagnosis, setDiagnosis] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const [scrollY, setScrollY] = useState(0)

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

  const handleFileUpload = () => fileInputRef.current?.click()
  const handleCameraCapture = () => cameraInputRef.current?.click()
  const handleSelectFile = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target?.result as string
      setSelectedImage(base64)
      setImagePreview(base64)
    }
    reader.readAsDataURL(file)
  }

  const runDiagnosis = async () => {
    if (!selectedImage || loading) return
    setLoading(true)
    setAssistantContent('')
    setDiagnosis(null)
    setCurrentProgress(null)
    setStreamingStage('diagnosing')

    try {
      for await (const event of chatAPI.chatStream('Please diagnose this potato leaf image', undefined, selectedImage, 'diagnostic')) {
        if (event.type === 'status') {
          setStreamingStage(event.stage)
          if (event.message && event.stage !== 'collect_weather') {
            setCurrentProgress({ message: event.message, stage: event.stage })
          }
        } else if (event.type === 'diagnostic_start' || event.type === 'diagnostic_thinking' || event.type === 'diagnostic_stream') {
          const chunk = event.message || event.chunk || ''
          if (chunk) setAssistantContent((prev) => prev + chunk)
        } else if (event.type === 'diagnostic_progress') {
          if (event.message) setAssistantContent((prev) => prev + `\n${event.message}\n`)
        } else if (event.type === 'diagnostic' || event.type === 'diagnostic_result') {
          setDiagnosis(event.data || event.diagnostic || event)
          setCurrentProgress({ message: 'Diagnosis complete', stage: 'complete' })
          setTimeout(() => setCurrentProgress(null), 1200)
        } else if (event.type === 'error') {
          setAssistantContent((prev) => prev + `\n❌ ${event.message}\n`)
        } else if (event.type === 'done') {
          break
        }
      }
    } finally {
      setLoading(false)
      setStreamingStage(null)
    }
  }

  return (
    <div className="min-h-screen bg-[#0e0e0f] text-[#e8e8e8] relative overflow-hidden">
      {/* Animated background */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div
          className="absolute -top-24 -left-24 w-[420px] h-[420px] bg-gradient-to-br from-rose-600/25 via-fuchsia-500/15 to-cyan-500/20 blur-3xl rounded-full animate-float-slow will-change-transform"
          style={{ transform: `translate3d(0, ${-scrollY * 0.08}px, 0)` }}
        />
        <div
          className="absolute bottom-[-120px] left-1/2 -translate-x-1/2 w-[520px] h-[520px] bg-gradient-to-tr from-emerald-500/15 via-sky-500/20 to-purple-600/15 blur-3xl rounded-full animate-orbit will-change-transform"
          style={{ transform: `translate3d(-50%, ${-scrollY * 0.03}px, 0)` }}
        />
        <div
          className="absolute -right-24 top-1/3 w-[420px] h-[420px] bg-gradient-to-tr from-amber-500/20 via-pink-500/15 to-red-600/20 blur-3xl rounded-full animate-float-slower will-change-transform"
          style={{ transform: `translate3d(0, ${-scrollY * 0.06}px, 0)` }}
        />
      </div>

      {/* Header */}
      <header className="bg-gradient-to-r from-rose-600 via-fuchsia-500 to-cyan-500 shadow-lg border-b border-white/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">🧠 Diagnostic Agent Dashboard</h1>
              <div className="mt-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 border border-white/30 text-white/90 text-xs backdrop-blur-md">
                  <span className="animate-pulse inline-block w-2 h-2 rounded-full bg-lime-300"></span>
                  <span>Diagnostic</span>
                  <span className="text-white/60">with</span>
                  <span className="px-2 py-0.5 rounded bg-black/20 border border-white/20">Multi‑Agent</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => window.open('/production-dashboard', '_blank')}
                className="px-4 py-2 bg-black/20 hover:bg-black/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30"
                title="Open in new tab"
              >
                📊 Predictive
              </button>
              <button
                onClick={() => window.open('/chat', '_blank')}
                className="px-4 py-2 bg-black/20 hover:bg-black/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30"
                title="Open in new tab"
              >
                💬 Chat
              </button>
              <button
                onClick={() => window.open('/welcome', '_blank')}
                className="px-4 py-2 bg-black/20 hover:bg-black/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30"
                title="Open in new tab"
              >
                🏠 Home
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="container mx-auto px-6 py-6 space-y-6">
        {/* Uploader */}
        <section className="bg-[#151515]/90 rounded-xl p-6 border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.45)] backdrop-blur-md">
          <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4">📷 Upload or Capture Leaf Image</h2>
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
              <div
                className="relative border-2 border-dashed border-[#3a3a3a] rounded-2xl p-6 h-64 flex items-center justify-center bg-[#101010] hover:bg-[#121212] transition-colors"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault()
                  const file = e.dataTransfer.files?.[0]
                  if (file) handleSelectFile(file)
                }}
              >
                {!imagePreview ? (
                  <div className="text-center">
                    <div className="text-5xl mb-3">🖼️</div>
                    <p className="text-[#b8b8b8]">Drag & drop an image here, or use the buttons</p>
                  </div>
                ) : (
                  <img src={imagePreview} alt="Preview" className="max-h-56 rounded-xl border border-[#2f2f2f] shadow-lg" />
                )}
              </div>
              <div className="flex gap-3 mt-4">
                <button
                  onClick={handleFileUpload}
                  className="px-4 py-2 rounded-xl bg-white text-black font-semibold hover:bg-gray-100 transition-colors"
                >
                  📁 Choose File
                </button>
                <button
                  onClick={handleCameraCapture}
                  className="px-4 py-2 rounded-xl bg-black/40 text-white border border-white/20 hover:bg-black/60 transition-colors"
                >
                  📷 Use Camera
                </button>
                <button
                  onClick={runDiagnosis}
                  disabled={!selectedImage || loading}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-rose-500 to-fuchsia-600 text-white font-semibold hover:from-rose-600 hover:to-fuchsia-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Analyzing…' : 'Analyze Image'}
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleSelectFile(file)
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
                  if (file) handleSelectFile(file)
                }}
              />
            </div>

            {/* Status / Narration */}
            <div className="w-full md:w-1/2 bg-[#111111] border border-[#2b2b2b] rounded-2xl p-4">
              <h3 className="text-lg font-semibold mb-3">🧪 Live Analysis</h3>
              <div className="min-h-[180px] text-sm whitespace-pre-wrap leading-6">
                {assistantContent || 'No output yet. Click “Analyze Image”.'}
              </div>
              <AnimatePresence>
                {currentProgress && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mt-3 text-xs text-[#c4c4c4]"
                  >
                    <span className="inline-block w-2 h-2 bg-fuchsia-400 rounded-full mr-2 animate-pulse"></span>
                    {currentProgress.message}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </section>

        {/* Result */}
        {diagnosis && (
          <section className="bg-[#151515]/90 rounded-xl p-6 border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.45)] backdrop-blur-md">
            <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4">✅ Diagnosis</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-[#1b1b1b] rounded-xl p-4 border border-[#2a2a2a]">
                <div className="text-sm text-[#b8b8b8] mb-1">Disease</div>
                <div className="text-2xl font-bold">{diagnosis.disease_type || 'Unknown'}</div>
              </div>
              <div className="bg-[#1b1b1b] rounded-xl p-4 border border-[#2a2a2a]">
                <div className="text-sm text-[#b8b8b8] mb-1">Confidence</div>
                <div className="text-2xl font-bold text-emerald-400">
                  {Math.round(diagnosis.confidence_percentage || diagnosis.confidence || 0)}%
                </div>
              </div>
              <div className="bg-[#1b1b1b] rounded-xl p-4 border border-[#2a2a2a]">
                <div className="text-sm text-[#b8b8b8] mb-1">Severity</div>
                <div className="text-2xl font-bold text-rose-400">{(diagnosis.severity || 'Unknown').toUpperCase()}</div>
              </div>
            </div>
            {diagnosis.summary && (
              <div className="mt-4 bg-[#111111] border border-[#2b2b2b] rounded-2xl p-4">
                <div className="text-sm text-[#b8b8b8] mb-1">Summary</div>
                <div className="text-[#e8e8e8]">{diagnosis.summary}</div>
              </div>
            )}
            {diagnosis.recommendations && (
              <div className="mt-4 bg-[#111111] border border-[#2b2b2b] rounded-2xl p-4">
                <div className="text-sm text-[#b8b8b8] mb-2">Recommendations</div>
                <div className="text-[#e8e8e8] whitespace-pre-wrap">{diagnosis.recommendations}</div>
              </div>
            )}
          </section>
        )}

        {/* Recommendations Section */}
        {diagnosis && (
          <section className="bg-[#151515]/90 rounded-xl p-6 border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.45)] backdrop-blur-md">
            <h2 className="text-2xl font-bold text-[#e8e8e8] mb-6 flex items-center gap-3">
              <span className="text-3xl">💊</span>
              <span>Treatment Recommendations & Research</span>
            </h2>

            {/* Key Visual Indicators */}
            {diagnosis.key_visual_indicators && diagnosis.key_visual_indicators.length > 0 && (
              <div className="mb-6 p-5 rounded-xl bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 border border-blue-500/20">
                <h3 className="text-lg font-semibold text-blue-300 mb-3 flex items-center gap-2">
                  <span>🔍</span>
                  Key Visual Indicators
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {diagnosis.key_visual_indicators.map((indicator: string, idx: number) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="flex items-start gap-2 p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                    >
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <span className="text-[#e8e8e8] text-sm">{indicator}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Base Recommendations */}
            {diagnosis.recommendations && (
              <div className="mb-6 p-5 rounded-xl bg-gradient-to-br from-emerald-500/10 via-teal-500/10 to-cyan-500/10 border border-emerald-500/20">
                <h3 className="text-lg font-semibold text-emerald-300 mb-3 flex items-center gap-2">
                  <span>💡</span>
                  Immediate Recommendations
                </h3>
                <div className="text-[#e8e8e8] leading-relaxed whitespace-pre-wrap bg-black/20 p-4 rounded-lg border border-emerald-500/10">
                  {diagnosis.recommendations}
                </div>
              </div>
            )}

            {/* Tavily Recommendations */}
            {diagnosis.tavily_data && (
              <div className="space-y-6">
                {/* Treatment & Management Recommendations */}
                {diagnosis.tavily_data.recommendations && diagnosis.tavily_data.recommendations.length > 0 && (
                  <div className="p-5 rounded-xl bg-gradient-to-br from-rose-500/10 via-pink-500/10 to-fuchsia-500/10 border border-rose-500/20">
                    <h3 className="text-lg font-semibold text-rose-300 mb-4 flex items-center gap-2">
                      <span>🧪</span>
                      Treatment & Management Recommendations
                    </h3>
                    <div className="space-y-4">
                      {diagnosis.tavily_data.recommendations.map((rec: any, idx: number) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="p-4 rounded-lg bg-black/20 border border-rose-500/10 hover:border-rose-500/30 transition-all"
                        >
                          {rec.title && (
                            <h4 className="text-base font-semibold text-rose-200 mb-2">{rec.title}</h4>
                          )}
                          {rec.summary && (
                            <p className="text-[#e8e8e8] text-sm mb-3 leading-relaxed">{rec.summary}</p>
                          )}
                          {rec.key_points && rec.key_points.length > 0 && (
                            <ul className="space-y-2 mb-3">
                              {rec.key_points.map((point: string, pointIdx: number) => (
                                <li key={pointIdx} className="flex items-start gap-2 text-sm text-[#d0d0d0]">
                                  <span className="text-rose-400 mt-1">•</span>
                                  <span>{point}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                          {rec.url && (
                            <a
                              href={rec.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 text-xs text-rose-300 hover:text-rose-200 underline"
                            >
                              <span>🔗</span>
                              <span>{rec.source_name || 'View Source'}</span>
                            </a>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Historical Context */}
                {diagnosis.tavily_data.historical_context && diagnosis.tavily_data.historical_context.length > 0 && (
                  <div className="p-5 rounded-xl bg-gradient-to-br from-amber-500/10 via-orange-500/10 to-red-500/10 border border-amber-500/20">
                    <h3 className="text-lg font-semibold text-amber-300 mb-4 flex items-center gap-2">
                      <span>📚</span>
                      Historical Outbreak Analysis
                    </h3>
                    <div className="space-y-4">
                      {diagnosis.tavily_data.historical_context.map((hist: any, idx: number) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="p-4 rounded-lg bg-black/20 border border-amber-500/10 hover:border-amber-500/30 transition-all"
                        >
                          {hist.outbreak_date && (
                            <div className="mb-2">
                              <span className="inline-block px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold border border-amber-500/30">
                                📅 {hist.outbreak_date}
                              </span>
                            </div>
                          )}
                          {hist.historical_weather && (
                            <div className="mb-3 p-3 rounded-lg bg-black/30 border border-amber-500/10">
                              <p className="text-xs text-amber-200/80 mb-2 font-semibold">Historical Weather Conditions:</p>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs text-[#d0d0d0]">
                                {hist.historical_weather.temperature && (
                                  <div>🌡️ Temp: {hist.historical_weather.temperature}</div>
                                )}
                                {hist.historical_weather.humidity && (
                                  <div>💧 Humidity: {hist.historical_weather.humidity}</div>
                                )}
                                {hist.historical_weather.rainfall && (
                                  <div>🌧️ Rainfall: {hist.historical_weather.rainfall}</div>
                                )}
                              </div>
                            </div>
                          )}
                          {hist.title && (
                            <h4 className="text-base font-semibold text-amber-200 mb-2">{hist.title}</h4>
                          )}
                          {hist.summary && (
                            <p className="text-[#e8e8e8] text-sm mb-3 leading-relaxed">{hist.summary}</p>
                          )}
                          {hist.key_points && hist.key_points.length > 0 && (
                            <ul className="space-y-2 mb-3">
                              {hist.key_points.map((point: string, pointIdx: number) => (
                                <li key={pointIdx} className="flex items-start gap-2 text-sm text-[#d0d0d0]">
                                  <span className="text-amber-400 mt-1">•</span>
                                  <span>{point}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                          {hist.url && (
                            <a
                              href={hist.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 text-xs text-amber-300 hover:text-amber-200 underline"
                            >
                              <span>🔗</span>
                              <span>{hist.source_name || 'View Source'}</span>
                            </a>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Preventive Measures */}
                {diagnosis.tavily_data.preventive_measures && diagnosis.tavily_data.preventive_measures.length > 0 && (
                  <div className="p-5 rounded-xl bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-violet-500/10 border border-indigo-500/20">
                    <h3 className="text-lg font-semibold text-indigo-300 mb-4 flex items-center gap-2">
                      <span>🛡️</span>
                      Preventive Measures
                    </h3>
                    <div className="space-y-4">
                      {diagnosis.tavily_data.preventive_measures.map((prev: any, idx: number) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="p-4 rounded-lg bg-black/20 border border-indigo-500/10 hover:border-indigo-500/30 transition-all"
                        >
                          {prev.title && (
                            <h4 className="text-base font-semibold text-indigo-200 mb-2">{prev.title}</h4>
                          )}
                          {prev.summary && (
                            <p className="text-[#e8e8e8] text-sm mb-3 leading-relaxed">{prev.summary}</p>
                          )}
                          {prev.key_points && prev.key_points.length > 0 && (
                            <ul className="space-y-2 mb-3">
                              {prev.key_points.map((point: string, pointIdx: number) => (
                                <li key={pointIdx} className="flex items-start gap-2 text-sm text-[#d0d0d0]">
                                  <span className="text-indigo-400 mt-1">•</span>
                                  <span>{point}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                          {prev.url && (
                            <a
                              href={prev.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 text-xs text-indigo-300 hover:text-indigo-200 underline"
                            >
                              <span>🔗</span>
                              <span>{prev.source_name || 'View Source'}</span>
                            </a>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Formatted Tavily Recommendations (Markdown) */}
            {diagnosis.tavily_recommendations && (
              <div className="mt-6 p-5 rounded-xl bg-gradient-to-br from-cyan-500/10 via-blue-500/10 to-teal-500/10 border border-cyan-500/20">
                <h3 className="text-lg font-semibold text-cyan-300 mb-4 flex items-center gap-2">
                  <span>📖</span>
                  Location-Specific Research & Treatment References
                </h3>
                <div className="bg-black/20 p-6 rounded-lg border border-cyan-500/10">
                  <div 
                    className="text-[#e8e8e8] leading-relaxed space-y-4"
                    dangerouslySetInnerHTML={{ 
                      __html: (() => {
                        const paragraphs = diagnosis.tavily_recommendations.split('\n\n')
                        return paragraphs
                          .map((para: string) => {
                            if (!para.trim()) return ''
                            let processedPara = para
                            // Headers
                            if (processedPara.startsWith('## ')) {
                              return `<h2 class="text-xl font-bold text-cyan-200 mt-6 mb-3 pb-2 border-b border-cyan-500/20">${processedPara.replace(/^##\s+/, '')}</h2>`
                            }
                            if (processedPara.startsWith('### ')) {
                              return `<h3 class="text-lg font-semibold text-cyan-300 mt-4 mb-2">${processedPara.replace(/^###\s+/, '')}</h3>`
                            }
                            // Links
                            processedPara = processedPara.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-cyan-300 hover:text-cyan-200 underline font-medium">$1</a>')
                            // Bold
                            processedPara = processedPara.replace(/\*\*(.*?)\*\*/g, '<strong class="text-cyan-200 font-semibold">$1</strong>')
                            // Italic
                            processedPara = processedPara.replace(/\*(.*?)\*/g, '<em class="text-cyan-300">$1</em>')
                            // Bullet points
                            if (processedPara.trim().startsWith('- ') || processedPara.trim().startsWith('* ')) {
                              const items = processedPara.split('\n').filter((line: string) => line.trim().startsWith('- ') || line.trim().startsWith('* '))
                              return `<ul class="list-disc space-y-2 ml-6 my-2">${items.map((item: string) => `<li class="text-sm text-[#d0d0d0]">${item.replace(/^[-*]\s+/, '')}</li>`).join('')}</ul>`
                            }
                            // Regular paragraph
                            return `<p class="text-sm leading-relaxed mb-3">${processedPara}</p>`
                          })
                          .filter((html: string) => html)
                          .join('')
                      })()
                    }}
                  />
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      {/* Global styles for animations */}
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

