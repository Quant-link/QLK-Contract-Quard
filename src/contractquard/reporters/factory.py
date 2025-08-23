"""
Reporter factory for ContractQuard Static Analyzer.
"""

from typing import Dict, Any, Type
import logging

from ..core.config import OutputConfig
from .base import BaseReporter
from .console import ConsoleReporter
from .json_reporter import JSONReporter, SARIFReporter


class ReporterFactory:
    """
    Factory class for creating report generators.

    This class manages the registration and instantiation of different
    report format generators.
    """

    def __init__(self, config: OutputConfig):
        """
        Initialize the reporter factory.

        Args:
            config: Output configuration.
        """
        self.config = config
        self.logger = logging.getLogger("contractquard.reporter")

        # Registry of available reporters
        self._reporters: Dict[str, Type[BaseReporter]] = {
            'console': ConsoleReporter,
            'json': JSONReporter,
            'sarif': SARIFReporter,
        }

    def register_reporter(self, format_name: str, reporter_class: Type[BaseReporter]) -> None:
        """
        Register a new reporter class.

        Args:
            format_name: Name of the report format.
            reporter_class: Reporter class to register.
        """
        if not issubclass(reporter_class, BaseReporter):
            raise ValueError(f"Reporter class must inherit from BaseReporter: {reporter_class}")

        self._reporters[format_name] = reporter_class
        self.logger.debug(f"Registered reporter: {format_name}")

    def create_reporter(self, format_name: str = None) -> BaseReporter:
        """
        Create a reporter instance.

        Args:
            format_name: Name of the report format. If None, uses config default.

        Returns:
            Reporter instance.

        Raises:
            ValueError: If the format is not supported.
        """
        if format_name is None:
            format_name = self.config.format

        if format_name not in self._reporters:
            available_formats = list(self._reporters.keys())
            raise ValueError(
                f"Unsupported report format: {format_name}. "
                f"Available formats: {available_formats}"
            )

        reporter_class = self._reporters[format_name]

        # Convert config to dictionary for reporter
        config_dict = {
            'format': self.config.format,
            'output_file': self.config.output_file,
            'include_code_snippets': self.config.include_code_snippets,
            'max_snippet_lines': self.config.max_snippet_lines,
            'color_output': self.config.color_output,
            'verbose': self.config.verbose
        }

        try:
            reporter = reporter_class(config_dict)
            self.logger.debug(f"Created reporter: {format_name}")
            return reporter
        except Exception as e:
            self.logger.error(f"Failed to create reporter {format_name}: {e}")
            raise

    def get_available_formats(self) -> list:
        """
        Get list of available report formats.

        Returns:
            List of format names.
        """
        return list(self._reporters.keys())

    def is_format_supported(self, format_name: str) -> bool:
        """
        Check if a report format is supported.

        Args:
            format_name: Name of the report format.

        Returns:
            True if format is supported, False otherwise.
        """
        return format_name in self._reporters


# Additional reporters can be added here

class MarkdownReporter(BaseReporter):
    """
    Markdown reporter for generating documentation-friendly reports.
    """

    @property
    def format_name(self) -> str:
        return "markdown"

    def generate_report(self, findings: list) -> str:
        """Generate a Markdown report from findings."""
        if not findings:
            return self._generate_no_issues_report()

        # Sort findings
        sorted_findings = self.sort_findings(findings)

        # Generate report sections
        report_parts = []

        # Header
        report_parts.append("# ContractQuard Security Analysis Report\n")

        # Summary
        summary = self.generate_summary(findings)
        report_parts.append(self._generate_markdown_summary(summary))

        # Detailed findings
        report_parts.append(self._generate_markdown_findings(sorted_findings))

        return '\n'.join(report_parts)

    def _generate_no_issues_report(self) -> str:
        """Generate markdown report when no issues are found."""
        return (
            "# ContractQuard Security Analysis Report\n\n"
            "## No Security Issues Found\n\n"
            "Your smart contract appears to be free of the vulnerabilities "
            "checked by ContractQuard's static analysis.\n"
        )

    def _generate_markdown_summary(self, summary: Dict[str, Any]) -> str:
        """Generate markdown summary section."""
        section = "## Summary\n\n"

        # Severity breakdown table
        section += "| Severity | Count |\n"
        section += "|----------|-------|\n"

        severity_counts = summary['severity_breakdown']
        for severity_name in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = severity_counts.get(severity_name, 0)
            if count > 0:
                icon = self._get_markdown_severity_icon(severity_name)
                section += f"| {icon} {severity_name} | {count} |\n"

        section += f"\n**Files with issues:** {summary['files_with_issues']}\n\n"

        return section

    def _generate_markdown_findings(self, findings: list) -> str:
        """Generate markdown findings section."""
        section = "## 🔍 Detailed Findings\n\n"

        current_file = None

        for i, finding in enumerate(findings, 1):
            # Group by file
            if finding.location.file_path != current_file:
                current_file = finding.location.file_path
                section += f"### 📄 {current_file}\n\n"

            section += self._format_markdown_finding(finding, i)
            section += "\n"

        return section

    def _format_markdown_finding(self, finding, index: int) -> str:
        """Format a single finding in markdown."""
        icon = self._get_markdown_severity_icon(finding.severity.value)

        finding_text = f"#### {index}. {icon} {finding.severity.value} - {finding.title}\n\n"

        # Location
        location = self.format_location(finding)
        finding_text += f"**Location:** `{location}`\n\n"

        # Description
        if finding.description:
            finding_text += f"**Description:** {finding.description}\n\n"

        # Code snippet
        if self.should_include_code_snippet(finding):
            snippet = self.truncate_code_snippet(finding.code_snippet)
            finding_text += f"**Code:**\n```solidity\n{snippet}\n```\n\n"

        # Recommendation
        if finding.recommendation:
            finding_text += f"**Recommendation:** {finding.recommendation}\n\n"

        # References
        if finding.references:
            finding_text += "**References:**\n"
            for ref in finding.references:
                finding_text += f"- {ref}\n"
            finding_text += "\n"

        return finding_text

    def _get_markdown_severity_icon(self, severity_name: str) -> str:
        """Get markdown icon for severity."""
        icons = {
            'CRITICAL': '[CRITICAL]',
            'HIGH': '[HIGH]',
            'MEDIUM': '[MEDIUM]',
            'LOW': '[LOW]',
            'INFO': '[INFO]'
        }
        return icons.get(severity_name, '[UNKNOWN]')


