"""
Console reporter for ContractQuard Static Analyzer.
"""

from typing import List, Dict, Any
from ..core.findings import Finding, Severity
from .base import BaseReporter


class ConsoleReporter(BaseReporter):
    """
    Console reporter that outputs findings in a human-readable format
    with color coding and clear structure.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the console reporter.

        Args:
            config: Reporter configuration.
        """
        super().__init__(config)
        self.use_colors = config.get('color_output', True)
        self.verbose = config.get('verbose', False)

    @property
    def format_name(self) -> str:
        return "console"

    def generate_report(self, findings: List[Finding]) -> str:
        """
        Generate a console report from findings.

        Args:
            findings: List of findings to report.

        Returns:
            Formatted console report.
        """
        if not findings:
            return self._generate_no_issues_report()

        # Sort findings by severity and location
        sorted_findings = self.sort_findings(findings)

        # Generate report sections
        report_parts = []

        # Header
        report_parts.append(self._generate_header(findings))

        # Summary
        report_parts.append(self._generate_summary_section(findings))

        # Detailed findings
        report_parts.append(self._generate_findings_section(sorted_findings))

        # Footer
        report_parts.append(self._generate_footer(findings))

        return '\n'.join(report_parts)

    def _generate_no_issues_report(self) -> str:
        """Generate report when no issues are found."""
        return (
            f"{self._colorize('✅ No security issues found!', 'green')}\n"
            "Your smart contract appears to be free of the vulnerabilities "
            "checked by ContractQuard's static analysis.\n"
        )

    def _generate_header(self, findings: List[Finding]) -> str:
        """Generate report header."""
        total_issues = len(findings)

        if total_issues == 0:
            return ""

        header = f"\n{self._colorize('🔍 ContractQuard Security Analysis Report', 'bold')}\n"
        header += "=" * 50 + "\n"

        if total_issues == 1:
            header += f"Found {self._colorize('1 security issue', 'yellow')}\n"
        else:
            header += f"Found {self._colorize(f'{total_issues} security issues', 'yellow')}\n"

        return header

    def _generate_summary_section(self, findings: List[Finding]) -> str:
        """Generate summary section."""
        summary = self.generate_summary(findings)

        section = f"\n{self._colorize('Summary', 'bold')}\n"
        section += "-" * 20 + "\n"

        # Severity breakdown
        severity_counts = summary['severity_breakdown']
        for severity_name in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = severity_counts.get(severity_name, 0)
            if count > 0:
                severity = Severity(severity_name)
                icon = self.get_severity_icon(severity)
                color = self._get_severity_color(severity)
                section += f"{icon} {self._colorize(severity_name, color)}: {count}\n"

        # File breakdown
        files_with_issues = summary['files_with_issues']
        section += f"\nFiles with issues: {files_with_issues}\n"

        return section

    def _generate_findings_section(self, findings: List[Finding]) -> str:
        """Generate detailed findings section."""
        section = f"\n{self._colorize('🔍 Detailed Findings', 'bold')}\n"
        section += "=" * 30 + "\n"

        current_file = None

        for i, finding in enumerate(findings, 1):
            # Group by file
            if finding.location.file_path != current_file:
                current_file = finding.location.file_path
                section += f"\n{self._colorize(f'📄 {current_file}', 'cyan')}\n"
                section += "-" * len(current_file) + "\n"

            section += self._format_finding(finding, i)
            section += "\n"

        return section

    def _format_finding(self, finding: Finding, index: int) -> str:
        """Format a single finding."""
        # Header with severity and title
        severity_color = self._get_severity_color(finding.severity)
        icon = self.get_severity_icon(finding.severity)

        finding_text = f"\n{index}. {icon} {self._colorize(finding.severity.value, severity_color)} - {finding.title}\n"

        # Location
        location = self.format_location(finding)
        finding_text += f"   Location: {location}\n"

        # Description
        if finding.description:
            finding_text += f"   Description: {finding.description}\n"

        # Confidence
        if finding.confidence < 1.0:
            confidence_pct = int(finding.confidence * 100)
            finding_text += f"   Confidence: {confidence_pct}%\n"

        # Code snippet
        if self.should_include_code_snippet(finding):
            snippet = self.truncate_code_snippet(finding.code_snippet)
            finding_text += f"   💻 Code:\n{self._indent_text(snippet, '      ')}\n"

        # Recommendation
        if finding.recommendation:
            finding_text += f"   💡 Recommendation: {finding.recommendation}\n"

        # References (in verbose mode)
        if self.verbose and finding.references:
            finding_text += f"   🔗 References:\n"
            for ref in finding.references:
                finding_text += f"      - {ref}\n"

        # Metadata (in verbose mode)
        if self.verbose and finding.metadata:
            finding_text += f"   🏷️  Metadata: {finding.metadata}\n"

        return finding_text

    def _generate_footer(self, findings: List[Finding]) -> str:
        """Generate report footer."""
        if not findings:
            return ""

        footer = "\n" + "=" * 50 + "\n"
        footer += f"{self._colorize('ContractQuard Analysis Complete', 'bold')}\n"

        # Risk assessment
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == Severity.HIGH)

        if critical_count > 0:
            footer += f"{self._colorize('CRITICAL ISSUES FOUND - Immediate attention required!', 'red')}\n"
        elif high_count > 0:
            footer += f"{self._colorize('HIGH SEVERITY ISSUES FOUND - Review recommended', 'yellow')}\n"
        else:
            footer += f"{self._colorize('No critical or high severity issues found', 'green')}\n"

        footer += "\nFor more information, visit: https://github.com/quantlink/contractquard\n"

        return footer

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if not self.use_colors:
            return text

        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }

        color_code = colors.get(color, '')
        reset_code = colors['reset']

        return f"{color_code}{text}{reset_code}"

    def _get_severity_color(self, severity: Severity) -> str:
        """Get color for a severity level."""
        color_map = {
            Severity.CRITICAL: 'red',
            Severity.HIGH: 'yellow',
            Severity.MEDIUM: 'blue',
            Severity.LOW: 'green',
            Severity.INFO: 'cyan'
        }
        return color_map.get(severity, 'white')

    def _indent_text(self, text: str, indent: str) -> str:
        """Indent all lines of text."""
        lines = text.split('\n')
        return '\n'.join(indent + line for line in lines)
