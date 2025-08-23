import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Play, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import FileUpload from '@/components/analysis/FileUpload'
import AnalysisProgress from '@/components/analysis/AnalysisProgress'
import { UploadedFile } from '@/types'
import { useToast } from '@/hooks/use-toast'
import { useAnalysis } from '@/hooks/useAnalysis'
import { useAnalysisStore } from '@/store/analysisStore'
import { useWebSocket } from '@/hooks/useWebSocket'

export default function AnalysisPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { analyzeFile, isAnalyzing } = useAnalysis()
  const {
    uploadedFiles,
    setUploadedFiles,
    resetAnalysisSession,
    addToHistory
  } = useAnalysisStore()

  const [analysisId, setAnalysisId] = useState<string | null>(null)

  // WebSocket for real-time updates
  const { subscribe } = useWebSocket({
    onConnect: () => console.log('Connected to WebSocket'),
    onError: (error) => console.error('WebSocket error:', error)
  })

  // Subscribe to WebSocket events
  useEffect(() => {
    const unsubscribe = subscribe('analysis_complete', (data) => {
      if (data.analysis_id === analysisId) {
        handleAnalysisComplete()
      }
    })

    return unsubscribe
  }, [analysisId, subscribe])

  const handleFilesSelected = (files: UploadedFile[]) => {
    setUploadedFiles(files)
  }

  const startAnalysis = async () => {
    if (uploadedFiles.length === 0) {
      toast({
        title: "No files selected",
        description: "Please upload at least one smart contract file to analyze.",
        variant: "destructive"
      })
      return
    }

    try {
      // Analyze the first file (for now)
      const firstFile = uploadedFiles[0]
      const result = await analyzeFile(firstFile.file)

      if (result) {
        setAnalysisId(result.analysis_id)
        addToHistory(result)

        toast({
          title: "Analysis completed",
          description: `Found ${result.metadata.total_findings} security findings.`
        })

        // Navigate to results after a short delay
        setTimeout(() => {
          navigate(`/results/${result.analysis_id}`)
        }, 1000)
      }
    } catch (error) {
      console.error('Analysis error:', error)
      toast({
        title: "Analysis failed",
        description: "An unexpected error occurred during analysis.",
        variant: "destructive"
      })
    }
  }

  const handleAnalysisComplete = () => {
    if (analysisId) {
      navigate(`/results/${analysisId}`)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold">Smart Contract Analysis</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Upload your smart contract files to get comprehensive security analysis 
          with AI-powered vulnerability detection.
        </p>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="upload" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload" disabled={isAnalyzing}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Files
          </TabsTrigger>
          <TabsTrigger value="settings" disabled={isAnalyzing}>
            <Settings className="mr-2 h-4 w-4" />
            Analysis Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-6">
          {/* File Upload */}
          <FileUpload 
            onFilesSelected={handleFilesSelected}
            maxFiles={5}
            maxSize={10}
          />

          {/* Analysis Controls */}
          {uploadedFiles.length > 0 && !isAnalyzing && (
            <Card>
              <CardHeader>
                <CardTitle>Ready to Analyze</CardTitle>
                <CardDescription>
                  {uploadedFiles.length} file(s) uploaded and ready for security analysis.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={startAnalysis}
                  size="lg"
                  variant="quantlink"
                  className="w-full"
                >
                  <Play className="mr-2 h-4 w-4" />
                  Start Security Analysis
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Analysis Progress */}
          {isAnalyzing && (
            <AnalysisProgress
              isAnalyzing={isAnalyzing}
              onComplete={handleAnalysisComplete}
            />
          )}
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Configuration</CardTitle>
              <CardDescription>
                Customize the security analysis settings for your smart contracts.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-12 w-12 mx-auto mb-4" />
                <p>Analysis settings will be available in a future update.</p>
                <p className="text-sm">Currently using default security analysis configuration.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Help Section */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-lg">Need Help?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground">
            • Supported file types: Solidity (.sol), Rust (.rs), Go (.go)
          </p>
          <p className="text-sm text-muted-foreground">
            • Maximum file size: 10MB per file
          </p>
          <p className="text-sm text-muted-foreground">
            • Analysis typically takes 30-60 seconds depending on contract complexity
          </p>
          <p className="text-sm text-muted-foreground">
            • Results include vulnerability details, severity levels, and remediation suggestions
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
