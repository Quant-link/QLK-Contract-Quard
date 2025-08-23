"""
AST-based access control vulnerability detector for ContractQuard.

This detector analyzes the Abstract Syntax Tree to identify potential
access control issues in Solidity contracts.
"""

from typing import List, Dict, Any, Set, Optional
import logging

from ..core.findings import Severity, Finding
from ..parsers.solidity_parser import ParsedContract
from .base import ASTDetector


class AccessControlDetector(ASTDetector):
    """
    AST-based detector for access control vulnerabilities.
    
    This detector identifies functions that modify state or perform privileged
    operations without proper access control mechanisms.
    """
    
    @property
    def name(self) -> str:
        return "ast_access_control_detector"
    
    @property
    def description(self) -> str:
        return "Detects missing or weak access control mechanisms using AST analysis"
    
    @property
    def vulnerability_types(self) -> List[str]:
        return ["missing_access_control", "weak_access_control", "privilege_escalation"]
    
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
        Analyze contract AST for access control issues.
        
        Args:
            ast: Contract AST.
            contract: Parsed contract data.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            List of access control findings.
        """
        findings = []
        
        # Get all function definitions
        functions = self._extract_functions(ast)
        
        # Get all modifier definitions
        modifiers = self._extract_modifiers(ast)
        access_control_modifiers = self._identify_access_control_modifiers(modifiers)
        
        for function in functions:
            function_findings = self._analyze_function_access_control(
                function, access_control_modifiers, source_code, file_path
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
    
    def _extract_modifiers(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all modifier definitions from the AST."""
        modifiers = []
        
        def traverse(node):
            if isinstance(node, dict):
                if node.get('nodeType') == 'ModifierDefinition':
                    modifiers.append(node)
                
                # Traverse children
                for key, value in node.items():
                    if isinstance(value, list):
                        for item in value:
                            traverse(item)
                    elif isinstance(value, dict):
                        traverse(value)
        
        traverse(ast)
        return modifiers
    
    def _identify_access_control_modifiers(self, modifiers: List[Dict[str, Any]]) -> Set[str]:
        """Identify which modifiers are used for access control."""
        access_control_modifiers = set()
        
        # Common access control modifier patterns
        access_control_patterns = [
            'only', 'require', 'owner', 'admin', 'auth', 'permission', 'role'
        ]
        
        for modifier in modifiers:
            modifier_name = modifier.get('name', '').lower()
            
            # Check if modifier name suggests access control
            if any(pattern in modifier_name for pattern in access_control_patterns):
                access_control_modifiers.add(modifier.get('name', ''))
            
            # Check modifier body for access control patterns
            elif self._modifier_has_access_control_logic(modifier):
                access_control_modifiers.add(modifier.get('name', ''))
        
        # Add common standard modifiers
        access_control_modifiers.update([
            'onlyOwner', 'onlyAdmin', 'onlyRole', 'onlyAuthorized',
            'requireOwner', 'requireAdmin', 'auth', 'authorized'
        ])
        
        return access_control_modifiers
    
    def _modifier_has_access_control_logic(self, modifier: Dict[str, Any]) -> bool:
        """Check if a modifier contains access control logic."""
        body = modifier.get('body', {})
        
        # Look for require statements or similar access control patterns
        return self._contains_access_control_statements(body)
    
    def _contains_access_control_statements(self, node: Dict[str, Any]) -> bool:
        """Check if a node contains access control statements."""
        if not isinstance(node, dict):
            return False
        
        node_type = node.get('nodeType')
        
        # Check for require statements
        if node_type == 'FunctionCall':
            expression = node.get('expression', {})
            if (expression.get('nodeType') == 'Identifier' and 
                expression.get('name') == 'require'):
                return True
        
        # Check for revert statements
        elif node_type == 'RevertStatement':
            return True
        
        # Recursively check children
        for key, value in node.items():
            if isinstance(value, list):
                for item in value:
                    if self._contains_access_control_statements(item):
                        return True
            elif isinstance(value, dict):
                if self._contains_access_control_statements(value):
                    return True
        
        return False
    
    def _analyze_function_access_control(
        self,
        function: Dict[str, Any],
        access_control_modifiers: Set[str],
        source_code: str,
        file_path: str
    ) -> List[Finding]:
        """
        Analyze a function for access control issues.
        
        Args:
            function: Function AST node.
            access_control_modifiers: Set of known access control modifier names.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            List of access control findings.
        """
        findings = []
        
        function_name = function.get('name', 'unknown')
        visibility = function.get('visibility', 'internal')
        
        # Skip internal/private functions and view/pure functions
        if visibility in ['internal', 'private']:
            return findings
        
        if self._is_view_or_pure_function(function):
            return findings
        
        # Skip constructor and fallback functions (different access control rules)
        if function.get('isConstructor') or function_name in ['', 'fallback', 'receive']:
            return findings
        
        # Check if function modifies state
        modifies_state = self._function_modifies_state(function)
        
        # Check if function has privileged operations
        has_privileged_ops = self._has_privileged_operations(function)
        
        # Check if function has access control
        has_access_control = self._has_access_control(function, access_control_modifiers)
        
        # Determine if access control is needed
        needs_access_control = (
            modifies_state or 
            has_privileged_ops or 
            self._is_sensitive_function(function_name)
        )
        
        if needs_access_control and not has_access_control:
            finding = self._create_access_control_finding(
                function, source_code, file_path, modifies_state, has_privileged_ops
            )
            if finding:
                findings.append(finding)
        
        return findings
    
    def _is_view_or_pure_function(self, function: Dict[str, Any]) -> bool:
        """Check if function is view or pure."""
        state_mutability = function.get('stateMutability')
        return state_mutability in ['view', 'pure']
    
    def _function_modifies_state(self, function: Dict[str, Any]) -> bool:
        """Check if function modifies contract state."""
        body = function.get('body', {})
        return self._contains_state_modifications(body)
    
    def _contains_state_modifications(self, node: Dict[str, Any]) -> bool:
        """Check if a node contains state modifications."""
        if not isinstance(node, dict):
            return False
        
        node_type = node.get('nodeType')
        
        # Assignment operations
        if node_type == 'Assignment':
            left = node.get('left', {})
            if self._is_state_variable_access(left):
                return True
        
        # Unary operations (++, --)
        elif node_type == 'UnaryOperation':
            operator = node.get('operator')
            if operator in ['++', '--']:
                sub_expression = node.get('subExpression', {})
                if self._is_state_variable_access(sub_expression):
                    return True
        
        # Recursively check children
        for key, value in node.items():
            if isinstance(value, list):
                for item in value:
                    if self._contains_state_modifications(item):
                        return True
            elif isinstance(value, dict):
                if self._contains_state_modifications(value):
                    return True
        
        return False
    
    def _is_state_variable_access(self, node: Dict[str, Any]) -> bool:
        """Check if a node represents access to a state variable."""
        if node.get('nodeType') == 'Identifier':
            return True
        elif node.get('nodeType') == 'IndexAccess':
            base = node.get('baseExpression', {})
            return self._is_state_variable_access(base)
        elif node.get('nodeType') == 'MemberAccess':
            expression = node.get('expression', {})
            return self._is_state_variable_access(expression)
        return False
    
    def _has_privileged_operations(self, function: Dict[str, Any]) -> bool:
        """Check if function contains privileged operations."""
        body = function.get('body', {})
        return self._contains_privileged_operations(body)
    
    def _contains_privileged_operations(self, node: Dict[str, Any]) -> bool:
        """Check if a node contains privileged operations."""
        if not isinstance(node, dict):
            return False
        
        node_type = node.get('nodeType')
        
        # Function calls that might be privileged
        if node_type == 'FunctionCall':
            expression = node.get('expression', {})
            
            # Check for dangerous function calls
            if expression.get('nodeType') == 'Identifier':
                function_name = expression.get('name', '')
                if function_name in ['selfdestruct', 'suicide']:
                    return True
            
            # Check for member access calls
            elif expression.get('nodeType') == 'MemberAccess':
                member_name = expression.get('memberName', '')
                if member_name in ['transfer', 'send', 'call', 'delegatecall']:
                    return True
        
        # Recursively check children
        for key, value in node.items():
            if isinstance(value, list):
                for item in value:
                    if self._contains_privileged_operations(item):
                        return True
            elif isinstance(value, dict):
                if self._contains_privileged_operations(value):
                    return True
        
        return False
    
    def _is_sensitive_function(self, function_name: str) -> bool:
        """Check if function name suggests it's sensitive."""
        sensitive_patterns = [
            'withdraw', 'transfer', 'send', 'mint', 'burn', 'destroy',
            'admin', 'owner', 'upgrade', 'pause', 'unpause', 'emergency',
            'set', 'update', 'change', 'modify', 'configure'
        ]
        
        function_name_lower = function_name.lower()
        return any(pattern in function_name_lower for pattern in sensitive_patterns)
    
    def _has_access_control(self, function: Dict[str, Any], access_control_modifiers: Set[str]) -> bool:
        """Check if function has access control mechanisms."""
        # Check for access control modifiers
        modifiers = function.get('modifiers', [])
        for modifier in modifiers:
            modifier_name = modifier.get('modifierName', {}).get('name', '')
            if modifier_name in access_control_modifiers:
                return True
        
        # Check for inline access control (require statements)
        body = function.get('body', {})
        return self._contains_access_control_statements(body)
    
    def _create_access_control_finding(
        self,
        function: Dict[str, Any],
        source_code: str,
        file_path: str,
        modifies_state: bool,
        has_privileged_ops: bool
    ) -> Optional[Finding]:
        """
        Create a finding for a missing access control.
        
        Args:
            function: Function AST node.
            source_code: Original source code.
            file_path: Path to source file.
            modifies_state: Whether the function modifies state.
            has_privileged_ops: Whether the function has privileged operations.
            
        Returns:
            A Finding object or None if invalid.
        """
        function_name = function.get('name', 'unknown_function')
        visibility = function.get('visibility', 'internal') # Should be public/external here due to prior checks
        location = self.get_node_location(function, source_code, file_path)
        
        title = f"Missing Access Control in Function '{function_name}'"
        
        reasons = []
        if modifies_state:
            reasons.append("modifies contract state")
        if has_privileged_ops:
            reasons.append("performs sensitive operations")
        if not reasons and self._is_sensitive_function(function_name):
            reasons.append("is a function with a potentially sensitive name (e.g., init, set, transfer)")
        if not reasons: # Fallback if no specific reason determined by prior flags
            reasons.append("is a public/external function that may require access control")

        description = (
            f"The {visibility} function '{function_name}' lacks explicit access control modifiers. "
            f"This function {', and '.join(reasons)}. "
            f"Without proper access control, unauthorized users might be able to execute this function, potentially leading to vulnerabilities."
        )
        
        recommendation = (
            "Review the function\'s purpose and sensitivity. "
            "If it performs critical operations or modifies state, ensure appropriate access control mechanisms are implemented, such as: "
            "1. Using modifiers (e.g., `onlyOwner`, custom role-based modifiers). "
            "2. Implementing `require` checks at the beginning of the function to validate `msg.sender`."
        )
        
        code_snippet = self.extract_code_snippet(
            source_code, location.line_start, location.line_end
        )

        # Determine if the function name itself suggests sensitivity
        is_sensitive_by_name = self._is_sensitive_function(function_name)

        finding_metadata = {
            "function_name": function_name,
            "function_visibility": visibility,
            "modifies_state": modifies_state,
            "has_privileged_operations": has_privileged_ops,
            "is_potentially_sensitive_by_name": is_sensitive_by_name,
            "details": f"Function is {visibility} and {', and '.join(reasons)}."
        }
        
        return self.create_finding(
            title=title,
            description=description,
            location=location,
            vulnerability_type="missing_access_control",
            severity=self.default_severity,
            code_snippet=code_snippet,
            recommendation=recommendation,
            references=[
                "https://swcregistry.io/docs/SWC-100", # General access control
                "https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/access-control/"
            ],
            metadata=finding_metadata
        )
