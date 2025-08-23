import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Download, Share, Filter, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import AnalysisSummary from '@/components/analysis/AnalysisSummary'
import FindingCard from '@/components/analysis/FindingCard'
import { AnalysisResponse, Finding } from '@/types'
import { useToast } from '@/hooks/use-toast'

export default function ResultsPage() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null)
  const [filteredFindings, setFilteredFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const { toast } = useToast()

  useEffect(() => {
    const fetchResults = async () => {
      if (!analysisId) {
        setError('No analysis ID provided')
        setLoading(false)
        return
      }

      try {
        const response = await fetch(`/api/analysis/${analysisId}`)
        
        if (!response.ok) {
          if (response.status === 404) {
            setError('Analysis results not found. Results may have expired or the analysis ID is invalid.')
          } else {
            throw new Error(`Failed to fetch results: ${response.statusText}`)
          }
          return
        }

        const data: AnalysisResponse = await response.json()
        setAnalysisResult(data)
        setFilteredFindings(data.findings)
      } catch (err) {
        console.error('Error fetching results:', err)
        setError(err instanceof Error ? err.message : 'Failed to load analysis results')
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [analysisId])

  useEffect(() => {
    if (!analysisResult) return

    let filtered = analysisResult.findings

    // Apply severity filter
    if (severityFilter !== 'all') {
      filtered = filtered.filter(finding => 
        finding.severity.toLowerCase() === severityFilter.toLowerCase()
      )
    }

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(finding =>
        finding.title.toLowerCase().includes(term) ||
        finding.description.toLowerCase().includes(term) ||
        finding.detector.toLowerCase().includes(term)
      )
    }

    setFilteredFindings(filtered)
  }, [analysisResult, searchTerm, severityFilter])

  const handleExport = () => {
    if (!analysisResult) return

    const dataStr = JSON.stringify(analysisResult, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `contractquard-analysis-${analysisId}.json`
    link.click()
    URL.revokeObjectURL(url)

    toast({
      title: "Export successful",
      description: "Analysis results have been downloaded as JSON file."
    })
  }

  const handleShare = async () => {
    const url = window.location.href
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'ContractQuard Analysis Results',
          text: 'Check out this smart contract security analysis',
          url: url
        })
      } catch (err) {
        // User cancelled sharing
      }
    } else {
      // Fallback to clipboard
      try {
        await navigator.clipboard.writeText(url)
        toast({
          title: "Link copied",
          description: "Analysis results link has been copied to clipboard."
        })
      } catch (err) {
        toast({
          title: "Share failed",
          description: "Unable to copy link to clipboard.",
          variant: "destructive"
        })
      }
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded"></div>
            ))}
          </div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-24 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Results</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline">
              <Link to="/analyze">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Start New Analysis
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!analysisResult) {
    return null
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Button asChild variant="ghost" size="sm">
              <Link to="/analyze">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Analysis
              </Link>
            </Button>
          </div>
          <h1 className="text-3xl font-bold">Analysis Results</h1>
          <p className="text-muted-foreground">
            Security analysis for {analysisResult.metadata.filename}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleShare}>
            <Share className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary */}
      <AnalysisSummary 
        metadata={analysisResult.metadata} 
        timestamp={analysisResult.timestamp}
      />

      {/* Findings Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Security Findings</h2>
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search findings..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64"
              />
            </div>

            {/* Severity Filter */}
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-40">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Filter by severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="info">Info</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Findings List */}
        {filteredFindings.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-muted-foreground">
                {analysisResult.findings.length === 0 
                  ? "No security issues found! Your contract looks clean." 
                  : "No findings match your current filters."
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredFindings.map((finding, index) => (
              <FindingCard 
                key={finding.id} 
                finding={finding} 
                index={index}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
