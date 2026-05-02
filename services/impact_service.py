"""
Impact Service
Main orchestrator for impact analysis
"""
from typing import List, Optional
from models import (
    ChangeInput, ImpactReport, FileChange, RiskLevel,
    DependencyInfo, Warning
)
from analyzers import (
    ChangeAnalyzer, RiskScorer, HistoryAnalyzer,
    ReviewerSuggester, LearningPathGenerator
)
from services.voice_service import VoiceService
from config import settings


class ImpactService:
    """Main service for analyzing code change impact"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the impact service
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path
        
        # Initialize analyzers
        self.change_analyzer = ChangeAnalyzer(repo_path)
        self.risk_scorer = RiskScorer()
        self.history_analyzer = HistoryAnalyzer(repo_path)
        self.reviewer_suggester = ReviewerSuggester(repo_path)
        self.learning_path_generator = LearningPathGenerator(repo_path)
        self.voice_service = VoiceService()
    
    def analyze_impact(self, change_input: ChangeInput) -> ImpactReport:
        """
        Perform complete impact analysis
        
        Args:
            change_input: Input containing change information
            
        Returns:
            Complete impact report
        """
        # Get changed files
        changed_files = change_input.changed_files
        if not changed_files:
            # Try to get from git diff
            changed_files = self.change_analyzer.get_diff_stats(change_input.branch)
        
        if not changed_files:
            # Return empty report if no changes
            return self._create_empty_report()
        
        # Step 1: Analyze changes
        change_analysis = self.change_analyzer.analyze_changes(changed_files)
        
        # Step 2: Analyze history
        file_paths = [f.path for f in changed_files]
        historical_data = self.history_analyzer.analyze_history(file_paths)
        
        # Step 3: Calculate risk score
        risk_score, risk_level, risk_warnings = self.risk_scorer.calculate_risk_score(
            changed_files=changed_files,
            critical_files=change_analysis['critical_files'],
            dependencies=change_analysis['dependencies'],
            historical_data=historical_data
        )
        
        # Step 4: Suggest reviewers
        suggested_reviewers = self.reviewer_suggester.suggest_reviewers(file_paths)
        
        # Step 5: Generate learning path
        learning_path = self.learning_path_generator.generate_learning_path(
            changed_files=file_paths,
            dependencies=change_analysis['dependencies'],
            critical_files=change_analysis['critical_files']
        )
        
        # Combine all warnings
        all_warnings = risk_warnings + historical_data.get('warnings', [])
        
        # Create impact report
        report = ImpactReport(
            risk_level=risk_level,
            risk_score=risk_score,
            affected_areas=change_analysis['affected_areas'],
            critical_files=change_analysis['critical_files'],
            dependencies=change_analysis['dependencies'],
            warnings=all_warnings,
            suggested_reviewers=suggested_reviewers,
            learning_path=learning_path,
            metadata={
                'total_changes': change_analysis['total_changes'],
                'files_count': change_analysis['files_count'],
                'hot_zones': [hz.dict() for hz in historical_data.get('hot_zones', [])],
                'patterns': [p.dict() for p in historical_data.get('patterns', [])]
            }
        )
        
        # Generate voice summary if enabled
        if settings.VOICE_ENABLED:
            report.voice_summary = self.voice_service.generate_voice_summary(report)
        
        return report
    
    def _create_empty_report(self) -> ImpactReport:
        """
        Create an empty impact report
        
        Returns:
            Empty impact report
        """
        return ImpactReport(
            risk_level=RiskLevel.LOW,
            risk_score=0.0,
            affected_areas=[],
            critical_files=[],
            dependencies=[],
            warnings=[],
            suggested_reviewers=[],
            learning_path=[],
            metadata={'message': 'No changes detected'}
        )
    
    def analyze_specific_files(self, file_paths: List[str]) -> ImpactReport:
        """
        Analyze impact of specific files
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            Impact report
        """
        # Convert file paths to FileChange objects
        changed_files = [
            FileChange(path=path, additions=0, deletions=0)
            for path in file_paths
        ]
        
        change_input = ChangeInput(
            repository_path=self.repo_path,
            changed_files=changed_files
        )
        
        return self.analyze_impact(change_input)
    
    def get_quick_summary(self, report: ImpactReport) -> str:
        """
        Get a quick text summary of the report
        
        Args:
            report: Impact report
            
        Returns:
            Summary text
        """
        lines = [
            f"Risk Level: {report.risk_level.value}",
            f"Risk Score: {report.risk_score:.2f}",
            f"Affected Areas: {', '.join(report.affected_areas) if report.affected_areas else 'None'}",
            f"Critical Files: {len(report.critical_files)}",
            f"Warnings: {len(report.warnings)}",
            f"Suggested Reviewers: {', '.join([r.name for r in report.suggested_reviewers[:3]])}",
        ]
        
        return "\n".join(lines)

# Made with Bob
