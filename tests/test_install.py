"""Tests for claude_bootstrap/install.py."""

import hashlib
import json
import shutil
from pathlib import Path

from conftest import REPO_ROOT, run_python

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

VARS_ACADEMIC_NEW = json.dumps(
    {
        "project_name": "test-acad",
        "project_description": "test (v0.4.0a0 generic academic)",
        "primary_language": "mixed",
        "is_monorepo": False,
        "git_remote": None,
        "profile_name": "academic",
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-05-14",
        "bootstrap_version": "0.4.0a0",
    }
)

VARS_DEVOPS = json.dumps(
    {
        "project_name": "test-devops",
        "project_description": "devops test",
        "primary_language": "shell",
        "is_monorepo": False,
        "git_remote": None,
        "profile_name": "devops",
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-05-14",
        "bootstrap_version": "0.4.0a0",
    }
)

VARS_DATA_SCIENCE = json.dumps(
    {
        "project_name": "test-ds",
        "project_description": "data-science test",
        "primary_language": "python",
        "is_monorepo": False,
        "git_remote": None,
        "profile_name": "data-science",
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-05-14",
        "bootstrap_version": "0.4.0a0",
    }
)

VARS_FRONTEND = json.dumps(
    {
        "project_name": "test-fe",
        "project_description": "frontend test",
        "primary_language": "typescript",
        "is_monorepo": False,
        "git_remote": None,
        "profile_name": "frontend",
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-05-14",
        "bootstrap_version": "0.4.0a0",
    }
)


VARS_BACKEND = json.dumps(
    {
        "project_name": "test-be",
        "project_description": "backend test",
        "primary_language": "python",
        "is_monorepo": False,
        "git_remote": None,
        "profile_name": "backend",
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-06-30",
        "bootstrap_version": "0.4.0a0",
    }
)


VARS_MULTI = json.dumps(
    {
        "project_name": "mono",
        "project_description": "monorepo test",
        "primary_language": "mixed",
        "is_monorepo": True,
        "git_remote": None,
        "profiles": ["backend", "devops", "frontend"],
        "stack_paths": {"backend": ["services/api"], "frontend": ["apps/web"], "devops": ["infra"]},
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-06-30",
        "bootstrap_version": "0.4.0a0",
    }
)


def test_init_with_backend_profile(tmp_project: Path):
    """Backend profile (config-only): 4 curated skills + rule + agent + app/CLAUDE.md subdir."""
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_BACKEND, "--target", str(tmp_project)])
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses.get(".claude/rules/backend.md") == "created"
    assert statuses.get(".claude/agents/api-contract-reviewer.md") == "created"
    assert statuses.get("app/CLAUDE.md") == "created"
    # 4 operator-approved skills (D02b)
    skill_dirs = {f.split("/")[2] for f in statuses if f.startswith(".claude/skills/")}
    assert skill_dirs == {
        "api-design-reviewer",
        "api-test-suite-builder",
        "database-schema-designer",
        "migration-architect",
    }, skill_dirs
    rule_body = (tmp_project / ".claude" / "rules" / "backend.md").read_text()
    assert "paths:" in rule_body and len(rule_body.strip()) > 100


def test_backend_profile_is_config_only(tmp_project: Path):
    """Config-only: deny PRECISE install commands; NEVER broad substrings that would block
    git add / git fetch / rsync. (SP-V advisory half.)"""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_BACKEND, "--target", str(tmp_project)])
    assert rc == 0
    settings = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    deny = settings["permissions"]["deny"]
    assert "Bash(pip install *)" in deny
    assert "Bash(npm ci *)" in deny
    assert "Bash(poetry add *)" in deny
    # No broad substring deny that would catch a benign command
    for entry in deny:
        assert entry not in ("Bash(*add*)", "Bash(*sync*)", "Bash(*fetch*)", "Bash(*install*)")
        # a precise install deny must name a concrete leading command, not a bare wildcard
        assert not entry.startswith("Bash(*")


def test_install_py_never_shells_a_package_manager():
    """The ENFORCED config-only guarantee (SP-V): install.py imports no subprocess / os.system."""
    src = (REPO_ROOT / "claude_bootstrap" / "install.py").read_text()
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "Popen" not in src


# --- D05: rule paths fill (multi dir-scoped from stack_paths; single byte-identical) -----------


def test_fill_rule_paths_derives_dir_globs():
    from claude_bootstrap.install import _fill_rule_paths

    content = '---\npaths:\n  - "**/*.py"\n  - "**/*.ts"\n---\n\n# Backend conventions\n\n- rule body\n'
    out = _fill_rule_paths(content, ["backend", "services/api"])
    assert '"backend/**"' in out
    assert '"services/api/**"' in out
    assert '"**/*.py"' not in out  # extension globs replaced by dir globs
    assert "# Backend conventions" in out  # body preserved


def test_fill_rule_paths_empty_dirs_is_noop():
    """Empty discovery → keep the static extension globs (never emit an empty paths:)."""
    from claude_bootstrap.install import _fill_rule_paths

    content = '---\npaths:\n  - "**/*.py"\n---\n\n# body\n'
    assert _fill_rule_paths(content, []) == content


