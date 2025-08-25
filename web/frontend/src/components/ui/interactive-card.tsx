import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { ReactNode, useRef } from 'react'

interface InteractiveCardProps {
  children: ReactNode
  className?: string
  glowColor?: string
}

export function InteractiveCard({ children, className = '', glowColor = 'blue' }: InteractiveCardProps) {
  const ref = useRef<HTMLDivElement>(null)
  
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  const mouseXSpring = useSpring(x)
  const mouseYSpring = useSpring(y)
  
  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["17.5deg", "-17.5deg"])
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-17.5deg", "17.5deg"])

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return
    
    const rect = ref.current.getBoundingClientRect()
    const width = rect.width
    const height = rect.height
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top
    
    const xPct = mouseX / width - 0.5
    const yPct = mouseY / height - 0.5
    
    x.set(xPct)
    y.set(yPct)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  const glowColors = {
    blue: 'shadow-blue-500/25',
    purple: 'shadow-purple-500/25',
    green: 'shadow-green-500/25',
    red: 'shadow-red-500/25',
    yellow: 'shadow-yellow-500/25',
    cyan: 'shadow-cyan-500/25'
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateY,
        rotateX,
        transformStyle: "preserve-3d"
      }}
      whileHover={{
        scale: 1.05,
        transition: { duration: 0.2 }
      }}
      className={`relative rounded-xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 transition-all duration-300 hover:shadow-2xl ${glowColors[glowColor as keyof typeof glowColors]} ${className}`}
    >
      <div style={{ transform: "translateZ(75px)" }}>
        {children}
      </div>
      
      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 rounded-xl opacity-0 transition-opacity duration-300"
        style={{
          background: `radial-gradient(circle at ${x.get() * 100 + 50}% ${y.get() * 100 + 50}%, rgba(59, 130, 246, 0.1), transparent 50%)`
        }}
        whileHover={{ opacity: 1 }}
      />
    </motion.div>
  )
}

interface FloatingCardProps {
  children: ReactNode
  className?: string
  delay?: number
  amplitude?: number
  duration?: number
}

export function FloatingCard({ 
  children, 
  className = '', 
  delay = 0, 
  amplitude = 10, 
  duration = 3 
}: FloatingCardProps) {
  return (
    <motion.div
      className={className}
      animate={{
        y: [0, -amplitude, 0],
        rotate: [0, 1, 0, -1, 0]
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut",
        delay
      }}
      whileHover={{
        scale: 1.05,
        transition: { duration: 0.2 }
      }}
    >
      {children}
    </motion.div>
  )
}

interface GlassmorphismCardProps {
  children: ReactNode
  className?: string
  blur?: 'sm' | 'md' | 'lg' | 'xl'
}

export function GlassmorphismCard({ 
  children, 
  className = '', 
  blur = 'md' 
}: GlassmorphismCardProps) {
  const blurClasses = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
    xl: 'backdrop-blur-xl'
  }

  return (
    <motion.div
      className={`relative rounded-2xl bg-white/10 dark:bg-white/5 ${blurClasses[blur]} border border-white/20 dark:border-white/10 shadow-xl ${className}`}
      whileHover={{
        scale: 1.02,
        backgroundColor: "rgba(255, 255, 255, 0.15)"
      }}
      transition={{ duration: 0.3 }}
    >
      <div className="relative z-10">
        {children}
      </div>
      
      {/* Gradient overlay */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/20 to-transparent opacity-50" />
    </motion.div>
  )
}

interface ParallaxCardProps {
  children: ReactNode
  className?: string
  offset?: number
}

export function ParallaxCard({ children, className = '', offset = 50 }: ParallaxCardProps) {
  const ref = useRef<HTMLDivElement>(null)
  
  const y = useMotionValue(0)
  const ySpring = useSpring(y, { stiffness: 300, damping: 30 })

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return
    
    const rect = ref.current.getBoundingClientRect()
    const mouseY = e.clientY - rect.top
    const yPct = (mouseY / rect.height - 0.5) * offset
    
    y.set(yPct)
  }

  const handleMouseLeave = () => {
    y.set(0)
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`relative overflow-hidden rounded-xl ${className}`}
    >
      <motion.div
        style={{ y: ySpring }}
        className="relative z-10"
      >
        {children}
      </motion.div>
    </motion.div>
  )
}

interface NeonCardProps {
  children: ReactNode
  className?: string
  color?: 'blue' | 'purple' | 'green' | 'pink' | 'cyan'
}

export function NeonCard({ children, className = '', color = 'blue' }: NeonCardProps) {
  const neonColors = {
    blue: 'shadow-blue-500/50 border-blue-500/50',
    purple: 'shadow-purple-500/50 border-purple-500/50',
    green: 'shadow-green-500/50 border-green-500/50',
    pink: 'shadow-pink-500/50 border-pink-500/50',
    cyan: 'shadow-cyan-500/50 border-cyan-500/50'
  }

  return (
    <motion.div
      className={`relative rounded-xl bg-gray-900/90 border-2 transition-all duration-300 ${neonColors[color]} ${className}`}
      whileHover={{
        scale: 1.05,
        boxShadow: `0 0 30px rgba(59, 130, 246, 0.6)`,
        transition: { duration: 0.2 }
      }}
      animate={{
        boxShadow: [
          `0 0 20px rgba(59, 130, 246, 0.3)`,
          `0 0 30px rgba(59, 130, 246, 0.5)`,
          `0 0 20px rgba(59, 130, 246, 0.3)`
        ]
      }}
      transition={{
        boxShadow: {
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }
      }}
    >
      {children}
    </motion.div>
  )
}
