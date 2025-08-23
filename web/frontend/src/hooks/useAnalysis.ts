import { useState, useCallback } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiService, handleApiError } from '../services/api'
import { AnalysisResponse } from '../types'
import { useToast } from '../hooks/use-toast'

export function useAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const { toast } = useToast()

  // Mutation for file analysis
  const analyzeFileMutation = useMutation({
    mutationFn: (file: File) => apiService.analyzeFile(file),
    onMutate: () => {
      setIsAnalyzing(true)
    },
    onSuccess: (data: AnalysisResponse) => {
      setIsAnalyzing(false)
      toast({
        title: "Analysis completed",
        description: `Found ${data.metadata.total_findings} security findings.`,
      })
    },
    onError: (error) => {
      setIsAnalyzing(false)
      const errorMessage = handleApiError(error)
      toast({
        title: "Analysis failed",
        description: errorMessage,
        variant: "destructive",
      })
    },
  })

  // Function to analyze a single file
  const analyzeFile = useCallback(async (file: File): Promise<AnalysisResponse | null> => {
    try {
      const result = await analyzeFileMutation.mutateAsync(file)
      return result
    } catch (error) {
      console.error('Analysis error:', error)
      return null
    }
  }, [analyzeFileMutation])

  // Function to analyze multiple files
  const analyzeMultipleFiles = useCallback(async (files: File[]): Promise<AnalysisResponse[]> => {
    const results: AnalysisResponse[] = []
    
    for (const file of files) {
      try {
        const result = await analyzeFile(file)
        if (result) {
          results.push(result)
        }
      } catch (error) {
        console.error(`Failed to analyze ${file.name}:`, error)
      }
    }
    
    return results
  }, [analyzeFile])

  return {
    analyzeFile,
    analyzeMultipleFiles,
    isAnalyzing: isAnalyzing || analyzeFileMutation.isPending,
    error: analyzeFileMutation.error,
    reset: analyzeFileMutation.reset,
  }
}

// Hook for fetching analysis results
export function useAnalysisResult(analysisId: string | undefined) {
  return useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: () => apiService.getAnalysisResult(analysisId!),
    enabled: !!analysisId,
    retry: 1,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Hook for health check
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: apiService.healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
    retry: 3,
  })
}
