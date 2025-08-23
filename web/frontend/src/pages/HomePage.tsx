import { Link } from 'react-router-dom'
import { Shield, Zap, Eye, ArrowRight, CheckCircle, BarChart3 } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import AnalyticsDashboard from '../components/dashboard/AnalyticsDashboard'

export default function HomePage() {
  const features = [
    {
      icon: Shield,
      title: 'Multi-Language Support',
      description: 'Analyze Solidity, Rust, and Go smart contracts with unified security analysis.'
    },
    {
      icon: Zap,
      title: 'AI-Augmented Analysis',
      description: 'Advanced static analysis powered by machine learning for comprehensive vulnerability detection.'
    },
    {
      icon: Eye,
      title: 'Real-time Results',
      description: 'Get instant feedback with detailed vulnerability reports and remediation suggestions.'
    }
  ]

  const supportedLanguages = [
    { name: 'Solidity', icon: '⟠', description: 'Ethereum smart contracts' },
    { name: 'Rust', icon: '🦀', description: 'Substrate & ink! contracts' },
    { name: 'Go', icon: '🐹', description: 'Cosmos SDK modules' }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            Secure Your Smart Contracts with{' '}
            <span className="gradient-text">AI-Powered Analysis</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            ContractQuard provides comprehensive security analysis for multi-language smart contracts,
            helping developers identify vulnerabilities before deployment.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild size="lg" variant="quantlink">
            <Link to="/analyze">
              Start Analysis <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link to="#features">Learn More</Link>
          </Button>
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
          {/* Supported Languages */}
          <section className="space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold">Supported Languages</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Comprehensive security analysis for multiple blockchain languages
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {supportedLanguages.map((lang, index) => (
                <Card key={index} className="text-center">
                  <CardHeader>
                    <div className="text-4xl mb-2">{lang.icon}</div>
                    <CardTitle>{lang.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{lang.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        </TabsContent>

        <TabsContent value="features" className="space-y-8">
          {/* Features Section */}
          <section id="features" className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Why Choose ContractQuard?</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Our advanced analysis engine combines traditional static analysis with AI-powered detection
            to provide the most comprehensive security assessment.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="text-center">
              <CardHeader>
                <feature.icon className="h-12 w-12 mx-auto text-Quantlink-cyan" />
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Supported Languages */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Multi-Language Support</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Analyze smart contracts written in different languages with unified security standards.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {supportedLanguages.map((lang, index) => (
            <Card key={index} className="text-center hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="text-4xl mb-2">{lang.icon}</div>
                <CardTitle>{lang.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{lang.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Security Checks */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Comprehensive Security Checks</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Our analysis engine detects a wide range of vulnerabilities and security issues.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          {[
            'Reentrancy vulnerabilities',
            'Integer overflow/underflow',
            'Access control issues',
            'Timestamp dependence',
            'Gas limit problems',
            'Unchecked external calls',
            'Logic errors',
            'Code quality issues'
          ].map((check, index) => (
            <div key={index} className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
              <span>{check}</span>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center space-y-8 bg-muted/50 rounded-lg p-8">
        <div className="space-y-4">
          <h2 className="text-3xl font-bold">Ready to Secure Your Contracts?</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Upload your smart contract files and get detailed security analysis in seconds.
          </p>
        </div>
        
        <Button asChild size="lg" variant="quantlink">
          <Link to="/analyze">
            Start Free Analysis <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </section>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-8">
          <AnalyticsDashboard />
        </TabsContent>
      </Tabs>
    </div>
  )
}
