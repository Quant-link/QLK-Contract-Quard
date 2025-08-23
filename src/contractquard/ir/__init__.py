"""
Unified Intermediate Representation (IR) for Multi-Language Contract Analysis.

This module provides a language-agnostic intermediate representation that normalizes
ASTs from Rust, Solidity, and Go into a common format for cross-language analysis.
"""

from .nodes import (
    IRNode, IRFunction, IRVariable, IRStatement, IRExpression,
    IRContract, IRModule, IRType, IRParameter
)
from .graphs import (
    ControlFlowGraph, DataFlowGraph, CallGraph,
    CFGNode, DFGNode, CallGraphNode
)
from .builder import IRBuilder
from .analyzer import IRAnalyzer
from .transformer import (
    SolidityToIRTransformer,
    RustToIRTransformer, 
    GoToIRTransformer
)

__all__ = [
    # Core IR Nodes
    "IRNode", "IRFunction", "IRVariable", "IRStatement", "IRExpression",
    "IRContract", "IRModule", "IRType", "IRParameter",
    
    # Graph Representations
    "ControlFlowGraph", "DataFlowGraph", "CallGraph",
    "CFGNode", "DFGNode", "CallGraphNode",
    
    # Builder and Analyzer
    "IRBuilder", "IRAnalyzer",
    
    # Language Transformers
    "SolidityToIRTransformer", "RustToIRTransformer", "GoToIRTransformer"
]
