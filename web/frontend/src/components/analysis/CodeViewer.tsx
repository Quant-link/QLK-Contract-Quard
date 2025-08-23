import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check, Maximize2, Minimize2, AlertTriangle, Download } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { useTheme } from '../theme-provider'
import { useToast } from '../../hooks/use-toast'
import { Finding } from '../../types'

interface CodeViewerProps {
  code: string
  language: string
  filename?: string
  findings?: Finding[]
  highlightLines?: number[]
  maxHeight?: number
}

export default function CodeViewer({
  code,
  language,
  filename,
  findings = [],
  highlightLines = [],
  maxHeight = 400
}: CodeViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [copied, setCopied] = useState(false)
  const [selectedLine, setSelectedLine] = useState<number | null>(null)
  const { theme } = useTheme()
  const { toast } = useToast()
  // const codeRef = useRef<HTMLDivElement>(null)

  const getLanguageFromFilename = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'sol':
        return 'solidity'
      case 'rs':
        return 'rust'
      case 'go':
        return 'go'
      case 'js':
      case 'ts':
        return 'typescript'
      default:
        return 'text'
    }
  }

  const displayLanguage = filename ? getLanguageFromFilename(filename) : language

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      toast({
        title: "Code copied",
        description: "Code has been copied to clipboard."
      })
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy code to clipboard.",
        variant: "destructive"
      })
    }
  }

  // Create findings map for quick lookup
  const findingsMap = new Map<number, Finding[]>()
  findings.forEach(finding => {
    if (finding.line_number) {
      const lineFindings = findingsMap.get(finding.line_number) || []
      lineFindings.push(finding)
      findingsMap.set(finding.line_number, lineFindings)
    }
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return theme === 'dark' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(239, 68, 68, 0.1)'
      case 'HIGH':
        return theme === 'dark' ? 'rgba(249, 115, 22, 0.2)' : 'rgba(249, 115, 22, 0.1)'
      case 'MEDIUM':
        return theme === 'dark' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(245, 158, 11, 0.1)'
      case 'LOW':
        return theme === 'dark' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.1)'
      default:
        return theme === 'dark' ? 'rgba(107, 114, 128, 0.2)' : 'rgba(107, 114, 128, 0.1)'
    }
  }

  const getSeverityBorderColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'rgb(239, 68, 68)'
      case 'HIGH':
        return 'rgb(249, 115, 22)'
      case 'MEDIUM':
        return 'rgb(245, 158, 11)'
      case 'LOW':
        return 'rgb(59, 130, 246)'
      default:
        return 'rgb(107, 114, 128)'
    }
  }

  const customStyle = {
    ...((theme === 'dark' ? oneDark : oneLight) as any),
    'pre[class*="language-"]': {
      ...((theme === 'dark' ? oneDark : oneLight) as any)['pre[class*="language-"]'],
      margin: 0,
      padding: '1rem',
      maxHeight: isExpanded ? 'none' : `${maxHeight}px`,
      overflow: 'auto',
    },
  }

  const lineProps = (lineNumber: number) => {
    const lineFindings = findingsMap.get(lineNumber) || []
    const hasFindings = lineFindings.length > 0
    const isHighlighted = highlightLines.includes(lineNumber)

    let backgroundColor = 'transparent'
    let borderLeft = 'none'

    if (hasFindings) {
      // Get highest severity finding for this line
      const highestSeverity = lineFindings.reduce((highest, finding) => {
        const severityOrder = { 'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'INFO': 1 }
        return severityOrder[finding.severity] > severityOrder[highest.severity] ? finding : highest
      }, lineFindings[0])

      backgroundColor = getSeverityColor(highestSeverity.severity)
      borderLeft = `3px solid ${getSeverityBorderColor(highestSeverity.severity)}`
    } else if (isHighlighted) {
      backgroundColor = theme === 'dark' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.05)'
      borderLeft = '3px solid rgb(59, 130, 246)'
    }

    if (selectedLine === lineNumber) {
      backgroundColor = theme === 'dark' ? 'rgba(59, 130, 246, 0.3)' : 'rgba(59, 130, 246, 0.2)'
    }

    return {
      style: {
        backgroundColor,
        borderLeft,
        display: 'block',
        width: '100%',
        cursor: hasFindings ? 'pointer' : 'default',
        paddingLeft: (hasFindings || isHighlighted) ? '8px' : '0',
        marginLeft: (hasFindings || isHighlighted) ? '-8px' : '0',
      },
      onClick: hasFindings ? () => setSelectedLine(lineNumber) : undefined
    }
  }

  const downloadCode = () => {
    const blob = new Blob([code], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'code.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">
            {filename || `Code (${displayLanguage})`}
          </CardTitle>
          <div className="flex items-center space-x-2">
            {findings.length > 0 && (
              <div className="flex items-center space-x-2 mr-4">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                <span className="text-sm text-muted-foreground">
                  {findings.length} issue{findings.length !== 1 ? 's' : ''} found
                </span>
              </div>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={downloadCode}
              className="h-8 w-8 p-0"
            >
              <Download className="h-4 w-4" />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={copyToClipboard}
              className="h-8 w-8 p-0"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-8 w-8 p-0"
            >
              {isExpanded ? (
                <Minimize2 className="h-4 w-4" />
              ) : (
                <Maximize2 className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative">
          <SyntaxHighlighter
            language={displayLanguage}
            style={customStyle}
            showLineNumbers
            lineProps={lineProps}
            customStyle={{
              margin: 0,
              borderRadius: '0 0 0.5rem 0.5rem',
            }}
          >
            {code}
          </SyntaxHighlighter>
          
          {!isExpanded && code.split('\n').length > 20 && (
            <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-background to-transparent flex items-end justify-center pb-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsExpanded(true)}
                className="bg-background"
              >
                <Maximize2 className="h-4 w-4 mr-2" />
                Show More
              </Button>
            </div>
          )}
        </div>

        {/* Selected Line Details */}
        {selectedLine && findingsMap.has(selectedLine) && (
          <div className="border-t p-4 bg-muted/30">
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Line {selectedLine} Issues:
            </h4>
            <div className="space-y-3">
              {findingsMap.get(selectedLine)?.map((finding, index) => (
                <div key={index} className="p-3 bg-background rounded-md border">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant={finding.severity === 'CRITICAL' ? 'destructive' : 'outline'}>
                      {finding.severity}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{finding.detector}</span>
                  </div>
                  <h5 className="font-medium mb-1">{finding.title}</h5>
                  <p className="text-sm text-muted-foreground mb-2">{finding.description}</p>
                  {finding.recommendation && (
                    <div className="bg-blue-50 border border-blue-200 rounded p-2">
                      <p className="text-sm text-blue-800">{finding.recommendation}</p>
                    </div>
                  )}
                  {finding.cwe_id && (
                    <div className="mt-2">
                      <Badge variant="outline" className="text-xs">
                        CWE-{finding.cwe_id}
                      </Badge>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
