"""
Code Complexity Analyzer - Command Line Interface

This module provides the command-line interface for the codecomplexity tool.
It handles argument parsing, user input validation, and output formatting.

Author: Dylan
Created: January 31, 2026
Last Modified: February 1, 2026
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List

# Import colorama for cross-platform colored terminal output
# init() is called to enable color support on Windows
from colorama import Fore, Style, init

from .analyzer import analyze_python_file, FunctionMetrics
from .scanner import analyze_directory, ProjectMetrics

# Initialize colorama for cross-platform color support
# Created: January 31, 2026
init(autoreset=True)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command-line argument parser.
    
    This function sets up all the command-line options and arguments
    that users can provide when running the tool.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
        
    Created: January 31, 2026
    Last Modified: February 1, 2026
    """
    parser = argparse.ArgumentParser(
        prog='codecomplexity',
        description='Analyze code complexity metrics for Python files',
        epilog='Example: codecomplexity analyze my_script.py'
    )
    
    # Create subcommands (analyze is the main one for now)
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # 'analyze' subcommand
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a Python file for complexity metrics'
    )
    
    # Required argument: the file to analyze
    analyze_parser.add_argument(
        'filepath',
        type=str,
        help='Path to the Python file to analyze'
    )
    
    # Optional: complexity threshold for warnings
    analyze_parser.add_argument(
        '--complexity-threshold',
        type=int,
        default=10,
        help='Warn about functions with complexity above this threshold (default: 10)'
    )
    
    # Optional: lines of code threshold
    analyze_parser.add_argument(
        '--loc-threshold',
        type=int,
        default=50,
        help='Warn about functions with more lines than this threshold (default: 50)'
    )
    
    # Optional: nesting depth threshold
    analyze_parser.add_argument(
        '--nesting-threshold',
        type=int,
        default=4,
        help='Warn about functions with nesting deeper than this threshold (default: 4)'
    )
    
    # Optional: show only problematic functions
    analyze_parser.add_argument(
        '--warnings-only',
        action='store_true',
        help='Only show functions that exceed thresholds'
    )
    
    # Optional: export results to JSON
    analyze_parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Export results to JSON file (e.g., --output results.json)'
    )
    
    # 'scan' subcommand for analyzing directories
    scan_parser = subparsers.add_parser(
        'scan',
        help='Scan a directory and analyze all Python files'
    )
    
    scan_parser.add_argument(
        'directory',
        type=str,
        help='Path to the directory to scan'
    )
    
    scan_parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Only scan the immediate directory, not subdirectories'
    )
    
    scan_parser.add_argument(
        '--complexity-threshold',
        type=int,
        default=10,
        help='Complexity threshold for warnings (default: 10)'
    )
    
    scan_parser.add_argument(
        '--loc-threshold',
        type=int,
        default=50,
        help='Lines of code threshold for warnings (default: 50)'
    )
    
    scan_parser.add_argument(
        '--nesting-threshold',
        type=int,
        default=4,
        help='Nesting depth threshold for warnings (default: 4)'
    )
    
    scan_parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Export results to JSON file'
    )
    
    return parser


