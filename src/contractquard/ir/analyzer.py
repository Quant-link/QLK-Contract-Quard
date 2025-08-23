"""
IR Analyzer for performing analysis on the unified intermediate representation.

This module provides analysis capabilities that work on the language-agnostic IR,
enabling cross-language vulnerability detection and semantic analysis.
"""

import logging
from typing import List, Dict, Set, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .nodes import (
    IRModule, IRContract, IRFunction, IRVariable, IRStatement, IRExpression,
    IRVisitor, StatementType, ExpressionType, Visibility
)
from .graphs import ControlFlowGraph, DataFlowGraph, CallGraph
from ..core.findings import Finding, Severity, SourceLocation


class AnalysisType(Enum):
    """Types of analysis that can be performed on IR."""
    CONTROL_FLOW = "control_flow"
    DATA_FLOW = "data_flow"
    TAINT_ANALYSIS = "taint_analysis"
    REACHABILITY = "reachability"
    DEAD_CODE = "dead_code"
    VULNERABILITY = "vulnerability"


@dataclass
class AnalysisResult:
    """Result of an IR analysis."""
    analysis_type: AnalysisType
    findings: List[Finding]
    metadata: Dict[str, Any]


class IRAnalyzer:
    """
    Main analyzer for the unified IR.
    
    This class provides various analysis capabilities that work on the
    language-agnostic IR representation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("contractquard.ir.analyzer")
        self.visitors = {
            AnalysisType.CONTROL_FLOW: ControlFlowAnalysisVisitor(),
            AnalysisType.DATA_FLOW: DataFlowAnalysisVisitor(),
            AnalysisType.TAINT_ANALYSIS: TaintAnalysisVisitor(),
            AnalysisType.REACHABILITY: ReachabilityAnalysisVisitor(),
            AnalysisType.DEAD_CODE: DeadCodeAnalysisVisitor(),
            AnalysisType.VULNERABILITY: VulnerabilityAnalysisVisitor()
        }
    
    def analyze_module(self, module: IRModule, 
                      analysis_types: List[AnalysisType]) -> List[AnalysisResult]:
        """
        Perform multiple types of analysis on an IR module.
        
        Args:
            module: IR module to analyze
            analysis_types: List of analysis types to perform
            
        Returns:
            List of analysis results
        """
        self.logger.debug(f"Analyzing module {module.name} with {len(analysis_types)} analysis types")
        
        results = []
        
        for analysis_type in analysis_types:
            if analysis_type in self.visitors:
                visitor = self.visitors[analysis_type]
                findings = visitor.analyze_module(module)
                
                result = AnalysisResult(
                    analysis_type=analysis_type,
                    findings=findings,
                    metadata=visitor.get_metadata()
                )
                results.append(result)
                
                self.logger.debug(f"{analysis_type.value} analysis found {len(findings)} issues")
            else:
                self.logger.warning(f"Unknown analysis type: {analysis_type}")
        
        return results
    
    def analyze_function(self, function: IRFunction, 
                        analysis_types: List[AnalysisType]) -> List[AnalysisResult]:
        """
        Perform analysis on a specific function.
        
        Args:
            function: IR function to analyze
            analysis_types: List of analysis types to perform
            
        Returns:
            List of analysis results
        """
        results = []
        
        for analysis_type in analysis_types:
            if analysis_type in self.visitors:
                visitor = self.visitors[analysis_type]
                findings = visitor.analyze_function(function)
                
                result = AnalysisResult(
                    analysis_type=analysis_type,
                    findings=findings,
                    metadata=visitor.get_metadata()
                )
                results.append(result)
        
        return results
    
    def detect_cross_language_issues(self, modules: List[IRModule]) -> List[Finding]:
        """
        Detect issues that span across multiple languages/modules.
        
        Args:
            modules: List of IR modules from different languages
            
        Returns:
            List of cross-language findings
        """
        self.logger.debug(f"Analyzing {len(modules)} modules for cross-language issues")
        
        findings = []
        
        # Check for interface consistency across languages
        findings.extend(self._check_interface_consistency(modules))
        
        # Check for data type compatibility
        findings.extend(self._check_type_compatibility(modules))
        
        # Check for calling convention consistency
        findings.extend(self._check_calling_conventions(modules))
        
        return findings
    
    def _check_interface_consistency(self, modules: List[IRModule]) -> List[Finding]:
        """Check for interface consistency across modules."""
        findings = []
        
        # Collect all public functions from all modules
        public_functions = {}
        
        for module in modules:
            for contract in module.contracts:
                for function in contract.functions:
                    if function.visibility == Visibility.PUBLIC:
                        key = f"{contract.name}::{function.name}"
                        if key in public_functions:
                            # Check if signatures match
                            existing_func = public_functions[key]
                            if not self._functions_compatible(existing_func, function):
                                findings.append(Finding(
                                    finding_id=f"interface_mismatch_{key}",
                                    title="Interface Mismatch",
                                    description=f"Function {key} has incompatible signatures across modules",
                                    severity=Severity.HIGH,
                                    location=function.source_location,
                                    vulnerability_type="interface_consistency",
                                    detector_name="ir_analyzer"
                                ))
                        else:
                            public_functions[key] = function
        
        return findings
    
    def _check_type_compatibility(self, modules: List[IRModule]) -> List[Finding]:
        """Check for type compatibility across modules."""
        findings = []
        
        # This would implement type compatibility checking
        # across different language type systems
        
        return findings
    
    def _check_calling_conventions(self, modules: List[IRModule]) -> List[Finding]:
        """Check for calling convention consistency."""
        findings = []
        
        # This would implement calling convention checking
        # for cross-language function calls
        
        return findings
    
    def _functions_compatible(self, func1: IRFunction, func2: IRFunction) -> bool:
        """Check if two functions have compatible signatures."""
        # Check parameter count
        if len(func1.parameters) != len(func2.parameters):
            return False
        
        # Check parameter types (simplified)
        for p1, p2 in zip(func1.parameters, func2.parameters):
            if p1.param_type.name != p2.param_type.name:
                return False
        
        # Check return types
        if func1.return_type and func2.return_type:
            if func1.return_type.name != func2.return_type.name:
                return False
        elif func1.return_type or func2.return_type:
            return False
        
        return True


class BaseAnalysisVisitor(IRVisitor):
    """Base class for analysis visitors."""
    
    def __init__(self):
        self.findings: List[Finding] = []
        self.metadata: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"contractquard.ir.{self.__class__.__name__}")
    
    def analyze_module(self, module: IRModule) -> List[Finding]:
        """Analyze a module and return findings."""
        self.findings.clear()
        self.metadata.clear()
        module.accept(self)
        return self.findings.copy()
    
    def analyze_function(self, function: IRFunction) -> List[Finding]:
        """Analyze a function and return findings."""
        self.findings.clear()
        self.metadata.clear()
        function.accept(self)
        return self.findings.copy()
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get analysis metadata."""
        return self.metadata.copy()
    
    def visit_module(self, node):
        for contract in node.contracts:
            contract.accept(self)
        for function in node.functions:
            function.accept(self)
    
    def visit_contract(self, node):
        for function in node.functions:
            function.accept(self)
        for variable in node.variables:
            variable.accept(self)
    
    def visit_function(self, node):
        for stmt in node.body:
            stmt.accept(self)
    
    def visit_variable(self, node):
        pass
    
    def visit_statement(self, node):
        for child in node.get_children():
            child.accept(self)
    
    def visit_expression(self, node):
        for child in node.get_children():
            child.accept(self)


