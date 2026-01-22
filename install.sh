#!/bin/bash
# Workflowy Flow Installer
# Usage: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/USER/REPO/main/install.sh)"
#
# This script installs Workflowy Flow and its dependencies.

set -e

# =============================================================================
# Configuration
# =============================================================================

REPO_URL="https://github.com/USER/workflowy-flow.git"  # TODO: Update with actual repo
INSTALL_DIR="${HOME}/workflowy-flow"
WORKFLOWY_API_URL="https://beta.workflowy.com/api-key/"

# =============================================================================
# Terminal Colors & Output
# =============================================================================

if [[ -t 1 ]]; then
  tty_escape() { printf "\033[%sm" "$1"; }
else
  tty_escape() { :; }
fi

tty_mkbold() { tty_escape "1;$1"; }
tty_blue="$(tty_mkbold 34)"
tty_green="$(tty_mkbold 32)"
tty_yellow="$(tty_mkbold 33)"
tty_red="$(tty_mkbold 31)"
tty_bold="$(tty_mkbold 39)"
tty_reset="$(tty_escape 0)"

ohai() {
  printf "${tty_blue}==>${tty_bold} %s${tty_reset}\n" "$*"
}

success() {
  printf "${tty_green}✓${tty_reset} %s\n" "$*"
}

warn() {
  printf "${tty_yellow}Warning${tty_reset}: %s\n" "$*" >&2
}

abort() {
  printf "${tty_red}Error${tty_reset}: %s\n" "$*" >&2
  exit 1
}

# =============================================================================
# OS Detection
# =============================================================================

OS="$(uname)"
ARCH="$(uname -m)"

case "${OS}" in
  Darwin)
    OS_TYPE="macos"
    ;;
  Linux)
    OS_TYPE="linux"
    ;;
  *)
    abort "Unsupported operating system: ${OS}"
    ;;
esac

ohai "Detected ${OS_TYPE} on ${ARCH}"

# =============================================================================
# Prerequisite Checks
# =============================================================================

command_exists() {
  command -v "$1" &> /dev/null
}

check_prerequisites() {
  ohai "Checking prerequisites..."

  # Check for curl or wget
  if ! command_exists curl && ! command_exists wget; then
    abort "curl or wget is required but not installed."
  fi
  success "curl/wget available"

  # Check for git
  if ! command_exists git; then
    abort "git is required but not installed. Please install git first."
  fi
  success "git available"
}

# =============================================================================
# Install mise
# =============================================================================

install_mise() {
  if command_exists mise; then
    success "mise is already installed"
    return
  fi

  ohai "Installing mise..."

  if command_exists curl; then
    curl https://mise.run | sh
  elif command_exists wget; then
    wget -qO- https://mise.run | sh
  fi

  # Add mise to PATH for this session
  export PATH="${HOME}/.local/bin:${PATH}"

  if ! command_exists mise; then
    abort "Failed to install mise. Please install manually: https://mise.jdx.dev/getting-started.html"
  fi

  success "mise installed"
}

# =============================================================================
# Shell Integration
# =============================================================================

setup_shell_integration() {
  ohai "Setting up shell integration..."

  local shell_name
  shell_name="$(basename "${SHELL}")"

  local shell_rc
  case "${shell_name}" in
    bash)
      shell_rc="${HOME}/.bashrc"
      ;;
    zsh)
      shell_rc="${HOME}/.zshrc"
      ;;
    fish)
      shell_rc="${HOME}/.config/fish/config.fish"
      ;;
    *)
      warn "Unknown shell: ${shell_name}. You may need to manually add mise to your shell config."
      return
      ;;
  esac

  # Check if mise is already in shell config
  if [[ -f "${shell_rc}" ]] && grep -q "mise activate" "${shell_rc}"; then
    success "mise shell integration already configured"
    return
  fi

  # Add mise activation
  if [[ "${shell_name}" == "fish" ]]; then
    echo 'mise activate fish | source' >> "${shell_rc}"
  else
    echo 'eval "$(mise activate '"${shell_name}"')"' >> "${shell_rc}"
  fi

  success "Added mise to ${shell_rc}"
}

# =============================================================================
# Clone Repository
# =============================================================================

