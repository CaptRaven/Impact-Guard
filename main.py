"""
ImpactGuard FastAPI Application with WatsonX Integration
Main entry point for the API with conversational AI capabilities
"""
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os
import io
from pathlib import Path

from models import ChangeInput, ImpactReport, FileChange
from services import ImpactService, ConversationalService
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global conversational service instance
conversational_service = ConversationalService()


@app.get("/")
async def root():
    """Serve the demo UI"""
    return FileResponse("static/index.html")


@app.get("/api")
async def api_info():
    """API information endpoint"""
    from services import get_mistral_service
    mistral = get_mistral_service()
    
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "status": "operational",
        "features": {
            "impact_analysis": True,
            "watsonx_nlu": settings.WATSONX_NLU_API_KEY is not None,
            "watsonx_tts": settings.WATSONX_TTS_API_KEY is not None,
            "watsonx_stt": settings.WATSONX_STT_API_KEY is not None,
            "conversational_ai": True,
            "mistral_llm": mistral.is_available(),
            "ai_pair_programming": mistral.is_available()
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from services import get_mistral_service
    mistral = get_mistral_service()
    
    return {
        "status": "healthy",
        "services": {
            "nlu": settings.WATSONX_NLU_API_KEY is not None,
            "tts": settings.WATSONX_TTS_API_KEY is not None,
            "stt": settings.WATSONX_STT_API_KEY is not None,
            "mistral_llm": mistral.is_available()
        }
    }


# ============================================================================
# CONVERSATIONAL AI ENDPOINTS (WatsonX Integration)
# ============================================================================

@app.post("/conversation/query")
async def conversational_query(
    query: str = Body(..., embed=True),
    repository_path: Optional[str] = Body(None, embed=True)
):
    """
    Process natural language query and return analysis with voice response
    
    Args:
        query: Natural language query (e.g., "analyze my auth changes")
        repository_path: Optional repository path
        
    Returns:
        Analysis results with contextual response
    """
    try:
        result = await conversational_service.process_text_query(query, repository_path)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@app.post("/conversation/voice-query")
async def voice_query(
    audio: UploadFile = File(...),
    repository_path: Optional[str] = Body(None)
):
    """
    Process voice query (audio file) and return analysis with voice response
    
    Args:
        audio: Audio file containing voice query
        repository_path: Optional repository path
        
    Returns:
        Analysis results with transcript and voice response
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{audio.filename}"
        with open(temp_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Process voice query
        result = await conversational_service.process_voice_query(temp_path, repository_path, content_type=audio.content_type)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice query processing failed: {str(e)}"
        )


@app.post("/conversation/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...)
):
    """
    Transcribe audio file to text
    
    Args:
        audio: Audio file to transcribe
        
    Returns:
        Transcription text and confidence
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{audio.filename}"
        with open(temp_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Transcribe
        transcript = conversational_service.stt_service.transcribe_audio_file(temp_path, content_type=audio.content_type)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if not transcript:
            return {"text": "", "confidence": 0, "error": "Failed to transcribe"}
            
        return {"text": transcript, "confidence": 0.9}  # Dummy confidence for now
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@app.post("/conversation/voice-response")
async def get_voice_response(
    text: str = Body(..., embed=True)
):
    """
    Generate voice response for given text
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Audio file (WAV format)
    """
    try:
        audio_data = conversational_service.get_voice_response(text)
        
        if not audio_data:
            raise HTTPException(
                status_code=500,
                detail="Voice synthesis failed"
            )
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=response.wav"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice response generation failed: {str(e)}"
        )


@app.get("/conversation/history")
async def get_conversation_history(limit: int = 10):
    """
    Get conversation history
    
    Args:
        limit: Maximum number of conversations to return
        
    Returns:
        List of recent conversations
    """
    try:
        history = conversational_service.get_conversation_history(limit)
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@app.delete("/conversation/history")
async def clear_conversation_history():
    """Clear conversation history"""
    try:
        conversational_service.clear_conversation_history()
        return {"message": "Conversation history cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear history: {str(e)}"
        )


@app.post("/conversation/set-repository")
async def set_default_repository(
    repository_path: str = Body(..., embed=True)
):
    """
    Set default repository for conversation session
    
    Args:
        repository_path: Path to repository
        
    Returns:
        Confirmation message
    """
    try:
        if not os.path.exists(repository_path):
            raise HTTPException(
                status_code=400,
                detail=f"Repository path does not exist: {repository_path}"
            )
        
        conversational_service.set_default_repository(repository_path)
        return {
            "message": "Default repository set",
            "repository_path": repository_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set repository: {str(e)}"
        )


@app.get("/conversation/summary")
async def get_conversation_summary():
    """Get conversation session summary"""
    try:
        summary = conversational_service.get_conversation_summary()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary: {str(e)}"
        )


