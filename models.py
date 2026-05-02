"""
Data models for ImpactGuard
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FileChange(BaseModel):
    """Represents a file change"""
    path: str
    additions: int = 0
    deletions: int = 0
    is_new: bool = False
    is_deleted: bool = False


class ChangeInput(BaseModel):
    """Input for change analysis"""
    repository_path: str = Field(..., description="Path to the git repository")
    changed_files: Optional[List[FileChange]] = None
    diff_content: Optional[str] = None
    branch: str = "main"


class DependencyInfo(BaseModel):
    """Information about file dependencies"""
    file: str
    depends_on: List[str] = []
    depended_by: List[str] = []
    depth: int = 0


class Warning(BaseModel):
    """Warning message with context"""
    message: str
    severity: str = "medium"
    related_commit: Optional[str] = None
    related_files: List[str] = []


class ReviewerSuggestion(BaseModel):
    """Suggested reviewer with confidence score"""
    name: str
    email: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    commits_count: int = 0
    last_commit_date: Optional[str] = None
    expertise_areas: List[str] = []


class LearningPathItem(BaseModel):
    """Item in the learning path"""
    file: str
    reason: str
    importance: str = "medium"
    lines_of_code: Optional[int] = None


class ImpactReport(BaseModel):
    """Complete impact analysis report"""
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=1.0)
    affected_areas: List[str] = []
    critical_files: List[str] = []
    dependencies: List[DependencyInfo] = []
    warnings: List[Warning] = []
    suggested_reviewers: List[ReviewerSuggestion] = []
    learning_path: List[LearningPathItem] = []
    metadata: Dict[str, Any] = {}
    voice_summary: Optional[str] = None


class HistoricalPattern(BaseModel):
    """Historical pattern detected in repository"""
    pattern_type: str
    description: str
    affected_files: List[str]
    frequency: int
    last_occurrence: Optional[str] = None


class HotZone(BaseModel):
    """High-change area in the codebase"""
    file: str
    change_count: int
    bug_count: int
    last_modified: str
    contributors: List[str]

# Made with Bob
