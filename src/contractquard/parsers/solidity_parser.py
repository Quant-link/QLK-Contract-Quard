"""
Solidity parser for ContractQuard Static Analyzer.

This module handles parsing Solidity source code into AST representations
using the Solidity compiler (solc).
"""

import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from solcx import compile_source, install_solc, get_installed_solc_versions, set_solc_version
    from solcx.exceptions import SolcError, SolcNotInstalled
    SOLC_AVAILABLE = True
except ImportError:
    # Fallback for py-solc-x
    try:
        from solc import compile_source
        from solc.exceptions import SolcError
        SolcNotInstalled = Exception
        def install_solc(version): pass
        def get_installed_solc_versions(): return []
        def set_solc_version(version): pass
        SOLC_AVAILABLE = True
    except ImportError:
        # Mock implementations for testing without solc
        SOLC_AVAILABLE = False

        class SolcError(Exception):
            pass

        class SolcNotInstalled(Exception):
            pass

        def compile_source(source_code, **kwargs):
            # Mock compilation that returns empty results
            return {}

        def install_solc(version):
            pass

        def get_installed_solc_versions():
            return []

        def set_solc_version(version):
            pass

from ..core.config import SolcConfig


@dataclass
class ParsedContract:
    """Represents a parsed Solidity contract."""
    name: str
    source_code: str
    ast: Dict[str, Any]
    bytecode: Optional[str] = None
    abi: Optional[List[Dict[str, Any]]] = None
    source_map: Optional[str] = None


@dataclass
class ParsedData:
    """Container for all parsed data from a Solidity file."""
    file_path: str
    source_code: str
    contracts: List[ParsedContract]
    compilation_errors: List[str]
    warnings: List[str]
    solc_version: str


