"""
Mistral AI LLM Service for ImpactGuard
Provides deep code reasoning, contextual understanding, and AI pair programming capabilities
"""
import os
import json
from typing import Dict, List, Optional, Any
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from config import settings


class MistralLLMService:
    """
    Advanced LLM service using Mistral AI for intelligent code analysis
    
    Capabilities:
    1. Deep "Why" Analysis - Explains the reasoning behind risks
    2. Conversational Summaries - Human-like explanations
    3. Complex "What If" Scenarios - Traces logic across files
    4. Actionable Remediation - Suggests specific code changes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Mistral AI client"""
        self.api_key = api_key or settings.MISTRAL_API_KEY
        self.client = None
        self.model = settings.MISTRAL_MODEL or "mistral-large-latest"
        
        if self.api_key:
            try:
                self.client = MistralClient(api_key=self.api_key)
                print("✅ Mistral AI LLM initialized successfully")
            except Exception as e:
                print(f"⚠️ Mistral AI initialization failed: {e}")
                self.client = None
        else:
            print("⚠️ Mistral API key not found. LLM features will use fallback mode.")
    
    def is_available(self) -> bool:
        """Check if Mistral AI is configured and available"""
        return self.client is not None
    
    async def explain_risk_reasoning(
        self,
        impact_report: Dict[str, Any],
        code_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Explain WHY a change is risky, not just WHAT the risk is
        
        Args:
            impact_report: The standard impact analysis report
            code_context: Optional dict of {filename: code_content}
        
        Returns:
            Human-readable explanation of the risk reasoning
        """
        if not self.is_available():
            return self._fallback_risk_explanation(impact_report)
        
        try:
            # Build context-rich prompt
            prompt = self._build_risk_reasoning_prompt(impact_report, code_context)
            
            messages = [
                ChatMessage(role="system", content=self._get_system_prompt()),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower for more focused, technical responses
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in Mistral risk reasoning: {e}")
            return self._fallback_risk_explanation(impact_report)
    
    async def generate_conversational_summary(
        self,
        impact_report: Dict[str, Any],
        user_context: Optional[str] = None,
        code_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a truly conversational, human-like summary
        
        Args:
            impact_report: The impact analysis report
            user_context: Optional context about what the user is trying to do
            code_context: Optional actual code snippets
        
        Returns:
            Conversational summary that feels like talking to a senior developer
        """
        if not self.is_available():
            return self._fallback_conversational_summary(impact_report)
        
        try:
            code_snippets_text = ""
            if code_context:
                code_snippets_text = f"Actual Code Snippets:\n{json.dumps(code_context, indent=2)}"
            
            context_text = ""
            if user_context:
                context_text = f"Developer's Context: {user_context}"
            
            prompt = f"""
You're a senior software engineer reviewing a colleague's code changes. Be conversational, helpful, and specific.

Impact Analysis Data:
{json.dumps(impact_report, indent=2)}

{context_text}

{code_snippets_text}

Provide a conversational summary that:
1. Starts with a friendly observation about what they're changing
2. Highlights the most important risks in plain English
3. Reference actual code logic if code snippets were provided
4. Suggests specific things to check or update
5. Ends with an encouraging note or helpful tip

Keep it under 150 words. Sound like a helpful colleague, not a robot.
"""
            
            messages = [
                ChatMessage(role="system", content="You are a helpful senior software engineer providing code review feedback."),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Higher for more natural conversation
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in conversational summary: {e}")
            return self._fallback_conversational_summary(impact_report)
    
    async def analyze_what_if_scenario(
        self,
        scenario: str,
        repository_context: Dict[str, Any],
        code_files: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Handle complex "what if" queries with deep reasoning
        
        Args:
            scenario: The what-if question (e.g., "If I refactor the database schema...")
            repository_context: Context about the repository structure
            code_files: Optional actual code content for deeper analysis
        
        Returns:
            Detailed analysis of the scenario with predicted impacts
        """
        if not self.is_available():
            return self._fallback_what_if_analysis(scenario)
        
        try:
            prompt = f"""
Analyze this hypothetical code change scenario:

Scenario: {scenario}

Repository Context:
{json.dumps(repository_context, indent=2)}

{f"Code Files Available: {list(code_files.keys())}" if code_files else ""}

Provide a detailed analysis that:
1. Traces the logical flow of how this change would propagate
2. Identifies which components would break first and why
3. Predicts secondary and tertiary effects
4. Suggests a safe implementation order

Be specific about file names, function names, and logical dependencies.
"""
            
            messages = [
                ChatMessage(role="system", content=self._get_system_prompt()),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in what-if analysis: {e}")
            return self._fallback_what_if_analysis(scenario)
    
    async def suggest_code_remediation(
        self,
        impact_report: Dict[str, Any],
        affected_files: Dict[str, str]
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Suggest actual code changes to mitigate risks
        
        Args:
            impact_report: The impact analysis report
            affected_files: Dict of {filename: code_content}
        
        Returns:
            Dict of {filename: [{"line": X, "suggestion": "...", "reason": "..."}]}
        """
        if not self.is_available():
            return self._fallback_remediation_suggestions(impact_report)
        
        try:
            prompt = f"""
Based on this impact analysis, suggest specific code changes to mitigate risks:

Impact Report:
{json.dumps(impact_report, indent=2)}

Affected Files:
{json.dumps({k: f"<{len(v)} lines of code>" for k, v in affected_files.items()}, indent=2)}

For each high-risk area, provide:
1. The specific file and approximate line number
2. What code change is needed
3. Why this change reduces the risk

Format as JSON:
{{
  "filename.py": [
    {{
      "line": 42,
      "suggestion": "Add null check before accessing user.session",
      "reason": "Prevents race condition when session expires during request"
    }}
  ]
}}
"""
            
            messages = [
                ChatMessage(role="system", content=self._get_system_prompt()),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Error in code remediation: {e}")
            return self._fallback_remediation_suggestions(impact_report)
    
    async def chat_with_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        code_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        General chat interface with code context awareness
        
        Args:
            user_message: The user's question or request
            conversation_history: Previous messages [{"role": "user/assistant", "content": "..."}]
            code_context: Current code analysis context
        
        Returns:
            AI assistant's response
        """
        if not self.is_available():
            return "I'm sorry, but the AI assistant is not configured. Please add your Mistral API key to enable intelligent conversations."
        
        try:
            # Build messages with context
            messages = [ChatMessage(role="system", content=self._get_chat_system_prompt(code_context))]
            
            # Add conversation history
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
            
            # Add current message
            messages.append(ChatMessage(role="user", content=user_message))
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return f"I encountered an error: {str(e)}. Please try rephrasing your question."
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for code analysis tasks"""
        return """You are an expert software engineer and code analyst specializing in impact analysis and risk assessment.

Your expertise includes:
- Deep understanding of code dependencies and architecture
- Identifying subtle bugs and race conditions
- Predicting cascading effects of code changes
- Suggesting practical, actionable solutions

Always be:
- Specific (mention exact files, functions, line numbers when possible)
- Practical (focus on actionable insights)
- Clear (explain technical concepts in understandable terms)
- Proactive (anticipate problems before they occur)

You're helping developers make safer code changes by explaining the "why" behind risks, not just the "what"."""
    
    def _get_chat_system_prompt(self, code_context: Optional[Dict[str, Any]] = None) -> str:
        """Get system prompt for general chat with code context"""
        base_prompt = """You are an AI pair programming assistant integrated into ImpactGuard, a code impact analysis system.

You help developers by:
- Answering questions about their code changes
- Explaining risk assessments in detail
- Suggesting safer ways to implement features
- Providing code examples and best practices

Be conversational, helpful, and technically accurate."""
        
        if code_context:
            base_prompt += f"\n\nCurrent Code Context:\n{json.dumps(code_context, indent=2)}"
        
        return base_prompt
    
    def _build_risk_reasoning_prompt(
        self,
        impact_report: Dict[str, Any],
        code_context: Optional[Dict[str, str]] = None
    ) -> str:
        """Build a detailed prompt for risk reasoning"""
        prompt = f"""
Analyze this code change impact report and explain WHY it's risky:

Risk Level: {impact_report.get('risk_level', 'UNKNOWN')}
Risk Score: {impact_report.get('risk_score', 0):.2f}

Critical Files: {', '.join(impact_report.get('critical_files', []))}
Affected Areas: {', '.join(impact_report.get('affected_areas', []))}

Warnings:
{json.dumps(impact_report.get('warnings', []), indent=2)}

{f"Code Context Available: {list(code_context.keys())}" if code_context else ""}

Explain:
1. The root cause of the risk (not just "high dependencies")
2. What could go wrong in production
3. Why this specific combination of changes is dangerous
4. What developers often forget when making similar changes

Be specific and technical. Focus on the "why" and "how", not just the "what".
"""
        return prompt
    
    # Fallback methods for when Mistral is not available
    
    def _fallback_risk_explanation(self, impact_report: Dict[str, Any]) -> str:
        """Fallback risk explanation without LLM"""
        risk_level = impact_report.get('risk_level', 'UNKNOWN')
        risk_score = impact_report.get('risk_score', 0)
        critical_files = impact_report.get('critical_files', [])
        warnings = impact_report.get('warnings', [])
        
        explanation = f"This change has a {risk_level} risk level (score: {risk_score:.2f}).\n\n"
        
        if critical_files:
            explanation += f"Critical files affected: {', '.join(critical_files[:3])}\n"
        
        if warnings:
            explanation += f"\nKey warnings:\n"
            for warning in warnings[:3]:
                explanation += f"- {warning.get('message', 'Unknown warning')}\n"
        
        explanation += "\n💡 Enable Mistral AI for deeper 'why' analysis and actionable recommendations."
        
        return explanation
    
    def _fallback_conversational_summary(self, impact_report: Dict[str, Any]) -> str:
        """Fallback conversational summary"""
        risk_level = impact_report.get('risk_level', 'UNKNOWN')
        affected_count = len(impact_report.get('affected_areas', []))
        
        return f"You're making changes that affect {affected_count} areas with {risk_level} risk. Consider reviewing the suggested files before committing. Enable Mistral AI for more conversational insights!"
    
    def _fallback_what_if_analysis(self, scenario: str) -> str:
        """Fallback what-if analysis"""
        return f"To analyze the scenario '{scenario}', please configure Mistral AI. This requires deep code reasoning capabilities that go beyond static analysis."
    
    def _fallback_remediation_suggestions(self, impact_report: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """Fallback remediation suggestions"""
        return {
            "general": [
                {
                    "line": 0,
                    "suggestion": "Review the learning path and suggested files",
                    "reason": "Enable Mistral AI for specific code-level recommendations"
                }
            ]
        }


# Singleton instance
_mistral_service = None


def get_mistral_service() -> MistralLLMService:
    """Get or create the Mistral LLM service singleton"""
    global _mistral_service
    if _mistral_service is None:
        _mistral_service = MistralLLMService()
    return _mistral_service

# Made with Bob
