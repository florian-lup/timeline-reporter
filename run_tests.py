#!/usr/bin/env python3
"""Test runner script for the timeline-reporter project."""

import sys
import subprocess
import argparse


def run_tests(test_type="all", coverage=True, verbose=False):
    """Run tests with specified options."""
    cmd = [sys.executable, "-m", "pytest"]
    
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "clients":
        cmd.extend(["tests/clients/"])
    
    if coverage:
        cmd.extend(["--cov=clients", "--cov-report=term-missing"])
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests for timeline-reporter")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "clients"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    result = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=args.verbose
    )
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main() 