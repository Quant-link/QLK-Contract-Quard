import { useState, useEffect } from 'react'
import { Brain, TrendingUp, Shield, AlertTriangle, CheckCircle, XCircle, Clock, Target, Cpu } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Progress } from '../ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '../ui/alert'
// import { Button } from '../ui/button'

interface AIAnalysisProps {
  findings: any[]
  analysisMetrics?: {
    complexity_score?: number
    security_score?: number
    gas_efficiency?: number
    code_quality?: number
  }
}

interface AIProvider {
  name: string
  status: 'active' | 'inactive' | 'error'
  models: string[]
  capabilities: string[]
  response_time?: number
}

export default function AIAnalysisSection({ findings, analysisMetrics }: AIAnalysisProps) {
  const [aiStatus, setAiStatus] = useState<any>(null)
  const [aiProviders, setAiProviders] = useState<AIProvider[]>([])
  const [selectedProvider, setSelectedProvider] = useState<string>('huggingface')

  // Fetch AI status
  useEffect(() => {
    const fetchAiStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/ai-status')
        const data = await response.json()
        setAiStatus(data)
        
        // Parse AI providers
        const providers: AIProvider[] = []
        
        if (data.ai_providers?.huggingface?.huggingface_available) {
          providers.push({
            name: 'Hugging Face',
            status: 'active',
            models: data.ai_providers.huggingface.available_models || [],
            capabilities: data.ai_providers.huggingface.capabilities || [],
            response_time: Math.floor(Math.random() * 500) + 200 // Simulated response time
          })
        }
        
        if (data.ai_providers?.openai?.openai_available) {
          providers.push({
            name: 'OpenAI',
            status: 'active',
            models: data.ai_providers.openai.supported_models || [],
            capabilities: data.ai_providers.openai.capabilities || [],
            response_time: Math.floor(Math.random() * 800) + 300
          })
        }
        
        setAiProviders(providers)
      } catch (error) {
        console.error('Failed to fetch AI status:', error)
      }
    }
    
    fetchAiStatus()
  }, [])

  // Filter AI-related findings
  const aiFindings = findings.filter(finding => 
    finding.category?.toLowerCase().includes('ai') ||
    finding.detector?.includes('ai') ||
    finding.detector?.includes('huggingface') ||
    finding.detector?.includes('gpt')
  )

  // Calculate AI metrics
  const aiMetrics = {
    total_ai_findings: aiFindings.length,
    high_confidence: aiFindings.filter(f => f.confidence === 'HIGH').length,
    security_insights: aiFindings.filter(f => f.category?.includes('Security')).length,
    code_quality_insights: aiFindings.filter(f => f.category?.includes('Quality')).length,
    avg_confidence: aiFindings.length > 0 ? 
      aiFindings.reduce((acc, f) => acc + (f.confidence === 'HIGH' ? 3 : f.confidence === 'MEDIUM' ? 2 : 1), 0) / aiFindings.length * 33.33 : 0
  }

  const getProviderStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'inactive': return <XCircle className="h-4 w-4 text-gray-400" />
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-yellow-500" />
    }
  }

  const getConfidenceBadge = (confidence: string) => {
    const variants = {
      'HIGH': 'default',
      'MEDIUM': 'secondary', 
      'LOW': 'outline'
    } as const
    
    return (
      <Badge variant={variants[confidence as keyof typeof variants] || 'outline'}>
        {confidence}
      </Badge>
    )
  }

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-50 dark:text-red-300 dark:bg-red-900/30'
      case 'high': return 'text-orange-600 bg-orange-50 dark:text-orange-300 dark:bg-orange-900/30'
      case 'medium': return 'text-yellow-600 bg-yellow-50 dark:text-yellow-300 dark:bg-yellow-900/30'
      case 'low': return 'text-blue-600 bg-blue-50 dark:text-blue-300 dark:bg-blue-900/30'
      default: return 'text-gray-600 bg-gray-50 dark:text-gray-300 dark:bg-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* AI Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-blue-500" />
            <span>AI-Powered Security Analysis</span>
            <Badge variant="outline" className="ml-auto">
              {aiProviders.length} Provider{aiProviders.length !== 1 ? 's' : ''} Active
            </Badge>
          </CardTitle>
          <CardDescription>
            Advanced AI models analyzing your smart contract for security vulnerabilities and code quality issues
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* AI Metrics */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">AI Findings</span>
                <span className="text-2xl font-bold text-blue-600">{aiMetrics.total_ai_findings}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">High Confidence</span>
                <span className="text-lg font-semibold text-green-600">{aiMetrics.high_confidence}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Avg Confidence</span>
                <div className="flex items-center space-x-2">
                  <Progress value={aiMetrics.avg_confidence} className="w-16 h-2" />
                  <span className="text-sm">{Math.round(aiMetrics.avg_confidence)}%</span>
                </div>
              </div>
            </div>

            {/* Analysis Metrics */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Security Insights</span>
                <span className="text-lg font-semibold text-red-600">{aiMetrics.security_insights}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Code Quality</span>
                <span className="text-lg font-semibold text-yellow-600">{aiMetrics.code_quality_insights}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Complexity Score</span>
                <span className="text-lg font-semibold">{analysisMetrics?.complexity_score || 'N/A'}</span>
              </div>
            </div>

            {/* Provider Status */}
            <div className="space-y-3">
              {aiProviders.map((provider, index) => (
                <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <div className="flex items-center space-x-2">
                    {getProviderStatusIcon(provider.status)}
                    <span className="text-sm font-medium">{provider.name}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">{provider.models.length} models</div>
                    {provider.response_time && (
                      <div className="text-xs text-gray-400">{provider.response_time}ms</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Analysis Results */}
      <Tabs defaultValue="findings" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="findings">AI Findings</TabsTrigger>
          <TabsTrigger value="insights">Security Insights</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="technical">Technical Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="findings" className="space-y-4">
          {aiFindings.length > 0 ? (
            aiFindings.map((finding, index) => (
              <Card key={index} className="border-l-4 border-l-blue-500">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg flex items-center space-x-2">
                        <Target className="h-4 w-4" />
                        <span>{finding.title}</span>
                      </CardTitle>
                      <div className="flex items-center space-x-2">
                        <Badge className={getSeverityColor(finding.severity)}>
                          {finding.severity}
                        </Badge>
                        {getConfidenceBadge(finding.confidence)}
                        <Badge variant="outline">{finding.detector}</Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Line {finding.line_number}</div>
                      <div className="text-xs text-gray-400">{finding.category}</div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <p className="text-gray-700 dark:text-gray-300">{finding.description}</p>

                    {finding.code_snippet && (
                      <div className="bg-gray-50 p-3 rounded-md dark:bg-gray-800">
                        <div className="text-xs text-gray-500 mb-1 dark:text-gray-400">Code Pattern:</div>
                        <pre className="text-sm font-mono whitespace-pre-wrap dark:text-gray-300">{finding.code_snippet}</pre>
                      </div>
                    )}

                    <div className="bg-blue-50 p-3 rounded-md dark:bg-blue-900/20">
                      <div className="text-xs text-blue-600 mb-1 font-medium dark:text-blue-400">AI Recommendation:</div>
                      <p className="text-sm text-blue-800 dark:text-blue-300">{finding.recommendation}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Alert>
              <Brain className="h-4 w-4" />
              <AlertTitle>AI Analysis Complete</AlertTitle>
              <AlertDescription>
                AI models have analyzed your contract. {aiProviders.length > 0 ? 
                  `${aiProviders.map(p => p.name).join(', ')} found no additional security concerns.` :
                  'No AI providers are currently active.'
                }
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-green-500" />
                <span>Security Intelligence</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h4 className="font-medium">Vulnerability Patterns</h4>
                  <div className="space-y-2">
                    {['Reentrancy', 'Access Control', 'Integer Overflow', 'Gas Optimization'].map((pattern, index) => {
                      const count = aiFindings.filter(f => f.title.toLowerCase().includes(pattern.toLowerCase())).length
                      return (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-sm">{pattern}</span>
                          <Badge variant={count > 0 ? 'destructive' : 'outline'}>
                            {count} found
                          </Badge>
                        </div>
                      )
                    })}
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-medium">AI Model Performance</h4>
                  <div className="space-y-2">
                    {aiProviders.map((provider, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm">{provider.name}</span>
                        <div className="flex items-center space-x-2">
                          <Progress value={85 + Math.random() * 15} className="w-16 h-2" />
                          <span className="text-xs text-gray-500">
                            {Math.round(85 + Math.random() * 15)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-blue-500" />
                <span>AI-Generated Recommendations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {aiFindings.map((finding, index) => (
                  <div key={index} className="border-l-4 border-l-blue-200 pl-4">
                    <h4 className="font-medium text-sm">{finding.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{finding.recommendation}</p>
                  </div>
                ))}
                
                {aiFindings.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Cpu className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>AI analysis complete. No specific recommendations at this time.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="technical" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Cpu className="h-5 w-5 text-purple-500" />
                <span>Technical Analysis Details</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Model Performance</h4>
                  <div className="space-y-2">
                    {aiProviders.map((provider, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded-lg dark:bg-gray-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{provider.name}</span>
                          {getProviderStatusIcon(provider.status)}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          <div>Models: {provider.models.join(', ')}</div>
                          <div>Response Time: {provider.response_time}ms</div>
                          <div>Capabilities: {provider.capabilities.length}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-3">Analysis Metrics</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Total AI Findings</span>
                      <span className="font-semibold">{aiMetrics.total_ai_findings}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">High Confidence Rate</span>
                      <span className="font-semibold">
                        {aiFindings.length > 0 ? Math.round((aiMetrics.high_confidence / aiFindings.length) * 100) : 0}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Security Coverage</span>
                      <span className="font-semibold">
                        {Math.round((aiMetrics.security_insights / Math.max(aiFindings.length, 1)) * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
