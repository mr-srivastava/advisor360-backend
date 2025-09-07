#!/usr/bin/env python3
"""
Test script to verify development tools are working correctly.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"Testing {description}...")
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {description} is working")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} not found")
        return False


def main():
    """Test all development tools."""
    print("Testing development tools setup...\n")
    
    tools = [
        ("black --version", "Black formatter"),
        ("isort --version", "isort import sorter"),
        ("ruff --version", "Ruff linter"),
        ("mypy --version", "MyPy type checker"),
        ("pytest --version", "Pytest test runner"),
        ("pre-commit --version", "Pre-commit hooks"),
    ]
    
    results = []
    for command, description in tools:
        results.append(run_command(command, description))
    
    print(f"\nResults: {sum(results)}/{len(results)} tools working correctly")
    
    if all(results):
        print("✓ All development tools are properly installed!")
        return 0
    else:
        print("❌ Some development tools are missing. Run 'make install-dev' to install them.")
        return 1


if __name__ == "__main__":
    sys.exit(main())