def format_metrics_output(
    metrics: List[FunctionMetrics],
    complexity_threshold: int,
    loc_threshold: int,
    nesting_threshold: int,
    warnings_only: bool = False
) -> str:
    """
    Format the function metrics into a readable, colorized text report.
    
    This function takes the raw metrics data and formats it into a
    human-readable report with clear sections, visual indicators,
    and color coding for problematic functions.
    
    Colors used:
    - Green: Functions that pass all thresholds
    - Yellow: Warning indicators
    - Red: High complexity/problematic metrics
    - Cyan: Headers and section separators
    
    Args:
        metrics: List of FunctionMetrics objects to format
        complexity_threshold: Complexity level to trigger warnings
        loc_threshold: Lines of code to trigger warnings
        nesting_threshold: Nesting depth to trigger warnings
        warnings_only: If True, only show functions exceeding thresholds
        
    Returns:
        str: Formatted, colorized report as a string
        
    Created: January 31, 2026
    Last Modified: January 31, 2026
    """
    if not metrics:
        return "No functions found in the file."
    
    # Filter metrics if warnings_only is set
    if warnings_only:
        metrics = [
            m for m in metrics
            if (m.cyclomatic_complexity > complexity_threshold or
                m.lines_of_code > loc_threshold or
                m.max_nesting_depth > nesting_threshold)
        ]
        
        if not metrics:
            return f"{Fore.GREEN}✓ No functions exceed the specified thresholds!"
    
    # Build the output string
    lines = []
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    lines.append(f"{Fore.CYAN}CODE COMPLEXITY ANALYSIS REPORT")
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    lines.append("")
    
    # Sort functions by complexity (highest first)
    sorted_metrics = sorted(
        metrics,
        key=lambda m: m.cyclomatic_complexity,
        reverse=True
    )
    
    for func in sorted_metrics:
        # Determine if this function has issues
        has_high_complexity = func.cyclomatic_complexity > complexity_threshold
        has_many_lines = func.lines_of_code > loc_threshold
        has_deep_nesting = func.max_nesting_depth > nesting_threshold
        
        # Determine overall function health
        has_any_issues = has_high_complexity or has_many_lines or has_deep_nesting
        
        # Add a warning indicator if any threshold is exceeded
        if has_any_issues:
            warning = f" {Fore.YELLOW}⚠️  WARNING"
            func_color = Fore.YELLOW
        else:
            warning = f" {Fore.GREEN}✓"
            func_color = Fore.GREEN
        
        # Function header
        lines.append(f"{func_color}Function: {func.name} (line {func.lineno}){warning}")
        lines.append(f"{Fore.CYAN}{'-' * 80}")
        
        # Cyclomatic Complexity
        if has_high_complexity:
            complexity_color = Fore.RED
            complexity_status = "HIGH"
        else:
            complexity_color = Fore.GREEN
            complexity_status = "OK"
        
        lines.append(
            f"  Cyclomatic Complexity: {func.cyclomatic_complexity} "
            f"{complexity_color}[{complexity_status}]{Style.RESET_ALL}"
        )
        
        # Lines of code
        if has_many_lines:
            loc_color = Fore.RED
            loc_status = "HIGH"
        else:
            loc_color = Fore.GREEN
            loc_status = "OK"
        
        lines.append(
            f"  Lines of Code: {func.lines_of_code} "
            f"{loc_color}[{loc_status}]{Style.RESET_ALL}"
        )
        
        # Nesting depth
        if has_deep_nesting:
            nesting_color = Fore.RED
            nesting_status = "HIGH"
        else:
            nesting_color = Fore.GREEN
            nesting_status = "OK"
        
        lines.append(
            f"  Max Nesting Depth: {func.max_nesting_depth} "
            f"{nesting_color}[{nesting_status}]{Style.RESET_ALL}"
        )
        
        lines.append("")
    
    # Summary statistics
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    lines.append(f"{Fore.CYAN}SUMMARY")
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    lines.append(f"Total Functions Analyzed: {len(metrics)}")
    
    avg_complexity = sum(m.cyclomatic_complexity for m in metrics) / len(metrics)
    lines.append(f"Average Complexity: {avg_complexity:.2f}")
    
    max_complexity = max(m.cyclomatic_complexity for m in metrics)
    lines.append(f"Highest Complexity: {max_complexity}")
    
    # Count warnings
    warning_count = sum(
        1 for m in metrics
        if (m.cyclomatic_complexity > complexity_threshold or
            m.lines_of_code > loc_threshold or
            m.max_nesting_depth > nesting_threshold)
    )
    
    if warning_count > 0:
        warning_color = Fore.YELLOW
    else:
        warning_color = Fore.GREEN
    
    lines.append(f"Functions Exceeding Thresholds: {warning_color}{warning_count}{Style.RESET_ALL}")
    
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    
    return "\n".join(lines)


