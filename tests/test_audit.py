"""D13a — `claude-bootstrap audit`: provenance + integrity report (the moat).

Offline, manifest-driven. After a real emit the report attests what was written,
each skill's upstream source@SHA, and whether on-disk bytes still match the manifest.
"""

from __future__ import annotations

import json
from pathlib import Path

from conftest import run_python

ACADEMIC_VARS = json.dumps(
    {
        "project_name": "audit-me",
        "project_description": "d13a",
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


def _install_academic(target: Path):
    rc, _, err = run_python("install.py", ["--vars-json", ACADEMIC_VARS, "--target", str(target)])
    assert rc == 0, err
    assert (target / ".claude" / ".bootstrap-manifest.json").exists()


def _audit_json(target: Path, *flags: str):
    rc, stdout, stderr = run_python("audit.py", [str(target), "--json", *flags])
    return rc, json.loads(stdout), stderr


MULTI_VARS = json.dumps(
    {
        "project_name": "mono",
        "project_description": "d13 union",
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


def test_audit_union_resolves_every_profile(tmp_path: Path):
    """D13/SP-X: a multi-profile union audits PASS — provenance resolves for EVERY profile's skills,
    not just profiles[0]'s. Before D13 this was INCOMPLETE (only profiles[0]'s NOTICE was read)."""
    rc, _, err = run_python("install.py", ["--vars-json", MULTI_VARS, "--target", str(tmp_path)])
    assert rc == 0, err
    rc, report, _ = _audit_json(tmp_path)
    assert rc == 0
    assert report["integrity"]["verdict"] == "PASS"
    assert report["profiles"] == ["backend", "devops", "frontend"]  # the set, not a single name
    assert report["profile"] == "backend"  # scalar kept for back-compat readers
    assert len(report["skills"]) == 16  # 4 backend + 5 devops + 7 frontend, all resolved
    assert all(s["provenance"] == "pinned" for s in report["skills"])
    assert report["provenance_conflicts"] == []


def test_audit_legacy_scalar_manifest_still_pass(tmp_path: Path):
    """Back-compat: a legacy single-profile manifest (scalar `profile`, no `profiles`) still audits;
    the report derives the set from the scalar."""
    _install_academic(tmp_path)
    manifest = json.loads((tmp_path / ".claude" / ".bootstrap-manifest.json").read_text())
    assert "profiles" not in manifest  # single-profile install writes only the scalar
    rc, report, _ = _audit_json(tmp_path)
    assert rc == 0
    assert report["profile"] == "academic"
    assert report["profiles"] == ["academic"]


def test_audit_surfaces_provenance_conflict(tmp_path: Path, monkeypatch):
    """D13/SP-X positive branch: two profiles' NOTICE maps disagreeing on a skill's owner are
    surfaced in `provenance_conflicts`, not silently last-wins."""
    from claude_bootstrap import audit

    claude = tmp_path / ".claude"
    claude.mkdir()
    (claude / ".bootstrap-manifest.json").write_text(
        json.dumps(
            {"version": "x", "profile": "a", "profiles": ["a", "b"], "files": [], "gitignore_added": []}
        )
    )

    def fake_prov(p):
        owner = "ownerA" if p == "a" else "ownerB"
        return {
            "shared": {
                "owner": owner,
                "repo": "r",
                "path": "x",
                "url": f"https://github.com/{owner}/r/tree/main/x",
            }
        }

    monkeypatch.setattr(audit, "_provenance_map", fake_prov)
    report = audit.build_report(tmp_path)
    assert report["provenance_conflicts"], "a same-name/different-owner clash must be surfaced"
    assert report["provenance_conflicts"][0]["skill"] == "shared"
    assert set(report["provenance_conflicts"][0]["owners"]) == {"ownerA", "ownerB"}


def test_audit_json_shape_pass(tmp_path: Path):
    _install_academic(tmp_path)
    rc, report, _ = _audit_json(tmp_path)
    assert rc == 0
    assert report["schema"] == "claude-bootstrap.audit/v1"
    assert report["generated_for"] == str(tmp_path.resolve())
    assert report["bootstrap_version"] == "0.4.0a0"
    assert report["profile"] == "academic"
    # all 3 academic skills, each with a resolvable upstream source + pinned SHA
    # (was 7 — docx/pdf/pptx/doc-coauthoring de-bundled 2026-07-26, not redistributable)
    assert len(report["skills"]) == 3
    for s in report["skills"]:
        assert s["source"] is not None
        assert s["source"]["url"].startswith("https://github.com/")
        assert s["source"]["pinned_sha"]  # non-null (pins resolve from the repo checkout)
        assert s["provenance"] == "pinned"
        assert s["manifest_match"] is True
    assert report["permissions"]["secret_deny_present"] is True
    assert report["integrity"]["verdict"] == "PASS"


def test_audit_detects_tamper(tmp_path: Path):
    _install_academic(tmp_path)
    skill = tmp_path / ".claude" / "skills" / "citation-management" / "SKILL.md"
    # discriminator: it must read PASS / matched BEFORE the edit...
    _, before, _ = _audit_json(tmp_path)
    assert before["integrity"]["verdict"] == "PASS"
    assert all(s["manifest_match"] for s in before["skills"])

    skill.write_text(skill.read_text() + "\n<!-- tampered -->\n")

    # ...and MODIFIED for exactly that skill AFTER
    rc, after, _ = _audit_json(tmp_path)
    assert after["integrity"]["verdict"] == "MODIFIED"
    tampered = next(s for s in after["skills"] if s["name"] == "citation-management")
    assert tampered["manifest_match"] is False
    assert all(s["manifest_match"] for s in after["skills"] if s["name"] != "citation-management")
    # --strict turns a non-PASS verdict into a non-zero exit
    rc_strict, _, _ = run_python("audit.py", [str(tmp_path), "--strict"])
    assert rc_strict == 1


def test_audit_empty_manifest_is_incomplete(tmp_path: Path):
    # a valid-JSON-but-empty manifest must NOT certify the tree clean: there is nothing
    # to attest, so it is INCOMPLETE (else truncating the manifest to {} after a tamper
    # would launder a tampered tree into a false PASS).
    _install_academic(tmp_path)
    (tmp_path / ".claude" / ".bootstrap-manifest.json").write_text("{}")
    rc, report, _ = _audit_json(tmp_path)
    assert report["integrity"]["files_audited"] == 0
    assert report["integrity"]["verdict"] == "INCOMPLETE"
    rc_strict, _, _ = run_python("audit.py", [str(tmp_path), "--strict"])
    assert rc_strict == 1


def test_audit_detects_untracked_injection(tmp_path: Path):
    _install_academic(tmp_path)
    # discriminator: a clean tree is PASS...
    _, before, _ = _audit_json(tmp_path)
    assert before["integrity"]["verdict"] == "PASS"
    assert before["integrity"]["files_untracked"] == 0

    # ...inject a skill that the manifest never knew about
    evil = tmp_path / ".claude" / "skills" / "evil-skill" / "SKILL.md"
    evil.parent.mkdir(parents=True)
    evil.write_text("---\nname: evil\n---\nplanted\n")

    rc, after, _ = _audit_json(tmp_path)
    assert after["integrity"]["verdict"] != "PASS"
    assert after["integrity"]["files_untracked"] >= 1
    assert any("evil-skill" in p for p in after["integrity"]["untracked"])
    rc_strict, _, _ = run_python("audit.py", [str(tmp_path), "--strict"])
    assert rc_strict == 1


def test_audit_no_manifest_is_incomplete(tmp_path: Path):
    # bare dir, no emit → must not crash
    rc, report, _ = _audit_json(tmp_path)
    assert rc == 0  # report-only without --strict
    assert report["integrity"]["manifest_present"] is False
    assert report["integrity"]["verdict"] == "INCOMPLETE"
    rc_strict, _, _ = run_python("audit.py", [str(tmp_path), "--strict"])
    assert rc_strict == 1


def test_audit_permissions_block(tmp_path: Path):
    _install_academic(tmp_path)
    _, report, _ = _audit_json(tmp_path)
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    assert report["permissions"]["deny_count"] == len(settings["permissions"]["deny"])
    assert report["permissions"]["allow_count"] == len(settings["permissions"]["allow"])
    assert report["permissions"]["secret_deny_present"] is True


def test_packaged_pins_match_canonical():
    # the wheel ships claude_bootstrap/skill-pins.json so a pip-installed `audit` resolves
    # pins; it must stay byte-identical to the canonical scripts/skill-pins.json (else the
    # wheel would attest a stale pinned_sha — the exact thing the no-SHA-fallback forbids).
    repo = Path(__file__).resolve().parent.parent
    canonical = (repo / "scripts" / "skill-pins.json").read_bytes()
    packaged = (repo / "claude_bootstrap" / "skill-pins.json").read_bytes()
    assert packaged == canonical, "package skill-pins.json drifted from scripts/skill-pins.json"


def test_cli_audit_dispatch(tmp_path: Path):
    _install_academic(tmp_path)
    rc, stdout, _ = run_python("cli", ["audit", "--json", str(tmp_path)])
    assert rc == 0
    assert json.loads(stdout)["schema"] == "claude-bootstrap.audit/v1"