# ============================================================================
# STANDARD IMPACT ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/analyze", response_model=ImpactReport)
async def analyze_changes(change_input: ChangeInput):
    """
    Analyze code changes and return impact report
    
    Args:
        change_input: Change input containing repository path and changed files
        
    Returns:
        Complete impact report
    """
    try:
        # Validate repository path
        if not os.path.exists(change_input.repository_path):
            raise HTTPException(
                status_code=400,
                detail=f"Repository path does not exist: {change_input.repository_path}"
            )
        
        # Initialize service with repository path
        service = ImpactService(change_input.repository_path)
        
        # Perform analysis
        report = service.analyze_impact(change_input)
        
        return report
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/files", response_model=ImpactReport)
async def analyze_specific_files(
    repository_path: str = Body(..., embed=True),
    file_paths: List[str] = Body(..., embed=True)
):
    """
    Analyze specific files in a repository
    
    Args:
        repository_path: Path to the git repository
        file_paths: List of file paths to analyze
        
    Returns:
        Impact report
    """
    try:
        # Validate repository path
        if not os.path.exists(repository_path):
            raise HTTPException(
                status_code=400,
                detail=f"Repository path does not exist: {repository_path}"
            )
        
        # Initialize service
        service = ImpactService(repository_path)
        
        # Analyze files
        report = service.analyze_specific_files(file_paths)
        
        return report
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/diff")
async def analyze_diff(
    repository_path: str = Body(..., embed=True),
    branch: str = Body(default="main", embed=True)
):
    """
    Analyze uncommitted changes in a repository
    
    Args:
        repository_path: Path to the git repository
        branch: Branch to compare against (default: main)
        
    Returns:
        Impact report
    """
    try:
        # Validate repository path
        if not os.path.exists(repository_path):
            raise HTTPException(
                status_code=400,
                detail=f"Repository path does not exist: {repository_path}"
            )
        
        # Initialize service
        service = ImpactService(repository_path)
        
        # Create change input
        change_input = ChangeInput(
            repository_path=repository_path,
            branch=branch
        )
        
        # Analyze changes
        report = service.analyze_impact(change_input)
        
        return report
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/summary")
async def get_summary(
    repository_path: str = Body(..., embed=True),
    file_paths: List[str] = Body(..., embed=True)
):
    """
    Get a quick summary of impact analysis
    
    Args:
        repository_path: Path to the git repository
        file_paths: List of file paths to analyze
        
    Returns:
        Quick summary text
    """
    try:
        # Initialize service
        service = ImpactService(repository_path)
        
        # Analyze files
        report = service.analyze_specific_files(file_paths)
        
        # Get summary
        summary = service.get_quick_summary(report)
        
        return {
            "summary": summary,
            "risk_level": report.risk_level.value,
            "risk_score": report.risk_score
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {str(e)}"
        )

# ============================================================================
# MISTRAL AI LLM ENDPOINTS - Deep Code Reasoning & AI Pair Programming
# ============================================================================

