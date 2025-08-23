"""
Solidity smart contract analyzer using multiple detection methods
"""

import re
import os
import tempfile
import subprocess
from typing import List, Dict, Any
from .base import BaseAnalyzer, AnalysisFinding, Severity

class SolidityAnalyzer(BaseAnalyzer):
    """Solidity contract analyzer with comprehensive vulnerability detection"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['sol']
        
    def supports_language(self, language: str) -> bool:
        """Check if this analyzer supports Solidity"""
        return language.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions"""
        return self.supported_extensions
    
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Analyze Solidity contract for security vulnerabilities
        
        Args:
            filename: Name of the Solidity file
            content: Contract source code
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Run multiple analysis methods
        findings.extend(self._analyze_reentrancy(content))
        findings.extend(self._analyze_access_control(content))
        findings.extend(self._analyze_integer_overflow(content))
        findings.extend(self._analyze_timestamp_dependence(content))
        findings.extend(self._analyze_unchecked_calls(content))
        findings.extend(self._analyze_gas_issues(content))
        findings.extend(self._analyze_tx_origin(content))
        findings.extend(self._analyze_uninitialized_storage(content))
        findings.extend(self._analyze_deprecated_functions(content))
        findings.extend(self._analyze_visibility_issues(content))
        
        # Try Slither if available
        try:
            slither_findings = self._run_slither_analysis(filename, content)
            findings.extend(slither_findings)
        except Exception as e:
            print(f"Slither analysis failed: {e}")
        
        return findings
    
    def _analyze_reentrancy(self, content: str) -> List[AnalysisFinding]:
        """Detect potential reentrancy vulnerabilities"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for external calls followed by state changes
            if re.search(r'\.(call|send|transfer)\s*\(', line, re.IGNORECASE):
                # Check if there are state changes after this call
                for j in range(i, min(i + 10, len(lines))):
                    if re.search(r'(balances?\[|\.balance\s*=|state\s*=)', lines[j], re.IGNORECASE):
                        findings.append(AnalysisFinding(
                            detector="reentrancy_detector",
                            severity=Severity.HIGH,
                            title="Potential Reentrancy Vulnerability",
                            description="External call followed by state change may be vulnerable to reentrancy attacks",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Use the checks-effects-interactions pattern or add reentrancy guards",
                            cwe_id=841,
                            references=["https://consensys.github.io/smart-contract-best-practices/attacks/reentrancy/"]
                        ))
                        break
        
        return findings
    
    def _analyze_access_control(self, content: str) -> List[AnalysisFinding]:
        """Analyze access control patterns"""
        findings = []
        lines = content.splitlines()
        
        # Check for missing access control on critical functions
        for i, line in enumerate(lines, 1):
            if re.search(r'function\s+\w+.*public', line, re.IGNORECASE):
                # Check if it modifies state
                if re.search(r'(payable|nonpayable)', line) or any(
                    re.search(r'(=|\+=|-=|\*=|/=)', lines[j]) 
                    for j in range(i, min(i + 20, len(lines)))
                ):
                    # Check if it has access control
                    function_body = '\n'.join(lines[i:min(i + 20, len(lines))])
                    if not re.search(r'(onlyOwner|require\s*\(.*msg\.sender|modifier)', function_body, re.IGNORECASE):
                        findings.append(AnalysisFinding(
                            detector="access_control_detector",
                            severity=Severity.MEDIUM,
                            title="Missing Access Control",
                            description="Public function that modifies state lacks access control",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Add appropriate access control modifiers or require statements",
                            cwe_id=284
                        ))
        
        return findings
    
    def _analyze_integer_overflow(self, content: str) -> List[AnalysisFinding]:
        """Detect potential integer overflow/underflow"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for arithmetic operations without SafeMath
            if re.search(r'[+\-*/]\s*=|[+\-*/]\s+\w+', line):
                if not re.search(r'SafeMath|unchecked', content):
                    findings.append(AnalysisFinding(
                        detector="integer_overflow_detector",
                        severity=Severity.MEDIUM,
                        title="Potential Integer Overflow/Underflow",
                        description="Arithmetic operation without overflow protection",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Use SafeMath library or Solidity 0.8+ built-in overflow protection",
                        cwe_id=190
                    ))
                    break  # Only report once per contract
        
        return findings
    
    def _analyze_timestamp_dependence(self, content: str) -> List[AnalysisFinding]:
        """Detect timestamp dependence issues"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if re.search(r'(block\.timestamp|now)\s*[<>=]', line, re.IGNORECASE):
                findings.append(AnalysisFinding(
                    detector="timestamp_dependence_detector",
                    severity=Severity.LOW,
                    title="Timestamp Dependence",
                    description="Contract behavior depends on block timestamp which can be manipulated",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Avoid using block.timestamp for critical logic or use block numbers instead",
                    cwe_id=829
                ))
        
        return findings
    
    def _analyze_unchecked_calls(self, content: str) -> List[AnalysisFinding]:
        """Detect unchecked external calls"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if re.search(r'\.call\s*\(', line) and not re.search(r'require\s*\(.*\.call', line):
                findings.append(AnalysisFinding(
                    detector="unchecked_call_detector",
                    severity=Severity.MEDIUM,
                    title="Unchecked External Call",
                    description="External call return value is not checked",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Check the return value of external calls",
                    cwe_id=252
                ))
        
        return findings
    
    def _analyze_gas_issues(self, content: str) -> List[AnalysisFinding]:
        """Detect gas-related issues"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for loops that might consume too much gas
            if re.search(r'for\s*\(.*;\s*\w+\s*<\s*\w+\.length', line):
                findings.append(AnalysisFinding(
                    detector="gas_limit_detector",
                    severity=Severity.MEDIUM,
                    title="Potential Gas Limit Issue",
                    description="Loop over dynamic array may consume excessive gas",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Consider pagination or limiting array size",
                    cwe_id=400
                ))
        
        return findings
    
    def _analyze_tx_origin(self, content: str) -> List[AnalysisFinding]:
        """Detect tx.origin usage"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if re.search(r'tx\.origin', line, re.IGNORECASE):
                findings.append(AnalysisFinding(
                    detector="tx_origin_detector",
                    severity=Severity.MEDIUM,
                    title="Use of tx.origin",
                    description="Using tx.origin for authorization is vulnerable to phishing attacks",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Use msg.sender instead of tx.origin for authorization",
                    cwe_id=346
                ))
        
        return findings
    
    def _analyze_uninitialized_storage(self, content: str) -> List[AnalysisFinding]:
        """Detect uninitialized storage pointers"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if re.search(r'storage\s+\w+;', line) and not re.search(r'=', line):
                findings.append(AnalysisFinding(
                    detector="uninitialized_storage_detector",
                    severity=Severity.HIGH,
                    title="Uninitialized Storage Pointer",
                    description="Storage pointer is declared but not initialized",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Initialize storage pointers before use",
                    cwe_id=824
                ))
        
        return findings
    
    def _analyze_deprecated_functions(self, content: str) -> List[AnalysisFinding]:
        """Detect deprecated function usage"""
        findings = []
        lines = content.splitlines()
        
        deprecated_functions = ['suicide', 'sha3', 'callcode', 'throw']
        
        for i, line in enumerate(lines, 1):
            for func in deprecated_functions:
                if re.search(rf'\b{func}\s*\(', line, re.IGNORECASE):
                    findings.append(AnalysisFinding(
                        detector="deprecated_function_detector",
                        severity=Severity.LOW,
                        title=f"Deprecated Function: {func}",
                        description=f"Use of deprecated function {func}",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation=f"Replace {func} with modern equivalent",
                        cwe_id=477
                    ))
        
        return findings
    
    def _analyze_visibility_issues(self, content: str) -> List[AnalysisFinding]:
        """Detect visibility issues"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for functions without explicit visibility
            if re.search(r'function\s+\w+\s*\([^)]*\)\s*{', line) and not re.search(r'(public|private|internal|external)', line):
                findings.append(AnalysisFinding(
                    detector="visibility_detector",
                    severity=Severity.LOW,
                    title="Missing Function Visibility",
                    description="Function lacks explicit visibility specifier",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Add explicit visibility specifier (public, private, internal, external)",
                    cwe_id=710
                ))
        
        return findings
    
    def _run_slither_analysis(self, filename: str, content: str) -> List[AnalysisFinding]:
        """Run Slither analysis if available"""
        findings = []

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
                f.write(content)
                temp_file = f.name

            # Run Slither with simpler output format
            result = subprocess.run(
                ['slither', temp_file, '--print', 'human-summary'],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse simple text output instead of JSON
            if result.stdout:
                lines = result.stdout.splitlines()
                for line in lines:
                    if 'High' in line or 'Medium' in line or 'Low' in line:
                        severity = Severity.MEDIUM
                        if 'High' in line:
                            severity = Severity.HIGH
                        elif 'Low' in line:
                            severity = Severity.LOW

                        findings.append(AnalysisFinding(
                            detector="slither_detector",
                            severity=severity,
                            title="Slither Detection",
                            description=line.strip(),
                            line_number=1,
                            code_snippet="",
                            recommendation="Review Slither output for details",
                            category="Slither"
                        ))

            # Clean up
            os.unlink(temp_file)

        except Exception as e:
            print(f"Slither analysis error: {e}")

        return findings
