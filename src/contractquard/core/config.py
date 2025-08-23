"""
Configuration management for ContractQuard Static Analyzer.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class DetectorConfig:
    """Configuration for individual detectors."""
    enabled: bool = True
    severity_override: Optional[str] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutputConfig:
    """Configuration for output formatting and reporting."""
    format: str = "console"  # console, json, html, markdown
    output_file: Optional[str] = None
    include_code_snippets: bool = True
    max_snippet_lines: int = 5
    color_output: bool = True
    verbose: bool = False


@dataclass
class SolcConfig:
    """Configuration for Solidity compiler integration."""
    version: Optional[str] = None  # Auto-detect if None
    optimize: bool = False
    optimize_runs: int = 200
    evm_version: Optional[str] = None
    allow_paths: List[str] = field(default_factory=list)


@dataclass
class Config:
    """Main configuration class for ContractQuard."""
    
    # Analysis settings
    max_file_size_mb: int = 10
    timeout_seconds: int = 300
    include_test_files: bool = False
    
    # Detector configurations
    detectors: Dict[str, DetectorConfig] = field(default_factory=dict)
    
    # Output configuration
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # Solidity compiler configuration
    solc: SolcConfig = field(default_factory=SolcConfig)
    
    # Severity filtering
    min_severity: str = "INFO"
    exclude_severities: List[str] = field(default_factory=list)
    
    # File filtering
    include_patterns: List[str] = field(default_factory=lambda: ["*.sol"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["*test*", "*mock*"])
    
    @classmethod
    def load_from_file(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        config = cls()
        
        # Update basic settings
        for key in ['max_file_size_mb', 'timeout_seconds', 'include_test_files', 
                   'min_severity', 'exclude_severities', 'include_patterns', 'exclude_patterns']:
            if key in data:
                setattr(config, key, data[key])
        
        # Update detector configurations
        if 'detectors' in data:
            for detector_name, detector_data in data['detectors'].items():
                config.detectors[detector_name] = DetectorConfig(
                    enabled=detector_data.get('enabled', True),
                    severity_override=detector_data.get('severity_override'),
                    custom_params=detector_data.get('custom_params', {})
                )
        
        # Update output configuration
        if 'output' in data:
            output_data = data['output']
            config.output = OutputConfig(
                format=output_data.get('format', 'console'),
                output_file=output_data.get('output_file'),
                include_code_snippets=output_data.get('include_code_snippets', True),
                max_snippet_lines=output_data.get('max_snippet_lines', 5),
                color_output=output_data.get('color_output', True),
                verbose=output_data.get('verbose', False)
            )
        
        # Update Solc configuration
        if 'solc' in data:
            solc_data = data['solc']
            config.solc = SolcConfig(
                version=solc_data.get('version'),
                optimize=solc_data.get('optimize', False),
                optimize_runs=solc_data.get('optimize_runs', 200),
                evm_version=solc_data.get('evm_version'),
                allow_paths=solc_data.get('allow_paths', [])
            )
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'max_file_size_mb': self.max_file_size_mb,
            'timeout_seconds': self.timeout_seconds,
            'include_test_files': self.include_test_files,
            'min_severity': self.min_severity,
            'exclude_severities': self.exclude_severities,
            'include_patterns': self.include_patterns,
            'exclude_patterns': self.exclude_patterns,
            'detectors': {
                name: {
                    'enabled': detector.enabled,
                    'severity_override': detector.severity_override,
                    'custom_params': detector.custom_params
                }
                for name, detector in self.detectors.items()
            },
            'output': {
                'format': self.output.format,
                'output_file': self.output.output_file,
                'include_code_snippets': self.output.include_code_snippets,
                'max_snippet_lines': self.output.max_snippet_lines,
                'color_output': self.output.color_output,
                'verbose': self.output.verbose
            },
            'solc': {
                'version': self.solc.version,
                'optimize': self.solc.optimize,
                'optimize_runs': self.solc.optimize_runs,
                'evm_version': self.solc.evm_version,
                'allow_paths': self.solc.allow_paths
            }
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to YAML file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
    
    @classmethod
    def get_default_config_path(cls) -> str:
        """Get the default configuration file path."""
        return os.path.join(os.getcwd(), "contractquard.yaml")
    
    def is_detector_enabled(self, detector_name: str) -> bool:
        """Check if a detector is enabled."""
        if detector_name in self.detectors:
            return self.detectors[detector_name].enabled
        return True  # Default to enabled if not specified
    
    def get_detector_config(self, detector_name: str) -> DetectorConfig:
        """Get configuration for a specific detector."""
        return self.detectors.get(detector_name, DetectorConfig())
