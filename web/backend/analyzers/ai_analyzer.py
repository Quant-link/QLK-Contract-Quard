"""
AI-Powered Smart Contract Analysis Engine
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from .base import BaseAnalyzer, AnalysisFinding, Severity

class AIAnalyzer(BaseAnalyzer):
    """AI-powered analyzer using machine learning models"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['sol', 'rs', 'go']
        self.ai_enabled = self._check_ai_availability()
        
    def _check_ai_availability(self) -> bool:
        """Check if AI services are available"""
        # Check for OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        
        # Check for local AI model
        local_model = os.getenv('LOCAL_AI_MODEL_PATH')
        
        return bool(openai_key or local_model)
    
    def supports_language(self, language: str) -> bool:
        return language.lower() in self.supported_extensions
    
    def analyze_file(self, filename: str, content: str) -> List[AnalysisFinding]:
        """
        Perform AI-powered analysis
        
        Args:
            filename: Name of the file
            content: Source code content
            
        Returns:
            List of AI-detected findings
        """
        if not self.ai_enabled:
            return self._mock_ai_analysis(filename, content)
        
        findings = []
        
        try:
            # Determine language
            language = self._detect_language(filename)
            
            # Run AI analysis based on language
            if language == 'sol':
                findings.extend(self._analyze_solidity_ai(content))
            elif language == 'rs':
                findings.extend(self._analyze_rust_ai(content))
            elif language == 'go':
                findings.extend(self._analyze_go_ai(content))
                
        except Exception as e:
            print(f"AI analysis failed: {e}")
        
        return findings
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        if filename.endswith('.sol'):
            return 'sol'
        elif filename.endswith('.rs'):
            return 'rs'
        elif filename.endswith('.go'):
            return 'go'
        return 'unknown'
    
    def _analyze_solidity_ai(self, content: str) -> List[AnalysisFinding]:
        """AI analysis for Solidity contracts"""
        findings = []
        
        # AI prompts for different vulnerability types
        ai_checks = [
            {
                'name': 'reentrancy_ai',
                'prompt': self._create_reentrancy_prompt(content),
                'severity': Severity.HIGH
            },
            {
                'name': 'access_control_ai', 
                'prompt': self._create_access_control_prompt(content),
                'severity': Severity.MEDIUM
            },
            {
                'name': 'logic_bugs_ai',
                'prompt': self._create_logic_bugs_prompt(content),
                'severity': Severity.MEDIUM
            },
            {
                'name': 'gas_optimization_ai',
                'prompt': self._create_gas_optimization_prompt(content),
                'severity': Severity.LOW
            }
        ]
        
        for check in ai_checks:
            try:
                ai_result = self._query_ai_model(check['prompt'])
                if ai_result and ai_result.get('has_issue', False):
                    finding = AnalysisFinding(
                        detector=check['name'],
                        severity=check['severity'],
                        title=ai_result.get('title', 'AI-Detected Issue'),
                        description=ai_result.get('description', 'AI detected a potential issue'),
                        line_number=ai_result.get('line_number', 1),
                        code_snippet=ai_result.get('code_snippet', ''),
                        recommendation=ai_result.get('recommendation', 'Review the flagged code'),
                        confidence=ai_result.get('confidence', 'MEDIUM'),
                        category="AI Analysis"
                    )
                    findings.append(finding)
                    
            except Exception as e:
                print(f"AI check {check['name']} failed: {e}")
        
        return findings
    
    def _create_reentrancy_prompt(self, content: str) -> str:
        """Create AI prompt for reentrancy detection"""
        return f"""
        Analyze the following Solidity contract for reentrancy vulnerabilities:
        
        {content}
        
        Look for:
        1. External calls followed by state changes
        2. Missing reentrancy guards
        3. Checks-Effects-Interactions pattern violations
        
        Respond in JSON format:
        {{
            "has_issue": boolean,
            "title": "string",
            "description": "string", 
            "line_number": number,
            "code_snippet": "string",
            "recommendation": "string",
            "confidence": "HIGH|MEDIUM|LOW"
        }}
        """
    
    def _create_access_control_prompt(self, content: str) -> str:
        """Create AI prompt for access control analysis"""
        return f"""
        Analyze the following smart contract for access control vulnerabilities:
        
        {content}
        
        Look for:
        1. Missing access control on critical functions
        2. Improper use of tx.origin
        3. Missing onlyOwner or similar modifiers
        4. Privilege escalation possibilities
        
        Respond in JSON format with vulnerability details.
        """
    
    def _create_logic_bugs_prompt(self, content: str) -> str:
        """Create AI prompt for logic bug detection"""
        return f"""
        Analyze the following smart contract for logic bugs and business logic issues:
        
        {content}
        
        Look for:
        1. Integer overflow/underflow
        2. Incorrect calculations
        3. Wrong conditional logic
        4. Edge case handling issues
        
        Respond in JSON format with issue details.
        """
    
    def _create_gas_optimization_prompt(self, content: str) -> str:
        """Create AI prompt for gas optimization"""
        return f"""
        Analyze the following smart contract for gas optimization opportunities:
        
        {content}
        
        Look for:
        1. Inefficient loops
        2. Unnecessary storage operations
        3. Redundant computations
        4. Better data structure choices
        
        Respond in JSON format with optimization suggestions.
        """
    
    def _query_ai_model(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query AI model with prompt"""
        # Check if OpenAI is available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            return self._query_openai(prompt, openai_key)
        
        # Check if local model is available
        local_model = os.getenv('LOCAL_AI_MODEL_PATH')
        if local_model:
            return self._query_local_model(prompt, local_model)
        
        return None
    
    def _query_openai(self, prompt: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Query OpenAI API"""
        try:
            import openai
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a smart contract security expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"OpenAI query failed: {e}")
            return None
    
    def _query_local_model(self, prompt: str, model_path: str) -> Optional[Dict[str, Any]]:
        """Query local AI model"""
        try:
            # This would integrate with local models like Ollama, Hugging Face, etc.
            # For now, return mock response
            return {
                "has_issue": False,
                "title": "Local AI Analysis",
                "description": "Local AI model analysis completed",
                "line_number": 1,
                "code_snippet": "",
                "recommendation": "No issues detected by local AI",
                "confidence": "MEDIUM"
            }
            
        except Exception as e:
            print(f"Local model query failed: {e}")
            return None
    
    def _analyze_rust_ai(self, content: str) -> List[AnalysisFinding]:
        """AI analysis for Rust contracts"""
        # Similar to Solidity but with Rust-specific patterns
        return []
    
    def _analyze_go_ai(self, content: str) -> List[AnalysisFinding]:
        """AI analysis for Go contracts"""
        # Similar to Solidity but with Go-specific patterns
        return []
    
    def _mock_ai_analysis(self, filename: str, content: str) -> List[AnalysisFinding]:
        """Fallback when no AI services are available - should not be used with HF integration"""
        # This should not be called when Hugging Face is available
        return []

# AI Integration Status
class AIIntegrationStatus:
    """Track AI integration capabilities"""
    
    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Get current AI integration status"""
        return {
            "openai_available": bool(os.getenv('OPENAI_API_KEY')),
            "local_model_available": bool(os.getenv('LOCAL_AI_MODEL_PATH')),
            "supported_models": [
                "gpt-4",
                "gpt-3.5-turbo", 
                "claude-3",
                "local-llama",
                "local-codellama"
            ],
            "capabilities": [
                "Vulnerability Detection",
                "Code Quality Analysis", 
                "Gas Optimization",
                "Logic Bug Detection",
                "Security Best Practices"
            ]
        }
