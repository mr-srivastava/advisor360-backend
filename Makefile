# Makefile for Advisor360 Backend Development

.PHONY: help dev start install install-dev lint format clean test test-logging deps-update setup pre-commit check fix health metrics

# Default target
help:
	@echo "Available commands:"
	@echo "  dev          - Start development server with auto-reload"
	@echo "  start        - Start production server"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  setup        - Complete development environment setup"
	@echo "  lint         - Run code linting with ruff and mypy"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean up cache files"
	@echo "  test         - Run tests with pytest"
	@echo "  test-logging - Test logging infrastructure"
	@echo "  deps-update  - Update dependencies"
	@echo "  pre-commit   - Install and run pre-commit hooks"

# Development server with auto-reload
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
start:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Install production dependencies
install:
	python3 -m pip install -r requirements.txt

# Install development dependencies
install-dev:
	python3 -m pip install -r requirements.txt
	python3 -m pip install -r requirements-dev.txt

# Complete development environment setup
setup: install-dev
	@echo "Setting up development environment..."
	pre-commit install
	@echo "✓ Development environment setup complete!"
	@echo "Run 'make dev' to start the development server"

# Code linting
lint:
	@echo "Running code linting..."
	@if command -v ruff >/dev/null 2>&1; then \
		echo "Running ruff checks..."; \
		ruff check app/; \
	else \
		echo "❌ ruff not found. Run 'make install-dev' to install development tools"; \
		exit 1; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		echo "Running mypy type checks..."; \
		mypy app/; \
	else \
		echo "❌ mypy not found. Run 'make install-dev' to install development tools"; \
		exit 1; \
	fi
	@echo "✓ Linting completed successfully!"

# Code formatting
format:
	@echo "Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		echo "Running black formatter..."; \
		black app/; \
	else \
		echo "❌ black not found. Run 'make install-dev' to install development tools"; \
		exit 1; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		echo "Running isort import sorting..."; \
		isort app/; \
	else \
		echo "❌ isort not found. Run 'make install-dev' to install development tools"; \
		exit 1; \
	fi
	@echo "✓ Code formatting completed successfully!"

# Clean up cache files
clean:
	@echo "Cleaning up cache files..."
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name "*.cover" -delete
	find . -name "coverage.xml" -delete
	find . -name "*.log" -delete

# Run tests
test:
	@echo "Running tests..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v --cov=app --cov-report=term-missing; \
	else \
		echo "❌ pytest not found. Run 'make install-dev' to install development tools"; \
		exit 1; \
	fi

# Test logging infrastructure
test-logging:
	@echo "Testing logging infrastructure..."
	python3 test_logging.py

# Update dependencies
deps-update:
	@echo "Updating dependencies..."
	@if [ -f "requirements.in" ]; then \
		python3 -m piptools compile requirements.in; \
	fi
	@if [ -f "requirements-dev.in" ]; then \
		python3 -m piptools compile requirements-dev.in; \
	fi

# Check application health
health:
	@echo "Checking application health..."
	@if curl -s http://localhost:8000/health > /dev/null; then \
		echo "✓ Application is healthy"; \
		curl -s http://localhost:8000/health | python3 -m json.tool; \
	else \
		echo "❌ Application is not responding"; \
	fi

# View application metrics
metrics:
	@echo "Fetching application metrics..."
	@if curl -s http://localhost:8000/metrics > /dev/null; then \
		curl -s http://localhost:8000/metrics | python3 -m json.tool; \
	else \
		echo "❌ Cannot fetch metrics - application may not be running"; \
	fi

# Pre-commit hooks
pre-commit:
	@echo "Installing and running pre-commit hooks..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
		pre-commit run --all-files; \
	else \
		echo "❌ pre-commit not found. Run 'make install-dev' to install development tools"; \
		exit 1; \
	fi

# Check code quality (format + lint + test)
check: format lint test
	@echo "✓ All code quality checks passed!"

# Fix common issues automatically
fix:
	@echo "Fixing common code issues..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check app/ --fix; \
	fi
	@if command -v black >/dev/null 2>&1; then \
		black app/; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort app/; \
	fi
	@echo "✓ Automatic fixes applied!"