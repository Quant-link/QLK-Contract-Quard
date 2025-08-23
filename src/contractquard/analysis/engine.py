"""
Main Static Analysis Engine for ContractQuard.

This module provides the main engine that coordinates all static analysis
components and provides a unified interface for comprehensive analysis.
"""

import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

from ..core.findings import Finding, Severity
from ..ir.nodes import IRModule, IRFunction, IRContract
from ..ir.builder import IRBuilder
from ..ir.analyzer import IRAnalyzer, AnalysisType

from .control_flow import ControlFlowAnalyzer
from .data_flow import DataFlowAnalyzer
from .taint_analysis import TaintAnalyzer
from .symbolic_execution import SymbolicExecutor
from .vulnerability_detector import VulnerabilityDetector
from .semantic_analyzer import SemanticAnalyzer


class AnalysisMode(Enum):
    """Analysis modes for different levels of analysis depth."""
    FAST = "fast"           # Basic analysis for quick feedback
    STANDARD = "standard"   # Standard analysis with good coverage
    DEEP = "deep"          # Comprehensive analysis with all techniques
    CUSTOM = "custom"      # Custom analysis with specific analyzers


@dataclass
class AnalysisConfiguration:
    """Configuration for static analysis."""
    mode: AnalysisMode = AnalysisMode.STANDARD
    enabled_analyzers: Set[str] = None
    max_analysis_time: int = 300  # seconds
    max_memory_usage: int = 1024  # MB
    enable_cross_language: bool = True
    enable_symbolic_execution: bool = True
    symbolic_execution_depth: int = 10
    enable_taint_analysis: bool = True
    taint_sources: List[str] = None
    taint_sinks: List[str] = None


@dataclass
class AnalysisResult:
    """Result of static analysis."""
    findings: List[Finding]
    statistics: Dict[str, Any]
    analysis_time: float
    memory_usage: float
    errors: List[str]
    warnings: List[str]


