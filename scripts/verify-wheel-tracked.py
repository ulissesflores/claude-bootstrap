#!/usr/bin/env python3
"""verify-wheel-tracked.py — every file inside the built wheel must be tracked in git.

Why this exists: `MANIFEST.in` does `recursive-include claude_bootstrap/templates *` and
`pyproject.toml` sets `include-package-data = true`, so the build reads the **filesystem**,
not git. Any untracked leftover under `templates/` — a stale skill dir nobody declares, an
editor backup, a scratch file, half of a rename — is redistributed to every user and archived
immutably on Zenodo with a DOI, carrying no NOTICE row and no licence attribution.

Every other gate reads a different source and is blind to this: `pii-scan.py` reads git,
`verify-skill-provenance.py` reads `NOTICE.md`, the test suite reads `profile.yaml`. Nobody
reads the artifact's own file list. This does.

Usage:
    python3 scripts/verify-wheel-tracked.py [path/to/wheel]

With no argument it takes the single wheel in `dist/`. Exit 0 = clean, 1 = stray files or
no wheel to check. Scope: the wheel only — the sdist additionally carries build-generated
files (`PKG-INFO`, `setup.cfg`) that are untracked by design.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def tracked_files() -> set[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return {f for f in out.split("\0") if f}


def shipped_files(wheel: Path) -> set[str]:
    """Wheel members that came from the repo — the `.dist-info/` metadata is generated."""
    with zipfile.ZipFile(wheel) as zf:
        names = zf.namelist()
    return {n for n in names if not n.endswith("/") and ".dist-info/" not in n}


def main() -> int:
    if len(sys.argv) > 1:
        wheel = Path(sys.argv[1])
        if not wheel.is_file():
            sys.stderr.write(f"ERROR: no such wheel: {wheel}\n")
            return 1
    else:
        wheels = sorted((REPO_ROOT / "dist").glob("*.whl"))
        if not wheels:
            sys.stderr.write("ERROR: no wheel in dist/ — run `uv build` (or `python -m build`) first.\n")
            return 1
        if len(wheels) > 1:
            sys.stderr.write(
                "ERROR: dist/ holds more than one wheel; pass the one to check explicitly:\n  "
                + "\n  ".join(w.name for w in wheels)
                + "\n"
            )
            return 1
        wheel = wheels[0]

    shipped = shipped_files(wheel)
    stray = sorted(shipped - tracked_files())
    if stray:
        sys.stderr.write(f"{len(stray)} untracked file(s) in {wheel.name}:\n")
        for path in stray:
            sys.stderr.write(f"  {path}\n")
        sys.stderr.write("\nEither `git add` them (with a NOTICE row if vendored) or delete them.\n")
        return 1

    print(f"{wheel.name}: {len(shipped)} shipped file(s), all tracked in git.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
