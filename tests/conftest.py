"""Shared fixtures and helpers for claude-bootstrap pytest suite."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    return tmp_path


def run_cli(args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Invoke bin/bootstrap.sh with args; returns (returncode, stdout, stderr)."""
    cmd = [str(REPO_ROOT / "bin" / "bootstrap.sh")] + [str(a) for a in args]
    result = subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def run_python(script: str, args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Invoke claude_bootstrap.<module> directly via uv -m; returns (returncode, stdout, stderr).

    `script` may be passed as bare module name ("install") or legacy `<name>.py`.
    """
    module_name = script[:-3] if script.endswith(".py") else script
    cmd = [
        "uv",
        "run",
        "--with",
        "jinja2",
        "--with",
        "pyyaml",
        "--with",
        "rich",
        "--with",
        "questionary",
        "--no-project",
        "python3",
        "-m",
        f"claude_bootstrap.{module_name}",
    ] + [str(a) for a in args]
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr
