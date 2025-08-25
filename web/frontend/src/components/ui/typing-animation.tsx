import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

interface TypingAnimationProps {
  texts: string[]
  className?: string
  speed?: number
  deleteSpeed?: number
  delayBetween?: number
}

export function TypingAnimation({ 
  texts, 
  className = '', 
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
      // Typing
      const timer = setTimeout(() => {
        setCurrentText(currentFullText.slice(0, currentText.length + 1))
      }, speed)
      return () => clearTimeout(timer)
    } else if (!isDeleting && currentText === currentFullText) {
      // Finished typing, wait before deleting
      setIsWaiting(true)
    } else if (isDeleting && currentText !== '') {
      // Deleting
      const timer = setTimeout(() => {
        setCurrentText(currentText.slice(0, -1))
      }, deleteSpeed)
      return () => clearTimeout(timer)
    } else if (isDeleting && currentText === '') {
      // Finished deleting, move to next text
      setIsDeleting(false)
      setCurrentTextIndex((prev) => (prev + 1) % texts.length)
    }
  }, [currentText, currentTextIndex, isDeleting, isWaiting, texts, speed, deleteSpeed, delayBetween])

  return (
    <span className={className}>
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
  duration?: number
}

export function AnimatedText({ children, className = '', delay = 0, duration = 0.8 }: AnimatedTextProps) {
  const words = children.split(' ')

  const container = {
    hidden: { opacity: 0 },
    visible: (i = 1) => ({
      opacity: 1,
      transition: { staggerChildren: 0.12, delayChildren: delay }
    })
  }

  const child = {
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        damping: 12,
        stiffness: 100,
        duration
      }
    },
    hidden: {
      opacity: 0,
      y: 20,
      transition: {
        type: "spring",
        damping: 12,
        stiffness: 100,
        duration
      }
    }
  }

  return (
    <motion.div
      className={className}
      variants={container}
      initial="hidden"
      animate="visible"
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

interface GlitchTextProps {
  children: string
  className?: string
}

export function GlitchText({ children, className = '' }: GlitchTextProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      whileHover="hover"
    >
      <motion.span
        variants={{
          hover: {
            x: [0, -2, 2, 0],
            transition: { duration: 0.3, repeat: 2 }
          }
        }}
        className="relative z-10"
      >
        {children}
      </motion.span>
      
      <motion.span
        className="absolute top-0 left-0 text-red-500 opacity-70"
        variants={{
          hover: {
            x: [0, 2, -2, 0],
            transition: { duration: 0.3, repeat: 2, delay: 0.1 }
          }
        }}
        style={{ clipPath: 'polygon(0 0, 100% 0, 100% 45%, 0 45%)' }}
      >
        {children}
      </motion.span>
      
      <motion.span
        className="absolute top-0 left-0 text-blue-500 opacity-70"
        variants={{
          hover: {
            x: [0, -2, 2, 0],
            transition: { duration: 0.3, repeat: 2, delay: 0.2 }
          }
        }}
        style={{ clipPath: 'polygon(0 55%, 100% 55%, 100% 100%, 0 100%)' }}
      >
        {children}
      </motion.span>
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
  const [count, setCount] = useState(0)

  useEffect(() => {
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
  }, [end, duration])

  return (
    <motion.span
      className={className}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {prefix}{count.toLocaleString()}{suffix}
    </motion.span>
  )
}
