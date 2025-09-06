# Development Guide

This document provides information about the development environment setup and available tools.

## Quick Start

1. **Set up the development environment:**

   ```bash
   make setup
   ```

2. **Start the development server:**
   ```bash
   make dev
   ```

## Available Commands

### Development Server

- `make dev` - Start development server with auto-reload
- `make start` - Start production server

### Dependencies

- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make setup` - Complete development environment setup (recommended for new developers)

### Code Quality

- `make format` - Format code with Black and isort
- `make lint` - Run linting with Ruff and type checking with MyPy
- `make check` - Run format + lint + test (comprehensive quality check)
- `make fix` - Automatically fix common code issues

### Testing

- `make test` - Run tests with pytest and coverage
- `make test-logging` - Test logging infrastructure specifically

### Maintenance

- `make clean` - Clean up cache files and temporary files
- `make deps-update` - Update dependencies (requires pip-tools)
- `make pre-commit` - Install and run pre-commit hooks

### Application Health

- `make health` - Check if the application is running and healthy
- `make metrics` - View application metrics (requires running server)

## Development Tools

### Code Formatting

- **Black**: Python code formatter with opinionated style
- **isort**: Import statement organizer

### Code Quality

- **Ruff**: Fast Python linter (replaces flake8, pylint, etc.)
- **MyPy**: Static type checker

### Testing

- **pytest**: Testing framework with coverage reporting
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Coverage reporting

### Pre-commit Hooks

Pre-commit hooks are automatically installed with `make setup` and will run:

- Trailing whitespace removal
- End-of-file fixing
- YAML validation
- Black formatting
- isort import sorting
- Ruff linting
- MyPy type checking

## Configuration Files

### pyproject.toml

Contains configuration for all development tools:

- Black formatter settings
- isort import sorting rules
- Ruff linting rules and exclusions
- MyPy type checking configuration
- pytest test configuration

### .pre-commit-config.yaml

Defines pre-commit hooks that run automatically before each commit.

### requirements-dev.txt

Development dependencies separate from production requirements.

## Code Style Guidelines

### Python Code Style

- Line length: 88 characters (Black default)
- Import organization: stdlib, third-party, first-party, local
- Type hints: Required for all public functions and methods
- Docstrings: Google style for public APIs

### Import Organization

```python
# Standard library imports
import os
from typing import Optional

# Third-party imports
from fastapi import FastAPI
from pydantic import BaseModel

# First-party imports
from app.core.config import settings
from app.services.commission_service import CommissionService

# Local imports
from .models import Commission
```

## Troubleshooting

### Development Tools Not Found

If you see errors about missing tools (black, ruff, mypy, etc.):

```bash
make install-dev
```

### Pre-commit Issues

If pre-commit hooks fail:

```bash
make pre-commit
```

### Test Development Tools

To verify all development tools are working:

```bash
python scripts/test_dev_tools.py
```

## IDE Integration

### VS Code

Recommended extensions:

- Python
- Black Formatter
- isort
- Ruff
- MyPy Type Checker

### PyCharm

Configure external tools for Black, isort, and Ruff using the Makefile commands.

## Continuous Integration

The development tools are configured to work with CI/CD pipelines:

- All configurations are in `pyproject.toml`
- Commands are standardized through Makefile
- Pre-commit hooks ensure consistent code quality
