"""
AST-based reentrancy vulnerability detector for ContractQuard.

This detector analyzes the Abstract Syntax Tree to identify potential
reentrancy vulnerabilities in Solidity contracts.
"""

from typing import List, Dict, Any, Set, Optional
import logging

from ..core.findings import Severity, Finding
from ..parsers.solidity_parser import ParsedContract
from .base import ASTDetector


class ReentrancyDetector(ASTDetector):
    """
    AST-based detector for reentrancy vulnerabilities.
    
    This detector identifies patterns where external calls are made before
    state variables are updated, which can lead to reentrancy attacks.
    """
    
    @property
    def name(self) -> str:
        return "ast_reentrancy_detector"
    
    @property
    def description(self) -> str:
        return "Detects potential reentrancy vulnerabilities using AST analysis"
    
    @property
    def vulnerability_types(self) -> List[str]:
        return ["reentrancy", "state_change_after_call"]
    
    @property
    def default_severity(self) -> Severity:
        return Severity.HIGH
    
    def analyze_contract_ast(
        self,
        ast: Dict[str, Any],
        contract: ParsedContract,
        source_code: str,
        file_path: str
    ) -> List[Finding]:
        """
        Analyze contract AST for reentrancy vulnerabilities.
        
        Args:
            ast: Contract AST.
            contract: Parsed contract data.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            List of reentrancy findings.
        """
        findings = []
        
        # Get all function definitions
        functions = self._extract_functions(ast)
        
        for function in functions:
            function_findings = self._analyze_function_for_reentrancy(
                function, source_code, file_path
            )
            findings.extend(function_findings)
        
        return findings
    
    def _extract_functions(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all function definitions from the AST."""
        functions = []
        
        def traverse(node):
            if isinstance(node, dict):
                if node.get('nodeType') == 'FunctionDefinition':
                    functions.append(node)
                
                # Traverse children
                for key, value in node.items():
                    if isinstance(value, list):
                        for item in value:
                            traverse(item)
                    elif isinstance(value, dict):
                        traverse(value)
        
        traverse(ast)
        return functions
    
    def _analyze_function_for_reentrancy(
        self,
        function: Dict[str, Any],
        source_code: str,
        file_path: str
    ) -> List[Finding]:
        """
        Analyze a single function for reentrancy vulnerabilities.
        
        Args:
            function: Function AST node.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            List of findings for this function.
        """
        findings = []
        
        # Skip view/pure functions as they can't have reentrancy issues
        if self._is_view_or_pure_function(function):
            return findings
        
        # Get function body
        body = function.get('body', {})
        if not body or body.get('nodeType') != 'Block':
            return findings
        
        # Analyze statements in the function body
        statements = body.get('statements', [])
        
        # Track external calls and state changes
        external_calls = []
        state_changes = []
        
        for i, statement in enumerate(statements):
            # Find external calls
            calls = self._find_external_calls(statement)
            for call in calls:
                external_calls.append({
                    'call': call,
                    'statement_index': i,
                    'statement': statement
                })
            
            # Find state changes
            changes = self._find_state_changes(statement)
            for change in changes:
                state_changes.append({
                    'change': change,
                    'statement_index': i,
                    'statement': statement
                })
        
        # Check for reentrancy patterns
        reentrancy_findings = self._check_reentrancy_pattern(
            external_calls, state_changes, function, source_code, file_path
        )
        findings.extend(reentrancy_findings)
        
        return findings
    
    def _is_view_or_pure_function(self, function: Dict[str, Any]) -> bool:
        """Check if function is view or pure."""
        modifiers = function.get('modifiers', [])
        for modifier in modifiers:
            if modifier.get('name') in ['view', 'pure', 'constant']:
                return True
        
        # Check state mutability
        state_mutability = function.get('stateMutability')
        return state_mutability in ['view', 'pure']
    
    def _find_external_calls(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find external calls in an AST node."""
        external_calls = []
        
        def traverse(n):
            if isinstance(n, dict):
                node_type = n.get('nodeType')
                
                # Check for function calls
                if node_type == 'FunctionCall':
                    expression = n.get('expression', {})
                    
                    # Check for member access (e.g., address.call())
                    if expression.get('nodeType') == 'MemberAccess':
                        member_name = expression.get('memberName', '')
                        
                        # External call methods
                        if member_name in ['call', 'delegatecall', 'staticcall', 'send', 'transfer']:
                            external_calls.append(n)
                        
                        # Check for contract calls (harder to detect generically)
                        elif self._is_likely_external_call(expression):
                            external_calls.append(n)
                
                # Traverse children
                for key, value in n.items():
                    if isinstance(value, list):
                        for item in value:
                            traverse(item)
                    elif isinstance(value, dict):
                        traverse(value)
        
        traverse(node)
        return external_calls
    
    def _is_likely_external_call(self, expression: Dict[str, Any]) -> bool:
        """Heuristic to determine if a member access is likely an external call."""
        # This is a simplified heuristic
        # In practice, you'd need more sophisticated analysis
        
        base_expression = expression.get('expression', {})
        
        # Check if calling on an address or contract variable
        if base_expression.get('nodeType') == 'Identifier':
            # Could be a contract instance
            return True
        
        return False
    
    def _find_state_changes(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find state variable changes in an AST node."""
        state_changes = []
        
        def traverse(n):
            if isinstance(n, dict):
                node_type = n.get('nodeType')
                
                # Assignment operations
                if node_type == 'Assignment':
                    left = n.get('left', {})
                    
                    # Check if assigning to state variable
                    if self._is_state_variable_access(left):
                        state_changes.append(n)
                
                # Unary operations (++, --)
                elif node_type == 'UnaryOperation':
                    operator = n.get('operator')
                    if operator in ['++', '--']:
                        sub_expression = n.get('subExpression', {})
                        if self._is_state_variable_access(sub_expression):
                            state_changes.append(n)
                
                # Traverse children
                for key, value in n.items():
                    if isinstance(value, list):
                        for item in value:
                            traverse(item)
                    elif isinstance(value, dict):
                        traverse(value)
        
        traverse(node)
        return state_changes
    
    def _is_state_variable_access(self, node: Dict[str, Any]) -> bool:
        """Check if a node represents access to a state variable."""
        # This is a simplified check
        # In practice, you'd need to track variable declarations and scopes
        
        if node.get('nodeType') == 'Identifier':
            # Simple identifier - could be state variable
            return True
        
        elif node.get('nodeType') == 'IndexAccess':
            # Array/mapping access - likely state variable
            base = node.get('baseExpression', {})
            return self._is_state_variable_access(base)
        
        elif node.get('nodeType') == 'MemberAccess':
            # Struct member access
            expression = node.get('expression', {})
            return self._is_state_variable_access(expression)
        
        return False
    
    def _check_reentrancy_pattern(
        self,
        external_calls: List[Dict],
        state_changes: List[Dict],
        function: Dict[str, Any],
        source_code: str,
        file_path: str
    ) -> List[Finding]:
        """
        Check for reentrancy patterns in the collected calls and state changes.
        
        Args:
            external_calls: List of external calls with their positions.
            state_changes: List of state changes with their positions.
            function: Function AST node.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            List of reentrancy findings.
        """
        findings = []
        
        # Check for external calls followed by state changes
        for call_info in external_calls:
            call_index = call_info['statement_index']
            
            # Look for state changes after this external call
            for change_info in state_changes:
                change_index = change_info['statement_index']
                
                if change_index > call_index:
                    # Found state change after external call - potential reentrancy
                    finding = self._create_reentrancy_finding(
                        call_info, change_info, function, source_code, file_path
                    )
                    if finding:
                        findings.append(finding)
                    break  # Only report first occurrence per call
        
        return findings
    
    def _create_reentrancy_finding(
        self,
        call_info: Dict,
        change_info: Dict,
        function: Dict[str, Any],
        source_code: str,
        file_path: str
    ) -> Optional[Finding]:
        """
        Create a finding for a detected reentrancy pattern.
        
        Args:
            call_info: Information about the external call.
            change_info: Information about the state change.
            function: Function AST node.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            A Finding object or None if invalid.
        """
        call_node = call_info['call']
        change_node = change_info['change']
        
        # Get source locations
        call_location = self.get_node_location(call_node, source_code, file_path)
        change_location = self.get_node_location(change_node, source_code, file_path)
        function_location = self.get_node_location(function, source_code, file_path)

        function_name = function.get('name', 'unknown_function')
        call_type_str = self._get_call_type(call_node)

        title = "Potential Reentrancy Vulnerability"
        description = (
            f"In function '{function_name}', an external call is made on line {call_location.line_start} "
            f"before a state variable is updated on line {change_location.line_start}. "
            f"This pattern can lead to reentrancy attacks if the external call execution can be hijacked."
        )
        
        recommendation = (
            "Ensure that all state changes are made before external calls (Checks-Effects-Interactions pattern). "
            "Consider using reentrancy guards if necessary."
        )
        
        # Extract code snippet around the call and state change
        # For simplicity, we'll center the snippet around the function if call/change are far apart
        # A more sophisticated approach might combine snippets or show a broader function context.
        snippet_line_start = min(call_location.line_start, change_location.line_start)
        snippet_line_end = max(call_location.line_start, change_location.line_start)
        
        # Ensure snippet focuses on the relevant parts within the function
        snippet_start_in_func = max(function_location.line_start, snippet_line_start - 2)
        snippet_end_in_func = min(function_location.line_end or snippet_start_in_func + 10, snippet_line_end + 2) # Ensure line_end is not None

        code_snippet = self.extract_code_snippet(
            source_code,
            line_start=snippet_start_in_func,
            line_end=snippet_end_in_func,
            context_lines=1 # We already added context with snippet_start/end_in_func
        )

        finding_metadata = {
            "vulnerable_function_name": function_name,
            "external_call_line": call_location.line_start,
            "external_call_details": call_type_str,
            "state_change_line": change_location.line_start,
            "interaction_pattern": "External Call Before State Update"
        }
        
        return self.create_finding(
            title=title,
            description=description,
            location=function_location, # Main location is the function
            vulnerability_type="reentrancy",
            severity=self.default_severity,
            code_snippet=code_snippet,
            recommendation=recommendation,
            references=[
                "https://swcregistry.io/docs/SWC-107",
                "https://consensys.github.io/smart-contract-best-practices/attacks/reentrancy/"
            ],
            metadata=finding_metadata
        )
    
    def _get_call_type(self, call_node: Dict[str, Any]) -> str:
        """Get the type of external call."""
        expression = call_node.get('expression', {})
        if expression.get('nodeType') == 'MemberAccess':
            return expression.get('memberName', 'unknown')
        return 'function_call'
