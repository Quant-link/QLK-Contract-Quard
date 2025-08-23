"""
Graph representations for the unified IR system.

This module provides Control Flow Graph (CFG), Data Flow Graph (DFG), and Call Graph
implementations for comprehensive program analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from enum import Enum
import uuid

from .nodes import IRNode, IRFunction, IRStatement, IRExpression, IRVariable


class EdgeType(Enum):
    """Types of edges in graphs."""
    CONTROL_FLOW = "control_flow"
    DATA_FLOW = "data_flow"
    CALL = "call"
    CONDITIONAL_TRUE = "conditional_true"
    CONDITIONAL_FALSE = "conditional_false"
    LOOP_BACK = "loop_back"
    EXCEPTION = "exception"


@dataclass
class GraphEdge:
    """Represents an edge in a graph."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphNode:
    """Base class for graph nodes."""
    node_id: str
    ir_node: Optional[IRNode] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.node_id:
            self.node_id = str(uuid.uuid4())


@dataclass
class CFGNode(GraphNode):
    """Control Flow Graph node."""
    statements: List[IRStatement] = field(default_factory=list)
    is_entry: bool = False
    is_exit: bool = False
    is_branch: bool = False
    is_merge: bool = False
    
    def add_statement(self, stmt: IRStatement):
        """Add a statement to this CFG node."""
        self.statements.append(stmt)
    
    def is_basic_block(self) -> bool:
        """Check if this node represents a basic block."""
        return len(self.statements) > 0 and not self.is_branch


@dataclass
class DFGNode(GraphNode):
    """Data Flow Graph node."""
    variable: Optional[IRVariable] = None
    definition_point: Optional[IRStatement] = None
    use_points: List[IRStatement] = field(default_factory=list)
    is_definition: bool = False
    is_use: bool = False

    def add_use(self, stmt: IRStatement):
        """Add a use point for this variable."""
        self.use_points.append(stmt)
        self.is_use = True


@dataclass
class CallGraphNode(GraphNode):
    """Call Graph node."""
    function: Optional[IRFunction] = None
    call_sites: List[IRExpression] = field(default_factory=list)
    is_external: bool = False
    is_recursive: bool = False

    def add_call_site(self, call_expr: IRExpression):
        """Add a call site for this function."""
        self.call_sites.append(call_expr)


