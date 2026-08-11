"""Tests for claude_bootstrap/doctor.py."""

import json
from pathlib import Path

from conftest import run_python

VARS_UNIVERSAL = json.dumps(
    {
        "project_name": "test-proj",
        "project_description": "test",
        "primary_language": "python",
        "is_monorepo": False,
        "git_remote": None,
        "profile_name": "universal-software",
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-01-01",
        "bootstrap_version": "0.1.0-alpha",
    }
)


def test_doctor_empty_dir_fails(tmp_project: Path):
    rc, stdout, stderr = run_python("doctor.py", ["--json", str(tmp_project)])
    assert rc == 1
    data = json.loads(stdout)
    assert data["summary"]["fail"] > 0


def test_doctor_bootstrapped_passes(tmp_project: Path):
    run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    rc, stdout, stderr = run_python("doctor.py", ["--json", str(tmp_project)])
    data = json.loads(stdout)
    assert data["summary"]["fail"] == 0
    assert data["summary"]["pass"] >= 1


def test_doctor_json_output(tmp_project: Path):
    rc, stdout, _ = run_python("doctor.py", ["--json", str(tmp_project)])
    data = json.loads(stdout)
    assert "checks" in data
    assert "summary" in data
    assert isinstance(data["checks"], list)
    assert len(data["checks"]) == 13  # +rules-present (D09)


VARS_MULTI = json.dumps(
    {
        "project_name": "mono",
        "project_description": "d09",
        "primary_language": "mixed",
        "is_monorepo": True,
        "git_remote": None,
        "profiles": ["backend", "devops", "frontend"],
        "stack_paths": {"backend": ["services/api"], "frontend": ["apps/web"], "devops": ["infra"]},
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-07-01",
        "bootstrap_version": "0.4.0a0",
    }
)


def test_doctor_multi_profile_emit_passes(tmp_project: Path):
    """D09: doctor passes on a multi-profile union emit (plural footer matched, rules present)."""
    run_python("install.py", ["--vars-json", VARS_MULTI, "--target", str(tmp_project)])
    rc, stdout, _ = run_python("doctor.py", ["--json", str(tmp_project)])
    data = json.loads(stdout)
    assert data["summary"]["fail"] == 0
    checks = {c["name"]: c["status"] for c in data["checks"]}
    assert checks["profile referenced in CLAUDE.md"] == "PASS"  # matches `profiles:` footer
    assert checks["path-scoped rules present"] == "PASS"  # union ships rules
    # multi root CLAUDE.md stays under the doctor WARN bar (≤150)
    assert (tmp_project / "CLAUDE.md").read_text().count("\n") <= 150


def test_profile_referenced_matches_singular_footer(tmp_path: Path):
    from claude_bootstrap.doctor import STATUS_PASS, check_profile_referenced

    (tmp_path / "CLAUDE.md").write_text("# Proj\n\n<!-- profile: frontend · v0.4.0a0 -->\n")
    res = check_profile_referenced(tmp_path)
    assert res["status"] == STATUS_PASS, res
    assert res["details"].endswith("frontend")


def test_profile_referenced_matches_plural_footer(tmp_path: Path):
    """A multi-profile emit writes `profiles: a, b` — doctor must PASS, not WARN (SP-L)."""
    from claude_bootstrap.doctor import STATUS_PASS, check_profile_referenced

    (tmp_path / "CLAUDE.md").write_text("# Proj\n\n<!-- profiles: backend, frontend · v0.4.0a0 -->\n")
    res = check_profile_referenced(tmp_path)
    assert res["status"] == STATUS_PASS, res
    assert "backend" in res["details"]
