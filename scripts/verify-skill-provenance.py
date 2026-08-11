#!/usr/bin/env python3
"""Verify (and optionally sync) bundled skills against their upstream commit pins.

Two modes:

  (default) VERIFY — for every skill in a profile's NOTICE.md, fetch the upstream
  SKILL.md at the pinned SHA and compare to the bundled copy:
    EXACT    byte-identical
    WS-ONLY  identical after trailing-whitespace strip (our pre-commit trims it)
    DIFFERS  substantive difference (drift)
  Exit 0 if all EXACT/WS-ONLY, else 1. Pins come from scripts/skill-pins.json
  (falling back to the SHA defaults below).

  --sync — refresh the bundled skills FROM upstream: clone each repo at HEAD,
  mirror every skill's tree (SKILL.md + references/ + scripts/, text only —
  binaries/tests excluded, existing LICENSE.txt preserved), and write the
  resolved HEAD SHAs to scripts/skill-pins.json. Needs git + network (run with
  the Bash network sandbox disabled). After --sync, run a plain verify (expect all EXACT/WS-ONLY).

Scope: verify compares `SKILL.md` only; --sync mirrors the whole text tree.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROFILES = REPO / "claude_bootstrap" / "templates" / "profiles"
PINS_FILE = REPO / "scripts" / "skill-pins.json"

# Fallback reference SHAs if skill-pins.json is absent (audit-time HEADs).
SHA_DEFAULT = {
    "alirezarezvani": "4a3c05b69e",
    "K-Dense-AI": "0807ddbc5c",
    "anthropics": "35414756ca",
}

# Files/dirs never redistributed (large binaries, schemas, vendored, tests).
EXCLUDE_SUFFIXES = {
    ".xsd",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".pdf",
    ".ico",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".zip",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}
EXCLUDE_NAMES = {".git", "__pycache__", "node_modules", "tests", ".pytest_cache"}

ROW = re.compile(r"^\|\s*`([^`]+)`.*?(https://github\.com/\S+?)\s*\|")
TREE = re.compile(r"github\.com/([^/]+)/([^/]+)/tree/main/(.+)$")

# A skill authored here has no upstream, so it has no pin, no HEAD, and nothing to fetch or
# diff against. That is a third class, not a missing one: `owner is None` marks it, and every
# consumer below must branch on it rather than treat it as an unresolved upstream.
#
# Deliberately NOT pointing the row at this repo's own GitHub URL: verifying a file against
# the repo it lives in is circular.
ROW_FIRST_PARTY = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*—\s*\(first-party\)\s*\|")


def load_pins() -> dict[str, str]:
    if PINS_FILE.exists():
        return json.loads(PINS_FILE.read_text())
    return dict(SHA_DEFAULT)


def rows() -> list[tuple[str, str | None, str | None, str | None, str | None]]:
    """(profile, skill, owner, repo, path) for every skill in every NOTICE.md.

    First-party skills come back with `owner`/`repo`/`path` all None. They are returned rather
    than skipped because this list is the single answer to "what is bundled" — it drives the
    NOTICE-vs-disk consistency test, and a skill omitted here would read as unadvertised.
    """
    out = []
    for notice in sorted(PROFILES.glob("*/NOTICE.md")):
        profile = notice.parent.name
        for line in notice.read_text().splitlines():
            fp = ROW_FIRST_PARTY.match(line)
            if fp:
                out.append((profile, fp.group(1), None, None, None))
                continue
            m = ROW.match(line)
            if not m:
                continue
            tm = TREE.search(m.group(2))
            if not tm:
                continue
            owner, repo, path = tm.groups()
            out.append((profile, m.group(1), owner, repo, path))
    return out


def fetch(url: str) -> tuple[int | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return None, str(e)[:60]


def _resolve_head(owner: str, repo: str) -> str | None:
    """Full HEAD SHA of the repo's `main` branch via the GitHub API, or None on any error.

    The SINGLE network seam for the currency check (tests monkeypatch this). Network is
    OPTIONAL: a None return degrades to UNKNOWN (WARN), never a hard failure — offline CI
    must stay green.
    """
    code, body = fetch(f"https://api.github.com/repos/{owner}/{repo}/commits/main")
    if code != 200:
        return None
    try:
        sha = json.loads(body).get("sha")
    except (json.JSONDecodeError, AttributeError):
        return None
    return sha if isinstance(sha, str) and sha else None


def do_currency() -> int:
    """Compare each bundled pin against the upstream HEAD (pin-vs-HEAD currency).

    Length-agnostic: a pin (10-char in skill-pins.json) is CURRENT exactly when it is a
    prefix of the upstream full 40-char SHA — no truncation guesswork. STALE if it isn't;
    UNKNOWN (WARN, never fail) when HEAD can't be resolved. Exit 1 iff any repo is STALE.
    """
    pins = load_pins()
    # First-party skills have no upstream HEAD to compare a pin against — skip, don't report.
    repos = sorted({(owner, repo) for _, _, owner, repo, _ in rows() if owner is not None})
    print("currency check (pin vs upstream HEAD):")
    any_stale = False
    for owner, repo in repos:
        pin = pins.get(owner, SHA_DEFAULT.get(owner, "?"))
        head = _resolve_head(owner, repo)
        if head is None:
            verdict = "UNKNOWN(network)"
        elif head.startswith(pin):
            verdict = "CURRENT"
        else:
            verdict = f"STALE({pin}→{head[: len(pin)]})"
            any_stale = True
        print(f"  {owner + '/' + repo:<34} {pin:<12} {verdict}")
    return 1 if any_stale else 0


def norm(text: str) -> list[str]:
    """Lines with trailing whitespace AND trailing blank lines stripped.

    Our pre-commit (trailing-whitespace + end-of-file-fixer) normalizes both, so
    a bundled file differing from upstream only in that way is WS-ONLY, not DIFFERS.
    """
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _ignore(_dir: str, names: list[str]) -> set[str]:
    skip = set()
    for n in names:
        if n in EXCLUDE_NAMES or any(n.endswith(s) for s in EXCLUDE_SUFFIXES):
            skip.add(n)
    return skip


def do_sync() -> int:
    by_repo: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
    for profile, skill, owner, repo, path in rows():
        # Skipping first-party is a DATA-LOSS guard, not tidiness: `copytree(..., dirs_exist_ok=True)`
        # below overwrites the destination skill dir with upstream content. A first-party row that
        # reached here would either clone `github.com/None/None` and abort the whole sync, or — if
        # a same-named upstream ever existed — silently overwrite authored work.
        if owner is None:
            continue
        by_repo.setdefault((owner, repo), []).append((profile, skill, path))

    pins: dict[str, str] = {}
    synced = 0
    with tempfile.TemporaryDirectory(prefix="skill-sync.") as tmp:
        for (owner, repo), items in by_repo.items():
            clone = Path(tmp) / f"{owner}__{repo}"
            url = f"https://github.com/{owner}/{repo}"
            print(f"[clone] {url}")
            rc = subprocess.run(
                ["git", "clone", "--depth", "1", "-q", url, str(clone)],
                capture_output=True,
                text=True,
            )
            if rc.returncode != 0:
                sys.stderr.write(f"ERROR: clone failed for {url}: {rc.stderr}\n")
                return 1
            head = subprocess.run(
                ["git", "-C", str(clone), "rev-parse", "--short=10", "HEAD"],
                capture_output=True,
                text=True,
            ).stdout.strip()
            pins[owner] = head
            for profile, skill, path in items:
                src = clone / path
                dst = PROFILES / profile / "skills" / skill
                if not src.is_dir():
                    sys.stderr.write(f"WARN: upstream path missing: {owner}/{repo}/{path}\n")
                    continue
                # Mirror the whole text tree (binaries/tests excluded); additive,
                # so a preserved LICENSE.txt absent upstream is kept.
                shutil.copytree(src, dst, dirs_exist_ok=True, ignore=_ignore)
                synced += 1

    pins_json = json.dumps(pins, indent=2) + "\n"
    PINS_FILE.write_text(pins_json)
    # Keep the shipped package-data copy in lockstep so a pip-installed `audit` resolves
    # pins (a test asserts these two are byte-identical).
    (REPO / "claude_bootstrap" / "skill-pins.json").write_text(pins_json)
    print(f"\n[pins] wrote {PINS_FILE.relative_to(REPO)} (+ package copy): {pins}")
    print(f"[sync] mirrored {synced} skill tree(s) from {len(by_repo)} repo(s).")
    print("Run `git status` / `git diff` for the file-level changes (this mirrors the")
    print(
        f"full text tree, not just SKILL.md), then `pytest` + a plain verify (expect {synced}/{synced} EXACT/WS-ONLY)."
    )
    return 0


def do_verify() -> int:
    pins = load_pins()
    results: list[tuple[str, str, str, str]] = []
    for profile, skill, owner, repo, path in rows():
        bundled = PROFILES / profile / "skills" / skill / "SKILL.md"
        if owner is None:
            # Authored here: nothing upstream to fetch or diff against. Still assert the file is
            # actually on disk, so a NOTICE row can't advertise a skill that does not ship.
            verdict = "FIRST-PARTY" if bundled.exists() else "NO-BUNDLED-FILE"
            results.append((profile, skill, verdict, "this repo (MIT)"))
            continue
        sha = pins.get(owner, SHA_DEFAULT.get(owner, "?"))
        if not bundled.exists():
            results.append((profile, skill, "NO-BUNDLED-FILE", f"{owner}@{sha}"))
            continue
        code, body = fetch(f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}/SKILL.md")
        if code != 200:
            results.append((profile, skill, f"FETCH-{code}", f"{owner}@{sha}"))
            continue
        bd = bundled.read_text()
        if body == bd:
            v = "EXACT"
        elif norm(body) == norm(bd):
            v = "WS-ONLY"
        else:
            u, b = norm(body), norm(bd)
            nd = sum(1 for a, c in zip(u, b, strict=False) if a != c) + abs(len(u) - len(b))
            v = f"DIFFERS({nd}ln)"
        results.append((profile, skill, v, f"{owner}@{sha}"))

    print(f"{'profile':<13} {'skill':<26} {'verdict':<14} source")
    print("-" * 78)
    counts: dict[str, int] = {}
    for profile, skill, verdict, src in results:
        counts[verdict.split("(")[0]] = counts.get(verdict.split("(")[0], 0) + 1
        print(f"{profile:<13} {skill:<26} {verdict:<14} {src}")
    print("-" * 78)
    print("totals:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())), f"| {len(results)} skills")
    return 0 if all(r[2].startswith(("EXACT", "WS-ONLY", "FIRST-PARTY")) for r in results) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--sync", action="store_true", help="refresh bundled skills from upstream HEAD + write pins"
    )
    ap.add_argument(
        "--check-currency",
        action="store_true",
        help="compare each bundled pin against upstream HEAD (CURRENT/STALE/UNKNOWN); exit 1 if any STALE",
    )
    args = ap.parse_args()
    if args.check_currency:
        return do_currency()
    return do_sync() if args.sync else do_verify()


if __name__ == "__main__":
    sys.exit(main())
