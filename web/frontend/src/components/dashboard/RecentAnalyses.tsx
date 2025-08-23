import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MoreHorizontal, Eye, Download, Trash2, AlertTriangle, CheckCircle, Clock, FileText, Shield } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../ui/dropdown-menu'
import { Progress } from '../ui/progress'
import { apiService } from '../../services/api'
import { useToast } from '../../hooks/use-toast'
import { formatDistanceToNow } from 'date-fns'
import { AnalysisResponse } from '../../types'

interface RecentAnalysesProps {
  limit?: number
  showHeader?: boolean
  compact?: boolean
}

export default function RecentAnalyses({ limit = 10, showHeader = true, compact = false }: RecentAnalysesProps) {
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    fetchAnalyses()
  }, [limit])

  const fetchAnalyses = async () => {
    try {
      setLoading(true)
      const result = await apiService.getAnalyses({ limit })
      setAnalyses(result.analyses)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analyses')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (analysisId: string) => {
    try {
      await apiService.deleteAnalysis(analysisId)
      setAnalyses(prev => prev.filter(a => a.analysis_id !== analysisId))
      toast({
        title: "Analysis deleted",
        description: "The analysis has been successfully deleted."
      })
    } catch (err) {
      toast({
        title: "Delete failed",
        description: "Failed to delete the analysis.",
        variant: "destructive"
      })
    }
  }

  const handleExport = async (analysisId: string, format: 'json' | 'pdf' | 'csv') => {
    try {
      const blob = await apiService.exportAnalysis(analysisId, format)
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'failed':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      case 'in_progress':
        return <Clock className="h-4 w-4 text-blue-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Completed</Badge>
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>
      case 'in_progress':
        return <Badge variant="secondary">In Progress</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  const getRiskBadge = (score: number) => {
    if (score >= 80) return <Badge variant="destructive">Critical</Badge>
    if (score >= 60) return <Badge variant="secondary" className="bg-orange-100 text-orange-800">High</Badge>
    if (score >= 40) return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Medium</Badge>
    if (score >= 20) return <Badge variant="outline" className="text-blue-600">Low</Badge>
    return <Badge variant="outline" className="text-green-600">Minimal</Badge>
  }

  const getLanguageIcon = (language: string) => {
    switch (language.toLowerCase()) {
      case 'sol':
        return '⟠'
      case 'rs':
        return '🦀'
      case 'go':
        return '🐹'
      default:
        return '📄'
    }
  }

  const getLanguageColor = (language: string) => {
    switch (language.toLowerCase()) {
      case 'sol':
        return 'text-blue-600 bg-blue-50'
      case 'rs':
        return 'text-orange-600 bg-orange-50'
      case 'go':
        return 'text-cyan-600 bg-cyan-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  if (loading) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Analyses
            </CardTitle>
          </CardHeader>
        )}
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4 p-4 border rounded-lg animate-pulse">
                <div className="w-8 h-8 bg-gray-200 rounded"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="w-16 h-6 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Analyses
            </CardTitle>
          </CardHeader>
        )}
        <CardContent>
          <div className="text-center py-8">
            <AlertTriangle className="h-8 w-8 mx-auto text-red-500 mb-2" />
            <p className="text-muted-foreground">{error}</p>
            <Button variant="outline" size="sm" onClick={fetchAnalyses} className="mt-2">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (compact) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Analyses
            </CardTitle>
          </CardHeader>
        )}
        <CardContent>
          <div className="space-y-3">
            {analyses.slice(0, 5).map((analysis) => (
              <div key={analysis.analysis_id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="text-lg">{getLanguageIcon(analysis.language || 'unknown')}</div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{analysis.filename || 'Unknown file'}</p>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <span>{(analysis.language || 'unknown').toUpperCase()}</span>
                      <span>•</span>
                      <span>{analysis.total_findings || 0} findings</span>
                      <span>•</span>
                      <span>{formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getRiskBadge(analysis.risk_score || 0)}
                  <Button variant="ghost" size="sm" asChild>
                    <Link to={`/analysis/${analysis.analysis_id}`}>
                      <Eye className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
          {analyses.length > 5 && (
            <div className="mt-4 text-center">
              <Button variant="outline" size="sm" asChild>
                <Link to="/analyses">View All Analyses</Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      {showHeader && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Analyses
            </CardTitle>
            <Button variant="outline" size="sm" onClick={fetchAnalyses}>
              <Shield className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
      )}
      <CardContent>
        {analyses.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Analyses Yet</h3>
            <p className="text-muted-foreground mb-4">
              Start by uploading a smart contract for security analysis.
            </p>
            <Button asChild>
              <Link to="/analyze">Start Analysis</Link>
            </Button>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>File</TableHead>
                <TableHead>Language</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead>Findings</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {analyses.map((analysis) => (
                <TableRow key={analysis.analysis_id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="text-lg">{getLanguageIcon(analysis.language || 'unknown')}</div>
                      <div>
                        <Link
                          to={`/analysis/${analysis.analysis_id}`}
                          className="font-medium hover:underline"
                        >
                          {analysis.filename || 'Unknown file'}
                        </Link>
                        <div className="text-sm text-muted-foreground">
                          ID: {analysis.analysis_id.substring(0, 8)}...
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getLanguageColor(analysis.language || 'unknown')}>
                      {(analysis.language || 'unknown').toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(analysis.status)}
                      {getStatusBadge(analysis.status)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <div className="w-16">
                        <Progress value={analysis.risk_score || 0} className="h-2" />
                      </div>
                      <span className="text-sm font-medium">{analysis.risk_score || 0}/100</span>
                      {getRiskBadge(analysis.risk_score || 0)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      <div className="text-sm font-medium">{analysis.total_findings || 0} total</div>
                      <div className="flex space-x-1">
                        {(analysis.critical_count || 0) > 0 && (
                          <Badge variant="destructive" className="text-xs px-1">
                            {analysis.critical_count}C
                          </Badge>
                        )}
                        {(analysis.high_count || 0) > 0 && (
                          <Badge variant="secondary" className="text-xs px-1 bg-orange-100 text-orange-800">
                            {analysis.high_count}H
                          </Badge>
                        )}
                        {(analysis.medium_count || 0) > 0 && (
                          <Badge variant="secondary" className="text-xs px-1 bg-yellow-100 text-yellow-800">
                            {analysis.medium_count}M
                          </Badge>
                        )}
                        {(analysis.low_count || 0) > 0 && (
                          <Badge variant="outline" className="text-xs px-1">
                            {analysis.low_count}L
                          </Badge>
                        )}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-muted-foreground">
                      {analysis.analysis_duration_ms || 0}ms
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-muted-foreground">
                      {formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true })}
                    </div>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem asChild>
                          <Link to={`/analysis/${analysis.analysis_id}`}>
                            <Eye className="h-4 w-4 mr-2" />
                            View Details
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleExport(analysis.analysis_id, 'json')}>
                          <Download className="h-4 w-4 mr-2" />
                          Export JSON
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleExport(analysis.analysis_id, 'pdf')}>
                          <Download className="h-4 w-4 mr-2" />
                          Export PDF
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          onClick={() => handleDelete(analysis.analysis_id)}
                          className="text-red-600"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
