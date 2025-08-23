"""
ContractQuard Static Analyzer MVP
=================================

QuantLink's AI-augmented smart contract security analysis tool.

This MVP provides foundational static analysis capabilities for Solidity smart contracts,
including regex-based pattern matching and AST-based vulnerability detection.

Author: QuantLink
Version: 0.1.0
License: MIT
"""

__version__ = "0.1.0"
__author__ = "QuantLink"
__email__ = "dev@quantlink.com"

from .core.analyzer import ContractQuardAnalyzer
from .core.config import Config
from .core.findings import Finding, Severity

__all__ = [
    "ContractQuardAnalyzer",
    "Config", 
    "Finding",
    "Severity",
]
