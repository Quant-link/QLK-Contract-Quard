"""
Enhanced Slither Framework Integration with 25+ Built-in Detectors
"""

import os
import json
import tempfile
import subprocess
from typing import List, Dict, Any, Optional
from .base import BaseAnalyzer, AnalysisFinding, Severity

class EnhancedSlitherAnalyzer(BaseAnalyzer):
    """Enhanced Slither analyzer with comprehensive detector integration"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['sol']
        
        # 25+ Built-in Slither Detectors
        self.slither_detectors = {
            # High Impact
            'reentrancy-eth': {'severity': Severity.HIGH, 'description': 'Reentrancy vulnerabilities (theft of ethers)'},
            'reentrancy-no-eth': {'severity': Severity.MEDIUM, 'description': 'Reentrancy vulnerabilities (no theft of ethers)'},
            'reentrancy-unlimited-gas': {'severity': Severity.MEDIUM, 'description': 'Reentrancy vulnerabilities through send and transfer'},
            'uninitialized-state': {'severity': Severity.HIGH, 'description': 'Uninitialized state variables'},
            'uninitialized-storage': {'severity': Severity.HIGH, 'description': 'Uninitialized storage variables'},
            'arbitrary-send-eth': {'severity': Severity.HIGH, 'description': 'Functions that send Ether to arbitrary destinations'},
            'controlled-delegatecall': {'severity': Severity.HIGH, 'description': 'Controlled delegatecall destination'},
            'delegatecall-loop': {'severity': Severity.HIGH, 'description': 'Payable functions using delegatecall inside a loop'},
            'msg-value-loop': {'severity': Severity.HIGH, 'description': 'msg.value inside a loop'},
            'contract-interface': {'severity': Severity.MEDIUM, 'description': 'Missing inheritance from interface'},
            
            # Medium Impact  
            'unchecked-lowlevel': {'severity': Severity.MEDIUM, 'description': 'Unchecked low-level calls'},
            'unchecked-send': {'severity': Severity.MEDIUM, 'description': 'Unchecked send'},
            'uninitialized-local': {'severity': Severity.MEDIUM, 'description': 'Uninitialized local variables'},
            'unused-return': {'severity': Severity.MEDIUM, 'description': 'Unused return values'},
            'incorrect-equality': {'severity': Severity.MEDIUM, 'description': 'Dangerous strict equalities'},
            'shadowing-abstract': {'severity': Severity.MEDIUM, 'description': 'State variables shadowing from abstract contracts'},
            'shadowing-state': {'severity': Severity.MEDIUM, 'description': 'State variables shadowing'},
            'shadowing-local': {'severity': Severity.MEDIUM, 'description': 'Local variables shadowing'},
            'shadowing-builtin': {'severity': Severity.MEDIUM, 'description': 'Built-in symbol shadowing'},
            'void-cst': {'severity': Severity.MEDIUM, 'description': 'Constructor called not implemented'},
            'calls-loop': {'severity': Severity.MEDIUM, 'description': 'Multiple calls in a loop'},
            'events-access': {'severity': Severity.MEDIUM, 'description': 'Missing Events Access Control'},
            'events-maths': {'severity': Severity.MEDIUM, 'description': 'Missing Events Arithmetic'},
            'incorrect-unary': {'severity': Severity.MEDIUM, 'description': 'Dangerous unary expressions'},
            'missing-zero-check': {'severity': Severity.MEDIUM, 'description': 'Missing zero address validation'},
            
            # Low Impact
            'pragma': {'severity': Severity.LOW, 'description': 'Different pragma directives are used'},
            'solc-version': {'severity': Severity.LOW, 'description': 'Incorrect Solidity version'},
            'low-level-calls': {'severity': Severity.LOW, 'description': 'Low level calls'},
            'naming-convention': {'severity': Severity.LOW, 'description': 'Conformity to Solidity naming conventions'},
            'external-function': {'severity': Severity.LOW, 'description': 'Public function that could be declared external'},
            'public-mappings': {'severity': Severity.LOW, 'description': 'Public mappings'},
            'too-many-digits': {'severity': Severity.LOW, 'description': 'Conformance to numeric notation best practices'},
            'constable-states': {'severity': Severity.LOW, 'description': 'State variables that could be declared constant'},
            'immutable-states': {'severity': Severity.LOW, 'description': 'State variables that could be declared immutable'},
            'var-read-using-this': {'severity': Severity.LOW, 'description': 'Contract reads its own variable using this'},
        }
    
    def supports_language(self, language: str) -> bool:
        """Check if this analyzer supports Solidity"""
        return language.lower() in self.supported_extensions
    
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Run comprehensive Slither analysis with all detectors
        
        Args:
            filename: Name of the Solidity file
            content: Contract source code
            
        Returns:
            List of security findings from Slither
        """
        findings = []
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Run Slither with JSON output
            findings.extend(self._run_slither_json(temp_path, filename))
            
            # Run specific detector categories
            findings.extend(self._run_detector_category(temp_path, filename, 'high'))
            findings.extend(self._run_detector_category(temp_path, filename, 'medium'))
            findings.extend(self._run_detector_category(temp_path, filename, 'low'))
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"Enhanced Slither analysis failed: {e}")
        
        return findings
    
    def _run_slither_json(self, file_path: str, original_filename: str) -> List[AnalysisFinding]:
        """Run Slither with JSON output for detailed analysis"""
        findings = []
        
        try:
            # Run Slither with JSON output
            result = subprocess.run([
                'slither', file_path,
                '--json', '-',
                '--disable-color',
                '--exclude-informational',
                '--exclude-optimization'
            ], capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                try:
                    slither_output = json.loads(result.stdout)
                    
                    # Parse results
                    if 'results' in slither_output and 'detectors' in slither_output['results']:
                        for detector_result in slither_output['results']['detectors']:
                            finding = self._parse_detector_result(detector_result, original_filename)
                            if finding:
                                findings.append(finding)
                                
                except json.JSONDecodeError:
                    # Fallback to text parsing
                    findings.extend(self._parse_text_output(result.stdout, original_filename))
                    
        except subprocess.TimeoutExpired:
            print("Slither analysis timed out")
        except Exception as e:
            print(f"Slither JSON analysis error: {e}")
            
        return findings
    
    def _run_detector_category(self, file_path: str, original_filename: str, category: str) -> List[AnalysisFinding]:
        """Run specific category of detectors"""
        findings = []
        
        # Get detectors for this category
        category_detectors = [
            name for name, info in self.slither_detectors.items()
            if (category == 'high' and info['severity'] == Severity.HIGH) or
               (category == 'medium' and info['severity'] == Severity.MEDIUM) or
               (category == 'low' and info['severity'] == Severity.LOW)
        ]
        
        for detector in category_detectors[:5]:  # Limit to avoid timeout
            try:
                result = subprocess.run([
                    'slither', file_path,
                    '--detect', detector,
                    '--disable-color'
                ], capture_output=True, text=True, timeout=10)
                
                if result.stdout and detector in result.stdout:
                    finding = AnalysisFinding(
                        detector=f"slither_{detector}",
                        severity=self.slither_detectors[detector]['severity'],
                        title=f"Slither: {detector.replace('-', ' ').title()}",
                        description=self.slither_detectors[detector]['description'],
                        line_number=self._extract_line_number(result.stdout),
                        code_snippet=self._extract_code_snippet(result.stdout),
                        recommendation=f"Review and fix {detector} issues detected by Slither",
                        category="Slither Detection",
                        references=[f"https://github.com/crytic/slither/wiki/Detector-Documentation#{detector}"]
                    )
                    findings.append(finding)
                    
            except subprocess.TimeoutExpired:
                continue
            except Exception:
                continue
                
        return findings
    
    def _parse_detector_result(self, detector_result: Dict[str, Any], filename: str) -> Optional[AnalysisFinding]:
        """Parse individual detector result from JSON"""
        try:
            check = detector_result.get('check', 'unknown')
            impact = detector_result.get('impact', 'Medium')
            confidence = detector_result.get('confidence', 'Medium')
            description = detector_result.get('description', 'Slither detection')
            
            # Map impact to severity
            severity_map = {
                'High': Severity.HIGH,
                'Medium': Severity.MEDIUM,
                'Low': Severity.LOW,
                'Informational': Severity.INFO
            }
            severity = severity_map.get(impact, Severity.MEDIUM)
            
            # Extract elements for line numbers and code
            elements = detector_result.get('elements', [])
            line_number = 1
            code_snippet = ""
            
            if elements:
                for element in elements:
                    if 'source_mapping' in element:
                        source_map = element['source_mapping']
                        if 'lines' in source_map and source_map['lines']:
                            line_number = source_map['lines'][0]
                        break
            
            return AnalysisFinding(
                detector=f"slither_{check}",
                severity=severity,
                title=f"Slither: {check.replace('-', ' ').title()}",
                description=description,
                line_number=line_number,
                code_snippet=code_snippet,
                recommendation=f"Review and address the {check} issue",
                confidence=confidence,
                category="Slither Detection"
            )
            
        except Exception as e:
            print(f"Error parsing detector result: {e}")
            return None
    
    def _parse_text_output(self, output: str, filename: str) -> List[AnalysisFinding]:
        """Parse text output as fallback"""
        findings = []
        lines = output.splitlines()
        
        for line in lines:
            if any(severity in line for severity in ['High', 'Medium', 'Low']):
                severity = Severity.MEDIUM
                if 'High' in line:
                    severity = Severity.HIGH
                elif 'Low' in line:
                    severity = Severity.LOW
                
                findings.append(AnalysisFinding(
                    detector="slither_text",
                    severity=severity,
                    title="Slither Detection",
                    description=line.strip(),
                    line_number=1,
                    code_snippet="",
                    recommendation="Review Slither output for details",
                    category="Slither"
                ))
        
        return findings
    
    def _extract_line_number(self, output: str) -> int:
        """Extract line number from Slither output"""
        import re
        match = re.search(r'#(\d+)', output)
        return int(match.group(1)) if match else 1
    
    def _extract_code_snippet(self, output: str) -> str:
        """Extract code snippet from Slither output"""
        lines = output.splitlines()
        for line in lines:
            if '->' in line or '|' in line:
                return line.strip()
        return ""
