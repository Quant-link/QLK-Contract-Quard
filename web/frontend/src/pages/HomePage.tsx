import { Link } from 'react-router-dom'
import { Shield, Zap, Eye, ArrowRight, CheckCircle, Brain, Sparkles } from 'lucide-react'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Button } from '../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { useTheme } from '../components/theme-provider'
import heroVideo from '../assets/videos/quard.mp4'
import solidityLogo from '../assets/logos/solidity-logo.svg'
import rustLogo from '../assets/logos/rust-logo.png'
import goLogo from '../assets/logos/go-logo.png'
import {
  TypingAnimation,
  AnimatedText,
  CountUp,
  FloatingElement,
  GlowCard,
  ParticleField
} from '../components/ui/enhanced-animations'
import AnalyticsDashboard from '../components/dashboard/AnalyticsDashboard'
import { LanguageCard } from '../components/ui/language-card'

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null)
  const featuresRef = useRef<HTMLDivElement>(null)
  const heroInView = useInView(heroRef, { once: true })
  const featuresInView = useInView(featuresRef, { once: true })
  const { theme } = useTheme()

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning algorithms detect complex vulnerabilities and security patterns.',
      color: 'blue' as const,
      stats: '99.7% Accuracy'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Get comprehensive security reports in seconds, not hours.',
      color: 'purple' as const,
      stats: '<2s Analysis'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Bank-grade security with comprehensive vulnerability detection.',
      color: 'green' as const,
      stats: '50+ Detectors'
    }
  ]

  const supportedLanguages = [
    {
      name: 'Solidity',
      logo: solidityLogo,
      description: 'Industry-leading Ethereum smart contract language with comprehensive tooling',
      gradient: 'from-blue-500 to-cyan-500',
      contracts: '2.5M+',
      bgColor: 'bg-gray-800',
      features: [
        'EVM Compatibility',
        'Advanced Type System',
        'Gas Optimization',
        'Inheritance Support',
        'Library Integration'
      ],
      popularity: 5,
      securityScore: 95,
      performance: 'High',
      ecosystem: ['Ethereum', 'Polygon', 'BSC', 'Arbitrum', 'Optimism', 'Avalanche']
    },
    {
      name: 'Rust',
      logo: rustLogo,
      description: 'Memory-safe systems programming for next-generation blockchain platforms',
      gradient: 'from-orange-500 to-red-500',
      contracts: '150K+',
      bgColor: 'bg-orange-900',
      features: [
        'Memory Safety',
        'Zero-Cost Abstractions',
        'Concurrent Programming',
        'WebAssembly Target',
        'Rich Type System'
      ],
      popularity: 4,
      securityScore: 98,
      performance: 'Ultra High',
      ecosystem: ['Substrate', 'ink!', 'Solana', 'NEAR', 'CosmWasm', 'Polkadot']
    },
    {
      name: 'Go',
      logo: goLogo,
      description: 'Scalable blockchain development with Google\'s efficient programming language',
      gradient: 'from-cyan-500 to-blue-500',
      contracts: '75K+',
      bgColor: 'bg-cyan-900',
      features: [
        'Concurrent Design',
        'Fast Compilation',
        'Simple Syntax',
        'Built-in Testing',
        'Cross-Platform'
      ],
      popularity: 4,
      securityScore: 92,
      performance: 'High',
      ecosystem: ['Cosmos SDK', 'Tendermint', 'Hyperledger', 'Ethereum Go', 'Chainlink', 'IPFS']
    }
  ]

  // Determine background style based on theme
  const getBackgroundStyle = () => {
    if (theme === 'light') {
      return {
        backgroundColor: '#ffffff',
        width: '100%',
        maxWidth: '100vw',
        position: 'relative' as const,
        overflowX: 'hidden' as const,
        minHeight: '100vh'
      }
    } else if (theme === 'dark') {
      return {
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
        width: '100%',
        maxWidth: '100vw',
        position: 'relative' as const,
        overflowX: 'hidden' as const,
        minHeight: '100vh'
      }
    } else {
      // System theme - check actual applied theme
      const isDark = document.documentElement.classList.contains('dark')
      if (isDark) {
        return {
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
          width: '100%',
          maxWidth: '100vw',
          position: 'relative' as const,
          overflowX: 'hidden' as const,
          minHeight: '100vh'
        }
      } else {
        return {
          backgroundColor: '#ffffff',
          width: '100%',
          maxWidth: '100vw',
          position: 'relative' as const,
          overflowX: 'hidden' as const,
          minHeight: '100vh'
        }
      }
    }
  }

  return (
    <div className="bg-full-screen no-scroll-x" style={getBackgroundStyle()}>
      {/* Overlay for better text readability */}
      <div className="absolute inset-0 bg-white/20 dark:bg-black/30" />
      <ParticleField className="absolute inset-0" particleCount={40} />

      <div className="relative z-10 space-y-32 no-scroll-x">
        {/* Enhanced Hero Section */}
        <motion.section
          ref={heroRef}
          className="relative min-h-screen flex items-center justify-center px-4 no-scroll-x w-full max-w-full"
        >

          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center w-full">
            {/* Left Content */}
            <div className="space-y-8 text-center lg:text-left">
              {/* Badge */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={heroInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20">
                  <Sparkles className="h-4 w-4 text-blue-400" />
                  <span className="text-sm font-medium text-blue-300">
                    AI-Powered Security Analysis
                  </span>
                </div>
              </motion.div>

              {/* Main Heading */}
              <div className="space-y-4">
                <AnimatedText
                  delay={0.4}
                  className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight"
                >
                  Secure Your
                </AnimatedText>

                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={heroInView ? { opacity: 1, scale: 1 } : {}}
                  transition={{ duration: 0.8, delay: 0.8 }}
                  className="relative"
                >
                  <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold" style={{ color: '#4dace1' }}>
                    Smart Contracts
                  </h1>
                </motion.div>

                <div className="text-2xl md:text-3xl lg:text-4xl text-gray-600 dark:text-gray-300">
                  with{' '}
                  <TypingAnimation
                    texts={[
                      'AI Intelligence',
                      'Advanced Analysis',
                      'Real-time Detection',
                      'Enterprise Security'
                    ]}
                    className="font-bold"
                    style={{ color: '#4dace1' }}
                  />
                </div>
              </div>

              {/* Description */}
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={heroInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 1.2 }}
                className="text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto lg:mx-0"
              >
                ContractQuard provides enterprise-grade security analysis for multi-language smart contracts,
                powered by advanced AI to identify vulnerabilities before deployment.
              </motion.p>

              {/* CTA Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={heroInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 1.4 }}
                className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
              >
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    asChild
                    size="lg"
                    className="btn-custom-primary shadow-lg"
                  >
                    <Link to="/analyze">
                      <Zap className="mr-2 h-5 w-5" />
                      Start Analysis
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                  </Button>
                </motion.div>

                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    asChild
                    size="lg"
                    variant="outline"
                    className="btn-custom-outline border-2 backdrop-blur-sm"
                  >
                    <Link to="#features">
                      <Eye className="mr-2 h-5 w-5" />
                      View Demo
                    </Link>
                  </Button>
                </motion.div>
              </motion.div>
            </div>

            {/* Right Content - Hero Video */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={heroInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="relative h-96 lg:h-[500px]"
            >
              <div className="w-full h-full rounded-2xl overflow-hidden bg-black/20 backdrop-blur-sm border border-white/20">
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  className="w-full h-full object-cover"
                >
                  <source src={heroVideo} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>

              {/* Floating Stats */}
              <div className="absolute -top-4 -left-4 lg:-left-8">
                <FloatingElement delay={0} amplitude={15}>
                  <GlowCard className="p-4 text-center" glowColor="blue">
                    <div className="text-2xl font-bold" style={{ color: '#4dace1' }}>
                      <CountUp end={2500000} suffix="+" />
                    </div>
                    <div className="text-xs text-gray-500">Contracts Analyzed</div>
                  </GlowCard>
                </FloatingElement>
              </div>

              <div className="absolute -bottom-4 -right-4 lg:-right-8">
                <FloatingElement delay={1} amplitude={12}>
                  <GlowCard className="p-4 text-center" glowColor="purple">
                    <div className="text-2xl font-bold" style={{ color: '#4dace1' }}>
                      <CountUp end={99.7} suffix="%" />
                    </div>
                    <div className="text-xs text-gray-500">Accuracy Rate</div>
                  </GlowCard>
                </FloatingElement>
              </div>
            </motion.div>
          </div>
        </motion.section>

        {/* Enhanced Features Section */}
        <motion.section
          ref={featuresRef}
          id="features"
          className="space-y-16 py-20 px-4"
        >
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8 }}
            className="text-center space-y-6"
          >
            <h2 className="text-4xl md:text-5xl font-bold">
              Why Choose{' '}
              <span style={{ color: '#4dace1' }}>
                ContractQuard?
              </span>
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our advanced analysis engine combines traditional static analysis with AI-powered detection
              to provide the most comprehensive security assessment.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={featuresInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8, delay: index * 0.2 }}
              >
                <motion.div
                  whileHover={{ y: -8, scale: 1.02 }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
                  className="h-full"
                >
                  <div className="relative h-full p-8 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 group overflow-hidden">
                    {/* Animated Background Gradient */}
                    <motion.div
                      className="absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-500"
                      style={{ background: 'linear-gradient(135deg, #4dace1, #3a9bd1)' }}
                      initial={false}
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    />

                    {/* Floating Particles */}
                    <div className="absolute inset-0 overflow-hidden">
                      {[...Array(3)].map((_, i) => (
                        <motion.div
                          key={i}
                          className="absolute w-1 h-1 rounded-full opacity-20"
                          style={{
                            backgroundColor: '#4dace1',
                            left: `${20 + i * 30}%`,
                            top: `${30 + i * 20}%`
                          }}
                          animate={{
                            x: [0, 100, 0],
                            y: [0, -50, 0],
                            opacity: [0, 0.6, 0]
                          }}
                          transition={{
                            duration: 4 + i,
                            repeat: Infinity,
                            delay: i * 1.5,
                            ease: "easeInOut"
                          }}
                        />
                      ))}
                    </div>

                    <div className="relative z-10 space-y-6">
                      {/* Header */}
                      <div className="space-y-4">
                        <motion.div
                          className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
                          style={{
                            backgroundColor: 'rgba(77, 172, 225, 0.1)',
                            color: '#4dace1',
                            border: '1px solid rgba(77, 172, 225, 0.3)'
                          }}
                          whileHover={{ scale: 1.05 }}
                        >
                          {feature.color === 'blue' ? 'AI-POWERED' :
                           feature.color === 'purple' ? 'PERFORMANCE' : 'ENTERPRISE'}
                        </motion.div>

                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">
                          {feature.title}
                        </h3>
                      </div>

                      {/* Description */}
                      <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                        {feature.description}
                      </p>

                      {/* Stats with Animation */}
                      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <motion.div
                          className="flex items-center justify-between"
                          whileHover={{ scale: 1.02 }}
                        >
                          <span className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                            Performance
                          </span>
                          <motion.div
                            className="text-2xl font-bold"
                            style={{ color: '#4dace1' }}
                            animate={{
                              textShadow: [
                                "0 0 0px #4dace1",
                                "0 0 10px #4dace1",
                                "0 0 0px #4dace1"
                              ]
                            }}
                            transition={{ duration: 2, repeat: Infinity }}
                          >
                            {feature.stats}
                          </motion.div>
                        </motion.div>
                      </div>

                      {/* Progress Bar Animation */}
                      <div className="space-y-2">
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
                          <motion.div
                            className="h-1 rounded-full"
                            style={{ background: 'linear-gradient(90deg, #4dace1, #3a9bd1)' }}
                            initial={{ width: 0 }}
                            whileInView={{ width: "85%" }}
                            transition={{ duration: 1.5, delay: index * 0.2 }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Supported Languages Section */}
        <section className="space-y-16 py-20 px-4">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center space-y-6"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-sm border border-white/20 mb-8"
            >
              <Brain className="h-5 w-5" style={{ color: '#4dace1' }} />
              <span className="text-sm font-medium uppercase tracking-wide" style={{ color: '#4dace1' }}>
                Advanced Language Support
              </span>
            </motion.div>

            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span style={{ color: '#4dace1' }}>Multi-Language</span> Smart Contract Analysis
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-4xl mx-auto leading-relaxed">
              Comprehensive security analysis across multiple blockchain programming languages with
              <span className="font-semibold" style={{ color: '#4dace1' }}> unified standards</span> and
              <span className="font-semibold" style={{ color: '#4dace1' }}> enterprise-grade detection</span>.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto mt-16">
            {supportedLanguages.map((language, index) => (
              <LanguageCard
                key={language.name}
                language={language}
                index={index}
              />
            ))}
          </div>
        </section>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-8 px-4">
        <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="features">Features</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-8">
          {/* Security Checks */}
          <motion.section
            className="space-y-16 py-20"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <div className="text-center space-y-6">
              <h2 className="text-4xl md:text-5xl font-bold">
                Comprehensive{' '}
                <span style={{ color: '#4dace1' }}>
                  Security Checks
                </span>
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                Our analysis engine detects a wide range of vulnerabilities and security issues.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
              {[
                {
                  name: 'Reentrancy Vulnerabilities',
                  description: 'Detects recursive call patterns that can drain contract funds',
                  severity: 'Critical',
                  category: 'Security'
                },
                {
                  name: 'Integer Overflow/Underflow',
                  description: 'Identifies arithmetic operations that may cause unexpected behavior',
                  severity: 'High',
                  category: 'Logic'
                },
                {
                  name: 'Access Control Issues',
                  description: 'Validates proper permission and authorization mechanisms',
                  severity: 'Critical',
                  category: 'Security'
                },
                {
                  name: 'Timestamp Dependence',
                  description: 'Checks for unsafe reliance on block timestamp values',
                  severity: 'Medium',
                  category: 'Logic'
                },
                {
                  name: 'Gas Limit Problems',
                  description: 'Analyzes gas consumption patterns and potential DoS vectors',
                  severity: 'High',
                  category: 'Performance'
                },
                {
                  name: 'Unchecked External Calls',
                  description: 'Ensures proper error handling for external contract interactions',
                  severity: 'Critical',
                  category: 'Security'
                },
                {
                  name: 'Logic Errors',
                  description: 'Identifies business logic flaws and implementation inconsistencies',
                  severity: 'High',
                  category: 'Logic'
                },
                {
                  name: 'Code Quality Issues',
                  description: 'Reviews coding standards, best practices, and maintainability',
                  severity: 'Low',
                  category: 'Quality'
                }
              ].map((check, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="group"
                >
                  <motion.div
                    whileHover={{ y: -4, scale: 1.01 }}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                    className="relative p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 group overflow-hidden"
                  >
                    {/* Animated Background */}
                    <motion.div
                      className="absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-500"
                      style={{ background: 'linear-gradient(135deg, #4dace1, #3a9bd1)' }}
                    />

                    {/* Category Badge */}
                    <div className="absolute top-4 right-4">
                      <motion.span
                        className="px-3 py-1 text-xs font-medium rounded-full border"
                        style={{
                          backgroundColor: 'rgba(77, 172, 225, 0.1)',
                          color: '#4dace1',
                          borderColor: 'rgba(77, 172, 225, 0.3)'
                        }}
                        whileHover={{ scale: 1.05 }}
                      >
                        {check.category}
                      </motion.span>
                    </div>

                    <div className="space-y-4">
                      {/* Content */}
                      <div className="w-full">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            {check.name}
                          </h3>
                        </div>

                        <p className="text-sm text-gray-600 dark:text-gray-300 mb-3 leading-relaxed">
                          {check.description}
                        </p>

                        <div className="flex items-center justify-between">
                          <div
                            className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium"
                            style={{
                              backgroundColor: 'rgba(77, 172, 225, 0.1)',
                              color: '#4dace1'
                            }}
                          >
                            {check.severity} Priority
                          </div>

                          <CheckCircle className="h-5 w-5" style={{ color: '#4dace1' }} />
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* CTA Section */}
          <motion.section
            className="text-center space-y-8 py-20"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <GlowCard className="p-12 max-w-4xl mx-auto" glowColor="blue">
              <div className="space-y-6">
                <h2 className="text-4xl md:text-5xl font-bold">
                  Ready to{' '}
                  <span style={{ color: '#4dace1' }}>
                    Secure
                  </span>{' '}
                  Your Contracts?
                </h2>
                <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                  Upload your smart contract files and get detailed security analysis in seconds.
                </p>

                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="pt-4"
                >
                  <Button
                    asChild
                    size="lg"
                    className="btn-custom-primary shadow-lg"
                  >
                    <Link to="/analyze">
                      <Zap className="mr-2 h-5 w-5" />
                      Start Free Analysis
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                  </Button>
                </motion.div>
              </div>
            </GlowCard>
          </motion.section>
        </TabsContent>

        <TabsContent value="features" className="space-y-8">
          <div className="text-center py-20">
            <h3 className="text-2xl font-bold text-gray-600 dark:text-gray-300">
              Features are showcased in the main sections above
            </h3>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-8">
          <AnalyticsDashboard />
        </TabsContent>
      </Tabs>
      </div>
    </div>
  )
}
