# Justfile Patterns

This document describes the patterns and conventions used in justfiles across our projects.

## File Structure

### Header Comments

Start with a description and usage hint:

```just
# Development commands for my-project
# Run `just` or `just --list` to see available commands
```

### Shell Configuration

Set shell options at the top:

```just
# Load .env files automatically
set dotenv-load

# Use bash with useful flags
set shell := ["bash", "-cu"]
```

Flags explained:
- `-c`: Read commands from string
- `-u`: Treat unset variables as errors
- `-x`: Print commands before execution (optional, for debugging)

### Section Headers

Use visual separators for sections:

```just
### ================================ ###
### Section Name
### ================================ ###
```

Or for larger projects:

```just
# =============================================================================
# Section Name
# =============================================================================
```

### Default Recipe

Always include a default recipe that lists commands:

```just
# List all recipes
default:
    @just --list
```

## Recipe Patterns

### Basic Recipe

```just
# Description of what this does
[group('category')]
recipe-name:
    command here
```

### Recipe with Parameters

```just
# Generate report for year and week
[group('dev')]
report year week:
    python generate.py {{year}} {{week}}
```

### Recipe with Default Parameters

```just
# Run tests (default: all)
[group('test')]
test target="all":
    pytest tests/{{target}}
```

### Recipe with Variable Arguments

```just
# Pass any arguments to the underlying command
[group('docker')]
docker-exec *args:
    docker exec -it mycontainer {{args}}
```

### Multi-line Recipes (Shell Scripts)

```just
# Complex setup that needs multiple commands
[group('setup')]
setup:
    #!/usr/bin/env bash
    set -euxo pipefail
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install mise
    mise install
```

### Dependent Recipes

```just
# Run all quality checks
[group('test')]
check: lint test
    @echo "All checks passed!"
```

## Grouping

Use `[group('name')]` to organize recipes:

```just
[group('setup')]
setup:
    mise install

[group('setup')]
install:
    uv sync

[group('dev')]
run:
    uvicorn app:app

[group('test')]
test:
    pytest
```

Common groups:
- `setup` - Installation and configuration
- `dev` - Development tasks
- `test` - Testing and linting
- `docker` - Docker operations
- `devcontainer` - Dev container operations
- `env` - Environment management
- `db` - Database operations
- `utils` - Utility commands

## Naming Conventions

### Recipe Names

- Use lowercase with hyphens: `docker-build`, `test-cov`
- Group related commands with prefixes: `docker-*`, `env-*`
- Be descriptive but concise

### Common Recipe Names

| Name | Purpose |
|------|---------|
| `setup` | Install tools |
| `install` | Install dependencies |
| `bootstrap` | Full project setup |
| `run` | Start development server |
| `test` | Run tests |
| `lint` | Run linter |
| `format` | Format code |
| `check` | Run all quality checks |
| `clean` | Remove generated files |
| `build` | Build for production |

## Environment Variables

### Checking Variables

```just
[group('env')]
env-check:
    @echo "API_KEY: ${API_KEY:+SET}"
    @echo "DEBUG: ${DEBUG:-false}"
```

- `${VAR:+SET}` - Prints "SET" if variable is set
- `${VAR:-default}` - Uses default if variable is unset

### Using mise

```just
# Run with mise environment
[group('dev')]
run:
    mise exec -- python app.py
```

## Output Control

### Silent Commands

Prefix with `@` to hide the command:

```just
clean:
    @rm -rf .cache
    @echo "Cleaned!"
```

### Verbose Commands

Use `set shell := ["bash", "-cux"]` to show commands.

### Progress Messages

```just
build:
    @echo "Building..."
    cargo build --release
    @echo "Done!"
```

## Error Handling

### Continue on Error

Use `|| true` to continue even if command fails:

```just
clean:
    rm -rf .cache || true
    rm -rf .venv || true
```

### Stop on Error (Default)

Recipes stop on first error by default. For explicit control:

```just
strict-recipe:
    #!/usr/bin/env bash
    set -euo pipefail
    command1
    command2
```

## Cross-Platform Considerations

### Path Separators

Use forward slashes (work on all platforms):

```just
build:
    python scripts/build.py
```

### Shell Commands

For maximum compatibility, use simple commands or check for tools:

```just
setup:
    #!/usr/bin/env bash
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y package
    elif command -v brew &> /dev/null; then
        brew install package
    fi
```

## Integration with mise

### Running Commands

```just
# Direct (if mise shell integration is active)
run:
    python app.py

# Explicit (always works)
run:
    mise exec -- python app.py
```

### Installing Tools

```just
setup:
    mise install
    mise exec -- uv sync
```

## Examples from Our Projects

### Python Project

```just
[group('test')]
test:
    uv run pytest tests/ -v

[group('test')]
lint:
    uv run ruff check app/ tests/

[group('test')]
format:
    uv run ruff format app/ tests/
```

### Docker Project

```just
[group('docker')]
docker-build:
    docker compose build

[group('docker')]
docker-up:
    docker compose up

[group('docker')]
docker-down:
    docker compose down
```

### Multi-Language Project

```just
# =============================================================================
# Python
# =============================================================================

[group('python')]
py-lint:
    uv run ruff check scripts/

[group('python')]
py-test:
    uv run pytest

# =============================================================================
# JavaScript
# =============================================================================

[group('js')]
js-lint:
    npm run lint

[group('js')]
js-test:
    npm run test
```

## References

- [just Manual](https://just.systems/man/en/)
- [just Cheatsheet](https://cheatography.com/linux-china/cheat-sheets/justfile/)