@app.post("/llm/explain-risk")
async def explain_risk_reasoning(
    repository_path: str = Body(...),
    file_paths: List[str] = Body(...),
    include_code: bool = Body(False)
):
    """
    Get deep "WHY" explanation of risks using Mistral AI LLM
    
    Args:
        repository_path: Path to the git repository
        file_paths: List of file paths to analyze
        include_code: Whether to include actual code content for deeper analysis
        
    Returns:
        Human-readable explanation of WHY the change is risky
    """
    try:
        from services import get_mistral_service
        
        # Get impact analysis
        service = ImpactService(repository_path)
        report = service.analyze_specific_files(file_paths)
        
        # Get code context if requested
        code_context = None
        if include_code:
            code_context = {}
            for file_path in file_paths[:5]:  # Limit to 5 files
                full_path = Path(repository_path) / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            code_context[file_path] = f.read()
                    except:
                        pass
        
        # Get LLM explanation
        mistral = get_mistral_service()
        explanation = await mistral.explain_risk_reasoning(
            report.dict(),
            code_context
        )
        
        return {
            "explanation": explanation,
            "risk_level": report.risk_level.value,
            "risk_score": report.risk_score,
            "llm_enabled": mistral.is_available()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk explanation failed: {str(e)}"
        )


@app.post("/llm/conversational-summary")
async def get_conversational_summary(
    repository_path: str = Body(...),
    file_paths: List[str] = Body(...),
    user_context: Optional[str] = Body(None)
):
    """
    Get a truly conversational, human-like summary from Mistral AI
    
    Args:
        repository_path: Path to the git repository
        file_paths: List of file paths to analyze
        user_context: Optional context about what the user is trying to do
        
    Returns:
        Conversational summary that feels like talking to a senior developer
    """
    try:
        from services import get_mistral_service
        
        # Get impact analysis
        service = ImpactService(repository_path)
        report = service.analyze_specific_files(file_paths)
        
        # Get conversational summary
        mistral = get_mistral_service()
        summary = await mistral.generate_conversational_summary(
            report.dict(),
            user_context
        )
        
        return {
            "summary": summary,
            "risk_level": report.risk_level.value,
            "risk_score": report.risk_score,
            "llm_enabled": mistral.is_available()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversational summary failed: {str(e)}"
        )


@app.post("/llm/what-if")
async def analyze_what_if_scenario(
    scenario: str = Body(...),
    repository_path: str = Body(...),
    include_code: bool = Body(False)
):
    """
    Handle complex "what if" queries with deep reasoning
    
    Args:
        scenario: The what-if question (e.g., "If I refactor the database schema...")
        repository_path: Path to the git repository
        include_code: Whether to include code content for analysis
        
    Returns:
        Detailed analysis of the scenario with predicted impacts
    """
    try:
        from services import get_mistral_service
        
        # Get repository context
        service = ImpactService(repository_path)
        
        # Build repository context
        repo_context = {
            "repository_path": repository_path,
            "critical_patterns": settings.CRITICAL_FILE_PATTERNS
        }
        
        # Get code files if requested
        code_files = None
        if include_code:
            # Get list of relevant files (simplified)
            code_files = {}
            repo_path = Path(repository_path)
            for py_file in repo_path.rglob("*.py"):
                if len(code_files) < 10:  # Limit to 10 files
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            code_files[str(py_file.relative_to(repo_path))] = f.read()
                    except:
                        pass
        
        # Get LLM analysis
        mistral = get_mistral_service()
        analysis = await mistral.analyze_what_if_scenario(
            scenario,
            repo_context,
            code_files
        )
        
        return {
            "analysis": analysis,
            "scenario": scenario,
            "llm_enabled": mistral.is_available()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"What-if analysis failed: {str(e)}"
        )


@app.post("/llm/suggest-fixes")
async def suggest_code_remediation(
    repository_path: str = Body(...),
    file_paths: List[str] = Body(...)
):
    """
    Get actionable code remediation suggestions from Mistral AI
    
    Args:
        repository_path: Path to the git repository
        file_paths: List of file paths to analyze
        
    Returns:
        Specific code changes to mitigate risks
    """
    try:
        from services import get_mistral_service
        
        # Get impact analysis
        service = ImpactService(repository_path)
        report = service.analyze_specific_files(file_paths)
        
        # Get code content
        affected_files = {}
        for file_path in file_paths[:5]:  # Limit to 5 files
            full_path = Path(repository_path) / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        affected_files[file_path] = f.read()
                except:
                    pass
        
        # Get remediation suggestions
        mistral = get_mistral_service()
        suggestions = await mistral.suggest_code_remediation(
            report.model_dump(),
            affected_files
        )
        
        return {
            "suggestions": suggestions,
            "risk_level": report.risk_level.value,
            "llm_enabled": mistral.is_available()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code remediation failed: {str(e)}"
        )


