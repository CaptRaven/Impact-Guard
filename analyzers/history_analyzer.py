"""
Historical Insight Extraction
Analyzes git history to detect patterns and provide insights
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import git
from models import HotZone, HistoricalPattern, Warning
from config import settings


class HistoryAnalyzer:
    """Analyzes repository history for patterns and insights"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the history analyzer
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = None
    
    def analyze_history(self, changed_files: List[str]) -> Dict:
        """
        Analyze historical data for changed files
        
        Args:
            changed_files: List of file paths
            
        Returns:
            Dictionary with historical insights
        """
        if not self.repo:
            return {
                'hot_zones': [],
                'bug_prone_files': [],
                'patterns': [],
                'warnings': []
            }
        
        hot_zones = self._identify_hot_zones(changed_files)
        bug_prone = self._identify_bug_prone_files(changed_files)
        patterns = self._detect_patterns(changed_files)
        warnings = self._generate_historical_warnings(changed_files, hot_zones, bug_prone)
        
        return {
            'hot_zones': hot_zones,
            'bug_prone_files': bug_prone,
            'patterns': patterns,
            'warnings': warnings
        }
    
    def _identify_hot_zones(self, changed_files: List[str]) -> List[HotZone]:
        """
        Identify high-change areas (hot zones)
        
        Args:
            changed_files: List of file paths
            
        Returns:
            List of hot zones
        """
        hot_zones = []
        cutoff_date = datetime.now() - timedelta(days=settings.HISTORY_LOOKBACK_DAYS)
        
        for file_path in changed_files:
            try:
                # Get commits for this file
                commits = list(self.repo.iter_commits(
                    paths=file_path,
                    since=cutoff_date.isoformat()
                ))
                
                if len(commits) >= settings.MIN_COMMITS_FOR_HOTZONE:
                    # Count bug-related commits
                    bug_count = sum(
                        1 for c in commits
                        if any(keyword in c.message.lower() 
                               for keyword in ['fix', 'bug', 'issue', 'error'])
                    )
                    
                    # Get unique contributors
                    contributors = list(set(c.author.name for c in commits))
                    
                    hot_zone = HotZone(
                        file=file_path,
                        change_count=len(commits),
                        bug_count=bug_count,
                        last_modified=commits[0].committed_datetime.isoformat(),
                        contributors=contributors[:5]  # Top 5 contributors
                    )
                    hot_zones.append(hot_zone)
            
            except Exception:
                continue
        
        # Sort by change count
        hot_zones.sort(key=lambda x: x.change_count, reverse=True)
        return hot_zones[:5]  # Return top 5 hot zones
    
    def _identify_bug_prone_files(self, changed_files: List[str]) -> List[str]:
        """
        Identify files with history of bugs
        
        Args:
            changed_files: List of file paths
            
        Returns:
            List of bug-prone file paths
        """
        bug_prone = []
        cutoff_date = datetime.now() - timedelta(days=settings.HISTORY_LOOKBACK_DAYS)
        
        for file_path in changed_files:
            try:
                commits = list(self.repo.iter_commits(
                    paths=file_path,
                    since=cutoff_date.isoformat()
                ))
                
                # Count bug-fix commits
                bug_fixes = sum(
                    1 for c in commits
                    if any(keyword in c.message.lower() 
                           for keyword in ['fix', 'bug', 'hotfix', 'patch'])
                )
                
                # If more than 30% of commits are bug fixes, mark as bug-prone
                if commits and (bug_fixes / len(commits)) > 0.3:
                    bug_prone.append(file_path)
            
            except Exception:
                continue
        
        return bug_prone
    
    def _detect_patterns(self, changed_files: List[str]) -> List[HistoricalPattern]:
        """
        Detect patterns in commit history
        
        Args:
            changed_files: List of file paths
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Pattern 1: Frequently changed together
        co_change_pattern = self._detect_co_change_pattern(changed_files)
        if co_change_pattern:
            patterns.append(co_change_pattern)
        
        # Pattern 2: Recent regression pattern
        regression_pattern = self._detect_regression_pattern(changed_files)
        if regression_pattern:
            patterns.append(regression_pattern)
        
        return patterns
    
    def _detect_co_change_pattern(self, changed_files: List[str]) -> Optional[HistoricalPattern]:
        """
        Detect files that are frequently changed together
        
        Args:
            changed_files: List of file paths
            
        Returns:
            Pattern if detected, None otherwise
        """
        if not self.repo or len(changed_files) < 2:
            return None
        
        try:
            # Get recent commits
            cutoff_date = datetime.now() - timedelta(days=90)
            commits = list(self.repo.iter_commits(
                since=cutoff_date.isoformat(),
                max_count=100
            ))
            
            # Track file co-occurrences
            co_changes = defaultdict(int)
            
            for commit in commits:
                commit_files = [item.a_path for item in commit.diff(commit.parents[0])] if commit.parents else []
                
                # Check if any of our changed files appear together
                for i, file1 in enumerate(changed_files):
                    if file1 in commit_files:
                        for file2 in changed_files[i+1:]:
                            if file2 in commit_files:
                                key = tuple(sorted([file1, file2]))
                                co_changes[key] += 1
            
            # Find most frequent co-change
            if co_changes:
                most_frequent = max(co_changes.items(), key=lambda x: x[1])
                if most_frequent[1] >= 3:  # At least 3 co-changes
                    return HistoricalPattern(
                        pattern_type="co_change",
                        description=f"Files frequently changed together ({most_frequent[1]} times)",
                        affected_files=list(most_frequent[0]),
                        frequency=most_frequent[1]
                    )
        
        except Exception:
            pass
        
        return None
    
    def _detect_regression_pattern(self, changed_files: List[str]) -> Optional[HistoricalPattern]:
        """
        Detect recent regression patterns
        
        Args:
            changed_files: List of file paths
            
        Returns:
            Pattern if detected, None otherwise
        """
        if not self.repo:
            return None
        
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for file_path in changed_files:
                commits = list(self.repo.iter_commits(
                    paths=file_path,
                    since=cutoff_date.isoformat(),
                    max_count=10
                ))
                
                # Look for revert or fix commits
                for commit in commits:
                    if any(keyword in commit.message.lower() 
                           for keyword in ['revert', 'rollback', 'fix regression']):
                        return HistoricalPattern(
                            pattern_type="regression",
                            description="Recent regression detected in this area",
                            affected_files=[file_path],
                            frequency=1,
                            last_occurrence=commit.committed_datetime.isoformat()
                        )
        
        except Exception:
            pass
        
        return None
    
    def _generate_historical_warnings(
        self,
        changed_files: List[str],
        hot_zones: List[HotZone],
        bug_prone: List[str]
    ) -> List[Warning]:
        """
        Generate warnings based on historical data
        
        Args:
            changed_files: List of file paths
            hot_zones: List of hot zones
            bug_prone: List of bug-prone files
            
        Returns:
            List of warnings
        """
        warnings = []
        
        # Warnings for hot zones
        for hot_zone in hot_zones:
            if hot_zone.file in changed_files:
                warnings.append(Warning(
                    message=f"High-change area: {hot_zone.change_count} commits in last {settings.HISTORY_LOOKBACK_DAYS} days",
                    severity="medium",
                    related_files=[hot_zone.file]
                ))
        
        # Warnings for bug-prone files
        for file_path in bug_prone:
            if file_path in changed_files:
                warnings.append(Warning(
                    message=f"File has history of bugs - extra caution recommended",
                    severity="high",
                    related_files=[file_path]
                ))
        
        return warnings
    
    def get_file_experts(self, file_path: str, limit: int = 5) -> List[Dict]:
        """
        Get experts (frequent contributors) for a file
        
        Args:
            file_path: Path to the file
            limit: Maximum number of experts to return
            
        Returns:
            List of expert information
        """
        if not self.repo:
            return []
        
        try:
            commits = list(self.repo.iter_commits(paths=file_path, max_count=50))
            
            # Count contributions by author
            author_counts = defaultdict(int)
            author_dates = {}
            
            for commit in commits:
                author = commit.author.name
                author_counts[author] += 1
                if author not in author_dates:
                    author_dates[author] = commit.committed_datetime
            
            # Sort by contribution count
            experts = [
                {
                    'name': author,
                    'commits': count,
                    'last_commit': author_dates[author].isoformat()
                }
                for author, count in sorted(
                    author_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ]
            
            return experts[:limit]
        
        except Exception:
            return []

# Made with Bob
