import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Download, Share2, RefreshCw, AlertTriangle, CheckCircle, Clock, FileText, Brain } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Separator } from '../components/ui/separator'
import AnalysisSummary from '../components/analysis/AnalysisSummary'
import FindingCard from '../components/analysis/FindingCard'
import CodeViewer from '../components/analysis/CodeViewer'
import AIAnalysisSection from '../components/analysis/AIAnalysisSection'
import { AnalysisResponse } from '../types'
import { apiService } from '../services/api'
import { useToast } from '../hooks/use-toast'
import { formatDistanceToNow } from 'date-fns'

export default function AnalysisResultsPage() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string>('')
  const { toast } = useToast()

  useEffect(() => {
    if (analysisId) {
      fetchAnalysis()
    }
  }, [analysisId])

  const fetchAnalysis = async () => {
    try {
      setLoading(true)
      const result = await apiService.getAnalysis(analysisId!)
      setAnalysis(result)

      // Fetch the original code content
      try {
        const codeResponse = await fetch(`http://localhost:8000/api/analysis/${analysisId}/code`)
        if (codeResponse.ok) {
          const codeData = await codeResponse.json()
          setFileContent(codeData.content)
        }
      } catch (err) {
        console.error('Failed to fetch code content:', err)
        // Fallback to empty content
        setFileContent('')
      }
    } catch (err) {
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
      
      toast({
        title: "Export successful",
        description: `Analysis exported as ${format.toUpperCase()}`
      })
    } catch (err) {
      toast({
        title: "Export failed",
        description: "Failed to export analysis",
        variant: "destructive"
      })
    }
  }

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-600'
    if (score >= 60) return 'text-orange-600'
    if (score >= 40) return 'text-yellow-600'
    if (score >= 20) return 'text-blue-600'
    return 'text-green-600'
  }

  const getRiskBadgeVariant = (score: number) => {
    if (score >= 80) return 'destructive'
    if (score >= 60) return 'secondary'
    return 'outline'
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center space-y-4">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
            <p className="text-muted-foreground">Loading analysis results...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center space-y-4">
          <AlertTriangle className="h-12 w-12 mx-auto text-red-500" />
          <h1 className="text-2xl font-bold">Analysis Not Found</h1>
          <p className="text-muted-foreground">{error || 'The requested analysis could not be found.'}</p>
          <Button asChild>
            <Link to="/analyze">Start New Analysis</Link>
          </Button>
        </div>
      </div>
    )
  }

  const criticalFindings = analysis.findings.filter(f => f.severity === 'CRITICAL')
  const highFindings = analysis.findings.filter(f => f.severity === 'HIGH')
  const mediumFindings = analysis.findings.filter(f => f.severity === 'MEDIUM')
  const lowFindings = analysis.findings.filter(f => f.severity === 'LOW')
  const infoFindings = analysis.findings.filter(f => f.severity === 'INFO')

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/analyze">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Analysis
            </Link>
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <div>
            <h1 className="text-3xl font-bold">{analysis.metadata.filename}</h1>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <span>Analysis completed {formatDistanceToNow(new Date(analysis.timestamp), { addSuffix: true })}</span>
              <span>•</span>
              <span>ID: {analysis.analysis_id.substring(0, 8)}...</span>
              <span>•</span>
              <span>{analysis.metadata.language?.toUpperCase()} Contract</span>
              <span>•</span>
              <span>{(analysis.metadata.file_size / 1024).toFixed(1)} KB</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
            <Download className="h-4 w-4 mr-2" />
            JSON
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('pdf')}>
            <Download className="h-4 w-4 mr-2" />
            PDF
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      {/* Risk Score Banner */}
      <Card className="border-l-4 border-l-red-500">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <div className={`text-4xl font-bold ${getRiskColor(analysis.metadata.risk_score || 0)}`}>
                  {analysis.metadata.risk_score || 0}
                </div>
                <div className="text-sm text-muted-foreground">Risk Score</div>
              </div>
              <Separator orientation="vertical" className="h-12" />
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <span className="text-sm font-medium">
                    {criticalFindings.length + highFindings.length} Critical/High Issues
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    {analysis.metadata.lines_of_code || 'N/A'} lines of code analyzed
                  </span>
                </div>
              </div>
            </div>
            
            <div className="text-right space-y-2">
              <Badge variant={getRiskBadgeVariant(analysis.metadata.risk_score || 0)} className="text-lg px-3 py-1">
                {(analysis.metadata.risk_score || 0) >= 80 ? 'CRITICAL RISK' :
                 (analysis.metadata.risk_score || 0) >= 60 ? 'HIGH RISK' :
                 (analysis.metadata.risk_score || 0) >= 40 ? 'MEDIUM RISK' :
                 (analysis.metadata.risk_score || 0) >= 20 ? 'LOW RISK' : 'MINIMAL RISK'}
              </Badge>
              <div className="text-sm text-muted-foreground">
                Analysis Duration: {analysis.metadata.analysis_duration_ms}ms
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary */}
      <AnalysisSummary metadata={analysis.metadata} timestamp={analysis.timestamp} />

      {/* Main Content */}
      <Tabs defaultValue="findings" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="findings" className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Findings ({analysis.findings.length})
          </TabsTrigger>
          <TabsTrigger value="ai-analysis" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            AI Analysis
          </TabsTrigger>
          <TabsTrigger value="code" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Code Review
          </TabsTrigger>
          <TabsTrigger value="timeline" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Timeline
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            Recommendations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="findings" className="space-y-6">
          {/* Findings by Severity */}
          {criticalFindings.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-600 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Critical Issues ({criticalFindings.length})
              </h3>
              <div className="space-y-4">
                {criticalFindings.map((finding, index) => (
                  <FindingCard key={finding.id} finding={finding} index={index} />
                ))}
              </div>
            </div>
          )}

          {highFindings.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-600 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                High Priority Issues ({highFindings.length})
              </h3>
              <div className="space-y-4">
                {highFindings.map((finding, index) => (
                  <FindingCard key={finding.id} finding={finding} index={index} />
                ))}
              </div>
            </div>
          )}

          {mediumFindings.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-600 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Medium Priority Issues ({mediumFindings.length})
              </h3>
              <div className="space-y-4">
                {mediumFindings.map((finding, index) => (
                  <FindingCard key={finding.id} finding={finding} index={index} />
                ))}
              </div>
            </div>
          )}

          {lowFindings.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-600 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Low Priority Issues ({lowFindings.length})
              </h3>
              <div className="space-y-4">
                {lowFindings.map((finding, index) => (
                  <FindingCard key={finding.id} finding={finding} index={index} />
                ))}
              </div>
            </div>
          )}

          {infoFindings.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-600 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Informational ({infoFindings.length})
              </h3>
              <div className="space-y-4">
                {infoFindings.map((finding, index) => (
                  <FindingCard key={finding.id} finding={finding} index={index} />
                ))}
              </div>
            </div>
          )}

          {analysis.findings.length === 0 && (
            <Card>
              <CardContent className="pt-6 text-center">
                <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Issues Found</h3>
                <p className="text-muted-foreground">
                  Great! No security vulnerabilities were detected in your contract.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="ai-analysis" className="space-y-6">
          <AIAnalysisSection
            findings={analysis.findings}
            analysisMetrics={{
              complexity_score: analysis.metadata.complexity_score,
              security_score: 100 - (analysis.metadata.risk_score || 0),
              gas_efficiency: analysis.metadata.gas_efficiency,
              code_quality: analysis.metadata.code_quality
            }}
          />
        </TabsContent>

        <TabsContent value="code" className="space-y-6">
          <CodeViewer
            code={fileContent}
            language={analysis.metadata.language || 'sol'}
            findings={analysis.findings}
            filename={analysis.metadata.filename}
          />
        </TabsContent>

        <TabsContent value="timeline" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="font-medium">Analysis Started</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(analysis.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="font-medium">Code Parsing Completed</p>
                    <p className="text-sm text-muted-foreground">
                      {analysis.metadata.lines_of_code} lines processed
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="font-medium">Vulnerability Detection</p>
                    <p className="text-sm text-muted-foreground">
                      {analysis.findings.length} issues identified
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="font-medium">Analysis Completed</p>
                    <p className="text-sm text-muted-foreground">
                      Duration: {analysis.metadata.analysis_duration_ms}ms
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Recommendations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {analysis.findings.length > 0 ? (
                <div className="space-y-4">
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h4 className="font-semibold text-red-900 mb-2">Immediate Actions Required</h4>
                    <ul className="space-y-1 text-sm text-red-800">
                      {criticalFindings.length > 0 && (
                        <li>• Address {criticalFindings.length} critical security vulnerabilities</li>
                      )}
                      {highFindings.length > 0 && (
                        <li>• Fix {highFindings.length} high-priority security issues</li>
                      )}
                    </ul>
                  </div>
                  
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-2">Best Practices</h4>
                    <ul className="space-y-1 text-sm text-blue-800">
                      <li>• Implement comprehensive access controls</li>
                      <li>• Use the checks-effects-interactions pattern</li>
                      <li>• Add input validation for all public functions</li>
                      <li>• Consider using OpenZeppelin's security libraries</li>
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Excellent Security Posture</h3>
                  <p className="text-muted-foreground">
                    Your contract follows security best practices. Continue monitoring for new vulnerabilities.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
