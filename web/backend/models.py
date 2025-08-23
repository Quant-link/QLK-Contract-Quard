"""
Pydantic models for ContractQuard API
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    """Severity levels for findings"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class AnalysisStatus(str, Enum):
    """Analysis status values"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Finding(BaseModel):
    """Individual security finding"""
    id: str
    detector: str
    severity: SeverityLevel
    title: str
    description: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None

class AnalysisMetadata(BaseModel):
    """Metadata about the analysis"""
    filename: str
    file_size: int
    total_findings: int
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    analysis_duration_ms: Optional[int] = None

class AnalysisRequest(BaseModel):
    """Request model for contract analysis"""
    filename: str
    content: str
    config: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    """Response model for contract analysis"""
    analysis_id: str
    status: AnalysisStatus
    findings: List[Finding]
    metadata: AnalysisMetadata
    timestamp: str
    error_message: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
    uptime_seconds: Optional[float] = None

class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    analysis_id: Optional[str] = None
    status: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: str
    message: Optional[str] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response format"""
    detail: str
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    size: int
    content_type: str
    upload_id: str
    timestamp: str
