#!/usr/bin/env bash
#
# claude-bootstrap dispatcher (thin wrapper around claude_bootstrap.cli).
# All subcommands and flags handled by the Python CLI.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# Pick a Python runner that has the required deps available.
pick_python_runner() {
    if python3 -c "import jinja2, yaml, rich, questionary" 2>/dev/null; then
        echo "python3"
        return
    fi
    if command -v uv >/dev/null 2>&1; then
        echo "uv run --with jinja2 --with pyyaml --with rich --with questionary --no-project python3"
        return
    fi
    echo "ERROR: required deps (jinja2 pyyaml rich questionary) not installed and 'uv' not found." >&2
    echo "       Install with: pip install jinja2 pyyaml rich questionary" >&2
    echo "       Or install uv: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 3
}

runner="$(pick_python_runner)"

# Ensure the package directory (sibling of bin/) is importable.
export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"

# shellcheck disable=SC2086
exec $runner -m claude_bootstrap.cli "$@"
