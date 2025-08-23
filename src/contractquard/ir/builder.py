"""
IR Builder for constructing unified intermediate representation from language-specific ASTs.

This module provides the IRBuilder class that coordinates the transformation of
language-specific ASTs into the unified IR format.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .nodes import IRModule, IRContract, IRFunction, IRVariable, SourceLocation
from .graphs import ControlFlowGraph, DataFlowGraph, CallGraph
from .transformer import SolidityToIRTransformer, RustToIRTransformer, GoToIRTransformer


class IRBuilder:
    """
    Main builder class for constructing unified IR from multiple languages.
    
    This class coordinates the transformation process and maintains the unified
    representation across different source languages.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("contractquard.ir.builder")
        self.transformers = {
            'solidity': SolidityToIRTransformer(),
            'rust': RustToIRTransformer(),
            'go': GoToIRTransformer()
        }
        self.modules: Dict[str, IRModule] = {}
        self.global_call_graph: Optional[CallGraph] = None
    
    def build_from_solidity(self, parsed_data, file_path: str) -> IRModule:
        """
        Build IR from Solidity parsed data.
        
        Args:
            parsed_data: Parsed Solidity data from SolidityParser
            file_path: Path to the source file
            
        Returns:
            IRModule representing the Solidity contracts
        """
        self.logger.debug(f"Building IR from Solidity file: {file_path}")
        
        transformer = self.transformers['solidity']
        ir_module = transformer.transform(parsed_data, file_path)
        
        self.modules[file_path] = ir_module
        self.logger.info(f"Built IR module with {len(ir_module.contracts)} contracts")
        
        return ir_module
    
    def build_from_rust(self, ast_data: Dict[str, Any], file_path: str) -> IRModule:
        """
        Build IR from Rust AST data.
        
        Args:
            ast_data: Rust AST data from syn parser
            file_path: Path to the source file
            
        Returns:
            IRModule representing the Rust code
        """
        self.logger.debug(f"Building IR from Rust file: {file_path}")
        
        transformer = self.transformers['rust']
        ir_module = transformer.transform(ast_data, file_path)
        
        self.modules[file_path] = ir_module
        self.logger.info(f"Built IR module with {len(ir_module.contracts)} contracts")
        
        return ir_module
    
    def build_from_go(self, ast_data: Dict[str, Any], file_path: str) -> IRModule:
        """
        Build IR from Go AST data.
        
        Args:
            ast_data: Go AST data from go/ast parser
            file_path: Path to the source file
            
        Returns:
            IRModule representing the Go code
        """
        self.logger.debug(f"Building IR from Go file: {file_path}")
        
        transformer = self.transformers['go']
        ir_module = transformer.transform(ast_data, file_path)
        
        self.modules[file_path] = ir_module
        self.logger.info(f"Built IR module with {len(ir_module.contracts)} contracts")
        
        return ir_module
    
    def build_control_flow_graphs(self) -> Dict[str, ControlFlowGraph]:
        """
        Build control flow graphs for all functions in all modules.
        
        Returns:
            Dictionary mapping function identifiers to their CFGs
        """
        self.logger.debug("Building control flow graphs")
        cfgs = {}
        
        for module_path, module in self.modules.items():
            # Build CFGs for module-level functions
            for function in module.functions:
                cfg_id = f"{module_path}::{function.name}"
                cfgs[cfg_id] = ControlFlowGraph(function)
            
            # Build CFGs for contract functions
            for contract in module.contracts:
                for function in contract.functions:
                    cfg_id = f"{module_path}::{contract.name}::{function.name}"
                    cfgs[cfg_id] = ControlFlowGraph(function)
        
        self.logger.info(f"Built {len(cfgs)} control flow graphs")
        return cfgs
    
    def build_data_flow_graphs(self) -> Dict[str, DataFlowGraph]:
        """
        Build data flow graphs for all functions in all modules.
        
        Returns:
            Dictionary mapping function identifiers to their DFGs
        """
        self.logger.debug("Building data flow graphs")
        dfgs = {}
        
        for module_path, module in self.modules.items():
            # Build DFGs for module-level functions
            for function in module.functions:
                dfg_id = f"{module_path}::{function.name}"
                dfgs[dfg_id] = DataFlowGraph(function)
            
            # Build DFGs for contract functions
            for contract in module.contracts:
                for function in contract.functions:
                    dfg_id = f"{module_path}::{contract.name}::{function.name}"
                    dfgs[dfg_id] = DataFlowGraph(function)
        
        self.logger.info(f"Built {len(dfgs)} data flow graphs")
        return dfgs
    
    def build_global_call_graph(self) -> CallGraph:
        """
        Build a global call graph across all modules and languages.
        
        Returns:
            CallGraph representing all function call relationships
        """
        self.logger.debug("Building global call graph")
        
        all_functions = []
        
        # Collect all functions from all modules
        for module in self.modules.values():
            all_functions.extend(module.functions)
            for contract in module.contracts:
                all_functions.extend(contract.functions)
        
        self.global_call_graph = CallGraph(all_functions)
        self.logger.info(f"Built global call graph with {len(all_functions)} functions")
        
        return self.global_call_graph
    
    def get_module(self, file_path: str) -> Optional[IRModule]:
        """Get IR module for a specific file path."""
        return self.modules.get(file_path)
    
    def get_all_modules(self) -> Dict[str, IRModule]:
        """Get all IR modules."""
        return self.modules.copy()
    
    def get_all_contracts(self) -> List[IRContract]:
        """Get all contracts from all modules."""
        contracts = []
        for module in self.modules.values():
            contracts.extend(module.contracts)
        return contracts
    
    def get_all_functions(self) -> List[IRFunction]:
        """Get all functions from all modules and contracts."""
        functions = []
        for module in self.modules.values():
            functions.extend(module.functions)
            for contract in module.contracts:
                functions.extend(contract.functions)
        return functions
    
    def get_all_variables(self) -> List[IRVariable]:
        """Get all variables from all modules and contracts."""
        variables = []
        for module in self.modules.values():
            variables.extend(module.variables)
            for contract in module.contracts:
                variables.extend(contract.variables)
        return variables
    
    def find_function_by_name(self, name: str) -> List[IRFunction]:
        """Find all functions with a given name across all modules."""
        functions = []
        for function in self.get_all_functions():
            if function.name == name:
                functions.append(function)
        return functions
    
    def find_contract_by_name(self, name: str) -> List[IRContract]:
        """Find all contracts with a given name across all modules."""
        contracts = []
        for contract in self.get_all_contracts():
            if contract.name == name:
                contracts.append(contract)
        return contracts
    
    def validate_ir(self) -> List[str]:
        """
        Validate the constructed IR for consistency and completeness.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for duplicate contract names
        contract_names = {}
        for module_path, module in self.modules.items():
            for contract in module.contracts:
                if contract.name in contract_names:
                    errors.append(
                        f"Duplicate contract name '{contract.name}' found in "
                        f"{module_path} and {contract_names[contract.name]}"
                    )
                else:
                    contract_names[contract.name] = module_path
        
        # Check for functions without bodies (except interfaces)
        for module in self.modules.values():
            for contract in module.contracts:
                if not contract.is_interface:
                    for function in contract.functions:
                        if not function.body and not function.is_constructor:
                            errors.append(
                                f"Function '{function.name}' in contract "
                                f"'{contract.name}' has no body"
                            )
        
        # Check for unreachable code in CFGs
        cfgs = self.build_control_flow_graphs()
        for cfg_id, cfg in cfgs.items():
            unreachable = cfg.has_unreachable_code()
            if unreachable:
                errors.append(
                    f"Unreachable code detected in function {cfg_id}: "
                    f"nodes {unreachable}"
                )
        
        self.logger.info(f"IR validation completed with {len(errors)} errors")
        return errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the constructed IR."""
        stats = {
            'modules': len(self.modules),
            'contracts': len(self.get_all_contracts()),
            'functions': len(self.get_all_functions()),
            'variables': len(self.get_all_variables()),
            'languages': set()
        }
        
        # Determine languages based on file extensions
        for file_path in self.modules.keys():
            path = Path(file_path)
            if path.suffix == '.sol':
                stats['languages'].add('solidity')
            elif path.suffix == '.rs':
                stats['languages'].add('rust')
            elif path.suffix == '.go':
                stats['languages'].add('go')
        
        stats['languages'] = list(stats['languages'])
        
        return stats
    
    def clear(self):
        """Clear all built IR data."""
        self.modules.clear()
        self.global_call_graph = None
        self.logger.debug("Cleared all IR data")
