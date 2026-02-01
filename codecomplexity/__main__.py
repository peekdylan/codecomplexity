"""
Entry point for running codecomplexity as a module.

This allows users to run: python -m codecomplexity

Author: Dylan
Created: January 31, 2026
"""

from .cli import main
import sys

if __name__ == '__main__':
    sys.exit(main())