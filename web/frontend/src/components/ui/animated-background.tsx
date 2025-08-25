import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface Particle {
  id: number
  x: number
  y: number
  size: number
  speedX: number
  speedY: number
  opacity: number
}

export function AnimatedBackground() {
  const [particles, setParticles] = useState<Particle[]>([])
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    // Generate particles
    const newParticles: Particle[] = []
    for (let i = 0; i < 50; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        size: Math.random() * 4 + 1,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: (Math.random() - 0.5) * 0.5,
        opacity: Math.random() * 0.5 + 0.1
      })
    }
    setParticles(newParticles)

    // Mouse move handler
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useEffect(() => {
    // Animate particles
    const interval = setInterval(() => {
      setParticles(prev => prev.map(particle => ({
        ...particle,
        x: (particle.x + particle.speedX + window.innerWidth) % window.innerWidth,
        y: (particle.y + particle.speedY + window.innerHeight) % window.innerHeight
      })))
    }, 50)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Gradient Background */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20"
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

      {/* Floating Particles */}
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-gradient-to-r from-blue-400 to-purple-400"
          style={{
            width: particle.size,
            height: particle.size,
            opacity: particle.opacity
          }}
          animate={{
            x: particle.x,
            y: particle.y,
            scale: [1, 1.2, 1],
          }}
          transition={{
            scale: {
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }
          }}
        />
      ))}

      {/* Mouse Follower */}
      <motion.div
        className="absolute w-96 h-96 rounded-full bg-gradient-radial from-blue-400/10 to-transparent pointer-events-none"
        animate={{
          x: mousePosition.x - 192,
          y: mousePosition.y - 192,
        }}
        transition={{
          type: "spring",
          damping: 30,
          stiffness: 200
        }}
      />

      {/* Geometric Shapes */}
      <motion.div
        className="absolute top-20 left-20 w-32 h-32 border border-blue-200/30 rounded-lg"
        animate={{
          rotate: 360,
          scale: [1, 1.1, 1]
        }}
        transition={{
          rotate: { duration: 20, repeat: Infinity, ease: "linear" },
          scale: { duration: 4, repeat: Infinity, ease: "easeInOut" }
        }}
      />

      <motion.div
        className="absolute top-40 right-32 w-24 h-24 border border-purple-200/30 rounded-full"
        animate={{
          rotate: -360,
          y: [0, -20, 0]
        }}
        transition={{
          rotate: { duration: 15, repeat: Infinity, ease: "linear" },
          y: { duration: 3, repeat: Infinity, ease: "easeInOut" }
        }}
      />

      <motion.div
        className="absolute bottom-32 left-1/4 w-16 h-16 bg-gradient-to-r from-cyan-200/20 to-blue-200/20 rounded-lg"
        animate={{
          rotate: [0, 45, 0],
          scale: [1, 1.2, 1]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </div>
  )
}

export function FloatingElements() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Code Symbols */}
      <motion.div
        className="absolute top-1/4 left-10 text-4xl text-blue-300/30 font-mono"
        animate={{
          y: [0, -20, 0],
          opacity: [0.3, 0.6, 0.3]
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {'{}'}
      </motion.div>

      <motion.div
        className="absolute top-1/3 right-20 text-3xl text-purple-300/30 font-mono"
        animate={{
          y: [0, 15, 0],
          rotate: [0, 10, 0]
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {'</>'}
      </motion.div>

      <motion.div
        className="absolute bottom-1/4 right-1/4 text-2xl text-cyan-300/30 font-mono"
        animate={{
          x: [0, 10, 0],
          y: [0, -10, 0]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {'()'}
      </motion.div>

      {/* Security Icons */}
      <motion.div
        className="absolute top-1/2 left-1/4 text-2xl text-green-300/30"
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 5, 0]
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        🛡️
      </motion.div>

      <motion.div
        className="absolute bottom-1/3 left-1/3 text-xl text-yellow-300/30"
        animate={{
          y: [0, -15, 0],
          opacity: [0.3, 0.7, 0.3]
        }}
        transition={{
          duration: 3.5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        🔒
      </motion.div>
    </div>
  )
}
