#!/usr/bin/env python3
"""Skill registry CLI for claude-bootstrap.

Subcommands:
  list                      List skills in registry (filterable by --profile, --tier)
  add <name> [--target P]   Install skill into target/.claude/skills/<name>/
  remove <name>             Remove skill from target/.claude/skills/<name>/
  update [--name X]         Re-pull installed skills from current registry sources (force overwrite)
  show <name>               Print full registry entry for one skill
  validate                  Sanity-check registry (required fields, paths exist, URLs reachable=skipped)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import __version__

VERSION = __version__
DEFAULT_REGISTRY = Path(__file__).resolve().parent / "registry" / "skills.yaml"
REPO_ROOT = Path(__file__).resolve().parent


def load_registry(path: Path) -> list[dict]:
    try:
        import yaml
    except ImportError:
        sys.stderr.write(
            "ERROR: pyyaml not installed. Install with: pip install pyyaml\n"
            "       (or run via uv: uv run --with pyyaml --no-project python3 ...)\n"
        )
        sys.exit(3)
    if not path.exists():
        sys.stderr.write(f"ERROR: registry not found: {path}\n")
        sys.exit(2)
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        sys.stderr.write(f"ERROR: invalid YAML in {path}: {e}\n")
        sys.exit(2)
    return data or []


def filter_skills(skills: list[dict], *, profile: str | None, tier: int | None) -> list[dict]:
    out = skills
    if profile:
        out = [s for s in out if profile in (s.get("profiles") or [])]
    if tier is not None:
        out = [s for s in out if s.get("tier") == tier]
    return out


def fmt_status(skill: dict, target: Path) -> str:
    target_skill = target / ".claude" / "skills" / skill["name"]
    if target_skill.is_dir():
        return "installed"
    return "available"


def cmd_list(args: argparse.Namespace) -> int:
    skills = load_registry(args.registry)
    skills = filter_skills(skills, profile=args.profile, tier=args.tier)
    target = Path(args.target).resolve()

    if args.json:
        out = [{**s, "_status": fmt_status(s, target)} for s in skills]
        print(json.dumps(out, indent=2, default=str))
        return 0

    print(f"{'NAME':<40} {'TIER':<5} {'STATUS':<12} {'SOURCE':<10} DESCRIPTION")
    print(f"{'-' * 40} {'-' * 5} {'-' * 12} {'-' * 10} {'-' * 40}")
    for s in skills:
        src_type = (s.get("source") or {}).get("type", "?")
        status = fmt_status(s, target)
        desc = (s.get("description") or "")[:60]
        print(f"{s['name']:<40} {s.get('tier', '?'):<5} {status:<12} {src_type:<10} {desc}")
    print(f"\nTotal: {len(skills)} skill(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    skills = load_registry(args.registry)
    matches = [s for s in skills if s["name"] == args.name]
    if not matches:
        sys.stderr.write(f"ERROR: skill not found: {args.name}\n")
        return 1
    print(json.dumps(matches[0], indent=2, default=str))
    return 0


def install_local(skill: dict, target: Path, force: bool) -> str:
    src_path = REPO_ROOT / skill["source"]["path"]
    if not src_path.is_dir():
        return f"source-missing: {src_path}"
    dst = target / ".claude" / "skills" / skill["name"]
    if dst.exists():
        if not force:
            return "exists-skipped"
        shutil.rmtree(dst)
    try:
        shutil.copytree(src_path, dst, symlinks=True)
    except OSError as e:
        return f"copy-failed: {e}"
    return "installed"


def install_github(skill: dict, target: Path, force: bool) -> str:
    url = skill["source"]["url"]
    subpath = skill["source"]["path"].lstrip("/")
    dst = target / ".claude" / "skills" / skill["name"]
    if dst.exists() and not force:
        return "exists-skipped"

    with tempfile.TemporaryDirectory(prefix="skill-clone-") as tmp:
        tmp_path = Path(tmp) / "repo"
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--no-tags", url, str(tmp_path)],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            return "git-clone-failed: timeout (60s)"
        except subprocess.CalledProcessError as e:
            return f"git-clone-failed: {e.stderr.strip()[:120]}"

        src_in_clone = tmp_path / subpath
        if not src_in_clone.is_dir():
            return f"subpath-missing: {subpath}"

        # Only delete dst AFTER clone succeeds — preserves user state on failure.
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copytree(src_in_clone, dst, symlinks=True)
        except OSError as e:
            return f"copy-failed: {e}"
    return "installed"


def cmd_add(args: argparse.Namespace) -> int:
    skills = load_registry(args.registry)
    matches = [s for s in skills if s["name"] == args.name]
    if not matches:
        sys.stderr.write(f"ERROR: skill not found in registry: {args.name}\n")
        return 1

    skill = matches[0]
    target = Path(args.target).resolve()
    src_type = skill["source"]["type"]

    if src_type == "local":
        result = install_local(skill, target, force=args.force)
    elif src_type == "github":
        result = install_github(skill, target, force=args.force)
    else:
        sys.stderr.write(f"ERROR: unsupported source type: {src_type}\n")
        return 1

    print(
        json.dumps(
            {
                "name": skill["name"],
                "status": result,
                "target": str(target / ".claude" / "skills" / skill["name"]),
            },
            indent=2,
        )
    )
    return 0 if result.startswith(("installed", "exists-skipped")) else 1


def cmd_remove(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    dst = target / ".claude" / "skills" / args.name
    if not dst.exists():
        sys.stderr.write(f"ERROR: skill not installed at {dst}\n")
        return 1
    shutil.rmtree(dst)
    print(json.dumps({"name": args.name, "status": "removed", "target": str(dst)}))
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Re-install installed skills from current registry sources (force overwrite)."""
    target = Path(args.target).resolve()
    skills_dir = target / ".claude" / "skills"
    if not skills_dir.is_dir():
        print(json.dumps({"target": str(target), "updated": [], "note": "no skills/ dir"}, indent=2))
        return 0

    registry = load_registry(args.registry)
    by_name = {s["name"]: s for s in registry}

    if args.name:
        if args.name not in by_name:
            sys.stderr.write(f"ERROR: skill not in registry: {args.name}\n")
            return 1
        candidates = [args.name]
    else:
        candidates = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())

    results: list[dict] = []
    for name in candidates:
        skill = by_name.get(name)
        if skill is None:
            results.append({"name": name, "status": "not-in-registry"})
            continue
        installed_path = skills_dir / name
        if not installed_path.is_dir():
            results.append({"name": name, "status": "not-installed"})
            continue
        src_type = skill["source"]["type"]
        if src_type == "local":
            status = install_local(skill, target, force=True)
        elif src_type == "github":
            status = install_github(skill, target, force=True)
        else:
            status = f"unsupported-source: {src_type}"
        results.append({"name": name, "status": status})

    print(json.dumps({"target": str(target), "updated": results}, indent=2))
    failed = [r for r in results if not r["status"].startswith(("installed", "exists-skipped"))]
    return 0 if not failed else 1


