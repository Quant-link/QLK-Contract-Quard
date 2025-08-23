"""
Factory for creating appropriate analyzers based on file type
"""

from typing import Optional, Dict, List
from .base import BaseAnalyzer
from .solidity_analyzer import SolidityAnalyzer
from .rust_analyzer import RustAnalyzer
from .go_analyzer import GoAnalyzer

class AnalyzerFactory:
    """Factory class for creating analyzers based on file extension"""
    
    def __init__(self):
        self._analyzers: Dict[str, BaseAnalyzer] = {
            'sol': SolidityAnalyzer(),
            'rs': RustAnalyzer(),
            'go': GoAnalyzer()
        }
    
    def get_analyzer(self, file_extension: str) -> Optional[BaseAnalyzer]:
        """
        Get appropriate analyzer for file extension
        
        Args:
            file_extension: File extension (e.g., 'sol', 'rs', 'go')
            
        Returns:
            Analyzer instance or None if not supported
        """
        return self._analyzers.get(file_extension.lower())
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions"""
        return list(self._analyzers.keys())
    
    def is_supported(self, file_extension: str) -> bool:
        """Check if file extension is supported"""
        return file_extension.lower() in self._analyzers
    
    def get_analyzer_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all available analyzers"""
        info = {}
        for ext, analyzer in self._analyzers.items():
            info[ext] = {
                'name': analyzer.name,
                'version': analyzer.version,
                'extensions': analyzer.get_supported_extensions()
            }
        return info

# Global factory instance
analyzer_factory = AnalyzerFactory()
