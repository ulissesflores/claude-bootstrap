"""D10 — docs/01 currency sweep guard, over both language copies.

Asserts that the canonical-Anthropic reference stays current for the surfaces
verified live vs code.claude.com/docs on 2026-06-08: the full set of 30 hook events,
the sandbox block (incl. the credential denyRead warning), the opt-in plugin field,
and the monorepo CLAUDE.md exclusion setting. A drift in any of these names is the
canary that the doc has rotted against the official schema.

The doc ships twice — `docs/` (English, canonical) and `docs/pt-br/` (the mirror).
Every check runs against both: the hook names, setting keys and handler types are
language-invariant identifiers, so a PT-BR-only rot would otherwise pass unnoticed.
Only the prose anchors that scope a check to a block are language-specific, and they
live in LANGS below rather than inline in the tests.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Per-copy prose anchors. Changing a heading or a bullet label in docs/01 means
# changing the matching entry here — that coupling is the point.
LANGS = {
    "en": {
        "path": REPO_ROOT / "docs" / "01-canonical-anthropic.md",
        "event_block_start": "complete lifecycle",
        "event_block_end": "Handler types",
        "event_count_prose": r"complete lifecycle — \*\*(\d+)\*\*",
        "not_emittable": ("does not emit them", "non-emittable"),
    },
    "pt-br": {
        "path": REPO_ROOT / "docs" / "pt-br" / "01-canonical-anthropic.md",
        "event_block_start": "lifecycle completo",
        "event_block_end": "Tipos de handler",
        "event_count_prose": r"lifecycle completo — \*\*(\d+)\*\*",
        "not_emittable": ("não os emite", "não-emittable"),
    },
}

pytestmark = pytest.mark.parametrize("lang", sorted(LANGS), ids=sorted(LANGS))

# Verified verbatim vs /docs/en/hooks on 2026-06-08 (GATE: list complete and exact).
HOOK_EVENTS_30 = [
    "SessionStart",
    "Setup",
    "UserPromptSubmit",
    "UserPromptExpansion",
    "PreToolUse",
    "PermissionRequest",
    "PermissionDenied",
    "PostToolUse",
    "PostToolUseFailure",
    "PostToolBatch",
    "Notification",
    "MessageDisplay",
    "SubagentStart",
    "SubagentStop",
    "TaskCreated",
    "TaskCompleted",
    "Stop",
    "StopFailure",
    "TeammateIdle",
    "InstructionsLoaded",
    "ConfigChange",
    "CwdChanged",
    "FileChanged",
    "WorktreeCreate",
    "WorktreeRemove",
    "PreCompact",
    "PostCompact",
    "Elicitation",
    "ElicitationResult",
    "SessionEnd",
]

# Tokens that must remain present for the swept surfaces (sandbox / plugins / settings).
CURRENCY_TOKENS = [
    "sandbox",
    "denyRead",
    "defaultEnabled",
    "claudeMdExcludes",
    "mcp_tool",  # hook handler type (was wrongly "mcp" before D10)
]


def _docs_text(lang: str) -> str:
    return LANGS[lang]["path"].read_text()


def _canonical_event_block(lang: str) -> str:
    """The §5 'Events (complete lifecycle)' bullet + sub-bullets — the list a reader sees.

    Scoping to this block (not the whole doc) is load-bearing: ~6 event names are also
    backtick-quoted in the exit-code table, so a whole-doc substring check would let the
    canonical list silently drop a row while staying green.
    """
    text = _docs_text(lang)
    start = text.index(LANGS[lang]["event_block_start"])
    end = text.index(LANGS[lang]["event_block_end"], start)
    return text[start:end]


def test_canonical_event_list_is_exactly_the_30(lang):
    tokens = set(re.findall(r"`([A-Za-z]+)`", _canonical_event_block(lang)))
    assert tokens == set(HOOK_EVENTS_30), (
        f"canonical event-list drift in {lang} — missing={set(HOOK_EVENTS_30) - tokens}, "
        f"extra={tokens - set(HOOK_EVENTS_30)}"
    )


def test_event_count_prose_says_30(lang):
    m = re.search(LANGS[lang]["event_count_prose"], _docs_text(lang))
    assert m and m.group(1) == "30", f"the {lang} §5 prose event count must read **30**"


def test_exactly_30_distinct_events_listed(lang):
    # guard against silently dropping/adding an event in the pinned constant itself
    assert len(set(HOOK_EVENTS_30)) == 30


def test_currency_tokens_present(lang):
    text = _docs_text(lang)
    missing = [t for t in CURRENCY_TOKENS if t not in text]
    assert not missing, f"docs/01 ({lang}) missing currency tokens: {missing}"


def test_sandbox_credential_warning_present(lang):
    text = _docs_text(lang)
    # the load-bearing security note: default still reads ~/.aws and ~/.ssh
    assert "~/.aws" in text and "~/.ssh" in text


def test_docs_state_workflows_and_routines_not_emittable(lang):
    # D12 (doc-only): the §11.1 boundary must say the scaffolder emits neither
    # Workflows (model-generated JS) nor Routines (server-side).
    text = _docs_text(lang)
    assert "Workflows & routines" in text
    for phrase in LANGS[lang]["not_emittable"]:
        assert phrase in text, f"docs/01 ({lang}) must state {phrase!r}"


def test_no_box_drawing(lang):
    # this repo's CLAUDE.md bans box-drawing in docs; §2/§7/§10 used to carry 47 lines of it
    text = _docs_text(lang)
    offenders = sorted({c for c in text if 0x2500 <= ord(c) <= 0x257F})
    assert not offenders, f"docs/01 ({lang}) has box-drawing characters: {offenders}"
