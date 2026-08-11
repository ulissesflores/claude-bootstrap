"""Emitted CLAUDE.md content guarantees (D08 auto-memory, D09 AGENTS.md interop).

The Memory block must distinguish the three memory layers without colliding with
Claude Code's native auto-memory; the template must stay within the ≤60-line policy.
"""

from __future__ import annotations

import json
from pathlib import Path

from conftest import run_python

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD_TEMPLATE = REPO_ROOT / "claude_bootstrap" / "templates" / "_base" / "CLAUDE.md.j2"


def _emit_claude_md(target: Path, **overrides) -> str:
    vars_dict = {
        "project_name": "memtest",
        "project_description": "d08/d09",
        "primary_language": "python",
        "is_monorepo": False,
        "git_remote": None,
        "profile_name": "universal-software",
        "superpowers_available": False,
        "agentic_stack_interop": False,
        "extra_rules": [],
        "generated_at": "2026-06-08",
        "bootstrap_version": "0.4.0a0",
    }
    vars_dict.update(overrides)
    rc, _, stderr = run_python("install.py", ["--vars-json", json.dumps(vars_dict), "--target", str(target)])
    assert rc == 0, stderr
    return (target / "CLAUDE.md").read_text()


# ---------------------------------------------------------------- D08


def test_memory_block_distinguishes_curated_and_auto_memory(tmp_path: Path):
    text = _emit_claude_md(tmp_path)
    # curated layer
    assert "PROJECT-STATE.md" in text
    # native auto-memory layer named distinctly (file + the term)
    assert "MEMORY.md" in text
    assert "auto-memory" in text.lower()
    # the two are not the same line
    project_line = next(ln for ln in text.splitlines() if "PROJECT-STATE.md" in ln)
    assert "MEMORY.md" not in project_line


def test_memory_block_states_bootstrap_never_writes_auto_memory(tmp_path: Path):
    text = _emit_claude_md(tmp_path)
    # anchor the never-write guarantee to the line that NAMES the auto-memory file,
    # so deleting the clause (or moving the phrase to an unrelated line) fails the test
    auto_line = next(ln for ln in text.splitlines() if "MEMORY.md" in ln and "auto-memory" in ln.lower())
    assert "never writes" in auto_line.lower()


# ---------------------------------------------------------------- D09 cardinality-conditional footer


def test_footer_singular_for_single_profile(tmp_path: Path):
    """Single-profile footer stays `profile: <name>` (byte-stable) and the Profile line is singular."""
    text = _emit_claude_md(tmp_path, profile_name="frontend")
    footer = text.strip().splitlines()[-1]
    assert footer.startswith("<!-- profile: frontend ·")
    assert "- **Profile**: `frontend`" in text
    assert "- **Profiles**:" not in text


def test_footer_plural_for_multi_profile(tmp_path: Path):
    """Multi-profile footer becomes `profiles: a, b, c` and the Profile line lists the set."""
    text = _emit_claude_md(
        tmp_path,
        profiles=["backend", "devops", "frontend"],
        stack_paths={"backend": ["services/api"]},
    )
    footer = text.strip().splitlines()[-1]
    assert footer.startswith("<!-- profiles: backend, devops, frontend ·")
    assert "- **Profiles**: `backend`, `devops`, `frontend`" in text


def test_claude_md_template_within_line_cap():
    lines = CLAUDE_MD_TEMPLATE.read_text().splitlines()
    assert len(lines) <= 60, f"CLAUDE.md.j2 is {len(lines)} lines (policy ≤60)"


# ---------------------------------------------------------------- D09


def test_agents_md_import_emitted_when_repo_ships_one(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n\nguidance\n")
    text = _emit_claude_md(tmp_path)
    lines = text.splitlines()
    # pin the functional contract, not mere presence: a Claude Code @-import resolves
    # only at column 0 and outside a fenced code block. An indented/fenced line would
    # be a dead import, so assert the directive is its own column-0 line, fences-balanced.
    assert "@AGENTS.md" in lines, "@AGENTS.md must be a column-0 import line (no indent)"
    idx = lines.index("@AGENTS.md")
    fences_before = sum(1 for ln in lines[:idx] if ln.lstrip().startswith("```"))
    assert fences_before % 2 == 0, "@AGENTS.md must not be inside a fenced code block"


def test_agents_md_import_absent_by_default(tmp_path: Path):
    text = _emit_claude_md(tmp_path)
    assert "@AGENTS.md" not in text


def test_agents_md_present_check_is_dry_run(tmp_path: Path):
    # detection runs at vars-assembly (before the --check branch), so it is construction-covered
    # for --check too; this asserts the weaker, testable guarantee: --check writes nothing.
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n")
    rc, stdout, stderr = run_python(
        "install.py",
        [
            "--vars-json",
            json.dumps(
                {
                    "project_name": "memtest",
                    "project_description": "d09",
                    "primary_language": "python",
                    "is_monorepo": False,
                    "git_remote": None,
                    "profile_name": "universal-software",
                    "superpowers_available": False,
                    "agentic_stack_interop": False,
                    "extra_rules": [],
                    "generated_at": "2026-06-08",
                    "bootstrap_version": "0.4.0a0",
                }
            ),
            "--target",
            str(tmp_path),
            "--check",
        ],
    )
    assert rc == 0, stderr
    # dry-run must not have written CLAUDE.md
    assert not (tmp_path / "CLAUDE.md").exists()


def test_docs_mention_claude_md_excludes():
    docs = (REPO_ROOT / "docs" / "01-canonical-anthropic.md").read_text()
    assert "claudeMdExcludes" in docs