class SolidityParser:
    """
    Parser for Solidity source code using the Solidity compiler.

    This class handles compilation of Solidity code and extraction of
    AST data for vulnerability analysis.
    """

    def __init__(self, config: SolcConfig):
        """
        Initialize the Solidity parser.

        Args:
            config: Solidity compiler configuration.
        """
        self.config = config
        self.logger = logging.getLogger("contractquard.parser")
        self._active_solc_version_str: Optional[str] = None
        self._ensure_solc_available()

    def _ensure_solc_available(self) -> None:
        """Ensure Solidity compiler is available."""
        if not SOLC_AVAILABLE:
            self.logger.warning("Solidity compiler not available - running in mock mode")
            self._active_solc_version_str = "mock"
            return

        try:
            installed_versions = get_installed_solc_versions()
            target_version = self.config.version
            version_to_set = None

            if target_version:
                if target_version not in [str(v) for v in installed_versions]:
                    self.logger.info(f"Installing Solidity compiler version {target_version}")
                    install_solc(target_version)
                version_to_set = target_version
            else:
                if not installed_versions:
                    self.logger.info("Installing latest Solidity compiler")
                    pass
                else:
                    version_to_set = str(max(installed_versions))
            
            if version_to_set:
                 set_solc_version(version_to_set)
            elif not installed_versions:
                install_solc("latest")
                set_solc_version("latest")
            else:
                 set_solc_version(None)

            if 'get_solc_version' in globals() and hasattr(globals()['get_solc_version'], '__call__'):
                try:
                    import solcx
                    actual_version = solcx.get_solc_version(with_commit_hash=True)
                    self._active_solc_version_str = str(actual_version)
                    self.logger.info(f"Using Solidity compiler version {self._active_solc_version_str}")
                except Exception as e:
                    self.logger.warning(f"Could not determine exact solc version string after setting: {e}. Falling back.")
                    self._active_solc_version_str = version_to_set if version_to_set else "latest_installed_or_default"
            else:
                self._active_solc_version_str = version_to_set if version_to_set else "unknown_fallback"
                self.logger.info(f"Using Solidity compiler (fallback interface) version approx: {self._active_solc_version_str}")

        except SolcNotInstalled:
            self.logger.warning("Solc not installed. Attempting to install latest.")
            try:
                install_solc("latest")
                set_solc_version("latest")
                import solcx
                actual_version = solcx.get_solc_version(with_commit_hash=True)
                self._active_solc_version_str = str(actual_version)
                self.logger.info(f"Successfully installed and using Solidity compiler version {self._active_solc_version_str}")
            except Exception as e_install:
                self.logger.error(f"Could not install or set Solidity compiler: {e_install}")
                self._active_solc_version_str = "installation_failed"
        except Exception as e:
            self.logger.error(f"Could not setup Solidity compiler: {e}")
            self._active_solc_version_str = "setup_error"

    def parse(self, source_code: str, file_path: str) -> ParsedData:
        """
        Parse Solidity source code into structured data.

        Args:
            source_code: The Solidity source code to parse.
            file_path: Path to the source file (for error reporting).

        Returns:
            ParsedData containing AST and compilation information.

        Raises:
            SolcError: If compilation fails with critical errors.
        """
        self.logger.debug(f"Parsing Solidity file: {file_path}")

        compilation_errors = []
        warnings = []
        contracts = []

        if not SOLC_AVAILABLE:
            self.logger.warning("Solidity compiler not available - returning mock parsed data")
            return ParsedData(
                file_path=file_path,
                source_code=source_code,
                contracts=[],
                compilation_errors=["Solidity compiler not available"],
                warnings=["Running in mock mode without actual compilation"],
                solc_version="mock"
            )

        try:
            compile_settings = {}

            if self.config.optimize:
                compile_settings['optimizer'] = {
                    'enabled': True,
                    'runs': self.config.optimize_runs
                }

            if self.config.evm_version:
                compile_settings['evmVersion'] = self.config.evm_version

            compiled = compile_source(
                source_code,
                output_values=['abi', 'ast', 'bin', 'srcmap'],
            )

            for contract_id, contract_data in compiled.items():
                if ':' in contract_id:
                    _, contract_name = contract_id.split(':', 1)
                else:
                    contract_name = contract_id

                ast_data = None
                if 'ast' in contract_data:
                    ast_data = contract_data['ast']
                elif hasattr(compiled, 'get') and compiled.get('ast'):
                    ast_data = compiled['ast']

                contract = ParsedContract(
                    name=contract_name,
                    source_code=source_code,
                    ast=ast_data or {},
                    bytecode=contract_data.get('bin'),
                    abi=contract_data.get('abi'),
                    source_map=contract_data.get('srcmap')
                )
                contracts.append(contract)

            solc_version_for_data = self._get_solc_version()

        except SolcError as e:
            error_msg = str(e)
            self.logger.error(f"Solidity compilation error: {error_msg}")

            if "Error:" in error_msg:
                compilation_errors.append(error_msg)
            else:
                warnings.append(error_msg)

            solc_version_for_data = self._get_solc_version()

        except Exception as e:
            self.logger.error(f"Unexpected parsing error: {e}")
            compilation_errors.append(f"Parser error: {str(e)}")
            solc_version_for_data = self._get_solc_version()

        return ParsedData(
            file_path=file_path,
            source_code=source_code,
            contracts=contracts,
            compilation_errors=compilation_errors,
            warnings=warnings,
            solc_version=solc_version_for_data
        )

    def _get_solc_version(self) -> str:
        """Get the current Solidity compiler version string that was activated."""
        if self._active_solc_version_str:
            return self._active_solc_version_str
        
        self.logger.warning("_active_solc_version_str not set, falling back to config or generic 'unknown'")
        return self.config.version or "unknown_fallback_fetch"

    def extract_ast_nodes(self, ast: Dict[str, Any], node_type: str) -> List[Dict[str, Any]]:
        """
        Extract all nodes of a specific type from an AST.

        Args:
            ast: The AST dictionary to search.
            node_type: The type of nodes to extract (e.g., 'FunctionDefinition').

        Returns:
            List of AST nodes matching the specified type.
        """
        nodes = []

        def traverse(node):
            if isinstance(node, dict):
                if node.get('nodeType') == node_type:
                    nodes.append(node)

                for key, value in node.items():
                    if key == 'nodes' or key == 'statements' or key == 'body':
                        if isinstance(value, list):
                            for child in value:
                                traverse(child)
                        else:
                            traverse(value)
                    elif isinstance(value, dict):
                        traverse(value)
                    elif isinstance(value, list):
                        for item in value:
                            traverse(item)

        traverse(ast)
        return nodes

    def get_function_calls(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all function calls from an AST."""
        return self.extract_ast_nodes(ast, 'FunctionCall')

    def get_function_definitions(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all function definitions from an AST."""
        return self.extract_ast_nodes(ast, 'FunctionDefinition')

    def get_variable_declarations(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all variable declarations from an AST."""
        return self.extract_ast_nodes(ast, 'VariableDeclaration')

    def get_assignments(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all assignment operations from an AST."""
        return self.extract_ast_nodes(ast, 'Assignment')

    def get_source_location(self, node: Dict[str, Any], source_code: str) -> tuple:
        """
        Get line and column information for an AST node.

        Args:
            node: AST node with 'src' field.
            source_code: Original source code.

        Returns:
            Tuple of (line_start, column_start, line_end, column_end).
        """
        if 'src' not in node:
            return (1, 1, 1, 1)

        src_parts = node['src'].split(':')
        if len(src_parts) < 2:
            return (1, 1, 1, 1)

        try:
            start = int(src_parts[0])
            length = int(src_parts[1])
            end = start + length

            lines_before = source_code[:start].count('\n')
            line_start = lines_before + 1

            last_newline = source_code.rfind('\n', 0, start)
            column_start = start - last_newline if last_newline != -1 else start + 1

            lines_in_node = source_code[start:end].count('\n')
            line_end = line_start + lines_in_node

            if lines_in_node > 0:
                last_newline_in_node = source_code.rfind('\n', start, end)
                column_end = end - last_newline_in_node
            else:
                column_end = column_start + length

            return (line_start, column_start, line_end, column_end)

        except (ValueError, IndexError):
            return (1, 1, 1, 1)