def format_project_output(
    project: ProjectMetrics,
    complexity_threshold: int,
    loc_threshold: int,
    nesting_threshold: int
) -> str:
    """
    Format project-wide metrics into a readable report.
    
    This function creates a summary report for an entire project,
    showing file-by-file statistics and overall project health.
    
    Args:
        project: ProjectMetrics object containing all file metrics
        complexity_threshold: Complexity threshold for warnings
        loc_threshold: Lines of code threshold for warnings
        nesting_threshold: Nesting depth threshold for warnings
        
    Returns:
        str: Formatted, colorized project report
        
    Created: February 1, 2026
    """
    lines = []
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    lines.append(f"{Fore.CYAN}PROJECT COMPLEXITY ANALYSIS")
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    lines.append("")
    
    # Project-wide summary
    lines.append(f"{Fore.CYAN}PROJECT SUMMARY")
    lines.append(f"{Fore.CYAN}{'-' * 80}")
    lines.append(f"Total Files Analyzed: {project.total_files}")
    lines.append(f"Total Functions: {project.total_functions}")
    lines.append(f"Average Complexity: {project.get_average_complexity():.2f}")
    lines.append(f"Highest Complexity: {project.get_max_complexity()}")
    lines.append("")
    
    # Per-file breakdown
    lines.append(f"{Fore.CYAN}FILE BREAKDOWN")
    lines.append(f"{Fore.CYAN}{'-' * 80}")
    
    # Sort files by average complexity
    file_stats = []
    for filepath, metrics in project.file_metrics.items():
        if metrics:
            avg_complexity = sum(m.cyclomatic_complexity for m in metrics) / len(metrics)
            max_complexity = max(m.cyclomatic_complexity for m in metrics)
            warning_count = sum(
                1 for m in metrics
                if (m.cyclomatic_complexity > complexity_threshold or
                    m.lines_of_code > loc_threshold or
                    m.max_nesting_depth > nesting_threshold)
            )
            file_stats.append((filepath, len(metrics), avg_complexity, max_complexity, warning_count))
    
    # Sort by warning count (descending), then by max complexity
    file_stats.sort(key=lambda x: (x[4], x[3]), reverse=True)
    
    for filepath, func_count, avg_complexity, max_complexity, warning_count in file_stats:
        # Color code based on warnings
        if warning_count > 0:
            file_color = Fore.YELLOW
            status = f"⚠️  {warning_count} warnings"
        else:
            file_color = Fore.GREEN
            status = "✓ OK"
        
        lines.append(f"{file_color}{filepath}")
        lines.append(f"  Functions: {func_count} | Avg Complexity: {avg_complexity:.2f} | "
                    f"Max: {max_complexity} | {status}{Style.RESET_ALL}")
        lines.append("")
    
    lines.append(f"{Fore.CYAN}{'=' * 80}")
    
    return "\n".join(lines)


def export_to_json(
    metrics: List[FunctionMetrics],
    filepath: Path,
    output_file: str
) -> None:
    """
    Export function metrics to a JSON file.
    
    This function converts the metrics data into a structured JSON format
    that can be consumed by other tools, CI/CD pipelines, or dashboards.
    
    JSON Structure:
    {
        "file": "path/to/file.py",
        "timestamp": "2026-01-31T20:00:00",
        "summary": {...},
        "functions": [...]
    }
    
    Args:
        metrics: List of FunctionMetrics objects to export
        filepath: Path to the analyzed file
        output_file: Path where JSON should be written
        
    Created: January 31, 2026
    """
    # Calculate summary statistics
    avg_complexity = sum(m.cyclomatic_complexity for m in metrics) / len(metrics) if metrics else 0
    max_complexity = max((m.cyclomatic_complexity for m in metrics), default=0)
    
    # Build the JSON structure
    data = {
        "file": str(filepath),
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_functions": len(metrics),
            "average_complexity": round(avg_complexity, 2),
            "highest_complexity": max_complexity
        },
        "functions": [
            {
                "name": m.name,
                "line_number": m.lineno,
                "cyclomatic_complexity": m.cyclomatic_complexity,
                "lines_of_code": m.lines_of_code,
                "max_nesting_depth": m.max_nesting_depth
            }
            for m in metrics
        ]
    }
    
    # Write to file with nice formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"{Fore.GREEN}✓ Results exported to {output_file}{Style.RESET_ALL}")


def export_project_to_json(
    project: ProjectMetrics,
    output_file: str
) -> None:
    """
    Export project-wide metrics to a JSON file.
    
    This function exports all metrics for a scanned project directory
    into a structured JSON format.
    
    Args:
        project: ProjectMetrics object containing all file metrics
        output_file: Path where JSON should be written
        
    Created: February 1, 2026
    """
    # Build the JSON structure
    data = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_files": project.total_files,
            "total_functions": project.total_functions,
            "average_complexity": round(project.get_average_complexity(), 2),
            "highest_complexity": project.get_max_complexity()
        },
        "files": []
    }
    
    # Add each file's metrics
    for filepath, metrics in project.file_metrics.items():
        if metrics:
            avg_complexity = sum(m.cyclomatic_complexity for m in metrics) / len(metrics)
            max_complexity = max(m.cyclomatic_complexity for m in metrics)
            
            file_data = {
                "file": str(filepath),
                "summary": {
                    "total_functions": len(metrics),
                    "average_complexity": round(avg_complexity, 2),
                    "highest_complexity": max_complexity
                },
                "functions": [
                    {
                        "name": m.name,
                        "line_number": m.lineno,
                        "cyclomatic_complexity": m.cyclomatic_complexity,
                        "lines_of_code": m.lines_of_code,
                        "max_nesting_depth": m.max_nesting_depth
                    }
                    for m in metrics
                ]
            }
            data["files"].append(file_data)
    
    # Write to file with nice formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"{Fore.GREEN}✓ Project results exported to {output_file}{Style.RESET_ALL}")


