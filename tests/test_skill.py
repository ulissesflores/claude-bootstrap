"""Tests for claude_bootstrap/skill.py."""

import json
from pathlib import Path

from conftest import run_python


def _local_registry(tmp_path: Path) -> Path:
    """Write a throwaway registry with one local `demo-local` skill (absolute source path).

    install_local resolves `REPO_ROOT / source.path`; an absolute path overrides REPO_ROOT,
    so the skill body can live in a tmp dir and no fixture needs to be committed.
    """
    src = tmp_path / "src" / "demo-local"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("---\nname: demo-local\n---\ndemo\n")
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        "- name: demo-local\n"
        "  description: local test skill\n"
        "  source:\n"
        "    type: local\n"
        f"    path: {src}\n"
        "  tier: 1\n"
        "  profiles: [universal-software]\n"
        "  last_validated_at: 2026-01-01\n"
    )
    return registry


def test_skill_validate_passes(tmp_project: Path):
    rc, stdout, stderr = run_python("skill.py", ["validate"])
    assert rc == 0
    assert "OK:" in stdout


def test_skill_validate_warns_on_stale_entries(tmp_project: Path, tmp_path: Path):
    stale_registry = tmp_path / "stale.yaml"
    stale_registry.write_text(
        "- name: stale-skill\n"
        "  description: test\n"
        "  source:\n"
        "    type: github\n"
        "    url: https://github.com/x/y\n"
        "    path: skills/stale-skill\n"
        "  tier: 1\n"
        "  profiles: [universal-software]\n"
        "  last_validated_at: 2024-01-01\n"
    )
    rc, stdout, stderr = run_python("skill.py", ["--registry", str(stale_registry), "validate"])
    assert rc == 0
    assert "WARN" in stderr
    assert "stale-skill" in stderr


def test_skill_list_outputs(tmp_project: Path):
    rc, stdout, _ = run_python("skill.py", ["list", "--target", str(tmp_project)])
    assert rc == 0
    assert "Total: 13 skill(s)" in stdout


def test_skill_add_local_idempotent(tmp_project: Path, tmp_path: Path):
    registry = _local_registry(tmp_path)
    args = ["--registry", str(registry), "add", "demo-local", "--target", str(tmp_project)]
    rc1, stdout1, _ = run_python("skill.py", args)
    assert rc1 == 0
    data1 = json.loads(stdout1)
    assert data1["status"] == "installed"

    rc2, stdout2, _ = run_python("skill.py", args)
    assert rc2 == 0
    data2 = json.loads(stdout2)
    assert data2["status"] == "exists-skipped"


def test_skill_update_no_skills_dir(tmp_project: Path):
    rc, stdout, _ = run_python("skill.py", ["update", "--target", str(tmp_project)])
    assert rc == 0
    data = json.loads(stdout)
    assert data["updated"] == []


def test_skill_update_reinstalls_local(tmp_project: Path, tmp_path: Path):
    registry = _local_registry(tmp_path)
    reg = ["--registry", str(registry)]
    add_args = [*reg, "add", "demo-local", "--target", str(tmp_project)]
    rc, _, _ = run_python("skill.py", add_args)
    assert rc == 0
    skill_path = tmp_project / ".claude" / "skills" / "demo-local"
    assert skill_path.is_dir()
    # corrupt installed copy
    (skill_path / "MARKER.txt").write_text("user mod")
    rc, stdout, _ = run_python("skill.py", [*reg, "update", "--target", str(tmp_project)])
    assert rc == 0
    statuses = {r["name"]: r["status"] for r in json.loads(stdout)["updated"]}
    assert statuses["demo-local"] == "installed"
    assert not (skill_path / "MARKER.txt").exists()


def test_skill_show_returns_entry(tmp_project: Path):
    # A wrong name yields rc=1 + "not found" in stderr; a real registry entry does not.
    rc_bad, _, stderr_bad = run_python("skill.py", ["show", "nonexistent-skill-xyz"])
    assert rc_bad == 1
    assert "not found" in stderr_bad

    rc_good, _, stderr_good = run_python("skill.py", ["show", "brainstorming"])
    assert rc_good == 0
    assert "not found" not in stderr_good
