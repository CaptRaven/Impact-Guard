"""
Conversational Service
Integrates NLU, TTS, and STT for conversational interface
"""
from typing import Dict, Optional, List
from pathlib import Path
from services.watsonx_nlu_service import WatsonXNLUService
from services.watsonx_tts_service import WatsonXTTSService
from services.watsonx_stt_service import WatsonXSTTService
from services.impact_service import ImpactService
from services.mistral_llm_service import get_mistral_service
from models import ImpactReport


class ConversationalService:
    """Handles conversational interactions with voice and natural language"""
    
    def __init__(self, default_repo_path: Optional[str] = None):
        """
        Initialize conversational service
        
        Args:
            default_repo_path: Default repository path for analysis
        """
        self.nlu_service = WatsonXNLUService()
        self.tts_service = WatsonXTTSService()
        self.stt_service = WatsonXSTTService()
        self.llm_service = get_mistral_service()
        self.default_repo_path = default_repo_path
        self.conversation_history = []
    
    async def process_text_query(self, query: str, repo_path: Optional[str] = None) -> Dict:
        """
        Process a text query and return analysis with voice response
        
        Args:
            query: Natural language query
            repo_path: Repository path (uses default if not provided)
            
        Returns:
            Dictionary with analysis results and voice response
        """
        # Parse the query using NLU
        parsed_query = self.nlu_service.parse_query(query)
        
        # Determine repository path
        repo = repo_path or parsed_query.get('repository_path') or self.default_repo_path
        
        if not repo:
            return {
                'error': 'No repository path specified',
                'suggestion': 'Please specify a repository path in your query or set a default'
            }
        
        # Perform analysis based on parsed intent
        analysis_result = self._perform_analysis(parsed_query, repo)
        
        # Get code context for live analysis
        changed_files = [w.get('file') for w in analysis_result.get('warnings', []) if w.get('file')]
        # If no files in warnings, check affected areas
        if not changed_files:
            changed_files = analysis_result.get('affected_areas', [])[:3]
            
        code_context = self._read_code_snippets(repo, changed_files)
        
        # Generate contextual response
        # Priority: LLM reasoning > NLU template
        if self.llm_service.is_available():
            try:
                response_text = await self.llm_service.generate_conversational_summary(
                    analysis_result,
                    user_context=f"The user asked: {query}",
                    code_context=code_context
                )
            except Exception as e:
                print(f"LLM reasoning failed, falling back to NLU: {e}")
                response_text = self.nlu_service.generate_response_context(
                    parsed_query,
                    analysis_result
                )
        else:
            response_text = self.nlu_service.generate_response_context(
                parsed_query,
                analysis_result
            )
        
        # Generate voice response
        voice_audio = self.tts_service.synthesize_speech(response_text)
        
        # Store in conversation history
        self.conversation_history.append({
            'query': query,
            'parsed': parsed_query,
            'response': response_text
        })
        
        return {
            'query': query,
            'parsed_query': parsed_query,
            'analysis': analysis_result,
            'response_text': response_text,
            'has_voice': voice_audio is not None,
            'conversation_id': len(self.conversation_history),
            'llm_enhanced': self.llm_service.is_available(),
            'live_files': changed_files
        }

    def _read_code_snippets(self, repository_path: str, file_paths: List[str]) -> Dict[str, str]:
        """Read first 50 lines of each file"""
        snippets = {}
        for file_path in file_paths[:5]:  # Limit to 5 files
            full_path = Path(repository_path) / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:50]  # First 50 lines
                        snippets[file_path] = "".join(lines)
                except:
                    pass
        return snippets
    
    async def process_voice_query(self, audio_file_path: str, repo_path: Optional[str] = None, content_type: Optional[str] = None) -> Dict:
        """
        Process a voice query (audio file) and return analysis with voice response
        
        Args:
            audio_file_path: Path to audio file containing query
            repo_path: Repository path (uses default if not provided)
            content_type: Optional MIME type of audio data
            
        Returns:
            Dictionary with analysis results and voice response
        """
        # Transcribe audio to text
        transcript = self.stt_service.transcribe_audio_file(audio_file_path, content_type)
        
        if not transcript:
            return {
                'error': 'Failed to transcribe audio',
                'suggestion': 'Please ensure audio is clear and in a supported format'
            }
        
        # Process as text query
        result = await self.process_text_query(transcript, repo_path)
        result['transcript'] = transcript
        result['input_type'] = 'voice'
        
        return result
    
    async def process_voice_data(self, audio_data: bytes, repo_path: Optional[str] = None) -> Dict:
        """
        Process voice data (bytes) and return analysis with voice response
        
        Args:
            audio_data: Audio data as bytes
            repo_path: Repository path (uses default if not provided)
            
        Returns:
            Dictionary with analysis results and voice response
        """
        # Transcribe audio to text
        transcript = self.stt_service.transcribe_audio_data(audio_data)
        
        if not transcript:
            return {
                'error': 'Failed to transcribe audio',
                'suggestion': 'Please ensure audio is clear and in a supported format'
            }
        
        # Process as text query
        result = await self.process_text_query(transcript, repo_path)
        result['transcript'] = transcript
        result['input_type'] = 'voice'
        
        return result
    
    def _perform_analysis(self, parsed_query: Dict, repo_path: str) -> Dict:
        """
        Perform analysis based on parsed query
        
        Args:
            parsed_query: Parsed query information
            repo_path: Repository path
            
        Returns:
            Analysis results
        """
        intent = parsed_query.get('intent', 'analyze')
        files = parsed_query.get('files', [])
        
        # Initialize impact service
        impact_service = ImpactService(repo_path)
        
        # Perform analysis based on files or areas
        if files:
            report = impact_service.analyze_specific_files(files)
        else:
            # Analyze uncommitted changes
            from models import ChangeInput
            change_input = ChangeInput(
                repository_path=repo_path,
                branch='main'
            )
            report = impact_service.analyze_impact(change_input)
        
        # Convert report to dict
        return report.dict()
    
    def get_voice_response(self, response_text: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Generate voice response for given text
        
        Args:
            response_text: Text to convert to speech
            output_path: Optional path to save audio
            
        Returns:
            Audio data as bytes
        """
        return self.tts_service.synthesize_speech(response_text, output_path)
    
    def get_conversation_history(self, limit: int = 10) -> list:
        """
        Get recent conversation history
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of recent conversations
        """
        return self.conversation_history[-limit:]
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def set_default_repository(self, repo_path: str):
        """
        Set default repository path
        
        Args:
            repo_path: Repository path
        """
        self.default_repo_path = repo_path
    
    def get_conversation_summary(self) -> Dict:
        """
        Get summary of conversation session
        
        Returns:
            Summary statistics
        """
        return {
            'total_queries': len(self.conversation_history),
            'nlu_available': self.nlu_service.nlu is not None,
            'tts_available': self.tts_service.tts is not None,
            'stt_available': self.stt_service.stt is not None,
            'default_repo': self.default_repo_path
        }
    
    async def process_follow_up(self, query: str) -> Dict:
        """
        Process a follow-up query using conversation context
        
        Args:
            query: Follow-up query
            
        Returns:
            Analysis results
        """
        # Get context from last conversation
        if not self.conversation_history:
            return await self.process_text_query(query)
        
        last_conversation = self.conversation_history[-1]
        last_parsed = last_conversation.get('parsed', {})
        
        # Use repository from last query if not specified
        repo_path = last_parsed.get('repository_path') or self.default_repo_path
        
        return await self.process_text_query(query, repo_path)

# Made with Bob
