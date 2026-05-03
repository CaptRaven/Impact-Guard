"""
Change Impact Analyzer
Analyzes code changes and identifies affected modules and dependencies
"""
import os
import re
from typing import List, Dict, Set, Tuple
from pathlib import Path
import git
from models import FileChange, DependencyInfo


class ChangeAnalyzer:
    """Analyzes code changes and their impact"""
    
    def __init__(self, repo_path: str):
        """
        Initialize the analyzer
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = None
    
    def analyze_changes(self, changed_files: List[FileChange]) -> Dict:
        """
        Analyze the impact of changed files
        
        Args:
            changed_files: List of changed files
            
        Returns:
            Dictionary with analysis results
        """
        affected_areas = self._identify_affected_areas(changed_files)
        dependencies = self._analyze_dependencies(changed_files)
        critical_files = self._identify_critical_files(changed_files)
        
        return {
            "affected_areas": affected_areas,
            "dependencies": dependencies,
            "critical_files": critical_files,
            "total_changes": sum(f.additions + f.deletions for f in changed_files),
            "files_count": len(changed_files)
        }
    
    def _identify_affected_areas(self, changed_files: List[FileChange]) -> List[str]:
        """
        Identify affected areas/modules based on file paths
        
        Args:
            changed_files: List of changed files
            
        Returns:
            List of affected area names
        """
        areas = set()
        
        for file_change in changed_files:
            path_parts = Path(file_change.path).parts
            
            # Extract module/area from path
            if len(path_parts) > 1:
                # Use first directory as area
                areas.add(path_parts[0])
            
            # Check for specific patterns in filename
            filename = Path(file_change.path).name.lower()
            
            if any(pattern in filename for pattern in ['auth', 'login', 'user']):
                areas.add('authentication')
            if any(pattern in filename for pattern in ['payment', 'billing', 'transaction']):
                areas.add('payment_service')
            if any(pattern in filename for pattern in ['api', 'endpoint', 'route']):
                areas.add('api')
            if any(pattern in filename for pattern in ['database', 'db', 'model']):
                areas.add('database')
            if any(pattern in filename for pattern in ['test', 'spec']):
                areas.add('testing')
            if any(pattern in filename for pattern in ['config', 'setting']):
                areas.add('configuration')
        
        return sorted(list(areas))
    
    def _analyze_dependencies(self, changed_files: List[FileChange]) -> List[DependencyInfo]:
        """
        Analyze dependencies for changed files
        
        Args:
            changed_files: List of changed files
            
        Returns:
            List of dependency information
        """
        dependencies = []
        
        for file_change in changed_files:
            file_path = os.path.join(self.repo_path, file_change.path)
            
            if not os.path.exists(file_path) or file_change.is_deleted:
                continue
            
            depends_on = self._extract_imports(file_path)
            depended_by = self._find_dependents(file_change.path)
            
            dep_info = DependencyInfo(
                file=file_change.path,
                depends_on=depends_on,
                depended_by=depended_by,
                depth=len(depends_on)
            )
            dependencies.append(dep_info)
        
        return dependencies
    
    def _extract_imports(self, file_path: str) -> List[str]:
        """
        Extract import statements from a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of imported modules/files
        """
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Python imports
            python_imports = re.findall(r'(?:from|import)\s+([a-zA-Z0-9_.]+)', content)
            imports.extend(python_imports)
            
            # JavaScript/TypeScript imports
            js_imports = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
            imports.extend(js_imports)
            
            # Require statements
            require_imports = re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', content)
            imports.extend(require_imports)
            
        except Exception:
            pass
        
        # Filter out standard library and external packages
        filtered_imports = [
            imp for imp in imports 
            if not imp.startswith('.') and '/' not in imp and '\\' not in imp
        ]
        
        return list(set(filtered_imports))[:10]  # Limit to 10 most relevant
    
    def _find_dependents(self, file_path: str) -> List[str]:
        """
        Find files that depend on the given file
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of dependent files
        """
        dependents = []
        file_name = Path(file_path).stem
        
        # Search for files that import this file
        for root, _, files in os.walk(self.repo_path):
            # Skip hidden directories and common ignore patterns
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                continue
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.repo_path)
                    
                    if rel_path == file_path:
                        continue
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if file_name in content:
                                dependents.append(rel_path)
                    except Exception:
                        continue
        
        return dependents[:10]  # Limit to 10 most relevant
    
    def _identify_critical_files(self, changed_files: List[FileChange]) -> List[str]:
        """
        Identify critical files from the changed files
        
        Args:
            changed_files: List of changed files
            
        Returns:
            List of critical file paths
        """
        from config import settings
        
        critical = []
        
        for file_change in changed_files:
            path_lower = file_change.path.lower()
            
            # Check against critical patterns
            for pattern in settings.CRITICAL_FILE_PATTERNS:
                if pattern in path_lower:
                    critical.append(file_change.path)
                    break
        
        return critical
    
    def get_diff_stats(self, branch: str = "main") -> List[FileChange]:
        """
        Get diff statistics for uncommitted changes (staged, unstaged, and untracked)
        
        Args:
            branch: Branch to compare against
            
        Returns:
            List of file changes
        """
        if not self.repo:
            return []
        
        changes_dict = {}
        
        try:
            # 1. Get unstaged changes
            diff_index = self.repo.index.diff(None)
            for diff_item in diff_index:
                path = diff_item.a_path or diff_item.b_path
                changes_dict[path] = FileChange(
                    path=path,
                    additions=0,
                    deletions=0,
                    is_new=diff_item.new_file,
                    is_deleted=diff_item.deleted_file
                )
            
            # 2. Get staged changes
            try:
                diff_staged = self.repo.index.diff('HEAD')
                for diff_item in diff_staged:
                    path = diff_item.a_path or diff_item.b_path
                    if path not in changes_dict:
                        changes_dict[path] = FileChange(
                            path=path,
                            additions=0,
                            deletions=0,
                            is_new=diff_item.new_file,
                            is_deleted=diff_item.deleted_file
                        )
            except Exception:
                # HEAD might not exist in a new repo
                pass
                
            # 3. Get untracked files
            untracked = self.repo.untracked_files
            for path in untracked:
                if path not in changes_dict:
                    changes_dict[path] = FileChange(
                        path=path,
                        additions=0,
                        deletions=0,
                        is_new=True,
                        is_deleted=False
                    )
                    
        except Exception as e:
            print(f"Error getting git diff stats: {e}")
            pass
        
        return list(changes_dict.values())

# Made with Bob
