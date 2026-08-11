"""Tests for claude_bootstrap/interview.py."""

import json
from pathlib import Path

from conftest import run_python


def test_help_runs_without_questionary(tmp_project: Path):
    rc, stdout, _ = run_python("interview.py", ["--help"], cwd=tmp_project)
    assert rc == 0
    assert "Interview wizard" in stdout or "usage" in stdout.lower()


def test_non_interactive_produces_valid_json(tmp_project: Path):
    rc, stdout, _ = run_python("interview.py", ["--non-interactive"], cwd=tmp_project)
    assert rc == 0
    data = json.loads(stdout)
    assert len(data) == 15
    expected_keys = {
        "project_name",
        "project_description",
        "primary_language",
        "is_monorepo",
        "git_remote",
        "profile_name",
        "superpowers_available",
        "agentic_stack_interop",
        "extra_rules",
        "generated_at",
        "bootstrap_version",
        "tier",
        "sandbox",
        "hooks",
        "fallback_model",
    }
    assert set(data.keys()) == expected_keys


def test_non_interactive_with_profile_flag(tmp_project: Path):
    rc, stdout, _ = run_python(
        "interview.py", ["--non-interactive", "--profile", "academic"], cwd=tmp_project
    )
    assert rc == 0
    data = json.loads(stdout)
    assert data["profile_name"] == "academic"


def test_target_drives_project_name_not_cwd(tmp_path: Path):
    """`--target X` run from a different cwd must use X's identity, not cwd's (fire-test Bug 1)."""
    target = tmp_path / "my-cool-project"
    target.mkdir()
    other = tmp_path / "elsewhere"
    other.mkdir()
    rc, stdout, _ = run_python("interview.py", ["--non-interactive", "--target", str(target)], cwd=other)
    assert rc == 0
    data = json.loads(stdout)
    assert data["project_name"] == "my-cool-project"


def test_output_to_file(tmp_project: Path):
    out_file = tmp_project / "vars.json"
    rc, stdout, _ = run_python(
        "interview.py", ["--non-interactive", "--output", str(out_file)], cwd=tmp_project
    )
    assert rc == 0
    assert stdout.strip() == ""
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "project_name" in data


# --- D08: repeatable --profile → multi-profile vars ---------------------------------------------


def test_interview_repeatable_profile_emits_multi_vars(tmp_project: Path):
    rc, stdout, _ = run_python(
        "interview.py",
        [
            "--non-interactive",
            "--profile",
            "backend",
            "--profile",
            "frontend",
            "--stack-paths-json",
            '{"backend": ["services/api"], "frontend": ["apps/web"]}',
        ],
        cwd=tmp_project,
    )
    assert rc == 0
    data = json.loads(stdout)
    assert data["profiles"] == ["backend", "frontend"]  # deduped + sorted
    assert data["profile_name"] == "backend"  # alphabetical scalar
    assert data["stack_paths"]["backend"] == ["services/api"]
    assert data["is_monorepo"] is True


def test_interview_single_profile_has_no_profiles_key(tmp_project: Path):
    """A single --profile keeps the vars shape byte-identical (no `profiles`/`stack_paths` keys)."""
    rc, stdout, _ = run_python(
        "interview.py", ["--non-interactive", "--profile", "frontend"], cwd=tmp_project
    )
    data = json.loads(stdout)
    assert data["profile_name"] == "frontend"
    assert "profiles" not in data
    assert "stack_paths" not in data
