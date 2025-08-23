import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Play, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import FileUpload from '@/components/analysis/FileUpload'
import AnalysisProgress from '@/components/analysis/AnalysisProgress'
import { UploadedFile } from '@/types'
import { useToast } from '@/hooks/use-toast'

export default function AnalysisPage() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const navigate = useNavigate()
  const { toast } = useToast()

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

    setIsAnalyzing(true)
    
    try {
      // For now, we'll analyze the first file
      // In a real implementation, you might want to analyze all files
      const firstFile = uploadedFiles[0]
      
      const formData = new FormData()
      formData.append('file', firstFile.file)

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }

      const result = await response.json()
      setAnalysisId(result.analysis_id)
      
      toast({
        title: "Analysis started",
        description: "Your smart contract is being analyzed. This may take a few moments."
      })

    } catch (error) {
      console.error('Analysis error:', error)
      setIsAnalyzing(false)
      toast({
        title: "Analysis failed",
        description: error instanceof Error ? error.message : "An unexpected error occurred.",
        variant: "destructive"
      })
    }
  }

  const handleAnalysisComplete = () => {
    setIsAnalyzing(false)
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
