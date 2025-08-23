"""
Base reporter class for ContractQuard Static Analyzer.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

from ..core.findings import Finding, Severity


class BaseReporter(ABC):
    """
    Abstract base class for all report generators.

    This class defines the interface that all reporters must implement
    and provides common functionality for generating reports.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the reporter.

        Args:
            config: Reporter configuration.
        """
        self.config = config
        self.include_code_snippets = config.get('include_code_snippets', True)
        self.max_snippet_lines = config.get('max_snippet_lines', 5)

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the name of this report format."""
        pass

    @abstractmethod
    def generate_report(self, findings: List[Finding]) -> str:
        """
        Generate a report from the findings.

        Args:
            findings: List of findings to include in the report.

        Returns:
            Formatted report as a string.
        """
        pass

    def generate_summary(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        Generate summary statistics from findings.

        Args:
            findings: List of findings.

        Returns:
            Dictionary with summary statistics.
        """
        total_findings = len(findings)

        # Count by severity
        severity_counts = {}
        for severity in Severity:
            severity_counts[severity.value] = sum(
                1 for f in findings if f.severity == severity
            )

        # Count by vulnerability type
        vuln_type_counts = {}
        for finding in findings:
            vuln_type = finding.vulnerability_type
            vuln_type_counts[vuln_type] = vuln_type_counts.get(vuln_type, 0) + 1

        # Count by detector
        detector_counts = {}
        for finding in findings:
            detector = finding.detector_name
            detector_counts[detector] = detector_counts.get(detector, 0) + 1

        # Count by file
        file_counts = {}
        for finding in findings:
            file_path = finding.location.file_path
            file_counts[file_path] = file_counts.get(file_path, 0) + 1

        return {
            'total_findings': total_findings,
            'severity_breakdown': severity_counts,
            'vulnerability_type_breakdown': vuln_type_counts,
            'detector_breakdown': detector_counts,
            'file_breakdown': file_counts,
            'files_with_issues': len(file_counts),
            'timestamp': datetime.now().isoformat()
        }

    def sort_findings(self, findings: List[Finding]) -> List[Finding]:
        """
        Sort findings by severity and then by file/line.

        Args:
            findings: List of findings to sort.

        Returns:
            Sorted list of findings.
        """
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4
        }

        return sorted(findings, key=lambda f: (
            severity_order.get(f.severity, 5),
            f.location.file_path,
            f.location.line_start
        ))

    def truncate_code_snippet(self, code_snippet: str) -> str:
        """
        Truncate code snippet to maximum number of lines.

        Args:
            code_snippet: Original code snippet.

        Returns:
            Truncated code snippet.
        """
        if not code_snippet:
            return ""

        lines = code_snippet.split('\n')
        if len(lines) <= self.max_snippet_lines:
            return code_snippet

        truncated_lines = lines[:self.max_snippet_lines]
        truncated_lines.append(f"... ({len(lines) - self.max_snippet_lines} more lines)")

        return '\n'.join(truncated_lines)

    def format_severity(self, severity: Severity) -> str:
        """
        Format severity for display.

        Args:
            severity: Severity level.

        Returns:
            Formatted severity string.
        """
        return severity.value

    def get_severity_icon(self, severity: Severity) -> str:
        """
        Get an icon/symbol for a severity level.

        Args:
            severity: Severity level.

        Returns:
            Icon string.
        """
        icons = {
            Severity.CRITICAL: "[CRITICAL]",
            Severity.HIGH: "[HIGH]",
            Severity.MEDIUM: "[MEDIUM]",
            Severity.LOW: "[LOW]",
            Severity.INFO: "[INFO]"
        }
        return icons.get(severity, "[UNKNOWN]")

    def format_location(self, finding: Finding) -> str:
        """
        Format location information for display.

        Args:
            finding: Finding with location information.

        Returns:
            Formatted location string.
        """
        location = finding.location
        if location.line_end and location.line_end != location.line_start:
            return f"{location.file_path}:{location.line_start}-{location.line_end}"
        return f"{location.file_path}:{location.line_start}"

    def should_include_code_snippet(self, finding: Finding) -> bool:
        """
        Determine if code snippet should be included for a finding.

        Args:
            finding: Finding to check.

        Returns:
            True if code snippet should be included.
        """
        return (
            self.include_code_snippets and
            finding.code_snippet and
            finding.code_snippet.strip()
        )