clone_repository() {
  if [[ -d "${INSTALL_DIR}" ]]; then
    warn "Directory ${INSTALL_DIR} already exists"
    read -p "Overwrite? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      abort "Installation cancelled"
    fi
    rm -rf "${INSTALL_DIR}"
  fi

  ohai "Cloning repository to ${INSTALL_DIR}..."
  git clone "${REPO_URL}" "${INSTALL_DIR}"
  success "Repository cloned"
}

# =============================================================================
# Install Dependencies
# =============================================================================

install_dependencies() {
  ohai "Installing project dependencies..."

  cd "${INSTALL_DIR}"

  # Trust the mise config
  mise trust

  # Install mise tools
  mise install

  # Install Python dependencies
  mise exec -- uv sync --all-extras

  success "Dependencies installed"
}

# =============================================================================
# Setup Instructions
# =============================================================================

print_setup_instructions() {
  echo ""
  echo "${tty_green}════════════════════════════════════════════════════════════════${tty_reset}"
  echo "${tty_bold}Installation Complete!${tty_reset}"
  echo "${tty_green}════════════════════════════════════════════════════════════════${tty_reset}"
  echo ""
  echo "${tty_bold}Next Steps:${tty_reset}"
  echo ""
  echo "1. ${tty_blue}Get a Workflowy API Key:${tty_reset}"
  echo ""
  echo "   a) Create a Workflowy account if you don't have one:"
  echo "      ${tty_yellow}https://workflowy.com/signup/${tty_reset}"
  echo ""
  echo "   b) Get your API key:"
  echo "      ${tty_yellow}${WORKFLOWY_API_URL}${tty_reset}"
  echo ""
  echo "2. ${tty_blue}Configure your API key:${tty_reset}"
  echo ""
  echo "   cd ${INSTALL_DIR}"
  echo "   echo 'WF_API_KEY = \"your_api_key_here\"' > mise.local.toml"
  echo ""
  echo "3. ${tty_blue}Restart your terminal${tty_reset} (or run: source ~/.zshrc)"
  echo ""
  echo "4. ${tty_blue}Start the application:${tty_reset}"
  echo ""
  echo "   cd ${INSTALL_DIR}"
  echo "   just run"
  echo ""
  echo "5. ${tty_blue}Open in your browser:${tty_reset}"
  echo "   ${tty_yellow}http://localhost:8000${tty_reset}"
  echo ""
  echo "${tty_green}════════════════════════════════════════════════════════════════${tty_reset}"
  echo ""
  echo "For more information, see the README or run: ${tty_bold}just${tty_reset}"
  echo ""
}

# =============================================================================
# Quick Setup (Local Install - No Clone)
# =============================================================================

quick_setup() {
  # For when running in an existing checkout
  ohai "Running quick setup in current directory..."

  if [[ ! -f "mise.toml" ]]; then
    abort "mise.toml not found. Are you in the project directory?"
  fi

  # Trust and install
  mise trust
  mise install
  mise exec -- uv sync --all-extras

  success "Setup complete!"

  if [[ ! -f "mise.local.toml" ]]; then
    echo ""
    warn "mise.local.toml not found. You need to configure your API key:"
    echo ""
    echo "   echo 'WF_API_KEY = \"your_api_key_here\"' > mise.local.toml"
    echo ""
    echo "   Get your API key at: ${tty_yellow}${WORKFLOWY_API_URL}${tty_reset}"
    echo ""
  fi
}

# =============================================================================
# Main
# =============================================================================

main() {
  echo ""
  echo "${tty_blue}╔═══════════════════════════════════════════════════════════════╗${tty_reset}"
  echo "${tty_blue}║${tty_reset}           ${tty_bold}Workflowy Flow Installer${tty_reset}                          ${tty_blue}║${tty_reset}"
  echo "${tty_blue}╚═══════════════════════════════════════════════════════════════╝${tty_reset}"
  echo ""

  # Parse arguments
  local quick_mode=false
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --quick|-q)
        quick_mode=true
        shift
        ;;
      --help|-h)
        echo "Usage: install.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --quick, -q    Quick setup in current directory (no clone)"
        echo "  --help, -h     Show this help message"
        exit 0
        ;;
      *)
        abort "Unknown option: $1"
        ;;
    esac
  done

  check_prerequisites
  install_mise
  setup_shell_integration

  if [[ "${quick_mode}" == "true" ]]; then
    quick_setup
  else
    clone_repository
    install_dependencies
    print_setup_instructions
  fi
}

main "$@"
