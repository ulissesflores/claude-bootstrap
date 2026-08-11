"""Metadata currency — what the repo *claims* must match what is *on disk*.

Deliberately LOW-CHURN: every assertion here is derived, never a hardcoded
inventory number. Adding a test, a skill, or a profile must not make this file
go red. What it catches is drift between the declarations (pyproject,
CITATION.cff, profile.yaml, registry) and the tree they describe — the class of
rot that made a registry tag point at a profile that had already been deleted.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT

from claude_bootstrap import __version__
from claude_bootstrap.interview import PROFILES

PROFILES_DIR = REPO_ROOT / "claude_bootstrap" / "templates" / "profiles"
REGISTRY = REPO_ROOT / "claude_bootstrap" / "registry" / "skills.yaml"


def _profile_yamls() -> list[Path]:
    return sorted(PROFILES_DIR.glob("*/profile.yaml"))


def _declared_profile_names() -> set[str]:
    """Profile names `interview.py` offers — the tool's own public list.

    Imported, not scraped: a text scrape of the literal breaks the moment ruff format
    explodes the list past `line-length` and inserts a magic trailing comma, which is
    exactly the "adding a profile must not go red" case this file promises to tolerate.
    """
    return set(PROFILES)


# --- version triple ---------------------------------------------------------


def test_version_matches_pyproject_and_citation():
    """`__version__`, pyproject and CITATION.cff must agree (a release forgets one)."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text()
    match = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)
    assert match, "pyproject.toml has no top-level `version = ...` line"
    pyproject_version = match.group(1)

    cff = yaml.safe_load((REPO_ROOT / "CITATION.cff").read_text())

    assert pyproject_version == __version__
    assert cff["version"] == __version__
    assert cff["preferred-citation"]["version"] == __version__


# --- profiles: declared <-> on disk -----------------------------------------


def test_every_offered_profile_exists_on_disk():
    for name in _declared_profile_names():
        assert (PROFILES_DIR / name / "profile.yaml").is_file(), f"{name} is offered but has no profile.yaml"


def test_every_profile_dir_is_offered():
    """The reverse direction — an orphan profile dir would ship without being reachable."""
    on_disk = {p.parent.name for p in _profile_yamls()}
    assert on_disk == _declared_profile_names()


@pytest.mark.parametrize("profile_yaml", _profile_yamls(), ids=lambda p: p.parent.name)
def test_profile_declares_only_assets_that_exist(profile_yaml: Path):
    """Every skill and rule a profile.yaml names must be present in its bundle."""
    profile_dir = profile_yaml.parent
    spec = yaml.safe_load(profile_yaml.read_text())

    for skill in spec.get("skills") or []:
        assert (profile_dir / "skills" / skill / "SKILL.md").is_file(), (
            f"{profile_dir.name}: declares skill {skill!r} with no SKILL.md"
        )
    for rule in spec.get("rules") or []:
        assert (profile_dir / "rules" / rule).is_file(), (
            f"{profile_dir.name}: declares rule {rule!r} which is missing"
        )


@pytest.mark.parametrize("profile_yaml", _profile_yamls(), ids=lambda p: p.parent.name)
def test_bundled_profile_has_a_notice(profile_yaml: Path):
    """Any profile that redistributes skills owes a NOTICE.md (licence + provenance)."""
    profile_dir = profile_yaml.parent
    if yaml.safe_load(profile_yaml.read_text()).get("skills"):
        assert (profile_dir / "NOTICE.md").is_file(), (
            f"{profile_dir.name}: bundles skills but has no NOTICE.md"
        )


# --- registry: declared <-> on disk -----------------------------------------


def test_registry_entries_target_real_profiles():
    """A registry entry tagged for a profile that no longer exists is dead config."""
    known = _declared_profile_names()
    for entry in yaml.safe_load(REGISTRY.read_text()):
        unknown = set(entry.get("profiles") or []) - known
        assert not unknown, f"registry entry {entry['name']!r} targets unknown profile(s): {sorted(unknown)}"


def test_registry_local_sources_resolve():
    for entry in yaml.safe_load(REGISTRY.read_text()):
        source = entry.get("source") or {}
        if source.get("type") == "local":
            assert (REPO_ROOT / source["path"]).is_dir(), (
                f"registry entry {entry['name']!r} points at a missing local path: {source['path']}"
            )
