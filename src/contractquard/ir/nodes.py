"""
Core IR node definitions for the unified intermediate representation.

This module defines the fundamental building blocks of the language-agnostic IR
that can represent contracts from Rust, Solidity, and Go.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set
from enum import Enum


class IRNodeType(Enum):
    """Types of IR nodes."""
    CONTRACT = "contract"
    MODULE = "module"
    FUNCTION = "function"
    VARIABLE = "variable"
    STATEMENT = "statement"
    EXPRESSION = "expression"
    TYPE = "type"
    PARAMETER = "parameter"


class Visibility(Enum):
    """Visibility levels for functions and variables."""
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"
    EXTERNAL = "external"
    PROTECTED = "protected"


class StatementType(Enum):
    """Types of statements in the IR."""
    ASSIGNMENT = "assignment"
    IF = "if"
    WHILE = "while"
    FOR = "for"
    RETURN = "return"
    FUNCTION_CALL = "function_call"
    VARIABLE_DECLARATION = "variable_declaration"
    BLOCK = "block"
    BREAK = "break"
    CONTINUE = "continue"
    THROW = "throw"
    TRY_CATCH = "try_catch"


class ExpressionType(Enum):
    """Types of expressions in the IR."""
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    FUNCTION_CALL = "function_call"
    MEMBER_ACCESS = "member_access"
    ARRAY_ACCESS = "array_access"
    CONDITIONAL = "conditional"
    CAST = "cast"


@dataclass
class SourceLocation:
    """Source code location information."""
    file_path: str
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0


@dataclass
class IRNode(ABC):
    """Base class for all IR nodes."""
    node_type: IRNodeType
    node_id: str
    source_location: Optional[SourceLocation] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization hook for subclasses."""
        pass

    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        pass

    def get_children(self) -> List['IRNode']:
        """Get all child nodes."""
        return []


@dataclass
class IRType:
    """Represents a type in the IR."""
    name: str
    is_primitive: bool = False
    is_array: bool = False
    array_size: Optional[int] = None
    element_type: Optional['IRType'] = None
    is_mapping: bool = False
    key_type: Optional['IRType'] = None
    value_type: Optional['IRType'] = None
    is_struct: bool = False
    struct_fields: Dict[str, 'IRType'] = field(default_factory=dict)
    is_nullable: bool = False
    
    def __str__(self) -> str:
        if self.is_array:
            size_str = f"[{self.array_size}]" if self.array_size else "[]"
            return f"{self.element_type}{size_str}"
        elif self.is_mapping:
            return f"mapping({self.key_type} => {self.value_type})"
        elif self.is_struct:
            fields = ", ".join(f"{k}: {v}" for k, v in self.struct_fields.items())
            return f"struct {self.name} {{ {fields} }}"
        else:
            return self.name


@dataclass
class IRParameter:
    """Represents a function parameter."""
    name: str
    param_type: IRType
    is_mutable: bool = False
    default_value: Optional['IRExpression'] = None
    annotations: List[str] = field(default_factory=list)


@dataclass
class IRVariable(IRNode):
    """Represents a variable declaration."""
    name: str = ""
    var_type: IRType = field(default_factory=lambda: IRType(name="unknown"))
    visibility: Visibility = Visibility.PRIVATE
    is_mutable: bool = True
    is_constant: bool = False
    is_static: bool = False
    initial_value: Optional['IRExpression'] = None

    def __post_init__(self):
        super().__post_init__()
        self.node_type = IRNodeType.VARIABLE

    def accept(self, visitor):
        return visitor.visit_variable(self)


@dataclass
class IRExpression(IRNode):
    """Base class for expressions."""
    expression_type: ExpressionType = ExpressionType.IDENTIFIER
    result_type: Optional[IRType] = None

    def __post_init__(self):
        super().__post_init__()
        self.node_type = IRNodeType.EXPRESSION

    def accept(self, visitor):
        return visitor.visit_expression(self)


@dataclass
class IRLiteral(IRExpression):
    """Represents a literal value."""
    value: Any = None
    literal_type: IRType = field(default_factory=lambda: IRType(name="unknown"))

    def __post_init__(self):
        super().__post_init__()
        self.expression_type = ExpressionType.LITERAL
        self.result_type = self.literal_type


@dataclass
class IRIdentifier(IRExpression):
    """Represents an identifier (variable reference)."""
    name: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.expression_type = ExpressionType.IDENTIFIER


@dataclass
class IRBinaryOperation(IRExpression):
    """Represents a binary operation."""
    operator: str = ""
    left: Optional[IRExpression] = None
    right: Optional[IRExpression] = None

    def __post_init__(self):
        super().__post_init__()
        self.expression_type = ExpressionType.BINARY_OP

    def get_children(self) -> List[IRNode]:
        children = []
        if self.left:
            children.append(self.left)
        if self.right:
            children.append(self.right)
        return children


