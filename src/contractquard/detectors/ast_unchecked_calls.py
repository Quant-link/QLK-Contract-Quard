"""
AST-based unchecked external calls detector for ContractQuard.

This detector analyzes the Abstract Syntax Tree to identify external calls
whose return values are not properly checked.
"""

from typing import List, Dict, Any, Set, Optional
import logging

from ..core.findings import Severity, Finding
from ..parsers.solidity_parser import ParsedContract
from .base import ASTDetector


class UncheckedCallsDetector(ASTDetector):
    """
    AST-based detector for unchecked external calls.
    
    This detector identifies external calls (call, delegatecall, send, etc.)
    whose return values are not checked, which can lead to silent failures.
    """
    
    @property
    def name(self) -> str:
        return "ast_unchecked_calls_detector"
    
    @property
    def description(self) -> str:
        return "Detects unchecked external calls that may fail silently"
    
    @property
    def vulnerability_types(self) -> List[str]:
        return ["unchecked_call", "silent_failure", "external_call_failure"]
    
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
        Analyze contract AST for unchecked external calls.
        
        Args:
            ast: Contract AST.
            contract: Parsed contract data.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            List of unchecked call findings.
        """
        findings = []
        
        # Get all function definitions
        functions = self._extract_functions(ast)
        
        for function in functions:
            function_findings = self._analyze_function_for_unchecked_calls(
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
    
    def _analyze_function_for_unchecked_calls(
        self,
        function: Dict[str, Any],
        source_code: str,
        file_path: str
    ) -> List[Finding]:
        """
        Analyze a function for unchecked external calls.
        
        Args:
            function: Function AST node.
            source_code: Original source code.
            file_path: Path to source file.
            
        Returns:
            List of findings for unchecked calls.
        """
        findings = []
        
        # Get function body
        body = function.get('body', {})
        if not body or body.get('nodeType') != 'Block':
            return findings
        
        # Find all external calls in the function
        external_calls = self._find_external_calls(body)
        
        for call in external_calls:
            if self._is_call_unchecked(call, body):
                finding = self._create_unchecked_call_finding(
                    call, function, source_code, file_path
                )
                if finding:
                    findings.append(finding)
        
        return findings
    
    def _find_external_calls(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find all external calls in an AST node."""
        external_calls = []
        
        def traverse(n):
            if isinstance(n, dict):
                node_type = n.get('nodeType')
                
                if node_type == 'FunctionCall':
                    expression = n.get('expression', {})
                    
                    # Check for member access calls
                    if expression.get('nodeType') == 'MemberAccess':
                        member_name = expression.get('memberName', '')
                        
                        # Low-level calls that return success boolean
                        if member_name in ['call', 'delegatecall', 'staticcall']:
                            external_calls.append(n)
                        
                        # send() also returns boolean but is often unchecked
                        elif member_name == 'send':
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
    
    def _is_call_unchecked(self, call: Dict[str, Any], function_body: Dict[str, Any]) -> bool:
        """
        Check if an external call's return value is unchecked.
        
        Args:
            call: The external call AST node.
            function_body: The function body containing the call.
            
        Returns:
            True if the call is unchecked, False otherwise.
        """
        # Find the statement containing this call
        call_statement = self._find_containing_statement(call, function_body)
        
        if not call_statement:
            return True  # If we can't find the statement, assume unchecked
        
        statement_type = call_statement.get('nodeType')
        
        # Check different statement types
        if statement_type == 'ExpressionStatement':
            # Call is used as a standalone statement - likely unchecked
            return True
        
        elif statement_type == 'VariableDeclarationStatement':
            # Call result is assigned to a variable
            # Check if the variable is subsequently used in a condition
            declarations = call_statement.get('declarations', [])
            if declarations:
                var_name = declarations[0].get('name')
                return not self._is_variable_checked(var_name, function_body, call_statement)
        
        elif statement_type == 'Assignment':
            # Call result is assigned to a variable
            left = call_statement.get('left', {})
            if left.get('nodeType') == 'Identifier':
                var_name = left.get('name')
                return not self._is_variable_checked(var_name, function_body, call_statement)
        
        elif statement_type == 'IfStatement':
            # Call is used directly in an if condition - checked
            return False
        
        elif statement_type == 'RequireStatement':
            # Call is used in a require statement - checked
            return False
        
        # For other cases, assume unchecked
        return True
    
    def _find_containing_statement(self, call: Dict[str, Any], function_body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the statement that contains the given call."""
        statements = function_body.get('statements', [])
        
        for statement in statements:
            if self._contains_node(statement, call):
                return statement
        
        return None
    
    def _contains_node(self, container: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check if a container node contains the target node."""
        if container is target:
            return True
        
        if not isinstance(container, dict):
            return False
        
        for key, value in container.items():
            if isinstance(value, list):
                for item in value:
                    if self._contains_node(item, target):
                        return True
            elif isinstance(value, dict):
                if self._contains_node(value, target):
                    return True
        
        return False
    
    def _is_variable_checked(self, var_name: str, function_body: Dict[str, Any], after_statement: Dict[str, Any]) -> bool:
        """
        Check if a variable is used in a conditional check after a given statement.
        
        Args:
            var_name: Name of the variable to check.
            function_body: Function body to search in.
            after_statement: Statement after which to look for checks.
            
        Returns:
            True if the variable is checked, False otherwise.
        """
        statements = function_body.get('statements', [])
        
        # Find the index of the after_statement
        after_index = -1
        for i, stmt in enumerate(statements):
            if stmt is after_statement:
                after_index = i
                break
        
        if after_index == -1:
            return False
        
        # Look for checks in subsequent statements
        for i in range(after_index + 1, len(statements)):
            statement = statements[i]
            if self._statement_checks_variable(statement, var_name):
                return True
        
        return False
    
    def _statement_checks_variable(self, statement: Dict[str, Any], var_name: str) -> bool:
        """Check if a statement contains a check of the given variable."""
        statement_type = statement.get('nodeType')
        
        # Check if statements
        if statement_type == 'IfStatement':
            condition = statement.get('condition', {})
            return self._expression_uses_variable(condition, var_name)
        
        # Require statements
        elif statement_type == 'ExpressionStatement':
            expression = statement.get('expression', {})
            if (expression.get('nodeType') == 'FunctionCall' and
                expression.get('expression', {}).get('name') == 'require'):
                arguments = expression.get('arguments', [])
                if arguments:
                    return self._expression_uses_variable(arguments[0], var_name)
        
        return False
    
    def _expression_uses_variable(self, expression: Dict[str, Any], var_name: str) -> bool:
        """Check if an expression uses the given variable."""
        if not isinstance(expression, dict):
            return False
        
        # Direct identifier reference
        if (expression.get('nodeType') == 'Identifier' and
            expression.get('name') == var_name):
            return True
        
        # Recursively check sub-expressions
        for key, value in expression.items():
            if isinstance(value, list):
                for item in value:
                    if self._expression_uses_variable(item, var_name):
                        return True
            elif isinstance(value, dict):
                if self._expression_uses_variable(value, var_name):
                    return True
        
        return False
    
    def _create_unchecked_call_finding(
        self,
        call: Dict[str, Any],
        function: Dict[str, Any],
        source_code: str,
        file_path: str
    ) -> Optional[Finding]:
        """Create a finding for an unchecked external call."""
        function_name = function.get('name', 'unknown')
        
        # Get call type
        expression = call.get('expression', {})
        call_type = 'unknown'
        if expression.get('nodeType') == 'MemberAccess':
            call_type = expression.get('memberName', 'unknown')
        
        location = self.get_node_location(call, source_code, file_path)
        code_snippet = self.extract_code_snippet(
            source_code, location.line_start, location.line_end
        )
        
        # Determine severity based on call type
        if call_type in ['call', 'delegatecall']:
            severity = Severity.HIGH
        elif call_type == 'send':
            severity = Severity.MEDIUM
        else:
            severity = Severity.MEDIUM
        
        title = f"Unchecked External Call in Function '{function_name}'"
        description = (
            f"Function '{function_name}' makes an external {call_type}() call "
            "but does not check its return value. External calls can fail for various reasons "
            "(out of gas, contract doesn't exist, etc.) and failing to check the return value "
            "can lead to unexpected behavior or silent failures."
        )
        
        if call_type == 'send':
            recommendation = (
                "Check the return value of send() calls:\n"
                "```solidity\n"
                "bool success = recipient.send(amount);\n"
                "require(success, \"Send failed\");\n"
                "```\n"
                "Or better yet, use call() with proper checks:\n"
                "```solidity\n"
                "(bool success, ) = recipient.call{value: amount}(\"\");\n"
                "require(success, \"Transfer failed\");\n"
                "```"
            )
        else:
            recommendation = (
                f"Check the return value of {call_type}() calls:\n"
                "```solidity\n"
                f"(bool success, bytes memory data) = target.{call_type}(callData);\n"
                "require(success, \"Call failed\");\n"
                "```"
            )
        
        references = [
            "https://consensys.github.io/smart-contract-best-practices/attacks/denial-of-service/",
            "https://swcregistry.io/docs/SWC-104"
        ]
        
        return self.create_finding(
            title=title,
            description=description,
            location=location,
            vulnerability_type="unchecked_call",
            severity=severity,
            confidence=0.9,
            code_snippet=code_snippet,
            recommendation=recommendation,
            references=references,
            metadata={
                "function_name": function_name,
                "call_type": call_type,
                "call_method": call_type
            }
        )
