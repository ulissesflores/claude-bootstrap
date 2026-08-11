#!/usr/bin/env python3
"""Fail if personal or machine-identifying strings reach tracked files.

claude-bootstrap grew out of a private workspace, so the published tree must not carry
context from the machine and the organisation it was authored on. This gate is the check.

Two layers, deliberately separated:

* **Structural patterns**, shipped here — absolute home paths, which identify a developer
  machine for *any* user of this tool, not just this project's maintainer.
* **Local patterns**, read from `.pii-patterns.local` (gitignored) when it is present, one
  `regex<TAB>reason` per line. Anything specific to a person, an organisation or a private
  host belongs there and never enters the repository — including this project's own list.
  Downstream users get the same extension point without forking the script.

The success line always names which layers ran. A clean result from fewer patterns is not
the same result, and printing an identical line for both would hide exactly that.

Scans `git ls-files` — what actually ships — rather than the working tree, so untracked
scratch dirs never trip it. Corollary: a newly written file is invisible to this gate until
it is staged.

Not in scope: *authorship* metadata (name, ORCID, e-mail in CITATION.cff / pyproject.toml)
is deliberate attribution, not leakage.

Usage:
    python3 scripts/pii-scan.py           # exit 1 on any hit
    python3 scripts/pii-scan.py --list    # show the active patterns and exit
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Gitignored, and absent by design on a fresh clone and in CI.
LOCAL_PATTERNS = REPO_ROOT / ".pii-patterns.local"

# (regex, why it must not ship). Structural only — see the module docstring.
# `user`/`usuario` are exempt: they are the placeholder the docs use when *teaching* that
# absolute paths are an anti-pattern, not a real machine.
PATTERNS: list[tuple[str, str]] = [
    (
        r"/(?:Users|home)/(?!user/|usuario/)[A-Za-z0-9][A-Za-z0-9._-]*/",
        "absolute home path of a developer machine (macOS or Linux)",
    ),
]


def read_local_patterns(path: Path) -> list[tuple[str, str]]:
    """Parse `regex<TAB>reason` lines. A malformed line is fatal, never skipped.

    Skipping would turn a typo into a silently narrower scan that still prints `clean`.
    """
    if not path.exists():
        return []
    out: list[tuple[str, str]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        pattern, tab, why = line.partition("\t")
        if not tab or not pattern.strip() or not why.strip():
            raise SystemExit(f"{path.name}:{lineno}: expected `regex<TAB>reason`, got: {line[:60]}")
        out.append((pattern.strip(), why.strip()))
    return out


def compile_patterns(specs: list[tuple[str, str]]) -> list[tuple[re.Pattern[str], str]]:
    compiled = []
    for pattern, why in specs:
        try:
            compiled.append((re.compile(pattern), why))
        except re.error as exc:
            raise SystemExit(f"invalid regex {pattern!r}: {exc}") from exc
    return compiled


def describe_mode(extra: list[tuple[str, str]]) -> str:
    if extra:
        return f"[+{len(extra)} local pattern(s) from {LOCAL_PATTERNS.name}]"
    return f"[structural only; no {LOCAL_PATTERNS.name}]"


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [f for f in out.split("\0") if f]


def scan(paths: list[str], root: Path, compiled: list[tuple[re.Pattern[str], str]]) -> list[str]:
    hits: list[str] = []
    for rel in paths:
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue  # binary asset or a staged deletion
        for lineno, line in enumerate(text.splitlines(), 1):
            for regex, why in compiled:
                if regex.search(line):
                    hits.append(f"{rel}:{lineno}: {why} -> {line.strip()[:100]}")
    return hits


def main() -> int:
    extra = read_local_patterns(LOCAL_PATTERNS)
    specs = PATTERNS + extra
    mode = describe_mode(extra)

    if "--list" in sys.argv:
        for pattern, why in specs:
            print(f"{pattern:<28} {why}")
        print(f"\n{len(specs)} pattern(s) active {mode}")
        return 0

    files = tracked_files()
    hits = scan(files, REPO_ROOT, compile_patterns(specs))

    if hits:
        print(f"PII scan FAILED — {len(hits)} hit(s) in tracked files {mode}:\n", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        print(
            "\nRemove or generalize the text. If a hit is a false positive, narrow the pattern "
            f"where it is defined — structural ones here, local ones in {LOCAL_PATTERNS.name}. "
            "There is no allowlist: a tracked file either passes or is fixed.",
            file=sys.stderr,
        )
        return 1

    print(f"PII scan clean — {len(files)} tracked file(s), 0 hit(s) {mode}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
