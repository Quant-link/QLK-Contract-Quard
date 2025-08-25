import { Link } from 'react-router-dom'
import { Shield, Zap, Eye, ArrowRight, CheckCircle, Brain, Sparkles, Star } from 'lucide-react'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Button } from '../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { AnimatedBackground, FloatingElements } from '../components/ui/animated-background'
import { TypingAnimation, AnimatedText, GlitchText, CountUp } from '../components/ui/typing-animation'
import { InteractiveCard, FloatingCard, GlassmorphismCard, NeonCard } from '../components/ui/interactive-card'
import AnalyticsDashboard from '../components/dashboard/AnalyticsDashboard'

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null)
  const featuresRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll()

  const heroInView = useInView(heroRef, { once: true })
  const featuresInView = useInView(featuresRef, { once: true })

  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%'])
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])

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
    <div className="relative">
      {/* Animated Background */}
      <AnimatedBackground />
      <FloatingElements />

      <div className="relative z-10 space-y-32">
        {/* Enhanced Hero Section */}
        <motion.section
          ref={heroRef}
          style={{ y, opacity }}
          className="relative min-h-screen flex items-center justify-center text-center px-4"
        >
          <div className="max-w-6xl mx-auto space-y-12">
            {/* Main Heading */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={heroInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="space-y-6"
            >
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={heroInView ? { scale: 1, opacity: 1 } : {}}
                transition={{ duration: 1, delay: 0.5 }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 backdrop-blur-sm"
              >
                <Sparkles className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                  AI-Powered Security Analysis
                </span>
              </motion.div>

              <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight">
                <AnimatedText delay={0.8} className="block">
                  Secure Your
                </AnimatedText>
                <div className="relative">
                  <GlitchText className="block bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                    Smart Contracts
                  </GlitchText>
                </div>
                <div className="text-3xl md:text-4xl lg:text-5xl mt-4 text-muted-foreground">
                  with{' '}
                  <TypingAnimation
                    texts={[
                      'AI Intelligence',
                      'Advanced Analysis',
                      'Real-time Detection',
                      'Enterprise Security'
                    ]}
                    className="text-blue-600 dark:text-blue-400 font-bold"
                  />
                </div>
              </h1>

              <motion.p
                initial={{ opacity: 0, y: 30 }}
                animate={heroInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8, delay: 1.5 }}
                className="text-xl md:text-2xl text-muted-foreground max-w-4xl mx-auto leading-relaxed"
              >
                ContractQuard provides enterprise-grade security analysis for multi-language smart contracts,
                powered by advanced AI to identify vulnerabilities before deployment.
              </motion.p>
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={heroInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 2 }}
              className="flex flex-col sm:flex-row gap-6 justify-center items-center"
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button asChild size="lg" className="text-lg px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg shadow-blue-500/25">
                  <Link to="/analyze">
                    <Zap className="mr-2 h-5 w-5" />
                    Start Analysis
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button asChild size="lg" variant="outline" className="text-lg px-8 py-4 border-2">
                  <Link to="#features">
                    <Eye className="mr-2 h-5 w-5" />
                    View Demo
                  </Link>
                </Button>
              </motion.div>
            </motion.div>

            {/* Stats Section */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={heroInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 2.5 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16"
            >
              {securityStats.map((stat, index) => (
                <GlassmorphismCard key={index} className="p-6 text-center">
                  <div className="text-3xl md:text-4xl font-bold text-blue-600 dark:text-blue-400">
                    <CountUp
                      end={stat.value}
                      duration={3}
                      suffix={stat.suffix}
                    />
                  </div>
                  <div className="text-sm text-muted-foreground mt-2">
                    {stat.label}
                  </div>
                </GlassmorphismCard>
              ))}
            </motion.div>
          </div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 3, duration: 1 }}
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center"
            >
              <motion.div
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-1 h-3 bg-gray-400 rounded-full mt-2"
              />
            </motion.div>
          </motion.div>
        </motion.section>

        {/* Enhanced Features Section */}
        <motion.section
          ref={featuresRef}
          id="features"
          className="space-y-16 py-20"
        >
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8 }}
            className="text-center space-y-6"
          >
            <h2 className="text-4xl md:text-5xl font-bold">
              Why Choose{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ContractQuard?
              </span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
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
                <InteractiveCard glowColor={feature.color} className="h-full p-8">
                  <div className="text-center space-y-6">
                    <motion.div
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-r ${
                        feature.color === 'blue' ? 'from-blue-500 to-cyan-500' :
                        feature.color === 'purple' ? 'from-purple-500 to-pink-500' :
                        'from-green-500 to-emerald-500'
                      } flex items-center justify-center`}
                    >
                      <feature.icon className="h-8 w-8 text-white" />
                    </motion.div>

                    <div>
                      <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </div>

                    <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {feature.stats}
                      </div>
                    </div>
                  </div>
                </InteractiveCard>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Supported Languages Section */}
        <section className="space-y-16 py-20">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center space-y-6"
          >
            <h2 className="text-4xl md:text-5xl font-bold">
              Multi-Language{' '}
              <span className="bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">
                Support
              </span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
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
                <FloatingCard
                  delay={index * 0.5}
                  amplitude={15}
                  className="h-full"
                >
                  <NeonCard color={index === 0 ? 'blue' : index === 1 ? 'purple' : 'cyan'} className="h-full p-8">
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
                  </NeonCard>
                </FloatingCard>
              </motion.div>
            ))}
          </div>
        </section>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-8">
        <TabsList className="grid w-full grid-cols-3">
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
                <span className="bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent">
                  Security Checks
                </span>
              </h2>
              <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
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
                  <GlassmorphismCard className="p-6 hover:scale-105 transition-transform duration-300">
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl">{check.icon}</div>
                      <div className="flex-1">
                        <div className="font-medium">{check.name}</div>
                        <div className={`text-sm ${
                          check.severity === 'Critical' ? 'text-red-500' :
                          check.severity === 'High' ? 'text-orange-500' :
                          check.severity === 'Medium' ? 'text-yellow-500' :
                          'text-blue-500'
                        }`}>
                          {check.severity} Priority
                        </div>
                      </div>
                      <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    </div>
                  </GlassmorphismCard>
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
            <GlassmorphismCard className="p-12 max-w-4xl mx-auto">
              <div className="space-y-6">
                <h2 className="text-4xl md:text-5xl font-bold">
                  Ready to{' '}
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Secure
                  </span>{' '}
                  Your Contracts?
                </h2>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                  Upload your smart contract files and get detailed security analysis in seconds.
                </p>

                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="pt-4"
                >
                  <Button asChild size="lg" className="text-lg px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg shadow-blue-500/25">
                    <Link to="/analyze">
                      <Zap className="mr-2 h-5 w-5" />
                      Start Free Analysis
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                  </Button>
                </motion.div>
              </div>
            </GlassmorphismCard>
          </motion.section>
        </TabsContent>

        <TabsContent value="features" className="space-y-8">
          <div className="text-center py-20">
            <h3 className="text-2xl font-bold text-muted-foreground">
              Features are showcased in the main hero section above
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
