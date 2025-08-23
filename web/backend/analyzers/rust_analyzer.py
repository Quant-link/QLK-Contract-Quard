"""
Rust smart contract analyzer for ink! and other Rust-based contracts
"""

import re
import subprocess
import tempfile
import os
from typing import List
from .base import BaseAnalyzer, AnalysisFinding, Severity

class RustAnalyzer(BaseAnalyzer):
    """Rust contract analyzer with focus on ink! smart contracts"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['rs']
        
    def supports_language(self, language: str) -> bool:
        """Check if this analyzer supports Rust"""
        return language.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions"""
        return self.supported_extensions
    
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Analyze Rust contract for security vulnerabilities
        
        Args:
            filename: Name of the Rust file
            content: Contract source code
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Run Rust-specific analysis
        findings.extend(self._analyze_panic_conditions(content))
        findings.extend(self._analyze_integer_arithmetic(content))
        findings.extend(self._analyze_ink_patterns(content))
        findings.extend(self._analyze_unsafe_code(content))
        findings.extend(self._analyze_error_handling(content))
        findings.extend(self._analyze_storage_patterns(content))
        findings.extend(self._analyze_cross_contract_calls(content))
        
        # Try Clippy if available
        try:
            clippy_findings = self._run_clippy_analysis(filename, content)
            findings.extend(clippy_findings)
        except Exception as e:
            print(f"Clippy analysis failed: {e}")
        
        return findings
    
    def _analyze_panic_conditions(self, content: str) -> List[AnalysisFinding]:
        """Detect potential panic conditions"""
        findings = []
        lines = content.splitlines()
        
        panic_patterns = [
            (r'\.unwrap\(\)', "unwrap() can panic if the value is None/Err"),
            (r'\.expect\(', "expect() can panic if the value is None/Err"),
            (r'panic!\(', "Direct panic call"),
            (r'assert!\(', "assert! can panic if condition is false"),
            (r'assert_eq!\(', "assert_eq! can panic if values are not equal"),
            (r'\[.*\]', "Array indexing can panic on out-of-bounds access")
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, description in panic_patterns:
                if re.search(pattern, line):
                    findings.append(AnalysisFinding(
                        detector="panic_detector",
                        severity=Severity.MEDIUM,
                        title="Potential Panic Condition",
                        description=description,
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Use proper error handling with Result<T, E> or Option<T>",
                        cwe_id=248
                    ))
        
        return findings
    
    def _analyze_integer_arithmetic(self, content: str) -> List[AnalysisFinding]:
        """Analyze integer arithmetic for overflow/underflow"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for arithmetic operations without checked variants
            if re.search(r'[+\-*/]\s*=|[+\-*/]\s+\w+', line):
                if not re.search(r'(checked_|saturating_|wrapping_)', line):
                    findings.append(AnalysisFinding(
                        detector="integer_arithmetic_detector",
                        severity=Severity.MEDIUM,
                        title="Unchecked Integer Arithmetic",
                        description="Integer arithmetic without overflow protection",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Use checked_add(), checked_sub(), etc. or saturating variants",
                        cwe_id=190
                    ))
        
        return findings
    
    def _analyze_ink_patterns(self, content: str) -> List[AnalysisFinding]:
        """Analyze ink!-specific patterns"""
        findings = []
        lines = content.splitlines()
        
        # Check for ink! contract structure
        is_ink_contract = '#[ink::contract]' in content or '#[ink(storage)]' in content
        
        if is_ink_contract:
            # Check for proper storage initialization
            for i, line in enumerate(lines, 1):
                if '#[ink(constructor)]' in line:
                    # Check if constructor properly initializes all storage
                    constructor_body = self._extract_function_body(lines, i)
                    if not re.search(r'Self\s*{', constructor_body):
                        findings.append(AnalysisFinding(
                            detector="ink_constructor_detector",
                            severity=Severity.HIGH,
                            title="Incomplete Storage Initialization",
                            description="ink! constructor may not properly initialize all storage fields",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Ensure all storage fields are initialized in constructor",
                            category="ink!"
                        ))
                
                # Check for proper message visibility
                if '#[ink(message)]' in line and 'pub' not in line:
                    findings.append(AnalysisFinding(
                        detector="ink_visibility_detector",
                        severity=Severity.LOW,
                        title="ink! Message Visibility",
                        description="ink! message function should be public",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Add 'pub' keyword to ink! message functions",
                        category="ink!"
                    ))
        
        return findings
    
    def _analyze_unsafe_code(self, content: str) -> List[AnalysisFinding]:
        """Detect unsafe code blocks"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if re.search(r'unsafe\s*{', line):
                findings.append(AnalysisFinding(
                    detector="unsafe_code_detector",
                    severity=Severity.HIGH,
                    title="Unsafe Code Block",
                    description="Unsafe code block bypasses Rust's safety guarantees",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Minimize unsafe code and ensure memory safety",
                    cwe_id=119
                ))
        
        return findings
    
    def _analyze_error_handling(self, content: str) -> List[AnalysisFinding]:
        """Analyze error handling patterns"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for ignored Results
            if re.search(r'\.unwrap_or\(.*\);', line) or re.search(r'let\s+_\s*=.*\.unwrap', line):
                findings.append(AnalysisFinding(
                    detector="error_handling_detector",
                    severity=Severity.LOW,
                    title="Ignored Error Result",
                    description="Error result is being ignored or handled with default value",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Properly handle error cases with match or if-let",
                    cwe_id=252
                ))
        
        return findings
    
    def _analyze_storage_patterns(self, content: str) -> List[AnalysisFinding]:
        """Analyze storage access patterns"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for direct storage field access without proper encapsulation
            if re.search(r'self\.\w+\s*=', line) and '#[ink(message)]' in '\n'.join(lines[max(0, i-10):i]):
                findings.append(AnalysisFinding(
                    detector="storage_access_detector",
                    severity=Severity.LOW,
                    title="Direct Storage Access",
                    description="Direct storage field modification in message function",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Consider using getter/setter methods for storage access",
                    category="Storage"
                ))
        
        return findings
    
    def _analyze_cross_contract_calls(self, content: str) -> List[AnalysisFinding]:
        """Analyze cross-contract call patterns"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for cross-contract calls
            if re.search(r'\.call\(', line) or re.search(r'ContractRef::', line):
                findings.append(AnalysisFinding(
                    detector="cross_contract_detector",
                    severity=Severity.MEDIUM,
                    title="Cross-Contract Call",
                    description="Cross-contract call detected - ensure proper error handling",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Handle cross-contract call failures and validate return values",
                    category="Cross-Contract"
                ))
        
        return findings
    
    def _extract_function_body(self, lines: List[str], start_line: int) -> str:
        """Extract function body starting from a line"""
        body_lines = []
        brace_count = 0
        started = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            if '{' in line:
                started = True
                brace_count += line.count('{')
            if started:
                body_lines.append(line)
                brace_count -= line.count('}')
                if brace_count <= 0:
                    break
        
        return '\n'.join(body_lines)
    
    def _run_clippy_analysis(self, filename: str, content: str) -> List[AnalysisFinding]:
        """Run Clippy analysis if available"""
        findings = []
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            # Run Clippy
            result = subprocess.run(
                ['cargo', 'clippy', '--', '--message-format=short'],
                cwd=os.path.dirname(temp_file),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse Clippy output
            if result.stderr:
                lines = result.stderr.splitlines()
                for line in lines:
                    if 'warning:' in line or 'error:' in line:
                        severity = Severity.MEDIUM if 'warning:' in line else Severity.HIGH
                        findings.append(AnalysisFinding(
                            detector="clippy_detector",
                            severity=severity,
                            title="Clippy Lint",
                            description=line.strip(),
                            line_number=1,
                            code_snippet="",
                            recommendation="Follow Clippy suggestions for better code quality",
                            category="Clippy"
                        ))
            
            # Clean up
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"Clippy analysis error: {e}")
        
        return findings
