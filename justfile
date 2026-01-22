# Development commands for workflowy-flow
# Run `just` or `just --list` to see available commands

# Set shell options
set dotenv-load
set shell := ["bash", "-cu"]

### ================================ ###
### Default
### ================================ ###

# List all recipes
default:
    @just --list

### ================================ ###
### Setup
### ================================ ###

# Install all mise tools (python, node, uv, ruff, devcontainer CLI, etc.)
[group('setup')]
setup:
    mise install

# Install Python dependencies
[group('setup')]
install:
    uv sync --all-extras

# Full setup: mise tools + Python dependencies
[group('setup')]
bootstrap: setup install
    @echo "Setup complete. Run 'just run' to start the dev server."

### ================================ ###
### Development Server
### ================================ ###

# Run the development server with live reload (watches py, html, css, js files)
[group('dev')]
run:
    DEBUG=true uv run uvicorn app.main:app --reload --port 8000 \
        --reload-include '*.html' \
        --reload-include '*.css' \
        --reload-include '*.js'

# Run development server (basic, Python files only)
[group('dev')]
run-basic:
    uv run uvicorn app.main:app --reload --port 8000

# Run the development server on all interfaces (for containers)
[group('dev')]
run-host:
    DEBUG=true uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 \
        --reload-include '*.html' \
        --reload-include '*.css' \
        --reload-include '*.js'

### ================================ ###
### Testing & Quality
### ================================ ###

# Run tests
[group('test')]
test:
    uv run pytest tests/ -v

# Run tests with coverage
[group('test')]
test-cov:
    uv run pytest tests/ -v --cov=app --cov-report=html

# Run linting
[group('test')]
lint:
    uv run ruff check app/ tests/

# Fix linting issues
[group('test')]
lint-fix:
    uv run ruff check app/ tests/ --fix

# Format code
[group('test')]
format:
    uv run ruff format app/ tests/

# Check all (lint + test)
[group('test')]
check: lint test

### ================================ ###
### Docker
### ================================ ###

# Build Docker image
[group('docker')]
docker-build:
    docker compose build

# Run with Docker Compose
[group('docker')]
docker-up:
    docker compose up

# Run with Docker Compose in background
[group('docker')]
docker-up-d:
    docker compose up -d

# Stop Docker containers
[group('docker')]
docker-down:
    docker compose down

# View Docker logs
[group('docker')]
docker-logs:
    docker compose logs -f

# Deploy locally (build and start with latest changes)
[group('docker')]
deploy:
    docker compose up --build -d --wait
    @echo "Deployed at http://localhost:8000"

# Rebuild and restart containers
[group('docker')]
docker-restart: docker-down docker-build docker-up-d
    @echo "Containers restarted"

### ================================ ###
### Dev Containers
### ================================ ###

# Build dev container
[group('devcontainer')]
devcontainer-build:
    devcontainer build --workspace-folder .

# Start dev container
[group('devcontainer')]
devcontainer-up:
    devcontainer up --workspace-folder .

# Execute command in dev container
[group('devcontainer')]
devcontainer-exec *args:
    devcontainer exec --workspace-folder . {{args}}

### ================================ ###
### Environment
### ================================ ###

# Generate .env file from mise config
[group('env')]
env-generate:
    mise env --dotenv > .env.development
    @echo "Generated .env.development"

# Show current environment variables
[group('env')]
env-show:
    mise env

# Check environment is set up correctly
[group('env')]
env-check:
    @echo "Checking environment..."
    @echo "Python: $(python --version)"
    @echo "UV: $(uv --version)"
    @echo "Ruff: $(ruff --version)"
    @echo "WF_API_KEY: ${WF_API_KEY:+SET}"

### ================================ ###
### Database
### ================================ ###

# Delete the local database
[group('db')]
db-reset:
    rm -f workflowy_flow.db
    @echo "Database deleted. It will be recreated on next run."

### ================================ ###
### Cleanup
### ================================ ###

# Clean all generated files
[group('utils')]
clean:
    rm -rf .pytest_cache .ruff_cache .coverage htmlcov
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    @echo "Cleaned generated files"

# Clean everything including venv and db
[group('utils')]
clean-all: clean
    rm -rf .venv workflowy_flow.db
    @echo "Cleaned all including .venv and database"
