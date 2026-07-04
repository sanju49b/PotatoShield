'use client'

import { useRef, useMemo, useEffect, useState } from 'react'
import { FloatingKawaiiPotatoes } from './FlipAnimPotato'

export default function FloatingPotatoes() {
  const [mouse, setMouse] = useState({ x: 0, y: 0 })
  const canvasRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!canvasRef.current) return
      const rect = canvasRef.current.getBoundingClientRect()
      const x = ((e.clientX - rect.left) / rect.width) * 100
      const y = ((e.clientY - rect.top) / rect.height) * 100
      setMouse({ x, y })
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (!canvasRef.current || !e.touches[0]) return
      const rect = canvasRef.current.getBoundingClientRect()
      const x = ((e.touches[0].clientX - rect.left) / rect.width) * 100
      const y = ((e.touches[0].clientY - rect.top) / rect.height) * 100
      setMouse({ x, y })
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('touchmove', handleTouchMove)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('touchmove', handleTouchMove)
    }
  }, [])

  return (
    <div ref={canvasRef} className="absolute inset-0 w-full h-full">
      <FloatingKawaiiPotatoes count={50} />
    </div>
  )
}
