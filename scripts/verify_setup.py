#!/usr/bin/env python3
"""
Verification script to check that all development setup is complete.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def check_makefile_targets() -> bool:
    """Check if Makefile has required targets."""
    makefile_path = Path("Makefile")
    if not makefile_path.exists():
        print("❌ Makefile not found")
        return False
    
    content = makefile_path.read_text()
    required_targets = [
        "dev:", "start:", "install:", "install-dev:", "setup:",
        "lint:", "format:", "clean:", "test:", "pre-commit:"
    ]
    
    missing_targets = []
    for target in required_targets:
        if target not in content:
            missing_targets.append(target)
    
    if missing_targets:
        print(f"❌ Missing Makefile targets: {', '.join(missing_targets)}")
        return False
    else:
        print("✓ All required Makefile targets present")
        return True


def main():
    """Verify the development setup."""
    print("Verifying development setup...\n")
    
    checks = [
        # Configuration files
        ("pyproject.toml", "Tool configuration"),
        ("requirements-dev.txt", "Development dependencies"),
        (".pre-commit-config.yaml", "Pre-commit configuration"),
        ("requirements.in", "Production requirements template"),
        ("requirements-dev.in", "Development requirements template"),
        
        # Documentation
        ("DEVELOPMENT.md", "Development guide"),
        
        # Scripts
        ("scripts/test_dev_tools.py", "Development tools test script"),
    ]
    
    results = []
    
    # Check files
    for filepath, description in checks:
        results.append(check_file_exists(filepath, description))
    
    # Check Makefile targets
    results.append(check_makefile_targets())
    
    print(f"\nResults: {sum(results)}/{len(results)} checks passed")
    
    if all(results):
        print("\n✓ Development setup is complete!")
        print("\nNext steps:")
        print("1. Run 'make install-dev' to install development tools")
        print("2. Run 'make setup' to complete environment setup")
        print("3. Run 'make dev' to start development server")
        return 0
    else:
        print("\n❌ Development setup is incomplete")
        return 1


if __name__ == "__main__":
    sys.exit(main())