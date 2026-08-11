"""CLI dispatcher for `claude-bootstrap`.

Subcommands: init | detect | doctor | skill | update | help | version

Each subcommand maps to the matching module's `main()` (with sys.argv adjusted)
or, for `init`/`update`, runs interview → install in sequence.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from . import __version__

HERE = Path(__file__).resolve().parent
TEMPLATES_DIR = HERE / "templates"
REGISTRY_PATH = HERE / "registry" / "skills.yaml"


def _run_module(module_name: str, args: list[str]) -> int:
    """Invoke `claude_bootstrap.<module_name>.main()` with adjusted sys.argv.

    Catches SystemExit so a sys.exit() inside the module doesn't kill the dispatcher.
    """
    from importlib import import_module

    mod = import_module(f"claude_bootstrap.{module_name}")
    saved_argv = sys.argv
    sys.argv = [module_name] + args
    try:
        try:
            rc = mod.main()
            return rc if isinstance(rc, int) else 0
        except SystemExit as e:
            code = e.code
            if code is None:
                return 0
            return code if isinstance(code, int) else 1
    finally:
        sys.argv = saved_argv


def _python_bin() -> str:
    """Path to the running Python interpreter (for subprocess calls when needed)."""
    return sys.executable


def _confirm(prompt: str) -> bool:
    """Ask a y/N question on stdin. Default (empty/EOF/anything not y[es]) is No."""
    try:
        answer = input(prompt).strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes")


def _render_detect_rationale(detect: dict) -> str:
    """Human-readable 'why this profile' from a detect.json dict.

    Surfaces the detection signals so the chosen profile reads as evidence-based,
    not arbitrary (the D7.2 'detection rationale' gap). Tolerant of missing keys.
    """
    profile = detect.get("profile_suggestion")
    mode = detect.get("mode")
    signals = detect.get("signals") or []
    lines: list[str] = []
    if profile:
        conf = detect.get("confidence")
        head = f"Detected profile: {profile}"
        if isinstance(conf, int | float):
            head += f" (confidence {conf:.0%})"
        lines.append(head)
        if signals:
            lines.append("  Why: " + ", ".join(signals))
    else:
        lines.append("No profile auto-detected — defaulting to universal-software.")
        if signals:
            lines.append("  Signals: " + ", ".join(signals))
    if mode:
        lines.append(f"  Mode: {mode}")
    return "\n".join(lines)


def _render_prune_footer() -> str:
    """Anti-bloat framing shown after a real emit (the D7.2 'toolkit theater' gap).

    Frames the emit as plain, prunable files and points at the escape hatches so
    an elaborate .claude/ tree doesn't read as an opaque framework.
    """
    return (
        "What was written is just files under .claude/ (plus root CLAUDE.md and "
        "PROJECT-STATE.md).\nRead, edit, or remove any of it — nothing is hidden or "
        "required; the profile is a starting point, not a framework.\n"
        "  - Preview a run without writing:  claude-bootstrap init --check\n"
        "  - Remove a single skill:          claude-bootstrap skill remove <name>\n"
        "  - Revert the whole emit:          claude-bootstrap uninstall"
    )


def cmd_init(args: list[str]) -> int:
    return _do_init_or_update(args, update=False)


def cmd_update(args: list[str]) -> int:
    return _do_init_or_update(args, update=True)


def _do_init_or_update(args: list[str], *, update: bool) -> int:
    """Shared flow for `init` and `update`: detect (info) → interview → install."""
    parser = argparse.ArgumentParser(
        prog="claude-bootstrap " + ("update" if update else "init"),
        description=(
            "Update existing claude-bootstrap install"
            if update
            else "Initialize claude-bootstrap in current directory"
        ),
    )
    parser.add_argument(
        "--profile",
        action="append",
        help="profile name (skip interactive choice); repeatable for a multi-profile monorepo union",
    )
    parser.add_argument("--non-interactive", action="store_true", help="use defaults; no prompts")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    parser.add_argument("--check", action="store_true", help="dry-run: report actions without writing")
    parser.add_argument("--yes", "-y", action="store_true", help="skip the confirm-before-write prompt")
    parser.add_argument("--target", default=".", help="target project (default: cwd)")
    parser.add_argument(
        "--tier", choices=["lax", "strict"], default=None, help="permission tier (default: lax)"
    )
    parser.add_argument("--sandbox", action="store_true", help="emit opt-in sandbox block")
    parser.add_argument(
        "--hooks",
        action="store_true",
        help="emit opt-in conservative hooks bundle (PreToolUse warn + skill-dispatch)",
    )
    parser.add_argument(
        "--fallback-model", action="store_true", help="emit opt-in fallbackModel (model resilience)"
    )
    ns = parser.parse_args(args)

    with tempfile.TemporaryDirectory(prefix="claude-bootstrap.") as tmpdir:
        tmp = Path(tmpdir)
        detect_args = ["--output", str(tmp / "detect.json"), ns.target]
        rc = _run_module("detect", detect_args)
        # detect returns non-zero when no profile suggestion (still useful, info-only)
        detect_data: dict = {}
        if (tmp / "detect.json").exists():
            try:
                detect_data = json.loads((tmp / "detect.json").read_text())
            except json.JSONDecodeError:
                detect_data = {}
            print("[detect]")
            print(_render_detect_rationale(detect_data))
            print()

        interview_args = ["--output", str(tmp / "vars.json"), "--target", ns.target]
        # D08: resolve the profile set — a user-forced --profile (repeatable) wins; otherwise the
        # detected set is the default for non-interactive OR whenever detection found a multi-stack
        # monorepo (>= 2 stacks). Interactive single-stack keeps prompting (chosen stays empty).
        detected = detect_data.get("profiles") or []
        if ns.profile:
            chosen = list(ns.profile)
        elif ns.non_interactive or len(detected) >= 2:
            chosen = detected
        else:
            chosen = []
        for p in chosen:
            interview_args += ["--profile", p]
        if len(chosen) >= 2:
            interview_args += ["--stack-paths-json", json.dumps(detect_data.get("stack_paths") or {})]
        if ns.non_interactive:
            interview_args.append("--non-interactive")
        if ns.tier:
            interview_args += ["--tier", ns.tier]
        if ns.sandbox:
            interview_args.append("--sandbox")
        if ns.hooks:
            interview_args.append("--hooks")
        if ns.fallback_model:
            interview_args.append("--fallback-model")
        print("[interview]")
        rc = _run_module("interview", interview_args)
        if rc != 0:
            return rc
        print((tmp / "vars.json").read_text())
        print()

        install_args = [
            "--vars-file",
            str(tmp / "vars.json"),
            "--target",
            ns.target,
            "--templates-dir",
            str(TEMPLATES_DIR),
        ]
        if ns.force:
            install_args.append("--force")
        if update:
            install_args.append("--update")

        # Pure dry-run: report the plan and stop (no writes, no prompt).
        if ns.check:
            print("[" + ("update" if update else "install") + " --check]")
            return _run_module("install", install_args + ["--check"])

        # Confirm-before-write gate. Show the plan (--check), then ask. Skipped by
        # --non-interactive (CI) and --yes; declining writes nothing.
        if not ns.non_interactive and not ns.yes:
            print("[plan]")
            plan_rc = _run_module("install", install_args + ["--check"])
            if plan_rc != 0:
                return plan_rc
            if not _confirm("\nProceed and write these files? [y/N] "):
                print("Aborted — no files written.")
                return 0

        print("[" + ("update" if update else "install") + "]")
        rc = _run_module("install", install_args)
        if rc == 0:
            print()
            print(_render_prune_footer())
        return rc


def cmd_uninstall(args: list[str]) -> int:
    """Reverse an emit via the install manifest. Mirrors init's confirm gate."""
    parser = argparse.ArgumentParser(
        prog="claude-bootstrap uninstall",
        description="Remove a claude-bootstrap emit (uses the install manifest).",
    )
    parser.add_argument("--target", default=".", help="target project (default: cwd)")
    parser.add_argument("--check", action="store_true", help="dry-run: report removals without deleting")
    parser.add_argument("--non-interactive", action="store_true", help="skip the confirm prompt")
    parser.add_argument("--yes", "-y", action="store_true", help="skip the confirm prompt")
    ns = parser.parse_args(args)

    uninstall_args = ["--target", ns.target]

    # Pure dry-run: report the plan and stop.
    if ns.check:
        print("[uninstall --check]")
        return _run_module("uninstall", uninstall_args + ["--check"])

    # Destructive: confirm-before-remove gate (same shape as init). Skipped by
    # --non-interactive (CI) and --yes; declining removes nothing.
    if not ns.non_interactive and not ns.yes:
        print("[plan]")
        plan_rc = _run_module("uninstall", uninstall_args + ["--check"])
        if plan_rc != 0:
            return plan_rc
        if not _confirm("\nRemove these files? [y/N] "):
            print("Aborted — nothing removed.")
            return 0

    print("[uninstall]")
    return _run_module("uninstall", uninstall_args)


