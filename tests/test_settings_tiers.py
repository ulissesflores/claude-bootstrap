"""P1-settings: permission tiers (D01), opt-in sandbox (D02), opt-in hooks (D04).

All three are flag-driven (cli -> interview -> vars.json -> install). Defaults
reproduce today's bytes: no flag => tier=lax (settings.json), sandbox/hooks absent.
Schema shapes pinned against the published Claude Code settings schema (hooks / sandbox).

Run with `uv run python -m pytest` (bare `uv run pytest` hits system Python 3.9).
"""

from __future__ import annotations

import json
from pathlib import Path

from conftest import run_python

from claude_bootstrap import cli

BASE_VARS = {
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


def vars_with(**overrides) -> str:
    return json.dumps({**BASE_VARS, **overrides})


def emit_settings(tmp_project: Path, vars_json: str) -> dict:
    rc, _, stderr = run_python("install.py", ["--vars-json", vars_json, "--target", str(tmp_project)])
    assert rc == 0, stderr
    return json.loads((tmp_project / ".claude" / "settings.json").read_text())


# --- D01: permission tiers ---------------------------------------------------


def test_strict_tier_narrows_allow_but_keeps_safe_planning(tmp_project: Path):
    s = emit_settings(tmp_project, vars_with(tier="strict"))
    allow = s["permissions"]["allow"]
    # safe-planning set kept
    assert "Bash(git status)" in allow
    assert "Bash(ls *)" in allow
    assert "Read" in allow
    assert "WebFetch" in allow
    # a broad lax-only entry is dropped under strict
    assert "Bash(jq *)" not in allow
    assert "Bash(tree *)" not in allow


def test_strict_tier_keeps_deny_superset_and_empty_env(tmp_path: Path):
    s_dir, l_dir = tmp_path / "s", tmp_path / "l"
    s_dir.mkdir()
    l_dir.mkdir()
    strict_deny = set(emit_settings(s_dir, vars_with(tier="strict"))["permissions"]["deny"])
    lax = emit_settings(l_dir, vars_with(tier="lax"))
    lax_deny = set(lax["permissions"]["deny"])
    # deny ⊇ lax: strict must never weaken the lax secret/destruction denies. The
    # subset check (not spot membership) is the load-bearing guardrail — it catches a
    # future drop of ANY entry (e.g. Bash(rm -rf *)) from settings.strict.json.
    assert lax_deny <= strict_deny, f"strict deny missing: {lax_deny - strict_deny}"
    assert "Bash(rm -rf *)" in strict_deny
    assert lax["env"] == {}


def test_no_tier_flag_byte_equals_explicit_lax(tmp_path: Path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    s_none = emit_settings(a, vars_with())  # no tier key at all
    s_lax = emit_settings(b, vars_with(tier="lax"))
    assert (a / ".claude" / "settings.json").read_text() == (b / ".claude" / "settings.json").read_text()
    assert s_none == s_lax


def test_profile_default_tier_selects_strict_without_flag(tmp_project: Path, tmp_path: Path):
    """A profile's `default_tier: strict` picks settings.strict.json with no --tier flag."""
    t = tmp_path / "templates"
    base = t / "_base"
    (base / ".claude").mkdir(parents=True)
    (base / "CLAUDE.md.j2").write_text("hi")
    (base / "PROJECT-STATE.md.j2").write_text("hi")
    (base / ".gitignore").write_text("")
    (base / ".claude" / "settings.json").write_text(
        json.dumps({"permissions": {"allow": ["LAX"], "deny": []}, "env": {}})
    )
    (base / ".claude" / "settings.strict.json").write_text(
        json.dumps({"permissions": {"allow": ["STRICT"], "deny": []}, "env": {}})
    )
    pdir = t / "profiles" / "tight"
    (pdir / "skills").mkdir(parents=True)
    (pdir / "profile.yaml").write_text("default_tier: strict\nsettings_overrides: {}\n")
    vars_json = json.dumps({**BASE_VARS, "profile_name": "tight"})  # no tier key
    rc, _, stderr = run_python(
        "install.py", ["--vars-json", vars_json, "--target", str(tmp_project), "--templates-dir", str(t)]
    )
    assert rc == 0, stderr
    s = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    assert s["permissions"]["allow"] == ["STRICT"]


def test_strict_source_file_does_not_leak_into_emit(tmp_project: Path):
    """settings.strict.json is a SOURCE read by install, never an artifact. Guards against
    a future glob of _base/.claude/* picking it up as a stray emit (+ manifest entry)."""
    emit_settings(tmp_project, vars_with(tier="strict"))
    assert not (tmp_project / ".claude" / "settings.strict.json").exists()
    emitted = {p.name for p in (tmp_project / ".claude").iterdir()}
    # `skills/` arrived when universal-software stopped being an empty profile (first-party
    # skills, 2026-07-28). Kept as an exact set — the point is that nothing UNEXPECTED is
    # emitted, so a stray artifact must still break this.
    assert emitted == {"settings.json", ".bootstrap-manifest.json", "skills"}, emitted


# --- D02: opt-in sandbox -----------------------------------------------------


def test_sandbox_flag_injects_denyread_for_secrets(tmp_project: Path):
    s = emit_settings(tmp_project, vars_with(sandbox=True))
    assert s["sandbox"]["enabled"] is True
    deny_read = s["sandbox"]["filesystem"]["denyRead"]
    assert "~/.ssh" in deny_read
    assert "~/.aws" in deny_read


def test_sandbox_absent_by_default(tmp_project: Path):
    s = emit_settings(tmp_project, vars_with())
    assert "sandbox" not in s


# --- D04: opt-in warn-only hook ----------------------------------------------


def test_hooks_flag_injects_conservative_bundle(tmp_project: Path):
    s = emit_settings(tmp_project, vars_with(hooks=True))
    pre = s["hooks"]["PreToolUse"][0]
    assert pre["matcher"] == "Bash"
    entry = pre["hooks"][0]
    assert entry["type"] == "command"
    # every hook in the bundle is warn-only: never a hard block
    all_cmds = [h["command"] for ev in s["hooks"].values() for grp in ev for h in grp["hooks"]]
    assert all("exit 2" not in c for c in all_cmds)
    # DA6: bundle also carries a forced-eval skill-dispatch hook (UserPromptSubmit -> context on exit 0)
    assert "UserPromptSubmit" in s["hooks"]
    assert "skill" in s["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]


def test_hooks_absent_by_default(tmp_project: Path):
    s = emit_settings(tmp_project, vars_with())
    assert "hooks" not in s


# --- DA6: opt-in fallbackModel ----------------------------------------------


def test_fallback_model_flag_injects_sonnet(tmp_project: Path):
    s = emit_settings(tmp_project, vars_with(fallback_model=True))
    assert s["fallbackModel"] == ["sonnet"]  # array per code.claude.com/docs/en/model-config
    assert isinstance(s["fallbackModel"], list)


def test_fallback_model_absent_by_default(tmp_project: Path):
    s = emit_settings(tmp_project, vars_with())
    assert "fallbackModel" not in s


# --- idempotency with every flag on --------------------------------------------


def test_all_flags_idempotent(tmp_project: Path):
    args = [
        "--vars-json",
        vars_with(tier="strict", sandbox=True, hooks=True, fallback_model=True),
        "--target",
        str(tmp_project),
    ]
    run_python("install.py", args)
    rc, stdout, _ = run_python("install.py", args)
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses[".claude/settings.json"] in ("unchanged", "exists-skipped")


# --- plumbing: cli -> interview -> vars.json ---------------------------------


def test_interview_emits_tier_sandbox_hooks(tmp_project: Path):
    rc, stdout, _ = run_python(
        "interview.py",
        ["--non-interactive", "--tier", "strict", "--sandbox", "--hooks", "--fallback-model"],
        cwd=tmp_project,
    )
    assert rc == 0
    data = json.loads(stdout)
    assert data["tier"] == "strict"
    assert data["sandbox"] is True
    assert data["hooks"] is True
    assert data["fallback_model"] is True


def test_interview_defaults_are_backward_compatible(tmp_project: Path):
    rc, stdout, _ = run_python("interview.py", ["--non-interactive"], cwd=tmp_project)
    assert rc == 0
    data = json.loads(stdout)
    assert data["tier"] is None
    assert data["sandbox"] is False
    assert data["hooks"] is False
    assert data["fallback_model"] is False


def test_cli_forwards_tier_sandbox_hooks_to_interview(monkeypatch, tmp_path: Path):
    calls: list[tuple[str, list[str]]] = []

    def fake_run_module(mod: str, args: list[str]) -> int:
        calls.append((mod, args))
        if mod == "interview" and "--output" in args:
            out = args[args.index("--output") + 1]
            Path(out).write_text(json.dumps(BASE_VARS))
        return 0

    monkeypatch.setattr(cli, "_run_module", fake_run_module)
    rc = cli.cmd_init(
        ["--non-interactive", "--tier", "strict", "--sandbox", "--hooks", "--target", str(tmp_path)]
    )
    assert rc == 0
    interview_args = next(args for mod, args in calls if mod == "interview")
    assert "--tier" in interview_args and "strict" in interview_args
    assert "--sandbox" in interview_args
    assert "--hooks" in interview_args
