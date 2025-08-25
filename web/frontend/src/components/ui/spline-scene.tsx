import Spline from '@splinetool/react-spline'
import { Suspense, useState } from 'react'
import { motion } from 'framer-motion'

interface SplineSceneProps {
  className?: string
  scene?: string
}

export function SplineScene({ 
  className = '', 
  scene = 'https://prod.spline.design/VaGfKTqOY07BzYCG/scene.splinecode' 
}: SplineSceneProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  const handleLoad = () => {
    setIsLoading(false)
  }

  const handleError = () => {
    setIsLoading(false)
    setHasError(true)
  }

  return (
    <div className={`relative ${className}`}>
      {/* Loading State */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-blue-900/20 rounded-lg"
        >
          <div className="text-center space-y-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"
            />
            <p className="text-sm text-muted-foreground">Loading 3D Scene...</p>
          </div>
        </motion.div>
      )}

      {/* Error State */}
      {hasError && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg"
        >
          <div className="text-center space-y-4 p-8">
            <div className="text-4xl">🎨</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                3D Scene Unavailable
              </h3>
              <p className="text-sm text-muted-foreground mt-2">
                The 3D animation couldn't load. The experience continues without it.
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Spline Scene */}
      <Suspense fallback={null}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: isLoading ? 0 : 1 }}
          transition={{ duration: 0.5 }}
          className="w-full h-full"
        >
          <Spline
            scene={scene}
            onLoad={handleLoad}
            onError={handleError}
            style={{
              width: '100%',
              height: '100%',
              background: 'transparent'
            }}
          />
        </motion.div>
      </Suspense>
    </div>
  )
}

interface FloatingSplineProps {
  className?: string
  scene?: string
  amplitude?: number
  duration?: number
}

export function FloatingSpline({ 
  className = '', 
  scene,
  amplitude = 20,
  duration = 4
}: FloatingSplineProps) {
  return (
    <motion.div
      animate={{
        y: [0, -amplitude, 0],
        rotate: [0, 2, 0, -2, 0]
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut"
      }}
      className={className}
    >
      <SplineScene scene={scene} className="w-full h-full" />
    </motion.div>
  )
}

interface InteractiveSplineProps {
  className?: string
  scene?: string
}

export function InteractiveSpline({ className = '', scene }: InteractiveSplineProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      className={`relative ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        animate={{
          rotateY: isHovered ? 10 : 0,
          rotateX: isHovered ? -5 : 0
        }}
        transition={{ duration: 0.3 }}
        style={{ transformStyle: "preserve-3d" }}
        className="w-full h-full"
      >
        <SplineScene scene={scene} className="w-full h-full" />
      </motion.div>
      
      {/* Glow Effect on Hover */}
      <motion.div
        className="absolute inset-0 rounded-lg pointer-events-none"
        animate={{
          boxShadow: isHovered 
            ? "0 0 30px rgba(59, 130, 246, 0.3), 0 0 60px rgba(59, 130, 246, 0.1)"
            : "0 0 0px rgba(59, 130, 246, 0)"
        }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  )
}