def test_install_profile_assets_multi_scopes_rules_and_suppresses_static_subdir(tmp_project: Path):
    from claude_bootstrap.install import install_profile_assets

    templates = REPO_ROOT / "claude_bootstrap" / "templates"
    actions = install_profile_assets(
        "backend", templates, tmp_project, force=False, check=False, multi=True, stack_dirs=["services/api"]
    )
    files = {f for f, _ in actions}
    # B3: static app/CLAUDE.md is SUPPRESSED in multi mode
    assert "app/CLAUDE.md" not in files
    assert not (tmp_project / "app" / "CLAUDE.md").exists()
    # D05: the rule is dir-scoped to the discovered dir, not extension-scoped
    rule = (tmp_project / ".claude" / "rules" / "backend.md").read_text()
    assert '"services/api/**"' in rule
    assert "**/*.py" not in rule


def test_install_profile_assets_single_still_emits_static_subdir(tmp_project: Path):
    """Single-profile (multi=False, default) keeps the static subdir-example — byte-identical path."""
    from claude_bootstrap.install import install_profile_assets

    templates = REPO_ROOT / "claude_bootstrap" / "templates"
    actions = install_profile_assets("backend", templates, tmp_project, force=False, check=False)
    files = {f for f, _ in actions}
    assert "app/CLAUDE.md" in files  # static subdir-example still emitted in single mode


# --- D06: install union emit (Model A: settings union, rules dir-scoped, manifest profiles[]) ---


def test_multi_profile_union_emit(tmp_project: Path):
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_MULTI, "--target", str(tmp_project)])
    assert rc == 0
    settings = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    allow, deny = settings["permissions"]["allow"], settings["permissions"]["deny"]
    # Union of all three profiles' permissions
    assert "Bash(pip install *)" in deny  # backend deny
    assert "Bash(terraform destroy *)" in deny  # devops deny
    assert "Bash(npm run *)" in allow  # frontend allow
    assert "Bash(terraform plan *)" in allow  # devops allow
    # Rules dir-scoped from stack_paths (D05 fill in the union path)
    assert '"services/api/**"' in (tmp_project / ".claude" / "rules" / "backend.md").read_text()
    assert '"apps/web/**"' in (tmp_project / ".claude" / "rules" / "frontend.md").read_text()
    assert '"infra/**"' in (tmp_project / ".claude" / "rules" / "infrastructure.md").read_text()
    # Manifest carries the sorted set + a back-compat scalar
    manifest = json.loads((tmp_project / ".claude" / ".bootstrap-manifest.json").read_text())
    assert manifest["profiles"] == ["backend", "devops", "frontend"]
    assert manifest["profile"] == "backend"


def test_multi_profile_union_idempotent(tmp_project: Path):
    args = ["--vars-json", VARS_MULTI, "--target", str(tmp_project)]
    run_python("install.py", args)
    rc, stdout, _ = run_python("install.py", args)
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    # Every content file is unchanged on re-run (byte-stable union)
    for f, s in statuses.items():
        if f == ".gitignore":
            assert s == "unchanged"
        else:
            assert s in ("unchanged", "exists-skipped"), (f, s)


def test_multi_profile_union_uninstall_pristine(tmp_project: Path):
    run_python("install.py", ["--vars-json", VARS_MULTI, "--target", str(tmp_project)])
    assert (tmp_project / ".claude").exists()
    assert (tmp_project / "services" / "api" / "CLAUDE.md").exists()  # per-subdir emitted
    rc, _stdout, _ = run_python("uninstall.py", ["--target", str(tmp_project)])
    assert rc == 0
    # Every union file reversed — host pristine (incl. the per-subdir layer + pruned dirs)
    assert not (tmp_project / ".claude").exists()
    assert not (tmp_project / "CLAUDE.md").exists()
    assert not (tmp_project / "PROJECT-STATE.md").exists()
    assert not (tmp_project / "services" / "api" / "CLAUDE.md").exists()
    assert not (tmp_project / "apps" / "web" / "CLAUDE.md").exists()
    assert not (tmp_project / "services").exists()  # emptied dir pruned
    assert not (tmp_project / "apps").exists()


def _fake_profile_with_skill(templates_root: Path, name: str, skill: str, body: str) -> None:
    pdir = templates_root / "profiles" / name
    (pdir / "skills" / skill).mkdir(parents=True)
    (pdir / "skills" / skill / "SKILL.md").write_text(body)
    (pdir / "profile.yaml").write_text(f"name: {name}\nskills:\n  - {skill}\n")


def test_warn_skill_collisions_surfaces_differing_same_name(tmp_path: Path, capsys):
    """D06/SP-I positive branch: a same-name skill bundled by 2 profiles with DIFFERING content
    emits a warning (not silent first-write-wins)."""
    from claude_bootstrap.install import _warn_skill_collisions

    tr = tmp_path / "templates"
    _fake_profile_with_skill(tr, "aprof", "shared", "AAA content")
    _fake_profile_with_skill(tr, "bprof", "shared", "BBB different")
    loaded = [("aprof", {"skills": ["shared"]}), ("bprof", {"skills": ["shared"]})]
    _warn_skill_collisions(loaded, tr)
    err = capsys.readouterr().err
    assert "shared" in err and "differing" in err.lower()