STALE_DAYS = 90


def cmd_validate(args: argparse.Namespace) -> int:
    import datetime

    skills = load_registry(args.registry)
    errors = []
    warnings = []
    seen_names: set[str] = set()
    required = ["name", "description", "source", "tier", "profiles"]
    today = datetime.date.today()
    for i, s in enumerate(skills):
        for k in required:
            if k not in s:
                errors.append(f"[{i}] missing required field: {k}")
        if "name" in s:
            if s["name"] in seen_names:
                errors.append(f"[{i}] duplicate name: {s['name']}")
            seen_names.add(s["name"])
        src = s.get("source") or {}
        if src.get("type") == "local":
            p = REPO_ROOT / src.get("path", "")
            if not p.is_dir():
                errors.append(f"[{s.get('name', i)}] local source not found: {p}")
        elif src.get("type") == "github":
            if not src.get("url") or not src.get("path"):
                errors.append(f"[{s.get('name', i)}] github source needs url + path")
        last_val = s.get("last_validated_at")
        if last_val:
            try:
                last_date = (
                    last_val
                    if isinstance(last_val, datetime.date)
                    else datetime.date.fromisoformat(str(last_val))
                )
                age_days = (today - last_date).days
                if age_days > STALE_DAYS:
                    warnings.append(
                        f"[{s.get('name', i)}] last_validated_at {last_date} is {age_days}d old (>{STALE_DAYS}d)"
                    )
            except (ValueError, TypeError):
                warnings.append(f"[{s.get('name', i)}] last_validated_at unparseable: {last_val!r}")

    if warnings:
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(
            f"\n{len(errors)} error(s), {len(warnings)} warning(s) in {len(skills)} skill(s)", file=sys.stderr
        )
        return 1
    print(f"OK: {len(skills)} skill(s) validated ({len(warnings)} warning(s))")
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Skill registry CLI for claude-bootstrap.")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY), type=Path, help="path to skills.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list skills in registry")
    p_list.add_argument("--target", default=".", help="target project (for installed/available status)")
    p_list.add_argument("--profile", help="filter by profile name")
    p_list.add_argument("--tier", type=int, help="filter by tier (1, 2, or 3)")
    p_list.add_argument("--json", action="store_true", help="JSON output")

    p_show = sub.add_parser("show", help="show full registry entry")
    p_show.add_argument("name")

    p_add = sub.add_parser("add", help="install skill into target/.claude/skills/")
    p_add.add_argument("name")
    p_add.add_argument("--target", default=".")
    p_add.add_argument("--force", action="store_true")

    p_rm = sub.add_parser("remove", help="remove installed skill")
    p_rm.add_argument("name")
    p_rm.add_argument("--target", default=".")

    p_up = sub.add_parser("update", help="re-pull installed skills from current registry sources")
    p_up.add_argument("--target", default=".")
    p_up.add_argument("--name", help="update only this skill (default: all installed)")

    sub.add_parser("validate", help="sanity-check registry")

    return p.parse_args()


def main() -> int:
    args = parse_args()
    return {
        "list": cmd_list,
        "show": cmd_show,
        "add": cmd_add,
        "remove": cmd_remove,
        "update": cmd_update,
        "validate": cmd_validate,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