@app.post("/llm/chat")
async def chat_with_ai(
    message: str = Body(...),
    repository_path: Optional[str] = Body(None),
    conversation_history: List[dict] = Body(default_factory=list)
):
    """
    General chat interface with code context awareness
    
    Args:
        message: The user's question or request
        repository_path: Optional path to repository for context
        conversation_history: Previous messages [{"role": "user/assistant", "content": "..."}]
        
    Returns:
        AI assistant's response
    """
    try:
        from services import get_mistral_service
        
        # Build code context if repository provided
        code_context = None
        if repository_path:
            service = ImpactService(repository_path)
            code_context = {
                "repository_path": repository_path,
                "critical_patterns": settings.CRITICAL_FILE_PATTERNS
            }
        
        # Get AI response
        mistral = get_mistral_service()
        response = await mistral.chat_with_context(
            message,
            conversation_history,
            code_context
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )

# ============================================================================
# UNIFIED LLM-POWERED PRE-PUSH ANALYSIS - THE BRAIN
# ============================================================================

@app.post("/pre-push/analyze")
async def unified_pre_push_analysis(
    repository_path: str = Body(...),
    changed_files: List[str] = Body(...)
):
    """
    UNIFIED PRE-PUSH ANALYSIS - LLM as the Brain
    
    This is the main endpoint for pre-push analysis.
    ALL analysis passes through Mistral AI LLM for comprehensive insights.
    
    Returns:
    - Why this is risky (root cause)
    - What will change and where (specific lines)
    - Who should review/fix (with reasoning)
    - Predicted cascade effects
    - Actionable recommendations
    
    Args:
        repository_path: Path to the git repository
        changed_files: List of files that changed
        
    Returns:
        Comprehensive LLM-powered analysis with all details
    """
    try:
        from services.unified_llm_service import get_unified_llm_service
        
        # Get basic impact analysis first
        service = ImpactService(repository_path)
        impact_report = service.analyze_specific_files(changed_files)
        
        # Get git context
        try:
            import subprocess
            git_log = subprocess.run(
                ['git', 'log', '--oneline', '-10'],
                cwd=repository_path,
                capture_output=True,
                text=True
            ).stdout
            
            git_context = {
                "recent_commits": git_log,
                "branch": subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=repository_path,
                    capture_output=True,
                    text=True
                ).stdout.strip()
            }
        except:
            git_context = None
        
        # Pass everything through the LLM brain
        unified_llm = get_unified_llm_service()
        comprehensive_analysis = await unified_llm.comprehensive_pre_push_analysis(
            repository_path=repository_path,
            changed_files=changed_files,
            impact_data=impact_report.model_dump(),
            git_context=git_context
        )
        
        return comprehensive_analysis
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pre-push analysis failed: {str(e)}"
        )


