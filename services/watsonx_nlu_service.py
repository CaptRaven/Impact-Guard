"""
WatsonX NLU Service
Natural Language Understanding for query interpretation
"""
from typing import Dict, List, Optional
import re
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, ConceptsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from config import settings


class WatsonXNLUService:
    """Handles natural language query understanding using IBM WatsonX NLU"""
    
    def __init__(self):
        """Initialize WatsonX NLU service"""
        self.nlu = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the NLU service with credentials"""
        if not settings.WATSONX_NLU_API_KEY or not settings.WATSONX_NLU_URL:
            print("Warning: WatsonX NLU credentials not configured")
            return
        
        try:
            authenticator = IAMAuthenticator(settings.WATSONX_NLU_API_KEY)
            self.nlu = NaturalLanguageUnderstandingV1(
                version=settings.WATSONX_NLU_VERSION,
                authenticator=authenticator
            )
            self.nlu.set_service_url(settings.WATSONX_NLU_URL)
        except Exception as e:
            print(f"Failed to initialize WatsonX NLU: {str(e)}")
            self.nlu = None
    
    def parse_query(self, query: str) -> Dict:
        """
        Parse natural language query and extract intent and entities
        
        Args:
            query: Natural language query from user
            
        Returns:
            Dictionary with parsed intent and entities
        """
        # Pre-process query to fix common STT misinterpretations
        sanitized_query = self._sanitize_stt_transcript(query)
        
        # First try rule-based parsing for common patterns
        rule_based_result = self._rule_based_parse(sanitized_query)
        
        # If NLU is available, enhance with AI understanding
        if self.nlu:
            try:
                nlu_result = self._nlu_parse(sanitized_query)
                # Merge results, prioritizing NLU insights
                return self._merge_results(rule_based_result, nlu_result)
            except Exception as e:
                print(f"NLU parsing failed, using rule-based: {str(e)}")
                return rule_based_result
        
        return rule_based_result

    def _sanitize_stt_transcript(self, transcript: str) -> str:
        """
        Fix common STT misinterpretations of technical terms
        """
        replacements = {
            r'\bconcede\b': 'config.py',
            r'\bconcede dot pi\b': 'config.py',
            r'\bconcord\b': 'config.py',
            r'\bmodels dot pi\b': 'models.py',
            r'\bmain dot pi\b': 'main.py',
            r'\banalyze\b': 'analyze',
            r'\banalysed\b': 'analyze',
            r'\bimpact guard\b': 'ImpactGuard',
            r'\bguard\b': 'Guard'
        }
        
        sanitized = transcript.lower()
        for pattern, replacement in replacements.items():
            sanitized = re.sub(pattern, replacement, sanitized)
            
        return sanitized
    
    def _rule_based_parse(self, query: str) -> Dict:
        """
        Rule-based query parsing for common patterns
        
        Args:
            query: User query
            
        Returns:
            Parsed query information
        """
        query_lower = query.lower()
        
        # Determine intent
        intent = "analyze"  # Default intent
        if any(word in query_lower for word in ["risk", "risky", "dangerous", "safe"]):
            intent = "assess_risk"
        elif any(word in query_lower for word in ["review", "reviewer", "who should"]):
            intent = "suggest_reviewers"
        elif any(word in query_lower for word in ["learn", "understand", "study", "read"]):
            intent = "learning_path"
        elif any(word in query_lower for word in ["history", "past", "previous", "before"]):
            intent = "historical_analysis"
        elif any(word in query_lower for word in ["summary", "summarize", "brief", "quick"]):
            intent = "quick_summary"
        
        # Extract file paths
        file_patterns = [
            r'[\w/\-\.]+\.(py|js|ts|jsx|tsx|java|cpp|c|go|rb|php)',  # File extensions
            r'[\w/\-]+/[\w\-]+',  # Path-like patterns
        ]
        
        files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, query)
            files.extend(matches)
        
        # Extract areas/modules
        areas = []
        area_keywords = {
            'auth': ['auth', 'authentication', 'login', 'user', 'password'],
            'payment': ['payment', 'billing', 'transaction', 'checkout'],
            'api': ['api', 'endpoint', 'route', 'controller'],
            'database': ['database', 'db', 'model', 'schema', 'migration'],
            'frontend': ['frontend', 'ui', 'component', 'view'],
            'backend': ['backend', 'server', 'service']
        }
        
        for area, keywords in area_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                areas.append(area)
        
        # Determine repository path (if mentioned)
        repo_path = None
        repo_match = re.search(r'(?:repo|repository|project)\s+(?:at|in|from)?\s*([^\s]+)', query_lower)
        if repo_match:
            repo_path = repo_match.group(1)
        
        return {
            'intent': intent,
            'files': list(set(files)),
            'areas': list(set(areas)),
            'repository_path': repo_path,
            'original_query': query,
            'confidence': 0.7  # Rule-based confidence
        }
    
    def _nlu_parse(self, query: str) -> Dict:
        """
        Use WatsonX NLU to parse query
        
        Args:
            query: User query
            
        Returns:
            NLU analysis results
        """
        response = self.nlu.analyze(
            text=query,
            features=Features(
                entities=EntitiesOptions(sentiment=False, limit=10),
                keywords=KeywordsOptions(sentiment=False, limit=10),
                concepts=ConceptsOptions(limit=5)
            )
        ).get_result()
        
        # Extract entities (files, paths, etc.)
        entities = []
        for entity in response.get('entities', []):
            entities.append({
                'text': entity['text'],
                'type': entity['type'],
                'relevance': entity['relevance']
            })
        
        # Extract keywords
        keywords = [kw['text'] for kw in response.get('keywords', [])]
        
        # Extract concepts
        concepts = [c['text'] for c in response.get('concepts', [])]
        
        return {
            'entities': entities,
            'keywords': keywords,
            'concepts': concepts,
            'nlu_confidence': 0.9
        }
    
    def _merge_results(self, rule_based: Dict, nlu_result: Dict) -> Dict:
        """
        Merge rule-based and NLU results
        
        Args:
            rule_based: Rule-based parsing results
            nlu_result: NLU parsing results
            
        Returns:
            Merged results
        """
        # Start with rule-based results
        merged = rule_based.copy()
        
        # Enhance with NLU entities
        if 'entities' in nlu_result:
            for entity in nlu_result['entities']:
                if entity['type'] in ['File', 'Path', 'Location']:
                    merged['files'].append(entity['text'])
        
        # Add NLU keywords to areas if relevant
        if 'keywords' in nlu_result:
            for keyword in nlu_result['keywords']:
                keyword_lower = keyword.lower()
                if any(area in keyword_lower for area in ['auth', 'payment', 'api', 'database']):
                    merged['areas'].append(keyword_lower)
        
        # Update confidence
        merged['confidence'] = max(rule_based['confidence'], nlu_result.get('nlu_confidence', 0.7))
        merged['nlu_enhanced'] = True
        
        # Deduplicate
        merged['files'] = list(set(merged['files']))
        merged['areas'] = list(set(merged['areas']))
        
        return merged
    
    def generate_response_context(self, parsed_query: Dict, analysis_result: Dict) -> str:
        """
        Generate contextual response based on query intent
        
        Args:
            parsed_query: Parsed query information
            analysis_result: Analysis results
            
        Returns:
            Contextual response text
        """
        intent = parsed_query.get('intent', 'analyze')
        
        if intent == 'assess_risk':
            return self._format_risk_response(analysis_result)
        elif intent == 'suggest_reviewers':
            return self._format_reviewer_response(analysis_result)
        elif intent == 'learning_path':
            return self._format_learning_path_response(analysis_result)
        elif intent == 'historical_analysis':
            return self._format_historical_response(analysis_result)
        elif intent == 'quick_summary':
            return self._format_quick_summary(analysis_result)
        else:
            return self._format_general_response(analysis_result)
    
    def _format_risk_response(self, result: Dict) -> str:
        """Format risk-focused response"""
        risk_level = result.get('risk_level', 'UNKNOWN')
        risk_score = result.get('risk_score', 0)
        
        response = f"Risk Assessment: {risk_level} (Score: {risk_score:.2f}). "
        
        if result.get('critical_files'):
            response += f"Critical files affected: {', '.join(result['critical_files'][:3])}. "
        
        if result.get('warnings'):
            response += f"Key warning: {result['warnings'][0]['message']}. "
        
        return response
    
    def _format_reviewer_response(self, result: Dict) -> str:
        """Format reviewer suggestion response"""
        reviewers = result.get('suggested_reviewers', [])
        
        if not reviewers:
            return "No reviewer suggestions available based on the analysis."
        
        response = "Recommended reviewers: "
        reviewer_list = [f"{r['name']} (confidence: {r['confidence']:.0%})" for r in reviewers[:3]]
        response += ", ".join(reviewer_list) + ". "
        
        return response
    
    def _format_learning_path_response(self, result: Dict) -> str:
        """Format learning path response"""
        learning_path = result.get('learning_path', [])
        
        if not learning_path:
            return "No specific learning path recommended for these changes."
        
        response = "Recommended files to study: "
        files = [f"{item['file']} ({item['reason']})" for item in learning_path[:3]]
        response += "; ".join(files) + ". "
        
        return response
    
    def _format_historical_response(self, result: Dict) -> str:
        """Format historical analysis response"""
        metadata = result.get('metadata', {})
        hot_zones = metadata.get('hot_zones', [])
        
        if not hot_zones:
            return "No significant historical patterns detected for these files."
        
        response = f"Historical analysis shows {len(hot_zones)} high-change areas. "
        if hot_zones:
            response += f"Most active: {hot_zones[0]['file']} with {hot_zones[0]['change_count']} recent changes. "
        
        return response
    
    def _format_quick_summary(self, result: Dict) -> str:
        """Format quick summary response"""
        return f"Risk: {result.get('risk_level', 'UNKNOWN')}, " \
               f"Affected areas: {len(result.get('affected_areas', []))}, " \
               f"Warnings: {len(result.get('warnings', []))}. "
    
    def _format_general_response(self, result: Dict) -> str:
        """Format general analysis response"""
        return f"Analysis complete. Risk level: {result.get('risk_level', 'UNKNOWN')}, " \
               f"Score: {result.get('risk_score', 0):.2f}. " \
               f"{len(result.get('affected_areas', []))} areas affected. "

# Made with Bob
