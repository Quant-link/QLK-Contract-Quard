"""
Core data structures for ContractQuard findings and severity levels.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import hashlib
from datetime import datetime


class Severity(Enum):
    """Severity levels for security findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH" 
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    def __str__(self) -> str:
        return self.value

    @property
    def color_code(self) -> str:
        """ANSI color codes for terminal output."""
        colors = {
            Severity.CRITICAL: "\033[91m",  # Red
            Severity.HIGH: "\033[93m",      # Yellow
            Severity.MEDIUM: "\033[94m",    # Blue
            Severity.LOW: "\033[92m",       # Green
            Severity.INFO: "\033[96m",      # Cyan
        }
        return colors.get(self, "\033[0m")

    @property
    def reset_code(self) -> str:
        """ANSI reset code."""
        return "\033[0m"


@dataclass
class SourceLocation:
    """Represents a location in source code."""
    file_path: str
    line_start: int
    line_end: Optional[int] = None
    column_start: Optional[int] = None
    column_end: Optional[int] = None

    def __str__(self) -> str:
        if self.line_end and self.line_end != self.line_start:
            return f"{self.file_path}:{self.line_start}-{self.line_end}"
        return f"{self.file_path}:{self.line_start}"


@dataclass
class Finding:
    """Represents a security finding from the analysis."""
    
    # Core identification
    finding_id: str
    title: str
    description: str
    severity: Severity
    
    # Location information
    location: SourceLocation
    
    # Vulnerability details
    vulnerability_type: str
    confidence: float = 1.0  # 0.0 to 1.0
    
    # Additional context
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    references: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Analysis metadata
    detector_name: str = "unknown"
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        if not self.finding_id:
            self.finding_id = self._generate_id()
        
        if self.references is None:
            self.references = []
        
        if self.metadata is None:
            self.metadata = {}

    def _generate_id(self) -> str:
        """Generate a unique ID for this finding."""
        content = f"{self.title}:{self.location}:{self.vulnerability_type}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary representation."""
        return {
            "finding_id": self.finding_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "location": {
                "file_path": self.location.file_path,
                "line_start": self.location.line_start,
                "line_end": self.location.line_end,
                "column_start": self.location.column_start,
                "column_end": self.location.column_end,
            },
            "vulnerability_type": self.vulnerability_type,
            "confidence": self.confidence,
            "code_snippet": self.code_snippet,
            "recommendation": self.recommendation,
            "references": self.references,
            "metadata": self.metadata,
            "detector_name": self.detector_name,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Finding":
        """Create Finding from dictionary representation."""
        location_data = data["location"]
        location = SourceLocation(
            file_path=location_data["file_path"],
            line_start=location_data["line_start"],
            line_end=location_data.get("line_end"),
            column_start=location_data.get("column_start"),
            column_end=location_data.get("column_end"),
        )
        
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            finding_id=data["finding_id"],
            title=data["title"],
            description=data["description"],
            severity=Severity(data["severity"]),
            location=location,
            vulnerability_type=data["vulnerability_type"],
            confidence=data.get("confidence", 1.0),
            code_snippet=data.get("code_snippet"),
            recommendation=data.get("recommendation"),
            references=data.get("references", []),
            metadata=data.get("metadata", {}),
            detector_name=data.get("detector_name", "unknown"),
            timestamp=timestamp,
        )

    def __str__(self) -> str:
        """String representation for console output."""
        return (
            f"{self.severity.color_code}[{self.severity.value}]{self.severity.reset_code} "
            f"{self.title} at {self.location}"
        )