def analyze_command(args: argparse.Namespace) -> int:
    """
    Execute the 'analyze' command.
    
    This function is called when the user runs 'codecomplexity analyze <file>'.
    It validates the input, runs the analysis, and displays the results.
    
    Args:
        args: Parsed command-line arguments from argparse
        
    Returns:
        int: Exit code (0 for success, 1 for error)
        
    Created: January 31, 2026
    Last Modified: January 31, 2026
    """
    # Convert the filepath string to a Path object
    filepath = Path(args.filepath)
    
    # Validate that the file exists
    if not filepath.exists():
        print(f"{Fore.RED}Error: File '{filepath}' not found.{Style.RESET_ALL}", file=sys.stderr)
        return 1
    
    # Validate that it's actually a file (not a directory)
    if not filepath.is_file():
        print(f"{Fore.RED}Error: '{filepath}' is not a file.{Style.RESET_ALL}", file=sys.stderr)
        return 1
    
    # Validate that it's a Python file
    if filepath.suffix != '.py':
        print(f"{Fore.YELLOW}Warning: '{filepath}' doesn't have a .py extension.{Style.RESET_ALL}", file=sys.stderr)
        print("Attempting to analyze anyway...", file=sys.stderr)
    
    try:
        # Run the analysis
        print(f"{Fore.CYAN}Analyzing {filepath}...{Style.RESET_ALL}\n")
        metrics = analyze_python_file(filepath)
        
        # If JSON output requested, export to file
        if args.output:
            export_to_json(metrics, filepath, args.output)
        
        # Always show the terminal output
        output = format_metrics_output(
            metrics,
            args.complexity_threshold,
            args.loc_threshold,
            args.nesting_threshold,
            args.warnings_only
        )
        print(output)
        
        return 0
        
    except SyntaxError as e:
        print(f"{Fore.RED}Error: Syntax error in Python file: {e}{Style.RESET_ALL}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to analyze file: {e}{Style.RESET_ALL}", file=sys.stderr)
        return 1


def scan_command(args: argparse.Namespace) -> int:
    """
    Execute the 'scan' command.
    
    This function is called when the user runs 'codecomplexity scan <directory>'.
    It scans a directory for Python files and analyzes them all.
    
    Args:
        args: Parsed command-line arguments from argparse
        
    Returns:
        int: Exit code (0 for success, 1 for error)
        
    Created: February 1, 2026
    """
    # Convert the directory string to a Path object
    directory = Path(args.directory)
    
    # Validate that the directory exists
    if not directory.exists():
        print(f"{Fore.RED}Error: Directory '{directory}' not found.{Style.RESET_ALL}", file=sys.stderr)
        return 1
    
    # Validate that it's actually a directory
    if not directory.is_dir():
        print(f"{Fore.RED}Error: '{directory}' is not a directory.{Style.RESET_ALL}", file=sys.stderr)
        return 1
    
    try:
        # Determine if we should recurse
        recursive = not args.no_recursive
        
        # Progress callback to show which file we're analyzing
        def show_progress(filepath: Path, total: int, current: int):
            print(f"{Fore.CYAN}[{current}/{total}] Analyzing {filepath}...{Style.RESET_ALL}")
        
        # Run the analysis
        print(f"{Fore.CYAN}Scanning directory: {directory}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Recursive: {recursive}{Style.RESET_ALL}\n")
        
        project = analyze_directory(directory, recursive, show_progress)
        
        print("")  # Blank line after progress
        
        # If JSON output requested, export to file
        if args.output:
            export_project_to_json(project, args.output)
        
        # Show the terminal output
        output = format_project_output(
            project,
            args.complexity_threshold,
            args.loc_threshold,
            args.nesting_threshold
        )
        print(output)
        
        return 0
        
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to scan directory: {e}{Style.RESET_ALL}", file=sys.stderr)
        return 1


def main() -> int:
    """
    Main entry point for the CLI application.
    
    This function is called when the user runs the 'codecomplexity' command.
    It parses arguments and dispatches to the appropriate command handler.
    
    Returns:
        int: Exit code to return to the operating system
        
    Created: January 31, 2026
    Last Modified: February 1, 2026
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # If no command was specified, show help
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to the appropriate command handler
    if args.command == 'analyze':
        return analyze_command(args)
    elif args.command == 'scan':
        return scan_command(args)
    
    # This shouldn't happen, but just in case
    print(f"{Fore.RED}Error: Unknown command '{args.command}'{Style.RESET_ALL}", file=sys.stderr)
    return 1


# This allows the module to be run directly: python -m codecomplexity.cli
if __name__ == '__main__':
    sys.exit(main())