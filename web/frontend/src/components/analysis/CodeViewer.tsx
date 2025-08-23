import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check, Maximize2, Minimize2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useTheme } from '@/components/theme-provider'
import { useToast } from '@/hooks/use-toast'

interface CodeViewerProps {
  code: string
  language: string
  filename?: string
  highlightLines?: number[]
  maxHeight?: number
}

export default function CodeViewer({ 
  code, 
  language, 
  filename, 
  highlightLines = [],
  maxHeight = 400 
}: CodeViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [copied, setCopied] = useState(false)
  const { theme } = useTheme()
  const { toast } = useToast()

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
    const isHighlighted = highlightLines.includes(lineNumber)
    return {
      style: {
        backgroundColor: isHighlighted 
          ? theme === 'dark' 
            ? 'rgba(239, 68, 68, 0.2)' 
            : 'rgba(239, 68, 68, 0.1)'
          : 'transparent',
        display: 'block',
        width: '100%',
      }
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">
            {filename || `Code (${displayLanguage})`}
          </CardTitle>
          <div className="flex items-center space-x-2">
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
      </CardContent>
    </Card>
  )
}
