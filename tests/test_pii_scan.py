"""`scripts/pii-scan.py`: the structural layer, and the guards that keep a clean run honest.

Scoped to the **structural** patterns on purpose. The scanner's person/organisation/host
literals live in a gitignored `.pii-patterns.local` and are exercised by a manual canary —
a committed test that embedded them would recreate the leak this split exists to close
(STATE inbox 12, 2026-08-10). What CI can prove without them is proved here.

The load-bearing case is `test_no_tracked_file_carries_a_home_path`: it runs with **zero
exemptions**, so it doubles as the check that nothing is hiding behind an allowlist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "pii-scan.py"

# Split so this file does not trip the gate it tests — the scan runs with no exemptions, and a
# whole home path written literally here would be a real hit. Caught by the gate on first run.
HOME_PATH = "/" + "Users/somebody/Developer/x/"


def _load_module():
    spec = importlib.util.spec_from_file_location("pii_scan", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_structural_pattern_catches_a_home_path(tmp_path):
    mod = _load_module()
    (tmp_path / "leak.md").write_text(f"see {HOME_PATH} for the config\n")
    hits = mod.scan(["leak.md"], tmp_path, mod.compile_patterns(mod.PATTERNS))
    assert len(hits) == 1
    assert "absolute home path" in hits[0]


@pytest.mark.parametrize("placeholder", ["/Users/user/project/", "/home/usuario/project/"])
def test_teaching_placeholders_are_exempt(tmp_path, placeholder):
    """The docs use these when *teaching* that absolute paths are an anti-pattern."""
    mod = _load_module()
    (tmp_path / "doc.md").write_text(f"never hardcode {placeholder}\n")
    assert mod.scan(["doc.md"], tmp_path, mod.compile_patterns(mod.PATTERNS)) == []


def test_no_tracked_file_carries_a_home_path():
    """The real repo, structural patterns only, no exemptions of any kind."""
    mod = _load_module()
    hits = mod.scan(mod.tracked_files(), REPO_ROOT, mod.compile_patterns(mod.PATTERNS))
    assert hits == [], f"{len(hits)} hit(s): {hits[:3]}"


def test_local_patterns_extend_the_scan(tmp_path):
    mod = _load_module()
    data = tmp_path / ".pii-patterns.local"
    data.write_text("# a comment\n\n(?i)acme-internal\tfictional org marker\n")
    extra = mod.read_local_patterns(data)
    assert extra == [("(?i)acme-internal", "fictional org marker")]

    (tmp_path / "leak.md").write_text("deployed on ACME-Internal last week\n")
    compiled = mod.compile_patterns(mod.PATTERNS + extra)
    assert len(mod.scan(["leak.md"], tmp_path, compiled)) == 1


def test_missing_local_file_is_a_supported_state(tmp_path):
    mod = _load_module()
    assert mod.read_local_patterns(tmp_path / "absent") == []


def test_malformed_local_line_is_fatal(tmp_path):
    """Skipping it would turn a typo into a narrower scan that still prints `clean`."""
    mod = _load_module()
    data = tmp_path / ".pii-patterns.local"
    data.write_text("no-tab-separator here\n")
    with pytest.raises(SystemExit):
        mod.read_local_patterns(data)


def test_invalid_regex_is_fatal():
    mod = _load_module()
    with pytest.raises(SystemExit):
        mod.compile_patterns([("(?i)[unclosed", "broken")])


def test_success_line_distinguishes_the_two_modes():
    """A clean run from fewer patterns is not the same result and must not read alike."""
    mod = _load_module()
    structural_only = mod.describe_mode([])
    extended = mod.describe_mode([("x", "y"), ("z", "w")])
    assert structural_only != extended
    assert "structural only" in structural_only
    assert "+2 local pattern(s)" in extended
