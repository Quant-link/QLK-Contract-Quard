"""
Base detector class for ContractQuard vulnerability detectors.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

from ..core.findings import Finding, Severity, SourceLocation
from ..core.config import DetectorConfig, SolcConfig
from ..parsers.solidity_parser import ParsedData, SolidityParser


class BaseDetector(ABC):
    """
    Abstract base class for all vulnerability detectors.
    
    This class defines the interface that all detectors must implement
    and provides common functionality for creating findings.
    """
    
    def __init__(self, config: DetectorConfig):
        """
        Initialize the detector.
        
        Args:
            config: Configuration for this detector.
        """
        self.config = config
        self.enabled = config.enabled
        self.logger = logging.getLogger(f"contractquard.detector.{self.name}")
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this detector."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this detector finds."""
        pass
    
    @property
    @abstractmethod
    def vulnerability_types(self) -> List[str]:
        """Return a list of vulnerability types this detector can find."""
        pass
    
    @property
    @abstractmethod
    def default_severity(self) -> Severity:
        """Return the default severity level for findings from this detector."""
        pass
    
    @abstractmethod
    def detect(self, parsed_data: ParsedData, source_code: str, file_path: str) -> List[Finding]:
        """
        Detect vulnerabilities in the parsed contract data.
        
        Args:
            parsed_data: Parsed Solidity contract data.
            source_code: Original source code.
            file_path: Path to the source file.
            
        Returns:
            List of findings detected by this detector.
        """
        pass
    
    def create_finding(
        self,
        title: str,
        description: str,
        location: SourceLocation,
        vulnerability_type: str,
        confidence: float = 1.0,
        severity: Optional[Severity] = None,
        code_snippet: Optional[str] = None,
        recommendation: Optional[str] = None,
        references: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Finding:
        """
        Create a finding with this detector's information.
        
        Args:
            title: Title of the finding.
            description: Detailed description.
            location: Source code location.
            vulnerability_type: Type of vulnerability.
            confidence: Confidence level (0.0 to 1.0).
            severity: Severity level (uses default if None).
            code_snippet: Relevant code snippet.
            recommendation: Recommended fix.
            references: External references.
            metadata: Additional metadata.
            
        Returns:
            A Finding object.
        """
        # Use configured severity override or default
        if self.config.severity_override:
            severity = Severity(self.config.severity_override)
        elif severity is None:
            severity = self.default_severity
        
        return Finding(
            finding_id="",  # Will be auto-generated
            title=title,
            description=description,
            severity=severity,
            location=location,
            vulnerability_type=vulnerability_type,
            confidence=confidence,
            code_snippet=code_snippet,
            recommendation=recommendation,
            references=references or [],
            metadata=metadata or {},
            detector_name=self.name
        )
    
    def extract_code_snippet(
        self,
        source_code: str,
        line_start: int,
        line_end: Optional[int] = None,
        context_lines: int = 3
    ) -> str:
        """
        Extract a code snippet from source code.
        
        Args:
            source_code: The full source code.
            line_start: Starting line number (1-based).
            line_end: Ending line number (1-based, optional).
            context_lines: Number of context lines to include.
            
        Returns:
            Code snippet as a string.
        """
        lines = source_code.split('\n')
        
        if line_end is None:
            line_end = line_start
        
        # Adjust for 0-based indexing
        start_idx = max(0, line_start - 1 - context_lines)
        end_idx = min(len(lines), line_end + context_lines)
        
        snippet_lines = []
        for i in range(start_idx, end_idx):
            line_num = i + 1
            prefix = ">>> " if line_start <= line_num <= line_end else "    "
            snippet_lines.append(f"{prefix}{line_num:3d}: {lines[i]}")
        
        return '\n'.join(snippet_lines)
    
    def get_custom_param(self, param_name: str, default_value: Any = None) -> Any:
        """
        Get a custom parameter from the detector configuration.
        
        Args:
            param_name: Name of the parameter.
            default_value: Default value if parameter is not set.
            
        Returns:
            Parameter value or default.
        """
        return self.config.custom_params.get(param_name, default_value)
    
    def log_detection(self, finding_count: int, file_path: str) -> None:
        """
        Log detection results.
        
        Args:
            finding_count: Number of findings detected.
            file_path: Path to the analyzed file.
        """
        if finding_count > 0:
            self.logger.info(f"Found {finding_count} issues in {file_path}")
        else:
            self.logger.debug(f"No issues found in {file_path}")


class RegexDetector(BaseDetector):
    """
    Base class for regex-based detectors.
    
    This class provides common functionality for detectors that use
    regular expressions to find patterns in source code.
    """
    
    @property
    @abstractmethod
    def patterns(self) -> Dict[str, str]:
        """
        Return a dictionary of regex patterns to search for.
        
        Returns:
            Dictionary mapping pattern names to regex strings.
        """
        pass
    
    def detect(self, parsed_data: ParsedData, source_code: str, file_path: str) -> List[Finding]:
        """
        Detect vulnerabilities using regex patterns.
        
        Args:
            parsed_data: Parsed contract data (not used in regex detection).
            source_code: Source code to analyze.
            file_path: Path to the source file.
            
        Returns:
            List of findings from regex pattern matching.
        """
        import re
        
        findings = []
        lines = source_code.split('\n')
        
        for pattern_name, pattern in self.patterns.items():
            try:
                regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
                
                for line_num, line in enumerate(lines, 1):
                    matches = regex.finditer(line)
                    
                    for match in matches:
                        finding = self._create_regex_finding(
                            pattern_name=pattern_name,
                            match=match,
                            line_num=line_num,
                            line_content=line,
                            source_code=source_code,
                            file_path=file_path
                        )
                        if finding:
                            findings.append(finding)
                            
            except re.error as e:
                self.logger.error(f"Invalid regex pattern '{pattern_name}': {e}")
        
        self.log_detection(len(findings), file_path)
        return findings
    
    @abstractmethod
    def _create_regex_finding(
        self,
        pattern_name: str,
        match: 're.Match',
        line_num: int,
        line_content: str,
        source_code: str,
        file_path: str
    ) -> Optional[Finding]:
        """
        Create a finding from a regex match.
        
        Args:
            pattern_name: Name of the matched pattern.
            match: The regex match object.
            line_num: Line number of the match.
            line_content: Content of the matched line.
            source_code: Full source code.
            file_path: Path to the source file.
            
        Returns:
            A Finding object or None if no finding should be created.
        """
        pass


class ASTDetector(BaseDetector):
    """
    Base class for AST-based detectors.
    
    This class provides common functionality for detectors that analyze
    the Abstract Syntax Tree of Solidity contracts.
    """
    
    def detect(self, parsed_data: ParsedData, source_code: str, file_path: str) -> List[Finding]:
        """
        Detect vulnerabilities using AST analysis.
        
        Args:
            parsed_data: Parsed contract data with AST.
            source_code: Source code for context.
            file_path: Path to the source file.
            
        Returns:
            List of findings from AST analysis.
        """
        findings = []
        
        # Check for compilation errors first
        if parsed_data.compilation_errors:
            self.logger.warning(f"Compilation errors in {file_path}, AST analysis may be limited")
        
        # Analyze each contract in the file
        for contract in parsed_data.contracts:
            if contract.ast:
                contract_findings = self.analyze_contract_ast(
                    contract.ast, contract, source_code, file_path
                )
                findings.extend(contract_findings)
        
        self.log_detection(len(findings), file_path)
        return findings
    
    @abstractmethod
    def analyze_contract_ast(
        self,
        ast: Dict[str, Any],
        contract: 'ParsedContract',
        source_code: str,
        file_path: str
    ) -> List[Finding]:
        """
        Analyze a contract's AST for vulnerabilities.
        
        Args:
            ast: The contract's AST.
            contract: The parsed contract data.
            source_code: Original source code.
            file_path: Path to the source file.
            
        Returns:
            List of findings from this contract.
        """
        pass
    
    def get_node_location(
        self,
        node: Dict[str, Any],
        source_code: str,
        file_path: str
    ) -> SourceLocation:
        """
        Get the source location for an AST node.
        
        Args:
            node: AST node with location information.
            source_code: Original source code.
            file_path: Path to the source file.
            
        Returns:
            SourceLocation object.
        """
        parser = SolidityParser(SolcConfig())
        
        line_start, col_start, line_end, col_end = parser.get_source_location(node, source_code)
        
        return SourceLocation(
            file_path=file_path,
            line_start=line_start,
            line_end=line_end if line_end != line_start else None,
            column_start=col_start,
            column_end=col_end if col_end != col_start else None
        )
