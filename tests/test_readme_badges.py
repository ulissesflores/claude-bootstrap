"""The tests badge in the READMEs must state the real size of the suite.

The badge went stale twice (75 -> 82 in 2026-06, then 249 while the suite grew to 270):
nothing forced it, because the only badge under test was the skill count. This closes the
class — the expected number comes from live pytest collection, not from a second hardcoded
copy that would rot alongside the first.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def collected_test_count() -> int:
    out = subprocess.run(
        ["uv", "run", "python", "-m", "pytest", "tests/", "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    m = re.search(r"(\d+) tests collected", out)
    assert m, f"could not parse collection count from: {out[-200:]}"
    return int(m.group(1))


def test_tests_badge_matches_the_collected_suite():
    total = collected_test_count()
    wrong = []
    for readme in sorted(REPO_ROOT.glob("README*.md")):
        for found in re.findall(r"badge/tests-(\d+)%2F(\d+)", readme.read_text()):
            if int(found[0]) != total or int(found[1]) != total:
                wrong.append(f"{readme.name} badge says {found[0]}/{found[1]}, suite has {total}")
    assert not wrong, "; ".join(wrong)
