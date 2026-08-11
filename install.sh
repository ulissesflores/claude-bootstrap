#!/usr/bin/env bash
#
# install.sh — install claude-bootstrap CLI.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh | bash
#
# Or:
#   curl -sSL https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh | bash -s -- --version 1.0.0
#
# What it does:
#   1. Verify Python 3.11+ is installed.
#   2. Prefer `pipx install` (isolated venv); fall back to `pip install --user`.
#   3. Verify `claude-bootstrap version` prints expected version.
#   4. Print PATH hint if the install dir isn't on PATH.

set -euo pipefail

VERSION_REQ=""
PACKAGE="claude-bootstrap"
PYPI_INDEX_URL="${PIP_INDEX_URL:-https://pypi.org/simple/}"

# Parse flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        --version) VERSION_REQ="$2"; shift 2 ;;
        --version=*) VERSION_REQ="${1#*=}"; shift ;;
        --help|-h)
            cat <<USAGE
install.sh — install claude-bootstrap CLI

Usage:
  curl -sSL <url>/install.sh | bash
  curl -sSL <url>/install.sh | bash -s -- --version 1.0.0

Options:
  --version <ver>   pin to specific PyPI version (default: latest)
  --help            show this message

After install, verify with: claude-bootstrap version
USAGE
            exit 0
            ;;
        *) echo "WARN: unknown flag: $1" >&2; shift ;;
    esac
done

# 1. Find Python 3.11+
find_python() {
    for py in python3.13 python3.12 python3.11 python3; do
        if command -v "$py" >/dev/null 2>&1; then
            ver=$("$py" -c "import sys; print(sys.version_info[:2])" 2>/dev/null || echo "(0,0)")
            if "$py" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
                echo "$py"
                return 0
            fi
        fi
    done
    return 1
}

PY=$(find_python) || {
    echo "ERROR: claude-bootstrap requires Python 3.11+. Install from https://python.org/" >&2
    exit 2
}

echo "→ Using $PY ($("$PY" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'))"

# 2. Build install spec
SPEC="$PACKAGE"
[[ -n "$VERSION_REQ" ]] && SPEC="$PACKAGE==$VERSION_REQ"

# 3. Try pipx first (isolated install — recommended for CLI tools)
if command -v pipx >/dev/null 2>&1; then
    echo "→ Installing $SPEC via pipx (isolated venv)..."
    if pipx install --force "$SPEC"; then
        INSTALL_METHOD="pipx"
        BIN_DIR=$(pipx environment --value PIPX_BIN_DIR 2>/dev/null || echo "$HOME/.local/bin")
    else
        echo "WARN: pipx install failed, falling back to private venv" >&2
        INSTALL_METHOD=""
    fi
fi

# 4. Fall back to private venv at ~/.local/share/claude-bootstrap (works under PEP 668)
if [[ -z "${INSTALL_METHOD:-}" ]]; then
    VENV_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/claude-bootstrap"
    BIN_DIR="$HOME/.local/bin"
    echo "→ Installing $SPEC into private venv at $VENV_DIR..."
    "$PY" -m venv "$VENV_DIR" --upgrade-deps >/dev/null 2>&1 || "$PY" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip >/dev/null 2>&1
    "$VENV_DIR/bin/pip" install --upgrade "$SPEC"
    mkdir -p "$BIN_DIR"
    ln -sf "$VENV_DIR/bin/claude-bootstrap" "$BIN_DIR/claude-bootstrap"
    INSTALL_METHOD="venv at $VENV_DIR"
fi

# 5. Verify CLI works
if "$BIN_DIR/claude-bootstrap" version >/dev/null 2>&1; then
    INSTALLED_VER=$("$BIN_DIR/claude-bootstrap" version)
elif command -v claude-bootstrap >/dev/null 2>&1; then
    INSTALLED_VER=$(claude-bootstrap version)
else
    echo
    echo "WARN: claude-bootstrap installed but not on PATH yet." >&2
    echo "      Add to your shell rc: export PATH=\"$BIN_DIR:\$PATH\"" >&2
    echo "      Or run directly: $BIN_DIR/claude-bootstrap" >&2
    exit 0
fi

echo
echo "✓ Installed: $INSTALLED_VER (via $INSTALL_METHOD)"
echo "  Bin dir: $BIN_DIR"
echo
echo "Next steps:"
echo "  claude-bootstrap init --profile=universal-software"
echo "  claude-bootstrap help"
