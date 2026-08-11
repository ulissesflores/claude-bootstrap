#!/usr/bin/env python3
"""Render Jinja templates + install files into a target project (idempotent).

Semantics:
- create-only for CLAUDE.md, PROJECT-STATE.md, .claude/settings.json (preserves user edits on re-run; --force overrides)
- soft-merge for .gitignore (appends only template lines not already present; re-run = no-op)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

from . import __version__

VERSION = __version__


def render_jinja(tpl_path: Path, vars_dict: dict) -> str:
    try:
        import jinja2
    except ImportError:
        sys.stderr.write(
            "ERROR: jinja2 not installed. Install with: pip install jinja2\n"
            "       (or run via uv: uv run --with jinja2 --no-project python3 ...)\n"
        )
        sys.exit(3)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(tpl_path.parent)),
        keep_trailing_newline=True,
    )
    return env.get_template(tpl_path.name).render(**vars_dict)


def _safe_write(path: Path, content: str, *, mkdir: bool = False) -> None:
    """Write text to path, raising clear OSError-derived message on failure."""
    try:
        if mkdir:
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    except OSError as e:
        sys.stderr.write(f"ERROR: cannot write {path}: {e}\n")
        sys.exit(1)


def _safe_read(path: Path) -> str:
    try:
        return path.read_text()
    except OSError as e:
        sys.stderr.write(f"ERROR: cannot read {path}: {e}\n")
        sys.exit(1)


def install_create_only(
    target_path: Path, content: str, *, force: bool, check: bool, update: bool = False
) -> str:
    """Write content to target_path.

    Modes:
    - default (init): create-only; existing diverged file → 'exists-skipped'.
    - update=True: existing diverged file → write '<path>.new', return 'diverged (.new)'.
    - force=True: always overwrite (wins over update).

    Returns one of: created | exists-skipped | overwritten | unchanged
    | diverged (.new) | would-create | would-overwrite | would-write-new
    """
    if check:
        if target_path.exists():
            existing = _safe_read(target_path)
            if existing == content:
                return "unchanged"
            if force:
                return "would-overwrite"
            if update:
                return "would-write-new"
            return "exists-skipped"
        return "would-create"

    if target_path.exists():
        existing = _safe_read(target_path)
        if existing == content:
            return "unchanged"
        if force:
            _safe_write(target_path, content)
            return "overwritten"
        if update:
            new_path = target_path.with_suffix(target_path.suffix + ".new")
            _safe_write(new_path, content)
            return "diverged (.new)"
        return "exists-skipped"

    _safe_write(target_path, content, mkdir=True)
    return "created"


GITIGNORE_MARKER = "# --- Added by claude-bootstrap ---"


def install_gitignore(
    template_path: Path, target_path: Path, *, force: bool, check: bool
) -> tuple[str, list[str]]:
    """Soft-merge .gitignore: append template lines not already present.

    Returns (status, managed_lines) where managed_lines is the deterministic set
    of non-comment template lines this tool owns (used by the uninstall manifest;
    independent of whether this run actually appended them).
    status is one of: created | merged | unchanged | would-create | would-merge
    """
    template_text = _safe_read(template_path)
    template_lines = template_text.splitlines()
    managed_lines = [line for line in template_lines if line.strip() and not line.strip().startswith("#")]

    if not target_path.exists():
        if check:
            return "would-create", managed_lines
        _safe_write(target_path, template_text, mkdir=True)
        return "created", managed_lines

    existing = _safe_read(target_path).splitlines()
    existing_set = {line.strip() for line in existing if line.strip() and not line.strip().startswith("#")}

    new_lines = []
    for line in template_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped not in existing_set:
            new_lines.append(line)

    if not new_lines:
        return "unchanged", managed_lines

    if check:
        return f"would-merge ({len(new_lines)} lines)", managed_lines

    # Always one separator newline before the marker, so uninstall can byte-restore
    # the original by dropping exactly that newline + the block (fire-test Bug 6b).
    addendum = "\n" + GITIGNORE_MARKER + "\n" + "\n".join(new_lines) + "\n"
    try:
        with target_path.open("a") as f:
            f.write(addendum)
    except OSError as e:
        sys.stderr.write(f"ERROR: cannot append to {target_path}: {e}\n")
        sys.exit(1)
    return f"merged ({len(new_lines)} lines)", managed_lines


MANIFEST_REL = ".claude/.bootstrap-manifest.json"
# Statuses that mean "this file is ours to track (and later remove)".
_OWNED_STATUSES = {"created", "overwritten", "unchanged"}


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest_content(
    target: Path,
    actions: list[tuple[str, str]],
    gitignore_managed: list[str],
    prior_files: dict[str, str],
    *,
    version: str,
    profile_name: str | None,
    profiles: list | None = None,
) -> str:
    """Render the uninstall manifest as deterministic JSON.

    Records every owned file's sha256, plus the `<path>.new` files written on
    update. Carries forward prior-manifest entries still on disk so an `update`
    that sees a file *diverged* doesn't drop it from tracking — uninstall's
    sha-check still protects genuine user edits (mismatch → kept). Sorted by
    path → byte-stable + idempotent (no timestamp).
    """
    files: dict[str, str] = {}
    for path, sha in (prior_files or {}).items():
        if path not in (".gitignore", MANIFEST_REL) and (target / path).exists():
            files[path] = sha
    for rel, status in actions:
        if rel in (".gitignore", MANIFEST_REL):
            continue
        if status in _OWNED_STATUSES:
            files[rel] = _sha256_path(target / rel)  # fresh, authoritative
        elif status == "diverged (.new)":
            new_rel = f"{rel}.new"
            if (target / new_rel).exists():
                files[new_rel] = _sha256_path(target / new_rel)
            # original `rel` stays via carry-forward (its original sha), not the diverged on-disk one
    manifest = {
        "version": version,
        "profile": profile_name or "universal-software",  # scalar kept for back-compat readers
        "files": [{"path": p, "sha256": files[p]} for p in sorted(files)],
        "gitignore_added": gitignore_managed,
    }
    if profiles:
        # D06: the multi-profile union records the full set; absent for single (byte-identical).
        manifest["profiles"] = list(profiles)
    return json.dumps(manifest, indent=2) + "\n"


def merge_settings_overrides(base: dict, overrides: dict) -> dict:
    """Deep-merge profile settings_overrides into base settings.

    Rules:
    - dict + dict: recurse (profile keys override or extend base keys).
    - list + list: concat base then profile, dedupe preserving order.
    - other types: profile wins.
    """
    if not overrides:
        return base
    result = dict(base)
    for key, ov in overrides.items():
        if key in result:
            bv = result[key]
            if isinstance(bv, dict) and isinstance(ov, dict):
                result[key] = merge_settings_overrides(bv, ov)
                continue
            if isinstance(bv, list) and isinstance(ov, list):
                seen: set = set()
                merged: list = []
                for item in (*bv, *ov):
                    key_ = json.dumps(item, sort_keys=True) if not isinstance(item, str) else item
                    if key_ in seen:
                        continue
                    seen.add(key_)
                    merged.append(item)
                result[key] = merged
                continue
        result[key] = ov
    return result


def _profile_dir(templates_dir: Path, profile_name: str) -> Path | None:
    """Resolve a profile name to its directory under `profiles/<name>/`."""
    candidate = templates_dir / "profiles" / profile_name
    if (candidate / "profile.yaml").exists():
        return candidate
    return None


def load_profile(profile_name: str, templates_dir: Path) -> dict | None:
    """Load `profiles/<name>/profile.yaml`. Returns None if the profile does not exist."""
    pdir = _profile_dir(templates_dir, profile_name)
    if pdir is None:
        return None
    profile_path = pdir / "profile.yaml"
    try:
        import yaml
    except ImportError:
        sys.stderr.write(
            "ERROR: pyyaml not installed (required for --profile). Install: pip install pyyaml\n"
            "       (or run via uv: uv run --with jinja2 --with pyyaml --no-project python3 ...)\n"
        )
        sys.exit(3)
    try:
        return yaml.safe_load(_safe_read(profile_path))
    except yaml.YAMLError as e:
        sys.stderr.write(f"ERROR: invalid YAML in {profile_path}: {e}\n")
        sys.exit(2)


def _fill_rule_paths(content: str, dirs: list[str]) -> str:
    """MULTI-profile only (D05): rewrite a rule's `paths:` frontmatter to dir-scoped globs derived
    from the profile's discovered concrete dirs (`<dir>/**`), so a `backend/**` rule does not bleed
    into a `ds-service/**` file. `dirs` empty → return unchanged (fall back to the static
    extension-scoped globs; never emit an empty `paths:`). Single-profile installs never call this,
    so their rules stay byte-identical.
    """
    if not dirs or not content.startswith("---"):
        return content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    try:
        import yaml

        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        fm = {}
    lines = ["---", "paths:"]
    lines += [f'  - "{d}/**"' for d in sorted(dirs)]
    lines += [f"{k}: {v}" for k, v in fm.items() if k != "paths"]
    lines.append("---")
    return "\n".join(lines) + parts[2]


def install_profile_assets(
    profile_name: str,
    templates_dir: Path,
    target: Path,
    *,
    force: bool,
    check: bool,
    update: bool = False,
    multi: bool = False,
    stack_dirs: list[str] | None = None,
) -> list[tuple[str, str]]:
    """Copy skills/, rules/, agents/, output-styles/, and subdir-examples/ from templates/profiles/<name>/.

    - skills/, rules/, agents/, output-styles/ → target/.claude/{skills,rules,agents,output-styles}/
    - subdir-examples/<subdir>-CLAUDE.md → target/<subdir>/CLAUDE.md (auto-installed
      when the profile ships them; the subdirectory CLAUDE.md mechanism, per
      code.claude.com/docs/en/memory, loads on demand and doesn't bloat root context).
    """
    profile = load_profile(profile_name, templates_dir)
    if profile is None:
        return [(f"profile/{profile_name}", "not-found")]

    profile_dir = _profile_dir(templates_dir, profile_name)
    assert profile_dir is not None  # load_profile already verified existence
    actions: list[tuple[str, str]] = []

    for skill_name in profile.get("skills") or []:
        src = profile_dir / "skills" / skill_name
        if not src.is_dir():
            actions.append((f"skill/{skill_name}", "source-missing"))
            continue
        for src_file in sorted(src.rglob("*")):
            if not src_file.is_file():
                continue
            # Skip compiled-bytecode artifacts: pip byte-compiles bundled skill `.py` into
            # `__pycache__/*.pyc` at install time; those are binary (not UTF-8) and must never
            # be read-as-text or emitted into the user's .claude/ (gate finding 2026-06-05 —
            # `init` crashed with UnicodeDecodeError from the pip-installed wheel).
            if "__pycache__" in src_file.parts or src_file.suffix in (".pyc", ".pyo"):
                continue
            rel = src_file.relative_to(profile_dir)
            dst = target / ".claude" / rel
            content = src_file.read_text(encoding="utf-8")
            status = install_create_only(dst, content, force=force, check=check, update=update)
            actions.append((f".claude/{rel}", status))

    for rule_name in profile.get("rules") or []:
        src = profile_dir / "rules" / rule_name
        if not src.is_file():
            actions.append((f"rule/{rule_name}", "source-missing"))
            continue
        dst = target / ".claude" / "rules" / rule_name
        content = src.read_text()
        if multi:
            content = _fill_rule_paths(content, stack_dirs or [])
        status = install_create_only(dst, content, force=force, check=check, update=update)
        actions.append((f".claude/rules/{rule_name}", status))

    for agent_name in profile.get("agents") or []:
        src = profile_dir / "agents" / agent_name
        if not src.is_file():
            actions.append((f"agent/{agent_name}", "source-missing"))
            continue
        dst = target / ".claude" / "agents" / agent_name
        content = src.read_text(encoding="utf-8")
        status = install_create_only(dst, content, force=force, check=check, update=update)
        actions.append((f".claude/agents/{agent_name}", status))

    for style_name in profile.get("output_styles") or []:
        src = profile_dir / "output-styles" / style_name
        if not src.is_file():
            actions.append((f"output-style/{style_name}", "source-missing"))
            continue
        dst = target / ".claude" / "output-styles" / style_name
        content = src.read_text(encoding="utf-8")
        status = install_create_only(dst, content, force=force, check=check, update=update)
        actions.append((f".claude/output-styles/{style_name}", status))

    # Static subdir-examples emit at FIXED conventional names (src/, notebooks/, …). In MULTI mode
    # they are SUPPRESSED (D07/B3): the dynamic per-subdir layer emits at the real discovered dirs
    # instead, and a static file would (a) scatter to the wrong place and (b) win under create-only.
    subdir_examples_dir = profile_dir / "subdir-examples"
    if not multi and subdir_examples_dir.is_dir():
        for src_file in sorted(subdir_examples_dir.glob("*-CLAUDE.md")):
            subdir = src_file.stem[: -len("-CLAUDE")]
            if not subdir:
                continue
            dst = target / subdir / "CLAUDE.md"
            content = src_file.read_text()
            status = install_create_only(dst, content, force=force, check=check, update=update)
            actions.append((f"{subdir}/CLAUDE.md", status))

    return actions


def _rehead_subdir_body(content: str, old_stem: str, new_dir: str) -> str:
    """Re-head a profile's subdir-example body for a discovered dir, stripping EVERY reference to
    the example subdir name (SP-T: else `apps/web/CLAUDE.md` would still say "under `src/`").
    """
    out = content.replace(f"`{old_stem}/`", f"`{new_dir}/`")
    lines = out.splitlines(keepends=True)
    if lines and lines[0].startswith("# CLAUDE.md"):
        lines[0] = f"# CLAUDE.md — `{new_dir}/`\n"
    return "".join(lines)


def _emit_per_subdir_claude(
    target: Path,
    loaded_profiles: list,
    stack_paths: dict,
    templates_root: Path,
    *,
    force: bool,
    check: bool,
    update: bool,
) -> list[tuple[str, str]]:
    """D07 (MULTI only): emit a thin `<dir>/CLAUDE.md` per discovered sub-project from stack_paths,
    via a NEW path (not the fixed-name static loop). Root-filtered (SP-Y — never clobber the root
    union CLAUDE.md, esp. under --force), nested-path safe (`apps/web/CLAUDE.md`), manifest-tracked
    (owned status via install_create_only), body re-headed for the dir. A pre-existing user
    `<dir>/CLAUDE.md` is preserved by create-only. Runs after the root CLAUDE.md is written.
    """
    actions: list[tuple[str, str]] = []
    root_claude = (target / "CLAUDE.md").resolve()
    for p, _prof in loaded_profiles:
        dirs = stack_paths.get(p) or []
        pdir = _profile_dir(templates_root, p)
        if pdir is None:
            continue
        examples_dir = pdir / "subdir-examples"
        examples = sorted(examples_dir.glob("*-CLAUDE.md")) if examples_dir.is_dir() else []
        if not examples:
            continue
        src_file = examples[0]  # one subdir-example per profile
        old_stem = src_file.stem[: -len("-CLAUDE")]
        template_body = src_file.read_text()
        target_resolved = target.resolve()
        for d in dirs:
            norm = str(PurePosixPath(d))
            if norm in (".", "/", ""):  # SP-Y: never the repo root
                continue
            dst = target / norm / "CLAUDE.md"
            dst_resolved = dst.resolve()
            # SP-Y (independent validator): reject the root union file AND any path that ESCAPES the
            # target subtree — `..`-overshoot (`a/../..` → an ANCESTOR's CLAUDE.md) or an absolute
            # path outside target. is_relative_to() catches both; the exact-root check catches the
            # in-tree root landing (which IS relative to target).
            if dst_resolved == root_claude or not dst_resolved.is_relative_to(target_resolved):
                continue
            body = _rehead_subdir_body(template_body, old_stem, norm)
            status = install_create_only(dst, body, force=force, check=check, update=update)
            actions.append((f"{norm}/CLAUDE.md", status))
    return actions


def _warn_skill_collisions(loaded_profiles: list, templates_root: Path) -> None:
    """SP-I: surface a same-name skill bundled by >1 profile with DIFFERING SKILL.md content.

    Identical same-name skills dedupe silently (create-only). A DIFFERING collision would otherwise
    be first-write-wins with no signal — so we warn (the union set is emitted in sorted profile
    order, so 'first' is deterministic). Today's profiles have zero cross-profile collisions.
    """
    seen: dict[str, dict[str, list[str]]] = {}
    for p, prof in loaded_profiles:
        pdir = _profile_dir(templates_root, p)
        if pdir is None:
            continue
        for sname in prof.get("skills") or []:
            sk = pdir / "skills" / sname / "SKILL.md"
            if sk.is_file():
                seen.setdefault(sname, {}).setdefault(_sha256_path(sk), []).append(p)
    for sname, by_hash in seen.items():
        if len(by_hash) > 1:
            where = sorted({p for ps in by_hash.values() for p in ps})
            sys.stderr.write(
                f"WARNING: skill '{sname}' bundled by multiple profiles {where} with differing "
                f"SKILL.md — first-in-sorted-order wins (create-only). Reconcile the union.\n"
            )


def load_vars(args: argparse.Namespace) -> dict:
    if args.vars_file:
        raw = _safe_read(Path(args.vars_file))
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"ERROR: invalid JSON in {args.vars_file}: {e}\n")
            sys.exit(2)
    if args.vars_json:
        try:
            return json.loads(args.vars_json)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"ERROR: invalid JSON in --vars-json: {e}\n")
            sys.exit(2)
    if not sys.stdin.isatty():
        try:
            return json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            sys.stderr.write(f"ERROR: invalid JSON on stdin: {e}\n")
            sys.exit(2)
    sys.stderr.write("ERROR: provide vars via --vars-file, --vars-json, or stdin\n")
    sys.exit(2)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render Jinja templates + install files into target (idempotent).",
    )
    p.add_argument("--target", default=".", help="target project directory (default: cwd)")
    p.add_argument("--vars-file", help="path to JSON file with template vars")
    p.add_argument("--vars-json", help="inline JSON string with template vars")
    p.add_argument(
        "--templates-dir",
        default=str(Path(__file__).resolve().parent / "templates"),
        help="directory containing _base/ templates",
    )
    p.add_argument("--profile", help="profile name (informational; passed through to vars if missing)")
    p.add_argument("--check", action="store_true", help="dry-run: report actions without writing")
    p.add_argument("--force", action="store_true", help="overwrite existing files")
    p.add_argument(
        "--update",
        action="store_true",
        help="update mode: write <path>.new for diverged files instead of skipping",
    )
    p.add_argument("--quiet", action="store_true", help="suppress JSON output, only errors")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    vars_dict = load_vars(args)

    if args.profile and "profile_name" not in vars_dict:
        vars_dict["profile_name"] = args.profile

    target = Path(args.target).resolve()
    base = Path(args.templates_dir).resolve() / "_base"

    # D09: respect an existing AGENTS.md in the target by emitting an @import.
    # Detected here at vars-assembly so it applies to --check dry-run and real write alike.
    vars_dict["agents_md_interop"] = (target / "AGENTS.md").is_file()

    # Resolve the active profile set BEFORE the template render so the footer reflects it.
    # MULTI iff vars carries `profiles` with >= 2 entries; a len-1 list or a scalar `profile_name`
    # takes the single-profile path (byte-identical). D06.
    templates_root = Path(args.templates_dir).resolve()
    _profiles_field = vars_dict.get("profiles")
    is_multi = isinstance(_profiles_field, list) and len(_profiles_field) >= 2
    if is_multi:
        active_profiles = sorted(_profiles_field)
        vars_dict["profiles"] = active_profiles
        vars_dict.setdefault("profile_name", active_profiles[0])
    else:
        if not vars_dict.get("profile_name") and isinstance(_profiles_field, list) and _profiles_field:
            vars_dict["profile_name"] = _profiles_field[0]
        active_profiles = [vars_dict["profile_name"]] if vars_dict.get("profile_name") else []
    loaded_profiles = [(p, load_profile(p, templates_root)) for p in active_profiles]
    loaded_profiles = [(p, prof) for p, prof in loaded_profiles if prof is not None]
    stack_paths = vars_dict.get("stack_paths") or {}

    if not base.is_dir():
        sys.stderr.write(f"ERROR: templates base dir not found: {base}\n")
        return 1

    actions: list[tuple[str, str]] = []

    rendered_claude = render_jinja(base / "CLAUDE.md.j2", vars_dict)
    actions.append(
        (
            "CLAUDE.md",
            install_create_only(
                target / "CLAUDE.md",
                rendered_claude,
                force=args.force,
                check=args.check,
                update=args.update,
            ),
        )
    )

    rendered_memory = render_jinja(base / "PROJECT-STATE.md.j2", vars_dict)
    actions.append(
        (
            "PROJECT-STATE.md",
            install_create_only(
                target / "PROJECT-STATE.md",
                rendered_memory,
                force=args.force,
                check=args.check,
                update=args.update,
            ),
        )
    )

    profile_name = vars_dict.get("profile_name")

    # D01 -- permission tier picks the base settings file BEFORE the profile merge. CLI flag wins,
    # then the STRICTEST default_tier across the active set (strict > lax), else "lax" (today's bytes).
    _tier_rank = {"lax": 0, "strict": 1}
    profile_tier = None
    for _p, _prof in loaded_profiles:
        t = _prof.get("default_tier")
        if t and _tier_rank.get(t, 0) > _tier_rank.get(profile_tier or "lax", 0):
            profile_tier = t
    tier = vars_dict.get("tier") or profile_tier or "lax"
    settings_filename = "settings.strict.json" if tier == "strict" else "settings.json"
    base_settings_path = base / ".claude" / settings_filename
    try:
        base_settings = json.loads(_safe_read(base_settings_path))
    except json.JSONDecodeError as e:
        sys.stderr.write(f"ERROR: invalid JSON in {base_settings_path}: {e}\n")
        return 1
    # Settings union: merge each active profile's overrides in sorted order (byte-stable, SP-C).
    for _p, _prof in loaded_profiles:
        overrides = _prof.get("settings_overrides") or {}
        base_settings = merge_settings_overrides(base_settings, overrides)

    # D02 -- opt-in sandbox (flag-gated; key ABSENT by default). Closes the documented
    # default-read gap on ~/.aws + ~/.ssh. Injected AFTER merge. Schema: SCHEMAS-VERIFIED s.3.
    if vars_dict.get("sandbox"):
        base_settings["sandbox"] = {
            "enabled": True,
            "filesystem": {"denyRead": ["~/.aws", "~/.ssh", "~/.aws/credentials"]},
        }

    # D04 -- opt-in warn-only hook (flag-gated; key ABSENT by default). Inline command,
    # exit 0 (never blocks; no .sh path -> no exec-bit gap). Schema: SCHEMAS-VERIFIED s.2.
    if vars_dict.get("hooks"):
        base_settings["hooks"] = {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "echo 'tip: prefer rg over grep for speed' >&2; exit 0",
                        }
                    ],
                }
            ],
            # DA6 -- forced-eval skill dispatch. Skills under-fire without a nudge (empirical
            # ja/ko/zh A/Bs: ~25% -> ~84-100% with a UserPromptSubmit hook). stdout -> context, exit 0.
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "echo 'Before answering, check whether a project skill or path-scoped rule applies to this request.'; exit 0",
                        }
                    ],
                }
            ],
        }

    # DA6 -- opt-in model-resilience fallback (flag-gated; key ABSENT by default). Given model
    # suspensions (e.g. Fable 5 export-hold, 2026-06), fall back to Sonnet (balanced, available).
    # Schema (code.claude.com/docs/en/model-config): an ARRAY of ≤3 model names/aliases, not a scalar.
    if vars_dict.get("fallback_model"):
        base_settings["fallbackModel"] = ["sonnet"]

    settings_content = json.dumps(base_settings, indent=2) + "\n"
    actions.append(
        (
            ".claude/settings.json",
            install_create_only(
                target / ".claude" / "settings.json",
                settings_content,
                force=args.force,
                check=args.check,
                update=args.update,
            ),
        )
    )

    gitignore_status, gitignore_managed = install_gitignore(
        base / ".gitignore", target / ".gitignore", force=args.force, check=args.check
    )
    actions.append((".gitignore", gitignore_status))

    # Opt-in MCP template: a `.mcp.json.example` (never an active `.mcp.json`, which Claude Code
    # would load + prompt for). The user renames it to wire real project-scoped MCP servers.
    mcp_example_src = base / ".mcp.json.example"
    if mcp_example_src.is_file():
        actions.append(
            (
                ".mcp.json.example",
                install_create_only(
                    target / ".mcp.json.example",
                    _safe_read(mcp_example_src),
                    force=args.force,
                    check=args.check,
                    update=args.update,
                ),
            )
        )

    # Emit each active profile's assets. MULTI fills rule paths from stack_paths + suppresses static
    # subdir-examples; a differing same-name skill across profiles is surfaced (SP-I), not silently
    # first-won. Single-profile: exactly one iteration with multi=False → byte-identical to today.
    if is_multi:
        _warn_skill_collisions(loaded_profiles, templates_root)
    if loaded_profiles:
        for p, _prof in loaded_profiles:
            actions.extend(
                install_profile_assets(
                    p,
                    templates_root,
                    target,
                    force=args.force,
                    check=args.check,
                    update=args.update,
                    multi=is_multi,
                    stack_dirs=stack_paths.get(p),
                )
            )
    elif profile_name:
        # named but not found → preserve today's "not-found" action
        actions.extend(
            install_profile_assets(
                profile_name,
                templates_root,
                target,
                force=args.force,
                check=args.check,
                update=args.update,
            )
        )

    # D07: MULTI mode also emits a thin per-subdir CLAUDE.md at each discovered dir (dynamic names
    # from stack_paths), riding native on-demand subtree loading. Root-filtered + manifest-tracked.
    if is_multi:
        actions.extend(
            _emit_per_subdir_claude(
                target,
                loaded_profiles,
                stack_paths,
                templates_root,
                force=args.force,
                check=args.check,
                update=args.update,
            )
        )

    # Uninstall manifest: written last (so it can hash every other file), only on
    # a real write (a dry-run leaves nothing to uninstall). force=True keeps it an
    # accurate mirror of current state, but install_create_only still returns
    # "unchanged" when content is byte-identical → init stays idempotent.
    if not args.check:
        manifest_path = target / ".claude" / ".bootstrap-manifest.json"
        prior_files: dict[str, str] = {}
        if manifest_path.exists():
            try:
                prior = json.loads(manifest_path.read_text())
                prior_files = {f["path"]: f["sha256"] for f in prior.get("files", [])}
            except (json.JSONDecodeError, KeyError, TypeError):
                prior_files = {}
        manifest_content = build_manifest_content(
            target,
            actions,
            gitignore_managed,
            prior_files,
            version=vars_dict.get("bootstrap_version") or VERSION,
            profile_name=profile_name,
            profiles=active_profiles if is_multi else None,
        )
        manifest_status = install_create_only(manifest_path, manifest_content, force=True, check=False)
        actions.append((MANIFEST_REL, manifest_status))

    summary = {
        "target": str(target),
        "templates_base": str(base),
        "check_mode": args.check,
        "force": args.force,
        "actions": [{"file": f, "status": s} for f, s in actions],
    }

    if not args.quiet:
        print(json.dumps(summary, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