class StaticAnalysisEngine:
    """
    Main static analysis engine that coordinates all analysis components.
    
    This engine provides a unified interface for performing comprehensive
    static analysis on multi-language smart contracts.
    """
    
    def __init__(self, config: Optional[AnalysisConfiguration] = None):
        self.config = config or AnalysisConfiguration()
        self.logger = logging.getLogger("contractquard.analysis.engine")
        
        # Initialize analyzers
        self.ir_builder = IRBuilder()
        self.ir_analyzer = IRAnalyzer()
        self.control_flow_analyzer = ControlFlowAnalyzer()
        self.data_flow_analyzer = DataFlowAnalyzer()
        self.taint_analyzer = TaintAnalyzer()
        self.symbolic_executor = SymbolicExecutor()
        self.vulnerability_detector = VulnerabilityDetector()
        self.semantic_analyzer = SemanticAnalyzer()
        
        # Analysis state
        self.current_modules: List[IRModule] = []
        self.analysis_cache: Dict[str, Any] = {}
        
        self.logger.info("Static Analysis Engine initialized")
    
    def analyze_solidity(self, parsed_data, file_path: str) -> AnalysisResult:
        """
        Analyze Solidity contracts.
        
        Args:
            parsed_data: Parsed Solidity data
            file_path: Path to the source file
            
        Returns:
            AnalysisResult containing findings and statistics
        """
        self.logger.info(f"Starting Solidity analysis: {file_path}")
        
        try:
            # Build IR
            ir_module = self.ir_builder.build_from_solidity(parsed_data, file_path)
            self.current_modules.append(ir_module)
            
            # Perform analysis
            return self._perform_analysis([ir_module])
            
        except Exception as e:
            self.logger.error(f"Error analyzing Solidity file {file_path}: {e}")
            return AnalysisResult(
                findings=[],
                statistics={},
                analysis_time=0.0,
                memory_usage=0.0,
                errors=[str(e)],
                warnings=[]
            )
    
    def analyze_rust(self, ast_data: Dict[str, Any], file_path: str) -> AnalysisResult:
        """
        Analyze Rust contracts.
        
        Args:
            ast_data: Rust AST data
            file_path: Path to the source file
            
        Returns:
            AnalysisResult containing findings and statistics
        """
        self.logger.info(f"Starting Rust analysis: {file_path}")
        
        try:
            # Build IR
            ir_module = self.ir_builder.build_from_rust(ast_data, file_path)
            self.current_modules.append(ir_module)
            
            # Perform analysis
            return self._perform_analysis([ir_module])
            
        except Exception as e:
            self.logger.error(f"Error analyzing Rust file {file_path}: {e}")
            return AnalysisResult(
                findings=[],
                statistics={},
                analysis_time=0.0,
                memory_usage=0.0,
                errors=[str(e)],
                warnings=[]
            )
    
    def analyze_go(self, ast_data: Dict[str, Any], file_path: str) -> AnalysisResult:
        """
        Analyze Go contracts.
        
        Args:
            ast_data: Go AST data
            file_path: Path to the source file
            
        Returns:
            AnalysisResult containing findings and statistics
        """
        self.logger.info(f"Starting Go analysis: {file_path}")
        
        try:
            # Build IR
            ir_module = self.ir_builder.build_from_go(ast_data, file_path)
            self.current_modules.append(ir_module)
            
            # Perform analysis
            return self._perform_analysis([ir_module])
            
        except Exception as e:
            self.logger.error(f"Error analyzing Go file {file_path}: {e}")
            return AnalysisResult(
                findings=[],
                statistics={},
                analysis_time=0.0,
                memory_usage=0.0,
                errors=[str(e)],
                warnings=[]
            )
    
    def analyze_multi_language(self, modules: List[IRModule]) -> AnalysisResult:
        """
        Perform cross-language analysis on multiple modules.
        
        Args:
            modules: List of IR modules from different languages
            
        Returns:
            AnalysisResult containing cross-language findings
        """
        self.logger.info(f"Starting multi-language analysis on {len(modules)} modules")
        
        try:
            # Perform individual module analysis
            result = self._perform_analysis(modules)
            
            # Add cross-language analysis if enabled
            if self.config.enable_cross_language:
                cross_language_findings = self.ir_analyzer.detect_cross_language_issues(modules)
                result.findings.extend(cross_language_findings)
                
                self.logger.info(f"Cross-language analysis found {len(cross_language_findings)} issues")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in multi-language analysis: {e}")
            return AnalysisResult(
                findings=[],
                statistics={},
                analysis_time=0.0,
                memory_usage=0.0,
                errors=[str(e)],
                warnings=[]
            )
    
    def _perform_analysis(self, modules: List[IRModule]) -> AnalysisResult:
        """
        Perform comprehensive analysis on IR modules.
        
        Args:
            modules: List of IR modules to analyze
            
        Returns:
            AnalysisResult containing all findings
        """
        import time
        import psutil
        import os
        
        start_time = time.time()
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        all_findings = []
        all_errors = []
        all_warnings = []
        statistics = {}
        
        try:
            # Determine which analyzers to run based on configuration
            analyzers_to_run = self._get_enabled_analyzers()
            
            for module in modules:
                self.logger.debug(f"Analyzing module: {module.name}")
                
                # IR-based analysis
                if 'ir_analyzer' in analyzers_to_run:
                    ir_results = self._run_ir_analysis(module)
                    all_findings.extend(ir_results.findings)
                    statistics.update(ir_results.metadata)
                
                # Control flow analysis
                if 'control_flow' in analyzers_to_run:
                    cf_findings = self.control_flow_analyzer.analyze_module(module)
                    all_findings.extend(cf_findings)
                
                # Data flow analysis
                if 'data_flow' in analyzers_to_run:
                    df_findings = self.data_flow_analyzer.analyze_module(module)
                    all_findings.extend(df_findings)
                
                # Taint analysis
                if 'taint_analysis' in analyzers_to_run and self.config.enable_taint_analysis:
                    taint_findings = self.taint_analyzer.analyze_module(module)
                    all_findings.extend(taint_findings)
                
                # Symbolic execution
                if 'symbolic_execution' in analyzers_to_run and self.config.enable_symbolic_execution:
                    symbolic_findings = self.symbolic_executor.analyze_module(module)
                    all_findings.extend(symbolic_findings)
                
                # Vulnerability detection
                if 'vulnerability_detector' in analyzers_to_run:
                    vuln_findings = self.vulnerability_detector.analyze_module(module)
                    all_findings.extend(vuln_findings)
                
                # Semantic analysis
                if 'semantic_analyzer' in analyzers_to_run:
                    semantic_findings = self.semantic_analyzer.analyze_module(module)
                    all_findings.extend(semantic_findings)
            
            # Post-processing
            all_findings = self._post_process_findings(all_findings)
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {e}")
            all_errors.append(str(e))
        
        # Calculate final statistics
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        analysis_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        statistics.update({
            'total_modules': len(modules),
            'total_findings': len(all_findings),
            'analysis_time': analysis_time,
            'memory_usage': memory_usage,
            'analyzers_run': list(analyzers_to_run)
        })
        
        self.logger.info(f"Analysis completed in {analysis_time:.2f}s with {len(all_findings)} findings")
        
        return AnalysisResult(
            findings=all_findings,
            statistics=statistics,
            analysis_time=analysis_time,
            memory_usage=memory_usage,
            errors=all_errors,
            warnings=all_warnings
        )
    
    def _get_enabled_analyzers(self) -> Set[str]:
        """Get the set of enabled analyzers based on configuration."""
        if self.config.enabled_analyzers:
            return self.config.enabled_analyzers
        
        # Default analyzer sets based on mode
        if self.config.mode == AnalysisMode.FAST:
            return {'ir_analyzer', 'vulnerability_detector'}
        elif self.config.mode == AnalysisMode.STANDARD:
            return {
                'ir_analyzer', 'control_flow', 'data_flow', 
                'vulnerability_detector', 'semantic_analyzer'
            }
        elif self.config.mode == AnalysisMode.DEEP:
            return {
                'ir_analyzer', 'control_flow', 'data_flow', 'taint_analysis',
                'symbolic_execution', 'vulnerability_detector', 'semantic_analyzer'
            }
        else:  # CUSTOM
            return set()
    
    def _run_ir_analysis(self, module: IRModule):
        """Run IR-based analysis on a module."""
        analysis_types = [
            AnalysisType.CONTROL_FLOW,
            AnalysisType.DATA_FLOW,
            AnalysisType.REACHABILITY,
            AnalysisType.DEAD_CODE,
            AnalysisType.VULNERABILITY
        ]
        
        results = self.ir_analyzer.analyze_module(module, analysis_types)
        
        # Combine all findings
        combined_result = type('AnalysisResult', (), {
            'findings': [],
            'metadata': {}
        })()
        
        for result in results:
            combined_result.findings.extend(result.findings)
            combined_result.metadata.update(result.metadata)
        
        return combined_result
    
    def _post_process_findings(self, findings: List[Finding]) -> List[Finding]:
        """Post-process findings to remove duplicates and rank by severity."""
        # Remove duplicates based on finding_id
        unique_findings = {}
        for finding in findings:
            if finding.finding_id not in unique_findings:
                unique_findings[finding.finding_id] = finding
            else:
                # Keep the one with higher severity
                existing = unique_findings[finding.finding_id]
                if finding.severity.value > existing.severity.value:
                    unique_findings[finding.finding_id] = finding
        
        # Sort by severity (Critical -> High -> Medium -> Low -> Info)
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4
        }
        
        sorted_findings = sorted(
            unique_findings.values(),
            key=lambda f: (severity_order.get(f.severity, 5), f.title)
        )
        
        return sorted_findings
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get comprehensive analysis statistics."""
        stats = {
            'modules_analyzed': len(self.current_modules),
            'total_contracts': sum(len(m.contracts) for m in self.current_modules),
            'total_functions': sum(len(m.functions) + sum(len(c.functions) for c in m.contracts) 
                                 for m in self.current_modules),
            'languages_detected': set(),
            'cache_hits': len(self.analysis_cache),
            'configuration': {
                'mode': self.config.mode.value,
                'cross_language_enabled': self.config.enable_cross_language,
                'symbolic_execution_enabled': self.config.enable_symbolic_execution,
                'taint_analysis_enabled': self.config.enable_taint_analysis
            }
        }
        
        # Detect languages from file paths
        for module in self.current_modules:
            if module.name.endswith('.sol'):
                stats['languages_detected'].add('solidity')
            elif module.name.endswith('.rs'):
                stats['languages_detected'].add('rust')
            elif module.name.endswith('.go'):
                stats['languages_detected'].add('go')
        
        stats['languages_detected'] = list(stats['languages_detected'])
        
        return stats
    
    def clear_cache(self):
        """Clear analysis cache."""
        self.analysis_cache.clear()
        self.current_modules.clear()
        self.logger.debug("Analysis cache cleared")
    
    def validate_configuration(self) -> List[str]:
        """Validate the analysis configuration."""
        errors = []
        
        if self.config.max_analysis_time <= 0:
            errors.append("max_analysis_time must be positive")
        
        if self.config.max_memory_usage <= 0:
            errors.append("max_memory_usage must be positive")
        
        if self.config.symbolic_execution_depth <= 0:
            errors.append("symbolic_execution_depth must be positive")
        
        if self.config.enabled_analyzers:
            valid_analyzers = {
                'ir_analyzer', 'control_flow', 'data_flow', 'taint_analysis',
                'symbolic_execution', 'vulnerability_detector', 'semantic_analyzer'
            }
            invalid = self.config.enabled_analyzers - valid_analyzers
            if invalid:
                errors.append(f"Invalid analyzers: {invalid}")
        
        return errors


# Analysis configuration presets
ANALYSIS_PRESETS = {
    'quick_scan': AnalysisConfiguration(
        mode=AnalysisMode.FAST,
        max_analysis_time=60,
        enable_symbolic_execution=False,
        enable_taint_analysis=False
    ),

    'security_audit': AnalysisConfiguration(
        mode=AnalysisMode.DEEP,
        max_analysis_time=600,
        enable_symbolic_execution=True,
        enable_taint_analysis=True,
        symbolic_execution_depth=15
    ),

    'ci_integration': AnalysisConfiguration(
        mode=AnalysisMode.STANDARD,
        max_analysis_time=180,
        enable_symbolic_execution=True,
        enable_taint_analysis=True,
        symbolic_execution_depth=8
    ),

    'development': AnalysisConfiguration(
        mode=AnalysisMode.STANDARD,
        max_analysis_time=120,
        enable_symbolic_execution=False,
        enable_taint_analysis=True
    )
}