class ControlFlowGraph:
    """Control Flow Graph for analyzing execution paths."""
    
    def __init__(self, function: IRFunction):
        self.function = function
        self.nodes: Dict[str, CFGNode] = {}
        self.edges: List[GraphEdge] = []
        self.entry_node: Optional[CFGNode] = None
        self.exit_nodes: List[CFGNode] = []
        self._build_cfg()
    
    def _build_cfg(self):
        """Build the control flow graph from the function's statements."""
        if not self.function.body:
            return
        
        # Create entry node
        self.entry_node = CFGNode(
            node_id=f"{self.function.name}_entry",
            is_entry=True
        )
        self.nodes[self.entry_node.node_id] = self.entry_node
        
        # Process statements and build basic blocks
        current_node = self.entry_node
        
        for stmt in self.function.body:
            current_node = self._process_statement(stmt, current_node)
        
        # Mark exit nodes
        if current_node and not current_node.is_exit:
            current_node.is_exit = True
            self.exit_nodes.append(current_node)
    
    def _process_statement(self, stmt: IRStatement, current_node: CFGNode) -> CFGNode:
        """Process a statement and update the CFG."""
        from .nodes import StatementType, IRIfStatement, IRWhileLoop, IRReturn
        
        if stmt.statement_type == StatementType.IF:
            return self._process_if_statement(stmt, current_node)
        elif stmt.statement_type == StatementType.WHILE:
            return self._process_while_statement(stmt, current_node)
        elif stmt.statement_type == StatementType.RETURN:
            current_node.add_statement(stmt)
            current_node.is_exit = True
            self.exit_nodes.append(current_node)
            return current_node
        else:
            # Regular statement - add to current basic block
            current_node.add_statement(stmt)
            return current_node
    
    def _process_if_statement(self, if_stmt, current_node: CFGNode) -> CFGNode:
        """Process an if statement and create branching structure."""
        # Add condition evaluation to current node
        current_node.add_statement(if_stmt)
        current_node.is_branch = True
        
        # Create then branch
        then_node = CFGNode(node_id=f"{current_node.node_id}_then")
        self.nodes[then_node.node_id] = then_node
        
        # Create else branch (if exists)
        else_node = None
        if if_stmt.else_block:
            else_node = CFGNode(node_id=f"{current_node.node_id}_else")
            self.nodes[else_node.node_id] = else_node
        
        # Create merge node
        merge_node = CFGNode(
            node_id=f"{current_node.node_id}_merge",
            is_merge=True
        )
        self.nodes[merge_node.node_id] = merge_node
        
        # Add edges
        self.edges.append(GraphEdge(
            current_node.node_id, then_node.node_id,
            EdgeType.CONDITIONAL_TRUE
        ))
        
        if else_node:
            self.edges.append(GraphEdge(
                current_node.node_id, else_node.node_id,
                EdgeType.CONDITIONAL_FALSE
            ))
        else:
            self.edges.append(GraphEdge(
                current_node.node_id, merge_node.node_id,
                EdgeType.CONDITIONAL_FALSE
            ))
        
        # Process then block
        last_then_node = then_node
        for stmt in if_stmt.then_block:
            last_then_node = self._process_statement(stmt, last_then_node)
        
        # Process else block
        if else_node and if_stmt.else_block:
            last_else_node = else_node
            for stmt in if_stmt.else_block:
                last_else_node = self._process_statement(stmt, last_else_node)
            
            # Connect else to merge
            self.edges.append(GraphEdge(
                last_else_node.node_id, merge_node.node_id,
                EdgeType.CONTROL_FLOW
            ))
        
        # Connect then to merge
        self.edges.append(GraphEdge(
            last_then_node.node_id, merge_node.node_id,
            EdgeType.CONTROL_FLOW
        ))
        
        return merge_node
    
    def _process_while_statement(self, while_stmt, current_node: CFGNode) -> CFGNode:
        """Process a while loop and create loop structure."""
        # Create loop header node
        loop_header = CFGNode(
            node_id=f"{current_node.node_id}_loop_header",
            is_branch=True
        )
        loop_header.add_statement(while_stmt)
        self.nodes[loop_header.node_id] = loop_header
        
        # Create loop body node
        loop_body = CFGNode(node_id=f"{current_node.node_id}_loop_body")
        self.nodes[loop_body.node_id] = loop_body
        
        # Create loop exit node
        loop_exit = CFGNode(node_id=f"{current_node.node_id}_loop_exit")
        self.nodes[loop_exit.node_id] = loop_exit
        
        # Add edges
        self.edges.append(GraphEdge(
            current_node.node_id, loop_header.node_id,
            EdgeType.CONTROL_FLOW
        ))
        
        self.edges.append(GraphEdge(
            loop_header.node_id, loop_body.node_id,
            EdgeType.CONDITIONAL_TRUE
        ))
        
        self.edges.append(GraphEdge(
            loop_header.node_id, loop_exit.node_id,
            EdgeType.CONDITIONAL_FALSE
        ))
        
        # Process loop body
        last_body_node = loop_body
        for stmt in while_stmt.body:
            last_body_node = self._process_statement(stmt, last_body_node)
        
        # Add loop back edge
        self.edges.append(GraphEdge(
            last_body_node.node_id, loop_header.node_id,
            EdgeType.LOOP_BACK
        ))
        
        return loop_exit
    
    def get_predecessors(self, node_id: str) -> List[str]:
        """Get predecessor nodes for a given node."""
        return [edge.source_id for edge in self.edges if edge.target_id == node_id]
    
    def get_successors(self, node_id: str) -> List[str]:
        """Get successor nodes for a given node."""
        return [edge.target_id for edge in self.edges if edge.source_id == node_id]
    
    def get_reachable_nodes(self, start_node_id: str) -> Set[str]:
        """Get all nodes reachable from a starting node."""
        visited = set()
        stack = [start_node_id]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            
            visited.add(current)
            successors = self.get_successors(current)
            stack.extend(successors)
        
        return visited
    
    def has_unreachable_code(self) -> List[str]:
        """Detect unreachable code in the CFG."""
        if not self.entry_node:
            return []
        
        reachable = self.get_reachable_nodes(self.entry_node.node_id)
        all_nodes = set(self.nodes.keys())
        unreachable = all_nodes - reachable
        
        return list(unreachable)