def test_warn_skill_collisions_silent_when_identical(tmp_path: Path, capsys):
    """An identical same-name skill dedupes silently — no warning."""
    from claude_bootstrap.install import _warn_skill_collisions

    tr = tmp_path / "templates"
    _fake_profile_with_skill(tr, "aprof", "shared", "SAME")
    _fake_profile_with_skill(tr, "bprof", "shared", "SAME")
    loaded = [("aprof", {"skills": ["shared"]}), ("bprof", {"skills": ["shared"]})]
    _warn_skill_collisions(loaded, tr)
    assert "differing" not in capsys.readouterr().err.lower()


# --- D10: legacy single-profile back-compat + no migration churn -------------------------------


def test_single_profile_manifest_has_no_profiles_key(tmp_project: Path):
    """Single-profile install writes only the scalar `profile` — no `profiles` key (byte-stable,
    no spurious migration churn under the new union-aware manifest builder)."""
    run_python("install.py", ["--vars-json", VARS_FRONTEND, "--target", str(tmp_project)])
    manifest = json.loads((tmp_project / ".claude" / ".bootstrap-manifest.json").read_text())
    assert manifest["profile"] == "frontend"
    assert "profiles" not in manifest


def test_legacy_scalar_manifest_uninstalls_clean(tmp_project: Path):
    """A single-profile install (scalar `profile`, no `profiles`) reverses cleanly + re-run stable."""
    run_python("install.py", ["--vars-json", VARS_FRONTEND, "--target", str(tmp_project)])
    # idempotent re-run — no churn from the union-aware code paths
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_FRONTEND, "--target", str(tmp_project)])
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses["CLAUDE.md"] in ("unchanged", "exists-skipped")
    # manifest-driven uninstall reverses the whole single-profile install
    rc, _, _ = run_python("uninstall.py", ["--target", str(tmp_project)])
    assert rc == 0
    assert not (tmp_project / ".claude").exists()
    assert not (tmp_project / "CLAUDE.md").exists()


# --- D07: per-subdir CLAUDE.md layer (dynamic names, root-filtered, no stale leakage) ----------


def test_multi_profile_per_subdir_claude(tmp_project: Path):
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_MULTI, "--target", str(tmp_project)])
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    # Dynamic per-subdir CLAUDE.md at each discovered dir (nested paths OK)
    assert statuses.get("services/api/CLAUDE.md") == "created"
    assert statuses.get("apps/web/CLAUDE.md") == "created"
    assert statuses.get("infra/CLAUDE.md") == "created"
    be = (tmp_project / "services" / "api" / "CLAUDE.md").read_text()
    # SP-T: re-headed for the dir, no stale example-subdir leakage, correct read-trigger phrasing
    assert "`services/api/`" in be
    assert "`app/`" not in be  # backend's static example subdir was app/
    assert "files under `services/api/`" in be
    assert "cd " not in be and "navigate to" not in be.lower()
    fe = (tmp_project / "apps" / "web" / "CLAUDE.md").read_text()
    assert "`apps/web/`" in fe and "`src/`" not in fe
    # B3: static subdir-examples suppressed in multi (no misplaced app/ or src/ at conventional names)
    assert not (tmp_project / "app" / "CLAUDE.md").exists()
    assert not (tmp_project / "src" / "CLAUDE.md").exists()
    # SP-Y: root CLAUDE.md is the union file, NOT a thin per-subdir body
    assert not (tmp_project / "CLAUDE.md").read_text().lstrip().startswith("# CLAUDE.md — `")
    # Manifest tracks each per-subdir file
    manifest = json.loads((tmp_project / ".claude" / ".bootstrap-manifest.json").read_text())
    paths = {f["path"] for f in manifest["files"]}
    assert {"services/api/CLAUDE.md", "apps/web/CLAUDE.md", "infra/CLAUDE.md"} <= paths


def test_per_subdir_root_dir_is_filtered(tmp_project: Path):
    """SP-Y hard stop: a stack_paths entry of '.' must NEVER write over the root union CLAUDE.md."""
    v = json.loads(VARS_MULTI)
    v["stack_paths"] = {"backend": ["."], "frontend": ["apps/web"], "devops": ["infra"]}
    rc, stdout, _ = run_python("install.py", ["--vars-json", json.dumps(v), "--target", str(tmp_project)])
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert "./CLAUDE.md" not in statuses  # root dir filtered → no per-subdir write there
    # root stays the union template, not a subdir body
    assert not (tmp_project / "CLAUDE.md").read_text().lstrip().startswith("# CLAUDE.md — `")


