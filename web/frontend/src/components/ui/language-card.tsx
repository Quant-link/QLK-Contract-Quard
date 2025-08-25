import { motion } from 'framer-motion'
import { useState } from 'react'
import { Code, Shield, Zap, TrendingUp, Users, Star } from 'lucide-react'

interface LanguageCardProps {
  language: {
    name: string
    logo: string
    description: string
    gradient: string
    contracts: string
    bgColor: string
    features: string[]
    popularity: number
    securityScore: number
    performance: string
    ecosystem: string[]
  }
  index: number
}

export function LanguageCard({ language, index }: LanguageCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const cardVariants = {
    hidden: { opacity: 0, y: 50, scale: 0.9 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.6,
        delay: index * 0.2,
        ease: "easeOut"
      }
    },
    hover: {
      y: -10,
      scale: 1.02,
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    }
  }

  const logoVariants = {
    hidden: { scale: 0, rotate: -180 },
    visible: {
      scale: 1,
      rotate: 0,
      transition: {
        duration: 0.8,
        delay: index * 0.2 + 0.3,
        ease: "easeOut"
      }
    },
    hover: {
      scale: 1.1,
      rotate: 5,
      transition: { duration: 0.3 }
    }
  }

  const getGradientColors = () => {
    switch (language.name) {
      case 'Solidity':
        return 'from-gray-600 via-gray-500 to-gray-400'
      case 'Rust':
        return 'from-orange-600 via-red-500 to-orange-400'
      case 'Go':
        return 'from-cyan-600 via-blue-500 to-teal-500'
      default:
        return 'from-gray-600 via-gray-500 to-gray-400'
    }
  }

  const getAccentColor = () => {
    switch (language.name) {
      case 'Solidity':
        return 'text-gray-400'
      case 'Rust':
        return 'text-orange-400'
      case 'Go':
        return 'text-cyan-400'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      whileInView="visible"
      whileHover="hover"
      viewport={{ once: true }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="relative group"
    >
      {/* Glow Effect */}
      <motion.div
        className={`absolute -inset-1 bg-gradient-to-r ${getGradientColors()} rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200`}
        animate={{
          scale: isHovered ? 1.05 : 1,
        }}
      />

      {/* Main Card */}
      <div className="relative bg-gray-900/95 backdrop-blur-xl rounded-2xl border border-gray-700/50 overflow-hidden">
        {/* Header with Logo */}
        <div className="relative p-8 pb-6">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-5">
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-radial from-white/5 to-transparent" />
          </div>

          <div className="relative z-10 flex flex-col items-center space-y-6">
            {/* Logo Container */}
            <motion.div
              variants={logoVariants}
              className="relative"
            >
              <div className={`absolute inset-0 bg-gradient-to-r ${getGradientColors()} rounded-2xl blur-lg opacity-50`} />
              <div className="relative bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <img 
                  src={language.logo} 
                  alt={`${language.name} logo`}
                  className="h-16 w-auto object-contain filter brightness-110 drop-shadow-2xl"
                />
              </div>
            </motion.div>

            {/* Language Name */}
            <div className="text-center">
              <h3 className="text-2xl font-bold text-white mb-2">{language.name}</h3>
              <p className="text-gray-300 text-sm leading-relaxed">{language.description}</p>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="px-8 pb-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white/5 rounded-xl p-4 border border-white/10">
              <div className="flex items-center space-x-2 mb-2">
                <Users className="h-4 w-4 text-blue-400" />
                <span className="text-xs text-gray-400 uppercase tracking-wide">Contracts</span>
              </div>
              <div className={`text-lg font-bold ${getAccentColor()}`}>{language.contracts}</div>
            </div>

            <div className="bg-white/5 rounded-xl p-4 border border-white/10">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-400" />
                <span className="text-xs text-gray-400 uppercase tracking-wide">Popularity</span>
              </div>
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-3 w-3 ${
                      i < language.popularity ? 'text-yellow-400 fill-current' : 'text-gray-600'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="px-8 pb-6">
          <div className="space-y-3">
            <div className="flex items-center space-x-2 mb-3">
              <Code className="h-4 w-4 text-purple-400" />
              <span className="text-sm font-medium text-gray-300">Key Features</span>
            </div>
            {language.features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 + idx * 0.1 }}
                className="flex items-center space-x-3"
              >
                <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${getGradientColors()}`} />
                <span className="text-sm text-gray-300">{feature}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="px-8 pb-6">
          <div className="bg-gradient-to-r from-white/5 to-white/10 rounded-xl p-4 border border-white/10">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-green-400" />
                <span className="text-sm font-medium text-gray-300">Security Score</span>
              </div>
              <span className={`text-sm font-bold ${getAccentColor()}`}>
                {language.securityScore}/100
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <motion.div
                className={`h-2 rounded-full bg-gradient-to-r ${getGradientColors()}`}
                initial={{ width: 0 }}
                whileInView={{ width: `${language.securityScore}%` }}
                transition={{ duration: 1, delay: index * 0.2 + 0.5 }}
              />
            </div>
          </div>
        </div>

        {/* Ecosystem */}
        <div className="px-8 pb-8">
          <div className="flex items-center space-x-2 mb-3">
            <Zap className="h-4 w-4 text-yellow-400" />
            <span className="text-sm font-medium text-gray-300">Ecosystem</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {language.ecosystem.map((item, idx) => (
              <motion.span
                key={idx}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 + idx * 0.05 }}
                className="px-3 py-1 bg-white/10 rounded-full text-xs text-gray-300 border border-white/20"
              >
                {item}
              </motion.span>
            ))}
          </div>
        </div>

        {/* Hover Overlay */}
        <motion.div
          className={`absolute inset-0 bg-gradient-to-br ${getGradientColors()} opacity-0 rounded-2xl`}
          animate={{
            opacity: isHovered ? 0.05 : 0,
          }}
          transition={{ duration: 0.3 }}
        />
      </div>
    </motion.div>
  )
}
