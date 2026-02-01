"""
Code Complexity Analyzer - C Language Support

This module provides complexity analysis for C source files using pycparser.

Author: Dylan
Created: February 1, 2026
Last Modified: February 1, 2026
"""

from pathlib import Path
from typing import List
import pycparser
from pycparser import c_ast

from .analyzer import FunctionMetrics


class CComplexityVisitor(c_ast.NodeVisitor):
    """
    AST visitor for analyzing C code complexity.
    
    This class extends pycparser's NodeVisitor to calculate complexity
    metrics for C functions, similar to what we do for Python.
    
    Attributes:
        functions: List of FunctionMetrics for analyzed functions
        current_function: The function currently being analyzed
        nesting_depth: Current nesting depth in control structures
        
    Created: February 1, 2026
    """
    
    def __init__(self):
        """
        Initialize the C complexity visitor.
        
        Created: February 1, 2026
        """
        self.functions: List[FunctionMetrics] = []
        self.current_function: FunctionMetrics | None = None
        self.nesting_depth = 0
    
    def visit_FuncDef(self, node):
        """
        Visit a function definition in C code.
        
        Args:
            node: The AST node representing the function definition
            
        Created: February 1, 2026
        """
        # Get function name
        func_name = node.decl.name
        
        # Get line number (if available)
        lineno = node.coord.line if node.coord else 0
        
        # Create metrics object
        func = FunctionMetrics(func_name, lineno)
        
        # Calculate lines of code (approximate)
        func.lines_of_code = self._estimate_loc(node)
        
        # Save current state
        previous_function = self.current_function
        previous_depth = self.nesting_depth
        
        # Analyze this function
        self.current_function = func
        self.nesting_depth = 0
        
        # Visit children to count complexity
        self.generic_visit(node)
        
        # Store max nesting depth
        func.max_nesting_depth = self.nesting_depth
        
        # Restore state
        self.current_function = previous_function
        self.nesting_depth = previous_depth
        
        # Add to results
        self.functions.append(func)
    
    def visit_If(self, node):
        """
        Visit an if statement.
        
        Args:
            node: The AST node representing the if statement
            
        Created: February 1, 2026
        """
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_For(self, node):
        """
        Visit a for loop.
        
        Args:
            node: The AST node representing the for loop
            
        Created: February 1, 2026
        """
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_While(self, node):
        """
        Visit a while loop.
        
        Args:
            node: The AST node representing the while loop
            
        Created: February 1, 2026
        """
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_DoWhile(self, node):
        """
        Visit a do-while loop.
        
        Args:
            node: The AST node representing the do-while loop
            
        Created: February 1, 2026
        """
        if self.current_function:
            self.current_function.cyclomatic_complexity += 1
        
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_Switch(self, node):
        """
        Visit a switch statement.
        
        Each case in a switch adds to complexity.
        
        Args:
            node: The AST node representing the switch statement
            
        Created: February 1, 2026
        """
        if self.current_function:
            # Count the number of case statements
            case_count = self._count_cases(node)
            self.current_function.cyclomatic_complexity += case_count
        
        self.nesting_depth += 1
        self.generic_visit(node)
        self.nesting_depth -= 1
    
    def visit_BinaryOp(self, node):
        """
        Visit a binary operation (like && or ||).
        
        Args:
            node: The AST node representing the binary operation
            
        Created: February 1, 2026
        """
        if self.current_function and node.op in ['&&', '||']:
            self.current_function.cyclomatic_complexity += 1
        
        self.generic_visit(node)
    
    def _count_cases(self, switch_node) -> int:
        """
        Count the number of case statements in a switch.
        
        Args:
            switch_node: The switch statement AST node
            
        Returns:
            Number of case statements
            
        Created: February 1, 2026
        """
        count = 0
        
        class CaseCounter(c_ast.NodeVisitor):
            def __init__(self):
                self.count = 0
            
            def visit_Case(self, node):
                self.count += 1
        
        counter = CaseCounter()
        counter.visit(switch_node)
        return counter.count
    
    def _estimate_loc(self, func_node) -> int:
        """
        Estimate lines of code in a C function.
        
        This is approximate since pycparser doesn't preserve
        all formatting information.
        
        Args:
            func_node: The function definition AST node
            
        Returns:
            Estimated lines of code
            
        Created: February 1, 2026
        """
        # Count the number of statements in the function
        # This is a rough approximation
        
        class StatementCounter(c_ast.NodeVisitor):
            def __init__(self):
                self.count = 0
            
            def visit_Decl(self, node):
                self.count += 1
            
            def visit_Assignment(self, node):
                self.count += 1
            
            def visit_FuncCall(self, node):
                self.count += 1
            
            def visit_Return(self, node):
                self.count += 1
        
        counter = StatementCounter()
        counter.visit(func_node)
        
        # Return statement count as a proxy for LOC
        return max(counter.count, 1)


def analyze_c_file(filepath: Path) -> List[FunctionMetrics]:
    """
    Analyze a C source file for complexity metrics.
    
    This function parses C code using pycparser and calculates
    complexity metrics similar to the Python analyzer.
    
    Args:
        filepath: Path to the C file to analyze
        
    Returns:
        List of FunctionMetrics objects for all functions in the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        pycparser.ParseError: If the C code has syntax errors
        
    Note:
        pycparser requires preprocessed C code (no #include, #define, etc.)
        For full C files, you may need to preprocess them first.
        
    Created: February 1, 2026
    """
    # Read the C source file
    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # Parse the C code
    # Note: pycparser expects preprocessed C code
    # For real-world use, you might need to run the C preprocessor first
    parser = pycparser.CParser()
    
    try:
        ast = parser.parse(source_code, filename=str(filepath))
    except pycparser.ParseError:
        # If parsing fails, try with fake libc headers
        # This helps with standard library includes
        from pycparser.plyparser import ParseError
        raise ParseError(f"Failed to parse {filepath}. "
                        "C files with #include directives need preprocessing.")
    
    # Analyze the AST
    visitor = CComplexityVisitor()
    visitor.visit(ast)
    
    return visitor.functions