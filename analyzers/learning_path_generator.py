"""
Guided Learning Path Generator
Suggests files to understand before making changes
"""
import os
from typing import List, Dict, Set
from pathlib import Path
from models import LearningPathItem, DependencyInfo
from config import settings


class LearningPathGenerator:
    """Generates learning paths for understanding code changes"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the learning path generator
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path
    
    def generate_learning_path(
        self,
        changed_files: List[str],
        dependencies: List[DependencyInfo],
        critical_files: List[str]
    ) -> List[LearningPathItem]:
        """
        Generate a learning path for understanding the changes
        
        Args:
            changed_files: List of file paths being changed
            dependencies: Dependency information
            critical_files: List of critical file paths
            
        Returns:
            List of learning path items
        """
        learning_items = []
        seen_files = set()
        
        # Priority 1: Critical files being changed
        for file_path in critical_files:
            if file_path not in seen_files:
                item = self._create_learning_item(
                    file_path,
                    "Critical system component - understand thoroughly",
                    "high"
                )
                learning_items.append(item)
                seen_files.add(file_path)
        
        # Priority 2: Core dependencies
        for dep in dependencies:
            # Add files this change depends on
            for dep_file in dep.depends_on[:3]:  # Top 3 dependencies
                if dep_file not in seen_files and self._is_local_file(dep_file):
                    item = self._create_learning_item(
                        dep_file,
                        f"Core dependency of {Path(dep.file).name}",
                        "high"
                    )
                    learning_items.append(item)
                    seen_files.add(dep_file)
        
        # Priority 3: Files that depend on changes
        for dep in dependencies:
            for dependent in dep.depended_by[:2]:  # Top 2 dependents
                if dependent not in seen_files:
                    item = self._create_learning_item(
                        dependent,
                        f"Will be affected by changes to {Path(dep.file).name}",
                        "medium"
                    )
                    learning_items.append(item)
                    seen_files.add(dependent)
        
        # Priority 4: Related files in same directory
        for file_path in changed_files:
            related = self._find_related_files(file_path)
            for related_file in related[:2]:  # Top 2 related
                if related_file not in seen_files:
                    item = self._create_learning_item(
                        related_file,
                        f"Related to {Path(file_path).name} in same module",
                        "medium"
                    )
                    learning_items.append(item)
                    seen_files.add(related_file)
        
        # Priority 5: Configuration files
        config_files = self._find_config_files(changed_files)
        for config_file in config_files:
            if config_file not in seen_files:
                item = self._create_learning_item(
                    config_file,
                    "Configuration that may affect this change",
                    "low"
                )
                learning_items.append(item)
                seen_files.add(config_file)
        
        # Limit to max items
        return learning_items[:settings.MAX_LEARNING_PATH_FILES]
    
    def _create_learning_item(
        self,
        file_path: str,
        reason: str,
        importance: str
    ) -> LearningPathItem:
        """
        Create a learning path item
        
        Args:
            file_path: Path to the file
            reason: Reason for including this file
            importance: Importance level (high, medium, low)
            
        Returns:
            Learning path item
        """
        lines_of_code = self._count_lines(file_path)
        
        return LearningPathItem(
            file=file_path,
            reason=reason,
            importance=importance,
            lines_of_code=lines_of_code
        )
    
    def _is_local_file(self, file_path: str) -> bool:
        """
        Check if a file path refers to a local project file
        
        Args:
            file_path: File path to check
            
        Returns:
            True if local file, False otherwise
        """
        # Filter out external packages and standard library
        if any(pattern in file_path for pattern in [
            'node_modules', 'site-packages', 'dist-packages',
            'venv', '.venv', 'env'
        ]):
            return False
        
        # Check if file exists in repo
        full_path = os.path.join(self.repo_path, file_path)
        return os.path.exists(full_path)
    
    def _find_related_files(self, file_path: str) -> List[str]:
        """
        Find files related to the given file (same directory, similar names)
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of related file paths
        """
        related = []
        
        try:
            directory = os.path.dirname(file_path)
            filename = Path(file_path).stem
            
            dir_path = os.path.join(self.repo_path, directory)
            if not os.path.exists(dir_path):
                return []
            
            for file in os.listdir(dir_path):
                if file.startswith('.'):
                    continue
                
                file_stem = Path(file).stem
                rel_path = os.path.join(directory, file)
                
                # Skip the original file
                if rel_path == file_path:
                    continue
                
                # Include files with similar names
                if filename.lower() in file_stem.lower() or \
                   file_stem.lower() in filename.lower():
                    related.append(rel_path)
                
                # Include test files
                if 'test' in file.lower() and filename.lower() in file.lower():
                    related.append(rel_path)
        
        except Exception:
            pass
        
        return related[:5]
    
    def _find_config_files(self, changed_files: List[str]) -> List[str]:
        """
        Find relevant configuration files
        
        Args:
            changed_files: List of changed file paths
            
        Returns:
            List of configuration file paths
        """
        config_files = []
        
        # Common config file patterns
        config_patterns = [
            'config.py', 'settings.py', 'config.js', 'config.ts',
            '.env', '.env.example', 'package.json', 'requirements.txt',
            'tsconfig.json', 'webpack.config.js', 'babel.config.js'
        ]
        
        # Get directories of changed files
        directories = set()
        for file_path in changed_files:
            directories.add(os.path.dirname(file_path))
        
        # Search for config files in relevant directories
        for directory in directories:
            dir_path = os.path.join(self.repo_path, directory)
            
            if not os.path.exists(dir_path):
                continue
            
            try:
                for file in os.listdir(dir_path):
                    if any(pattern in file.lower() for pattern in config_patterns):
                        config_files.append(os.path.join(directory, file))
            except Exception:
                continue
        
        # Also check root directory
        try:
            for file in os.listdir(self.repo_path):
                if any(pattern in file.lower() for pattern in config_patterns):
                    config_files.append(file)
        except Exception:
            pass
        
        return list(set(config_files))[:3]  # Return up to 3 config files
    
    def _count_lines(self, file_path: str) -> int:
        """
        Count lines of code in a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of lines
        """
        try:
            full_path = os.path.join(self.repo_path, file_path)
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len(f.readlines())
        except Exception:
            return 0

# Made with Bob
