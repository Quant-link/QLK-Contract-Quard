import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AnalysisResponse, UploadedFile } from '@/types'

interface AnalysisState {
  // Current analysis session
  uploadedFiles: UploadedFile[]
  currentAnalysis: AnalysisResponse | null
  isAnalyzing: boolean
  analysisProgress: number
  currentStep: string | null
  
  // Analysis history
  analysisHistory: AnalysisResponse[]
  
  // UI state
  selectedSeverityFilter: string
  searchTerm: string
  
  // Actions
  setUploadedFiles: (files: UploadedFile[]) => void
  addUploadedFile: (file: UploadedFile) => void
  removeUploadedFile: (index: number) => void
  clearUploadedFiles: () => void
  
  setCurrentAnalysis: (analysis: AnalysisResponse | null) => void
  setIsAnalyzing: (analyzing: boolean) => void
  setAnalysisProgress: (progress: number) => void
  setCurrentStep: (step: string | null) => void
  
  addToHistory: (analysis: AnalysisResponse) => void
  removeFromHistory: (analysisId: string) => void
  clearHistory: () => void
  
  setSeverityFilter: (filter: string) => void
  setSearchTerm: (term: string) => void
  
  // Reset functions
  resetAnalysisSession: () => void
  resetAll: () => void
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set, get) => ({
      // Initial state
      uploadedFiles: [],
      currentAnalysis: null,
      isAnalyzing: false,
      analysisProgress: 0,
      currentStep: null,
      analysisHistory: [],
      selectedSeverityFilter: 'all',
      searchTerm: '',

      // File management actions
      setUploadedFiles: (files) => set({ uploadedFiles: files }),
      
      addUploadedFile: (file) => set((state) => ({
        uploadedFiles: [...state.uploadedFiles, file]
      })),
      
      removeUploadedFile: (index) => set((state) => ({
        uploadedFiles: state.uploadedFiles.filter((_, i) => i !== index)
      })),
      
      clearUploadedFiles: () => set({ uploadedFiles: [] }),

      // Analysis state actions
      setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
      
      setIsAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
      
      setAnalysisProgress: (progress) => set({ analysisProgress: progress }),
      
      setCurrentStep: (step) => set({ currentStep: step }),

      // History management
      addToHistory: (analysis) => set((state) => {
        // Avoid duplicates
        const existingIndex = state.analysisHistory.findIndex(
          item => item.analysis_id === analysis.analysis_id
        )
        
        if (existingIndex >= 0) {
          // Update existing entry
          const newHistory = [...state.analysisHistory]
          newHistory[existingIndex] = analysis
          return { analysisHistory: newHistory }
        } else {
          // Add new entry (keep only last 10)
          const newHistory = [analysis, ...state.analysisHistory].slice(0, 10)
          return { analysisHistory: newHistory }
        }
      }),
      
      removeFromHistory: (analysisId) => set((state) => ({
        analysisHistory: state.analysisHistory.filter(
          item => item.analysis_id !== analysisId
        )
      })),
      
      clearHistory: () => set({ analysisHistory: [] }),

      // UI state actions
      setSeverityFilter: (filter) => set({ selectedSeverityFilter: filter }),
      
      setSearchTerm: (term) => set({ searchTerm: term }),

      // Reset functions
      resetAnalysisSession: () => set({
        uploadedFiles: [],
        currentAnalysis: null,
        isAnalyzing: false,
        analysisProgress: 0,
        currentStep: null,
      }),
      
      resetAll: () => set({
        uploadedFiles: [],
        currentAnalysis: null,
        isAnalyzing: false,
        analysisProgress: 0,
        currentStep: null,
        analysisHistory: [],
        selectedSeverityFilter: 'all',
        searchTerm: '',
      }),
    }),
    {
      name: 'contractquard-analysis-store',
      // Only persist certain parts of the state
      partialize: (state) => ({
        analysisHistory: state.analysisHistory,
        selectedSeverityFilter: state.selectedSeverityFilter,
      }),
    }
  )
)

// Selectors for computed values
export const useAnalysisSelectors = () => {
  const store = useAnalysisStore()
  
  return {
    // Get filtered findings based on current filters
    getFilteredFindings: (findings: any[]) => {
      let filtered = findings
      
      if (store.selectedSeverityFilter !== 'all') {
        filtered = filtered.filter(finding => 
          finding.severity.toLowerCase() === store.selectedSeverityFilter.toLowerCase()
        )
      }
      
      if (store.searchTerm) {
        const term = store.searchTerm.toLowerCase()
        filtered = filtered.filter(finding =>
          finding.title.toLowerCase().includes(term) ||
          finding.description.toLowerCase().includes(term) ||
          finding.detector.toLowerCase().includes(term)
        )
      }
      
      return filtered
    },
    
    // Get recent analyses
    getRecentAnalyses: (limit = 5) => {
      return store.analysisHistory.slice(0, limit)
    },
    
    // Check if file is already uploaded
    isFileUploaded: (filename: string) => {
      return store.uploadedFiles.some(file => file.name === filename)
    },
  }
}