@app.post("/pre-push/quick")
async def quick_pre_push_check(
    repository_path: str = Body(...),
    changed_files: List[str] = Body(...)
):
    """
    Quick pre-push check with LLM summary
    
    Faster version that gives a quick go/no-go decision with brief explanation
    """
    try:
        from services.unified_llm_service import get_unified_llm_service
        
        # Get basic analysis
        service = ImpactService(repository_path)
        impact_report = service.analyze_specific_files(changed_files)
        
        # Get LLM quick summary
        unified_llm = get_unified_llm_service()
        
        if not unified_llm.is_available():
            return {
                "decision": "REVIEW_NEEDED" if impact_report.risk_level.value == "HIGH" else "OK",
                "summary": f"{impact_report.risk_level.value} risk detected. Configure Mistral AI for detailed analysis.",
                "llm_enabled": False
            }
        
        # Quick LLM prompt
        from mistralai.models.chat_completion import ChatMessage
        
        prompt = f"""Quick pre-push decision for {len(changed_files)} files.
Risk: {impact_report.risk_level.value} ({impact_report.risk_score:.2f})
Files: {', '.join(changed_files[:5])}

Provide:
1. Decision: SAFE_TO_PUSH, REVIEW_NEEDED, or STOP
2. One sentence why
3. One critical action if needed

Format:
DECISION: [choice]
WHY: [one sentence]
ACTION: [one critical step or "None"]"""
        
        messages = [
            ChatMessage(role="system", content="You are a code review assistant. Be concise."),
            ChatMessage(role="user", content=prompt)
        ]
        
        response = unified_llm.client.chat(
            model=unified_llm.model,
            messages=messages,
            temperature=0.3,
            max_tokens=200
        )
        
        llm_response = response.choices[0].message.content
        
        return {
            "decision": "SAFE_TO_PUSH" if impact_report.risk_level.value == "LOW" else "REVIEW_NEEDED",
            "summary": llm_response,
            "risk_level": impact_report.risk_level.value,
            "risk_score": impact_report.risk_score,
            "llm_enabled": True
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick check failed: {str(e)}"
        )


# ============================================================================
# BOB - THE AI CODE ANALYZER (Main Pre-Commit Endpoint)
# ============================================================================

@app.post("/bob/analyze")
async def bob_analyze(
    repository_path: str = Body(..., embed=True),
    changed_files: List[str] = Body(None, embed=True)
):
    """
    Get Bob's deep reasoning analysis for uncommitted changes
    
    Args:
        repository_path: Path to the git repository
        changed_files: Optional list of files. If empty, analyzes actual uncommitted changes.
        
    Returns:
        Bob's analysis with 5 clear sections
    """
    try:
        from services.bob_analyzer import get_bob_analyzer
        
        # Initialize service
        service = ImpactService(repository_path)
        
        # If no files provided, detect actual uncommitted changes
        files_to_analyze = changed_files
        if not files_to_analyze:
            diff_stats = service.change_analyzer.get_diff_stats("main")
            files_to_analyze = [f.path for f in diff_stats]
        
        if not files_to_analyze:
            return {
                "risk_level": "LOW",
                "analysis": {
                    "impact_prediction": "No uncommitted changes detected in the repository.",
                    "breakage_simulation": "Nothing to simulate.",
                    "smart_reviewer": "No review needed.",
                    "learning_path": "Not needed.",
                    "voice_explanation": "I don't see any changes in your repository right now. You're all set!"
                }
            }
            
        # Get impact analysis
        impact_report = service.analyze_specific_files(files_to_analyze)
        
        # Get Bob's analysis
        bob = get_bob_analyzer()
        analysis = await bob.analyze_before_commit(
            repository_path=repository_path,
            changed_files=files_to_analyze,
            impact_data=impact_report.model_dump()
        )
        
        return analysis
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bob analysis failed: {str(e)}"
        )


@app.get("/git/status")
async def get_git_status(repository_path: str):
    """Get currently changed files in the repository"""
    try:
        service = ImpactService(repository_path)
        diff_stats = service.change_analyzer.get_diff_stats("main")
        return {
            "changed_files": [f.path for f in diff_stats],
            "count": len(diff_stats)
        }
    except Exception as e:
        return {"error": str(e), "changed_files": [], "count": 0}


@app.post("/voice")
async def get_voice_summary(
    repository_path: str = Body(..., embed=True),
    file_paths: List[str] = Body(..., embed=True)
):
    """
    Get voice summary of impact analysis
    
    Args:
        repository_path: Path to the git repository
        file_paths: List of file paths to analyze
        
    Returns:
        Voice summary text
    """
    try:
        # Initialize service
        service = ImpactService(repository_path)
        
        # Analyze files
        report = service.analyze_specific_files(file_paths)
        
        # Get voice summary
        voice_summary = service.voice_service.generate_voice_summary(report)
        
        return {
            "voice_summary": voice_summary,
            "risk_level": report.risk_level.value
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice summary generation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
