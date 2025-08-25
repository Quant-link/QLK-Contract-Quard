import { motion, useMotionValue, useSpring, useTransform, useInView } from 'framer-motion'
import { ReactNode, useRef, useState, useEffect } from 'react'

interface TypingAnimationProps {
  texts: string[]
  className?: string
  style?: React.CSSProperties
  speed?: number
  deleteSpeed?: number
  delayBetween?: number
}

export function TypingAnimation({
  texts,
  className = '',
  style,
  speed = 100,
  deleteSpeed = 50,
  delayBetween = 2000
}: TypingAnimationProps) {
  const [currentTextIndex, setCurrentTextIndex] = useState(0)
  const [currentText, setCurrentText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [isWaiting, setIsWaiting] = useState(false)

  useEffect(() => {
    const currentFullText = texts[currentTextIndex]
    
    if (isWaiting) {
      const waitTimer = setTimeout(() => {
        setIsWaiting(false)
        setIsDeleting(true)
      }, delayBetween)
      return () => clearTimeout(waitTimer)
    }

    if (!isDeleting && currentText !== currentFullText) {
      const timer = setTimeout(() => {
        setCurrentText(currentFullText.slice(0, currentText.length + 1))
      }, speed)
      return () => clearTimeout(timer)
    } else if (!isDeleting && currentText === currentFullText) {
      setIsWaiting(true)
    } else if (isDeleting && currentText !== '') {
      const timer = setTimeout(() => {
        setCurrentText(currentText.slice(0, -1))
      }, deleteSpeed)
      return () => clearTimeout(timer)
    } else if (isDeleting && currentText === '') {
      setIsDeleting(false)
      setCurrentTextIndex((prev) => (prev + 1) % texts.length)
    }
  }, [currentText, currentTextIndex, isDeleting, isWaiting, texts, speed, deleteSpeed, delayBetween])

  return (
    <span className={className} style={style}>
      {currentText}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity }}
        className="inline-block w-0.5 h-[1em] bg-current ml-1"
      />
    </span>
  )
}

interface AnimatedTextProps {
  children: string
  className?: string
  delay?: number
}

export function AnimatedText({ children, className = '', delay = 0 }: AnimatedTextProps) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true })
  const words = children.split(' ')

  const container = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.12, delayChildren: delay }
    }
  }

  const child = {
    visible: {
      opacity: 1,
      y: 0,
      transition: { type: "spring", damping: 12, stiffness: 100 }
    },
    hidden: {
      opacity: 0,
      y: 20,
      transition: { type: "spring", damping: 12, stiffness: 100 }
    }
  }

  return (
    <motion.div
      ref={ref}
      className={className}
      variants={container}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
    >
      {words.map((word, index) => (
        <motion.span
          variants={child}
          key={index}
          className="inline-block mr-2"
        >
          {word}
        </motion.span>
      ))}
    </motion.div>
  )
}

interface CountUpProps {
  end: number
  duration?: number
  className?: string
  prefix?: string
  suffix?: string
}

export function CountUp({ end, duration = 2, className = '', prefix = '', suffix = '' }: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true })
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!isInView) return

    let startTime: number
    let animationFrame: number

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1)
      
      setCount(Math.floor(progress * end))
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [end, duration, isInView])

  return (
    <motion.span
      ref={ref}
      className={className}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={isInView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.5 }}
    >
      {prefix}{count.toLocaleString()}{suffix}
    </motion.span>
  )
}

interface FloatingElementProps {
  children: ReactNode
  className?: string
  delay?: number
  amplitude?: number
  duration?: number
}

export function FloatingElement({ 
  children, 
  className = '', 
  delay = 0, 
  amplitude = 10, 
  duration = 3 
}: FloatingElementProps) {
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
    >
      {children}
    </motion.div>
  )
}

interface GlowCardProps {
  children: ReactNode
  className?: string
  glowColor?: string
}

export function GlowCard({ children, className = '', glowColor = 'blue' }: GlowCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const glowColors = {
    blue: 'rgba(59, 130, 246, 0.4)',
    purple: 'rgba(147, 51, 234, 0.4)',
    green: 'rgba(34, 197, 94, 0.4)',
    cyan: 'rgba(6, 182, 212, 0.4)'
  }

  return (
    <motion.div
      className={`relative rounded-xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 transition-all duration-300 ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ scale: 1.02, y: -5 }}
      animate={{
        boxShadow: isHovered 
          ? `0 20px 40px ${glowColors[glowColor as keyof typeof glowColors]}`
          : '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  )
}

interface ParticleFieldProps {
  className?: string
  particleCount?: number
}

export function ParticleField({ className = '', particleCount = 30 }: ParticleFieldProps) {
  const particles = Array.from({ length: particleCount }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 1,
    duration: Math.random() * 3 + 2
  }))

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-gradient-to-r from-blue-400/30 to-purple-400/30"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size,
          }}
          animate={{
            y: [0, -20, 0],
            opacity: [0.3, 0.8, 0.3],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: particle.duration,
            repeat: Infinity,
            ease: "easeInOut",
            delay: Math.random() * 2
          }}
        />
      ))}
    </div>
  )
}

interface GradientBackgroundProps {
  className?: string
}

export function GradientBackground({ className = '' }: GradientBackgroundProps) {
  return (
    <motion.div
      className={`absolute inset-0 ${className}`}
      animate={{
        background: [
          'linear-gradient(45deg, #f0f9ff, #e0e7ff, #f3e8ff)',
          'linear-gradient(135deg, #e0e7ff, #f3e8ff, #fef3c7)',
          'linear-gradient(225deg, #f3e8ff, #fef3c7, #f0f9ff)',
          'linear-gradient(315deg, #fef3c7, #f0f9ff, #e0e7ff)'
        ]
      }}
      transition={{
        duration: 20,
        repeat: Infinity,
        ease: "linear"
      }}
    />
  )
}