class HTMLReporter(BaseReporter):
    """
    HTML reporter for generating web-friendly reports.
    """

    @property
    def format_name(self) -> str:
        return "html"

    def generate_report(self, findings: list) -> str:
        """Generate an HTML report from findings."""
        if not findings:
            return self._generate_no_issues_html()

        sorted_findings = self.sort_findings(findings)
        summary = self.generate_summary(findings)

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContractQuard Security Analysis Report</title>
    <style>
        {self._get_html_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ContractQuard Security Analysis Report</h1>
            <p class="subtitle">Generated on {summary['timestamp']}</p>
        </header>

        {self._generate_html_summary(summary)}
        {self._generate_html_findings(sorted_findings)}

        <footer>
            <p>Generated by <a href="https://github.com/quantlink/contractquard">ContractQuard</a> v0.1.0</p>
        </footer>
    </div>
</body>
</html>
"""
        return html

    def _generate_no_issues_html(self) -> str:
        """Generate HTML report when no issues are found."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContractQuard Security Analysis Report</title>
    <style>{self._get_html_styles()}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>No Security Issues Found</h1>
        </header>
        <div class="success">
            <p>Your smart contract appears to be free of the vulnerabilities checked by ContractQuard's static analysis.</p>
        </div>
    </div>
</body>
</html>
"""

    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML report."""
        return """
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        header { text-align: center; margin-bottom: 30px; }
        h1 { color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; margin: 0; }
        .summary { background: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 30px; }
        .severity-critical { color: #dc3545; }
        .severity-high { color: #fd7e14; }
        .severity-medium { color: #ffc107; }
        .severity-low { color: #28a745; }
        .severity-info { color: #17a2b8; }
        .finding { border: 1px solid #ddd; margin-bottom: 20px; border-radius: 6px; }
        .finding-header { padding: 15px; background: #f8f9fa; border-bottom: 1px solid #ddd; }
        .finding-body { padding: 15px; }
        .code-snippet { background: #f8f8f8; padding: 10px; border-radius: 4px; font-family: monospace; overflow-x: auto; }
        .success { text-align: center; padding: 40px; color: #28a745; }
        footer { text-align: center; margin-top: 40px; color: #666; }
        """

    def _generate_html_summary(self, summary: Dict[str, Any]) -> str:
        """Generate HTML summary section."""
        section = '<div class="summary"><h2>Summary</h2>'

        severity_counts = summary['severity_breakdown']
        for severity_name in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = severity_counts.get(severity_name, 0)
            if count > 0:
                css_class = f"severity-{severity_name.lower()}"
                section += f'<p><span class="{css_class}"><strong>{severity_name}:</strong> {count}</span></p>'

        section += f'<p><strong>Files with issues:</strong> {summary["files_with_issues"]}</p>'
        section += '</div>'

        return section

    def _generate_html_findings(self, findings: list) -> str:
        """Generate HTML findings section."""
        section = '<div class="findings"><h2>Detailed Findings</h2>'

        for i, finding in enumerate(findings, 1):
            css_class = f"severity-{finding.severity.value.lower()}"

            section += f'''
            <div class="finding">
                <div class="finding-header">
                    <h3 class="{css_class}">{i}. {finding.severity.value} - {finding.title}</h3>
                    <p><strong>Location:</strong> {self.format_location(finding)}</p>
                </div>
                <div class="finding-body">
                    <p><strong>Description:</strong> {finding.description}</p>
            '''

            if self.should_include_code_snippet(finding):
                snippet = self.truncate_code_snippet(finding.code_snippet)
                section += f'<div class="code-snippet"><pre>{snippet}</pre></div>'

            if finding.recommendation:
                section += f'<p><strong>Recommendation:</strong> {finding.recommendation}</p>'

            section += '</div></div>'

        section += '</div>'
        return section


# Register additional reporters
def register_additional_reporters(factory: ReporterFactory) -> None:
    """Register additional reporter formats."""
    factory.register_reporter('markdown', MarkdownReporter)
    factory.register_reporter('html', HTMLReporter)
