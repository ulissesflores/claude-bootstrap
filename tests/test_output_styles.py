"""D11 — statusLine + output-styles (opt-in, off by default).

Both surfaces are emitted only when a profile opts in. Schemas verified live vs
code.claude.com/docs/en/statusline + /docs/en/output-styles (2026-06-08):
- statusLine: settings.json `statusLine.type == "command"`, `command` may be an
  inline shell command (no script file → no exec-bit problem).
- output style: `.claude/output-styles/<name>.md`, YAML frontmatter `name` /
  `description` (+ `keep-coding-instructions`), body added to the system prompt.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from conftest import run_python

REPO_ROOT = Path(__file__).resolve().parent.parent


def _vars(profile: str) -> str:
    return json.dumps(
        {
            "project_name": "d11",
            "project_description": "statusline + output-styles",
            "primary_language": "mixed",
            "is_monorepo": False,
            "git_remote": None,
            "profile_name": profile,
            "superpowers_available": False,
            "agentic_stack_interop": False,
            "extra_rules": [],
            "generated_at": "2026-06-08",
            "bootstrap_version": "0.4.0a0",
        }
    )


def _install(target: Path, profile: str, extra: list[str] | None = None):
    rc, stdout, stderr = run_python(
        "install.py", ["--vars-json", _vars(profile), "--target", str(target)] + (extra or [])
    )
    assert rc == 0, stderr
    return stdout


# ---------------------------------------------------------------- off by default


def test_output_styles_off_by_default(tmp_path: Path):
    _install(tmp_path, "universal-software")
    # two separate emit paths — assert both stay silent
    assert not (tmp_path / ".claude" / "output-styles").exists()
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    assert "statusLine" not in settings


# ---------------------------------------------------------------- on when opted (academic)


def test_statusline_emitted_for_opted_profile(tmp_path: Path):
    _install(tmp_path, "academic")
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    # json.loads is the guard: a YAML→JSON quote-escaping mangle would fail to parse here
    assert settings["statusLine"]["type"] == "command"
    assert isinstance(settings["statusLine"]["command"], str) and settings["statusLine"]["command"]


def test_output_style_file_emitted_and_frontmatter_parses(tmp_path: Path):
    _install(tmp_path, "academic")
    style = tmp_path / ".claude" / "output-styles" / "concise-academic.md"
    assert style.exists()
    text = style.read_text()
    assert text.startswith("---")
    fm = yaml.safe_load(text.split("---", 2)[1])
    assert fm["name"] and fm["description"]
    # academic still codes (EDA/scripts) → keep Claude's software-engineering instructions
    assert fm.get("keep-coding-instructions") is True


def test_output_styles_idempotent(tmp_path: Path):
    _install(tmp_path, "academic")
    stdout = _install(tmp_path, "academic")
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses[".claude/output-styles/concise-academic.md"] in ("unchanged", "exists-skipped")


# ---------------------------------------------------------------- reversible


def test_no_workflows_or_routines_emitted(tmp_path: Path):
    # D12 (doc-only): Workflows are Claude-written JS and Routines are server-side,
    # so a static scaffolder emits neither — assert absence on the richest profile.
    _install(tmp_path, "academic")
    assert not (tmp_path / ".claude" / "workflows").exists()
    assert not list(tmp_path.rglob("*.schedule"))


def test_output_styles_uninstall_round_trip(tmp_path: Path):
    _install(tmp_path, "academic")
    style = tmp_path / ".claude" / "output-styles" / "concise-academic.md"
    assert style.exists()
    rc, _, stderr = run_python("uninstall.py", ["--target", str(tmp_path)])
    assert rc == 0, stderr
    assert not style.exists()
    assert not (tmp_path / ".claude" / "output-styles").exists()
    assert not (tmp_path / ".claude").exists()  # whole emit reverted, host pristine