class ControlFlowAnalysisVisitor(BaseAnalysisVisitor):
    """Visitor for control flow analysis."""
    
    def visit_function(self, node):
        # Build CFG and analyze
        cfg = ControlFlowGraph(node)
        
        # Check for unreachable code
        unreachable = cfg.has_unreachable_code()
        if unreachable:
            self.findings.append(Finding(
                finding_id=f"unreachable_code_{node.name}",
                title="Unreachable Code",
                description=f"Function {node.name} contains unreachable code blocks",
                severity=Severity.MEDIUM,
                location=node.source_location,
                vulnerability_type="dead_code",
                detector_name="control_flow_analyzer"
            ))
        
        # Check for infinite loops (simplified)
        if self._has_potential_infinite_loop(cfg):
            self.findings.append(Finding(
                finding_id=f"infinite_loop_{node.name}",
                title="Potential Infinite Loop",
                description=f"Function {node.name} may contain an infinite loop",
                severity=Severity.HIGH,
                location=node.source_location,
                vulnerability_type="infinite_loop",
                detector_name="control_flow_analyzer"
            ))
        
        self.metadata[f"cfg_{node.name}"] = {
            'nodes': len(cfg.nodes),
            'edges': len(cfg.edges),
            'unreachable_nodes': len(unreachable)
        }
    
    def _has_potential_infinite_loop(self, cfg: ControlFlowGraph) -> bool:
        """Check for potential infinite loops in CFG."""
        # Simplified check - look for back edges without exit conditions
        for edge in cfg.edges:
            if edge.edge_type.value == "loop_back":
                # This would need more sophisticated analysis
                return True
        return False


