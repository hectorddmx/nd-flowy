# just - Command Runner

[just](https://just.systems/) is a command runner for project-specific tasks. It's like `make` but simpler and more portable.

## Installation

```bash
# Via mise (recommended - already configured)
mise install

# Or via Homebrew
brew install just

# Or via cargo
cargo install just
```

## Quick Start

```bash
# List all available commands
just

# Run a specific command
just run

# Full project setup
just bootstrap
```

## Available Commands

Run `just` to see all commands grouped by category:

### Setup
| Command | Description |
|---------|-------------|
| `just setup` | Install mise tools |
| `just install` | Install Python dependencies |
| `just bootstrap` | Full setup (mise + deps) |

### Development
| Command | Description |
|---------|-------------|
| `just run` | Start dev server (localhost) |
| `just run-host` | Start dev server (all interfaces) |

### Testing & Quality
| Command | Description |
|---------|-------------|
| `just test` | Run tests |
| `just test-cov` | Run tests with coverage |
| `just lint` | Run linter |
| `just lint-fix` | Auto-fix lint issues |
| `just format` | Format code |
| `just check` | Run lint + test |

### Docker
| Command | Description |
|---------|-------------|
| `just docker-build` | Build Docker image |
| `just docker-up` | Run with Docker Compose |
| `just docker-up-d` | Run in background |
| `just docker-down` | Stop containers |
| `just docker-logs` | View logs |

### Dev Containers
| Command | Description |
|---------|-------------|
| `just devcontainer-build` | Build dev container |
| `just devcontainer-up` | Start dev container |
| `just devcontainer-exec <cmd>` | Run command in container |

### Environment
| Command | Description |
|---------|-------------|
| `just env-generate` | Generate .env file |
| `just env-show` | Show environment vars |
| `just env-check` | Verify environment |

### Utilities
| Command | Description |
|---------|-------------|
| `just db-reset` | Delete local database |
| `just clean` | Clean generated files |
| `just clean-all` | Clean everything |

## Common Workflows

### First-time Setup

```bash
# 1. Set up your API key
echo 'WF_API_KEY = "your_key"' >> mise.local.toml

# 2. Bootstrap the project
just bootstrap

# 3. Run the app
just run
```

### Daily Development

```bash
# Start the server
just run

# In another terminal, run tests on changes
just test

# Before committing
just check
```

### Docker Development

```bash
# Build and run
just docker-build
just docker-up

# Or in background
just docker-up-d
just docker-logs
```

## References

- [just Manual](https://just.systems/man/en/)
- [just GitHub](https://github.com/casey/just)
- [Justfile Patterns](patterns.md)