def cmd_skill(args: list[str]) -> int:
    # Inject default registry path if --registry not provided
    if "--registry" not in args:
        args = ["--registry", str(REGISTRY_PATH)] + args
    return _run_module("skill", args)


def usage() -> None:
    print(f"""claude-bootstrap v{__version__}

Usage: claude-bootstrap <command> [args...]

Commands:
  init        Initialize claude-bootstrap in current directory
              Flags: --profile <name>, --non-interactive, --force, --check, --target <dir>,
                     --tier <lax|strict>, --sandbox, --hooks
  update      Re-run install; diverged files written as <path>.new (use --force to overwrite)
              Flags: --profile <name>, --non-interactive, --force, --check, --target <dir>,
                     --tier <lax|strict>, --sandbox, --hooks
  uninstall   Reverse an emit via its manifest; keeps user-modified files
              Flags: --check, --yes, --non-interactive, --target <dir>
  detect      Scan project, suggest profile (read-only, JSON output)
  doctor      Health check current installation
  audit       Provenance + integrity report for an emitted .claude/ (offline; --json, --strict)
  skill       Manage skills (list|show|add|remove|update|validate)
  version     Print version
  help        Show this message

Templates dir: {TEMPLATES_DIR}
Registry:      {REGISTRY_PATH}
""")


def main() -> int:
    if len(sys.argv) < 2:
        usage()
        return 0
    cmd = sys.argv[1]
    rest = sys.argv[2:]

    if cmd in ("help", "-h", "--help"):
        usage()
        return 0
    if cmd in ("version", "-V", "--version"):
        print(f"claude-bootstrap v{__version__}")
        return 0
    if cmd == "init":
        return cmd_init(rest)
    if cmd == "update":
        return cmd_update(rest)
    if cmd == "uninstall":
        return cmd_uninstall(rest)
    if cmd == "detect":
        return _run_module("detect", rest)
    if cmd == "doctor":
        return _run_module("doctor", rest)
    if cmd == "audit":
        return _run_module("audit", rest)
    if cmd == "skill":
        return cmd_skill(rest)

    sys.stderr.write(f"ERROR: unknown command: {cmd}\n")
    usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
