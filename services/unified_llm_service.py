"""
Unified LLM Service - The Brain of ImpactGuard
All analysis passes through Mistral AI for comprehensive, human-readable insights
"""
import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


class UnifiedLLMService:
    """
    Central LLM service that processes ALL analysis through Mistral AI
    Provides comprehensive, conversational insights about code changes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Mistral AI client"""
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.client = None
        self.model = "mistral-large-latest"
        
        if self.api_key:
            try:
                self.client = MistralClient(api_key=self.api_key)
                print("✅ Unified LLM Service initialized successfully")
            except Exception as e:
                print(f"⚠️ Unified LLM initialization failed: {e}")
                self.client = None
        else:
            print("⚠️ Mistral API key not found. LLM features disabled.")
    
    def is_available(self) -> bool:
        """Check if LLM is configured and available"""
        return self.client is not None
    
    async def comprehensive_pre_push_analysis(
        self,
        repository_path: str,
        changed_files: List[str],
        impact_data: Dict[str, Any],
        git_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete pre-push analysis with LLM as the brain
        
        Returns comprehensive analysis including:
        - Why this is risky (root cause explanation)
        - What will change and where (specific lines)
        - Who should review/fix (with reasoning)
        - Predicted impacts (cascade effects)
        - Actionable recommendations
        """
        if not self.is_available():
            return self._fallback_analysis(impact_data)
        
        try:
            # Read actual code content
            code_contents = {}
            for file_path in changed_files[:10]:  # Limit to 10 files
                full_path = Path(repository_path) / file_path
                if full_path.exists() and full_path.suffix in ['.py', '.js', '.ts', '.java', '.go']:
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            code_contents[file_path] = f.read()
                    except:
                        pass
            
            # Build comprehensive prompt
            prompt = self._build_comprehensive_prompt(
                changed_files,
                impact_data,
                code_contents,
                git_context
            )
            
            messages = [
                ChatMessage(
                    role="system",
                    content=self._get_comprehensive_system_prompt()
                ),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=3000
            )
            
            # Parse LLM response into structured format
            llm_response = response.choices[0].message.content
            
            return {
                "success": True,
                "llm_enabled": True,
                "analysis": {
                    "summary": self._extract_section(llm_response, "SUMMARY"),
                    "risk_explanation": self._extract_section(llm_response, "WHY RISKY"),
                    "affected_components": self._extract_section(llm_response, "WHAT WILL CHANGE"),
                    "specific_impacts": self._extract_section(llm_response, "WHERE (SPECIFIC LINES)"),
                    "responsible_developers": self._extract_section(llm_response, "WHO SHOULD FIX"),
                    "cascade_effects": self._extract_section(llm_response, "CASCADE EFFECTS"),
                    "recommendations": self._extract_section(llm_response, "RECOMMENDATIONS"),
                    "full_response": llm_response
                },
                "risk_level": impact_data.get("risk_level", "UNKNOWN"),
                "risk_score": impact_data.get("risk_score", 0),
                "changed_files": changed_files,
                "repository": repository_path
            }
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            return self._fallback_analysis(impact_data)
    
    def _build_comprehensive_prompt(
        self,
        changed_files: List[str],
        impact_data: Dict[str, Any],
        code_contents: Dict[str, str],
        git_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build a comprehensive prompt for the LLM"""
        
        prompt = f"""
You are a senior software architect reviewing code changes before they are pushed to production.

CHANGED FILES:
{json.dumps(changed_files, indent=2)}

IMPACT ANALYSIS DATA:
Risk Level: {impact_data.get('risk_level', 'UNKNOWN')}
Risk Score: {impact_data.get('risk_score', 0):.2f}
Critical Files: {', '.join(impact_data.get('critical_files', []))}
Affected Areas: {', '.join(impact_data.get('affected_areas', []))}
Warnings: {json.dumps(impact_data.get('warnings', []), indent=2)}

CODE CONTENTS:
{self._format_code_contents(code_contents)}

{f"GIT CONTEXT: {json.dumps(git_context, indent=2)}" if git_context else ""}

Provide a COMPREHENSIVE analysis in the following format:

## SUMMARY
[One paragraph overview of what's being changed and overall risk]

## WHY RISKY
[Explain the ROOT CAUSE of the risk. Not just "high dependencies" but WHY that matters.
What could go wrong in production? What are the failure scenarios?]

## WHAT WILL CHANGE
[List the specific components, services, or modules that will be affected.
Be specific about the nature of the changes.]

## WHERE (SPECIFIC LINES)
[For each critical file, identify:
- File name
- Specific line numbers that are problematic or need attention
- What's wrong with those lines
- What needs to be changed

Format as:
filename.py:
  - Line 42: [Issue] - [What needs to change]
  - Line 89: [Issue] - [What needs to change]
]

## WHO SHOULD FIX
[Based on the git history and code ownership, identify:
- Who are the experts for these files
- Who should review this change
- Who should be responsible for fixing issues
- Why each person is recommended (their expertise)]

## CASCADE EFFECTS
[Predict the ripple effects:
- What will break first if this is pushed?
- What secondary systems will be affected?
- What will break later (delayed effects)?
- Timeline of potential failures]

## RECOMMENDATIONS
[Provide actionable steps:
1. Immediate actions before pushing
2. Code changes needed (be specific)
3. Tests to add
4. Monitoring to set up
5. Rollback plan]

Be SPECIFIC, TECHNICAL, and ACTIONABLE. Use actual file names, line numbers, and developer names from the data.
"""
        return prompt
    
    def _format_code_contents(self, code_contents: Dict[str, str]) -> str:
        """Format code contents for the prompt"""
        if not code_contents:
            return "No code contents available"
        
        formatted = []
        for filename, content in code_contents.items():
            lines = content.split('\n')
            # Include line numbers
            numbered_lines = [f"{i+1:4d} | {line}" for i, line in enumerate(lines[:100])]  # First 100 lines
            formatted.append(f"\n### {filename}\n```\n" + "\n".join(numbered_lines) + "\n```")
        
        return "\n".join(formatted)
    
    def _get_comprehensive_system_prompt(self) -> str:
        """Get the system prompt for comprehensive analysis"""
        return """You are an expert senior software architect and code reviewer with 15+ years of experience.

Your role is to provide comprehensive, actionable code review insights before developers push to production.

Key principles:
1. Be SPECIFIC - Use actual file names, line numbers, function names
2. Be TECHNICAL - Explain the engineering reasons, not just surface-level observations
3. Be ACTIONABLE - Every insight should lead to a concrete action
4. Be PREDICTIVE - Anticipate what will break and when
5. Be HUMAN - Write like you're talking to a colleague, not generating a report

Focus on:
- Root causes, not symptoms
- Specific code locations (file:line)
- Real-world production impacts
- Concrete fix suggestions
- Developer accountability (who should handle what)

Avoid:
- Generic advice
- Vague warnings
- Obvious statements
- Repeating the input data"""
    
    def _extract_section(self, response: str, section_name: str) -> str:
        """Extract a specific section from the LLM response"""
        try:
            # Look for section headers
            lines = response.split('\n')
            section_lines = []
            in_section = False
            
            for line in lines:
                if section_name in line.upper():
                    in_section = True
                    continue
                elif line.startswith('##') and in_section:
                    break
                elif in_section:
                    section_lines.append(line)
            
            return '\n'.join(section_lines).strip()
        except:
            return ""
    
    def _fallback_analysis(self, impact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        return {
            "success": True,
            "llm_enabled": False,
            "analysis": {
                "summary": f"Risk Level: {impact_data.get('risk_level', 'UNKNOWN')}. Configure Mistral AI for detailed analysis.",
                "risk_explanation": "LLM not configured. Basic analysis only.",
                "affected_components": ', '.join(impact_data.get('affected_areas', [])),
                "specific_impacts": "Configure Mistral AI for line-by-line analysis",
                "responsible_developers": ', '.join([r.get('name', 'Unknown') for r in impact_data.get('suggested_reviewers', [])[:3]]),
                "cascade_effects": "Configure Mistral AI for cascade prediction",
                "recommendations": "1. Configure Mistral AI API key\n2. Review the basic impact report\n3. Consult with team leads",
                "full_response": "Mistral AI not configured. Add MISTRAL_API_KEY to .env for comprehensive analysis."
            },
            "risk_level": impact_data.get('risk_level', 'UNKNOWN'),
            "risk_score": impact_data.get('risk_score', 0),
            "changed_files": [],
            "repository": ""
        }


# Singleton instance
_unified_llm_service = None


def get_unified_llm_service() -> UnifiedLLMService:
    """Get or create the unified LLM service singleton"""
    global _unified_llm_service
    if _unified_llm_service is None:
        _unified_llm_service = UnifiedLLMService()
    return _unified_llm_service

# Made with Bob
