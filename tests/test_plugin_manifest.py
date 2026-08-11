"""D07 — plugin-manifest expansion.

Each profile's ``.claude-plugin/plugin.json`` carries the current-schema fields
(``$schema``, ``displayName``, ``defaultEnabled``, ``keywords``), agrees with the
marketplace entry, validates under ``claude plugin validate``, and never leaks
into an emitted project.

Schema verified live vs ``code.claude.com/docs/en/plugins-reference`` (2026-06-08)
and ``claude plugin validate`` (Claude Code 2.1.168). ``defaultEnabled: false`` is
the documented opt-in shape: the bundle installs disabled; the user enables it via
``claude plugin enable`` / ``/plugin``.

The CI backstop is ``test_plugin_manifest_full_structural_contract`` (always runs).
``test_claude_plugin_validate_passes`` is a stronger *live* check that skips when the
Claude Code CLI is absent (e.g. in CI), so it is a bonus, not the sole acceptance.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import run_python

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = REPO_ROOT / "claude_bootstrap" / "templates" / "profiles"
PROFILE_NAMES = ["academic", "backend", "data-science", "devops", "frontend", "universal-software"]
SCHEMA_URL = "https://json.schemastore.org/claude-code-plugin-manifest.json"


def _manifest(profile: str) -> dict:
    return json.loads((PROFILES_DIR / profile / ".claude-plugin" / "plugin.json").read_text())


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_plugin_manifest_has_current_schema_fields(profile: str):
    data = _manifest(profile)
    assert data["name"] == profile
    assert data["$schema"] == SCHEMA_URL
    assert isinstance(data["displayName"], str) and data["displayName"].strip()
    # opt-in bundles ship disabled (docs: "installs disabled... a user should opt into")
    assert data["defaultEnabled"] is False
    assert isinstance(data["keywords"], list) and len(data["keywords"]) >= 3


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_plugin_manifest_full_structural_contract(profile: str):
    """Deterministic CI backstop for the shape `claude plugin validate` enforces.

    Runs everywhere (no CLI needed), so a malformed manifest fails CI even though the
    live-validate test skips. Field types pinned per the 2026-06-08 verified schema.
    Intentionally NOT a vendored JSON-Schema file: that would reintroduce the very
    drift this project exists to prevent (the schema URL would itself go stale).
    """
    data = _manifest(profile)
    assert isinstance(data["name"], str) and data["name"] == profile
    assert data["$schema"] == SCHEMA_URL
    assert isinstance(data["displayName"], str) and data["displayName"].strip()
    assert isinstance(data["description"], str) and data["description"].strip()
    assert isinstance(data["version"], str) and data["version"]
    assert isinstance(data["license"], str) and data["license"]
    assert isinstance(data["author"], dict) and data["author"].get("name")
    assert isinstance(data["homepage"], str) and data["homepage"].startswith("http")
    assert isinstance(data["repository"], str) and data["repository"].startswith("http")
    assert isinstance(data["keywords"], list) and data["keywords"]
    assert all(isinstance(k, str) and k for k in data["keywords"])
    assert data["defaultEnabled"] is False
    # no `dependencies` on leaf bundles (would dangle — superpowers is not a plugin here)
    assert "dependencies" not in data


def test_marketplace_entries_match_plugin_manifests():
    market = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text())
    market_names = {p["name"] for p in market["plugins"]}
    assert market_names == set(PROFILE_NAMES)
    for profile in PROFILE_NAMES:
        assert _manifest(profile)["name"] == profile


@pytest.mark.skipif(shutil.which("claude") is None, reason="claude CLI not on PATH")
@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_claude_plugin_validate_passes(profile: str):
    result = subprocess.run(
        ["claude", "plugin", "validate", str(PROFILES_DIR / profile)],
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_plugin_manifests_not_leaked_into_emit(tmp_path: Path):
    vars_json = json.dumps(
        {
            "project_name": "leak-check",
            "project_description": "d07 no-leak",
            "primary_language": "mixed",
            "is_monorepo": False,
            "git_remote": None,
            "profile_name": "academic",
            "superpowers_available": False,
            "agentic_stack_interop": False,
            "extra_rules": [],
            "generated_at": "2026-06-08",
            "bootstrap_version": "0.4.0a0",
        }
    )
    rc, _, _ = run_python("install.py", ["--vars-json", vars_json, "--target", str(tmp_path)])
    assert rc == 0
    leaked = list(tmp_path.rglob("plugin.json")) + list(tmp_path.rglob(".claude-plugin"))
    assert leaked == [], f"packaging manifest leaked into emit: {leaked}"
