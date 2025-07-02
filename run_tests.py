#!/usr/bin/env python3
"""Test runner script for the timeline-reporter project."""

import argparse
import subprocess
import sys


def run_tests(
    test_type: str = "all", coverage: bool = True, verbose: bool = False
) -> subprocess.CompletedProcess[bytes]:
    """Run tests with specified options."""
    cmd = [sys.executable, "-m", "pytest"]

    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "clients":
        cmd.extend(["tests/clients/"])
    elif test_type == "services":
        cmd.extend(["tests/services/"])

    if coverage:
        if test_type == "clients":
            cmd.extend(
                [
                    "--override-ini",
                    "addopts=--verbose --tb=short --strict-markers --disable-warnings",
                    "--cov=clients",
                    "--cov-report=term-missing",
                    "--cov-fail-under=85",
                ]
            )
        elif test_type == "services":
            cmd.extend(
                [
                    "--override-ini",
                    "addopts=--verbose --tb=short --strict-markers --disable-warnings",
                    "--cov=services",
                    "--cov-report=term-missing",
                    "--cov-fail-under=85",
                ]
            )
        # For "all", "unit", "integration" use default pytest.ini settings
    else:
        cmd.append("--no-cov")

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests for timeline-reporter")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "clients", "services"],
        default="all",
        help="Type of tests to run (default: all)",
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Disable coverage reporting"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    result = run_tests(
        test_type=args.type, coverage=not args.no_coverage, verbose=args.verbose
    )

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
