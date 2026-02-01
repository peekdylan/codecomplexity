"""
Code Complexity Analyzer - Core Analysis Module

This module provides the core functionality for analyzing Python source code
and calculating complexity metrics including cyclomatic complexity, lines of
code, and maximum nesting depth.

Author: Dylan
Created: January 31, 2026
Last Modified: January 31, 2026
"""

import ast
from pathlib import Path
from typing import Dict, List, Any


class FunctionMetrics:
    """
    Data class that stores complexity metrics for a single function.
    
    This class encapsulates all the metrics we track for each function
    in the analyzed codebase, including complexity, size, and structure.
    
    Attributes:
        name (str): The name of the function as it appears in the source code
        lineno (int): The line number where the function is defined
        lines_of_code (int): Count of non-blank, non-comment lines in the function
        cyclomatic_complexity (int): McCabe complexity score (starts at 1)
        max_nesting_depth (int): Maximum depth of nested control structures
    
    Created: January 31, 2026
    """
    
    def __init__(self, name: str, lineno: int):
        """
        Initialize a new FunctionMetrics object.
        
        Args:
            name: The function name
            lineno: The line number where the function starts
            
        Note: Cyclomatic complexity starts at 1 because even a function with
        no branches has one execution path through it.
        
        Created: January 31, 2026
        """
        self.name = name
        self.lineno = lineno
        self.lines_of_code = 0
        self.cyclomatic_complexity = 1  # Base complexity for any function
        self.max_nesting_depth = 0