class DataFlowAnalysisVisitor(BaseAnalysisVisitor):
    """Visitor for data flow analysis."""
    
    def visit_function(self, node):
        # Build DFG and analyze
        dfg = DataFlowGraph(node)
        
        # Check for uninitialized variables (simplified)
        self._check_uninitialized_variables(node)
        
        self.metadata[f"dfg_{node.name}"] = {
            'variables': len(dfg.variable_nodes)
        }
    
    def _check_uninitialized_variables(self, function: IRFunction):
        """Check for potentially uninitialized variables."""
        # This would implement proper data flow analysis
        # to detect uninitialized variable usage
        pass


class TaintAnalysisVisitor(BaseAnalysisVisitor):
    """Visitor for taint analysis."""
    
    def visit_function(self, node):
        # Perform taint analysis to track untrusted data flow
        self._analyze_taint_flow(node)
    
    def _analyze_taint_flow(self, function: IRFunction):
        """Analyze taint flow in function."""
        # This would implement taint analysis to track
        # data flow from untrusted sources to sensitive operations
        pass


class ReachabilityAnalysisVisitor(BaseAnalysisVisitor):
    """Visitor for reachability analysis."""
    
    def visit_function(self, node):
        # Analyze function reachability
        if node.visibility == Visibility.PRIVATE and not self._is_called_internally(node):
            self.findings.append(Finding(
                finding_id=f"unused_function_{node.name}",
                title="Unused Private Function",
                description=f"Private function {node.name} is never called",
                severity=Severity.LOW,
                location=node.source_location,
                vulnerability_type="dead_code",
                detector_name="reachability_analyzer"
            ))
    
    def _is_called_internally(self, function: IRFunction) -> bool:
        """Check if function is called internally."""
        # This would check the call graph to see if function is called
        return True  # Simplified


class DeadCodeAnalysisVisitor(BaseAnalysisVisitor):
    """Visitor for dead code analysis."""
    
    def visit_function(self, node):
        # Analyze for dead code patterns
        self._check_dead_assignments(node)
        self._check_unused_variables(node)
    
    def _check_dead_assignments(self, function: IRFunction):
        """Check for dead assignments."""
        # This would implement dead assignment detection
        pass
    
    def _check_unused_variables(self, function: IRFunction):
        """Check for unused variables."""
        # This would implement unused variable detection
        pass


class VulnerabilityAnalysisVisitor(BaseAnalysisVisitor):
    """Visitor for vulnerability analysis."""
    
    def visit_function(self, node):
        # Check for common vulnerability patterns
        self._check_reentrancy_patterns(node)
        self._check_access_control_patterns(node)
        self._check_integer_overflow_patterns(node)
    
    def _check_reentrancy_patterns(self, function: IRFunction):
        """Check for reentrancy vulnerability patterns."""
        # This would implement reentrancy detection logic
        pass
    
    def _check_access_control_patterns(self, function: IRFunction):
        """Check for access control issues."""
        if function.visibility == Visibility.PUBLIC and not function.modifiers:
            self.findings.append(Finding(
                finding_id=f"missing_access_control_{function.name}",
                title="Missing Access Control",
                description=f"Public function {function.name} lacks access control modifiers",
                severity=Severity.MEDIUM,
                location=function.source_location,
                vulnerability_type="access_control",
                detector_name="vulnerability_analyzer"
            ))
    
    def _check_integer_overflow_patterns(self, function: IRFunction):
        """Check for integer overflow patterns."""
        # This would implement integer overflow detection
        pass
