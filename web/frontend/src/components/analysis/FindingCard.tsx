import { useState } from 'react'
import { ChevronDown, ChevronRight, AlertTriangle, Info, Bug, Shield } from 'lucide-react'
import { Card, CardContent, CardHeader } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible'
import { Finding } from '../../types'
import { getSeverityBadgeColor } from '../../lib/utils'

interface FindingCardProps {
  finding: Finding
  index: number
}

export default function FindingCard({ finding, index }: FindingCardProps) {
  const [isOpen, setIsOpen] = useState(false)

  const getSeverityIcon = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      case 'HIGH':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />
      case 'MEDIUM':
        return <Bug className="h-4 w-4 text-yellow-600" />
      case 'LOW':
        return <Info className="h-4 w-4 text-blue-600" />
      case 'INFO':
        return <Shield className="h-4 w-4 text-gray-600" />
      default:
        return <Info className="h-4 w-4 text-gray-600" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'border-l-red-500'
      case 'HIGH':
        return 'border-l-orange-500'
      case 'MEDIUM':
        return 'border-l-yellow-500'
      case 'LOW':
        return 'border-l-blue-500'
      case 'INFO':
        return 'border-l-gray-500'
      default:
        return 'border-l-gray-500'
    }
  }

  return (
    <Card className={`border-l-4 ${getSeverityColor(finding.severity)}`}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-sm font-mono text-muted-foreground">
                  #{index + 1}
                </span>
                {getSeverityIcon(finding.severity)}
                <div className="flex-1">
                  <h3 className="font-semibold text-left">{finding.title}</h3>
                  <p className="text-sm text-muted-foreground text-left">
                    {finding.detector}
                    {finding.line_number && ` • Line ${finding.line_number}`}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Badge 
                  variant="outline" 
                  className={getSeverityBadgeColor(finding.severity)}
                >
                  {finding.severity}
                </Badge>
                <Button variant="ghost" size="sm">
                  {isOpen ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <CardContent className="pt-0 space-y-4">
            {/* Description */}
            <div>
              <h4 className="font-medium mb-2">Description</h4>
              <p className="text-sm text-muted-foreground">{finding.description}</p>
            </div>

            {/* Code Snippet */}
            {finding.code_snippet && (
              <div>
                <h4 className="font-medium mb-2">Code Snippet</h4>
                <div className="bg-muted rounded-md p-3 font-mono text-sm overflow-x-auto">
                  <pre className="whitespace-pre-wrap">{finding.code_snippet}</pre>
                </div>
              </div>
            )}

            {/* Location */}
            {(finding.line_number || finding.column) && (
              <div>
                <h4 className="font-medium mb-2">Location</h4>
                <div className="text-sm text-muted-foreground">
                  {finding.line_number && `Line: ${finding.line_number}`}
                  {finding.line_number && finding.column && ' • '}
                  {finding.column && `Column: ${finding.column}`}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="flex flex-wrap gap-2">
              {finding.confidence && (
                <div className="px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                  Confidence: {finding.confidence}
                </div>
              )}
              {finding.impact && (
                <div className="px-2 py-1 rounded-md text-xs font-medium bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
                  Impact: {finding.impact}
                </div>
              )}
              {finding.cwe_id && (
                <div className="px-2 py-1 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
                  CWE-{finding.cwe_id}
                </div>
              )}
              {finding.category && (
                <div className="px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                  {finding.category}
                </div>
              )}
            </div>

            {/* Recommendation */}
            {finding.recommendation && (
              <div>
                <h4 className="font-medium mb-2">Recommendation</h4>
                <div className="bg-green-50 border border-green-200 rounded-md p-3 dark:bg-green-900/20 dark:border-green-800">
                  <p className="text-sm text-green-800 dark:text-green-300">{finding.recommendation}</p>
                </div>
              </div>
            )}

            {/* References */}
            {finding.references && finding.references.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">References</h4>
                <div className="space-y-1">
                  {finding.references.map((ref, index) => (
                    <a
                      key={index}
                      href={ref}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 underline block"
                    >
                      {ref}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}
