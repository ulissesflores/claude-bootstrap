#!/usr/bin/env python3
"""Schema drift-guard: keep emitted Claude-Code schemas tied to their live docs.

Sibling of the skill drift-guard (verify-skill-provenance.py + skill-pins.json +
skill-drift.yml). Where that guard pins bundled *skills* to upstream commits, this
one pins every schema-bearing *emit* (settings.permissions, hooks, sandbox,
agents-frontmatter, .mcp.json, plugin.json) to the official doc page that defines
it, so a doc that moves or a stale attestation surfaces in CI instead of silently
rotting.

Two failure axes, deliberately kept apart:

  default (network)  LIVENESS  — HTTP each doc URL; exit = count of dead (non-2xx)
                     URLs (mirrors validate-refs.sh `exit "$dead"`). Answers "did the
                     page disappear or move?" — auto-detected.

  --check (offline)  STALENESS — pure date arithmetic, no network. Flags any `verified`
                     attestation older than --max-age-days (default 90); exit 1 if any
                     is stale. Answers "has a human re-read this page lately?".

There is deliberately NO content hash: live doc HTML churns weekly and any content
diff would false-trip. A *changed* schema is caught by a human re-reading the page on
the staleness cadence and bumping `verified` — that bump is the only "it changed" signal.

Source of truth: scripts/schema-sources.json (override with $SCHEMA_SOURCES — used by
the tests to point at a temp file).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = REPO / "scripts" / "schema-sources.json"


def sources_path() -> Path:
    return Path(os.environ.get("SCHEMA_SOURCES", DEFAULT_SOURCES))


def load_sources() -> list[dict]:
    return json.loads(sources_path().read_text())


def fetch_status(url: str) -> int | None:
    """HTTP status for `url`, following redirects; None on a network-level failure.

    Sends a browser User-Agent: a blank UA 403s on code.claude.com (see
    validate-refs.sh, bot-block note). urlopen follows 3xx on GET, so a page that moved but still
    resolves 2xx counts as live — only a genuine 4xx/5xx or network error is "dead".
    """
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001 — any network failure counts as dead (None)
        return None


def run_liveness() -> int:
    entries = load_sources()
    print(f"{'schema':<22} {'verdict':<12} url")
    print("-" * 78)
    dead = 0
    for e in entries:
        status = fetch_status(e["url"])
        live = status is not None and 200 <= status < 300
        if not live:
            dead += 1
        verdict = "LIVE" if live else f"DEAD[{status}]"
        print(f"{e['schema']:<22} {verdict:<12} {e['url']}")
    print("-" * 78)
    print(f"totals: {len(entries) - dead} live, {dead} dead | {len(entries)} schemas")
    return dead


def run_check(max_age_days: int) -> int:
    entries = load_sources()
    today = datetime.date.today()
    print(f"{'schema':<22} {'verdict':<14} verified")
    print("-" * 78)
    stale = 0
    for e in entries:
        age = (today - datetime.date.fromisoformat(e["verified"])).days
        is_stale = age > max_age_days
        if is_stale:
            stale += 1
        verdict = f"STALE({age}d)" if is_stale else f"OK({age}d)"
        print(f"{e['schema']:<22} {verdict:<14} {e['verified']}")
    print("-" * 78)
    print(f"totals: {len(entries) - stale} ok, {stale} stale (>{max_age_days}d) | {len(entries)} schemas")
    return 1 if stale else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="offline staleness check (no network)")
    ap.add_argument(
        "--max-age-days", type=int, default=90, help="staleness threshold for --check (default 90)"
    )
    args = ap.parse_args()
    return run_check(args.max_age_days) if args.check else run_liveness()


if __name__ == "__main__":
    sys.exit(main())
