"""
Control Flow Analysis for ContractQuard.

This module provides control flow analysis capabilities including
unreachable code detection, infinite loop detection, and control flow
graph construction and analysis.
"""

import logging
from typing import List, Dict, Set, Any, Optional, Tuple
from dataclasses import dataclass

from ..core.findings import Finding, Severity, SourceLocation
from ..ir.nodes import IRModule, IRFunction, IRContract, IRStatement, StatementType
from ..ir.graphs import ControlFlowGraph, CFGNode


@dataclass
class ControlFlowIssue:
    """Represents a control flow issue."""
    issue_type: str
    function_name: str
    description: str
    severity: Severity
    location: Optional[SourceLocation] = None
    affected_nodes: List[str] = None


class ControlFlowAnalyzer:
    """
    Control Flow Analyzer for detecting control flow related issues.
    
    This analyzer constructs control flow graphs and detects various
    control flow anomalies and potential security issues.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("contractquard.analysis.control_flow")
        self.cfgs: Dict[str, ControlFlowGraph] = {}
        self.issues: List[ControlFlowIssue] = []
    
    def analyze_module(self, module: IRModule) -> List[Finding]:
        """
        Analyze control flow for all functions in a module.
        
        Args:
            module: IR module to analyze
            
        Returns:
            List of control flow findings
        """
        self.logger.debug(f"Starting control flow analysis for module: {module.name}")
        
        findings = []
        self.issues.clear()
        self.cfgs.clear()
        
        # Analyze module-level functions
        for function in module.functions:
            function_findings = self.analyze_function(function)
            findings.extend(function_findings)
        
        # Analyze contract functions
        for contract in module.contracts:
            for function in contract.functions:
                function_findings = self.analyze_function(function)
                findings.extend(function_findings)
        
        self.logger.info(f"Control flow analysis found {len(findings)} issues")
        return findings
    
    def analyze_function(self, function: IRFunction) -> List[Finding]:
        """
        Analyze control flow for a specific function.
        
        Args:
            function: IR function to analyze
            
        Returns:
            List of control flow findings for the function
        """
        findings = []
        
        if not function.body:
            return findings
        
        try:
            # Build control flow graph
            cfg = ControlFlowGraph(function)
            self.cfgs[function.name] = cfg
            
            # Detect unreachable code
            unreachable_findings = self._detect_unreachable_code(cfg, function)
            findings.extend(unreachable_findings)
            
            # Detect infinite loops
            infinite_loop_findings = self._detect_infinite_loops(cfg, function)
            findings.extend(infinite_loop_findings)
            
            # Detect missing return statements
            missing_return_findings = self._detect_missing_returns(cfg, function)
            findings.extend(missing_return_findings)
            
            # Detect complex control flow
            complexity_findings = self._detect_complex_control_flow(cfg, function)
            findings.extend(complexity_findings)
            
            # Detect dead code after returns
            dead_code_findings = self._detect_dead_code_after_returns(cfg, function)
            findings.extend(dead_code_findings)
            
        except Exception as e:
            self.logger.error(f"Error analyzing function {function.name}: {e}")
            findings.append(Finding(
                finding_id=f"control_flow_error_{function.name}",
                title="Control Flow Analysis Error",
                description=f"Failed to analyze control flow in function {function.name}: {str(e)}",
                severity=Severity.LOW,
                location=function.source_location,
                vulnerability_type="analysis_error",
                detector_name="control_flow_analyzer"
            ))
        
        return findings
    
    def _detect_unreachable_code(self, cfg: ControlFlowGraph, 
                                function: IRFunction) -> List[Finding]:
        """Detect unreachable code in the control flow graph."""
        findings = []
        
        unreachable_nodes = cfg.has_unreachable_code()
        
        if unreachable_nodes:
            for node_id in unreachable_nodes:
                node = cfg.nodes.get(node_id)
                if node and node.statements:
                    findings.append(Finding(
                        finding_id=f"unreachable_code_{function.name}_{node_id}",
                        title="Unreachable Code",
                        description=f"Code block in function {function.name} is unreachable",
                        severity=Severity.MEDIUM,
                        location=function.source_location,
                        vulnerability_type="dead_code",
                        detector_name="control_flow_analyzer"
                    ))
        
        return findings
    
    def _detect_infinite_loops(self, cfg: ControlFlowGraph, 
                              function: IRFunction) -> List[Finding]:
        """Detect potential infinite loops."""
        findings = []
        
        # Look for strongly connected components that might indicate infinite loops
        scc_components = self._find_strongly_connected_components(cfg)
        
        for component in scc_components:
            if len(component) > 1:  # Cycle detected
                # Check if the cycle has any exit conditions
                has_exit = self._cycle_has_exit_condition(cfg, component)
                
                if not has_exit:
                    findings.append(Finding(
                        finding_id=f"infinite_loop_{function.name}_{hash(tuple(component))}",
                        title="Potential Infinite Loop",
                        description=f"Function {function.name} contains a potential infinite loop",
                        severity=Severity.HIGH,
                        location=function.source_location,
                        vulnerability_type="infinite_loop",
                        detector_name="control_flow_analyzer"
                    ))
        
        return findings
    
    def _detect_missing_returns(self, cfg: ControlFlowGraph, 
                               function: IRFunction) -> List[Finding]:
        """Detect functions that should return a value but have paths without returns."""
        findings = []
        
        # Only check functions that have a return type
        if not function.return_type:
            return findings
        
        # Check if all exit nodes have return statements
        for exit_node in cfg.exit_nodes:
            has_return = any(
                stmt.statement_type == StatementType.RETURN 
                for stmt in exit_node.statements
            )
            
            if not has_return:
                findings.append(Finding(
                    finding_id=f"missing_return_{function.name}_{exit_node.node_id}",
                    title="Missing Return Statement",
                    description=f"Function {function.name} has execution path without return statement",
                    severity=Severity.MEDIUM,
                    location=function.source_location,
                    vulnerability_type="missing_return",
                    detector_name="control_flow_analyzer"
                ))
        
        return findings
    
    def _detect_complex_control_flow(self, cfg: ControlFlowGraph, 
                                   function: IRFunction) -> List[Finding]:
        """Detect overly complex control flow that might indicate issues."""
        findings = []
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(cfg)
        
        if complexity > 15:  # High complexity threshold
            findings.append(Finding(
                finding_id=f"high_complexity_{function.name}",
                title="High Cyclomatic Complexity",
                description=f"Function {function.name} has high cyclomatic complexity ({complexity})",
                severity=Severity.LOW,
                location=function.source_location,
                vulnerability_type="code_quality",
                detector_name="control_flow_analyzer"
            ))
        
        # Check for excessive nesting
        max_nesting = self._calculate_max_nesting_depth(function)
        
        if max_nesting > 6:  # Deep nesting threshold
            findings.append(Finding(
                finding_id=f"deep_nesting_{function.name}",
                title="Deep Nesting",
                description=f"Function {function.name} has deep nesting level ({max_nesting})",
                severity=Severity.LOW,
                location=function.source_location,
                vulnerability_type="code_quality",
                detector_name="control_flow_analyzer"
            ))
        
        return findings
    
    def _detect_dead_code_after_returns(self, cfg: ControlFlowGraph, 
                                       function: IRFunction) -> List[Finding]:
        """Detect code that appears after return statements."""
        findings = []
        
        for node in cfg.nodes.values():
            return_found = False
            for i, stmt in enumerate(node.statements):
                if return_found:
                    # Code after return statement
                    findings.append(Finding(
                        finding_id=f"dead_code_after_return_{function.name}_{node.node_id}_{i}",
                        title="Dead Code After Return",
                        description=f"Code after return statement in function {function.name}",
                        severity=Severity.LOW,
                        location=function.source_location,
                        vulnerability_type="dead_code",
                        detector_name="control_flow_analyzer"
                    ))
                    break
                
                if stmt.statement_type == StatementType.RETURN:
                    return_found = True
        
        return findings
    
    def _find_strongly_connected_components(self, cfg: ControlFlowGraph) -> List[List[str]]:
        """Find strongly connected components in the CFG using Tarjan's algorithm."""
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        components = []
        
        def strongconnect(node_id):
            index[node_id] = index_counter[0]
            lowlinks[node_id] = index_counter[0]
            index_counter[0] += 1
            stack.append(node_id)
            on_stack[node_id] = True
            
            # Get successors
            successors = cfg.get_successors(node_id)
            for successor in successors:
                if successor not in index:
                    strongconnect(successor)
                    lowlinks[node_id] = min(lowlinks[node_id], lowlinks[successor])
                elif on_stack.get(successor, False):
                    lowlinks[node_id] = min(lowlinks[node_id], index[successor])
            
            # If node_id is a root node, pop the stack and create component
            if lowlinks[node_id] == index[node_id]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.append(w)
                    if w == node_id:
                        break
                components.append(component)
        
        for node_id in cfg.nodes:
            if node_id not in index:
                strongconnect(node_id)
        
        return components
    
    def _cycle_has_exit_condition(self, cfg: ControlFlowGraph, 
                                 cycle_nodes: List[str]) -> bool:
        """Check if a cycle has any exit conditions."""
        cycle_set = set(cycle_nodes)
        
        for node_id in cycle_nodes:
            successors = cfg.get_successors(node_id)
            # If any successor is outside the cycle, there's an exit
            if any(succ not in cycle_set for succ in successors):
                return True
        
        return False
    
    def _calculate_cyclomatic_complexity(self, cfg: ControlFlowGraph) -> int:
        """Calculate cyclomatic complexity: M = E - N + 2P."""
        edges = len(cfg.edges)
        nodes = len(cfg.nodes)
        components = 1  # Assuming single connected component
        
        return edges - nodes + 2 * components
    
    def _calculate_max_nesting_depth(self, function: IRFunction) -> int:
        """Calculate maximum nesting depth in a function."""
        max_depth = 0
        current_depth = 0
        
        def calculate_depth(statements: List[IRStatement], depth: int) -> int:
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            
            for stmt in statements:
                if stmt.statement_type in [StatementType.IF, StatementType.WHILE, StatementType.FOR]:
                    # Get nested statements
                    nested_statements = []
                    if hasattr(stmt, 'then_block') and stmt.then_block:
                        nested_statements.extend(stmt.then_block)
                    if hasattr(stmt, 'else_block') and stmt.else_block:
                        nested_statements.extend(stmt.else_block)
                    if hasattr(stmt, 'body') and stmt.body:
                        nested_statements.extend(stmt.body)
                    
                    if nested_statements:
                        calculate_depth(nested_statements, depth + 1)
            
            return max_depth
        
        return calculate_depth(function.body, 0)
    
    def get_cfg_statistics(self) -> Dict[str, Any]:
        """Get statistics about constructed CFGs."""
        if not self.cfgs:
            return {}
        
        total_nodes = sum(len(cfg.nodes) for cfg in self.cfgs.values())
        total_edges = sum(len(cfg.edges) for cfg in self.cfgs.values())
        
        complexities = [
            self._calculate_cyclomatic_complexity(cfg) 
            for cfg in self.cfgs.values()
        ]
        
        return {
            'total_functions': len(self.cfgs),
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'avg_nodes_per_function': total_nodes / len(self.cfgs) if self.cfgs else 0,
            'avg_edges_per_function': total_edges / len(self.cfgs) if self.cfgs else 0,
            'avg_complexity': sum(complexities) / len(complexities) if complexities else 0,
            'max_complexity': max(complexities) if complexities else 0,
            'min_complexity': min(complexities) if complexities else 0
        }
