"""
Code Complexity Analyzer - Directory Scanner

This module provides functionality for scanning directories and analyzing
multiple Python files in a project.

Author: Dylan
Created: February 1, 2026
Last Modified: February 1, 2026
"""

from pathlib import Path
from typing import List, Dict
from .analyzer import analyze_python_file, FunctionMetrics


class ProjectMetrics:
    """
    Stores aggregated metrics for an entire project.
    
    This class holds metrics for all files in a project, providing
    both file-level and project-level statistics.
    
    Attributes:
        file_metrics: Dictionary mapping file paths to their function metrics
        total_files: Total number of Python files analyzed
        total_functions: Total number of functions across all files
        
    Created: February 1, 2026
    """
    
    def __init__(self):
        """
        Initialize an empty ProjectMetrics object.
        
        Created: February 1, 2026
        """
        self.file_metrics: Dict[Path, List[FunctionMetrics]] = {}
        self.total_files = 0
        self.total_functions = 0
    
    def add_file(self, filepath: Path, metrics: List[FunctionMetrics]) -> None:
        """
        Add metrics for a single file to the project.
        
        Args:
            filepath: Path to the analyzed file
            metrics: List of function metrics from that file
            
        Created: February 1, 2026
        """
        self.file_metrics[filepath] = metrics
        self.total_files += 1
        self.total_functions += len(metrics)
    
    def get_all_functions(self) -> List[FunctionMetrics]:
        """
        Get a flat list of all function metrics across all files.
        
        Returns:
            List of all FunctionMetrics objects from all files
            
        Created: February 1, 2026
        """
        all_functions = []
        for metrics in self.file_metrics.values():
            all_functions.extend(metrics)
        return all_functions
    
    def get_average_complexity(self) -> float:
        """
        Calculate average cyclomatic complexity across all functions.
        
        Returns:
            Average complexity as a float, or 0 if no functions found
            
        Created: February 1, 2026
        """
        all_functions = self.get_all_functions()
        if not all_functions:
            return 0.0
        
        total_complexity = sum(f.cyclomatic_complexity for f in all_functions)
        return total_complexity / len(all_functions)
    
    def get_max_complexity(self) -> int:
        """
        Find the highest cyclomatic complexity across all functions.
        
        Returns:
            Maximum complexity value, or 0 if no functions found
            
        Created: February 1, 2026
        """
        all_functions = self.get_all_functions()
        if not all_functions:
            return 0
        
        return max(f.cyclomatic_complexity for f in all_functions)


def find_python_files(directory: Path, recursive: bool = True) -> List[Path]:
    """
    Find all Python files in a directory.
    
    This function scans a directory for .py files, optionally recursing
    into subdirectories. It skips common directories that typically don't
    contain source code (like virtual environments and cache directories).
    
    Args:
        directory: Path to the directory to scan
        recursive: If True, scan subdirectories recursively
        
    Returns:
        List of Path objects pointing to Python files
        
    Directories excluded from scanning:
    - .venv, venv, env (virtual environments)
    - __pycache__ (Python cache)
    - .git (version control)
    - node_modules (Node.js dependencies)
    - .tox, .pytest_cache (testing artifacts)
    
    Created: February 1, 2026
    """
    # Directories to skip during scanning
    # These typically contain generated code or dependencies
    skip_dirs = {
        '.venv', 'venv', 'env', 'ENV',
        '__pycache__',
        '.git',
        'node_modules',
        '.tox',
        '.pytest_cache',
        'build',
        'dist',
        '.eggs',
        '*.egg-info'
    }
    
    python_files = []
    
    if recursive:
        # Recursively find all .py files
        for path in directory.rglob('*.py'):
            # Check if any parent directory is in skip_dirs
            if not any(part in skip_dirs for part in path.parts):
                python_files.append(path)
    else:
        # Only check the immediate directory
        for path in directory.glob('*.py'):
            python_files.append(path)
    
    return sorted(python_files)


def analyze_directory(
    directory: Path,
    recursive: bool = True,
    progress_callback=None
) -> ProjectMetrics:
    """
    Analyze all Python files in a directory.
    
    This function scans a directory for Python files and analyzes each one,
    aggregating the results into a ProjectMetrics object.
    
    Args:
        directory: Path to the directory to analyze
        recursive: If True, analyze subdirectories recursively
        progress_callback: Optional callback function called for each file
                          Signature: callback(current_file: Path, total_files: int, current_index: int)
        
    Returns:
        ProjectMetrics object containing all analyzed files
        
    Example:
        >>> from pathlib import Path
        >>> def show_progress(file, total, index):
        ...     print(f"Analyzing {index}/{total}: {file}")
        >>> metrics = analyze_directory(Path("my_project"), progress_callback=show_progress)
        
    Created: February 1, 2026
    """
    # Find all Python files in the directory
    python_files = find_python_files(directory, recursive)
    
    # Create project metrics object
    project = ProjectMetrics()
    
    # Analyze each file
    total_files = len(python_files)
    for index, filepath in enumerate(python_files, start=1):
        # Call progress callback if provided
        if progress_callback:
            progress_callback(filepath, total_files, index)
        
        try:
            # Analyze the file
            metrics = analyze_python_file(filepath)
            project.add_file(filepath, metrics)
        except (SyntaxError, UnicodeDecodeError) as e:
            # Skip files that can't be parsed
            # In a production tool, you might want to log these errors
            continue
    
    return project