class PythonAnalyzer(ast.NodeVisitor):
    """
    AST visitor that traverses Python code and calculates complexity metrics.
    
    This class extends Python's ast.NodeVisitor to walk through the Abstract
    Syntax Tree (AST) of Python source code. As it visits each node, it
    calculates various complexity metrics.
    
    The visitor pattern allows us to define custom behavior for each type
    of AST node (functions, if statements, loops, etc.) without modifying
    the AST itself.
    
    Attributes:
        source_code (str): The raw Python source code being analyzed
        source_lines (List[str]): Source code split into individual lines
        functions (List[FunctionMetrics]): List of all analyzed functions
        current_function (FunctionMetrics | None): The function currently being analyzed
        nesting_depth (int): Current depth in nested control structures
    
    Created: January 31, 2026
    """
    
    def __init__(self, source_code: str):
        """
        Initialize the analyzer with source code to analyze.
        
        Args:
            source_code: The complete Python source code as a string
            
        The source code is stored both as a complete string and as individual
        lines to facilitate different types of analysis (AST parsing vs line counting).
        
        Created: January 31, 2026
        """
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.functions: List[FunctionMetrics] = []
        self.current_function: FunctionMetrics | None = None
        self.nesting_depth = 0
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visit a function definition node and calculate its metrics.
        
        This is called automatically by the AST visitor when it encounters
        a function definition. It creates a new FunctionMetrics object,
        calculates all metrics for the function, then continues visiting
        the function's child nodes.
        
        Args:
            node: The AST node representing the function definition
            
        The method uses a stack-based approach to handle nested functions:
        - Save the current function context
        - Analyze the new function
        - Restore the previous context
        
        This ensures that metrics for inner functions don't affect outer
        function metrics.
        
        Created: January 31, 2026
        Last Modified: January 31, 2026
        """
        # Create a new metrics object for this function
        func = FunctionMetrics(node.name, node.lineno)
        
        # Calculate the total lines of code in this function
        # This excludes blank lines and comments for a more accurate metric
        func.lines_of_code = self._calculate_loc(node)
        
        # Save the current function context so we can restore it later
        # This is critical for handling nested functions correctly
        previous_function = self.current_function
        self.current_function = func
        
        # Reset nesting depth for this new function scope
        # Each function starts at depth 0
        previous_depth = self.nesting_depth
        self.nesting_depth = 0
        
        # Visit all child nodes (statements inside the function)
        # This is where we'll encounter if/for/while statements that
        # contribute to complexity and nesting depth
        self.generic_visit(node)
        
        # Store the maximum nesting depth we encountered
        # This is tracked during the visit of child nodes
        func.max_nesting_depth = self.nesting_depth
        
        # Restore the previous function context
        # This is important for nested function definitions
        self.nesting_depth = previous_depth
        self.current_function = previous_function
        
        # Add this function's metrics to our results list
        self.functions.append(func)
    
    def visit_If(self, node: ast.If):
        """
        Visit an if statement and update complexity metrics.
        
        If statements create branching paths in the code, which increases
        cyclomatic complexity. Each if/elif/else block represents a decision
        point that adds one to the complexity score.
        
        Args:
            node: The AST node representing the if statement
            
        Nesting depth is also tracked here because if statements can be
        nested inside each other or inside loops.
        
        Created: January 31, 2026
        """
        # Only increment complexity if we're inside a function
        # Top-level if statements don't contribute to function complexity
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        # Track that we've entered a nested structure
        self.nesting_depth += 1
        
        # Continue visiting child nodes (code inside the if block)
        self.generic_visit(node)
        
        # We've exited this level of nesting
        self.nesting_depth -= 1
    
    def visit_For(self, node: ast.For):
        """
        Visit a for loop and update complexity metrics.
        
        For loops add to cyclomatic complexity because they represent
        a decision point: the loop condition that determines whether to
        continue iterating or exit the loop.
        
        Args:
            node: The AST node representing the for loop
            
        Created: January 31, 2026
        """
        # Increment complexity for this decision point
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        # Track nesting depth as we enter the loop body
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_While(self, node: ast.While):
        """
        Visit a while loop and update complexity metrics.
        
        While loops are similar to for loops in their contribution to
        complexity - they represent a decision point with a condition
        that's evaluated on each iteration.
        
        Args:
            node: The AST node representing the while loop
            
        Created: January 31, 2026
        """
        # Increment complexity for the loop condition
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        # Track nesting as we enter the loop body
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """
        Visit an exception handler (except block) and update complexity.
        
        Exception handlers add to complexity because they represent an
        alternative execution path. When an exception is raised, the code
        can branch to the except handler instead of continuing normally.
        
        Args:
            node: The AST node representing the except handler
            
        Note: Each except block in a try/except chain adds its own complexity.
        
        Created: January 31, 2026
        """
        # Each exception handler is a potential execution path
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        # Track nesting depth within the except block
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_With(self, node: ast.With):
        """
        Visit a with statement (context manager) and track nesting.
        
        With statements don't add to cyclomatic complexity (they don't
        create branching), but they do add to nesting depth since they
        create a new indented block of code.
        
        Args:
            node: The AST node representing the with statement
            
        Created: January 31, 2026
        """
        # With statements increase nesting but not complexity
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_BoolOp(self, node: ast.BoolOp):
        """
        Visit a boolean operation (and/or) and update complexity.
        
        Boolean operators like 'and' and 'or' add to cyclomatic complexity
        because they create additional decision points. For example:
        
        if x and y:  # Two conditions = complexity +2 (one for if, one for and)
        
        Args:
            node: The AST node representing the boolean operation
            
        The complexity increase is (number of conditions - 1) because the
        first condition is already counted by the parent if/while/etc.
        
        Example:
            if a and b and c:  # Three values = +2 complexity
            
        Created: January 31, 2026
        """
        if self.current_function:
            # node.values contains all the operands in the boolean expression
            # If we have "a and b and c", node.values has 3 elements
            # We add (3 - 1) = 2 to complexity
            self.current_function.cyclomatic_complexity += len(node.values) - 1
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def _calculate_loc(self, node: ast.FunctionDef) -> int:
        """
        Calculate lines of code for a function, excluding blanks and comments.
        
        This provides a more accurate measure of function size than simply
        counting all lines. We exclude:
        - Blank lines (whitespace only)
        - Comment-only lines (lines starting with #)
        
        Args:
            node: The AST node representing the function
            
        Returns:
            int: The number of actual code lines in the function
            
        The calculation works by:
        1. Finding the start and end line numbers from the AST
        2. Extracting those lines from the source code
        3. Filtering out blank and comment lines
        4. Counting what remains
        
        Created: January 31, 2026
        """
        # Convert to 0-indexed (Python lists are 0-indexed but line numbers are 1-indexed)
        start_line = node.lineno - 1
        
        # Find the last line of the function by walking the entire AST subtree
        # We need to check all nodes because the function might contain nested
        # structures that extend beyond simple sequential statements
        if node.body:
            # Get the maximum end_lineno from all nodes in the function
            # This handles cases where the last statement spans multiple lines
            end_line = max(
                getattr(stmt, 'end_lineno', stmt.lineno) 
                for stmt in ast.walk(node)
                if hasattr(stmt, 'lineno')
            )
        else:
            # Empty function - just the def line
            end_line = node.lineno
        
        # Extract the relevant lines from the source code
        lines = self.source_lines[start_line:end_line]
        
        # Count lines that are not blank and not pure comments
        # strip() removes leading/trailing whitespace
        # We check if the stripped line exists and doesn't start with #
        loc = sum(
            1 for line in lines 
            if line.strip() and not line.strip().startswith('#')
        )
        
        return loc


def analyze_python_file(filepath: Path) -> List[FunctionMetrics]:
    """
    Analyze a Python file and return complexity metrics for all functions.
    
    This is the main entry point for analyzing a single Python file. It:
    1. Reads the source code from the file
    2. Parses it into an Abstract Syntax Tree (AST)
    3. Walks the AST to calculate metrics
    4. Returns a list of metrics for all functions found
    
    Args:
        filepath: Path object pointing to the Python file to analyze
        
    Returns:
        List of FunctionMetrics objects, one for each function in the file
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        SyntaxError: If the Python file has syntax errors
        UnicodeDecodeError: If the file encoding is not UTF-8
        
    Example:
        >>> from pathlib import Path
        >>> metrics = analyze_python_file(Path("my_script.py"))
        >>> for func in metrics:
        ...     print(f"{func.name}: complexity={func.cyclomatic_complexity}")
        
    Created: January 31, 2026
    """
    # Read the entire source file
    # Using UTF-8 encoding as it's the standard for Python files
    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # Parse the source code into an Abstract Syntax Tree
    # The filename parameter is used in error messages if parsing fails
    tree = ast.parse(source_code, filename=str(filepath))
    
    # Create an analyzer instance and walk the AST
    # The visitor pattern will call our visit_* methods for each node type
    analyzer = PythonAnalyzer(source_code)
    analyzer.visit(tree)
    
    # Return all the function metrics we collected
    return analyzer.functions