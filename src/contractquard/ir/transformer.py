"""
Language-specific transformers for converting ASTs to unified IR.

This module provides transformer classes that convert language-specific ASTs
(Solidity, Rust, Go) into the unified intermediate representation.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import uuid

from .nodes import (
    IRModule, IRContract, IRFunction, IRVariable, IRStatement, IRExpression,
    IRType, IRParameter, Visibility, SourceLocation, StatementType, ExpressionType,
    IRAssignment, IRIfStatement, IRWhileLoop, IRReturn, IRLiteral, IRIdentifier,
    IRBinaryOperation, IRUnaryOperation, IRFunctionCall
)


class BaseTransformer(ABC):
    """Base class for language-specific transformers."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"contractquard.ir.transformer.{self.__class__.__name__}")
    
    @abstractmethod
    def transform(self, ast_data: Any, file_path: str) -> IRModule:
        """Transform language-specific AST to unified IR."""
        pass
    
    def _generate_node_id(self, prefix: str = "node") -> str:
        """Generate a unique node ID."""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def _create_source_location(self, file_path: str, line: int = 1, 
                               column: int = 0) -> SourceLocation:
        """Create a source location object."""
        return SourceLocation(
            file_path=file_path,
            line_start=line,
            line_end=line,
            column_start=column,
            column_end=column
        )


