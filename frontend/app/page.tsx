'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ScrollPotato from '@/components/ScrollPotato'
import { motion, useScroll, useTransform } from 'framer-motion'

export default function HomePage() {
  const router = useRouter()
  const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 })
  const { scrollYProgress } = useScroll()
  const opacity = useTransform(scrollYProgress, [0, 0.3], [1, 0])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPos({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden">
      {/* Custom Cursor */}
      <motion.div
        className="fixed pointer-events-none z-50 mix-blend-difference"
        style={{
          left: cursorPos.x,
          top: cursorPos.y,
        }}
        animate={{
          x: -10,
          y: -10,
        }}
        transition={{ type: 'spring', stiffness: 500, damping: 28 }}
      >
        <div className="w-5 h-5 border-2 border-gray-900 rounded-full opacity-90" />
        <motion.div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-gray-900 rounded-full"
          animate={{ scale: [1, 1.5, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </motion.div>

      {/* Hero Section */}
      <section className="relative min-h-screen w-full overflow-hidden" style={{ cursor: 'none' }}>
        {/* Warm gradient background */}
        <div 
          className="absolute inset-0 z-0"
          style={{
            background: 'linear-gradient(180deg, #FFE5D4 0%, #FFD4B3 50%, #FFC996 100%)',
          }}
        >
          <div 
            className="absolute inset-0 opacity-30"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
              mixBlendMode: 'overlay',
            }}
          />
        </div>

        {/* Background gradient - no floating potatoes */}

        {/* Content Layer */}
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="absolute top-8 left-8"
          >
            <h1 className="text-2xl font-bold tracking-wider text-gray-800" style={{ 
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
              letterSpacing: '0.1em',
            }}>
              <span className="not-italic font-normal">POTATO</span><br />
              <span className="italic font-semibold">SHIELD</span>
            </h1>
          </motion.div>

          {/* Menu Icon */}
          <motion.button
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="absolute top-8 right-8 text-gray-800 hover:text-gray-600 transition-colors"
            onClick={() => router.push('/login')}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </motion.button>

          {/* Main Headline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.3 }}
            className="text-center max-w-4xl"
          >
            <motion.h2 
              className="text-5xl md:text-7xl mb-6 text-gray-900"
              style={{ 
                fontFamily: 'Georgia, serif',
                lineHeight: '1.1',
                fontStyle: 'italic',
                fontWeight: 300,
                letterSpacing: '-0.02em',
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.3 }}
            >
              <span className="font-normal not-italic">Will your crops be</span><br />
              <span className="font-semibold italic">Healthy</span>
              <span className="font-light not-italic">, or</span><br />
              <span className="font-semibold italic">Diseased</span><span className="font-light not-italic">?</span>
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.6 }}
              className="text-lg md:text-xl text-gray-700 mb-12 max-w-2xl mx-auto leading-relaxed"
              style={{ 
                fontFamily: 'Georgia, serif',
                fontStyle: 'italic',
                fontWeight: 400,
              }}
            >
              Protect your <span className="font-semibold not-italic">potato crops</span> with AI-powered disease detection.<br />
              <span className="font-light italic">Early diagnosis.</span> <span className="font-medium not-italic">Intelligent prevention.</span> <span className="font-semibold italic">Optimal harvests.</span>
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.9 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <motion.button
                onClick={() => router.push('/login')}
                className="px-8 py-4 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all duration-300 hover:scale-105 shadow-lg"
                style={{ 
                  fontFamily: 'Georgia, serif',
                  fontStyle: 'italic',
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                Get Started
              </motion.button>
              <motion.a
                href="#features"
                className="px-8 py-4 bg-transparent border-2 border-gray-900 text-gray-900 rounded-full font-medium hover:bg-gray-900 hover:text-white transition-all duration-300 hover:scale-105"
                style={{ 
                  fontFamily: 'Georgia, serif',
                  fontStyle: 'italic',
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                Learn More
              </motion.a>
            </motion.div>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1.2 }}
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-6 h-10 border-2 border-gray-800 rounded-full flex items-start justify-center p-2"
            >
              <motion.div
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-1 h-1 bg-gray-800 rounded-full"
              />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Scroll Potato Section - appears after hero, moves with scroll like BlueYard bubble */}
      <div className="relative" style={{ background: 'linear-gradient(180deg, #FFE5D4 0%, #FFD4B3 50%, #FFC996 100%)' }}>
        <ScrollPotato />
      </div>

      {/* Features Section */}
      <section id="features" className="relative min-h-screen w-full flex items-center justify-center px-6 py-20"
        style={{
          background: 'linear-gradient(180deg, #FFC996 0%, #FFD4B3 50%, #FFE5D4 100%)',
        }}
      >
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-6xl mb-6 text-gray-900" style={{ 
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
              fontWeight: 300,
              letterSpacing: '-0.01em',
            }}>
              <span className="font-normal not-italic">How It</span> <span className="font-semibold italic">Works</span>
            </h2>
            <p className="text-xl text-gray-700 max-w-2xl mx-auto" style={{ 
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
            }}>
              <span className="font-light italic">Simple</span>, <span className="font-medium not-italic">intelligent</span>, and <span className="font-semibold italic">powerful</span> disease management solutions for your crops
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Upload & Analyze',
                description: 'Capture or upload an image of your potato leaves. Our AI instantly analyzes and identifies diseases with exceptional accuracy.',
                icon: '📷',
              },
              {
                title: 'Smart Routing',
                description: 'Our intelligent system automatically determines whether you need diagnostic analysis or predictive forecasting based on your query.',
                icon: '🔀',
              },
              {
                title: 'Get Recommendations',
                description: 'Receive comprehensive disease reports, treatment recommendations, and preventive measures tailored to your specific field conditions.',
                icon: '💊',
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.2 }}
                className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 hover:bg-white/80 transition-all duration-300 hover:scale-105 shadow-lg"
              >
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-2xl mb-4 text-gray-900" style={{ 
                  fontFamily: 'Georgia, serif',
                  fontStyle: 'italic',
                  fontWeight: 600,
                }}>
                  {feature.title}
                </h3>
                <p className="text-gray-700 leading-relaxed" style={{ 
                  fontFamily: 'Georgia, serif',
                  fontStyle: 'italic',
                  fontWeight: 400,
                }}>
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="relative min-h-screen w-full flex items-center justify-center px-6 py-20"
        style={{
          background: 'linear-gradient(180deg, #FFE5D4 0%, #FFD4B3 50%, #FFC996 100%)',
        }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl md:text-6xl mb-8 text-gray-900" style={{ 
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
              fontWeight: 300,
              letterSpacing: '-0.01em',
            }}>
              <span className="font-normal not-italic">Why</span> <span className="font-semibold italic">Potato Shield</span><span className="font-light not-italic">?</span>
            </h2>
            <p className="text-xl text-gray-700 mb-12 leading-relaxed" style={{ 
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
            }}>
              <span className="font-semibold not-italic">Potato Shield</span> combines <span className="font-medium italic">cutting-edge AI technology</span> with agricultural expertise to provide farmers with 
              instant, accurate disease diagnosis and actionable recommendations. Our system utilizes <span className="font-semibold italic">advanced computer 
              vision</span> to identify diseases such as <span className="font-medium not-italic">Early Blight</span> and <span className="font-medium not-italic">Late Blight</span>, enabling you to protect your crops before 
              significant damage occurs.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { stat: '90%+', label: 'Accuracy Rate' },
                { stat: '< 5s', label: 'Analysis Time' },
                { stat: '24/7', label: 'Available' },
                { stat: 'Free', label: 'To Start' },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  className="bg-white/60 backdrop-blur-sm rounded-2xl p-6"
                >
                  <div className="text-4xl font-bold text-gray-900 mb-2" style={{ 
                    fontFamily: 'Georgia, serif',
                    fontStyle: 'italic',
                    fontWeight: 700,
                  }}>
                    {item.stat}
                  </div>
                  <div className="text-gray-700" style={{ 
                    fontFamily: 'Georgia, serif',
                    fontStyle: 'italic',
                  }}>
                    {item.label}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative min-h-screen w-full flex items-center justify-center px-6 py-20"
        style={{
          background: 'linear-gradient(180deg, #FFC996 0%, #FFD4B3 100%)',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-3xl mx-auto"
        >
          <h2 className="text-4xl md:text-6xl mb-6 text-gray-900" style={{ 
            fontFamily: 'Georgia, serif',
            fontStyle: 'italic',
            fontWeight: 300,
            letterSpacing: '-0.01em',
          }}>
            <span className="font-normal not-italic">Ready to</span> <span className="font-semibold italic">Protect</span> <span className="font-light not-italic">Your Crops</span><span className="font-semibold italic">?</span>
          </h2>
          <p className="text-xl text-gray-700 mb-12" style={{ 
            fontFamily: 'Georgia, serif',
            fontStyle: 'italic',
          }}>
            Join <span className="font-semibold not-italic">thousands of farmers</span> using <span className="font-medium italic">AI</span> to keep their potato fields <span className="font-semibold italic">healthy</span> and <span className="font-medium not-italic">productive</span>.
          </p>
          <motion.button
            onClick={() => router.push('/login')}
            className="px-12 py-5 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-all duration-300 hover:scale-105 shadow-lg text-lg"
            style={{ 
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
            }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
          >
            Start Protecting Your Crops
          </motion.button>
        </motion.div>
      </section>
    </div>
  )
}
