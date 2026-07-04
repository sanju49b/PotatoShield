'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface FlipAnimPotatoProps {
  size?: number
  className?: string
  style?: React.CSSProperties
  floating?: boolean
}

/**
 * Component that embeds the FlipAnim kawaii potato animation
 * Animation ID: 1Cre6WOE
 * Source: https://flipanim.com/anim=1Cre6WOE
 */
export default function FlipAnimPotato({ 
  size = 60, 
  className = '', 
  style = {},
  floating = true 
}: FlipAnimPotatoProps) {
  // Animation reference: https://flipanim.com/anim=1Cre6WOE
  // The kawaii potato animation component below matches the FlipAnim style

  // Fallback HAPPY kawaii potato animation (refreshing and epic style)
  const FallbackPotato = () => (
    <div
      className={`relative ${className}`}
      style={{
        width: size,
        height: size,
        ...style
      }}
    >
      {/* Happy Potato body - bright, cheerful colors */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: 'linear-gradient(135deg, #FFB366 0%, #FF8C42 50%, #FF6B35 100%)',
          boxShadow: '0 3px 10px rgba(255, 107, 53, 0.3)',
          transform: 'scale(1.05, 0.95)',
          border: '2px solid rgba(255, 255, 255, 0.3)',
        }}
      >
        {/* Happy Eyes - bright and cheerful */}
        <div className="absolute top-[28%] left-[28%] w-3 h-3 bg-white rounded-full shadow-sm" />
        <div className="absolute top-[28%] right-[28%] w-3 h-3 bg-white rounded-full shadow-sm" />
        
        {/* Pupils - looking forward happily */}
        <div className="absolute top-[29%] left-[29%] w-1.5 h-1.5 bg-black rounded-full" />
        <div className="absolute top-[29%] right-[29%] w-1.5 h-1.5 bg-black rounded-full" />
        
        {/* HAPPY Smile - wide, cheerful smile */}
        <svg
          className="absolute bottom-[30%] left-1/2 transform -translate-x-1/2"
          width={size * 0.4}
          height={size * 0.25}
          viewBox="0 0 24 12"
          style={{ overflow: 'visible' }}
        >
          <path
            d="M 3 8 Q 12 4 21 8"
            stroke="#000"
            strokeWidth="2.5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        
        {/* Bright blush cheeks - happy and healthy */}
        <div
          className="absolute top-[35%] left-[5%] w-3 h-3 bg-pink-400 rounded-full opacity-70"
          style={{ transform: 'scale(1.8)', boxShadow: '0 0 8px rgba(255, 182, 193, 0.6)' }}
        />
        <div
          className="absolute top-[35%] right-[5%] w-3 h-3 bg-pink-400 rounded-full opacity-70"
          style={{ transform: 'scale(1.8)', boxShadow: '0 0 8px rgba(255, 182, 193, 0.6)' }}
        />
      </div>
    </div>
  )

  // Use the actual GIF file from FlipAnim (should be in public folder)
  const [gifLoaded, setGifLoaded] = useState(false)
  
  useEffect(() => {
    const img = new Image()
    img.onload = () => setGifLoaded(true)
    img.onerror = () => setGifLoaded(false)
    img.src = '/potato-animation.gif'
  }, [])
  
  if (gifLoaded) {
    return (
      <div
        className={`relative ${className}`}
        style={{ 
          width: size, 
          height: size, 
          ...style,
          filter: 'drop-shadow(0 3px 8px rgba(255, 107, 53, 0.25))',
        }}
      >
        <img
          src="/potato-animation.gif"
          alt="Happy Kawaii Potato Animation"
          className="w-full h-full object-contain"
          style={{ 
            imageRendering: 'auto',
            willChange: 'auto',
          }}
          loading="lazy"
        />
      </div>
    )
  }
  
  return <FallbackPotato />
}

// Multiple floating kawaii potatoes component - minimal, refreshing movement
export function FloatingKawaiiPotatoes({ count = 50 }: { count?: number }) {
  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
      {Array.from({ length: count }).map((_, i) => {
        const size = Math.random() * 35 + 35 // 35-70px (slightly larger range)
        const left = Math.random() * 100
        const top = Math.random() * 100
        const delay = Math.random() * 3
        const duration = 8 + Math.random() * 4 // Slower, more graceful (8-12 seconds)
        
        return (
          <motion.div
            key={i}
            className="absolute"
            style={{
              left: `${left}%`,
              top: `${top}%`,
              zIndex: Math.floor(Math.random() * 5), // Lower z-index range
            }}
            initial={{ opacity: 0.4, y: 0 }}
            animate={{
              opacity: [0.4, 0.6, 0.4], // Subtle opacity change
              y: [0, -8, 0], // Minimal vertical movement (only 8px)
              x: [0, Math.random() * 4 - 2, 0], // Very minimal horizontal drift (only 2px max)
            }}
            transition={{
              duration,
              delay,
              repeat: Infinity,
              ease: [0.25, 0.1, 0.25, 1], // Smooth, natural easing
            }}
          >
            <FlipAnimPotato size={size} floating={false} />
          </motion.div>
        )
      })}
    </div>
  )
}

