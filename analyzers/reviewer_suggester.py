"""
Smart Reviewer Suggestion
Identifies and recommends code reviewers based on git history
"""
from typing import List, Dict
from collections import defaultdict
from datetime import datetime
import git
from models import ReviewerSuggestion
from config import settings


class ReviewerSuggester:
    """Suggests code reviewers based on expertise and contribution history"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the reviewer suggester
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = None
    
    def suggest_reviewers(self, changed_files: List[str]) -> List[ReviewerSuggestion]:
        """
        Suggest reviewers for changed files
        
        Args:
            changed_files: List of file paths
            
        Returns:
            List of reviewer suggestions with confidence scores
        """
        if not self.repo:
            return []
        
        # Collect contributor data for each file
        file_experts = {}
        for file_path in changed_files:
            experts = self._get_file_contributors(file_path)
            file_experts[file_path] = experts
        
        # Aggregate and score reviewers
        reviewer_scores = self._calculate_reviewer_scores(file_experts, changed_files)
        
        # Convert to ReviewerSuggestion objects
        suggestions = []
        for reviewer_data in reviewer_scores:
            suggestion = ReviewerSuggestion(
                name=reviewer_data['name'],
                email=reviewer_data.get('email'),
                confidence=reviewer_data['confidence'],
                commits_count=reviewer_data['commits'],
                last_commit_date=reviewer_data.get('last_commit'),
                expertise_areas=reviewer_data.get('expertise_areas', [])
            )
            suggestions.append(suggestion)
        
        # Filter by minimum confidence and limit results
        filtered = [
            s for s in suggestions 
            if s.confidence >= settings.MIN_REVIEWER_CONFIDENCE
        ]
        
        return sorted(filtered, key=lambda x: x.confidence, reverse=True)[:settings.MAX_SUGGESTED_REVIEWERS]
    
    def _get_file_contributors(self, file_path: str, max_commits: int = 50) -> List[Dict]:
        """
        Get contributors for a specific file
        
        Args:
            file_path: Path to the file
            max_commits: Maximum number of commits to analyze
            
        Returns:
            List of contributor information
        """
        contributors = []
        
        try:
            commits = list(self.repo.iter_commits(paths=file_path, max_count=max_commits))
            
            # Aggregate contributor data
            author_data = defaultdict(lambda: {
                'commits': 0,
                'last_commit': None,
                'email': None
            })
            
            for commit in commits:
                author = commit.author.name
                author_data[author]['commits'] += 1
                author_data[author]['email'] = commit.author.email
                
                if not author_data[author]['last_commit']:
                    author_data[author]['last_commit'] = commit.committed_datetime.isoformat()
            
            # Convert to list
            for author, data in author_data.items():
                contributors.append({
                    'name': author,
                    'email': data['email'],
                    'commits': data['commits'],
                    'last_commit': data['last_commit']
                })
        
        except Exception:
            pass
        
        return contributors
    
    def _calculate_reviewer_scores(
        self,
        file_experts: Dict[str, List[Dict]],
        changed_files: List[str]
    ) -> List[Dict]:
        """
        Calculate confidence scores for potential reviewers
        
        Args:
            file_experts: Dictionary mapping files to their contributors
            changed_files: List of changed file paths
            
        Returns:
            List of reviewer data with confidence scores
        """
        # Aggregate all reviewers
        reviewer_data = defaultdict(lambda: {
            'commits': 0,
            'files_touched': set(),
            'last_commit': None,
            'email': None
        })
        
        for file_path, experts in file_experts.items():
            for expert in experts:
                name = expert['name']
                reviewer_data[name]['commits'] += expert['commits']
                reviewer_data[name]['files_touched'].add(file_path)
                reviewer_data[name]['email'] = expert.get('email')
                
                # Track most recent commit
                if expert.get('last_commit'):
                    if not reviewer_data[name]['last_commit'] or \
                       expert['last_commit'] > reviewer_data[name]['last_commit']:
                        reviewer_data[name]['last_commit'] = expert['last_commit']
        
        # Calculate confidence scores
        reviewers = []
        total_files = len(changed_files)
        
        for name, data in reviewer_data.items():
            # Factors for confidence score:
            # 1. Coverage: How many of the changed files they've worked on
            coverage = len(data['files_touched']) / total_files
            
            # 2. Expertise: Number of commits (normalized)
            expertise = min(1.0, data['commits'] / 20)  # Normalize to 20 commits
            
            # 3. Recency: How recent their last commit was
            recency = self._calculate_recency_score(data['last_commit'])
            
            # Weighted confidence score
            confidence = (
                coverage * 0.4 +
                expertise * 0.35 +
                recency * 0.25
            )
            
            # Identify expertise areas
            expertise_areas = self._identify_expertise_areas(data['files_touched'])
            
            reviewers.append({
                'name': name,
                'email': data['email'],
                'confidence': round(confidence, 2),
                'commits': data['commits'],
                'last_commit': data['last_commit'],
                'expertise_areas': expertise_areas
            })
        
        return reviewers
    
    def _calculate_recency_score(self, last_commit_date: str) -> float:
        """
        Calculate recency score based on last commit date
        
        Args:
            last_commit_date: ISO format date string
            
        Returns:
            Score between 0 and 1
        """
        if not last_commit_date:
            return 0.0
        
        try:
            last_commit = datetime.fromisoformat(last_commit_date.replace('Z', '+00:00'))
            days_ago = (datetime.now(last_commit.tzinfo) - last_commit).days
            
            # Score decreases with time
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 30:
                return 0.8
            elif days_ago <= 90:
                return 0.6
            elif days_ago <= 180:
                return 0.4
            else:
                return 0.2
        
        except Exception:
            return 0.5
    
    def _identify_expertise_areas(self, files: set) -> List[str]:
        """
        Identify expertise areas based on files worked on
        
        Args:
            files: Set of file paths
            
        Returns:
            List of expertise area names
        """
        areas = set()
        
        for file_path in files:
            path_lower = file_path.lower()
            
            # Identify areas based on file patterns
            if any(pattern in path_lower for pattern in ['auth', 'login', 'user']):
                areas.add('authentication')
            if any(pattern in path_lower for pattern in ['payment', 'billing']):
                areas.add('payments')
            if any(pattern in path_lower for pattern in ['api', 'endpoint', 'route']):
                areas.add('api')
            if any(pattern in path_lower for pattern in ['database', 'db', 'model']):
                areas.add('database')
            if any(pattern in path_lower for pattern in ['frontend', 'ui', 'component']):
                areas.add('frontend')
            if any(pattern in path_lower for pattern in ['backend', 'server', 'service']):
                areas.add('backend')
            if any(pattern in path_lower for pattern in ['test', 'spec']):
                areas.add('testing')
        
        return sorted(list(areas))

# Made with Bob