def test_per_subdir_root_dir_is_filtered_under_force(tmp_project: Path):
    """Under --force the root guard is the ONLY protection (create-only would overwrite)."""
    run_python("install.py", ["--vars-json", VARS_MULTI, "--target", str(tmp_project)])
    root_before = (tmp_project / "CLAUDE.md").read_text()
    v = json.loads(VARS_MULTI)
    v["stack_paths"] = {"backend": ["./"], "frontend": ["apps/web"], "devops": ["infra"]}
    rc, _, _ = run_python(
        "install.py", ["--vars-json", json.dumps(v), "--target", str(tmp_project), "--force"]
    )
    assert rc == 0
    # root union CLAUDE.md not clobbered by a './' backend subdir body
    assert (tmp_project / "CLAUDE.md").read_text() == root_before


def test_per_subdir_rejects_parent_escape_under_force(tmp_path: Path):
    """SP-Y (independent validator): a `..`-overshoot value (`a/../..`) must NEVER write/overwrite
    an ANCESTOR's CLAUDE.md, even under --force. Reproduces the validator's escape."""
    parent = tmp_path / "parent"
    target = parent / "child"
    target.mkdir(parents=True)
    (parent / "CLAUDE.md").write_text("PARENT USER FILE - do not touch\n")
    v = json.loads(VARS_MULTI)
    v["stack_paths"] = {"backend": ["a/../.."], "frontend": ["apps/web"], "devops": ["infra"]}
    rc, stdout, _ = run_python(
        "install.py", ["--vars-json", json.dumps(v), "--target", str(target), "--force"]
    )
    assert rc == 0
    assert (parent / "CLAUDE.md").read_text() == "PARENT USER FILE - do not touch\n"
    files = {a["file"] for a in json.loads(stdout)["actions"]}
    assert not any(f.startswith("..") or "/../" in f for f in files)


def test_per_subdir_rejects_absolute_escape(tmp_path: Path):
    """SP-Y: an absolute stack_paths dir OUTSIDE the target is rejected (never written)."""
    target = tmp_path / "proj"
    target.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    v = json.loads(VARS_MULTI)
    v["stack_paths"] = {"backend": [str(outside)], "frontend": ["apps/web"], "devops": ["infra"]}
    rc, _, _ = run_python("install.py", ["--vars-json", json.dumps(v), "--target", str(target), "--force"])
    assert rc == 0
    assert not (outside / "CLAUDE.md").exists()


def test_per_subdir_multi_dir_per_profile(tmp_project: Path):
    v = json.loads(VARS_MULTI)
    v["stack_paths"] = {
        "frontend": ["apps/web", "apps/admin"],
        "backend": ["services/api"],
        "devops": ["infra"],
    }
    rc, stdout, _ = run_python("install.py", ["--vars-json", json.dumps(v), "--target", str(tmp_project)])
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses.get("apps/web/CLAUDE.md") == "created"
    assert statuses.get("apps/admin/CLAUDE.md") == "created"


def test_per_subdir_preserves_pre_existing_user_file(tmp_project: Path):
    (tmp_project / "services" / "api").mkdir(parents=True)
    (tmp_project / "services" / "api" / "CLAUDE.md").write_text("MY OWN FILE\n")
    run_python("install.py", ["--vars-json", VARS_MULTI, "--target", str(tmp_project)])
    assert (tmp_project / "services" / "api" / "CLAUDE.md").read_text() == "MY OWN FILE\n"


def test_init_creates_artifacts(tmp_project: Path):
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    assert (tmp_project / "CLAUDE.md").exists()
    assert (tmp_project / "PROJECT-STATE.md").exists()
    assert (tmp_project / ".claude" / "settings.json").exists()
    assert (tmp_project / ".gitignore").exists()


def test_init_idempotent(tmp_project: Path):
    args = ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)]
    run_python("install.py", args)
    rc, stdout, _ = run_python("install.py", args)
    assert rc == 0
    data = json.loads(stdout)
    statuses = {a["file"]: a["status"] for a in data["actions"]}
    assert statuses["CLAUDE.md"] in ("exists-skipped", "unchanged")
    assert statuses["PROJECT-STATE.md"] in ("exists-skipped", "unchanged")
    assert statuses[".claude/settings.json"] in ("exists-skipped", "unchanged")
    assert statuses[".gitignore"] in ("unchanged",)


def test_init_with_academic_profile(tmp_project: Path):
    """v0.4.0a0 academic profile — 3 skills (K-Dense MIT).

    Was 7: docx/pdf/pptx/doc-coauthoring were de-bundled 2026-07-26 — none carries a licence
    permitting redistribution (see templates/profiles/academic/NOTICE.md)."""
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_ACADEMIC_NEW, "--target", str(tmp_project)])
    assert rc == 0
    data = json.loads(stdout)
    statuses = {a["file"]: a["status"] for a in data["actions"]}
    skill_dirs = {f.split("/")[2] for f in statuses if f.startswith(".claude/skills/")}
    assert len(skill_dirs) == 3, f"expected 3 skills, got {skill_dirs}"
    assert not (skill_dirs & {"docx", "pdf", "pptx", "doc-coauthoring"}), "de-bundled skill reappeared"
    # Ships manuscript/CLAUDE.md subdir example
    assert statuses.get("manuscript/CLAUDE.md") == "created"
    # Academic permissions merged
    settings = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    assert "Bash(pandoc *)" in settings["permissions"]["allow"]
    assert "Bash(latexmk *)" in settings["permissions"]["allow"]


