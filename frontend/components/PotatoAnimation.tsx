'use client'

import { FloatingKawaiiPotatoes } from './FlipAnimPotato'
import { motion } from 'framer-motion'

export default function PotatoAnimation() {
  return (
    <motion.div
      className="w-full h-full relative"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <FloatingKawaiiPotatoes count={20} />
    </motion.div>
  )
}

