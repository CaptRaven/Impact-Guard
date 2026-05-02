"""
Bob - The AI Code Impact Analyzer
Analyzes code changes BEFORE commit and provides clear, actionable insights
"""
import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


class BobAnalyzer:
    """
    Bob analyzes your code changes and tells you:
    1. Impact Prediction - What this touches and risk level
    2. Breakage Simulation - What broke before with similar changes
    3. Smart Reviewer Assignment - Who should review this
    4. Auto Learning Path - What to understand first (when needed)
    5. Voice Explanation - Why this is risky (spoken)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Bob with Mistral AI"""
        from config import settings
        self.api_key = api_key or settings.MISTRAL_API_KEY or os.getenv("MISTRAL_API_KEY")
        self.client = None
        self.model = settings.MISTRAL_MODEL
        
        if self.api_key:
            try:
                self.client = MistralClient(api_key=self.api_key)
                print("✅ Bob (AI Analyzer) initialized successfully")
            except Exception as e:
                print(f"⚠️ Bob initialization failed: {e}")
                self.client = None
        else:
            print("⚠️ Mistral API key not found. Bob will use basic analysis.")
    
    def is_available(self) -> bool:
        """Check if Bob (LLM) is available"""
        return self.client is not None
    
    async def analyze_before_commit(
        self,
        repository_path: str,
        changed_files: List[str],
        impact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Bob's complete analysis before commit
        
        Returns exactly 5 things:
        1. Impact Prediction
        2. Breakage Simulation
        3. Smart Reviewer Assignment
        4. Auto Learning Path (only when needed)
        5. Voice Explanation
        """
        
        # Read code for context
        code_snippets = self._read_code_snippets(repository_path, changed_files)
        
        if not self.is_available():
            return self._basic_analysis(impact_data, changed_files)
        
        try:
            # Build focused prompt for Bob
            prompt = f"""You are Bob, an AI code analyzer. A developer is about to commit these changes:

CHANGED FILES: {', '.join(changed_files)}

IMPACT DATA:
- Risk Level: {impact_data.get('risk_level', 'UNKNOWN')}
- Risk Score: {impact_data.get('risk_score', 0):.2f}
- Critical Files: {', '.join(impact_data.get('critical_files', []))}
- Affected Areas: {', '.join(impact_data.get('affected_areas', []))}
- Dependencies: {len(impact_data.get('affected_areas', []))} modules affected

HISTORICAL WARNINGS:
{json.dumps(impact_data.get('warnings', []), indent=2)}

SUGGESTED REVIEWERS:
{json.dumps([{{
    'name': r.get('name'),
    'confidence': r.get('confidence'),
    'commits': r.get('commits_count')
}} for r in impact_data.get('suggested_reviewers', [])[:3]], indent=2)}

CODE SNIPPETS:
{code_snippets}

Provide analysis in EXACTLY this format:

## 1. IMPACT PREDICTION
[One clear sentence: "This change affects X → Y → Z → risk level"]

## 2. BREAKAGE SIMULATION
[One clear sentence: "Similar change in commit #abc caused XYZ failure" OR "No similar failures found"]

## 3. SMART REVIEWER ASSIGNMENT
[One clear sentence: "Send this to NAME (X% ownership of this module)" - pick the TOP reviewer]

## 4. AUTO LEARNING PATH
[ONLY if risk is HIGH, list 2-3 files to understand first. Otherwise say "Not needed - straightforward change"]

## 5. VOICE EXPLANATION
[2-3 sentences explaining WHY this is risky in simple terms, as if speaking to the developer]

Be CONCISE. Each section should be 1-3 sentences maximum.
"""
            
            messages = [
                ChatMessage(
                    role="system",
                    content="You are Bob, a helpful AI code analyzer. Be concise and clear."
                ),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=800
            )
            
            llm_response = response.choices[0].message.content
            
            # Parse the 5 sections
            return {
                "success": True,
                "bob_enabled": True,
                "analysis": {
                    "impact_prediction": self._extract_section(llm_response, "1. IMPACT PREDICTION"),
                    "breakage_simulation": self._extract_section(llm_response, "2. BREAKAGE SIMULATION"),
                    "smart_reviewer": self._extract_section(llm_response, "3. SMART REVIEWER ASSIGNMENT"),
                    "learning_path": self._extract_section(llm_response, "4. AUTO LEARNING PATH"),
                    "voice_explanation": self._extract_section(llm_response, "5. VOICE EXPLANATION"),
                    "full_response": llm_response
                },
                "risk_level": impact_data.get('risk_level', 'UNKNOWN'),
                "risk_score": impact_data.get('risk_score', 0),
                "changed_files": changed_files
            }
            
        except Exception as e:
            print(f"Bob analysis error: {e}")
            return self._basic_analysis(impact_data, changed_files)
    
    def _read_code_snippets(self, repository_path: str, changed_files: List[str]) -> str:
        """Read first 50 lines of each changed file"""
        snippets = []
        for file_path in changed_files[:5]:  # Limit to 5 files
            full_path = Path(repository_path) / file_path
            if full_path.exists() and full_path.suffix in ['.py', '.js', '.ts', '.java', '.go']:
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:50]  # First 50 lines
                        snippets.append(f"\n{file_path}:\n" + "".join(lines))
                except:
                    pass
        return "\n".join(snippets) if snippets else "No code snippets available"
    
    def _extract_section(self, response: str, section_name: str) -> str:
        """Extract a specific section from Bob's response"""
        try:
            lines = response.split('\n')
            section_lines = []
            in_section = False
            
            for line in lines:
                if section_name in line:
                    in_section = True
                    continue
                elif line.startswith('##') and in_section:
                    break
                elif in_section and line.strip():
                    section_lines.append(line)
            
            return '\n'.join(section_lines).strip()
        except:
            return "Not available"
    
    def _basic_analysis(self, impact_data: Dict[str, Any], changed_files: List[str]) -> Dict[str, Any]:
        """Basic analysis when Bob (LLM) is not available"""
        risk_level = impact_data.get('risk_level', 'UNKNOWN')
        affected_areas = impact_data.get('affected_areas', [])
        reviewers = impact_data.get('suggested_reviewers', [])
        warnings = impact_data.get('warnings', [])
        
        # Build basic analysis
        impact_prediction = f"This change affects {', '.join(changed_files)} → {len(affected_areas)} modules → {risk_level} risk"
        
        breakage_simulation = warnings[0].get('message', 'No historical data available') if warnings else "No similar failures found"
        
        smart_reviewer = f"Send this to {reviewers[0].get('name', 'Unknown')} ({int(reviewers[0].get('confidence', 0) * 100)}% ownership)" if reviewers else "No reviewer data available"
        
        learning_path = "Configure Mistral AI for learning path recommendations" if risk_level == "HIGH" else "Not needed - straightforward change"
        
        voice_explanation = f"This is a {risk_level} risk change affecting {len(affected_areas)} modules. Configure Mistral AI for detailed explanation."
        
        return {
            "success": True,
            "bob_enabled": False,
            "analysis": {
                "impact_prediction": impact_prediction,
                "breakage_simulation": breakage_simulation,
                "smart_reviewer": smart_reviewer,
                "learning_path": learning_path,
                "voice_explanation": voice_explanation,
                "full_response": "Bob (Mistral AI) not configured. Add MISTRAL_API_KEY to .env for AI-powered analysis."
            },
            "risk_level": risk_level,
            "risk_score": impact_data.get('risk_score', 0),
            "changed_files": changed_files
        }


# Singleton instance
_bob_analyzer = None


def get_bob_analyzer() -> BobAnalyzer:
    """Get or create Bob analyzer singleton"""
    global _bob_analyzer
    if _bob_analyzer is None:
        _bob_analyzer = BobAnalyzer()
    return _bob_analyzer

# Made with Bob
