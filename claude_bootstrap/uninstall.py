#!/usr/bin/env python3
"""Reverse a claude-bootstrap emit using the manifest written at install time.

Reads target/.claude/.bootstrap-manifest.json. Removes files whose current
sha256 still matches what we emitted; user-modified files are kept and reported.
Reverts the .gitignore lines we manage, then removes the manifest itself and any
directories we emptied. Safe by construction: nothing whose content diverged
from the manifest is ever deleted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from .install import GITIGNORE_MARKER, MANIFEST_REL


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_files(target: Path, manifest: dict) -> list[tuple[str, str]]:
    """For each manifest file return (rel, action): remove | modified-kept | missing."""
    results: list[tuple[str, str]] = []
    for entry in manifest.get("files") or []:
        rel = entry["path"]
        p = target / rel
        if not p.exists():
            results.append((rel, "missing"))
        elif _sha256(p) == entry.get("sha256"):
            results.append((rel, "remove"))
        else:
            results.append((rel, "modified-kept"))
    return results


def revert_gitignore(target: Path, managed: list[str], *, check: bool) -> str:
    """Strip our marker + managed lines from .gitignore.

    If only comments/blank lines remain afterwards, the file was wholly ours →
    remove it. If the user has real (non-comment) entries, keep the file. User
    entries are never deleted.
    """
    gi = target / ".gitignore"
    if not gi.exists():
        return "absent"
    # Work in BYTES so we never translate the user's line endings (CRLF) — fire-test Bug 6c.
    data = gi.read_bytes()
    marker = GITIGNORE_MARKER.encode()
    idx = data.find(marker)
    if idx != -1:
        # Soft-merge case: our block is the marker onward, preceded by exactly one separator
        # "\n" that install always adds. Byte-restore the user's original (everything before)
        # by dropping that one newline — never strip by managed-set (would delete the user's
        # overlapping entries) and never normalize EOL/blanks. (fire-test Bug 6 / 6b / 6c)
        before = data[:idx]
        if before.endswith(b"\n"):
            before = before[:-1]
        removed = data[idx:].rstrip(b"\n").count(b"\n") + 1
        if check:
            return (
                f"would-revert ({removed} lines)"
                if before.strip()
                else f"would-remove-file ({removed} lines)"
            )
        if not before.strip():
            gi.unlink()
            return f"removed ({removed} lines)"
        gi.write_bytes(before)
        return f"reverted ({removed} lines)"
    # No marker: the file was created wholesale by us iff its real lines ⊆ managed.
    managed_set = {m.strip() for m in (managed or [])}
    lines = data.decode("utf-8", "replace").splitlines()
    real = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    if real and all(line.strip() in managed_set for line in real):
        if not check:
            gi.unlink()
        return f"{'would-remove-file' if check else 'removed'} ({len(lines)} lines)"
    return "unchanged"


def _prune_empty_dirs(target: Path, rels: list[str]) -> list[str]:
    """rmdir directories we emptied (deepest first); never the target root."""
    dirs: set[Path] = set()
    for rel in rels:
        parent = (target / rel).parent
        while parent != target and target in parent.parents:
            dirs.add(parent)
            parent = parent.parent
    dirs.add(target / ".claude")
    removed: list[str] = []
    for d in sorted(dirs, key=lambda p: len(p.parts), reverse=True):
        try:
            d.rmdir()
            removed.append(str(d.relative_to(target)))
        except OSError:
            pass  # not empty (user content) or already gone — leave it
    return removed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Reverse a claude-bootstrap emit using its install manifest.",
    )
    p.add_argument("--target", default=".", help="target project directory (default: cwd)")
    p.add_argument("--check", action="store_true", help="dry-run: report removals without deleting")
    p.add_argument("--quiet", action="store_true", help="suppress JSON output, only errors")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.target).resolve()
    manifest_path = target / MANIFEST_REL
    if not manifest_path.exists():
        sys.stderr.write(f"ERROR: no install manifest at {manifest_path}; nothing to uninstall\n")
        return 1
    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        sys.stderr.write(f"ERROR: invalid manifest JSON in {manifest_path}: {e}\n")
        return 1

    file_plan = plan_files(target, manifest)
    gi_status = revert_gitignore(target, manifest.get("gitignore_added") or [], check=args.check)

    removed_dirs: list[str] = []
    if not args.check:
        for rel, action in file_plan:
            if action == "remove":
                (target / rel).unlink()
        manifest_path.unlink()
        removed_rels = [rel for rel, action in file_plan if action == "remove"] + [MANIFEST_REL]
        removed_dirs = _prune_empty_dirs(target, removed_rels)

    def present(action: str) -> str:
        return "would-remove" if (args.check and action == "remove") else action

    summary = {
        "target": str(target),
        "check_mode": args.check,
        "files": [{"path": rel, "action": present(action)} for rel, action in file_plan],
        "manifest": "would-remove" if args.check else "removed",
        "gitignore": gi_status,
        "removed_dirs": removed_dirs,
    }
    if not args.quiet:
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
