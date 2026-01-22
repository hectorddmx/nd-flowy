# Development commands for workflowy-flow

# Default recipe - show available commands
default:
    @just --list

# Install dependencies
install:
    uv sync --all-extras

# Run the development server
run:
    uv run uvicorn app.main:app --reload --port 8000

# Run tests
test:
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    uv run pytest tests/ -v --cov=app --cov-report=html

# Run linting
lint:
    uv run ruff check app/

# Fix linting issues
lint-fix:
    uv run ruff check app/ --fix

# Format code
format:
    uv run ruff format app/

# Check all (lint + test)
check: lint test
