export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export interface AnalysisStatistics {
  total_findings: number;
  analysis_time_seconds: number;
  severity_breakdown: Record<Severity, number>;
  detector_breakdown: Record<string, number>;
  files_analyzed: number;
  solc_version?: string;
  vulnerability_type_breakdown?: Record<string, number>;
  timestamp?: string;
}

export interface SourceLocation {
  file_path: string;
  line_start: number;
  line_end?: number;
  column_start?: number;
  column_end?: number;
}

export interface Finding {
  finding_id: string;
  title: string;
  description: string;
  severity: Severity;
  location: SourceLocation;
  vulnerability_type: string;
  confidence: number;
  code_snippet?: string;
  recommendation?: string;
  references?: string[];
  metadata?: Record<string, any>;
  detector_name: string;
  timestamp?: string;
}

export interface AnalysisResult {
  analysis_id: string;
  status: 'started' | 'running' | 'analyzing' | 'processing' | 'completed' | 'error';
  file_name: string;
  findings: Finding[];
  statistics: AnalysisStatistics;
  started_at: string;
  completed_at?: string;
  error?: string;
  solc_version?: string;
}

export interface Detector {
  name: string;
  description: string;
  vulnerability_types: string[];
  enabled: boolean;
  default_severity: Severity;
}

export interface DetectorConfig {
  enabled: boolean;
  severity_override?: Severity;
  custom_params?: Record<string, any>;
}

export interface AnalysisConfig {
  detectors?: Record<string, DetectorConfig>;
  min_severity?: Severity;
  include_test_files?: boolean;
  max_file_size_mb?: number;
}

export interface WebSocketMessage {
  type: 'analysis_update' | 'echo' | 'error';
  analysis_id?: string;
  status?: string;
  data?: any;
  timestamp: string;
  message?: string;
  error?: string;
}

export interface UploadedFile {
  file: File;
  content: string;
  name: string;
  size: number;
  lastModified: number;
}

// ... (Keep other existing types like Detector, DetectorConfig, UploadedFile, etc.)
// This edit assumes the primary issue was around Severity and AnalysisStatistics
// and aims to restore them correctly while preserving the rest of the file if possible.
// If the file was completely truncated, more definitions would be needed. 