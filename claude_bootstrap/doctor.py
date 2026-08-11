#!/usr/bin/env python3
"""doctor.py — read-only health-check CLI for claude-bootstrap projects."""

import argparse
import json
import re
import sys
from pathlib import Path

STATUS_PASS = "PASS"
STATUS_WARN = "WARN"
STATUS_FAIL = "FAIL"
STATUS_SKIP = "SKIP"
STATUS_ORDER = [STATUS_PASS, STATUS_WARN, STATUS_FAIL, STATUS_SKIP]


def result(name, status, details=""):
    return {"name": name, "status": status, "details": details}


def check_claude_md_exists(root: Path):
    name = "CLAUDE.md exists"
    candidates = [root / "CLAUDE.md", root / ".claude" / "CLAUDE.md"]
    found = [p for p in candidates if p.is_file()]
    if found:
        return result(name, STATUS_PASS, str(found[0].relative_to(root)))
    return result(name, STATUS_FAIL, "CLAUDE.md not found in root or .claude/")


def check_claude_md_size(root: Path, prev_pass: bool):
    name = "CLAUDE.md size ≤150 lines (ideal ≤60)"
    if not prev_pass:
        return result(name, STATUS_FAIL, "skipped — CLAUDE.md missing")
    candidates = [root / "CLAUDE.md", root / ".claude" / "CLAUDE.md"]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        return result(name, STATUS_FAIL, "CLAUDE.md missing")
    lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    if lines <= 150:
        return result(name, STATUS_PASS, f"{lines} lines")
    if lines <= 200:
        return result(name, STATUS_WARN, f"{lines} lines (max ~150; split into .claude/rules/)")
    return result(name, STATUS_FAIL, f"{lines} lines (max ~150; split into .claude/rules/)")


def check_claude_dir(root: Path):
    name = ".claude/ directory exists"
    if (root / ".claude").is_dir():
        return result(name, STATUS_PASS, ".claude/ present")
    return result(name, STATUS_FAIL, ".claude/ absent or not a directory")


def _load_settings(root: Path):
    """Return (data, error_str). data=None on failure."""
    path = root / ".claude" / "settings.json"
    if not path.is_file():
        return None, "settings.json absent"
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSON error: {e}"


def check_settings_json_valid(root: Path):
    name = ".claude/settings.json valid JSON"
    data, err = _load_settings(root)
    if err:
        return result(name, STATUS_FAIL, err)
    return result(name, STATUS_PASS, "parses OK")


def check_settings_schema(root: Path):
    name = ".claude/settings.json has $schema"
    data, err = _load_settings(root)
    if err:
        return result(name, STATUS_WARN, err)
    if "$schema" in data:
        return result(name, STATUS_PASS, "$schema key present")
    return result(name, STATUS_WARN, "$schema key absent")


_SECRET_RE = re.compile(r"(?i)\.env|secret|credential|key|pem")


def check_settings_secret_deny(root: Path):
    name = ".claude/settings.json has secret-deny rules"
    data, err = _load_settings(root)
    if err:
        return result(name, STATUS_FAIL, err)
    deny = data.get("permissions", {}).get("deny", [])
    if not isinstance(deny, list):
        deny = []
    matches = [r for r in deny if isinstance(r, str) and _SECRET_RE.search(r)]
    if matches:
        return result(name, STATUS_PASS, f"deny rule(s): {matches[:2]}")
    return result(name, STATUS_FAIL, "no secret/key/env deny rules found")


def check_gitignore_exists(root: Path):
    name = ".gitignore exists"
    if (root / ".gitignore").is_file():
        return result(name, STATUS_PASS, ".gitignore present")
    return result(name, STATUS_WARN, ".gitignore absent")


def _gitignore_lines(root: Path):
    path = root / ".gitignore"
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def check_gitignore_local_md(root: Path):
    name = ".gitignore covers CLAUDE.local.md"
    lines = _gitignore_lines(root)
    if any(line.strip() == "CLAUDE.local.md" for line in lines):
        return result(name, STATUS_PASS, "CLAUDE.local.md covered")
    return result(name, STATUS_WARN, "CLAUDE.local.md not in .gitignore")


def check_gitignore_env(root: Path):
    name = ".gitignore covers .env"
    lines = _gitignore_lines(root)
    env_re = re.compile(r"^\.env")
    if any(env_re.match(line.strip()) for line in lines):
        return result(name, STATUS_PASS, ".env pattern covered")
    return result(name, STATUS_WARN, ".env not covered in .gitignore")


def check_memory_md(root: Path):
    name = "PROJECT-STATE.md exists"
    if (root / "PROJECT-STATE.md").is_file():
        return result(name, STATUS_PASS, "PROJECT-STATE.md present")
    return result(name, STATUS_WARN, "PROJECT-STATE.md absent")


_SUPERPOWERS_RE = re.compile(r"superpowers", re.IGNORECASE)


