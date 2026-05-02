"""
Voice Output Service
Converts impact reports to spoken explanations
"""
from typing import Optional
import pyttsx3
from models import ImpactReport, RiskLevel


class VoiceService:
    """Handles text-to-speech conversion for impact reports"""
    
    def __init__(self):
        """Initialize the voice service"""
        self.engine = None
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Words per minute
        except Exception:
            # Voice engine not available
            pass
    
    def generate_voice_summary(self, report: ImpactReport) -> Optional[str]:
        """
        Generate a concise voice summary of the impact report
        
        Args:
            report: Impact report
            
        Returns:
            Voice summary text (under 30 seconds when spoken)
        """
        summary_parts = []
        
        # Risk level announcement
        risk_text = self._get_risk_announcement(report.risk_level, report.risk_score)
        summary_parts.append(risk_text)
        
        # Affected areas
        if report.affected_areas:
            areas_text = f"Affected areas: {', '.join(report.affected_areas[:3])}"
            summary_parts.append(areas_text)
        
        # Critical files warning
        if report.critical_files:
            critical_count = len(report.critical_files)
            if critical_count == 1:
                summary_parts.append(f"One critical file affected: {report.critical_files[0]}")
            else:
                summary_parts.append(f"{critical_count} critical files affected")
        
        # Top warnings
        if report.warnings:
            top_warning = report.warnings[0]
            summary_parts.append(f"Warning: {top_warning.message}")
        
        # Reviewer suggestion
        if report.suggested_reviewers:
            top_reviewer = report.suggested_reviewers[0]
            summary_parts.append(f"Recommended reviewer: {top_reviewer.name}")
        
        # Final recommendation
        if report.risk_level == RiskLevel.HIGH:
            summary_parts.append("Thorough review and testing required before proceeding")
        elif report.risk_level == RiskLevel.MEDIUM:
            summary_parts.append("Careful review recommended")
        
        return ". ".join(summary_parts) + "."
    
    def _get_risk_announcement(self, risk_level: RiskLevel, score: float) -> str:
        """
        Get risk level announcement text
        
        Args:
            risk_level: Risk level
            score: Risk score
            
        Returns:
            Announcement text
        """
        if risk_level == RiskLevel.HIGH:
            return f"High risk detected with score {score:.2f}"
        elif risk_level == RiskLevel.MEDIUM:
            return f"Medium risk detected with score {score:.2f}"
        else:
            return f"Low risk detected with score {score:.2f}"
    
    def speak(self, text: str) -> bool:
        """
        Speak the given text
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            return False
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception:
            return False
    
    def save_to_audio(self, text: str, output_path: str) -> bool:
        """
        Save text as audio file
        
        Args:
            text: Text to convert
            output_path: Path to save audio file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            return False
        
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return True
        except Exception:
            return False

# Made with Bob
