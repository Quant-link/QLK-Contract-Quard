"""
Main analyzer engine for ContractQuard Static Analyzer MVP.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .config import Config
from .findings import Finding, Severity, SourceLocation
from ..parsers.solidity_parser import SolidityParser
from ..detectors.registry import DetectorRegistry
from ..reporters.factory import ReporterFactory, register_additional_reporters


class ContractQuardAnalyzer:
    """
    Main analyzer class that orchestrates the static analysis process.

    This class coordinates between parsers, detectors, and reporters to provide
    comprehensive smart contract security analysis.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the analyzer with configuration.

        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or Config()
        self.logger = self._setup_logging()

        # Initialize components
        self.parser = SolidityParser(self.config.solc)
        self.detector_registry = DetectorRegistry(self.config)
        self.reporter_factory = ReporterFactory(self.config.output)

        # Register additional reporters
        register_additional_reporters(self.reporter_factory)

        # Analysis state
        self.findings: List[Finding] = []
        self.analysis_stats: Dict[str, Any] = {}

        self.logger.info("ContractQuard Analyzer initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("contractquard")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        level = logging.DEBUG if self.config.output.verbose else logging.INFO
        logger.setLevel(level)

        return logger

    def analyze_file(self, file_path: str) -> List[Finding]:
        """
        Analyze a single Solidity file.

        Args:
            file_path: Path to the Solidity file to analyze.

        Returns:
            List of findings from the analysis.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file is too large or invalid.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.suffix == '.sol':
            raise ValueError(f"Not a Solidity file: {file_path}")

        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(
                f"File too large: {file_size_mb:.1f}MB > {self.config.max_file_size_mb}MB"
            )

        self.logger.info(f"Analyzing file: {file_path}")

        start_time = time.time()
        file_findings = []

        try:
            # Parse the Solidity file
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            parsed_data = self.parser.parse(source_code, str(file_path))

            # Run detectors
            for detector in self.detector_registry.get_enabled_detectors():
                detector_findings = detector.detect(parsed_data, source_code, str(file_path))
                file_findings.extend(detector_findings)

                self.logger.debug(
                    f"Detector {detector.name} found {len(detector_findings)} issues"
                )

            # Filter findings based on configuration
            file_findings = self._filter_findings(file_findings)

            analysis_time = time.time() - start_time
            self.logger.info(
                f"Analysis completed in {analysis_time:.2f}s, "
                f"found {len(file_findings)} issues"
            )

            return file_findings

        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {str(e)}")
            # Create an error finding
            error_finding = Finding(
                finding_id="",
                title="Analysis Error",
                description=f"Failed to analyze file: {str(e)}",
                severity=Severity.INFO,
                location=SourceLocation(str(file_path), 1),
                vulnerability_type="analysis_error",
                detector_name="analyzer"
            )
            return [error_finding]

    def analyze_directory(self, directory_path: str, recursive: bool = True) -> List[Finding]:
        """
        Analyze all Solidity files in a directory.

        Args:
            directory_path: Path to the directory to analyze.
            recursive: Whether to search subdirectories recursively.

        Returns:
            List of all findings from the analysis.
        """
        directory = Path(directory_path).resolve()

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        self.logger.info(f"Analyzing directory: {directory}")

        # Find Solidity files
        pattern = "**/*.sol" if recursive else "*.sol"
        sol_files = list(directory.glob(pattern))

        # Filter files based on configuration
        sol_files = self._filter_files(sol_files)

        self.logger.info(f"Found {len(sol_files)} Solidity files to analyze")

        all_findings = []

        for sol_file in sol_files:
            try:
                file_findings = self.analyze_file(str(sol_file))
                all_findings.extend(file_findings)
            except Exception as e:
                self.logger.error(f"Failed to analyze {sol_file}: {str(e)}")
                continue

        return all_findings

    def _filter_files(self, files: List[Path]) -> List[Path]:
        """Filter files based on include/exclude patterns."""
        filtered_files = []

        for file_path in files:
            file_name = file_path.name.lower()

            # Check exclude patterns
            if any(pattern.lower() in file_name for pattern in self.config.exclude_patterns):
                if not self.config.include_test_files:
                    continue

            # Check include patterns
            if any(file_path.match(pattern) for pattern in self.config.include_patterns):
                filtered_files.append(file_path)

        return filtered_files

    def _filter_findings(self, findings: List[Finding]) -> List[Finding]:
        """Filter findings based on severity and configuration."""
        severity_order = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1
        }

        min_severity_level = severity_order.get(
            Severity(self.config.min_severity), 1
        )

        filtered_findings = []

        for finding in findings:
            # Check minimum severity
            if severity_order.get(finding.severity, 0) < min_severity_level:
                continue

            # Check excluded severities
            if finding.severity.value in self.config.exclude_severities:
                continue

            filtered_findings.append(finding)

        return filtered_findings

    def generate_report(self, findings: List[Finding]) -> str:
        """
        Generate a report from the findings.

        Args:
            findings: List of findings to include in the report.

        Returns:
            Formatted report as a string.
        """
        reporter = self.reporter_factory.create_reporter()
        return reporter.generate_report(findings)

    def run_analysis(self, target_path: str) -> Dict[str, Any]:
        """
        Run complete analysis on a file or directory.

        Args:
            target_path: Path to file or directory to analyze.

        Returns:
            Dictionary containing findings and statistics.
        """
        self.logger.info(f"Starting full analysis for target: {target_path}")
        start_time = time.time()
        
        all_findings: List[Finding] = []
        final_solc_version: Optional[str] = None # To store solc version from parse

        target = Path(target_path)
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                parsed_data = self.parser.parse(source_code, str(target))
                final_solc_version = parsed_data.solc_version # Capture solc version

                if parsed_data.compilation_errors:
                    self.logger.warning(f"Compilation errors in {target}: {parsed_data.compilation_errors}")
                    # Optionally create findings for compilation errors
                    for err in parsed_data.compilation_errors:
                        all_findings.append(Finding(
                            finding_id="", title="Compilation Error", description=err,
                            severity=Severity.CRITICAL, # Or other appropriate severity
                            location=SourceLocation(str(target), 1),
                            vulnerability_type="compilation_error", detector_name="parser"
                        ))
                
                for detector in self.detector_registry.get_enabled_detectors():
                    detector_findings = detector.detect(parsed_data, source_code, str(target))
                    all_findings.extend(detector_findings)
            except Exception as e:
                self.logger.error(f"Error during file analysis of {target}: {e}")
                all_findings.append(Finding(
                    finding_id="", title="Analysis Error", description=str(e),
                    severity=Severity.CRITICAL, location=SourceLocation(str(target),1),
                    vulnerability_type="analyzer_error", detector_name="analyzer"
                ))
        elif target.is_dir():
            # For directory analysis, get solc version from the parser instance after it's been configured
            # This assumes the parser configures a single version for the session.
            if hasattr(self.parser, '_active_solc_version_str') and self.parser._active_solc_version_str:
                 final_solc_version = self.parser._active_solc_version_str
            else: # Fallback if parser hasn't exposed it directly yet or it's an older/mock parser
                 final_solc_version = self.parser._get_solc_version() 

            found_files = False
            for sol_file_path in self._filter_files(list(target.rglob("*.sol") if self.config.output.verbose else target.glob("*.sol"))):
                found_files = True
                try:
                    with open(sol_file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    # If parsing multiple files and solc version could change, this logic would need refinement.
                    # For now, we assume one main solc version for the run or use the first one found.
                    parsed_data = self.parser.parse(source_code, str(sol_file_path))
                    if not final_solc_version or final_solc_version in ["unknown", "mock", "setup_error", "latest_installed_or_default", "unknown_fallback_fetch"]:
                        final_solc_version = parsed_data.solc_version # Update if we get a better version

                    if parsed_data.compilation_errors:
                        self.logger.warning(f"Compilation errors in {sol_file_path}: {parsed_data.compilation_errors}")
                        for err in parsed_data.compilation_errors:
                             all_findings.append(Finding(
                                finding_id="", title="Compilation Error", description=err,
                                severity=Severity.CRITICAL, location=SourceLocation(str(sol_file_path),1),
                                vulnerability_type="compilation_error", detector_name="parser"
                            ))

                    for detector in self.detector_registry.get_enabled_detectors():
                        detector_findings = detector.detect(parsed_data, source_code, str(sol_file_path))
                        all_findings.extend(detector_findings)
                except Exception as e:
                    self.logger.error(f"Error during file analysis of {sol_file_path}: {e}")
                    all_findings.append(Finding(
                        finding_id="", title="Analysis Error", description=str(e),
                        severity=Severity.CRITICAL, location=SourceLocation(str(sol_file_path),1),
                        vulnerability_type="analyzer_error", detector_name="analyzer"
                    ))
            if not found_files:
                 self.logger.warning(f"No Solidity files found in directory {target_path}")
        else:
            self.logger.error(f"Target path is not a file or directory: {target_path}")
            raise ValueError(f"Invalid target path: {target_path}")

        # Filter all collected findings
        self.findings = self._filter_findings(all_findings)

        analysis_time = time.time() - start_time
        self.logger.info(f"Full analysis completed in {analysis_time:.2f}s. Total issues: {len(self.findings)} (after filtering)")

        # Generate statistics
        self.analysis_stats = self._generate_statistics(self.findings, analysis_time, final_solc_version or "unknown")

        return {
            "findings": self.findings,
            "statistics": self.analysis_stats
        }

    def _generate_statistics(self, findings: List[Finding], analysis_time: float, solc_version: str) -> Dict[str, Any]:
        """
        Generate summary statistics from findings.

        Args:
            findings: List of findings.
            analysis_time: Total analysis time in seconds.
            solc_version: The Solidity compiler version used.

        Returns:
            Dictionary with summary statistics.
        """
        total_findings = len(findings)
        severity_counts = {}
        for severity in Severity:
            severity_counts[severity.value] = sum(
                1 for f in findings if f.severity == severity
            )

        detector_counts = {}
        for finding in findings:
            detector_counts[finding.detector_name] = detector_counts.get(
                finding.detector_name, 0
            ) + 1

        vuln_type_counts = {}
        for finding in findings:
            vuln_type_counts[finding.vulnerability_type] = vuln_type_counts.get(
                finding.vulnerability_type, 0
            ) + 1

        file_counts = {}
        for finding in findings:
            file_path = finding.location.file_path
            file_counts[file_path] = file_counts.get(file_path, 0) + 1

        # Get number of unique files analyzed from findings locations
        files_analyzed_count = len(set(f.location.file_path for f in findings if f.location))
        if files_analyzed_count == 0 and total_findings == 0 : # if no findings, it might mean no issues in 1 file
            # This part is tricky, if analysis ran on one file and found nothing, files_analyzed should be 1.
            # The caller of run_analysis knows if it was a file or dir. This count is from findings.
            # For now, let's assume if there are no findings, it implies 0 files with findings, not 0 analyzed.
            # The API layer (main.py) knows the input filename and can report that.
            pass # We will rely on API layer to report input file if needed when no findings

        return {
            'total_findings': total_findings,
            'severity_breakdown': severity_counts,
            'vulnerability_type_breakdown': vuln_type_counts,
            'detector_breakdown': detector_counts,
            # 'file_breakdown': file_counts, # This might be too verbose for summary stats
            'files_analyzed': files_analyzed_count, # Number of files with findings
            'analysis_time_seconds': round(analysis_time, 2),
            'solc_version': solc_version,
            'timestamp': datetime.now().isoformat()
        }
