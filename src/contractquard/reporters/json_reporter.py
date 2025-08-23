"""
JSON reporter for ContractQuard Static Analyzer.
"""

import json
from typing import List, Dict, Any
from datetime import datetime

from ..core.findings import Finding
from .base import BaseReporter


class JSONReporter(BaseReporter):
    """
    JSON reporter that outputs findings in structured JSON format
    suitable for machine processing and integration with other tools.
    """
    
    @property
    def format_name(self) -> str:
        return "json"
    
    def generate_report(self, findings: List[Finding]) -> str:
        """
        Generate a JSON report from findings.
        
        Args:
            findings: List of findings to report.
            
        Returns:
            JSON formatted report.
        """
        # Generate summary
        summary = self.generate_summary(findings)
        
        # Convert findings to dictionaries
        findings_data = []
        for finding in findings:
            finding_dict = finding.to_dict()
            
            # Optionally truncate code snippet
            if (finding_dict.get('code_snippet') and 
                not self.include_code_snippets):
                finding_dict['code_snippet'] = None
            elif finding_dict.get('code_snippet'):
                finding_dict['code_snippet'] = self.truncate_code_snippet(
                    finding_dict['code_snippet']
                )
            
            findings_data.append(finding_dict)
        
        # Build complete report structure
        report = {
            "contractquard_version": "0.1.0",
            "report_format": "json",
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "findings": findings_data,
            "metadata": {
                "total_findings": len(findings),
                "analysis_complete": True,
                "report_config": {
                    "include_code_snippets": self.include_code_snippets,
                    "max_snippet_lines": self.max_snippet_lines
                }
            }
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)


class SARIFReporter(BaseReporter):
    """
    SARIF (Static Analysis Results Interchange Format) reporter.
    
    SARIF is a standard format for static analysis tool output that
    is supported by many IDEs and CI/CD platforms.
    """
    
    @property
    def format_name(self) -> str:
        return "sarif"
    
    def generate_report(self, findings: List[Finding]) -> str:
        """
        Generate a SARIF report from findings.
        
        Args:
            findings: List of findings to report.
            
        Returns:
            SARIF formatted report.
        """
        # Build SARIF structure
        sarif_report = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "ContractQuard",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/quantlink/contractquard",
                            "organization": "QuantLink",
                            "shortDescription": {
                                "text": "AI-augmented smart contract security analysis tool"
                            },
                            "fullDescription": {
                                "text": "ContractQuard is QuantLink's AI-augmented smart contract security analysis tool that provides foundational static analysis capabilities for Solidity smart contracts."
                            },
                            "rules": self._generate_sarif_rules(findings)
                        }
                    },
                    "results": self._generate_sarif_results(findings),
                    "columnKind": "utf16CodeUnits"
                }
            ]
        }
        
        return json.dumps(sarif_report, indent=2, ensure_ascii=False)
    
    def _generate_sarif_rules(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """Generate SARIF rules from findings."""
        # Collect unique vulnerability types
        vulnerability_types = set(f.vulnerability_type for f in findings)
        
        rules = []
        for vuln_type in vulnerability_types:
            # Find a representative finding for this vulnerability type
            representative = next(f for f in findings if f.vulnerability_type == vuln_type)
            
            rule = {
                "id": vuln_type,
                "name": vuln_type.replace('_', ' ').title(),
                "shortDescription": {
                    "text": representative.title
                },
                "fullDescription": {
                    "text": representative.description
                },
                "defaultConfiguration": {
                    "level": self._severity_to_sarif_level(representative.severity)
                },
                "helpUri": representative.references[0] if representative.references else None,
                "properties": {
                    "category": "security",
                    "detector": representative.detector_name
                }
            }
            
            # Remove None values
            rule = {k: v for k, v in rule.items() if v is not None}
            rules.append(rule)
        
        return rules
    
    def _generate_sarif_results(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """Generate SARIF results from findings."""
        results = []
        
        for finding in findings:
            result = {
                "ruleId": finding.vulnerability_type,
                "ruleIndex": 0,  # Would need to map to actual rule index
                "message": {
                    "text": finding.description
                },
                "level": self._severity_to_sarif_level(finding.severity),
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": finding.location.file_path
                            },
                            "region": {
                                "startLine": finding.location.line_start,
                                "endLine": finding.location.line_end or finding.location.line_start,
                                "startColumn": finding.location.column_start or 1,
                                "endColumn": finding.location.column_end or 1
                            }
                        }
                    }
                ],
                "properties": {
                    "confidence": finding.confidence,
                    "detector": finding.detector_name,
                    "vulnerability_type": finding.vulnerability_type
                }
            }
            
            # Add code snippet if available
            if finding.code_snippet and self.include_code_snippets:
                result["locations"][0]["physicalLocation"]["contextRegion"] = {
                    "snippet": {
                        "text": self.truncate_code_snippet(finding.code_snippet)
                    }
                }
            
            results.append(result)
        
        return results
    
    def _severity_to_sarif_level(self, severity) -> str:
        """Convert ContractQuard severity to SARIF level."""
        from ..core.findings import Severity
        
        mapping = {
            Severity.CRITICAL: "error",
            Severity.HIGH: "error", 
            Severity.MEDIUM: "warning",
            Severity.LOW: "note",
            Severity.INFO: "note"
        }
        
        return mapping.get(severity, "warning")
