"""
Risk Scoring Engine
Assigns risk scores to code changes based on multiple factors
"""
from typing import List, Dict
from models import FileChange, DependencyInfo, RiskLevel, Warning
from config import settings


class RiskScorer:
    """Calculates risk scores for code changes"""
    
    def __init__(self):
        """Initialize the risk scorer"""
        self.weights = {
            'critical_files': 0.35,
            'dependency_impact': 0.25,
            'change_magnitude': 0.20,
            'historical_issues': 0.20
        }
    
    def calculate_risk_score(
        self,
        changed_files: List[FileChange],
        critical_files: List[str],
        dependencies: List[DependencyInfo],
        historical_data: Dict = None
    ) -> tuple[float, RiskLevel, List[Warning]]:
        """
        Calculate overall risk score
        
        Args:
            changed_files: List of changed files
            critical_files: List of critical file paths
            dependencies: Dependency information
            historical_data: Historical analysis data
            
        Returns:
            Tuple of (risk_score, risk_level, warnings)
        """
        warnings = []
        
        # Calculate individual risk factors
        critical_score = self._score_critical_files(changed_files, critical_files)
        dependency_score = self._score_dependencies(dependencies)
        magnitude_score = self._score_change_magnitude(changed_files)
        historical_score = self._score_historical_issues(historical_data or {})
        
        # Calculate weighted total
        total_score = (
            critical_score * self.weights['critical_files'] +
            dependency_score * self.weights['dependency_impact'] +
            magnitude_score * self.weights['change_magnitude'] +
            historical_score * self.weights['historical_issues']
        )
        
        # Generate warnings
        if critical_score > 0.7:
            warnings.append(Warning(
                message=f"Changes affect {len(critical_files)} critical file(s)",
                severity="high",
                related_files=critical_files
            ))
        
        if dependency_score > 0.7:
            total_deps = sum(len(d.depended_by) for d in dependencies)
            warnings.append(Warning(
                message=f"High dependency impact across {total_deps} dependent modules",
                severity="high"
            ))
        
        if magnitude_score > 0.8:
            total_changes = sum(f.additions + f.deletions for f in changed_files)
            warnings.append(Warning(
                message=f"Large change magnitude: {total_changes} lines modified",
                severity="medium"
            ))
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score)
        
        return total_score, risk_level, warnings
    
    def _score_critical_files(
        self,
        changed_files: List[FileChange],
        critical_files: List[str]
    ) -> float:
        """
        Score based on critical files affected
        
        Args:
            changed_files: List of changed files
            critical_files: List of critical file paths
            
        Returns:
            Score between 0 and 1
        """
        if not changed_files:
            return 0.0
        
        critical_count = len(critical_files)
        total_count = len(changed_files)
        
        # Base score on ratio of critical files
        ratio = critical_count / total_count
        
        # Apply non-linear scaling
        if critical_count == 0:
            return 0.0
        elif critical_count == 1:
            return 0.5
        elif critical_count == 2:
            return 0.7
        else:
            return min(0.9, 0.7 + (critical_count - 2) * 0.1)
    
    def _score_dependencies(self, dependencies: List[DependencyInfo]) -> float:
        """
        Score based on dependency impact
        
        Args:
            dependencies: List of dependency information
            
        Returns:
            Score between 0 and 1
        """
        if not dependencies:
            return 0.0
        
        # Count total dependents
        total_dependents = sum(len(d.depended_by) for d in dependencies)
        
        # Count files with high dependency depth
        high_depth_count = sum(1 for d in dependencies if d.depth > 5)
        
        # Calculate score
        dependent_score = min(1.0, total_dependents / 10)  # Normalize to 10 dependents
        depth_score = min(1.0, high_depth_count / 3)  # Normalize to 3 high-depth files
        
        return (dependent_score * 0.7 + depth_score * 0.3)
    
    def _score_change_magnitude(self, changed_files: List[FileChange]) -> float:
        """
        Score based on the magnitude of changes
        
        Args:
            changed_files: List of changed files
            
        Returns:
            Score between 0 and 1
        """
        if not changed_files:
            return 0.0
        
        total_changes = sum(f.additions + f.deletions for f in changed_files)
        file_count = len(changed_files)
        
        # Score based on total lines changed
        lines_score = min(1.0, total_changes / 500)  # Normalize to 500 lines
        
        # Score based on number of files
        files_score = min(1.0, file_count / 10)  # Normalize to 10 files
        
        # New or deleted files increase risk
        structural_changes = sum(1 for f in changed_files if f.is_new or f.is_deleted)
        structural_score = min(1.0, structural_changes / 3)  # Normalize to 3 files
        
        return (lines_score * 0.4 + files_score * 0.3 + structural_score * 0.3)
    
    def _score_historical_issues(self, historical_data: Dict) -> float:
        """
        Score based on historical issues
        
        Args:
            historical_data: Historical analysis data
            
        Returns:
            Score between 0 and 1
        """
        if not historical_data:
            return 0.0
        
        hot_zones = historical_data.get('hot_zones', [])
        bug_prone_files = historical_data.get('bug_prone_files', [])
        
        # Score based on hot zones
        hot_zone_score = min(1.0, len(hot_zones) / 3)
        
        # Score based on bug-prone files
        bug_score = min(1.0, len(bug_prone_files) / 3)
        
        return (hot_zone_score * 0.5 + bug_score * 0.5)
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """
        Determine risk level from score
        
        Args:
            score: Risk score between 0 and 1
            
        Returns:
            Risk level enum
        """
        if score < settings.RISK_LOW_THRESHOLD:
            return RiskLevel.LOW
        elif score < settings.RISK_MEDIUM_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    def get_risk_explanation(self, risk_level: RiskLevel, score: float) -> str:
        """
        Get human-readable explanation of risk level
        
        Args:
            risk_level: Risk level
            score: Risk score
            
        Returns:
            Explanation string
        """
        from config import RISK_LEVELS
        
        base_explanation = RISK_LEVELS.get(risk_level.value, "Unknown risk level")
        return f"{base_explanation} (Score: {score:.2f})"

# Made with Bob
