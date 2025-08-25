import { Link } from 'react-router-dom'
import { Shield, Zap, Eye, ArrowRight, CheckCircle, Brain, Sparkles, Star } from 'lucide-react'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Button } from '../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { FloatingSpline, InteractiveSpline } from '../components/ui/spline-scene'
import {
  TypingAnimation,
  AnimatedText,
  CountUp,
  FloatingElement,
  GlowCard,
  ParticleField,
  GradientBackground
} from '../components/ui/enhanced-animations'
import AnalyticsDashboard from '../components/dashboard/AnalyticsDashboard'

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null)
  const featuresRef = useRef<HTMLDivElement>(null)
  const heroInView = useInView(heroRef, { once: true })
  const featuresInView = useInView(featuresRef, { once: true })

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
      icon: '⟠',
      description: 'Ethereum smart contracts',
      gradient: 'from-blue-500 to-cyan-500',
      contracts: '2.5M+'
    },
    {
      name: 'Rust',
      icon: '🦀',
      description: 'Substrate & ink! contracts',
      gradient: 'from-orange-500 to-red-500',
      contracts: '150K+'
    },
    {
      name: 'Go',
      icon: '🐹',
      description: 'Cosmos SDK modules',
      gradient: 'from-cyan-500 to-blue-500',
      contracts: '75K+'
    }
  ]

  const securityStats = [
    { label: 'Vulnerabilities Detected', value: 125000, suffix: '+' },
    { label: 'Contracts Analyzed', value: 2500000, suffix: '+' },
    { label: 'Security Score', value: 99.7, suffix: '%' },
    { label: 'Response Time', value: 1.2, suffix: 's' }
  ]

  return (
    <div className="relative min-h-screen">
      {/* Animated Background */}
      <GradientBackground className="fixed inset-0 -z-10" />
      <ParticleField className="fixed inset-0 -z-10" particleCount={40} />

      <div className="relative z-10 space-y-32">
        {/* Enhanced Hero Section with Spline */}
        <motion.section
          ref={heroRef}
          className="relative min-h-screen flex items-center justify-center px-4 overflow-hidden"
        >
          {/* Spline 3D Scene - Background */}
          <div className="absolute inset-0 -z-10">
            <FloatingSpline
              className="w-full h-full opacity-30"
              amplitude={30}
              duration={6}
            />
          </div>

          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
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
                  <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
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
                    className="text-blue-400 font-bold"
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
                  <Button asChild size="lg" className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white shadow-lg">
                    <Link to="/analyze">
                      <Zap className="mr-2 h-5 w-5" />
                      Start Analysis
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                  </Button>
                </motion.div>

                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button asChild size="lg" variant="outline" className="border-2 border-white/20 backdrop-blur-sm">
                    <Link to="#features">
                      <Eye className="mr-2 h-5 w-5" />
                      View Demo
                    </Link>
                  </Button>
                </motion.div>
              </motion.div>
            </div>

            {/* Right Content - Interactive Spline */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={heroInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="relative h-96 lg:h-[500px]"
            >
              <InteractiveSpline className="w-full h-full rounded-2xl" />

              {/* Floating Stats */}
              <div className="absolute -top-4 -left-4 lg:-left-8">
                <FloatingElement delay={0} amplitude={15}>
                  <GlowCard className="p-4 text-center" glowColor="blue">
                    <div className="text-2xl font-bold text-blue-400">
                      <CountUp end={2500000} suffix="+" />
                    </div>
                    <div className="text-xs text-gray-500">Contracts Analyzed</div>
                  </GlowCard>
                </FloatingElement>
              </div>

              <div className="absolute -bottom-4 -right-4 lg:-right-8">
                <FloatingElement delay={1} amplitude={12}>
                  <GlowCard className="p-4 text-center" glowColor="purple">
                    <div className="text-2xl font-bold text-purple-400">
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
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
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
                <GlowCard glowColor={feature.color} className="h-full p-8">
                  <div className="text-center space-y-6">
                    <motion.div
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-r ${
                        feature.color === 'blue' ? 'from-blue-500 to-cyan-500' :
                        feature.color === 'purple' ? 'from-purple-500 to-pink-500' :
                        'from-green-500 to-emerald-500'
                      } flex items-center justify-center shadow-lg`}
                    >
                      <feature.icon className="h-8 w-8 text-white" />
                    </motion.div>

                    <div>
                      <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                      <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>

                    <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-2xl font-bold text-blue-400">
                        {feature.stats}
                      </div>
                    </div>
                  </div>
                </GlowCard>
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
            <h2 className="text-4xl md:text-5xl font-bold">
              Multi-Language{' '}
              <span className="bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
                Support
              </span>
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Analyze smart contracts written in different languages with unified security standards.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {supportedLanguages.map((lang, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <FloatingElement
                  delay={index * 0.5}
                  amplitude={15}
                  className="h-full"
                >
                  <GlowCard
                    glowColor={index === 0 ? 'blue' : index === 1 ? 'purple' : 'cyan'}
                    className="h-full p-8 bg-gradient-to-br from-gray-900/90 to-gray-800/90 border-gray-700"
                  >
                    <div className="text-center space-y-6">
                      <motion.div
                        whileHover={{ scale: 1.2, rotate: 10 }}
                        className="text-6xl mb-4"
                      >
                        {lang.icon}
                      </motion.div>

                      <div>
                        <h3 className="text-2xl font-bold text-white mb-2">{lang.name}</h3>
                        <p className="text-gray-300 mb-4">{lang.description}</p>

                        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${lang.gradient} text-white text-sm font-medium`}>
                          <Star className="h-4 w-4" />
                          {lang.contracts} contracts
                        </div>
                      </div>
                    </div>
                  </GlowCard>
                </FloatingElement>
              </motion.div>
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
                <span className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
                  Security Checks
                </span>
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                Our analysis engine detects a wide range of vulnerabilities and security issues.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {[
                { name: 'Reentrancy vulnerabilities', icon: '🔄', severity: 'Critical' },
                { name: 'Integer overflow/underflow', icon: '🔢', severity: 'High' },
                { name: 'Access control issues', icon: '🔐', severity: 'Critical' },
                { name: 'Timestamp dependence', icon: '⏰', severity: 'Medium' },
                { name: 'Gas limit problems', icon: '⛽', severity: 'High' },
                { name: 'Unchecked external calls', icon: '📞', severity: 'Critical' },
                { name: 'Logic errors', icon: '🧠', severity: 'High' },
                { name: 'Code quality issues', icon: '✨', severity: 'Low' }
              ].map((check, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <GlowCard className="p-6 hover:scale-105 transition-transform duration-300">
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl">{check.icon}</div>
                      <div className="flex-1">
                        <div className="font-medium">{check.name}</div>
                        <div className={`text-sm ${
                          check.severity === 'Critical' ? 'text-red-400' :
                          check.severity === 'High' ? 'text-orange-400' :
                          check.severity === 'Medium' ? 'text-yellow-400' :
                          'text-blue-400'
                        }`}>
                          {check.severity} Priority
                        </div>
                      </div>
                      <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0" />
                    </div>
                  </GlowCard>
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
                  <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
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
                  <Button asChild size="lg" className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white shadow-lg">
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
