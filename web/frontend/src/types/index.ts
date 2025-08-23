// API Types
export interface Finding {
  id: string
  detector: string
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
  title: string
  description: string
  line_number?: number
  column?: number
  code_snippet?: string
  recommendation?: string
  confidence?: string
  impact?: string
  cwe_id?: number
  references?: string[]
  category?: string
}

export interface AnalysisMetadata {
  filename: string
  file_size: number
  total_findings: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  info_count: number
  analysis_duration_ms?: number
  language?: string
  lines_of_code?: number
  risk_score?: number
}

export interface AnalysisResponse {
  analysis_id: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  findings: Finding[]
  metadata: AnalysisMetadata
  timestamp: string
  error_message?: string
}

export interface HealthResponse {
  status: string
  version: string
  timestamp: string
  uptime_seconds?: number
}

export interface WebSocketMessage {
  type: string
  analysis_id?: string
  status?: string
  data?: any
  timestamp: string
  message?: string
  error?: string
}

// UI Types
export interface UploadedFile {
  file: File
  content: string
  name: string
  size: number
  lastModified: number
}

export interface AnalysisConfig {
  detectors?: Record<string, DetectorConfig>
  min_severity?: Finding['severity']
  include_test_files?: boolean
  max_file_size_mb?: number
}

export interface DetectorConfig {
  enabled: boolean
  severity_override?: Finding['severity']
  custom_params?: Record<string, any>
}

// Theme Types
export type Theme = 'dark' | 'light' | 'system'

// Navigation Types
export interface NavItem {
  title: string
  href: string
  icon?: React.ComponentType<{ className?: string }>
  disabled?: boolean
}

// Chart Types
export interface ChartData {
  name: string
  value: number
  color: string
}

// Error Types
export interface ApiError {
  detail: string
  error_code?: string
  timestamp: string
}

// File Types
export type SupportedFileType = '.sol' | '.rs' | '.go'

export interface FileTypeInfo {
  extension: SupportedFileType
  language: string
  icon: string
  color: string
}