def test_settings_overrides_noop_for_universal(tmp_project: Path):
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    settings = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    # universal-software has empty settings_overrides → env stays empty
    assert settings["env"] == {}


def test_init_check_dry_run(tmp_project: Path):
    rc, stdout, _ = run_python(
        "install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project), "--check"]
    )
    assert rc == 0
    assert not (tmp_project / "CLAUDE.md").exists()
    assert not (tmp_project / "PROJECT-STATE.md").exists()


def test_update_writes_new_for_diverged_file(tmp_project: Path):
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    claude_md = tmp_project / "CLAUDE.md"
    claude_md.write_text(claude_md.read_text() + "\n# user appended this\n")
    rc, stdout, _ = run_python(
        "install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project), "--update"]
    )
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses["CLAUDE.md"] == "diverged (.new)"
    assert (tmp_project / "CLAUDE.md.new").exists()
    # original preserved (still has user edit)
    assert "user appended this" in claude_md.read_text()


def test_invalid_json_vars_exits_gracefully(tmp_project: Path):
    rc, _, stderr = run_python("install.py", ["--vars-json", "{not valid json", "--target", str(tmp_project)])
    assert rc == 2
    assert "invalid JSON" in stderr


def test_invalid_yaml_profile_exits_gracefully(tmp_project: Path, tmp_path: Path):
    bad_templates = tmp_path / "templates"
    base = bad_templates / "_base"
    base.mkdir(parents=True)
    (base / "CLAUDE.md.j2").write_text("hi")
    (base / "PROJECT-STATE.md.j2").write_text("hi")
    (base / ".gitignore").write_text("")
    (base / ".claude").mkdir()
    (base / ".claude" / "settings.json").write_text('{"a": 1}')
    bad_profile_dir = bad_templates / "profiles" / "broken"
    bad_profile_dir.mkdir(parents=True)
    (bad_profile_dir / "profile.yaml").write_text(": :: not valid yaml :: :")
    vars_json = json.dumps({**json.loads(VARS_UNIVERSAL), "profile_name": "broken"})
    rc, _, stderr = run_python(
        "install.py",
        ["--vars-json", vars_json, "--target", str(tmp_project), "--templates-dir", str(bad_templates)],
    )
    assert rc == 2
    assert "invalid YAML" in stderr


def test_readonly_target_exits_gracefully(tmp_project: Path):
    import os
    import stat

    (tmp_project / "CLAUDE.md").write_text("existing")
    os.chmod(tmp_project, stat.S_IREAD | stat.S_IEXEC)
    try:
        rc, _, stderr = run_python(
            "install.py",
            ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project), "--force"],
        )
    finally:
        os.chmod(tmp_project, stat.S_IRWXU)
    assert rc == 1
    assert "cannot write" in stderr or "Permission" in stderr


def test_init_with_devops_profile(tmp_project: Path):
    """Devops profile ships 5 real skills + infra/CLAUDE.md (subdir example)."""
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_DEVOPS, "--target", str(tmp_project)])
    assert rc == 0
    data = json.loads(stdout)
    statuses = {a["file"]: a["status"] for a in data["actions"]}
    skill_dirs = {f.split("/")[2] for f in statuses if f.startswith(".claude/skills/")}
    assert len(skill_dirs) == 5, (
        f"expected 5 skills (senior-devops + release-manager de-bundled), got {skill_dirs}"
    )
    assert statuses.get("infra/CLAUDE.md") == "created"
    settings = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    # Read/plan allowed
    assert "Bash(terraform plan *)" in settings["permissions"]["allow"]
    assert "Bash(kubectl get *)" in settings["permissions"]["allow"]
    # Destructive denied
    assert "Bash(terraform destroy *)" in settings["permissions"]["deny"]
    assert "Bash(kubectl delete *)" in settings["permissions"]["deny"]


def test_init_with_data_science_profile(tmp_project: Path):
    """Data-science profile ships 6 real skills + notebooks/CLAUDE.md (subdir example)."""
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_DATA_SCIENCE, "--target", str(tmp_project)])
    assert rc == 0
    data = json.loads(stdout)
    statuses = {a["file"]: a["status"] for a in data["actions"]}
    skill_dirs = {f.split("/")[2] for f in statuses if f.startswith(".claude/skills/")}
    assert len(skill_dirs) == 6, f"expected 6 skills (xlsx de-bundled), got {skill_dirs}"
    assert statuses.get("notebooks/CLAUDE.md") == "created"
    settings = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    assert "Bash(jupyter *)" in settings["permissions"]["allow"]
    assert "Bash(uv run *)" in settings["permissions"]["allow"]


