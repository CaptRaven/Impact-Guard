"""
Configuration settings for ImpactGuard
"""
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "ImpactGuard API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Code change impact analysis system with AI-powered voice interaction"
    
    # IBM WatsonX Credentials
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_URL: Optional[str] = None
    
    # WatsonX NLU (Natural Language Understanding)
    WATSONX_NLU_API_KEY: Optional[str] = None
    WATSONX_NLU_URL: Optional[str] = None
    WATSONX_NLU_VERSION: str = "2022-04-07"
    
    # WatsonX TTS (Text-to-Speech)
    WATSONX_TTS_API_KEY: Optional[str] = None
    WATSONX_TTS_URL: Optional[str] = None
    WATSONX_TTS_VOICE: str = "en-US_AllisonV3Voice"  # Default voice
    
    # WatsonX STT (Speech-to-Text)
    WATSONX_STT_API_KEY: Optional[str] = None
    WATSONX_STT_URL: Optional[str] = None
    WATSONX_STT_MODEL: str = "en-US_Multimedia"
    
    # Mistral AI LLM
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-large-latest"  # Best for code reasoning
    MISTRAL_TEMPERATURE: float = 0.4  # Balance between creativity and precision
    
    # Risk Scoring Thresholds
    RISK_LOW_THRESHOLD: float = 0.3
    RISK_MEDIUM_THRESHOLD: float = 0.6
    RISK_HIGH_THRESHOLD: float = 0.6
    
    # Critical File Patterns
    CRITICAL_FILE_PATTERNS: List[str] = [
        "auth", "authentication", "login", "password",
        "payment", "billing", "transaction",
        "security", "encryption", "token",
        "database", "migration", "schema",
        "config", "settings", "env"
    ]
    
    # Analysis Settings
    MAX_DEPENDENCY_DEPTH: int = 3
    MIN_REVIEWER_CONFIDENCE: float = 0.5
    MAX_SUGGESTED_REVIEWERS: int = 5
    MAX_LEARNING_PATH_FILES: int = 5
    
    # Historical Analysis
    HISTORY_LOOKBACK_DAYS: int = 180
    MIN_COMMITS_FOR_HOTZONE: int = 10
    
    # Voice Output
    VOICE_ENABLED: bool = True
    VOICE_RATE: int = 150  # Words per minute
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Risk level mapping
RISK_LEVELS: Dict[str, str] = {
    "LOW": "Low risk - Standard review process",
    "MEDIUM": "Medium risk - Careful review recommended",
    "HIGH": "High risk - Thorough review and testing required"
}

# Made with Bob
