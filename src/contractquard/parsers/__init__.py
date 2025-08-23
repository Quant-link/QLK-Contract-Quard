"""
Parsers for ContractQuard Static Analyzer.

This module handles parsing of Solidity source code into
structured representations (AST, etc.) for analysis.
"""

from .solidity_parser import SolidityParser

__all__ = [
    "SolidityParser",
]
