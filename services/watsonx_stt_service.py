"""
WatsonX STT Service
Speech-to-Text for voice input using IBM WatsonX
"""
from typing import Optional, Dict
import os
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from config import settings


class WatsonXSTTService:
    """Handles speech-to-text conversion using IBM WatsonX STT"""
    
    def __init__(self):
        """Initialize WatsonX STT service"""
        self.stt = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the STT service with credentials"""
        if not settings.WATSONX_STT_API_KEY or not settings.WATSONX_STT_URL:
            print("Warning: WatsonX STT credentials not configured")
            return
        
        try:
            authenticator = IAMAuthenticator(settings.WATSONX_STT_API_KEY)
            self.stt = SpeechToTextV1(authenticator=authenticator)
            self.stt.set_service_url(settings.WATSONX_STT_URL)
        except Exception as e:
            print(f"Failed to initialize WatsonX STT: {str(e)}")
            self.stt = None
    
    def transcribe_audio_file(self, audio_file_path: str, content_type: Optional[str] = None) -> Optional[str]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            content_type: Optional MIME type of audio data
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.stt:
            print("WatsonX STT not initialized")
            return None
        
        if not os.path.exists(audio_file_path):
            print(f"Audio file not found: {audio_file_path}")
            return None
        
        # Use provided content_type or determine from extension
        # Fallback to extension if content_type is generic application/octet-stream
        actual_content_type = content_type
        if not actual_content_type or actual_content_type == 'application/octet-stream':
            actual_content_type = self._get_content_type(audio_file_path)
        
        # Sanitize MIME type for IBM Watson compatibility
        actual_content_type = self._sanitize_content_type(actual_content_type)
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = self.stt.recognize(
                    audio=audio_file,
                    content_type=actual_content_type,
                    model=settings.WATSONX_STT_MODEL,
                    timestamps=False,
                    word_confidence=False,
                    smart_formatting=True,
                    end_of_phrase_silence_time=1.0
                ).get_result()
            
            # Extract transcript
            transcript = self._extract_transcript(response)
            return transcript
        
        except Exception as e:
            print(f"Transcription failed ({actual_content_type}): {str(e)}")
            return None
    
    def transcribe_audio_data(self, audio_data: bytes, content_type: str = 'audio/wav') -> Optional[str]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Audio data as bytes
            content_type: MIME type of audio data
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.stt:
            print("WatsonX STT not initialized")
            return None
        
        # Sanitize MIME type
        actual_content_type = self._sanitize_content_type(content_type)
        
        try:
            response = self.stt.recognize(
                audio=audio_data,
                content_type=actual_content_type,
                model=settings.WATSONX_STT_MODEL,
                timestamps=False,
                word_confidence=False,
                smart_formatting=True,
                end_of_phrase_silence_time=1.0
            ).get_result()
            
            # Extract transcript
            transcript = self._extract_transcript(response)
            return transcript
        
        except Exception as e:
            print(f"Transcription failed ({actual_content_type}): {str(e)}")
            return None
    
    def _sanitize_content_type(self, content_type: str) -> str:
        """
        Sanitize MIME type for IBM Watson compatibility
        
        Args:
            content_type: Original MIME type
            
        Returns:
            Sanitized MIME type string
        """
        if not content_type:
            return 'audio/wav'
            
        # Extract the base type (remove codecs, etc.)
        base_type = content_type.split(';')[0].strip().lower()
        
        # Mapping for common browser variations
        mapping = {
            'audio/x-wav': 'audio/wav',
            'audio/vnd.wav': 'audio/wav',
            'audio/mp4': 'audio/mp4',
            'audio/m4a': 'audio/mp4',
            'audio/x-m4a': 'audio/mp4',
            'audio/mpeg': 'audio/mpeg',
            'audio/x-mpeg': 'audio/mpeg',
            'audio/mp3': 'audio/mpeg',
            'audio/x-mp3': 'audio/mpeg',
            'audio/webm': 'audio/webm',
            'audio/ogg': 'audio/ogg'
        }
        
        sanitized = mapping.get(base_type, base_type)
        
        # IBM Watson specific: for webm and ogg, it often prefers/requires opus codec info
        # but for mp4 it is often forbidden to include extra codec info.
        if 'opus' in content_type.lower() and ('webm' in sanitized or 'ogg' in sanitized):
            return f"{sanitized};codecs=opus"
            
        # If the model is Multimedia, it is much more flexible with containers
        return sanitized

    def transcribe_with_details(self, audio_file_path: str) -> Optional[Dict]:
        """
        Transcribe audio with detailed information
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dictionary with transcript and metadata
        """
        if not self.stt:
            print("WatsonX STT not initialized")
            return None
        
        if not os.path.exists(audio_file_path):
            print(f"Audio file not found: {audio_file_path}")
            return None
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = self.stt.recognize(
                    audio=audio_file,
                    content_type=self._get_content_type(audio_file_path),
                    model=settings.WATSONX_STT_MODEL,
                    timestamps=True,
                    word_confidence=True,
                    speaker_labels=False
                ).get_result()
            
            # Extract detailed information
            results = response.get('results', [])
            if not results:
                return None
            
            transcript = self._extract_transcript(response)
            
            # Get word-level details
            words = []
            for result in results:
                for alternative in result.get('alternatives', []):
                    if 'timestamps' in alternative:
                        for word_info in alternative['timestamps']:
                            words.append({
                                'word': word_info[0],
                                'start_time': word_info[1],
                                'end_time': word_info[2]
                            })
            
            # Get confidence scores
            confidences = []
            for result in results:
                for alternative in result.get('alternatives', []):
                    if 'word_confidence' in alternative:
                        confidences.extend([wc[1] for wc in alternative['word_confidence']])
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'transcript': transcript,
                'words': words,
                'confidence': avg_confidence,
                'word_count': len(words)
            }
        
        except Exception as e:
            print(f"Detailed transcription failed: {str(e)}")
            return None
    
    def _extract_transcript(self, response: Dict) -> str:
        """
        Extract transcript text from STT response
        
        Args:
            response: STT API response
            
        Returns:
            Transcript text
        """
        results = response.get('results', [])
        if not results:
            return ""
        
        transcripts = []
        for result in results:
            alternatives = result.get('alternatives', [])
            if alternatives:
                transcripts.append(alternatives[0].get('transcript', ''))
        
        return ' '.join(transcripts).strip()
    
    def _get_content_type(self, file_path: str) -> str:
        """
        Determine content type from file extension
        
        Args:
            file_path: Path to audio file
            
        Returns:
            MIME type string
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mp3',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
            '.m4a': 'audio/mp4',
            '.mp4': 'audio/mp4'
        }
        
        return content_types.get(ext, 'audio/wav')
    
    def get_available_models(self) -> list:
        """
        Get list of available STT models
        
        Returns:
            List of available model names
        """
        if not self.stt:
            return []
        
        try:
            models = self.stt.list_models().get_result()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            print(f"Failed to get models: {str(e)}")
            return []
    
    def set_model(self, model_name: str) -> bool:
        """
        Set the model to use for recognition
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if successful, False otherwise
        """
        available_models = self.get_available_models()
        if model_name in available_models:
            settings.WATSONX_STT_MODEL = model_name
            return True
        return False
    
    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate if audio file is suitable for transcription
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        valid_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.webm']
        
        if ext not in valid_extensions:
            print(f"Unsupported audio format: {ext}")
            return False
        
        # Check file size (max 100MB for most STT services)
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB
        
        if file_size > max_size:
            print(f"Audio file too large: {file_size / (1024*1024):.2f}MB")
            return False
        
        return True

# Made with Bob
