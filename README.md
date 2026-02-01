# codecomplexity

A professional CLI tool for analyzing code complexity metrics in Python codebases. Helps identify overly complex functions that may need refactoring.

## Features

- **Cyclomatic Complexity Analysis** - Measures the number of independent paths through code
- **Lines of Code Counting** - Tracks function size (excluding comments and blank lines)
- **Nesting Depth Detection** - Identifies deeply nested control structures
- **Customizable Thresholds** - Set your own warning levels
- **Color-Coded Output** - Easy-to-read reports with visual indicators
- **Warnings-Only Mode** - Focus on problematic functions

## Installation

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install from source
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/codecomplexity.git
cd codecomplexity

# Install with uv
uv pip install -e .
```

## Usage

### Basic Analysis

Analyze a Python file:
```bash
uv run codecomplexity analyze path/to/your_file.py
```

### Custom Thresholds

Set custom warning thresholds:
```bash
uv run codecomplexity analyze your_file.py \
  --complexity-threshold 15 \
  --loc-threshold 100 \
  --nesting-threshold 5
```

### Warnings Only

Show only functions that exceed thresholds:
```bash
uv run codecomplexity analyze your_file.py --warnings-only
```

## Output Example
```
================================================================================
CODE COMPLEXITY ANALYSIS REPORT
================================================================================

Function: complex_function (line 45) ⚠️  WARNING
--------------------------------------------------------------------------------
  Cyclomatic Complexity: 12 [HIGH]
  Lines of Code: 85 [HIGH]
  Max Nesting Depth: 3 [OK]

Function: simple_function (line 10) ✓
--------------------------------------------------------------------------------
  Cyclomatic Complexity: 2 [OK]
  Lines of Code: 15 [OK]
  Max Nesting Depth: 1 [OK]

================================================================================
SUMMARY
================================================================================
Total Functions Analyzed: 2
Average Complexity: 7.00
Highest Complexity: 12
Functions Exceeding Thresholds: 1
================================================================================
```

## Understanding the Metrics

### Cyclomatic Complexity
Measures the number of independent paths through code. Higher values indicate more complex logic.

**Guidelines:**
- 1-10: Simple, easy to test
- 11-20: Moderate complexity
- 21+: High complexity, consider refactoring

### Lines of Code (LOC)
Counts actual code lines, excluding comments and blank lines.

**Guidelines:**
- < 50: Good
- 50-100: Acceptable
- 100+: Consider breaking into smaller functions

### Nesting Depth
Measures how deeply control structures are nested (if/for/while/try).

**Guidelines:**
- 1-3: Good
- 4-5: Acceptable
- 6+: Hard to understand, refactor recommended

## Development

### Project Structure
```
codecomplexity-project/
├── codecomplexity/          # Source code
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py          # Core analysis logic
│   └── cli.py               # Command-line interface
├── pyproject.toml           # Project configuration
├── README.md
└── .gitignore
```

### Running Tests
```bash
# Analyze the tool itself
uv run codecomplexity analyze codecomplexity/analyzer.py
uv run codecomplexity analyze codecomplexity/cli.py
```

## Technology Stack

- **Python 3.10+** - Core language
- **AST (Abstract Syntax Tree)** - Code parsing and analysis
- **argparse** - Command-line interface
- **colorama** - Cross-platform colored output

## Author

Dylan - [Boot.dev Student](https://boot.dev)

## License

MIT License - Feel free to use this project for learning and portfolio purposes.

## Acknowledgments

Built as part of the Boot.dev Computer Science curriculum. This project demonstrates:
- Working with Abstract Syntax Trees
- Building professional CLI tools
- Code quality analysis
- Software engineering best practices