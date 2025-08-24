"""
AST (Abstract Syntax Tree) Parser and Analyzer for Solidity
"""

import re
import json
import tempfile
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from .base import BaseAnalyzer, AnalysisFinding, Severity

class ASTAnalyzer(BaseAnalyzer):
    """AST-based analyzer for deep code structure analysis"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['sol']
        
    def supports_language(self, language: str) -> bool:
        return language.lower() in self.supported_extensions
    
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Perform AST-based analysis
        
        Args:
            filename: Name of the Solidity file
            content: Contract source code
            
        Returns:
            List of AST-based findings
        """
        findings = []
        
        try:
            # Parse AST
            ast_data = self._parse_ast(content)
            if not ast_data:
                return findings
            
            # Extract contract information
            contracts = self._extract_contracts(ast_data)
            
            # Analyze each contract
            for contract in contracts:
                findings.extend(self._analyze_contract_ast(contract, content))
                
        except Exception as e:
            print(f"AST analysis failed: {e}")
        
        return findings
    
    def _parse_ast(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse Solidity code to AST using solc"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Use solc to generate AST
            result = subprocess.run([
                'solc', '--ast-compact-json', temp_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                # Parse JSON output
                for line in result.stdout.splitlines():
                    if line.startswith('{"'):
                        return json.loads(line)
            
            return None
            
        except Exception as e:
            print(f"AST parsing error: {e}")
            return None
    
    def _extract_contracts(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract contract definitions from AST"""
        contracts = []
        
        def traverse_ast(node):
            if isinstance(node, dict):
                if node.get('nodeType') == 'ContractDefinition':
                    contracts.append(node)
                
                # Traverse children
                for key, value in node.items():
                    if isinstance(value, list):
                        for item in value:
                            traverse_ast(item)
                    elif isinstance(value, dict):
                        traverse_ast(value)
        
        traverse_ast(ast_data)
        return contracts
    
    def _analyze_contract_ast(self, contract: Dict[str, Any], content: str) -> List[AnalysisFinding]:
        """Analyze individual contract AST"""
        findings = []
        
        # Extract functions
        functions = self._extract_functions(contract)
        
        # Extract state variables
        state_vars = self._extract_state_variables(contract)
        
        # Extract modifiers
        modifiers = self._extract_modifiers(contract)
        
        # Extract events
        events = self._extract_events(contract)
        
        # Analyze function patterns
        findings.extend(self._analyze_functions(functions, content))
        
        # Analyze state variable patterns
        findings.extend(self._analyze_state_variables(state_vars, content))
        
        # Analyze modifier usage
        findings.extend(self._analyze_modifiers(modifiers, functions, content))
        
        # Analyze event usage
        findings.extend(self._analyze_events(events, functions, content))
        
        # Create control flow graph
        findings.extend(self._analyze_control_flow(functions, content))
        
        return findings
    
    def _extract_functions(self, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function definitions from contract AST"""
        functions = []
        
        for node in contract.get('nodes', []):
            if node.get('nodeType') == 'FunctionDefinition':
                functions.append(node)
        
        return functions
    
    def _extract_state_variables(self, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract state variable declarations"""
        state_vars = []
        
        for node in contract.get('nodes', []):
            if node.get('nodeType') == 'VariableDeclaration':
                state_vars.append(node)
        
        return state_vars
    
    def _extract_modifiers(self, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract modifier definitions"""
        modifiers = []
        
        for node in contract.get('nodes', []):
            if node.get('nodeType') == 'ModifierDefinition':
                modifiers.append(node)
        
        return modifiers
    
    def _extract_events(self, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract event definitions"""
        events = []
        
        for node in contract.get('nodes', []):
            if node.get('nodeType') == 'EventDefinition':
                events.append(node)
        
        return events
    
    def _analyze_functions(self, functions: List[Dict[str, Any]], content: str) -> List[AnalysisFinding]:
        """Analyze function definitions for vulnerabilities"""
        findings = []
        
        for func in functions:
            func_name = func.get('name', 'unknown')
            
            # Check function visibility
            visibility = func.get('visibility', 'internal')
            if visibility == 'public' and not self._has_access_control(func):
                findings.append(AnalysisFinding(
                    detector="ast_access_control",
                    severity=Severity.MEDIUM,
                    title="Missing Access Control in Public Function",
                    description=f"Function '{func_name}' is public but lacks access control",
                    line_number=self._get_line_number(func),
                    code_snippet=self._extract_function_signature(func, content),
                    recommendation="Add appropriate access control modifiers",
                    category="Access Control"
                ))
            
            # Check for state changes in view/pure functions
            if func.get('stateMutability') in ['view', 'pure']:
                if self._has_state_changes(func):
                    findings.append(AnalysisFinding(
                        detector="ast_state_mutability",
                        severity=Severity.HIGH,
                        title="State Changes in View/Pure Function",
                        description=f"Function '{func_name}' declared as view/pure but modifies state",
                        line_number=self._get_line_number(func),
                        code_snippet=self._extract_function_signature(func, content),
                        recommendation="Remove state modifications or change function mutability",
                        category="State Mutability"
                    ))
            
            # Check for external calls
            external_calls = self._find_external_calls(func)
            if external_calls:
                findings.append(AnalysisFinding(
                    detector="ast_external_calls",
                    severity=Severity.MEDIUM,
                    title="External Call Detected",
                    description=f"Function '{func_name}' makes external calls",
                    line_number=self._get_line_number(func),
                    code_snippet=self._extract_function_signature(func, content),
                    recommendation="Ensure external calls are safe and handle failures",
                    category="External Calls"
                ))
        
        return findings
    
    def _analyze_state_variables(self, state_vars: List[Dict[str, Any]], content: str) -> List[AnalysisFinding]:
        """Analyze state variable declarations"""
        findings = []
        
        for var in state_vars:
            var_name = var.get('name', 'unknown')
            
            # Check for uninitialized state variables
            if not var.get('value') and not self._is_initialized_elsewhere(var_name, content):
                findings.append(AnalysisFinding(
                    detector="ast_uninitialized_state",
                    severity=Severity.MEDIUM,
                    title="Uninitialized State Variable",
                    description=f"State variable '{var_name}' is not initialized",
                    line_number=self._get_line_number(var),
                    code_snippet=self._extract_variable_declaration(var, content),
                    recommendation="Initialize state variables or ensure they are set in constructor",
                    category="Initialization"
                ))
            
            # Check for public state variables that could be constant
            visibility = var.get('visibility', 'internal')
            if visibility == 'public' and not var.get('constant', False):
                if self._could_be_constant(var_name, content):
                    findings.append(AnalysisFinding(
                        detector="ast_constant_state",
                        severity=Severity.LOW,
                        title="State Variable Could Be Constant",
                        description=f"State variable '{var_name}' could be declared as constant",
                        line_number=self._get_line_number(var),
                        code_snippet=self._extract_variable_declaration(var, content),
                        recommendation="Consider declaring as constant if value never changes",
                        category="Gas Optimization"
                    ))
        
        return findings
    
    def _analyze_control_flow(self, functions: List[Dict[str, Any]], content: str) -> List[AnalysisFinding]:
        """Analyze control flow patterns"""
        findings = []
        
        for func in functions:
            func_name = func.get('name', 'unknown')
            
            # Check for complex control flow
            complexity = self._calculate_cyclomatic_complexity(func)
            if complexity > 10:
                findings.append(AnalysisFinding(
                    detector="ast_complexity",
                    severity=Severity.MEDIUM,
                    title="High Cyclomatic Complexity",
                    description=f"Function '{func_name}' has high complexity ({complexity})",
                    line_number=self._get_line_number(func),
                    code_snippet=self._extract_function_signature(func, content),
                    recommendation="Consider breaking down into smaller functions",
                    category="Code Quality"
                ))
            
            # Check for unreachable code
            if self._has_unreachable_code(func):
                findings.append(AnalysisFinding(
                    detector="ast_unreachable",
                    severity=Severity.MEDIUM,
                    title="Unreachable Code Detected",
                    description=f"Function '{func_name}' contains unreachable code",
                    line_number=self._get_line_number(func),
                    code_snippet=self._extract_function_signature(func, content),
                    recommendation="Remove unreachable code",
                    category="Code Quality"
                ))
        
        return findings
    
    # Helper methods
    def _get_line_number(self, node: Dict[str, Any]) -> int:
        """Extract line number from AST node"""
        src = node.get('src', '0:0:0')
        return int(src.split(':')[0]) if ':' in src else 1
    
    def _has_access_control(self, func: Dict[str, Any]) -> bool:
        """Check if function has access control modifiers"""
        modifiers = func.get('modifiers', [])
        access_control_modifiers = ['onlyOwner', 'onlyAdmin', 'requireAuth']
        
        for modifier in modifiers:
            if modifier.get('modifierName', {}).get('name') in access_control_modifiers:
                return True
        return False
    
    def _has_state_changes(self, func: Dict[str, Any]) -> bool:
        """Check if function modifies state"""
        # This would require deeper AST traversal
        # For now, simple heuristic
        return False
    
    def _find_external_calls(self, func: Dict[str, Any]) -> List[str]:
        """Find external calls in function"""
        # This would require deeper AST traversal
        return []
    
    def _calculate_cyclomatic_complexity(self, func: Dict[str, Any]) -> int:
        """Calculate cyclomatic complexity"""
        # Simplified calculation
        return 1
    
    def _has_unreachable_code(self, func: Dict[str, Any]) -> bool:
        """Check for unreachable code"""
        return False
    
    def _is_initialized_elsewhere(self, var_name: str, content: str) -> bool:
        """Check if variable is initialized in constructor"""
        return f"{var_name} =" in content
    
    def _could_be_constant(self, var_name: str, content: str) -> bool:
        """Check if variable could be constant"""
        return f"{var_name} =" not in content.split('constructor')[1] if 'constructor' in content else True
    
    def _extract_function_signature(self, func: Dict[str, Any], content: str) -> str:
        """Extract function signature from content"""
        func_name = func.get('name', 'unknown')
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if f"function {func_name}" in line:
                return f"Line {i+1}: {line.strip()}"
        return f"function {func_name}(...)"
    
    def _extract_variable_declaration(self, var: Dict[str, Any], content: str) -> str:
        """Extract variable declaration from content"""
        var_name = var.get('name', 'unknown')
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if var_name in line and ('uint' in line or 'address' in line or 'bool' in line):
                return f"Line {i+1}: {line.strip()}"
        return f"{var_name} declaration"
