"""Acceptance tests for the schema drift-guard (D00).

Invokes scripts/verify-schema-currency.py BY PATH — it is a standalone stdlib
script, not a claude_bootstrap module, so conftest.run_python (which targets
claude_bootstrap.<module>) does not apply. Run the suite with
`uv run python -m pytest` (bare `uv run pytest` hits macOS system Python 3.9).

The offline tests (1-7) gate the suite. The network test (8) self-skips when
there is no connectivity (or when OFFLINE is set) so CI/offline runs stay green;
liveness is exercised for real in the schema-currency CI job + manual smoke.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "verify-schema-currency.py"
SOURCES = REPO_ROOT / "scripts" / "schema-sources.json"

EXPECTED_SCHEMAS = {
    "settings.permissions",
    "permission-modes",
    "hooks",
    "sandbox",
    "agents-frontmatter",
    ".mcp.json",
    "plugin.json",
    "statusLine",
    "output-styles",
}


def run(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run the guard script by path, returning the completed process."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


def load_sources() -> list[dict]:
    return json.loads(SOURCES.read_text())


# --- deterministic / offline (these gate the suite) ---


def test_sources_is_array_of_well_formed_items():
    data = load_sources()
    assert isinstance(data, list) and data, "expected a non-empty JSON array"
    for item in data:
        assert {"schema", "url", "verified"} <= set(item), f"missing keys in {item}"


def test_every_url_is_https():
    for item in load_sources():
        assert item["url"].startswith("https://"), item["url"]


def test_every_verified_is_iso_date():
    for item in load_sources():
        datetime.date.fromisoformat(item["verified"])  # raises ValueError if not ISO


def test_all_expected_schemas_present():
    names = {item["schema"] for item in load_sources()}
    assert names == EXPECTED_SCHEMAS, names ^ EXPECTED_SCHEMAS


def test_check_with_huge_max_age_passes():
    r = run(["--check", "--max-age-days", "100000"])
    assert r.returncode == 0, r.stdout + r.stderr


def test_check_flags_stale_entry(tmp_path: Path):
    stale = tmp_path / "stale.json"
    stale.write_text(
        json.dumps(
            [{"schema": "settings.permissions", "url": "https://example.com", "verified": "2000-01-01"}]
        )
    )
    r = run(["--check"], env={"SCHEMA_SOURCES": str(stale)})
    assert r.returncode != 0
    assert "STALE" in r.stdout


def test_check_today_is_fresh(tmp_path: Path):
    today = datetime.date.today().isoformat()
    fresh = tmp_path / "fresh.json"
    fresh.write_text(json.dumps([{"schema": "hooks", "url": "https://example.com", "verified": today}]))
    r = run(["--check"], env={"SCHEMA_SOURCES": str(fresh)})
    assert r.returncode == 0, r.stdout + r.stderr


# --- network (does NOT gate; self-skips with no connectivity) ---


@pytest.mark.skipif(bool(os.environ.get("OFFLINE")), reason="OFFLINE set")
def test_liveness_all_urls_live():
    r = run([])
    # status None => network error (not a real dead URL) => skip, don't fail.
    if r.returncode != 0 and "DEAD[None]" in r.stdout:
        pytest.skip("no network in this sandbox")
    assert r.returncode == 0, r.stdout + r.stderr