def test_init_with_frontend_profile(tmp_project: Path):
    """Frontend profile ships 7 real skills + src/CLAUDE.md (subdir example)."""
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_FRONTEND, "--target", str(tmp_project)])
    assert rc == 0
    data = json.loads(stdout)
    statuses = {a["file"]: a["status"] for a in data["actions"]}
    # Each of the 7 skills installs at least 1 file (SKILL.md); theme-factory de-bundled (frente-2)
    skill_files = [f for f in statuses if f.startswith(".claude/skills/")]
    assert len({f.split("/")[2] for f in skill_files}) == 7, f"expected 7 skills, got {skill_files}"
    # frontend ships src/CLAUDE.md (subdir example from H6)
    assert statuses.get("src/CLAUDE.md") == "created"
    # Profile permissions merged
    settings = json.loads((tmp_project / ".claude" / "settings.json").read_text())
    assert "Bash(npm run *)" in settings["permissions"]["allow"]
    assert "Bash(playwright test *)" in settings["permissions"]["allow"]


def test_install_creates_subdir_examples_when_profile_has_them(tmp_project: Path):
    """When a profile ships subdir-examples/<subdir>-CLAUDE.md, install creates target/<subdir>/CLAUDE.md."""
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses.get("scripts/CLAUDE.md") == "created"
    subdir_claude = tmp_project / "scripts" / "CLAUDE.md"
    assert subdir_claude.exists()
    content = subdir_claude.read_text()
    assert "subdirectory `CLAUDE.md` mechanism" in content


def test_install_reports_not_found_for_unknown_profile(tmp_project: Path):
    """An unresolvable profile name is reported as an action, not silently ignored."""
    bad_vars = json.dumps({**json.loads(VARS_UNIVERSAL), "profile_name": "no-such-profile"})
    rc, stdout, _ = run_python("install.py", ["--vars-json", bad_vars, "--target", str(tmp_project)])
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses.get("profile/no-such-profile") == "not-found"


def test_install_skips_subdir_examples_when_profile_lacks_them(tmp_path: Path):
    """A profile that RESOLVES but ships no subdir-examples/ creates no <subdir>/CLAUDE.md.

    Needs a synthesized templates tree: every shipped profile has the dir, so pointing at a
    real one never reaches the `subdir_examples_dir.is_dir()` guard, and pointing at an
    unresolved name returns before it.
    """
    target = tmp_path / "proj"
    target.mkdir()
    templates = tmp_path / "templates"
    src = REPO_ROOT / "claude_bootstrap" / "templates"
    shutil.copytree(src / "_base", templates / "_base")
    shutil.copytree(src / "profiles" / "universal-software", templates / "profiles" / "universal-software")
    shutil.rmtree(templates / "profiles" / "universal-software" / "subdir-examples")

    rc, stdout, _ = run_python(
        "install.py",
        ["--vars-json", VARS_UNIVERSAL, "--target", str(target), "--templates-dir", str(templates)],
    )
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses.get("profile/universal-software") != "not-found"
    subdir_files = [f for f in statuses if f.endswith("/CLAUDE.md") and not f.startswith(".claude/")]
    assert subdir_files == []


MANIFEST_REL = ".claude/.bootstrap-manifest.json"


def test_install_writes_manifest(tmp_project: Path):
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    manifest_path = tmp_project / ".claude" / ".bootstrap-manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["profile"] == "universal-software"
    assert manifest["version"]  # non-empty
    # files list records the create-only roots with sha256
    paths = {f["path"]: f["sha256"] for f in manifest["files"]}
    assert "CLAUDE.md" in paths
    assert ".claude/settings.json" in paths
    # sha256 matches the file actually on disk
    actual = hashlib.sha256((tmp_project / "CLAUDE.md").read_bytes()).hexdigest()
    assert paths["CLAUDE.md"] == actual
    # the manifest does not list itself
    assert MANIFEST_REL not in paths
    # gitignore tracked separately (managed lines), not in files
    assert isinstance(manifest["gitignore_added"], list)
    assert ".gitignore" not in paths


def test_manifest_idempotent(tmp_project: Path):
    args = ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)]
    run_python("install.py", args)
    first = (tmp_project / ".claude" / ".bootstrap-manifest.json").read_text()
    rc, stdout, _ = run_python("install.py", args)
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses[MANIFEST_REL] == "unchanged"
    second = (tmp_project / ".claude" / ".bootstrap-manifest.json").read_text()
    assert first == second  # byte-identical across runs


def test_check_writes_no_manifest(tmp_project: Path):
    rc, _, _ = run_python(
        "install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project), "--check"]
    )
    assert rc == 0
    assert not (tmp_project / ".claude" / ".bootstrap-manifest.json").exists()


def test_update_tracks_new_files_and_keeps_original_in_manifest(tmp_project: Path):
    """Update that diverges must track `<path>.new` (Bug 3) AND keep the original (Bug 2)."""
    base = json.loads(VARS_UNIVERSAL)
    a = json.dumps({**base, "project_name": "alpha-proj"})
    b = json.dumps({**base, "project_name": "beta-proj"})  # different → CLAUDE.md diverges
    run_python("install.py", ["--vars-json", a, "--target", str(tmp_project)])
    run_python("install.py", ["--vars-json", b, "--target", str(tmp_project), "--update"])
    assert (tmp_project / "CLAUDE.md.new").exists()
    manifest = json.loads((tmp_project / ".claude" / ".bootstrap-manifest.json").read_text())
    paths = {f["path"] for f in manifest["files"]}
    assert "CLAUDE.md.new" in paths, "the .new file must be tracked (Bug 3)"
    assert "CLAUDE.md" in paths, "the original must stay tracked across update divergence (Bug 2)"


