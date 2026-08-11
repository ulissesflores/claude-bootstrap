"""D13b — `verify-skill-provenance.py --check-currency`: pin-vs-upstream-HEAD drift.

The pin in skill-pins.json (10-char) is CURRENT exactly when it prefixes the upstream
full SHA — length-agnostic, so a 10-char pin vs a 40-char API SHA compares correctly.
All network goes through the single `_resolve_head` seam, monkeypatched here so CI is
offline (a None return = UNKNOWN = WARN, never a hard failure).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "verify-skill-provenance.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_skill_provenance", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_currency_flags_stale(monkeypatch, capsys):
    mod = _load_module()
    # a real 40-char SHA that prefixes no pin → every repo STALE
    monkeypatch.setattr(mod, "_resolve_head", lambda owner, repo: "f" * 40)
    rc = mod.do_currency()
    out = capsys.readouterr().out
    assert "STALE" in out
    assert rc == 1


def test_currency_current(monkeypatch, capsys):
    mod = _load_module()
    pins = mod.load_pins()

    def head(owner, repo):
        # a REALISTIC full-length (40-char) SHA the pin actually prefixes — not the pin
        # verbatim, so the test fails if the compare ever truncated/round-tripped the pin
        pin = pins.get(owner, mod.SHA_DEFAULT.get(owner, ""))
        return (pin + "a" * 40)[:40]

    monkeypatch.setattr(mod, "_resolve_head", head)
    rc = mod.do_currency()
    out = capsys.readouterr().out
    assert "CURRENT" in out
    assert "STALE" not in out
    assert rc == 0


def test_currency_offline_is_warn(monkeypatch, capsys):
    mod = _load_module()
    monkeypatch.setattr(mod, "_resolve_head", lambda owner, repo: None)
    rc = mod.do_currency()
    out = capsys.readouterr().out
    assert "UNKNOWN" in out
    assert rc == 0  # offline must not fail CI


def test_plain_verify_unchanged(monkeypatch):
    # --check-currency is a third mode; plain verify (no flag) must still dispatch to
    # do_verify untouched, and the new flag must route to do_currency.
    mod = _load_module()
    called: list[str] = []
    monkeypatch.setattr(mod, "do_verify", lambda: called.append("verify") or 0)
    monkeypatch.setattr(mod, "do_currency", lambda: called.append("currency") or 0)
    monkeypatch.setattr(mod, "do_sync", lambda: called.append("sync") or 0)

    monkeypatch.setattr(sys, "argv", ["verify-skill-provenance.py"])
    mod.main()
    assert called == ["verify"]

    called.clear()
    monkeypatch.setattr(sys, "argv", ["verify-skill-provenance.py", "--check-currency"])
    mod.main()
    assert called == ["currency"]
