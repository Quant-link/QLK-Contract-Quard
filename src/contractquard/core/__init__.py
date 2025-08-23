"""
Core module for ContractQuard Static Analyzer.

Contains the main analyzer engine, configuration management,
and core data structures.
"""

from .analyzer import ContractQuardAnalyzer
from .config import Config
from .findings import Finding, Severity

__all__ = [
    "ContractQuardAnalyzer",
    "Config",
    "Finding", 
    "Severity",
]
