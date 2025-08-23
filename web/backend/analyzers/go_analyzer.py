"""
Go smart contract analyzer for Cosmos SDK and other Go-based contracts
"""

import re
import subprocess
import tempfile
import os
from typing import List
from .base import BaseAnalyzer, AnalysisFinding, Severity

class GoAnalyzer(BaseAnalyzer):
    """Go contract analyzer with focus on Cosmos SDK smart contracts"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['go']
        
    def supports_language(self, language: str) -> bool:
        """Check if this analyzer supports Go"""
        return language.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions"""
        return self.supported_extensions
    
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Analyze Go contract for security vulnerabilities
        
        Args:
            filename: Name of the Go file
            content: Contract source code
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Run Go-specific analysis
        findings.extend(self._analyze_error_handling(content))
        findings.extend(self._analyze_cosmos_sdk_patterns(content))
        findings.extend(self._analyze_keeper_security(content))
        findings.extend(self._analyze_message_validation(content))
        findings.extend(self._analyze_state_machine(content))
        findings.extend(self._analyze_gas_metering(content))
        findings.extend(self._analyze_permission_checks(content))
        findings.extend(self._analyze_panic_conditions(content))
        
        # Try gosec if available
        try:
            gosec_findings = self._run_gosec_analysis(filename, content)
            findings.extend(gosec_findings)
        except Exception as e:
            print(f"Gosec analysis failed: {e}")
        
        return findings
    
    def _analyze_error_handling(self, content: str) -> List[AnalysisFinding]:
        """Analyze error handling patterns"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for ignored errors
            if re.search(r'_,\s*_\s*:=', line) or re.search(r'_\s*:=.*\(.*\)', line):
                if 'err' in line:
                    findings.append(AnalysisFinding(
                        detector="error_handling_detector",
                        severity=Severity.MEDIUM,
                        title="Ignored Error",
                        description="Error return value is being ignored",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Properly handle error return values",
                        cwe_id=252
                    ))
            
            # Look for panic instead of error return
            if re.search(r'panic\(', line):
                findings.append(AnalysisFinding(
                    detector="panic_detector",
                    severity=Severity.HIGH,
                    title="Panic Usage",
                    description="Using panic instead of proper error handling",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Return errors instead of panicking",
                    cwe_id=248
                ))
        
        return findings
    
    def _analyze_cosmos_sdk_patterns(self, content: str) -> List[AnalysisFinding]:
        """Analyze Cosmos SDK specific patterns"""
        findings = []
        lines = content.splitlines()
        
        # Check if this is a Cosmos SDK module
        is_cosmos_module = any(
            import_line for import_line in lines 
            if 'github.com/cosmos/cosmos-sdk' in import_line
        )
        
        if is_cosmos_module:
            for i, line in enumerate(lines, 1):
                # Check for proper message validation
                if 'func (msg' in line and 'ValidateBasic()' in line:
                    # Check if validation is comprehensive
                    validation_body = self._extract_function_body(lines, i)
                    if not re.search(r'(len\(|strings\.TrimSpace|sdk\.AccAddress)', validation_body):
                        findings.append(AnalysisFinding(
                            detector="cosmos_validation_detector",
                            severity=Severity.MEDIUM,
                            title="Incomplete Message Validation",
                            description="ValidateBasic() may not perform comprehensive validation",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Validate all message fields including addresses and amounts",
                            category="Cosmos SDK"
                        ))
                
                # Check for proper keeper usage
                if 'keeper.' in line and 'Set' in line:
                    if not re.search(r'(ctx\.KVStore|store\.Set)', content):
                        findings.append(AnalysisFinding(
                            detector="cosmos_keeper_detector",
                            severity=Severity.LOW,
                            title="Direct Keeper Usage",
                            description="Direct keeper method usage without store abstraction",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Use proper store abstraction for state management",
                            category="Cosmos SDK"
                        ))
        
        return findings
    
    def _analyze_keeper_security(self, content: str) -> List[AnalysisFinding]:
        """Analyze keeper security patterns"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for unauthorized keeper access
            if re.search(r'func\s+\(k\s+Keeper\)', line):
                function_body = self._extract_function_body(lines, i)
                if not re.search(r'(ctx\.IsCheckTx|ctx\.IsReCheckTx|authority)', function_body):
                    if re.search(r'(Set|Delete|Store)', function_body):
                        findings.append(AnalysisFinding(
                            detector="keeper_security_detector",
                            severity=Severity.HIGH,
                            title="Unauthorized Keeper Access",
                            description="Keeper method modifies state without proper authorization checks",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Add proper authorization checks before state modifications",
                            category="Keeper Security"
                        ))
        
        return findings
    
    def _analyze_message_validation(self, content: str) -> List[AnalysisFinding]:
        """Analyze message validation patterns"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for message handler functions
            if re.search(r'func\s+.*Handle.*Msg', line):
                handler_body = self._extract_function_body(lines, i)
                
                # Check for input validation
                if not re.search(r'(ValidateBasic|len\(|strings\.TrimSpace)', handler_body):
                    findings.append(AnalysisFinding(
                        detector="message_validation_detector",
                        severity=Severity.MEDIUM,
                        title="Missing Input Validation",
                        description="Message handler lacks proper input validation",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Add comprehensive input validation in message handlers",
                        category="Message Validation"
                    ))
                
                # Check for authorization
                if not re.search(r'(msg\.GetSigners|sdk\.AccAddress)', handler_body):
                    findings.append(AnalysisFinding(
                        detector="authorization_detector",
                        severity=Severity.HIGH,
                        title="Missing Authorization Check",
                        description="Message handler lacks authorization verification",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Verify message signer authorization before processing",
                        category="Authorization"
                    ))
        
        return findings
    
    def _analyze_state_machine(self, content: str) -> List[AnalysisFinding]:
        """Analyze state machine transitions"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for state transitions
            if re.search(r'\.SetState\(|\.UpdateState\(', line):
                # Check if state transition is validated
                context_lines = lines[max(0, i-5):i+5]
                context = '\n'.join(context_lines)
                
                if not re.search(r'(if.*state|switch.*state|ValidateTransition)', context):
                    findings.append(AnalysisFinding(
                        detector="state_machine_detector",
                        severity=Severity.MEDIUM,
                        title="Unvalidated State Transition",
                        description="State transition without proper validation",
                        line_number=i,
                        code_snippet=self.extract_code_snippet(content, i),
                        recommendation="Validate state transitions before applying changes",
                        category="State Machine"
                    ))
        
        return findings
    
    def _analyze_gas_metering(self, content: str) -> List[AnalysisFinding]:
        """Analyze gas metering patterns"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for loops that might consume excessive gas
            if re.search(r'for\s+.*range', line) or re.search(r'for\s+.*;.*{', line):
                loop_body = self._extract_loop_body(lines, i)
                
                # Check if loop has gas consumption controls
                if not re.search(r'(ctx\.GasMeter|ConsumeGas|OutOfGas)', loop_body):
                    if len(loop_body.splitlines()) > 5:  # Complex loop
                        findings.append(AnalysisFinding(
                            detector="gas_metering_detector",
                            severity=Severity.MEDIUM,
                            title="Potential Gas Limit Issue",
                            description="Loop without gas metering may cause out-of-gas errors",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Add gas consumption checks in loops",
                            category="Gas Metering"
                        ))
        
        return findings
    
    def _analyze_permission_checks(self, content: str) -> List[AnalysisFinding]:
        """Analyze permission and access control"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for admin/governance functions
            if re.search(r'(Admin|Gov|Authority|Owner)', line, re.IGNORECASE):
                if 'func' in line:
                    function_body = self._extract_function_body(lines, i)
                    
                    # Check for permission verification
                    if not re.search(r'(authority|admin|gov|owner|permission)', function_body, re.IGNORECASE):
                        findings.append(AnalysisFinding(
                            detector="permission_detector",
                            severity=Severity.HIGH,
                            title="Missing Permission Check",
                            description="Administrative function lacks permission verification",
                            line_number=i,
                            code_snippet=self.extract_code_snippet(content, i),
                            recommendation="Add proper permission checks for administrative functions",
                            category="Access Control"
                        ))
        
        return findings
    
    def _analyze_panic_conditions(self, content: str) -> List[AnalysisFinding]:
        """Analyze potential panic conditions"""
        findings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for array/slice access without bounds checking
            if re.search(r'\[\d+\]|\[.*\]', line) and not re.search(r'(len\(|cap\()', line):
                findings.append(AnalysisFinding(
                    detector="bounds_check_detector",
                    severity=Severity.MEDIUM,
                    title="Potential Index Out of Bounds",
                    description="Array/slice access without bounds checking",
                    line_number=i,
                    code_snippet=self.extract_code_snippet(content, i),
                    recommendation="Check array/slice bounds before accessing elements",
                    cwe_id=125
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
    
    def _extract_loop_body(self, lines: List[str], start_line: int) -> str:
        """Extract loop body starting from a line"""
        return self._extract_function_body(lines, start_line)
    
    def _run_gosec_analysis(self, filename: str, content: str) -> List[AnalysisFinding]:
        """Run gosec analysis if available"""
        findings = []
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            # Run gosec
            result = subprocess.run(
                ['gosec', '-fmt=text', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse gosec output
            if result.stdout:
                lines = result.stdout.splitlines()
                for line in lines:
                    if 'Severity:' in line:
                        severity = Severity.MEDIUM
                        if 'HIGH' in line:
                            severity = Severity.HIGH
                        elif 'LOW' in line:
                            severity = Severity.LOW
                        
                        findings.append(AnalysisFinding(
                            detector="gosec_detector",
                            severity=severity,
                            title="Gosec Security Issue",
                            description=line.strip(),
                            line_number=1,
                            code_snippet="",
                            recommendation="Follow gosec recommendations for security improvements",
                            category="Gosec"
                        ))
            
            # Clean up
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"Gosec analysis error: {e}")
        
        return findings
