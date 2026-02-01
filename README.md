# codecomplexity

A professional CLI tool for analyzing code complexity metrics in Python and C codebases. Helps identify overly complex functions that may need refactoring.

![Language](https://img.shields.io/badge/language-Python-blue)
![Version](https://img.shields.io/badge/version-0.2.0-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

### Core Analysis
- **Cyclomatic Complexity Analysis** - Measures the number of independent paths through code
- **Lines of Code Counting** - Tracks function size (excluding comments and blank lines)
- **Nesting Depth Detection** - Identifies deeply nested control structures
- **Multi-Language Support** - Analyze both Python and C source files
- **Directory Scanning** - Analyze entire projects with recursive directory traversal

### Output Options
- **Color-Coded Terminal Output** - Easy-to-read reports with visual indicators
- **JSON Export** - Export results for CI/CD pipelines, dashboards, or further analysis
- **Customizable Thresholds** - Set your own warning levels for each metric
- **Warnings-Only Mode** - Focus on problematic functions that need attention

## Quick Start

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Installation

**Option 1: Install with uv (Recommended)**
```bash
# Clone the repository
git clone https://github.com/peekdylan/codecomplexity.git
cd codecomplexity

# Install the package
uv pip install -e .

# For C language support (optional)
uv pip install -e ".[c-support]"
```

**Option 2: Install with pip**
```bash
# Clone the repository
git clone https://github.com/peekdylan/codecomplexity.git
cd codecomplexity

# Install the package
pip install -e .

# For C language support (optional)
pip install -e ".[c-support]"
```

### Try It Immediately
```bash
# Analyze a single Python file
uv run codecomplexity analyze yourfile.py

# Scan an entire project
uv run codecomplexity scan /path/to/project

# Analyze a C file
uv run codecomplexity analyze yourfile.c

# Export results to JSON
uv run codecomplexity analyze yourfile.py --output results.json

# See the tool analyze itself!
uv run codecomplexity scan codecomplexity
```

**Expected output:**
```
================================================================================
PROJECT COMPLEXITY ANALYSIS
================================================================================

PROJECT SUMMARY
--------------------------------------------------------------------------------
Total Files Analyzed: 6
Total Functions: 45
Average Complexity: 2.64
Highest Complexity: 16
```

## Usage

### Analyze a Single File

**Python file:**
```bash
uv run codecomplexity analyze path/to/your_file.py
```

**C file:**
```bash
uv run codecomplexity analyze path/to/your_file.c
```

### Scan an Entire Directory

**Scan Python files:**
```bash
uv run codecomplexity scan path/to/project
```

**Include C files:**
```bash
uv run codecomplexity scan path/to/project --include-c
```

**Non-recursive (current directory only):**
```bash
uv run codecomplexity scan path/to/project --no-recursive
```

### Export to JSON

**Single file:**
```bash
uv run codecomplexity analyze your_file.py --output results.json
```

**Entire project:**
```bash
uv run codecomplexity scan path/to/project --output project_metrics.json
```

### Custom Thresholds

Set custom warning thresholds for any command:
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

## Output Examples

### Single File Analysis
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

### Project Scan
```
================================================================================
PROJECT COMPLEXITY ANALYSIS
================================================================================

PROJECT SUMMARY
--------------------------------------------------------------------------------
Total Files Analyzed: 5
Total Functions: 27
Average Complexity: 2.96
Highest Complexity: 16

FILE BREAKDOWN
--------------------------------------------------------------------------------
src/api.py
  Functions: 9 | Avg Complexity: 5.00 | Max: 16 | ⚠️  3 warnings

src/utils.py
  Functions: 7 | Avg Complexity: 2.43 | Max: 5 | ✓ OK

src/models.py
  Functions: 11 | Avg Complexity: 1.64 | Max: 3 | ✓ OK
================================================================================
```

### JSON Output

**Single file export:**
```json
{
  "file": "example.py",
  "timestamp": "2026-02-01T16:28:00.327264",
  "summary": {
    "total_functions": 11,
    "average_complexity": 1.64,
    "highest_complexity": 3
  },
  "functions": [
    {
      "name": "process_data",
      "line_number": 45,
      "cyclomatic_complexity": 8,
      "lines_of_code": 42,
      "max_nesting_depth": 3
    }
  ]
}
```

**Project scan export:**
```json
{
  "timestamp": "2026-02-01T16:30:00.123456",
  "summary": {
    "total_files": 5,
    "total_functions": 27,
    "average_complexity": 2.96,
    "highest_complexity": 16
  },
  "files": [
    {
      "file": "src/api.py",
      "summary": {
        "total_functions": 9,
        "average_complexity": 5.0,
        "highest_complexity": 16
      },
      "functions": [...]
    }
  ]
}
```

## Understanding the Metrics

### Cyclomatic Complexity
Measures the number of independent paths through code. Higher values indicate more complex logic that's harder to test and maintain.

**How it's calculated:**
- Start at 1 (base complexity)
- +1 for each `if`, `elif`, `else`
- +1 for each `for`, `while` loop
- +1 for each `and`, `or` in conditions
- +1 for each `except` handler
- +1 for each `case` in switch statements (C)

**Guidelines:**
- **1-10**: Simple, easy to test and maintain
- **11-20**: Moderate complexity, consider refactoring
- **21+**: High complexity, **should** be refactored

### Lines of Code (LOC)
Counts actual code lines, excluding:
- Blank lines
- Comment-only lines
- Whitespace

**Guidelines:**
- **< 50**: Good, focused function
- **50-100**: Acceptable, but monitor
- **100+**: Consider breaking into smaller functions

### Nesting Depth
Measures how deeply control structures are nested (if/for/while/try blocks).

**Guidelines:**
- **1-3**: Good readability
- **4-5**: Acceptable, but harder to follow
- **6+**: Poor readability, refactor recommended

## Development

### Project Structure
```
codecomplexity-project/
├── codecomplexity/          # Source code
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py          # Python analysis logic
│   ├── c_analyzer.py        # C analysis logic
│   ├── scanner.py           # Directory scanning
│   └── cli.py               # Command-line interface
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
├── README.md
└── .gitignore
```

### Running Tests

Analyze the tool itself:
```bash
# Analyze individual modules
uv run codecomplexity analyze codecomplexity/analyzer.py
uv run codecomplexity analyze codecomplexity/cli.py

# Scan the entire project
uv run codecomplexity scan codecomplexity

# Export analysis
uv run codecomplexity scan codecomplexity --output self-analysis.json
```

### Adding New Features

The codebase is organized for extensibility:
- **New language support**: Create a new analyzer module (e.g., `java_analyzer.py`)
- **New metrics**: Extend the `FunctionMetrics` class in `analyzer.py`
- **New output formats**: Add export functions in `cli.py`

## Technology Stack

- **Python 3.10+** - Core language
- **AST (Abstract Syntax Tree)** - Python code parsing
- **pycparser** - C code parsing (optional)
- **argparse** - Command-line interface
- **colorama** - Cross-platform colored output

## Use Cases

### Local Development
Identify complex functions while coding:
```bash
uv run codecomplexity analyze src/mymodule.py --warnings-only
```

### Code Review
Check complexity before committing:
```bash
uv run codecomplexity scan src/ --complexity-threshold 15
```

### CI/CD Integration
Export metrics for automated quality gates:
```bash
uv run codecomplexity scan . --output metrics.json
# Parse metrics.json in your CI pipeline
```

### Refactoring Guidance
Find the most complex parts of a codebase:
```bash
uv run codecomplexity scan . --output analysis.json
# Sort by complexity to prioritize refactoring efforts
```

### Multi-Language Projects
Analyze mixed Python/C codebases:
```bash
uv run codecomplexity scan . --include-c --output full_analysis.json
```

## Command Reference
```bash
# Show help
uv run codecomplexity --help
uv run codecomplexity analyze --help
uv run codecomplexity scan --help

# Analyze commands
codecomplexity analyze <file>              # Analyze single file
  --complexity-threshold N                 # Set complexity warning level (default: 10)
  --loc-threshold N                        # Set LOC warning level (default: 50)
  --nesting-threshold N                    # Set nesting warning level (default: 4)
  --warnings-only                          # Show only problematic functions
  --output FILE, -o FILE                   # Export to JSON

# Scan commands
codecomplexity scan <directory>            # Scan directory
  --no-recursive                           # Don't scan subdirectories
  --include-c                              # Also analyze C files
  --complexity-threshold N                 # Set complexity warning level
  --loc-threshold N                        # Set LOC warning level
  --nesting-threshold N                    # Set nesting warning level
  --output FILE, -o FILE                   # Export to JSON
```

## Limitations

### C Language Support
- Requires preprocessed C code (no `#include`, `#define` directives)
- For full C projects, preprocess files first with `gcc -E`
- Header files (`.h`) are analyzed but may have parsing limitations

### Python Language Support
- Analyzes Python 3.x syntax
- Some complex decorators may affect LOC calculations
- Dynamic code (eval, exec) complexity cannot be determined statically

## Contributing

This is a personal portfolio project, but suggestions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Fork and experiment
- Share feedback

## Author

**Dylan** - [Boot.dev](https://boot.dev) Student

Built as an independent project to demonstrate:
- Software architecture and design
- Algorithm implementation (AST traversal, complexity analysis)
- CLI tool development
- Multi-language parsing
- Professional documentation practices

View my other projects and code quality analysis: [CODE_QUALITY.md](CODE_QUALITY.md)

## License

MIT License - Free to use for learning and portfolio purposes.

## Acknowledgments

- Built as part of the [Boot.dev](https://boot.dev) Computer Science curriculum
- Inspired by industry tools like `pylint`, `radon`, and `lizard`
- Uses the excellent [pycparser](https://github.com/eliben/pycparser) library for C analysis

## Version History

- **v0.2.0** (2026-02-01)
  - Added C language support
  - Added directory scanning
  - Added JSON export
  - Added project-wide metrics
  
- **v0.1.0** (2026-01-31)
  - Initial release
  - Python complexity analysis
  - Colorized terminal output
  - Customizable thresholds

---

**Ready to improve your code quality?** Clone and start analyzing today!
```bash
git clone https://github.com/peekdylan/codecomplexity.git
cd codecomplexity
uv pip install -e .
uv run codecomplexity scan your-project/
```