class SolidityToIRTransformer(BaseTransformer):
    """Transformer for Solidity AST to unified IR."""
    
    def transform(self, parsed_data, file_path: str) -> IRModule:
        """
        Transform Solidity parsed data to IR.
        
        Args:
            parsed_data: ParsedData from SolidityParser
            file_path: Path to the source file
            
        Returns:
            IRModule representing the Solidity contracts
        """
        self.logger.debug(f"Transforming Solidity file: {file_path}")
        
        contracts = []
        
        for parsed_contract in parsed_data.contracts:
            ir_contract = self._transform_contract(parsed_contract, file_path)
            contracts.append(ir_contract)
        
        module = IRModule(
            node_id=self._generate_node_id("solidity_module"),
            name=file_path,
            contracts=contracts,
            functions=[],  # Solidity doesn't have module-level functions
            variables=[],  # Solidity doesn't have module-level variables
            source_location=self._create_source_location(file_path)
        )
        
        self.logger.info(f"Transformed {len(contracts)} Solidity contracts")
        return module
    
    def _transform_contract(self, parsed_contract, file_path: str) -> IRContract:
        """Transform a parsed Solidity contract to IR."""
        functions = []
        variables = []
        
        # Extract contract information from AST
        if parsed_contract.ast and 'nodes' in parsed_contract.ast:
            for node in parsed_contract.ast['nodes']:
                if node.get('nodeType') == 'FunctionDefinition':
                    ir_function = self._transform_function(node, file_path)
                    functions.append(ir_function)
                elif node.get('nodeType') == 'VariableDeclaration':
                    ir_variable = self._transform_variable(node, file_path)
                    variables.append(ir_variable)
        
        return IRContract(
            node_id=self._generate_node_id("solidity_contract"),
            name=parsed_contract.name,
            functions=functions,
            variables=variables,
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_function(self, ast_node: Dict[str, Any], file_path: str) -> IRFunction:
        """Transform a Solidity function AST node to IR."""
        name = ast_node.get('name', 'unknown')
        
        # Extract visibility
        visibility = Visibility.PRIVATE
        if ast_node.get('visibility') == 'public':
            visibility = Visibility.PUBLIC
        elif ast_node.get('visibility') == 'external':
            visibility = Visibility.EXTERNAL
        elif ast_node.get('visibility') == 'internal':
            visibility = Visibility.INTERNAL
        
        # Extract parameters
        parameters = []
        if 'parameters' in ast_node and 'parameters' in ast_node['parameters']:
            for param in ast_node['parameters']['parameters']:
                ir_param = self._transform_parameter(param)
                parameters.append(ir_param)
        
        # Extract return type
        return_type = None
        if 'returnParameters' in ast_node and 'parameters' in ast_node['returnParameters']:
            return_params = ast_node['returnParameters']['parameters']
            if return_params:
                return_type = self._transform_type(return_params[0]['typeDescriptions'])
        
        # Transform function body
        body = []
        if 'body' in ast_node and ast_node['body']:
            body = self._transform_statement_block(ast_node['body'], file_path)
        
        # Extract modifiers
        modifiers = []
        if 'modifiers' in ast_node:
            modifiers = [mod.get('modifierName', {}).get('name', '') 
                        for mod in ast_node['modifiers']]
        
        return IRFunction(
            node_id=self._generate_node_id("solidity_function"),
            name=name,
            parameters=parameters,
            return_type=return_type,
            visibility=visibility,
            body=body,
            is_constructor=ast_node.get('kind') == 'constructor',
            is_fallback=ast_node.get('kind') == 'fallback',
            is_payable='payable' in ast_node.get('stateMutability', ''),
            is_view=ast_node.get('stateMutability') == 'view',
            is_pure=ast_node.get('stateMutability') == 'pure',
            modifiers=modifiers,
            source_location=self._create_source_location(
                file_path, 
                ast_node.get('src', '0:0:0').split(':')[0]
            )
        )
    
    def _transform_parameter(self, param_node: Dict[str, Any]) -> IRParameter:
        """Transform a Solidity parameter to IR."""
        name = param_node.get('name', '')
        param_type = self._transform_type(param_node.get('typeDescriptions', {}))
        
        return IRParameter(
            name=name,
            param_type=param_type
        )
    
    def _transform_type(self, type_desc: Dict[str, Any]) -> IRType:
        """Transform Solidity type description to IR type."""
        type_string = type_desc.get('typeString', 'unknown')
        
        # Basic type mapping
        if type_string.startswith('uint'):
            return IRType(name=type_string, is_primitive=True)
        elif type_string.startswith('int'):
            return IRType(name=type_string, is_primitive=True)
        elif type_string == 'bool':
            return IRType(name='bool', is_primitive=True)
        elif type_string == 'address':
            return IRType(name='address', is_primitive=True)
        elif type_string == 'string':
            return IRType(name='string', is_primitive=True)
        elif type_string == 'bytes':
            return IRType(name='bytes', is_primitive=True)
        elif '[]' in type_string:
            # Array type
            element_type_str = type_string.replace('[]', '')
            element_type = IRType(name=element_type_str, is_primitive=True)
            return IRType(
                name=type_string,
                is_array=True,
                element_type=element_type
            )
        elif 'mapping' in type_string:
            # Mapping type - simplified parsing
            return IRType(
                name=type_string,
                is_mapping=True,
                key_type=IRType(name='unknown', is_primitive=True),
                value_type=IRType(name='unknown', is_primitive=True)
            )
        else:
            # Custom type
            return IRType(name=type_string, is_struct=True)
    
    def _transform_variable(self, var_node: Dict[str, Any], file_path: str) -> IRVariable:
        """Transform a Solidity variable declaration to IR."""
        name = var_node.get('name', 'unknown')
        var_type = self._transform_type(var_node.get('typeDescriptions', {}))
        
        # Extract visibility
        visibility = Visibility.PRIVATE
        if var_node.get('visibility') == 'public':
            visibility = Visibility.PUBLIC
        elif var_node.get('visibility') == 'internal':
            visibility = Visibility.INTERNAL
        
        return IRVariable(
            node_id=self._generate_node_id("solidity_variable"),
            name=name,
            var_type=var_type,
            visibility=visibility,
            is_constant=var_node.get('constant', False),
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_statement_block(self, block_node: Dict[str, Any], 
                                  file_path: str) -> List[IRStatement]:
        """Transform a Solidity statement block to IR."""
        statements = []
        
        if 'statements' in block_node:
            for stmt_node in block_node['statements']:
                ir_stmt = self._transform_statement(stmt_node, file_path)
                if ir_stmt:
                    statements.append(ir_stmt)
        
        return statements
    
    def _transform_statement(self, stmt_node: Dict[str, Any], 
                           file_path: str) -> Optional[IRStatement]:
        """Transform a Solidity statement to IR."""
        node_type = stmt_node.get('nodeType', '')
        
        if node_type == 'ExpressionStatement':
            # Handle expression statements (assignments, function calls)
            expr = stmt_node.get('expression')
            if expr and expr.get('nodeType') == 'Assignment':
                return self._transform_assignment(expr, file_path)
            elif expr and expr.get('nodeType') == 'FunctionCall':
                # Convert function call to statement
                call_expr = self._transform_function_call(expr, file_path)
                return IRStatement(
                    node_id=self._generate_node_id("solidity_stmt"),
                    statement_type=StatementType.FUNCTION_CALL,
                    source_location=self._create_source_location(file_path)
                )
        elif node_type == 'IfStatement':
            return self._transform_if_statement(stmt_node, file_path)
        elif node_type == 'WhileStatement':
            return self._transform_while_statement(stmt_node, file_path)
        elif node_type == 'Return':
            return self._transform_return_statement(stmt_node, file_path)
        
        # Default: create a generic statement
        return IRStatement(
            node_id=self._generate_node_id("solidity_stmt"),
            statement_type=StatementType.BLOCK,
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_assignment(self, assign_node: Dict[str, Any], 
                            file_path: str) -> IRAssignment:
        """Transform a Solidity assignment to IR."""
        target = self._transform_expression(assign_node.get('left', {}), file_path)
        value = self._transform_expression(assign_node.get('right', {}), file_path)
        
        return IRAssignment(
            node_id=self._generate_node_id("solidity_assignment"),
            target=target,
            value=value,
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_if_statement(self, if_node: Dict[str, Any], 
                              file_path: str) -> IRIfStatement:
        """Transform a Solidity if statement to IR."""
        condition = self._transform_expression(if_node.get('condition', {}), file_path)
        
        then_block = []
        if 'trueBody' in if_node:
            then_block = self._transform_statement_block(if_node['trueBody'], file_path)
        
        else_block = None
        if 'falseBody' in if_node:
            else_block = self._transform_statement_block(if_node['falseBody'], file_path)
        
        return IRIfStatement(
            node_id=self._generate_node_id("solidity_if"),
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_while_statement(self, while_node: Dict[str, Any], 
                                 file_path: str) -> IRWhileLoop:
        """Transform a Solidity while statement to IR."""
        condition = self._transform_expression(while_node.get('condition', {}), file_path)
        body = self._transform_statement_block(while_node.get('body', {}), file_path)
        
        return IRWhileLoop(
            node_id=self._generate_node_id("solidity_while"),
            condition=condition,
            body=body,
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_return_statement(self, return_node: Dict[str, Any], 
                                  file_path: str) -> IRReturn:
        """Transform a Solidity return statement to IR."""
        value = None
        if 'expression' in return_node:
            value = self._transform_expression(return_node['expression'], file_path)
        
        return IRReturn(
            node_id=self._generate_node_id("solidity_return"),
            value=value,
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_expression(self, expr_node: Dict[str, Any], 
                            file_path: str) -> IRExpression:
        """Transform a Solidity expression to IR."""
        node_type = expr_node.get('nodeType', '')
        
        if node_type == 'Literal':
            return IRLiteral(
                node_id=self._generate_node_id("solidity_literal"),
                value=expr_node.get('value'),
                literal_type=self._transform_type(expr_node.get('typeDescriptions', {})),
                source_location=self._create_source_location(file_path)
            )
        elif node_type == 'Identifier':
            return IRIdentifier(
                node_id=self._generate_node_id("solidity_identifier"),
                name=expr_node.get('name', ''),
                source_location=self._create_source_location(file_path)
            )
        elif node_type == 'BinaryOperation':
            return IRBinaryOperation(
                node_id=self._generate_node_id("solidity_binary_op"),
                operator=expr_node.get('operator', ''),
                left=self._transform_expression(expr_node.get('left', {}), file_path),
                right=self._transform_expression(expr_node.get('right', {}), file_path),
                source_location=self._create_source_location(file_path)
            )
        elif node_type == 'FunctionCall':
            return self._transform_function_call(expr_node, file_path)
        
        # Default: create a generic identifier
        return IRIdentifier(
            node_id=self._generate_node_id("solidity_expr"),
            name='unknown',
            source_location=self._create_source_location(file_path)
        )
    
    def _transform_function_call(self, call_node: Dict[str, Any], 
                               file_path: str) -> IRFunctionCall:
        """Transform a Solidity function call to IR."""
        function_name = 'unknown'
        
        # Extract function name
        if 'expression' in call_node:
            expr = call_node['expression']
            if expr.get('nodeType') == 'Identifier':
                function_name = expr.get('name', 'unknown')
            elif expr.get('nodeType') == 'MemberAccess':
                function_name = expr.get('memberName', 'unknown')
        
        # Transform arguments
        arguments = []
        if 'arguments' in call_node:
            for arg in call_node['arguments']:
                ir_arg = self._transform_expression(arg, file_path)
                arguments.append(ir_arg)
        
        return IRFunctionCall(
            node_id=self._generate_node_id("solidity_call"),
            function_name=function_name,
            arguments=arguments,
            source_location=self._create_source_location(file_path)
        )


class RustToIRTransformer(BaseTransformer):
    """Transformer for Rust AST to unified IR."""
    
    def transform(self, ast_data: Dict[str, Any], file_path: str) -> IRModule:
        """Transform Rust AST data to IR."""
        self.logger.debug(f"Transforming Rust file: {file_path}")
        
        # Placeholder implementation - would use syn crate output
        module = IRModule(
            node_id=self._generate_node_id("rust_module"),
            name=file_path,
            contracts=[],  # Rust contracts would be extracted from impl blocks
            functions=[],  # Module-level functions
            variables=[],  # Module-level variables
            source_location=self._create_source_location(file_path)
        )
        
        self.logger.info("Transformed Rust module (placeholder implementation)")
        return module


class GoToIRTransformer(BaseTransformer):
    """Transformer for Go AST to unified IR."""
    
    def transform(self, ast_data: Dict[str, Any], file_path: str) -> IRModule:
        """Transform Go AST data to IR."""
        self.logger.debug(f"Transforming Go file: {file_path}")
        
        # Placeholder implementation - would use go/ast output
        module = IRModule(
            node_id=self._generate_node_id("go_module"),
            name=file_path,
            contracts=[],  # Go contracts would be extracted from struct/interface patterns
            functions=[],  # Package-level functions
            variables=[],  # Package-level variables
            source_location=self._create_source_location(file_path)
        )
        
        self.logger.info("Transformed Go module (placeholder implementation)")
        return module
