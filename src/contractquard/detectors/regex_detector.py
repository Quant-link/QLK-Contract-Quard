"""
Regex-based vulnerability detector for ContractQuard.

This detector uses regular expressions to identify common vulnerability
patterns and code smells in Solidity source code.
"""

import re
from typing import Dict, Optional, List

from ..core.findings import Severity, SourceLocation
from .base import RegexDetector, Finding


class RegexVulnerabilityDetector(RegexDetector):
    """
    Regex-based detector for common Solidity vulnerabilities and code smells.
    
    This detector searches for textual patterns that indicate potential
    security issues or deviations from best practices.
    """
    
    @property
    def name(self) -> str:
        return "regex_detector"
    
    @property
    def description(self) -> str:
        return "Detects common vulnerability patterns using regular expressions"
    
    @property
    def vulnerability_types(self) -> List[str]:
        return [
            "deprecated_constructs",
            "dangerous_functions",
            "weak_randomness",
            "tx_origin_usage",
            "timestamp_dependence",
            "hardcoded_addresses",
            "floating_pragma",
            "unsafe_math",
            "todo_fixme_comments"
        ]
    
    @property
    def default_severity(self) -> Severity:
        return Severity.MEDIUM
    
    @property
    def patterns(self) -> Dict[str, str]:
        """
        Define regex patterns for vulnerability detection.
        
        Returns:
            Dictionary mapping pattern names to regex strings.
        """
        return {
            # Deprecated and dangerous constructs
            "deprecated_throw": r'\bthrow\b',
            "deprecated_suicide": r'\bsuicide\b',
            "deprecated_sha3": r'\bsha3\b',
            "deprecated_callcode": r'\.callcode\b',
            "selfdestruct_usage": r'\bselfdestruct\b',
            
            # Dangerous authorization patterns
            "tx_origin_auth": r'tx\.origin\s*==|require\s*\(\s*tx\.origin',
            "msg_sender_auth": r'tx\.origin\s*==\s*msg\.sender',
            
            # Timestamp dependence
            "block_timestamp": r'\b(block\.timestamp|now)\b',
            "block_number_time": r'\bblock\.number\b.*\b(time|delay|period)\b',
            
            # Weak randomness
            "weak_randomness": r'\b(block\.timestamp|block\.difficulty|block\.number|blockhash)\b.*\b(random|rand)\b',
            "blockhash_randomness": r'\bblockhash\b.*\b(random|rand)\b',
            
            # Hardcoded addresses (basic pattern)
            "hardcoded_address": r'0x[a-fA-F0-9]{40}',
            
            # Floating pragma
            "floating_pragma": r'pragma\s+solidity\s*\^',
            
            # Unsafe math operations (pre-0.8.0)
            "unchecked_math": r'(\+\+|--|\+=|-=|\*=|/=|%=)',
            
            # Gas limit issues
            "transfer_send": r'\.(transfer|send)\s*\(',
            
            # TODO/FIXME comments indicating known issues
            "todo_security": r'(TODO|FIXME|XXX|HACK).*\b(security|vuln|exploit|attack|fix)\b',
            "security_todo": r'\b(security|vuln|exploit|attack|fix)\b.*(TODO|FIXME|XXX|HACK)',
            
            # Assembly usage (potentially dangerous)
            "inline_assembly": r'\bassembly\s*\{',
            
            # Unchecked external calls (basic pattern)
            "unchecked_call": r'\.call\s*\([^)]*\)\s*;',
            "unchecked_delegatecall": r'\.delegatecall\s*\([^)]*\)\s*;',
            
            # Reentrancy patterns (basic)
            "external_call_pattern": r'\.call\{value:\s*\w+\}',
            
            # Access control issues
            "missing_modifier": r'function\s+\w+\s*\([^)]*\)\s*(public|external)(?!.*\b(onlyOwner|onlyAdmin|require)\b)',
        }
    
    def _create_regex_finding(
        self,
        pattern_name: str,
        match: re.Match,
        line_num: int,
        line_content: str,
        source_code: str,
        file_path: str
    ) -> Optional[Finding]:
        """
        Create a finding from a regex match.
        
        Args:
            pattern_name: Name of the matched pattern.
            match: The regex match object.
            line_num: Line number of the match.
            line_content: Content of the matched line.
            source_code: Full source code.
            file_path: Path to the source file.
            
        Returns:
            A Finding object or None if no finding should be created.
        """
        # Skip matches in comments (basic check)
        if line_content.strip().startswith('//') or line_content.strip().startswith('*'):
            return None
        
        # Get pattern-specific information
        finding_info = self._get_finding_info(pattern_name, match.group())
        
        if not finding_info:
            return None
        
        location = SourceLocation(
            file_path=file_path,
            line_start=line_num,
            column_start=match.start() + 1,
            column_end=match.end() + 1
        )
        
        code_snippet = self.extract_code_snippet(source_code, line_num)
        
        return self.create_finding(
            title=finding_info["title"],
            description=finding_info["description"],
            location=location,
            vulnerability_type=finding_info["vulnerability_type"],
            severity=finding_info.get("severity", self.default_severity),
            confidence=finding_info.get("confidence", 0.7),
            code_snippet=code_snippet,
            recommendation=finding_info.get("recommendation"),
            references=finding_info.get("references", [])
        )
    
    def _get_finding_info(self, pattern_name: str, matched_text: str) -> Optional[Dict]:
        """
        Get finding information for a specific pattern match.
        
        Args:
            pattern_name: Name of the matched pattern.
            matched_text: The actual matched text.
            
        Returns:
            Dictionary with finding information or None.
        """
        finding_info = {
            "deprecated_throw": {
                "title": "Deprecated 'throw' Statement",
                "description": "The 'throw' statement is deprecated. Use 'require()' or 'revert()' instead.",
                "vulnerability_type": "deprecated_constructs",
                "severity": Severity.LOW,
                "recommendation": "Replace 'throw' with 'require(condition)' or 'revert(\"message\")'",
                "references": ["https://docs.soliditylang.org/en/latest/control-structures.html#error-handling"]
            },
            
            "deprecated_suicide": {
                "title": "Deprecated 'suicide' Function",
                "description": "The 'suicide' function is deprecated. Use 'selfdestruct' instead.",
                "vulnerability_type": "deprecated_constructs",
                "severity": Severity.LOW,
                "recommendation": "Replace 'suicide' with 'selfdestruct'",
            },
            
            "tx_origin_auth": {
                "title": "tx.origin Used for Authorization",
                "description": "Using tx.origin for authorization is vulnerable to phishing attacks.",
                "vulnerability_type": "tx_origin_usage",
                "severity": Severity.HIGH,
                "confidence": 0.9,
                "recommendation": "Use msg.sender instead of tx.origin for authorization checks",
                "references": ["https://consensys.github.io/smart-contract-best-practices/attacks/tx-origin/"]
            },
            
            "block_timestamp": {
                "title": "Block Timestamp Dependence",
                "description": "Relying on block.timestamp or 'now' can be manipulated by miners.",
                "vulnerability_type": "timestamp_dependence",
                "severity": Severity.MEDIUM,
                "recommendation": "Avoid using block.timestamp for critical logic or use block numbers instead",
                "references": ["https://consensys.github.io/smart-contract-best-practices/attacks/timestamp-dependence/"]
            },
            
            "weak_randomness": {
                "title": "Weak Source of Randomness",
                "description": "Using block properties for randomness is predictable and can be manipulated.",
                "vulnerability_type": "weak_randomness",
                "severity": Severity.HIGH,
                "recommendation": "Use a secure randomness source like Chainlink VRF or commit-reveal schemes",
                "references": ["https://consensys.github.io/smart-contract-best-practices/attacks/randomness/"]
            },
            
            "hardcoded_address": {
                "title": "Hardcoded Address",
                "description": "Hardcoded addresses reduce contract flexibility and may indicate configuration issues.",
                "vulnerability_type": "hardcoded_addresses",
                "severity": Severity.LOW,
                "confidence": 0.5,  # Many false positives possible
                "recommendation": "Consider using configurable addresses or constants with clear documentation"
            },
            
            "floating_pragma": {
                "title": "Floating Pragma",
                "description": "Floating pragma allows compilation with different compiler versions.",
                "vulnerability_type": "floating_pragma",
                "severity": Severity.INFO,
                "recommendation": "Lock pragma to a specific compiler version for production contracts"
            },
            
            "transfer_send": {
                "title": "Use of transfer() or send()",
                "description": "transfer() and send() have a fixed gas limit that may cause failures.",
                "vulnerability_type": "dangerous_functions",
                "severity": Severity.MEDIUM,
                "recommendation": "Use call{value: amount}(\"\") with proper checks instead",
                "references": ["https://consensys.github.io/smart-contract-best-practices/attacks/denial-of-service/#gas-limit-dos-on-the-network-via-block-stuffing"]
            },
            
            "todo_security": {
                "title": "Security-Related TODO/FIXME Comment",
                "description": "Found a TODO/FIXME comment related to security that may indicate unresolved issues.",
                "vulnerability_type": "todo_fixme_comments",
                "severity": Severity.MEDIUM,
                "recommendation": "Review and resolve security-related TODO/FIXME comments before deployment"
            },
            
            "inline_assembly": {
                "title": "Inline Assembly Usage",
                "description": "Inline assembly bypasses Solidity's safety features and should be used carefully.",
                "vulnerability_type": "dangerous_functions",
                "severity": Severity.MEDIUM,
                "confidence": 0.6,
                "recommendation": "Ensure assembly code is thoroughly reviewed and tested"
            },
            
            "unchecked_call": {
                "title": "Unchecked External Call",
                "description": "External call result is not checked, which may lead to silent failures.",
                "vulnerability_type": "dangerous_functions",
                "severity": Severity.HIGH,
                "recommendation": "Check the return value of external calls and handle failures appropriately"
            },
            
            "selfdestruct_usage": {
                "title": "selfdestruct Usage",
                "description": "selfdestruct can be dangerous if not properly protected.",
                "vulnerability_type": "dangerous_functions",
                "severity": Severity.HIGH,
                "recommendation": "Ensure selfdestruct is properly protected with access controls"
            }
        }
        
        return finding_info.get(pattern_name)
