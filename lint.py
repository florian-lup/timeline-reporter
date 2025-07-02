#!/usr/bin/env python3
"""
Linting and formatting script for the timeline-reporter project.

Usage:
    python lint.py [command]

Commands:
    check     - Run all checks (ruff, mypy) without modifying files
    format    - Format code with black and ruff
    fix       - Auto-fix ruff issues
    all       - Run format, fix, and check
    ruff      - Run only ruff linting
    black     - Run only black formatting
    mypy      - Run only mypy type checking

Examples:
    python lint.py check     # Check code quality
    python lint.py format    # Format all Python files
    python lint.py all       # Format, fix, and check everything
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")
    
    return result.returncode


def run_ruff_check():
    """Run ruff linting."""
    return run_command(["ruff", "check", "."], "Ruff linting")


def run_ruff_fix():
    """Run ruff with auto-fix."""
    return run_command(["ruff", "check", ".", "--fix"], "Ruff auto-fix")


def run_black_check():
    """Run black in check mode."""
    return run_command(["black", ".", "--check", "--diff"], "Black formatting check")


def run_black_format():
    """Run black formatting."""
    return run_command(["black", "."], "Black formatting")


def run_mypy():
    """Run mypy type checking."""
    return run_command(["mypy", "."], "MyPy type checking")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    command = sys.argv[1].lower()
    exit_code = 0
    
    if command == "check":
        exit_code += run_ruff_check()
        exit_code += run_mypy()
        
    elif command == "format":
        exit_code += run_black_format()
        exit_code += run_ruff_fix()
        
    elif command == "fix":
        exit_code += run_ruff_fix()
        
    elif command == "all":
        exit_code += run_black_format()
        exit_code += run_ruff_fix()
        exit_code += run_ruff_check()
        exit_code += run_mypy()
        
    elif command == "ruff":
        exit_code += run_ruff_check()
        
    elif command == "black":
        exit_code += run_black_check()
        
    elif command == "mypy":
        exit_code += run_mypy()
        
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        return 1
    
    print("\n" + "=" * 50)
    if exit_code == 0:
        print("🎉 All checks passed!")
    else:
        print(f"💥 {exit_code} check(s) failed!")
    
    return min(exit_code, 1)  # Return 0 or 1 for shell compatibility


if __name__ == "__main__":
    sys.exit(main()) 