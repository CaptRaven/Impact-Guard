"""
WatsonX TTS Service
High-quality Text-to-Speech using IBM WatsonX
"""
from typing import Optional
import os
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from models import ImpactReport, RiskLevel
from config import settings


class WatsonXTTSService:
    """Handles text-to-speech conversion using IBM WatsonX TTS"""
    
    def __init__(self):
        """Initialize WatsonX TTS service"""
        self.tts = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the TTS service with credentials"""
        if not settings.WATSONX_TTS_API_KEY or not settings.WATSONX_TTS_URL:
            print("Warning: WatsonX TTS credentials not configured")
            return
        
        try:
            authenticator = IAMAuthenticator(settings.WATSONX_TTS_API_KEY)
            self.tts = TextToSpeechV1(authenticator=authenticator)
            self.tts.set_service_url(settings.WATSONX_TTS_URL)
        except Exception as e:
            print(f"Failed to initialize WatsonX TTS: {str(e)}")
            self.tts = None
    
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
    
    def synthesize_speech(self, text: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech using WatsonX TTS
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file
            
        Returns:
            Audio data as bytes, or None if failed
        """
        if not self.tts:
            print("WatsonX TTS not initialized")
            return None
        
        try:
            # Synthesize speech
            response = self.tts.synthesize(
                text=text,
                voice=settings.WATSONX_TTS_VOICE,
                accept='audio/wav'
            ).get_result()
            
            # The result from synthesize() is already the audio content (bytes)
            audio_data = response
            
            if hasattr(response, 'content'):
                audio_data = response.content
            
            # Save to file if path provided
            if output_path:
                with open(output_path, 'wb') as audio_file:
                    audio_file.write(audio_data)
                print(f"Audio saved to: {output_path}")
            
            return audio_data
        
        except Exception as e:
            print(f"Speech synthesis failed: {str(e)}")
            return None
    
    def speak_report(self, report: ImpactReport, save_path: Optional[str] = None) -> bool:
        """
        Generate and optionally save speech for impact report
        
        Args:
            report: Impact report
            save_path: Optional path to save audio file
            
        Returns:
            True if successful, False otherwise
        """
        summary = self.generate_voice_summary(report)
        if not summary:
            return False
        
        audio_data = self.synthesize_speech(summary, save_path)
        return audio_data is not None
    
    def speak_text(self, text: str, save_path: Optional[str] = None) -> bool:
        """
        Convert any text to speech
        
        Args:
            text: Text to speak
            save_path: Optional path to save audio file
            
        Returns:
            True if successful, False otherwise
        """
        audio_data = self.synthesize_speech(text, save_path)
        return audio_data is not None
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices
        
        Returns:
            List of available voice names
        """
        if not self.tts:
            return []
        
        try:
            voices = self.tts.list_voices().get_result()
            return [voice['name'] for voice in voices.get('voices', [])]
        except Exception as e:
            print(f"Failed to get voices: {str(e)}")
            return []
    
    def set_voice(self, voice_name: str) -> bool:
        """
        Set the voice to use for synthesis
        
        Args:
            voice_name: Name of the voice
            
        Returns:
            True if successful, False otherwise
        """
        available_voices = self.get_available_voices()
        if voice_name in available_voices:
            settings.WATSONX_TTS_VOICE = voice_name
            return True
        return False
    
    def generate_contextual_response(self, text: str, context: str = "neutral") -> str:
        """
        Generate contextually appropriate speech text
        
        Args:
            text: Base text
            context: Context (urgent, warning, success, neutral)
            
        Returns:
            Enhanced text with appropriate tone markers
        """
        # Add SSML-like markers for emphasis based on context
        if context == "urgent":
            return f"<emphasis level='strong'>{text}</emphasis>"
        elif context == "warning":
            return f"<prosody rate='slow'>{text}</prosody>"
        elif context == "success":
            return f"<prosody pitch='+5%'>{text}</prosody>"
        else:
            return text

# Made with Bob