@dataclass
class IRUnaryOperation(IRExpression):
    """Represents a unary operation."""
    operator: str = ""
    operand: Optional[IRExpression] = None

    def __post_init__(self):
        super().__post_init__()
        self.expression_type = ExpressionType.UNARY_OP

    def get_children(self) -> List[IRNode]:
        return [self.operand] if self.operand else []


@dataclass
class IRFunctionCall(IRExpression):
    """Represents a function call."""
    function_name: str = ""
    arguments: List[IRExpression] = field(default_factory=list)
    is_external: bool = False
    target_contract: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.expression_type = ExpressionType.FUNCTION_CALL

    def get_children(self) -> List[IRNode]:
        return self.arguments


@dataclass
class IRStatement(IRNode):
    """Base class for statements."""
    statement_type: StatementType = StatementType.BLOCK

    def __post_init__(self):
        super().__post_init__()
        self.node_type = IRNodeType.STATEMENT

    def accept(self, visitor):
        return visitor.visit_statement(self)


@dataclass
class IRAssignment(IRStatement):
    """Represents an assignment statement."""
    target: Optional[IRExpression] = None
    value: Optional[IRExpression] = None

    def __post_init__(self):
        super().__post_init__()
        self.statement_type = StatementType.ASSIGNMENT

    def get_children(self) -> List[IRNode]:
        children = []
        if self.target:
            children.append(self.target)
        if self.value:
            children.append(self.value)
        return children


@dataclass
class IRIfStatement(IRStatement):
    """Represents an if statement."""
    condition: Optional[IRExpression] = None
    then_block: List[IRStatement] = field(default_factory=list)
    else_block: Optional[List[IRStatement]] = None

    def __post_init__(self):
        super().__post_init__()
        self.statement_type = StatementType.IF

    def get_children(self) -> List[IRNode]:
        children = []
        if self.condition:
            children.append(self.condition)
        children.extend(self.then_block)
        if self.else_block:
            children.extend(self.else_block)
        return children


@dataclass
class IRWhileLoop(IRStatement):
    """Represents a while loop."""
    condition: Optional[IRExpression] = None
    body: List[IRStatement] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.statement_type = StatementType.WHILE

    def get_children(self) -> List[IRNode]:
        children = []
        if self.condition:
            children.append(self.condition)
        children.extend(self.body)
        return children


@dataclass
class IRReturn(IRStatement):
    """Represents a return statement."""
    value: Optional[IRExpression] = None

    def __post_init__(self):
        super().__post_init__()
        self.statement_type = StatementType.RETURN

    def get_children(self) -> List[IRNode]:
        return [self.value] if self.value else []


@dataclass
class IRFunction(IRNode):
    """Represents a function definition."""
    name: str = ""
    parameters: List[IRParameter] = field(default_factory=list)
    return_type: Optional[IRType] = None
    visibility: Visibility = Visibility.PRIVATE
    body: List[IRStatement] = field(default_factory=list)
    is_constructor: bool = False
    is_fallback: bool = False
    is_payable: bool = False
    is_view: bool = False
    is_pure: bool = False
    modifiers: List[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.node_type = IRNodeType.FUNCTION

    def accept(self, visitor):
        return visitor.visit_function(self)

    def get_children(self) -> List[IRNode]:
        return self.body


@dataclass
class IRContract(IRNode):
    """Represents a contract (Solidity) or similar top-level construct."""
    name: str = ""
    functions: List[IRFunction] = field(default_factory=list)
    variables: List[IRVariable] = field(default_factory=list)
    inheritance: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.node_type = IRNodeType.CONTRACT

    def accept(self, visitor):
        return visitor.visit_contract(self)

    def get_children(self) -> List[IRNode]:
        return self.functions + self.variables


@dataclass
class IRModule(IRNode):
    """Represents a module (Rust/Go) or compilation unit."""
    name: str = ""
    contracts: List[IRContract] = field(default_factory=list)
    functions: List[IRFunction] = field(default_factory=list)
    variables: List[IRVariable] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.node_type = IRNodeType.MODULE

    def accept(self, visitor):
        return visitor.visit_module(self)

    def get_children(self) -> List[IRNode]:
        return self.contracts + self.functions + self.variables


# Visitor interface for IR traversal
class IRVisitor(ABC):
    """Abstract base class for IR visitors."""

    @abstractmethod
    def visit_module(self, node: IRModule):
        pass

    @abstractmethod
    def visit_contract(self, node: IRContract):
        pass

    @abstractmethod
    def visit_function(self, node: IRFunction):
        pass

    @abstractmethod
    def visit_variable(self, node: IRVariable):
        pass

    @abstractmethod
    def visit_statement(self, node: IRStatement):
        pass

    @abstractmethod
    def visit_expression(self, node: IRExpression):
        pass
