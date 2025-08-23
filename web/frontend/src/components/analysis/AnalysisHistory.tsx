import { Link } from 'react-router-dom'
import { Clock, FileText, Trash2 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { useAnalysisStore } from '../../store/analysisStore'
import { formatDate, formatFileSize } from '../../lib/utils'
import { AnalysisResponse } from '../../types'

export default function AnalysisHistory() {
  const { analysisHistory, removeFromHistory, clearHistory } = useAnalysisStore()

  if (analysisHistory.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">No analysis history yet.</p>
          <p className="text-sm text-muted-foreground mt-1">
            Your completed analyses will appear here.
          </p>
        </CardContent>
      </Card>
    )
  }

  const getRiskBadgeVariant = (metadata: AnalysisResponse['metadata']) => {
    if (metadata.critical_count > 0) return 'critical'
    if (metadata.high_count > 0) return 'high'
    if (metadata.medium_count > 0) return 'medium'
    if (metadata.low_count > 0) return 'low'
    return 'info'
  }

  const getRiskLevel = (metadata: AnalysisResponse['metadata']) => {
    if (metadata.critical_count > 0) return 'Critical'
    if (metadata.high_count > 0) return 'High'
    if (metadata.medium_count > 0) return 'Medium'
    if (metadata.low_count > 0) return 'Low'
    return 'Clean'
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Analysis History</CardTitle>
            <CardDescription>
              Your recent security analysis results
            </CardDescription>
          </div>
          {analysisHistory.length > 0 && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={clearHistory}
              className="text-muted-foreground hover:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {analysisHistory.map((analysis) => (
          <div
            key={analysis.analysis_id}
            className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <FileText className="h-8 w-8 text-muted-foreground" />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="font-medium truncate">
                    {analysis.metadata.filename}
                  </h3>
                  <Badge variant={getRiskBadgeVariant(analysis.metadata)}>
                    {getRiskLevel(analysis.metadata)}
                  </Badge>
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <span>{formatFileSize(analysis.metadata.file_size)}</span>
                  <span>•</span>
                  <span>{analysis.metadata.total_findings} findings</span>
                  <span>•</span>
                  <span>{formatDate(analysis.timestamp)}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button asChild variant="outline" size="sm">
                <Link to={`/results/${analysis.analysis_id}`}>
                  View Results
                </Link>
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFromHistory(analysis.analysis_id)}
                className="text-muted-foreground hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