class DataFlowGraph:
    """Data Flow Graph for analyzing variable definitions and uses."""
    
    def __init__(self, function: IRFunction):
        self.function = function
        self.nodes: Dict[str, DFGNode] = {}
        self.edges: List[GraphEdge] = []
        self.variable_nodes: Dict[str, List[DFGNode]] = {}
        self._build_dfg()
    
    def _build_dfg(self):
        """Build the data flow graph from the function."""
        # Collect all variable references
        self._collect_variable_references()
        
        # Build def-use chains
        self._build_def_use_chains()
    
    def _collect_variable_references(self):
        """Collect all variable definitions and uses."""
        # This would be implemented with a visitor pattern
        # to traverse the IR and identify variable references
        pass
    
    def _build_def_use_chains(self):
        """Build definition-use chains for variables."""
        # Connect variable definitions to their uses
        pass
    
    def get_definitions(self, variable_name: str) -> List[DFGNode]:
        """Get all definition points for a variable."""
        nodes = self.variable_nodes.get(variable_name, [])
        return [node for node in nodes if node.is_definition]
    
    def get_uses(self, variable_name: str) -> List[DFGNode]:
        """Get all use points for a variable."""
        nodes = self.variable_nodes.get(variable_name, [])
        return [node for node in nodes if node.is_use]


class CallGraph:
    """Call Graph for analyzing function call relationships."""
    
    def __init__(self, functions: List[IRFunction]):
        self.functions = functions
        self.nodes: Dict[str, CallGraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._build_call_graph()
    
    def _build_call_graph(self):
        """Build the call graph from the functions."""
        # Create nodes for all functions
        for func in self.functions:
            node = CallGraphNode(
                node_id=func.name,
                function=func
            )
            self.nodes[func.name] = node
        
        # Find function calls and create edges
        for func in self.functions:
            self._analyze_function_calls(func)
    
    def _analyze_function_calls(self, function: IRFunction):
        """Analyze function calls within a function."""
        # This would use a visitor to find all function call expressions
        # and create appropriate edges in the call graph
        pass
    
    def get_callers(self, function_name: str) -> List[str]:
        """Get all functions that call the given function."""
        return [edge.source_id for edge in self.edges 
                if edge.target_id == function_name and edge.edge_type == EdgeType.CALL]
    
    def get_callees(self, function_name: str) -> List[str]:
        """Get all functions called by the given function."""
        return [edge.target_id for edge in self.edges 
                if edge.source_id == function_name and edge.edge_type == EdgeType.CALL]
    
    def detect_recursive_calls(self) -> List[str]:
        """Detect recursive function calls."""
        recursive_functions = []
        
        for func_name in self.nodes:
            if self._has_recursive_path(func_name, func_name, set()):
                recursive_functions.append(func_name)
                self.nodes[func_name].is_recursive = True
        
        return recursive_functions
    
    def _has_recursive_path(self, start: str, target: str, visited: Set[str]) -> bool:
        """Check if there's a recursive path from start to target."""
        if start in visited:
            return start == target
        
        visited.add(start)
        callees = self.get_callees(start)
        
        for callee in callees:
            if self._has_recursive_path(callee, target, visited.copy()):
                return True
        
        return False
