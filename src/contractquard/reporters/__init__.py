"""
Report generators for ContractQuard Static Analyzer.

This module handles formatting and outputting analysis results
in various formats (console, JSON, HTML, etc.).
"""

from .factory import ReporterFactory
from .base import BaseReporter

__all__ = [
    "ReporterFactory",
    "BaseReporter",
]
