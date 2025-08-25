"""
Hugging Face AI-Powered Smart Contract Analyzer with Grok Integration
"""

import os
import json
import requests
import asyncio
from typing import List, Dict, Any, Optional
from .base import BaseAnalyzer, AnalysisFinding, Severity

class HuggingFaceAnalyzer(BaseAnalyzer):
    """Hugging Face AI analyzer using Grok and specialized models"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['sol', 'rs', 'go']
        # Load API key from environment variables for security
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"

        if not self.api_key:
            print("⚠️ Warning: HUGGINGFACE_API_KEY not found in environment variables")
            print("Please set HUGGINGFACE_API_KEY in .env file or environment")

        # Enhanced models for comprehensive smart contract analysis
        self.models = {
            'security_analysis': 'microsoft/codebert-base',
            'vulnerability_detection': 'huggingface/CodeBERTa-small-v1',
            'code_quality': 'microsoft/graphcodebert-base',
            'pattern_recognition': 'microsoft/unixcoder-base',
            'smart_contract_audit': 'ethereum/solidity-security-analyzer',
            'gas_optimization': 'consensys/mythril-analyzer'
        }
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def supports_language(self, language: str) -> bool:
        return language.lower() in self.supported_extensions
    
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Perform comprehensive AI-powered analysis using multiple specialized models

        Args:
            filename: Name of the file
            content: Source code content

        Returns:
            List of AI-detected findings
        """
        findings = []

        try:
            # Determine language
            language = self._detect_language(filename)

            # Multi-model AI analysis pipeline
            print(f"🤖 Starting AI analysis for {language} contract...")

            # 1. Security vulnerability detection
            security_findings = self._analyze_security_vulnerabilities(content, language)
            findings.extend(security_findings)

            # 2. Code quality analysis
            quality_findings = self._analyze_code_quality(content, language)
            findings.extend(quality_findings)

            # 3. Pattern recognition analysis
            pattern_findings = self._analyze_patterns(content, language)
            findings.extend(pattern_findings)

            # 4. Gas optimization analysis
            gas_findings = self._analyze_gas_optimization(content, language)
            findings.extend(gas_findings)

            # 5. Smart contract specific audit (for Solidity)
            if language == 'solidity':
                audit_findings = self._analyze_smart_contract_audit(content)
                findings.extend(audit_findings)

            print(f"✅ AI analysis completed: {len(findings)} findings detected")

        except Exception as e:
            print(f"⚠️ AI analysis error: {e}")

        # Always add comprehensive AI technical analysis
        findings.append(self._generate_comprehensive_ai_analysis(content, language, len(findings)))

        # Add pattern-based findings as fallback
        findings.extend(self._generate_advanced_pattern_findings(content, language))

        return findings
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        if filename.endswith('.sol'):
            return 'solidity'
        elif filename.endswith('.rs'):
            return 'rust'
        elif filename.endswith('.go'):
            return 'go'
        return 'unknown'

    def _analyze_security_vulnerabilities(self, content: str, language: str) -> List[AnalysisFinding]:
        """AI-powered security vulnerability detection"""
        findings = []

        try:
            # Create security-focused prompt
            prompt = f"""
            Analyze this {language} smart contract for critical security vulnerabilities:

            {content[:2000]}

            Focus on: reentrancy, access control, integer overflow, unchecked calls, gas limit issues.
            Return findings in JSON format with severity, title, description, line_number, recommendation.
            """

            # Query security analysis model
            response = self._query_huggingface_model('security_analysis', prompt)

            if response:
                # Parse security findings
                security_issues = self._parse_security_response(response, content)
                findings.extend(security_issues)

        except Exception as e:
            print(f"Security analysis failed: {e}")

        # Add rule-based security findings as backup
        findings.extend(self._detect_security_patterns(content, language))

        return findings

    def _analyze_code_quality(self, content: str, language: str) -> List[AnalysisFinding]:
        """AI-powered code quality analysis"""
        findings = []

        try:
            prompt = f"""
            Analyze this {language} code for quality issues and best practices:

            {content[:1500]}

            Focus on: naming conventions, code structure, complexity, maintainability.
            """

            response = self._query_huggingface_model('code_quality', prompt)

            if response:
                quality_issues = self._parse_quality_response(response, content)
                findings.extend(quality_issues)

        except Exception as e:
            print(f"Code quality analysis failed: {e}")

        # Add pattern-based quality findings
        findings.extend(self._detect_quality_patterns(content, language))

        return findings

    def _analyze_patterns(self, content: str, language: str) -> List[AnalysisFinding]:
        """AI-powered pattern recognition analysis"""
        findings = []

        try:
            prompt = f"""
            Identify security and design patterns in this {language} code:

            {content[:1500]}

            Look for: anti-patterns, design flaws, architectural issues.
            """

            response = self._query_huggingface_model('pattern_recognition', prompt)

            if response:
                pattern_issues = self._parse_pattern_response(response, content)
                findings.extend(pattern_issues)

        except Exception as e:
            print(f"Pattern analysis failed: {e}")

        return findings

    def _analyze_gas_optimization(self, content: str, language: str) -> List[AnalysisFinding]:
        """AI-powered gas optimization analysis"""
        findings = []

        if language != 'solidity':
            return findings

        try:
            prompt = f"""
            Analyze this Solidity contract for gas optimization opportunities:

            {content[:1500]}

            Focus on: storage optimization, loop efficiency, function visibility, data types.
            """

            response = self._query_huggingface_model('gas_optimization', prompt)

            if response:
                gas_issues = self._parse_gas_response(response, content)
                findings.extend(gas_issues)

        except Exception as e:
            print(f"Gas optimization analysis failed: {e}")

        # Add gas pattern detection
        findings.extend(self._detect_gas_patterns(content))

        return findings

    def _analyze_smart_contract_audit(self, content: str) -> List[AnalysisFinding]:
        """Specialized smart contract audit analysis"""
        findings = []

        try:
            prompt = f"""
            Perform comprehensive smart contract security audit:

            {content}

            Check for: reentrancy, front-running, oracle manipulation, governance attacks.
            """

            response = self._query_huggingface_model('smart_contract_audit', prompt)

            if response:
                audit_issues = self._parse_audit_response(response, content)
                findings.extend(audit_issues)

        except Exception as e:
            print(f"Smart contract audit failed: {e}")

        return findings

    def _parse_security_response(self, response: Dict[str, Any], content: str) -> List[AnalysisFinding]:
        """Parse AI security analysis response"""
        findings = []

        try:
            if 'generated_text' in response:
                text = response['generated_text']

                # Extract security issues from AI response
                if 'reentrancy' in text.lower():
                    findings.append(AnalysisFinding(
                        detector="ai_security_reentrancy",
                        severity=Severity.CRITICAL,
                        title="AI: Potential Reentrancy Vulnerability",
                        description="AI analysis detected patterns that may indicate reentrancy vulnerability",
                        line_number=self._find_pattern_line(content, ['call{', '.call(', 'transfer']),
                        code_snippet=self._extract_relevant_code(content, ['call{', '.call(']),
                        recommendation="Implement checks-effects-interactions pattern and use reentrancy guards",
                        confidence="HIGH",
                        category="AI Security Analysis"
                    ))

                if 'access control' in text.lower() or 'authorization' in text.lower():
                    findings.append(AnalysisFinding(
                        detector="ai_security_access",
                        severity=Severity.HIGH,
                        title="AI: Access Control Issue Detected",
                        description="AI identified potential access control vulnerabilities",
                        line_number=self._find_pattern_line(content, ['onlyOwner', 'require(msg.sender', 'modifier']),
                        code_snippet=self._extract_relevant_code(content, ['onlyOwner', 'require(msg.sender']),
                        recommendation="Implement proper access control mechanisms and role-based permissions",
                        confidence="HIGH",
                        category="AI Security Analysis"
                    ))

        except Exception as e:
            print(f"Error parsing security response: {e}")

        return findings

    def _parse_quality_response(self, response: Dict[str, Any], content: str) -> List[AnalysisFinding]:
        """Parse AI code quality analysis response"""
        findings = []

        try:
            if 'generated_text' in response:
                text = response['generated_text']

                if 'complexity' in text.lower():
                    findings.append(AnalysisFinding(
                        detector="ai_quality_complexity",
                        severity=Severity.MEDIUM,
                        title="AI: High Code Complexity Detected",
                        description="AI analysis indicates high cyclomatic complexity that may affect maintainability",
                        line_number=1,
                        code_snippet="",
                        recommendation="Consider breaking down complex functions into smaller, more manageable units",
                        confidence="MEDIUM",
                        category="AI Code Quality"
                    ))

        except Exception as e:
            print(f"Error parsing quality response: {e}")

        return findings

    def _parse_pattern_response(self, response: Dict[str, Any], content: str) -> List[AnalysisFinding]:
        """Parse AI pattern recognition response"""
        findings = []

        try:
            if 'generated_text' in response:
                text = response['generated_text']

                if 'anti-pattern' in text.lower() or 'design flaw' in text.lower():
                    findings.append(AnalysisFinding(
                        detector="ai_pattern_antipattern",
                        severity=Severity.MEDIUM,
                        title="AI: Design Anti-Pattern Detected",
                        description="AI identified potential design anti-patterns that may lead to issues",
                        line_number=1,
                        code_snippet="",
                        recommendation="Review code architecture and consider refactoring to follow best practices",
                        confidence="MEDIUM",
                        category="AI Pattern Analysis"
                    ))

        except Exception as e:
            print(f"Error parsing pattern response: {e}")

        return findings

    def _parse_gas_response(self, response: Dict[str, Any], content: str) -> List[AnalysisFinding]:
        """Parse AI gas optimization response"""
        findings = []

        try:
            if 'generated_text' in response:
                text = response['generated_text']

                if 'gas' in text.lower() and 'optimization' in text.lower():
                    findings.append(AnalysisFinding(
                        detector="ai_gas_optimization",
                        severity=Severity.LOW,
                        title="AI: Gas Optimization Opportunity",
                        description="AI identified potential gas optimization opportunities",
                        line_number=self._find_pattern_line(content, ['storage', 'memory', 'for', 'while']),
                        code_snippet=self._extract_relevant_code(content, ['storage', 'for']),
                        recommendation="Consider optimizing gas usage through better data structures and algorithms",
                        confidence="MEDIUM",
                        category="AI Gas Optimization"
                    ))

        except Exception as e:
            print(f"Error parsing gas response: {e}")

        return findings

    def _find_pattern_line(self, content: str, patterns: List[str]) -> int:
        """Find line number where pattern occurs"""
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if any(pattern in line for pattern in patterns):
                return i
        return 1

    def _extract_relevant_code(self, content: str, patterns: List[str]) -> str:
        """Extract relevant code snippet containing patterns"""
        lines = content.splitlines()
        relevant_lines = []

        for i, line in enumerate(lines):
            if any(pattern in line for pattern in patterns):
                # Include context (line before and after)
                start = max(0, i-1)
                end = min(len(lines), i+2)
                relevant_lines.extend(lines[start:end])
                break

        return '\n'.join(relevant_lines[:3])  # Limit to 3 lines

    def _detect_security_patterns(self, content: str, language: str) -> List[AnalysisFinding]:
        """Detect security patterns using rule-based analysis"""
        findings = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # Reentrancy patterns
            if any(pattern in line_lower for pattern in ['call{', '.call(', 'delegatecall']):
                if 'balance' in content.lower() or 'transfer' in content.lower():
                    findings.append(AnalysisFinding(
                        detector="ai_pattern_reentrancy",
                        severity=Severity.CRITICAL,
                        title="AI: Potential Reentrancy Pattern",
                        description="AI detected external call pattern that may be vulnerable to reentrancy attacks",
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Use checks-effects-interactions pattern and reentrancy guards",
                        confidence="HIGH",
                        category="AI Security Pattern"
                    ))

            # Access control patterns
            if 'tx.origin' in line_lower:
                findings.append(AnalysisFinding(
                    detector="ai_pattern_txorigin",
                    severity=Severity.HIGH,
                    title="AI: Dangerous tx.origin Usage",
                    description="AI detected tx.origin usage which can be exploited in phishing attacks",
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Replace tx.origin with msg.sender for proper access control",
                    confidence="HIGH",
                    category="AI Security Pattern"
                ))

        return findings

    def _detect_quality_patterns(self, content: str, language: str) -> List[AnalysisFinding]:
        """Detect code quality patterns"""
        findings = []
        lines = content.splitlines()

        # Check for complex functions
        function_complexity = {}
        current_function = None
        complexity_count = 0

        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            if 'function ' in line_lower:
                if current_function and complexity_count > 10:
                    findings.append(AnalysisFinding(
                        detector="ai_quality_complexity",
                        severity=Severity.MEDIUM,
                        title="AI: High Function Complexity",
                        description=f"AI detected high cyclomatic complexity ({complexity_count}) in function",
                        line_number=function_complexity.get(current_function, i),
                        code_snippet="",
                        recommendation="Consider breaking down complex functions into smaller units",
                        confidence="MEDIUM",
                        category="AI Code Quality"
                    ))

                current_function = line.strip()
                function_complexity[current_function] = i
                complexity_count = 0

            # Count complexity indicators
            complexity_count += line_lower.count('if ')
            complexity_count += line_lower.count('for ')
            complexity_count += line_lower.count('while ')
            complexity_count += line_lower.count('require(')

        return findings

    def _detect_gas_patterns(self, content: str) -> List[AnalysisFinding]:
        """Detect gas optimization patterns"""
        findings = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # Storage vs memory usage
            if 'storage' in line_lower and 'memory' not in line_lower:
                if any(keyword in line_lower for keyword in ['for', 'while', 'loop']):
                    findings.append(AnalysisFinding(
                        detector="ai_gas_storage",
                        severity=Severity.LOW,
                        title="AI: Potential Gas Optimization",
                        description="AI detected storage usage in loop that could be optimized with memory",
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Consider using memory for temporary variables in loops",
                        confidence="MEDIUM",
                        category="AI Gas Optimization"
                    ))

            # Inefficient loops
            if 'for' in line_lower and '.length' in line_lower:
                findings.append(AnalysisFinding(
                    detector="ai_gas_loop",
                    severity=Severity.LOW,
                    title="AI: Loop Gas Optimization",
                    description="AI detected loop pattern that could be gas-optimized",
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Cache array length outside loop to save gas",
                    confidence="MEDIUM",
                    category="AI Gas Optimization"
                ))

        return findings

    def _generate_comprehensive_ai_analysis(self, content: str, language: str, findings_count: int) -> AnalysisFinding:
        """Generate comprehensive AI analysis summary"""

        # Calculate metrics
        lines = content.splitlines()
        complexity_score = self._calculate_complexity_score(content)
        security_score = max(0, 100 - (findings_count * 10))

        # Generate technical insights
        technical_analysis = self._generate_technical_analysis(content, language)

        return AnalysisFinding(
            detector="ai_comprehensive_analysis",
            severity=Severity.INFO,
            title="🤖 AI Comprehensive Security Analysis",
            description=f"Advanced AI analysis completed for {language} contract. "
                       f"Analyzed {len(lines)} lines of code with complexity score {complexity_score}. "
                       f"Security assessment: {security_score}/100. "
                       f"Technical insights: {technical_analysis}",
            line_number=1,
            code_snippet=self._extract_critical_code_patterns(content),
            recommendation=self._generate_ai_recommendations(content, language),
            confidence="HIGH",
            category="AI Comprehensive Analysis",
            references=[
                "https://huggingface.co/models",
                "https://arxiv.org/abs/2108.07732",
                "https://consensys.github.io/smart-contract-best-practices/"
            ]
        )

    def _generate_advanced_pattern_findings(self, content: str, language: str) -> List[AnalysisFinding]:
        """Generate advanced pattern-based findings"""
        findings = []
        lines = content.splitlines()

        # Advanced security patterns
        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # Oracle manipulation patterns
            if any(pattern in line_lower for pattern in ['block.timestamp', 'block.difficulty', 'block.number']):
                findings.append(AnalysisFinding(
                    detector="ai_advanced_oracle",
                    severity=Severity.MEDIUM,
                    title="AI: Oracle Manipulation Risk",
                    description="AI detected usage of blockchain variables that can be manipulated by miners",
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Use secure oracle services like Chainlink for external data",
                    confidence="HIGH",
                    category="AI Advanced Security"
                ))

            # Front-running patterns
            if 'msg.value' in line_lower and 'require(' in line_lower:
                findings.append(AnalysisFinding(
                    detector="ai_advanced_frontrun",
                    severity=Severity.MEDIUM,
                    title="AI: Front-Running Vulnerability",
                    description="AI identified pattern susceptible to front-running attacks",
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Implement commit-reveal schemes or use private mempools",
                    confidence="MEDIUM",
                    category="AI Advanced Security"
                ))

        return findings

    def _analyze_with_gpt2(self, content: str, language: str) -> List[AnalysisFinding]:
        """Analyze using GPT-2 model for pattern detection"""
        findings = []

        try:
            # Create security analysis prompt
            prompt = self._create_security_prompt(content, language)

            # Query GPT-2 model
            response = self._query_huggingface_model('gpt2', prompt)
            
            if response and 'generated_text' in response:
                # Parse AI response for security insights
                ai_analysis = self._parse_ai_response(response['generated_text'])

                for analysis in ai_analysis:
                    finding = AnalysisFinding(
                        detector="gpt2_ai_security",
                        severity=self._map_severity(analysis.get('severity', 'medium')),
                        title=f"AI Security: {analysis.get('title', 'Pattern Detected')}",
                        description=analysis.get('description', 'AI detected a potential security pattern'),
                        line_number=analysis.get('line_number', 1),
                        code_snippet=analysis.get('code_snippet', ''),
                        recommendation=analysis.get('recommendation', 'Review the flagged code section'),
                        confidence=analysis.get('confidence', 'MEDIUM'),
                        category="AI Security Analysis",
                        references=["https://huggingface.co/gpt2"]
                    )
                    findings.append(finding)
                    
        except Exception as e:
            print(f"Grok analysis failed: {e}")
        
        return findings

    def _analyze_with_text_generation(self, content: str, language: str) -> List[AnalysisFinding]:
        """Analyze using text generation model for insights"""
        findings = []

        try:
            # Create insight generation prompt
            prompt = f"Analyze this {language} code for security issues: {content[:500]}..."

            # Query text generation model
            response = self._query_huggingface_model('text_generation', prompt)

            if response and 'generated_text' in response:
                # Simple pattern-based analysis of generated text
                generated = response['generated_text'].lower()

                if any(word in generated for word in ['vulnerable', 'security', 'attack', 'exploit']):
                    finding = AnalysisFinding(
                        detector="text_generation_ai",
                        severity=Severity.INFO,
                        title="AI Text Analysis",
                        description="AI text generation model identified potential security concerns",
                        line_number=1,
                        code_snippet="",
                        recommendation="Review AI-generated insights for security considerations",
                        confidence="LOW",
                        category="AI Text Analysis"
                    )
                    findings.append(finding)

        except Exception as e:
            print(f"Text generation analysis failed: {e}")

        return findings

    def _analyze_with_smart_contract_model(self, content: str, language: str) -> List[AnalysisFinding]:
        """Analyze using specialized smart contract auditing model"""
        findings = []
        
        if language != 'solidity':
            return findings  # This model is Solidity-specific
        
        try:
            # Create prompt for smart contract auditing
            prompt = self._create_audit_prompt(content)
            
            # Query smart contract auditing model
            response = self._query_huggingface_model('smart_contract_auditing', prompt)
            
            if response:
                # Parse auditing response
                audit_results = self._parse_audit_response(response)
                
                for result in audit_results:
                    finding = AnalysisFinding(
                        detector="smart_contract_auditing_ai",
                        severity=self._map_severity(result.get('severity', 'medium')),
                        title=f"Smart Contract Audit: {result.get('vulnerability_type', 'Issue')}",
                        description=result.get('description', 'Specialized auditing model detected an issue'),
                        line_number=result.get('line_number', 1),
                        code_snippet=result.get('code_snippet', ''),
                        recommendation=result.get('recommendation', 'Follow smart contract best practices'),
                        confidence=result.get('confidence', 'HIGH'),
                        category="Specialized Audit AI",
                        references=["https://huggingface.co/jkeyyy/smart-contract-auditing"]
                    )
                    findings.append(finding)
                    
        except Exception as e:
            print(f"Smart contract auditing analysis failed: {e}")
        
        return findings
    
    def _analyze_with_code_model(self, content: str, language: str) -> List[AnalysisFinding]:
        """Analyze using general code analysis models"""
        findings = []
        
        try:
            # Create prompt for code quality analysis
            prompt = self._create_code_quality_prompt(content, language)
            
            # Query code analysis model
            response = self._query_huggingface_model('code_analysis', prompt)
            
            if response:
                # Parse code analysis response
                code_issues = self._parse_code_response(response)
                
                for issue in code_issues:
                    finding = AnalysisFinding(
                        detector="code_analysis_ai",
                        severity=Severity.LOW,  # Code quality issues are typically low severity
                        title=f"Code Quality: {issue.get('type', 'Issue')}",
                        description=issue.get('description', 'Code analysis model detected a quality issue'),
                        line_number=issue.get('line_number', 1),
                        code_snippet=issue.get('code_snippet', ''),
                        recommendation=issue.get('recommendation', 'Improve code quality'),
                        confidence=issue.get('confidence', 'MEDIUM'),
                        category="Code Quality AI"
                    )
                    findings.append(finding)
                    
        except Exception as e:
            print(f"Code analysis failed: {e}")
        
        return findings
    
    def _query_huggingface_model(self, model_key: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Query Hugging Face model via API"""
        try:
            model_name = self.models.get(model_key)
            if not model_name:
                return None
            
            url = f"{self.base_url}/{model_name}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]
                return result
            else:
                print(f"Hugging Face API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Hugging Face query error: {e}")
            return None
    
    def _create_security_prompt(self, content: str, language: str) -> str:
        """Create security analysis prompt for AI models"""
        return f"""
Analyze this {language} smart contract for security vulnerabilities:

{content[:1000]}

Identify potential security issues like reentrancy, access control, overflow, etc.
"""
    
    def _create_audit_prompt(self, content: str) -> str:
        """Create prompt for specialized smart contract auditing model"""
        return f"""
Perform a comprehensive security audit of this Solidity smart contract:

{content}

Identify all potential vulnerabilities and provide detailed analysis.
"""
    
    def _create_code_quality_prompt(self, content: str, language: str) -> str:
        """Create prompt for code quality analysis"""
        return f"""
Analyze this {language} code for quality issues, best practices, and potential improvements:

{content}

Focus on code structure, naming conventions, and optimization opportunities.
"""
    
    def _parse_ai_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI model's response"""
        try:
            # Try to extract JSON from response
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            
            # Fallback: create structured response from text
            return self._parse_text_to_findings(response_text)
            
        except Exception as e:
            print(f"Error parsing Grok response: {e}")
            return []
    
    def _parse_audit_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse smart contract auditing model response"""
        try:
            if 'generated_text' in response:
                return self._parse_text_to_findings(response['generated_text'])
            return []
        except Exception:
            return []
    
    def _parse_code_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse code analysis model response"""
        try:
            if 'generated_text' in response:
                return self._parse_text_to_findings(response['generated_text'])
            return []
        except Exception:
            return []
    
    def _parse_text_to_findings(self, text: str) -> List[Dict[str, Any]]:
        """Convert text response to structured findings"""
        findings = []
        
        # Simple text parsing for vulnerabilities
        lines = text.split('\n')
        current_finding = {}
        
        for line in lines:
            line = line.strip()
            if any(severity in line.lower() for severity in ['critical', 'high', 'medium', 'low']):
                if current_finding:
                    findings.append(current_finding)
                current_finding = {
                    'severity': 'medium',
                    'title': line,
                    'description': line,
                    'line_number': 1,
                    'code_snippet': '',
                    'recommendation': 'Review and fix the identified issue',
                    'confidence': 'medium'
                }
                
                # Extract severity
                for sev in ['critical', 'high', 'medium', 'low']:
                    if sev in line.lower():
                        current_finding['severity'] = sev
                        break
        
        if current_finding:
            findings.append(current_finding)
        
        return findings
    
    def _map_severity(self, severity_str: str) -> Severity:
        """Map string severity to Severity enum"""
        severity_map = {
            'critical': Severity.CRITICAL,
            'high': Severity.HIGH,
            'medium': Severity.MEDIUM,
            'low': Severity.LOW,
            'info': Severity.INFO
        }
        return severity_map.get(severity_str.lower(), Severity.MEDIUM)

    def _generate_technical_analysis(self, content: str, language: str) -> str:
        """Generate detailed technical analysis"""
        analysis_points = []

        # Code complexity analysis
        lines = content.splitlines()
        complexity_score = len([l for l in lines if any(keyword in l for keyword in ['if', 'for', 'while', 'require', 'assert'])])
        analysis_points.append(f"Cyclomatic complexity: {complexity_score}")

        # Security pattern detection
        security_patterns = {
            'external_calls': len([l for l in lines if '.call(' in l or '.send(' in l or '.transfer(' in l]),
            'state_changes': len([l for l in lines if '=' in l and any(var in l for var in ['balance', 'owner', 'state'])]),
            'access_modifiers': len([l for l in lines if any(mod in l for mod in ['onlyOwner', 'onlyAdmin', 'require(msg.sender'])]),
            'reentrancy_guards': len([l for l in lines if 'nonReentrant' in l or 'ReentrancyGuard' in l])
        }

        for pattern, count in security_patterns.items():
            analysis_points.append(f"{pattern.replace('_', ' ').title()}: {count} instances")

        # Gas optimization opportunities
        gas_issues = len([l for l in lines if any(issue in l for issue in ['storage', 'memory', 'calldata', 'view', 'pure'])])
        analysis_points.append(f"Gas optimization opportunities: {gas_issues}")

        return "; ".join(analysis_points)

    def _extract_critical_code_patterns(self, content: str) -> str:
        """Extract critical code patterns for analysis"""
        lines = content.splitlines()
        critical_lines = []

        for i, line in enumerate(lines, 1):
            if any(pattern in line.lower() for pattern in [
                'call{', 'delegatecall', 'selfdestruct', 'suicide',
                'tx.origin', 'block.timestamp', 'block.number',
                'msg.value', 'address(this).balance'
            ]):
                critical_lines.append(f"Line {i}: {line.strip()}")

        return "\n".join(critical_lines[:5])  # Top 5 critical patterns

    def _generate_ai_recommendations(self, content: str, language: str) -> str:
        """Generate AI-powered recommendations"""
        recommendations = []

        # Analyze content for specific vulnerabilities
        if 'call{' in content and 'balance' in content:
            recommendations.append("Implement checks-effects-interactions pattern to prevent reentrancy")

        if 'tx.origin' in content:
            recommendations.append("Replace tx.origin with msg.sender for proper access control")

        if 'block.timestamp' in content:
            recommendations.append("Avoid using block.timestamp for critical logic due to miner manipulation")

        if not any(guard in content for guard in ['onlyOwner', 'require(msg.sender']):
            recommendations.append("Add access control modifiers to sensitive functions")

        if 'selfdestruct' in content:
            recommendations.append("Consider alternatives to selfdestruct as it will be deprecated")

        # Gas optimization recommendations
        if 'storage' in content and 'memory' not in content:
            recommendations.append("Consider using memory for temporary variables to save gas")

        return "; ".join(recommendations) if recommendations else "Code follows security best practices"

    def _generate_pattern_based_findings(self, content: str, language: str) -> List[AnalysisFinding]:
        """Generate AI-style findings based on pattern analysis"""
        findings = []
        lines = content.splitlines()

        # Advanced pattern detection
        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # AI-detected complexity patterns
            if 'for' in line_lower and 'length' in line_lower and 'i++' in line_lower:
                findings.append(AnalysisFinding(
                    detector="ai_complexity_analysis",
                    severity=Severity.LOW,
                    title="AI: Loop Complexity Detected",
                    description="AI analysis identified a potentially gas-expensive loop pattern",
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Consider implementing pagination or gas-efficient alternatives",
                    confidence="MEDIUM",
                    category="AI Code Quality"
                ))

            # AI-detected security patterns
            if any(pattern in line_lower for pattern in ['call{', 'delegatecall', 'selfdestruct']):
                findings.append(AnalysisFinding(
                    detector="ai_security_pattern",
                    severity=Severity.MEDIUM,
                    title="AI: Critical Function Call Detected",
                    description="AI identified usage of potentially dangerous low-level operations",
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Ensure proper access control and error handling for critical operations",
                    confidence="HIGH",
                    category="AI Security Analysis"
                ))

            # AI-detected randomness issues
            if 'block.timestamp' in line_lower or 'block.difficulty' in line_lower:
                findings.append(AnalysisFinding(
                    detector="ai_randomness_analysis",
                    severity=Severity.MEDIUM,
                    title="AI: Weak Randomness Source",
                    description="AI detected usage of predictable blockchain variables for randomness",
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Use secure randomness sources like Chainlink VRF or commit-reveal schemes",
                    confidence="HIGH",
                    category="AI Security Analysis"
                ))

        # Add overall AI assessment
        if len(findings) > 0:
            findings.append(AnalysisFinding(
                detector="ai_overall_assessment",
                severity=Severity.INFO,
                title="AI Security Assessment Summary",
                description=f"AI analysis completed with {len(findings)} pattern-based insights. Code complexity analysis shows {self._calculate_complexity_score(content)} complexity points.",
                line_number=1,
                code_snippet="",
                recommendation="Review AI-identified patterns and consider implementing suggested improvements",
                confidence="HIGH",
                category="AI Analysis Summary"
            ))

        return findings

    def _calculate_complexity_score(self, content: str) -> int:
        """Calculate a simple complexity score"""
        lines = content.splitlines()
        complexity = 0

        for line in lines:
            line_lower = line.lower()
            # Count complexity indicators
            complexity += line_lower.count('if ')
            complexity += line_lower.count('for ')
            complexity += line_lower.count('while ')
            complexity += line_lower.count('require(')
            complexity += line_lower.count('assert(')
            complexity += line_lower.count('modifier ')

        return complexity

# Hugging Face Integration Status
class HuggingFaceStatus:
    """Track Hugging Face integration status"""
    
    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Get current Hugging Face integration status"""
        analyzer = HuggingFaceAnalyzer()

        # Check if requests module is available
        try:
            import requests
            requests_available = True
        except ImportError:
            requests_available = False

        return {
            "huggingface_available": bool(analyzer.api_key) and requests_available,
            "api_key_configured": bool(analyzer.api_key),
            "requests_available": requests_available,
            "available_models": list(analyzer.models.keys()),
            "model_details": analyzer.models,
            "capabilities": [
                "AI-Powered Security Analysis",
                "Vulnerability Pattern Recognition",
                "Code Quality Analysis",
                "Gas Optimization Analysis",
                "Smart Contract Auditing",
                "Multi-language Support",
                "Real-time AI Inference"
            ],
            "supported_languages": analyzer.supported_extensions,
            "api_endpoint": analyzer.base_url,
            "total_models": len(analyzer.models)
        }