def check_superpowers(root: Path):
    name = "superpowers reachable"
    candidates = [root / "CLAUDE.md", root / ".claude" / "CLAUDE.md"]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        return result(name, STATUS_SKIP, "CLAUDE.md absent — cannot check")
    content = path.read_text(encoding="utf-8", errors="replace")
    if not _SUPERPOWERS_RE.search(content):
        return result(name, STATUS_SKIP, "superpowers not referenced in CLAUDE.md")
    home = Path.home()
    sp_paths = [home / ".claude" / "superpowers", home / ".claude" / "skills" / "superpowers"]
    found = next((p for p in sp_paths if p.exists()), None)
    if found:
        return result(name, STATUS_PASS, f"found at {found}")
    return result(name, STATUS_WARN, "mentioned in CLAUDE.md but not found on disk")


_PROFILE_RE = re.compile(r"profiles?:\s*(\w[\w-]*)")


def check_profile_referenced(root: Path):
    name = "profile referenced in CLAUDE.md"
    candidates = [root / "CLAUDE.md", root / ".claude" / "CLAUDE.md"]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        return result(name, STATUS_WARN, "CLAUDE.md absent")
    content = path.read_text(encoding="utf-8", errors="replace")
    m = _PROFILE_RE.search(content)
    if m:
        return result(name, STATUS_PASS, f"profile: {m.group(1)}")
    return result(name, STATUS_WARN, "no 'profile: <name>' found in CLAUDE.md")


def check_rules_present(root: Path):
    """Report path-scoped rules. PASS when `.claude/rules/*.md` exist (the multi-profile union +
    every code profile ship them); WARN — never FAIL — when absent, so a legitimately rule-less
    profile (universal-software) still passes overall (D09; validator-flagged)."""
    name = "path-scoped rules present"
    rules_dir = root / ".claude" / "rules"
    md = sorted(rules_dir.glob("*.md")) if rules_dir.is_dir() else []
    if md:
        return result(name, STATUS_PASS, f"{len(md)} rule file(s) in .claude/rules/")
    return result(name, STATUS_WARN, "no path-scoped rules (.claude/rules/ empty or absent)")


def run_checks(root: Path):
    r1 = check_claude_md_exists(root)
    r2 = check_claude_md_size(root, r1["status"] == STATUS_PASS)
    return [
        r1,
        r2,
        check_claude_dir(root),
        check_settings_json_valid(root),
        check_settings_schema(root),
        check_settings_secret_deny(root),
        check_gitignore_exists(root),
        check_gitignore_local_md(root),
        check_gitignore_env(root),
        check_memory_md(root),
        check_superpowers(root),
        check_profile_referenced(root),
        check_rules_present(root),
    ]


_STATUS_COLORS = {
    STATUS_PASS: "green",
    STATUS_WARN: "yellow",
    STATUS_FAIL: "red",
    STATUS_SKIP: "bright_black",
}


def summarize(checks):
    counts = {s: 0 for s in STATUS_ORDER}
    for c in checks:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    return counts


def print_rich(checks, quiet):
    try:
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        return False

    console = Console()
    table = Table(show_header=True, header_style="bold")
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center", width=6)
    table.add_column("Details")

    for c in checks:
        if quiet and c["status"] in (STATUS_PASS, STATUS_WARN, STATUS_SKIP):
            continue
        color = _STATUS_COLORS.get(c["status"], "white")
        table.add_row(c["name"], f"[{color}]{c['status']}[/{color}]", c["details"])

    console.print(table)
    counts = summarize(checks)
    console.print(
        f"[green]{counts[STATUS_PASS]} pass[/green] · "
        f"[yellow]{counts[STATUS_WARN]} warn[/yellow] · "
        f"[red]{counts[STATUS_FAIL]} fail[/red] · "
        f"[bright_black]{counts[STATUS_SKIP]} skip[/bright_black]"
    )
    return True


def print_plain(checks, quiet):
    for c in checks:
        if quiet and c["status"] in (STATUS_PASS, STATUS_WARN, STATUS_SKIP):
            continue
        print(f"[{c['status']}] {c['name']}: {c['details']}")
    counts = summarize(checks)
    print(
        f"{counts[STATUS_PASS]} pass · {counts[STATUS_WARN]} warn · "
        f"{counts[STATUS_FAIL]} fail · {counts[STATUS_SKIP]} skip"
    )


def print_json(checks, root: Path):
    counts = summarize(checks)
    output = {
        "path": str(root.resolve()),
        "checks": checks,
        "summary": {
            "pass": counts[STATUS_PASS],
            "warn": counts[STATUS_WARN],
            "fail": counts[STATUS_FAIL],
            "skip": counts[STATUS_SKIP],
        },
    }
    print(json.dumps(output, indent=2))


def exit_code(checks, strict: bool) -> int:
    for c in checks:
        if c["status"] == STATUS_FAIL:
            return 1
        if strict and c["status"] == STATUS_WARN:
            return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="claude-bootstrap doctor",
        description="Read-only health-check for claude-bootstrap projects.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project root to check (default: current directory)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Print only FAIL lines",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat WARN as FAIL for exit-code purposes",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="Output as JSON",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        sys.exit(2)

    checks = run_checks(root)

    if args.json_out:
        print_json(checks, root)
    else:
        if not print_rich(checks, args.quiet):
            print_plain(checks, args.quiet)

    sys.exit(exit_code(checks, args.strict))


if __name__ == "__main__":
    main()