def test_update_unchanged_when_no_drift(tmp_project: Path):
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    rc, stdout, _ = run_python(
        "install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project), "--update"]
    )
    assert rc == 0
    statuses = {a["file"]: a["status"] for a in json.loads(stdout)["actions"]}
    assert statuses["CLAUDE.md"] == "unchanged"
    assert statuses["PROJECT-STATE.md"] == "unchanged"
    assert statuses[".claude/settings.json"] == "unchanged"
    assert not (tmp_project / "CLAUDE.md.new").exists()


def test_install_skips_compiled_bytecode(tmp_path: Path):
    """pip byte-compiles bundled skill `.py` into `__pycache__/*.pyc` on install; the asset
    copy must skip those binaries, not `read_text()` them as UTF-8. Gate finding 2026-06-05:
    `init` crashed with UnicodeDecodeError from the pip-installed wheel (not the uv-tool path)."""
    from claude_bootstrap.install import install_profile_assets

    templates = tmp_path / "templates"
    prof = templates / "profiles" / "demo"
    skill = prof / "skills" / "demoskill"
    (skill / "__pycache__").mkdir(parents=True)
    prof.joinpath("profile.yaml").write_text("name: demo\nskills:\n  - demoskill\nrules: []\n")
    skill.joinpath("SKILL.md").write_text("# demo skill\n")
    skill.joinpath("helper.py").write_text("x = 1\n")
    # a real .pyc: 16-byte header with the 0xdb byte that crashed the wheel install
    (skill / "__pycache__" / "helper.cpython-314.pyc").write_bytes(
        b"\xa7\r\r\n\x00\x00\x00\x00\xdb\x00\x00\x00\x00\x00\x00\x00binary-bytecode"
    )

    target = tmp_path / "proj"
    target.mkdir()
    actions = install_profile_assets("demo", templates, target, force=False, check=False)

    # must not raise; the source files emit; the compiled bytecode is skipped
    assert (target / ".claude" / "skills" / "demoskill" / "SKILL.md").exists()
    assert (target / ".claude" / "skills" / "demoskill" / "helper.py").exists()
    assert not (target / ".claude" / "skills" / "demoskill" / "__pycache__").exists()
    assert not any("__pycache__" in a[0] or a[0].endswith(".pyc") for a in actions)


def test_claude_md_omits_empty_description(tmp_path: Path):
    """Frente-2 finding: --non-interactive shipped a `> (no description)` placeholder in CLAUDE.md.
    The blockquote must render only when a real description exists."""
    from claude_bootstrap.install import render_jinja

    tpl = Path("claude_bootstrap/templates/_base/CLAUDE.md.j2")
    base = dict(
        project_name="x",
        primary_language="python",
        is_monorepo=False,
        git_remote=None,
        profile_name="universal-software",
        superpowers_available=False,
        agentic_stack_interop=False,
        extra_rules=[],
        generated_at="2026-01-01",
        bootstrap_version="0.4.0a0",
    )
    empty = render_jinja(tpl, {**base, "project_description": ""})
    assert "(no description)" not in empty
    assert not any(line.strip() == ">" for line in empty.splitlines()), "empty blockquote leaked"

    filled = render_jinja(tpl, {**base, "project_description": "A real description"})
    assert "> A real description" in filled


def test_devops_hardens_iac_destructive_ops(tmp_project: Path):
    """Frente-2 A: devops deny must cover IaC-specific destruction (tfstate/tfvars exfil,
    terraform state surgery, docker prune/volume rm); allow must include `terraform init`."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_DEVOPS, "--target", str(tmp_project)])
    assert rc == 0
    perms = json.loads((tmp_project / ".claude" / "settings.json").read_text())["permissions"]
    for d in [
        "Read(**/*.tfstate)",
        "Read(**/*.tfvars)",
        "Bash(terraform state rm *)",
        "Bash(terraform import *)",
        "Bash(terraform taint *)",
        "Bash(docker system prune *)",
        "Bash(docker volume rm *)",
    ]:
        assert d in perms["deny"], f"missing deny: {d}"
    assert "Bash(terraform init *)" in perms["allow"]


def test_gitignore_includes_ml_artifacts(tmp_project: Path):
    """Frente-2 B: the emitted .gitignore enables jupyter/mlflow workflows but ignored no ML
    artifacts, so mlruns/ and checkpoints would get committed. The base must cover them."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    gi = (tmp_project / ".gitignore").read_text()
    for pat in [".ipynb_checkpoints/", "mlruns/", "wandb/", "*.pkl", "*.pt", "*.ckpt"]:
        assert pat in gi, f"missing gitignore pattern: {pat}"


