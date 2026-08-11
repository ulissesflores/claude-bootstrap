#!/usr/bin/env python3
"""Interview wizard for claude-bootstrap. Collects vars for Jinja templates."""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from . import __version__

VERSION = __version__
PROFILES = ["universal-software", "academic", "data-science", "frontend", "devops", "backend"]
LANGUAGES = ["python", "typescript", "javascript", "rust", "go", "shell", "markdown", "mixed"]


def detect_git_remote(cwd: Path | None = None) -> str | None:
    try:
        cmd = ["git", "remote", "get-url", "origin"]
        if cwd is not None:
            cmd = ["git", "-C", str(cwd), "remote", "get-url", "origin"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        url = result.stdout.strip()
        return url if result.returncode == 0 and url else None
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return None


def detect_superpowers() -> bool:
    home = Path.home()
    return (home / ".claude" / "superpowers").exists() or (
        home / ".claude" / "skills" / "superpowers"
    ).exists()


def detect_agentic_stack(cwd: Path) -> bool:
    return (Path.home() / ".agent").exists() or (cwd / ".agent").exists()


def _resolve_profile_set(args) -> tuple[list[str], str, dict]:
    """Normalize the repeatable --profile + --stack-paths-json into (profiles, profile_name,
    stack_paths). A set of >= 2 → multi (both `profiles` and `stack_paths` emitted into vars); a
    single or empty selection → single (profile_name only, no `profiles` key → byte-identical)."""
    raw = getattr(args, "profile", None) or []
    if isinstance(raw, str):
        raw = [raw]
    profiles = sorted(dict.fromkeys(raw))  # dedupe, deterministic order
    if len(profiles) >= 2:
        stack_paths: dict = {}
        if getattr(args, "stack_paths_json", None):
            try:
                stack_paths = json.loads(args.stack_paths_json) or {}
            except json.JSONDecodeError:
                stack_paths = {}
        return profiles, profiles[0], stack_paths
    if len(profiles) == 1:
        return [], profiles[0], {}
    return [], "universal-software", {}


def run_non_interactive(args) -> dict:
    target = Path(getattr(args, "target", ".") or ".").resolve()
    profiles, profile_name, stack_paths = _resolve_profile_set(args)
    vars_dict = {
        "project_name": args.project_name or target.name,
        "project_description": "",
        "primary_language": "mixed",
        "is_monorepo": bool(profiles),
        "git_remote": detect_git_remote(target),
        "profile_name": profile_name,
        "superpowers_available": detect_superpowers(),
        "agentic_stack_interop": detect_agentic_stack(target),
        "extra_rules": [],
        "generated_at": datetime.date.today().isoformat(),
        "bootstrap_version": VERSION,
        "tier": getattr(args, "tier", None),
        "sandbox": bool(getattr(args, "sandbox", False)),
        "hooks": bool(getattr(args, "hooks", False)),
        "fallback_model": bool(getattr(args, "fallback_model", False)),
    }
    if profiles:
        vars_dict["profiles"] = profiles
        vars_dict["stack_paths"] = stack_paths
    return vars_dict


def run_interactive(args) -> dict:
    # Lazy import: questionary is only needed in interactive mode
    try:
        import questionary
    except ImportError:
        print(
            "Error: 'questionary' is not installed.\n"
            "  Install it with: pip install questionary\n"
            "  Or skip the wizard with: claude-bootstrap init --non-interactive",
            file=sys.stderr,
        )
        sys.exit(2)

    target = Path(getattr(args, "target", ".") or ".").resolve()
    git_remote = detect_git_remote(target)
    superpowers = detect_superpowers()
    agentic = detect_agentic_stack(target)

    project_name = questionary.text(
        "Project name:",
        default=args.project_name or target.name,
    ).ask()

    project_description = questionary.text(
        "One-line description (max 200 chars):",
        default="",
        validate=lambda v: True if len(v) <= 200 else "Max 200 characters",
    ).ask()

    primary_language = questionary.select(
        "Primary language:",
        choices=LANGUAGES,
        default="mixed",
    ).ask()

    is_monorepo = questionary.confirm("Is this a monorepo?", default=False).ask()

    git_remote_answer = questionary.text(
        "Git remote origin URL (leave blank for none):",
        default=git_remote or "",
    ).ask()

    # Skip the profile question if --profile was passed (repeatable → a multi-profile set).
    profiles_set, profile_name, stack_paths = _resolve_profile_set(args)
    if not args.profile:
        profile_name = questionary.select(
            "Bootstrap profile:",
            choices=PROFILES,
            default="universal-software",
        ).ask()
        profiles_set, stack_paths = [], {}

    superpowers_available = questionary.confirm(
        "Superpowers available?",
        default=superpowers,
    ).ask()

    agentic_stack_interop = questionary.confirm(
        "Enable agentic-stack interop?",
        # Offer True as default if ~/.agent/ or .agent/ was found
        default=agentic,
    ).ask()

    result = {
        "project_name": project_name,
        "project_description": project_description,
        "primary_language": primary_language,
        "is_monorepo": is_monorepo,
        "git_remote": git_remote_answer or None,
        "profile_name": profile_name,
        "superpowers_available": superpowers_available,
        "agentic_stack_interop": agentic_stack_interop,
        "extra_rules": [],
        "generated_at": datetime.date.today().isoformat(),
        "bootstrap_version": VERSION,
        "tier": getattr(args, "tier", None),
        "sandbox": bool(getattr(args, "sandbox", False)),
        "hooks": bool(getattr(args, "hooks", False)),
        "fallback_model": bool(getattr(args, "fallback_model", False)),
    }
    if profiles_set:
        result["profiles"] = profiles_set
        result["stack_paths"] = stack_paths
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Interview wizard for claude-bootstrap. Outputs JSON for Jinja templates."
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Use sensible defaults; no prompts required.",
    )
    parser.add_argument(
        "--profile",
        action="append",
        choices=PROFILES,
        metavar="PROFILE",
        help=(
            f"Pre-select a profile (one of: {', '.join(PROFILES)}). "
            f"Repeatable — pass it more than once for a multi-profile monorepo union."
        ),
    )
    parser.add_argument(
        "--stack-paths-json",
        dest="stack_paths_json",
        metavar="JSON",
        default=None,
        help="JSON map {profile: [dir, ...]} for a multi-profile union (from detect.json).",
    )
    parser.add_argument(
        "--project-name",
        dest="project_name",
        metavar="NAME",
        help="Override the project name (default: current directory name).",
    )
    parser.add_argument(
        "--target",
        metavar="DIR",
        default=".",
        help="Target project directory — used for project name, git remote, and agentic detection.",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Write JSON to this file instead of stdout.",
    )
    # Settings tier / opt-in security blocks (flag-only; no prompt = genuinely opt-in).
    parser.add_argument(
        "--tier",
        choices=["lax", "strict"],
        default=None,
        help="Permission tier (default: lax). strict = narrow allow-list, deny ⊇ lax.",
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Emit an opt-in sandbox block (denyRead ~/.aws, ~/.ssh).",
    )
    parser.add_argument(
        "--hooks",
        action="store_true",
        help="Emit an opt-in conservative hooks bundle (PreToolUse warn + skill-dispatch).",
    )
    parser.add_argument(
        "--fallback-model",
        action="store_true",
        help="Emit an opt-in fallbackModel (model resilience; falls back to Sonnet).",
    )
    args = parser.parse_args()

    try:
        data = run_non_interactive(args) if args.non_interactive else run_interactive(args)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 1

    payload = json.dumps(data, indent=2)

    if args.output:
        try:
            Path(args.output).write_text(payload, encoding="utf-8")
        except OSError as e:
            print(f"ERROR: cannot write {args.output}: {e}", file=sys.stderr)
            return 1
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    sys.exit(main())
