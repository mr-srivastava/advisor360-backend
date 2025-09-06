#!/usr/bin/env python3
"""
Demo script showing the complete development workflow.
"""

import subprocess
import sys


def run_make_command(command: str, description: str) -> bool:
    """Run a make command and show the result."""
    print(f"\n{'='*60}")
    print(f"Running: make {command}")
    print(f"Description: {description}")
    print('='*60)
    
    try:
        result = subprocess.run(
            ["make", command],
            capture_output=False,  # Show output in real-time
            text=True,
            check=True
        )
        print(f"✓ 'make {command}' completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 'make {command}' failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ make command not found")
        return False


def main():
    """Demonstrate the development workflow."""
    print("Development Workflow Demo")
    print("This script demonstrates the available make commands")
    print("(Note: Some commands may fail if dependencies are not installed)")
    
    # Commands that should work without dependencies
    safe_commands = [
        ("help", "Show available commands"),
        ("clean", "Clean up cache files"),
    ]
    
    # Commands that require development dependencies
    dev_commands = [
        ("format", "Format code with black and isort"),
        ("lint", "Run linting with ruff and mypy"),
        ("test", "Run tests with pytest"),
    ]
    
    print("\n" + "="*60)
    print("SAFE COMMANDS (should work without dependencies)")
    print("="*60)
    
    for command, description in safe_commands:
        run_make_command(command, description)
    
    print("\n" + "="*60)
    print("DEVELOPMENT COMMANDS (require 'make install-dev' first)")
    print("="*60)
    
    for command, description in dev_commands:
        print(f"\nCommand: make {command}")
        print(f"Description: {description}")
        print("Status: Requires development dependencies")
    
    print("\n" + "="*60)
    print("SETUP INSTRUCTIONS")
    print("="*60)
    print("To use all development commands:")
    print("1. make install-dev    # Install development tools")
    print("2. make setup          # Complete environment setup")
    print("3. make dev            # Start development server")
    print("4. make check          # Run all quality checks")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())