def test_profiles_emit_path_scoped_rules(tmp_project: Path):
    """Frente-2 E: code profiles must ship path-scoped rules (`.claude/rules/<x>.md` with valid
    `paths:` frontmatter), not an empty rules/ dir — the biggest miss the audit found for IaC."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_DEVOPS, "--target", str(tmp_project)])
    assert rc == 0
    rule = tmp_project / ".claude" / "rules" / "infrastructure.md"
    assert rule.is_file(), "devops should emit a path-scoped infra rule"
    txt = rule.read_text()
    assert txt.startswith("---") and "paths:" in txt and "*.tf" in txt and "tfstate" in txt


def test_frontend_emits_path_scoped_rule(tmp_project: Path):
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_FRONTEND, "--target", str(tmp_project)])
    assert rc == 0
    rule = tmp_project / ".claude" / "rules" / "frontend.md"
    assert rule.is_file()
    assert "paths:" in rule.read_text() and "*.tsx" in rule.read_text()


def test_debundled_skills_absent(tmp_project: Path):
    """Frente-2 D: senior-devops (misleading copy-paste stubs) dropped from devops;
    xlsx (financial-modeling misfit) dropped from data-science."""
    import json as _j

    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_DEVOPS, "--target", str(tmp_project)])
    assert rc == 0
    devops_files = {a["file"] for a in _j.loads(stdout)["actions"]}
    assert not any("/skills/senior-devops/" in f for f in devops_files), "senior-devops not de-bundled"

    ds_vars = _j.loads(VARS_UNIVERSAL)
    ds_vars["profile_name"] = "data-science"
    rc2, stdout2, _ = run_python(
        "install.py", ["--vars-json", _j.dumps(ds_vars), "--target", str(tmp_project / "ds"), "--force"]
    )
    assert rc2 == 0
    ds_files = {a["file"] for a in _j.loads(stdout2)["actions"]}
    assert not any("/skills/xlsx/" in f for f in ds_files), "xlsx not de-bundled"


def test_base_denies_env_recursively(tmp_project: Path):
    """Frente-2 FE-4: the .env Read-deny was root-anchored (`./.env`) while credential denies were
    recursive — a monorepo `packages/app/.env` slipped through. Make it recursive."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    deny = json.loads((tmp_project / ".claude" / "settings.json").read_text())["permissions"]["deny"]
    assert "Read(**/.env)" in deny and "Read(**/.env.*)" in deny


def test_academic_emits_latex_rule(tmp_project: Path):
    """Frente-2 AC-1: academic guidance was mis-scoped to manuscript/; ship a path-scoped latex rule."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_ACADEMIC_NEW, "--target", str(tmp_project)])
    assert rc == 0
    rule = tmp_project / ".claude" / "rules" / "latex.md"
    assert rule.is_file()
    txt = rule.read_text()
    assert "paths:" in txt and "*.tex" in txt and "*.bib" in txt


def test_gitignore_includes_latex_artifacts(tmp_project: Path):
    """Frente-2 AC-2: LaTeX build artifacts polluted git status the moment latexmk ran."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    gi = (tmp_project / ".gitignore").read_text()
    for p in ["*.aux", "*.bbl", "*.synctex.gz", "*.fdb_latexmk"]:
        assert p in gi, f"missing latex ignore: {p}"


def test_frontend_rule_covers_vue_svelte_astro(tmp_project: Path):
    """Frente-2 FE-5: the rule glob omitted frameworks the senior-frontend skill itself supports."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_FRONTEND, "--target", str(tmp_project)])
    assert rc == 0
    rule = (tmp_project / ".claude" / "rules" / "frontend.md").read_text()
    assert "*.vue" in rule and "*.svelte" in rule and "*.astro" in rule


def test_theme_factory_debundled_from_frontend(tmp_project: Path):
    """Frente-2 FE-2: theme-factory is a slide-deck theming misfit + references an unshipped PDF."""
    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_FRONTEND, "--target", str(tmp_project)])
    assert rc == 0
    files = {a["file"] for a in json.loads(stdout)["actions"]}
    assert not any("/skills/theme-factory/" in f for f in files), "theme-factory not de-bundled"


def test_profiles_emit_subagents(tmp_project: Path):
    """SOTA D05: code profiles ship a path-scoped subagent in .claude/agents/<name>.md."""
    import yaml as _yaml

    rc, stdout, _ = run_python("install.py", ["--vars-json", VARS_DEVOPS, "--target", str(tmp_project)])
    assert rc == 0
    agent = tmp_project / ".claude" / "agents" / "terraform-plan-reviewer.md"
    assert agent.is_file(), "devops should emit a subagent"
    fm = _yaml.safe_load(agent.read_text().split("---", 2)[1])
    assert fm["name"] == "terraform-plan-reviewer" and fm["description"]
    # descriptive, not auto-spawn routing language
    assert "must be used" not in fm["description"].lower()


def test_mcp_example_emitted_off_by_default(tmp_project: Path):
    """SOTA D06: emit a `.mcp.json.example` (opt-in template), never an active `.mcp.json`."""
    rc, _, _ = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    assert rc == 0
    ex = tmp_project / ".mcp.json.example"
    assert ex.is_file(), ".mcp.json.example should be emitted"
    assert "mcpServers" in json.loads(ex.read_text())
    assert not (tmp_project / ".mcp.json").exists(), "must NOT emit an active .mcp.json"
