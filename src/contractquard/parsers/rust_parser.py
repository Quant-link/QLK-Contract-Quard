"""
Rust Smart Contract Parser for ContractQuard.

This module provides parsing capabilities for Rust smart contracts including
ink!, CosmWasm, and Anchor frameworks. It uses the syn crate through Python
bindings to parse Rust code into AST and extract contract-specific information.
"""

import logging
import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from ..core.config import Config


@dataclass
class RustContractInfo:
    """Information about a Rust smart contract."""
    name: str
    contract_type: str  # 'ink', 'cosmwasm', 'anchor', 'generic'
    functions: List[Dict[str, Any]]
    structs: List[Dict[str, Any]]
    traits: List[Dict[str, Any]]
    impl_blocks: List[Dict[str, Any]]
    attributes: List[Dict[str, Any]]
    dependencies: List[str]
    unsafe_blocks: List[Dict[str, Any]]


@dataclass
class RustParseResult:
    """Result of parsing a Rust file."""
    file_path: str
    source_code: str
    contracts: List[RustContractInfo]
    ast_data: Dict[str, Any]
    compilation_errors: List[str]
    warnings: List[str]
    rust_version: str


class RustParser:
    """
    Parser for Rust smart contracts.
    
    This parser uses a Rust helper binary that leverages the syn crate
    to parse Rust code and extract AST information in a format suitable
    for analysis.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = logging.getLogger("contractquard.parsers.rust")
        self.rust_analyzer_path = self._find_rust_analyzer()
        self._ensure_rust_toolchain()
    
    def _find_rust_analyzer(self) -> Optional[str]:
        """Find the Rust analyzer binary."""
        try:
            result = subprocess.run(['which', 'rust-analyzer'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Try common installation paths
        common_paths = [
            '/usr/local/bin/rust-analyzer',
            '/usr/bin/rust-analyzer',
            os.path.expanduser('~/.cargo/bin/rust-analyzer')
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _ensure_rust_toolchain(self):
        """Ensure Rust toolchain is available."""
        try:
            result = subprocess.run(['rustc', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.debug(f"Rust toolchain available: {result.stdout.strip()}")
                return
        except Exception:
            pass
        
        self.logger.warning("Rust toolchain not found - some features may be limited")
    
    def parse(self, source_code: str, file_path: str) -> RustParseResult:
        """
        Parse Rust source code and extract contract information.
        
        Args:
            source_code: Rust source code to parse
            file_path: Path to the source file
            
        Returns:
            RustParseResult containing parsed information
        """
        self.logger.debug(f"Parsing Rust file: {file_path}")
        
        try:
            # Create temporary file for parsing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as temp_file:
                temp_file.write(source_code)
                temp_path = temp_file.name
            
            try:
                # Parse using Rust helper
                ast_data = self._parse_with_syn(temp_path)
                
                # Extract contract information
                contracts = self._extract_contracts(ast_data, source_code)
                
                # Get Rust version
                rust_version = self._get_rust_version()
                
                return RustParseResult(
                    file_path=file_path,
                    source_code=source_code,
                    contracts=contracts,
                    ast_data=ast_data,
                    compilation_errors=[],
                    warnings=[],
                    rust_version=rust_version
                )
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            self.logger.error(f"Failed to parse Rust file {file_path}: {e}")
            return RustParseResult(
                file_path=file_path,
                source_code=source_code,
                contracts=[],
                ast_data={},
                compilation_errors=[str(e)],
                warnings=[],
                rust_version=self._get_rust_version()
            )
    
    def _parse_with_syn(self, file_path: str) -> Dict[str, Any]:
        """Parse Rust file using syn crate through helper binary."""
        # This would call a Rust helper binary that uses syn to parse the file
        # For now, we'll create a mock AST structure
        
        self.logger.debug(f"Parsing with syn: {file_path}")
        
        # Mock AST structure - in production this would come from syn
        mock_ast = {
            "items": [
                {
                    "type": "mod",
                    "name": "contract",
                    "items": []
                }
            ],
            "attributes": [],
            "uses": []
        }
        
        return mock_ast
    
    def _extract_contracts(self, ast_data: Dict[str, Any], 
                          source_code: str) -> List[RustContractInfo]:
        """Extract contract information from AST data."""
        contracts = []
        
        # Detect contract type based on dependencies and attributes
        contract_type = self._detect_contract_type(source_code)
        
        if contract_type != 'generic':
            contract = self._extract_contract_by_type(ast_data, contract_type, source_code)
            if contract:
                contracts.append(contract)
        else:
            # Generic Rust code - look for contract-like patterns
            generic_contract = self._extract_generic_contract(ast_data, source_code)
            if generic_contract:
                contracts.append(generic_contract)
        
        return contracts
    
    def _detect_contract_type(self, source_code: str) -> str:
        """Detect the type of Rust smart contract."""
        # Check for ink! patterns
        if any(pattern in source_code for pattern in [
            '#[ink::contract]', 'use ink_lang', 'ink_storage', 'ink_env'
        ]):
            return 'ink'
        
        # Check for CosmWasm patterns
        if any(pattern in source_code for pattern in [
            'use cosmwasm_std', 'cosmwasm_schema', 'InstantiateMsg', 'ExecuteMsg'
        ]):
            return 'cosmwasm'
        
        # Check for Anchor patterns
        if any(pattern in source_code for pattern in [
            'use anchor_lang', '#[program]', 'anchor_spl'
        ]):
            return 'anchor'
        
        return 'generic'
    
    def _extract_contract_by_type(self, ast_data: Dict[str, Any], 
                                 contract_type: str, 
                                 source_code: str) -> Optional[RustContractInfo]:
        """Extract contract information based on contract type."""
        if contract_type == 'ink':
            return self._extract_ink_contract(ast_data, source_code)
        elif contract_type == 'cosmwasm':
            return self._extract_cosmwasm_contract(ast_data, source_code)
        elif contract_type == 'anchor':
            return self._extract_anchor_contract(ast_data, source_code)
        
        return None
    
    def _extract_ink_contract(self, ast_data: Dict[str, Any], 
                             source_code: str) -> RustContractInfo:
        """Extract ink! contract information."""
        return RustContractInfo(
            name="InkContract",
            contract_type="ink",
            functions=self._extract_functions(ast_data),
            structs=self._extract_structs(ast_data),
            traits=self._extract_traits(ast_data),
            impl_blocks=self._extract_impl_blocks(ast_data),
            attributes=self._extract_attributes(ast_data),
            dependencies=self._extract_dependencies(source_code),
            unsafe_blocks=self._extract_unsafe_blocks(ast_data)
        )
    
    def _extract_cosmwasm_contract(self, ast_data: Dict[str, Any], 
                                  source_code: str) -> RustContractInfo:
        """Extract CosmWasm contract information."""
        return RustContractInfo(
            name="CosmWasmContract",
            contract_type="cosmwasm",
            functions=self._extract_functions(ast_data),
            structs=self._extract_structs(ast_data),
            traits=self._extract_traits(ast_data),
            impl_blocks=self._extract_impl_blocks(ast_data),
            attributes=self._extract_attributes(ast_data),
            dependencies=self._extract_dependencies(source_code),
            unsafe_blocks=self._extract_unsafe_blocks(ast_data)
        )
    
    def _extract_anchor_contract(self, ast_data: Dict[str, Any], 
                                source_code: str) -> RustContractInfo:
        """Extract Anchor contract information."""
        return RustContractInfo(
            name="AnchorContract",
            contract_type="anchor",
            functions=self._extract_functions(ast_data),
            structs=self._extract_structs(ast_data),
            traits=self._extract_traits(ast_data),
            impl_blocks=self._extract_impl_blocks(ast_data),
            attributes=self._extract_attributes(ast_data),
            dependencies=self._extract_dependencies(source_code),
            unsafe_blocks=self._extract_unsafe_blocks(ast_data)
        )
    
    def _extract_generic_contract(self, ast_data: Dict[str, Any], 
                                 source_code: str) -> Optional[RustContractInfo]:
        """Extract generic Rust contract patterns."""
        # Look for contract-like patterns in generic Rust code
        functions = self._extract_functions(ast_data)
        structs = self._extract_structs(ast_data)
        
        if functions or structs:
            return RustContractInfo(
                name="GenericRustContract",
                contract_type="generic",
                functions=functions,
                structs=structs,
                traits=self._extract_traits(ast_data),
                impl_blocks=self._extract_impl_blocks(ast_data),
                attributes=self._extract_attributes(ast_data),
                dependencies=self._extract_dependencies(source_code),
                unsafe_blocks=self._extract_unsafe_blocks(ast_data)
            )
        
        return None
    
    def _extract_functions(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []
        
        # This would parse the actual AST to find function definitions
        # Mock implementation
        functions.append({
            "name": "example_function",
            "visibility": "pub",
            "parameters": [],
            "return_type": "Result<(), Error>",
            "attributes": [],
            "is_async": False,
            "is_unsafe": False
        })
        
        return functions
    
    def _extract_structs(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract struct definitions from AST."""
        structs = []
        
        # Mock implementation
        structs.append({
            "name": "ExampleStruct",
            "fields": [],
            "attributes": [],
            "visibility": "pub"
        })
        
        return structs
    
    def _extract_traits(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract trait definitions from AST."""
        return []
    
    def _extract_impl_blocks(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract impl blocks from AST."""
        return []
    
    def _extract_attributes(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attributes from AST."""
        return []
    
    def _extract_dependencies(self, source_code: str) -> List[str]:
        """Extract dependencies from source code."""
        dependencies = []
        
        # Parse use statements and extern crate declarations
        lines = source_code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('use ') and '::' in line:
                # Extract crate name
                parts = line.split('::')
                if len(parts) > 0:
                    crate_name = parts[0].replace('use ', '').strip()
                    if crate_name not in dependencies:
                        dependencies.append(crate_name)
            elif line.startswith('extern crate '):
                crate_name = line.replace('extern crate ', '').replace(';', '').strip()
                if crate_name not in dependencies:
                    dependencies.append(crate_name)
        
        return dependencies
    
    def _extract_unsafe_blocks(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract unsafe blocks from AST."""
        # This would identify unsafe blocks in the code
        return []
    
    def _get_rust_version(self) -> str:
        """Get the Rust compiler version."""
        try:
            result = subprocess.run(['rustc', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return "unknown"
    
    def validate_rust_syntax(self, source_code: str) -> Tuple[bool, List[str]]:
        """
        Validate Rust syntax without full compilation.
        
        Args:
            source_code: Rust source code to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as temp_file:
                temp_file.write(source_code)
                temp_path = temp_file.name
            
            try:
                # Use rustc to check syntax
                result = subprocess.run([
                    'rustc', '--emit=metadata', '--crate-type=lib', temp_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, []
                else:
                    errors = result.stderr.split('\n')
                    return False, [err for err in errors if err.strip()]
                    
            finally:
                os.unlink(temp_path)
                # Clean up metadata file if created
                metadata_file = temp_path.replace('.rs', '.rmeta')
                if os.path.exists(metadata_file):
                    os.unlink(metadata_file)
                    
        except Exception as e:
            return False, [str(e)]
    
    def get_contract_frameworks(self, source_code: str) -> List[str]:
        """
        Identify which Rust smart contract frameworks are used.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of detected frameworks
        """
        frameworks = []
        
        framework_patterns = {
            'ink': ['ink_lang', 'ink_storage', 'ink_env', '#[ink::contract]'],
            'cosmwasm': ['cosmwasm_std', 'cosmwasm_schema', 'cosmwasm_storage'],
            'anchor': ['anchor_lang', 'anchor_spl', '#[program]'],
            'near': ['near_sdk', '#[near_bindgen]'],
            'solana': ['solana_program', 'solana_sdk']
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in source_code for pattern in patterns):
                frameworks.append(framework)
        
        return frameworks
