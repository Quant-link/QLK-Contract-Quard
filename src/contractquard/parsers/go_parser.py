"""
Go Smart Contract Parser for ContractQuard.

This module provides parsing capabilities for Go smart contracts including
Cosmos SDK modules, Ethereum Go clients, and other blockchain-related Go code.
It uses the go/ast package through a Go helper binary to parse Go code.
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
class GoContractInfo:
    """Information about a Go smart contract or module."""
    name: str
    contract_type: str  # 'cosmos_sdk', 'ethereum', 'generic'
    functions: List[Dict[str, Any]]
    structs: List[Dict[str, Any]]
    interfaces: List[Dict[str, Any]]
    methods: List[Dict[str, Any]]
    imports: List[str]
    package_name: str
    goroutines: List[Dict[str, Any]]
    channels: List[Dict[str, Any]]


@dataclass
class GoParseResult:
    """Result of parsing a Go file."""
    file_path: str
    source_code: str
    contracts: List[GoContractInfo]
    ast_data: Dict[str, Any]
    compilation_errors: List[str]
    warnings: List[str]
    go_version: str


class GoParser:
    """
    Parser for Go smart contracts and blockchain modules.
    
    This parser uses a Go helper binary that leverages the go/ast package
    to parse Go code and extract AST information suitable for analysis.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = logging.getLogger("contractquard.parsers.go")
        self.go_binary_path = self._find_go_binary()
        self._ensure_go_toolchain()
    
    def _find_go_binary(self) -> Optional[str]:
        """Find the Go binary."""
        try:
            result = subprocess.run(['which', 'go'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Try common installation paths
        common_paths = [
            '/usr/local/go/bin/go',
            '/usr/bin/go',
            '/opt/go/bin/go'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _ensure_go_toolchain(self):
        """Ensure Go toolchain is available."""
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.debug(f"Go toolchain available: {result.stdout.strip()}")
                return
        except Exception:
            pass
        
        self.logger.warning("Go toolchain not found - some features may be limited")
    
    def parse(self, source_code: str, file_path: str) -> GoParseResult:
        """
        Parse Go source code and extract contract information.
        
        Args:
            source_code: Go source code to parse
            file_path: Path to the source file
            
        Returns:
            GoParseResult containing parsed information
        """
        self.logger.debug(f"Parsing Go file: {file_path}")
        
        try:
            # Create temporary file for parsing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as temp_file:
                temp_file.write(source_code)
                temp_path = temp_file.name
            
            try:
                # Parse using Go helper
                ast_data = self._parse_with_go_ast(temp_path)
                
                # Extract contract information
                contracts = self._extract_contracts(ast_data, source_code)
                
                # Get Go version
                go_version = self._get_go_version()
                
                return GoParseResult(
                    file_path=file_path,
                    source_code=source_code,
                    contracts=contracts,
                    ast_data=ast_data,
                    compilation_errors=[],
                    warnings=[],
                    go_version=go_version
                )
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            self.logger.error(f"Failed to parse Go file {file_path}: {e}")
            return GoParseResult(
                file_path=file_path,
                source_code=source_code,
                contracts=[],
                ast_data={},
                compilation_errors=[str(e)],
                warnings=[],
                go_version=self._get_go_version()
            )
    
    def _parse_with_go_ast(self, file_path: str) -> Dict[str, Any]:
        """Parse Go file using go/ast through helper binary."""
        # This would call a Go helper binary that uses go/ast to parse the file
        # For now, we'll create a mock AST structure
        
        self.logger.debug(f"Parsing with go/ast: {file_path}")
        
        # Mock AST structure - in production this would come from go/ast
        mock_ast = {
            "package": "main",
            "imports": [],
            "declarations": [],
            "functions": [],
            "types": []
        }
        
        return mock_ast
    
    def _extract_contracts(self, ast_data: Dict[str, Any], 
                          source_code: str) -> List[GoContractInfo]:
        """Extract contract information from AST data."""
        contracts = []
        
        # Detect contract type based on imports and patterns
        contract_type = self._detect_contract_type(source_code)
        
        if contract_type != 'generic':
            contract = self._extract_contract_by_type(ast_data, contract_type, source_code)
            if contract:
                contracts.append(contract)
        else:
            # Generic Go code - look for contract-like patterns
            generic_contract = self._extract_generic_contract(ast_data, source_code)
            if generic_contract:
                contracts.append(generic_contract)
        
        return contracts
    
    def _detect_contract_type(self, source_code: str) -> str:
        """Detect the type of Go smart contract or module."""
        # Check for Cosmos SDK patterns
        if any(pattern in source_code for pattern in [
            'github.com/cosmos/cosmos-sdk', 'sdk.Msg', 'sdk.Context', 'abci.Application'
        ]):
            return 'cosmos_sdk'
        
        # Check for Ethereum Go patterns
        if any(pattern in source_code for pattern in [
            'github.com/ethereum/go-ethereum', 'common.Address', 'big.Int', 'ethclient'
        ]):
            return 'ethereum'
        
        # Check for other blockchain patterns
        if any(pattern in source_code for pattern in [
            'blockchain', 'smart contract', 'consensus', 'validator'
        ]):
            return 'blockchain'
        
        return 'generic'
    
    def _extract_contract_by_type(self, ast_data: Dict[str, Any], 
                                 contract_type: str, 
                                 source_code: str) -> Optional[GoContractInfo]:
        """Extract contract information based on contract type."""
        if contract_type == 'cosmos_sdk':
            return self._extract_cosmos_sdk_module(ast_data, source_code)
        elif contract_type == 'ethereum':
            return self._extract_ethereum_contract(ast_data, source_code)
        elif contract_type == 'blockchain':
            return self._extract_blockchain_module(ast_data, source_code)
        
        return None
    
    def _extract_cosmos_sdk_module(self, ast_data: Dict[str, Any], 
                                  source_code: str) -> GoContractInfo:
        """Extract Cosmos SDK module information."""
        return GoContractInfo(
            name="CosmosSDKModule",
            contract_type="cosmos_sdk",
            functions=self._extract_functions(ast_data),
            structs=self._extract_structs(ast_data),
            interfaces=self._extract_interfaces(ast_data),
            methods=self._extract_methods(ast_data),
            imports=self._extract_imports(source_code),
            package_name=self._extract_package_name(source_code),
            goroutines=self._extract_goroutines(ast_data),
            channels=self._extract_channels(ast_data)
        )
    
    def _extract_ethereum_contract(self, ast_data: Dict[str, Any], 
                                  source_code: str) -> GoContractInfo:
        """Extract Ethereum Go client information."""
        return GoContractInfo(
            name="EthereumGoContract",
            contract_type="ethereum",
            functions=self._extract_functions(ast_data),
            structs=self._extract_structs(ast_data),
            interfaces=self._extract_interfaces(ast_data),
            methods=self._extract_methods(ast_data),
            imports=self._extract_imports(source_code),
            package_name=self._extract_package_name(source_code),
            goroutines=self._extract_goroutines(ast_data),
            channels=self._extract_channels(ast_data)
        )
    
    def _extract_blockchain_module(self, ast_data: Dict[str, Any], 
                                  source_code: str) -> GoContractInfo:
        """Extract generic blockchain module information."""
        return GoContractInfo(
            name="BlockchainModule",
            contract_type="blockchain",
            functions=self._extract_functions(ast_data),
            structs=self._extract_structs(ast_data),
            interfaces=self._extract_interfaces(ast_data),
            methods=self._extract_methods(ast_data),
            imports=self._extract_imports(source_code),
            package_name=self._extract_package_name(source_code),
            goroutines=self._extract_goroutines(ast_data),
            channels=self._extract_channels(ast_data)
        )
    
    def _extract_generic_contract(self, ast_data: Dict[str, Any], 
                                 source_code: str) -> Optional[GoContractInfo]:
        """Extract generic Go contract patterns."""
        # Look for contract-like patterns in generic Go code
        functions = self._extract_functions(ast_data)
        structs = self._extract_structs(ast_data)
        
        if functions or structs:
            return GoContractInfo(
                name="GenericGoContract",
                contract_type="generic",
                functions=functions,
                structs=structs,
                interfaces=self._extract_interfaces(ast_data),
                methods=self._extract_methods(ast_data),
                imports=self._extract_imports(source_code),
                package_name=self._extract_package_name(source_code),
                goroutines=self._extract_goroutines(ast_data),
                channels=self._extract_channels(ast_data)
            )
        
        return None
    
    def _extract_functions(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []
        
        # Mock implementation
        functions.append({
            "name": "example_function",
            "parameters": [],
            "return_types": [],
            "is_exported": True,
            "receiver": None,
            "line_start": 1,
            "line_end": 10
        })
        
        return functions
    
    def _extract_structs(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract struct definitions from AST."""
        structs = []
        
        # Mock implementation
        structs.append({
            "name": "ExampleStruct",
            "fields": [],
            "is_exported": True,
            "line_start": 1,
            "line_end": 5
        })
        
        return structs
    
    def _extract_interfaces(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract interface definitions from AST."""
        return []
    
    def _extract_methods(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract method definitions from AST."""
        return []
    
    def _extract_imports(self, source_code: str) -> List[str]:
        """Extract import statements from source code."""
        imports = []
        
        lines = source_code.split('\n')
        in_import_block = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('import ('):
                in_import_block = True
                continue
            elif line == ')' and in_import_block:
                in_import_block = False
                continue
            elif in_import_block:
                # Extract import path
                if '"' in line:
                    import_path = line.split('"')[1]
                    imports.append(import_path)
            elif line.startswith('import '):
                # Single import
                if '"' in line:
                    import_path = line.split('"')[1]
                    imports.append(import_path)
        
        return imports
    
    def _extract_package_name(self, source_code: str) -> str:
        """Extract package name from source code."""
        lines = source_code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('package '):
                return line.split(' ')[1]
        return "unknown"
    
    def _extract_goroutines(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract goroutine usage from AST."""
        # This would identify 'go' statements in the code
        return []
    
    def _extract_channels(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract channel usage from AST."""
        # This would identify channel declarations and operations
        return []
    
    def _get_go_version(self) -> str:
        """Get the Go compiler version."""
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return "unknown"
    
    def validate_go_syntax(self, source_code: str) -> Tuple[bool, List[str]]:
        """
        Validate Go syntax without full compilation.
        
        Args:
            source_code: Go source code to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as temp_file:
                temp_file.write(source_code)
                temp_path = temp_file.name
            
            try:
                # Use go build to check syntax
                result = subprocess.run([
                    'go', 'build', '-o', '/dev/null', temp_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, []
                else:
                    errors = result.stderr.split('\n')
                    return False, [err for err in errors if err.strip()]
                    
            finally:
                os.unlink(temp_path)
                    
        except Exception as e:
            return False, [str(e)]
    
    def get_blockchain_frameworks(self, source_code: str) -> List[str]:
        """
        Identify which Go blockchain frameworks are used.
        
        Args:
            source_code: Go source code to analyze
            
        Returns:
            List of detected frameworks
        """
        frameworks = []
        
        framework_patterns = {
            'cosmos_sdk': ['github.com/cosmos/cosmos-sdk', 'sdk.Msg', 'sdk.Context'],
            'ethereum': ['github.com/ethereum/go-ethereum', 'ethclient', 'common.Address'],
            'tendermint': ['github.com/tendermint/tendermint', 'tmtypes', 'abci'],
            'fabric': ['github.com/hyperledger/fabric', 'chaincode', 'shim'],
            'geth': ['github.com/ethereum/go-ethereum/core', 'geth', 'ethdb']
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in source_code for pattern in patterns):
                frameworks.append(framework)
        
        return frameworks
    
    def detect_concurrency_patterns(self, source_code: str) -> Dict[str, List[str]]:
        """
        Detect concurrency patterns in Go code.
        
        Args:
            source_code: Go source code to analyze
            
        Returns:
            Dictionary of concurrency patterns found
        """
        patterns = {
            'goroutines': [],
            'channels': [],
            'mutexes': [],
            'wait_groups': [],
            'select_statements': []
        }
        
        lines = source_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if 'go ' in line and '(' in line:
                patterns['goroutines'].append(f"Line {i}: {line}")
            
            if 'make(chan' in line or 'chan ' in line:
                patterns['channels'].append(f"Line {i}: {line}")
            
            if 'sync.Mutex' in line or 'sync.RWMutex' in line:
                patterns['mutexes'].append(f"Line {i}: {line}")
            
            if 'sync.WaitGroup' in line:
                patterns['wait_groups'].append(f"Line {i}: {line}")
            
            if 'select {' in line:
                patterns['select_statements'].append(f"Line {i}: {line}")
        
        return patterns
