"""
Detector registry for ContractQuard Static Analyzer.

This module manages the registration and instantiation of all vulnerability detectors.
"""

import logging
from typing import List, Dict, Type, Optional

from ..core.config import Config, DetectorConfig
from .base import BaseDetector


class DetectorRegistry:
    """
    Registry for managing vulnerability detectors.
    
    This class handles the registration, configuration, and instantiation
    of all available detectors.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the detector registry.
        
        Args:
            config: Global configuration object.
        """
        self.config = config
        self.logger = logging.getLogger("contractquard.registry")
        self._detector_classes: Dict[str, Type[BaseDetector]] = {}
        self._detector_instances: Dict[str, BaseDetector] = {}
        
        # Register built-in detectors
        self._register_builtin_detectors()
    
    def _register_builtin_detectors(self) -> None:
        """Register all built-in detectors."""
        try:
            # Import and register regex-based detectors
            from .regex_detector import RegexVulnerabilityDetector
            self.register_detector("regex_detector", RegexVulnerabilityDetector)
            
            # Import and register AST-based detectors
            from .ast_reentrancy import ReentrancyDetector
            self.register_detector("ast_reentrancy_detector", ReentrancyDetector)
            
            from .ast_access_control import AccessControlDetector
            self.register_detector("ast_access_control_detector", AccessControlDetector)
            
            from .ast_unchecked_calls import UncheckedCallsDetector
            self.register_detector("ast_unchecked_calls_detector", UncheckedCallsDetector)
            
            self.logger.info(f"Registered {len(self._detector_classes)} built-in detectors")
            
        except ImportError as e:
            self.logger.warning(f"Could not import some detectors: {e}")
    
    def register_detector(self, name: str, detector_class: Type[BaseDetector]) -> None:
        """
        Register a detector class.
        
        Args:
            name: Unique name for the detector.
            detector_class: The detector class to register.
        """
        if not issubclass(detector_class, BaseDetector):
            raise ValueError(f"Detector class must inherit from BaseDetector: {detector_class}")
        
        self._detector_classes[name] = detector_class
        self.logger.debug(f"Registered detector: {name}")
    
    def get_detector_config(self, detector_name: str) -> DetectorConfig:
        """
        Get configuration for a specific detector.
        
        Args:
            detector_name: Name of the detector.
            
        Returns:
            DetectorConfig for the specified detector.
        """
        return self.config.get_detector_config(detector_name)
    
    def create_detector(self, detector_name: str) -> Optional[BaseDetector]:
        """
        Create an instance of a detector.
        
        Args:
            detector_name: Name of the detector to create.
            
        Returns:
            Detector instance or None if not found/disabled.
        """
        if detector_name not in self._detector_classes:
            self.logger.warning(f"Unknown detector: {detector_name}")
            return None
        
        # Check if detector is enabled
        if not self.config.is_detector_enabled(detector_name):
            self.logger.debug(f"Detector disabled: {detector_name}")
            return None
        
        # Create instance if not already cached
        if detector_name not in self._detector_instances:
            detector_config = self.get_detector_config(detector_name)
            detector_class = self._detector_classes[detector_name]
            
            try:
                detector_instance = detector_class(detector_config)
                self._detector_instances[detector_name] = detector_instance
                self.logger.debug(f"Created detector instance: {detector_name}")
            except Exception as e:
                self.logger.error(f"Failed to create detector {detector_name}: {e}")
                return None
        
        return self._detector_instances[detector_name]
    
    def get_enabled_detectors(self) -> List[BaseDetector]:
        """
        Get all enabled detector instances.
        
        Returns:
            List of enabled detector instances.
        """
        detectors = []
        
        for detector_name in self._detector_classes.keys():
            detector = self.create_detector(detector_name)
            if detector and detector.enabled:
                detectors.append(detector)
        
        return detectors
    
    def get_all_detectors(self) -> List[BaseDetector]:
        """
        Get all detector instances (enabled and disabled).
        
        Returns:
            List of all detector instances.
        """
        detectors = []
        
        for detector_name in self._detector_classes.keys():
            # Temporarily enable to create instance
            original_enabled = self.config.is_detector_enabled(detector_name)
            
            # Force creation by temporarily enabling
            if detector_name not in self.config.detectors:
                self.config.detectors[detector_name] = DetectorConfig(enabled=True)
            else:
                self.config.detectors[detector_name].enabled = True
            
            detector = self.create_detector(detector_name)
            if detector:
                # Restore original enabled state
                detector.enabled = original_enabled
                detectors.append(detector)
            
            # Restore configuration
            if original_enabled:
                self.config.detectors[detector_name].enabled = True
            else:
                self.config.detectors[detector_name].enabled = False
        
        return detectors
    
    def get_detector_by_name(self, detector_name: str) -> Optional[BaseDetector]:
        """
        Get a specific detector by name.
        
        Args:
            detector_name: Name of the detector.
            
        Returns:
            Detector instance or None if not found.
        """
        return self.create_detector(detector_name)
    
    def list_available_detectors(self) -> List[str]:
        """
        List all available detector names.
        
        Returns:
            List of detector names.
        """
        return list(self._detector_classes.keys())
    
    def get_detectors_by_vulnerability_type(self, vulnerability_type: str) -> List[BaseDetector]:
        """
        Get all detectors that can find a specific vulnerability type.
        
        Args:
            vulnerability_type: The vulnerability type to search for.
            
        Returns:
            List of detectors that can find this vulnerability type.
        """
        matching_detectors = []
        
        for detector in self.get_enabled_detectors():
            if vulnerability_type in detector.vulnerability_types:
                matching_detectors.append(detector)
        
        return matching_detectors
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the detector configuration.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        # Check for unknown detectors in configuration
        for detector_name in self.config.detectors.keys():
            if detector_name not in self._detector_classes:
                errors.append(f"Unknown detector in configuration: {detector_name}")
        
        # Check for invalid severity overrides
        valid_severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        for detector_name, detector_config in self.config.detectors.items():
            if (detector_config.severity_override and 
                detector_config.severity_override not in valid_severities):
                errors.append(
                    f"Invalid severity override for {detector_name}: "
                    f"{detector_config.severity_override}"
                )
        
        return errors
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about registered detectors.
        
        Returns:
            Dictionary with detector statistics.
        """
        all_detectors = self.get_all_detectors()
        enabled_detectors = [d for d in all_detectors if d.enabled]
        
        # Count by vulnerability types
        vulnerability_types = set()
        for detector in all_detectors:
            vulnerability_types.update(detector.vulnerability_types)
        
        return {
            "total_detectors": len(all_detectors),
            "enabled_detectors": len(enabled_detectors),
            "disabled_detectors": len(all_detectors) - len(enabled_detectors),
            "vulnerability_types_covered": len(vulnerability_types)
        }
