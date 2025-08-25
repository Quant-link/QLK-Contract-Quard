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

export interface WebSocketMessage {
  type: string
  analysis_id?: string
  status?: string
  data?: any
  timestamp: string
  message?: string
  error?: string
}

export interface HealthResponse {
  status: string
  version: string
  timestamp: string
  uptime_seconds?: number
}

// UI Types
export interface UploadedFile {
  file: File
  content: string
  name: string
  size: number
  lastModified: number
}

// Enhanced Analysis Configuration
export interface AnalysisConfig {
  // Security Configuration
  security_level: SecurityLevel
  vulnerability_categories: VulnerabilityCategory[]
  custom_rules: CustomRule[]

  // Language-Specific Settings
  language_settings: LanguageSettings

  // Analysis Scope
  analysis_scope: AnalysisScope

  // Report Configuration
  report_config: ReportConfig

  // Notification Settings
  notification_config: NotificationConfig

  // Legacy fields (for backward compatibility)
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

export type SecurityLevel = 'basic' | 'standard' | 'advanced' | 'enterprise'

export interface VulnerabilityCategory {
  id: string
  name: string
  enabled: boolean
  severity_threshold: Finding['severity']
  description: string
  detectors: string[]
}

export interface CustomRule {
  id: string
  name: string
  description: string
  pattern: string
  severity: Finding['severity']
  enabled: boolean
  language?: 'solidity' | 'rust' | 'go' | 'all'
}

export interface LanguageSettings {
  solidity: SoliditySettings
  rust: RustSettings
  go: GoSettings
}

export interface SoliditySettings {
  compiler_version: string
  evm_version: string
  optimization_enabled: boolean
  optimization_runs: number
  enable_experimental_features: boolean
  custom_imports: string[]
}

export interface RustSettings {
  edition: '2018' | '2021'
  target: string
  features: string[]
  no_default_features: boolean
  enable_clippy: boolean
  clippy_config: Record<string, any>
}

export interface GoSettings {
  version: string
  build_tags: string[]
  cgo_enabled: boolean
  race_detection: boolean
  enable_vet: boolean
  vet_config: Record<string, any>
}

export interface AnalysisScope {
  type: 'full' | 'quick' | 'custom'
  include_dependencies: boolean
  include_test_files: boolean
  include_examples: boolean
  max_file_size_mb: number
  max_lines_per_file: number
  specific_functions?: string[]
  specific_contracts?: string[]
  exclude_patterns: string[]
}

export interface ReportConfig {
  format: ReportFormat[]
  detail_level: 'minimal' | 'standard' | 'detailed' | 'comprehensive'
  include_code_snippets: boolean
  include_recommendations: boolean
  include_references: boolean
  include_metrics: boolean
  group_by_severity: boolean
  group_by_category: boolean
  custom_template?: string
}

export type ReportFormat = 'json' | 'pdf' | 'html' | 'markdown' | 'csv'

export interface NotificationConfig {
  email_notifications: EmailNotificationConfig
  webhook_notifications: WebhookNotificationConfig
  slack_notifications: SlackNotificationConfig
  real_time_updates: boolean
}

export interface EmailNotificationConfig {
  enabled: boolean
  recipients: string[]
  on_completion: boolean
  on_critical_findings: boolean
  on_errors: boolean
  include_summary: boolean
}

export interface WebhookNotificationConfig {
  enabled: boolean
  url: string
  secret?: string
  events: WebhookEvent[]
  retry_attempts: number
  timeout_seconds: number
}

export type WebhookEvent = 'analysis_started' | 'analysis_completed' | 'analysis_failed' | 'critical_finding'

export interface SlackNotificationConfig {
  enabled: boolean
  webhook_url: string
  channel: string
  username: string
  on_completion: boolean
  on_critical_findings: boolean
}

// Analysis Settings Store State
export interface AnalysisSettingsState {
  config: AnalysisConfig
  presets: AnalysisPreset[]
  current_preset: string | null
  is_loading: boolean
  is_saving: boolean
  last_saved: string | null
  validation_errors: Record<string, string[]>
}

export interface AnalysisPreset {
  id: string
  name: string
  description: string
  config: AnalysisConfig
  is_default: boolean
  created_at: string
  updated_at: string
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
