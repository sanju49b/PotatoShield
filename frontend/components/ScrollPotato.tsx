'use client'

import { useRef, useState, useEffect } from 'react'
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'

export default function ScrollPotato() {
  const containerRef = useRef<HTMLDivElement>(null)
  const [gifLoaded, setGifLoaded] = useState(false)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start 0.7', 'end 0.3']
  })

  // Check if GIF loads
  useEffect(() => {
    const img = new Image()
    img.onload = () => setGifLoaded(true)
    img.onerror = () => setGifLoaded(false)
    img.src = '/potatojump.gif'
  }, [])

  // Physics-based movement - smoother spring animations
  // Moves up and to the right as you scroll, with gentle rotation
  const physicsY = useSpring(
    useTransform(scrollYProgress, [0, 1], [100, -400]),
    {
      stiffness: 100,
      damping: 50,
      mass: 0.5,
    }
  )

  const physicsX = useSpring(
    useTransform(scrollYProgress, [0, 1], [-100, 300]),
    {
      stiffness: 90,
      damping: 45,
      mass: 0.6,
    }
  )

  const physicsRotate = useSpring(
    useTransform(scrollYProgress, [0, 1], [-15, 30]),
    {
      stiffness: 60,
      damping: 40,
      mass: 0.7,
    }
  )

  // Opacity - smoother fade in/out
  const opacity = useTransform(scrollYProgress, [0, 0.15, 0.85, 1], [0, 1, 1, 0])
  
  // Scale - smoother scaling with larger range
  const scale = useSpring(
    useTransform(scrollYProgress, [0, 0.2, 0.5, 0.8, 1], [0.5, 1.1, 1.4, 1.3, 1.1]),
    {
      stiffness: 80,
      damping: 35,
      mass: 0.5,
    }
  )

  // Dialogue visibility - smoother transitions
  const dialogueOpacity = useSpring(
    useTransform(scrollYProgress, [0, 0.15, 0.85, 1], [0, 1, 1, 0]),
    {
      stiffness: 100,
      damping: 40,
      mass: 0.4,
    }
  )
  const dialogueY = useSpring(
    useTransform(scrollYProgress, [0, 0.5, 1], [5, 0, -5]),
    {
      stiffness: 120,
      damping: 45,
      mass: 0.3,
    }
  )

  return (
    <div 
      ref={containerRef}
      className="relative w-full"
      style={{
        minHeight: '200vh',
        height: '200vh',
      }}
    >
      <motion.div
        className="fixed"
        style={{
          top: '50%',
          left: '50%',
          y: physicsY,
          x: physicsX,
          rotate: physicsRotate,
          opacity,
          scale,
          zIndex: 50,
        }}
      >
        {/* Large Jumping Potato GIF - covers good chunk of page */}
        <div className="relative transform -translate-x-1/2 -translate-y-1/2">
          {gifLoaded ? (
            <img
              src="/potatojump.gif"
              alt="Jumping Potato"
              className="block"
              style={{
                width: '800px',
                height: 'auto',
                maxWidth: '85vw',
                maxHeight: '85vh',
                filter: 'drop-shadow(0 15px 50px rgba(255, 107, 53, 0.5))',
                imageRendering: 'auto',
              }}
            />
          ) : (
            <div 
              className="bg-orange-400 rounded-full animate-pulse"
              style={{
                width: '800px',
                height: '800px',
                maxWidth: '85vw',
                maxHeight: '85vh',
              }}
            />
          )}
        </div>

        {/* Cute Dialogue Box */}
        <motion.div
          className="absolute -top-32 left-1/2 transform -translate-x-1/2 whitespace-nowrap pointer-events-none"
          style={{
            opacity: dialogueOpacity,
            y: dialogueY,
          }}
        >
          <motion.div
            className="relative bg-gradient-to-br from-yellow-50 to-orange-50 rounded-3xl px-10 py-5 shadow-2xl"
            style={{
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
              fontSize: '28px',
              fontWeight: 700,
              color: '#1f2937',
              border: '4px solid #fbbf24',
              boxShadow: '0 15px 40px rgba(255, 107, 53, 0.4)',
            }}
            animate={{
              scale: [1, 1.08, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <span className="text-4xl mr-3">💬</span>
            <span className="text-pink-600">Save meeeeee!</span>
            <span className="text-3xl ml-3">🥔</span>
            
            {/* Cute speech bubble tail pointing down */}
            <div
              className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full"
              style={{
                width: 0,
                height: 0,
                borderLeft: '20px solid transparent',
                borderRight: '20px solid transparent',
                borderTop: '25px solid #fef3c7',
                filter: 'drop-shadow(0 2px 4px rgba(251, 191, 36, 0.3))',
              }}
            />
            <div
              className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full"
              style={{
                width: 0,
                height: 0,
                borderLeft: '22px solid transparent',
                borderRight: '22px solid transparent',
                borderTop: '27px solid #fbbf24',
                marginTop: '4px',
              }}
            />
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}
