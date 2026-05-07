"""Executable entry point.

Run with:
    python main.py [path/to/file.pdf]
"""
import sys
import os

# Ensure the project root is on sys.path so that 'src' resolves as a package.
sys.path.insert(0, os.path.dirname(__file__))

from src.app import run

if __name__ == "__main__":
    sys.exit(run())
