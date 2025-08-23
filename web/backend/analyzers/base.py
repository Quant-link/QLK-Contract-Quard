"""
Base analyzer class and common structures
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    """Severity levels for findings"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class AnalysisFinding:
    """Represents a security finding from analysis"""
    detector: str
    severity: Severity
    title: str
    description: str
    line_number: int
    column: int = 0
    code_snippet: str = ""
    recommendation: str = ""
    confidence: str = "HIGH"
    impact: str = "MEDIUM"
    cwe_id: Optional[int] = None
    references: List[str] = None
    category: str = "Security"
    
    def __post_init__(self):
        if self.references is None:
            self.references = []

class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
    
    @abstractmethod
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Analyze a file and return findings
        
        Args:
            filename: Name of the file being analyzed
            content: Content of the file
            
        Returns:
            List of AnalysisFinding objects
        """
        pass
    
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """
        Check if this analyzer supports the given language
        
        Args:
            language: File extension (e.g., 'sol', 'rs', 'go')
            
        Returns:
            True if supported, False otherwise
        """
        pass
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return []
    
    def calculate_risk_score(self, findings: List[AnalysisFinding]) -> int:
        """
        Calculate overall risk score based on findings
        
        Args:
            findings: List of findings
            
        Returns:
            Risk score from 0-100
        """
        if not findings:
            return 0
            
        severity_weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 8,
            Severity.LOW: 3,
            Severity.INFO: 1
        }
        
        total_score = sum(severity_weights.get(finding.severity, 0) for finding in findings)
        
        # Cap at 100
        return min(total_score, 100)
    
    def get_severity_counts(self, findings: List[AnalysisFinding]) -> Dict[str, int]:
        """Get count of findings by severity"""
        counts = {
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "info_count": 0
        }
        
        for finding in findings:
            if finding.severity == Severity.CRITICAL:
                counts["critical_count"] += 1
            elif finding.severity == Severity.HIGH:
                counts["high_count"] += 1
            elif finding.severity == Severity.MEDIUM:
                counts["medium_count"] += 1
            elif finding.severity == Severity.LOW:
                counts["low_count"] += 1
            elif finding.severity == Severity.INFO:
                counts["info_count"] += 1
                
        return counts
    
    def extract_code_snippet(self, content: str, line_number: int, context_lines: int = 2) -> str:
        """
        Extract code snippet around a specific line
        
        Args:
            content: Full file content
            line_number: Target line number (1-based)
            context_lines: Number of context lines before/after
            
        Returns:
            Code snippet with context
        """
        lines = content.splitlines()
        if not lines or line_number < 1:
            return ""
            
        # Convert to 0-based indexing
        target_line = line_number - 1
        
        # Calculate range
        start = max(0, target_line - context_lines)
        end = min(len(lines), target_line + context_lines + 1)
        
        # Extract lines with line numbers
        snippet_lines = []
        for i in range(start, end):
            line_num = i + 1
            marker = ">>> " if i == target_line else "    "
            snippet_lines.append(f"{marker}{line_num:3d}: {lines[i]}")
            
        return "\n".join(snippet_lines)
