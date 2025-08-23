import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Download,
  Share2,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Code,
  BarChart3,
  Shield,
  Bug,
  Zap
} from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Separator } from '../ui/separator'
import { apiService } from '../../services/api'
import { AnalysisResponse } from '../../types'
import { formatDate, formatDuration, getRiskLevel, getSeverityColor, getLanguageInfo } from '../../lib/utils'
import CodeViewer from './CodeViewer'
import FindingCard from './FindingCard'

export default function EnhancedAnalysisResults() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const navigate = useNavigate()
  
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [fileContent, setFileContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (analysisId) {
      fetchAnalysisData()
    }
  }, [analysisId])

  const fetchAnalysisData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch analysis data
      const analysisData = await apiService.getAnalysis(analysisId!)
      setAnalysis(analysisData)

      // Fetch code content
      const codeResponse = await fetch(`http://localhost:8000/api/analysis/${analysisId}/code`)
      if (codeResponse.ok) {
        const codeData = await codeResponse.json()
        setFileContent(codeData.content)
      }
    } catch (err) {
      console.error('Error fetching analysis:', err)
      setError(err instanceof Error ? err.message : 'Failed to load analysis')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: 'json' | 'pdf' | 'csv') => {
    try {
      const blob = await apiService.exportAnalysis(analysisId!, format)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analysis-${analysisId}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading analysis results...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              Error Loading Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">{error}</p>
            <div className="flex gap-2">
              <Button onClick={() => navigate('/')} variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Go Back
              </Button>
              <Button onClick={fetchAnalysisData}>
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Analysis Not Found</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">The requested analysis could not be found.</p>
            <Button onClick={() => navigate('/')} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const riskLevel = getRiskLevel(analysis.metadata.risk_score || 0)
  const languageInfo = getLanguageInfo(analysis.metadata.language || 'unknown')

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button 
            onClick={() => navigate('/')} 
            variant="outline" 
            size="sm"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {analysis.metadata.filename}
            </h1>
            <div className="flex items-center gap-4 mt-2">
              <Badge variant="outline" className={languageInfo.color}>
                {languageInfo.icon} {languageInfo.name}
              </Badge>
              <span className="text-sm text-gray-500">
                Analyzed {formatDate(analysis.metadata.created_at)}
              </span>
              <span className="text-sm text-gray-500">
                Duration: {formatDuration(analysis.metadata.analysis_duration_ms)}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button onClick={() => handleExport('json')} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
          <Button onClick={() => handleExport('pdf')} variant="outline" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      {/* Risk Score Overview */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className={`text-4xl font-bold ${riskLevel.color} mb-2`}>
                {analysis.metadata.risk_score}
              </div>
              <div className={`text-sm font-medium px-3 py-1 rounded-full ${riskLevel.bgColor} ${riskLevel.color}`}>
                {riskLevel.level} Risk
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 mb-2">
                {analysis.metadata.total_findings}
              </div>
              <div className="text-sm text-gray-600">Total Findings</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600 mb-2">
                {analysis.metadata.critical_count + analysis.metadata.high_count}
              </div>
              <div className="text-sm text-gray-600">Critical & High</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 mb-2">
                {analysis.metadata.file_size}
              </div>
              <div className="text-sm text-gray-600">Lines of Code</div>
            </div>
          </div>
          
          <Separator className="my-6" />
          
          {/* Severity Breakdown */}
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Severity Breakdown</h4>
            {[
              { label: 'Critical', count: analysis.metadata.critical_count, color: 'bg-red-500' },
              { label: 'High', count: analysis.metadata.high_count, color: 'bg-orange-500' },
              { label: 'Medium', count: analysis.metadata.medium_count, color: 'bg-yellow-500' },
              { label: 'Low', count: analysis.metadata.low_count, color: 'bg-blue-500' },
              { label: 'Info', count: analysis.metadata.info_count, color: 'bg-gray-500' }
            ].map(({ label, count, color }) => (
              <div key={label} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${color}`}></div>
                  <span className="text-sm font-medium">{label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">{count}</span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${color}`}
                      style={{ 
                        width: `${analysis.metadata.total_findings > 0 ? (count / analysis.metadata.total_findings) * 100 : 0}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="findings" className="flex items-center gap-2">
            <Bug className="h-4 w-4" />
            Findings ({analysis.findings.length})
          </TabsTrigger>
          <TabsTrigger value="code" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Code
          </TabsTrigger>
          <TabsTrigger value="timeline" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Timeline
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Recommendations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Analysis Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">File Size</span>
                  <span className="font-medium">{analysis.metadata.file_size} bytes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Language</span>
                  <span className="font-medium">{languageInfo.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Analysis Time</span>
                  <span className="font-medium">{formatDuration(analysis.metadata.analysis_duration_ms)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status</span>
                  <Badge variant="outline" className="text-green-600 bg-green-50">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Completed
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Top Findings */}
            <Card>
              <CardHeader>
                <CardTitle>Critical Issues</CardTitle>
                <CardDescription>
                  Most severe security findings that require immediate attention
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysis.findings
                    .filter(f => f.severity === 'CRITICAL' || f.severity === 'HIGH')
                    .slice(0, 3)
                    .map((finding, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                        <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {finding.title}
                          </p>
                          <p className="text-xs text-gray-500">
                            Line {finding.line_number} • {finding.detector}
                          </p>
                        </div>
                        <Badge 
                          variant="outline" 
                          className={getSeverityColor(finding.severity)}
                        >
                          {finding.severity}
                        </Badge>
                      </div>
                    ))}
                  {analysis.findings.filter(f => f.severity === 'CRITICAL' || f.severity === 'HIGH').length === 0 && (
                    <div className="text-center py-4 text-gray-500">
                      <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                      No critical or high severity issues found
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="findings" className="mt-6">
          <div className="space-y-4">
            {analysis.findings.length > 0 ? (
              analysis.findings.map((finding, index) => (
                <FindingCard 
                  key={index} 
                  finding={finding} 
                  fileContent={fileContent}
                />
              ))
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No Security Issues Found
                  </h3>
                  <p className="text-gray-600">
                    Great! Your code appears to be free of common security vulnerabilities.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="code" className="mt-6">
          <CodeViewer 
            content={fileContent}
            language={analysis.metadata.language}
            findings={analysis.findings}
          />
        </TabsContent>

        <TabsContent value="timeline" className="mt-6">
          <AnalysisTimeline analysis={analysis} />
        </TabsContent>

        <TabsContent value="recommendations" className="mt-6">
          <SecurityRecommendations findings={analysis.findings} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
