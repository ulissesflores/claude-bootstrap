"""Tests for the claude-bootstrap CLI dispatcher (cli.py).

Two layers:
- `_confirm()` unit tests: in-process, monkeypatch builtins.input (no tty).
- Confirm-gate wiring tests: in-process, monkeypatch `_run_module`/`_confirm`
  so the gate logic is exercised without driving questionary through a tty.
"""

from __future__ import annotations

import json
from pathlib import Path

from claude_bootstrap import cli

# --- _confirm() unit tests -------------------------------------------------


def test_confirm_accepts_y(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "y")
    assert cli._confirm("? ") is True


def test_confirm_accepts_yes_case_insensitive(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "  YES ")
    assert cli._confirm("? ") is True


def test_confirm_rejects_n(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    assert cli._confirm("? ") is False


def test_confirm_rejects_empty_default_no(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    assert cli._confirm("? ") is False


def test_confirm_rejects_on_eof(monkeypatch):
    def boom(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", boom)
    assert cli._confirm("? ") is False


# --- confirm-gate wiring (in-process) --------------------------------------


def _recorder(calls):
    """Fake _run_module: records (name, args); writes a stub file for --output.

    The dispatcher reads back detect.json / vars.json after running those
    modules, so the stub must materialise whatever path follows --output.
    """

    def fake_run_module(name, args):
        calls.append((name, list(args)))
        if "--output" in args:
            out = args[args.index("--output") + 1]
            Path(out).write_text("{}")
        return 0

    return fake_run_module


def _install_calls(calls):
    return [args for name, args in calls if name == "install"]


def test_init_aborts_when_confirm_declined(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: False)

    rc = cli.cmd_init(["--target", str(tmp_path)])

    assert rc == 0
    installs = _install_calls(calls)
    # A plan ran (--check), but the real write (no --check) never did.
    assert installs, "expected a --check plan run before the prompt"
    assert all("--check" in args for args in installs)


def test_init_writes_when_confirm_accepted(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: True)

    rc = cli.cmd_init(["--target", str(tmp_path)])

    assert rc == 0
    installs = _install_calls(calls)
    assert any("--check" in args for args in installs), "expected a plan run"
    assert any("--check" not in args for args in installs), "expected a real write"


def test_init_non_interactive_skips_confirm(tmp_path, monkeypatch):
    calls = []
    confirmed = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: confirmed.append(True) or True)

    rc = cli.cmd_init(["--non-interactive", "--target", str(tmp_path)])

    assert rc == 0
    assert confirmed == [], "confirm must not be called in --non-interactive"
    installs = _install_calls(calls)
    assert len(installs) == 1 and "--check" not in installs[0]


def test_init_yes_skips_confirm(tmp_path, monkeypatch):
    calls = []
    confirmed = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: confirmed.append(True) or True)

    rc = cli.cmd_init(["--yes", "--target", str(tmp_path)])

    assert rc == 0
    assert confirmed == [], "confirm must not be called when --yes is passed"
    installs = _install_calls(calls)
    assert len(installs) == 1 and "--check" not in installs[0]


# --- D08: multi-profile flow (detected set → interview) --------------------


def _multi_detect_recorder(calls):
    def fake_run_module(name, args):
        calls.append((name, list(args)))
        if "--output" in args:
            out = args[args.index("--output") + 1]
            if name == "detect":
                Path(out).write_text(
                    json.dumps(
                        {
                            "profile_suggestion": "backend",
                            "profiles": ["backend", "frontend"],
                            "stack_paths": {"backend": ["services/api"], "frontend": ["apps/web"]},
                            "signals": [],
                            "mode": "init",
                        }
                    )
                )
            else:
                Path(out).write_text("{}")
        return 0

    return fake_run_module


def test_init_flows_detected_multi_set_to_interview(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_module", _multi_detect_recorder(calls))
    rc = cli.cmd_init(["--non-interactive", "--target", str(tmp_path)])
    assert rc == 0
    interview_args = next(a for n, a in calls if n == "interview")
    assert interview_args.count("--profile") == 2  # both detected profiles passed
    assert "backend" in interview_args and "frontend" in interview_args
    assert "--stack-paths-json" in interview_args


def test_init_forced_single_profile_stays_single(tmp_path, monkeypatch):
    """A user-forced single --profile takes the single path even if detect found a multi set."""
    calls = []
    monkeypatch.setattr(cli, "_run_module", _multi_detect_recorder(calls))
    rc = cli.cmd_init(["--non-interactive", "--profile", "frontend", "--target", str(tmp_path)])
    assert rc == 0
    interview_args = next(a for n, a in calls if n == "interview")
    assert interview_args.count("--profile") == 1
    assert "frontend" in interview_args
    assert "--stack-paths-json" not in interview_args


def test_init_check_skips_confirm_and_write(tmp_path, monkeypatch):
    calls = []
    confirmed = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: confirmed.append(True) or True)

    rc = cli.cmd_init(["--check", "--target", str(tmp_path)])

    assert rc == 0
    assert confirmed == [], "confirm must not be called in --check (dry-run)"
    installs = _install_calls(calls)
    assert len(installs) == 1 and "--check" in installs[0]


# --- uninstall confirm-gate wiring (in-process) ----------------------------


def _uninstall_calls(calls):
    return [args for name, args in calls if name == "uninstall"]


def test_uninstall_aborts_when_confirm_declined(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: False)

    rc = cli.cmd_uninstall(["--target", str(tmp_path)])

    assert rc == 0
    runs = _uninstall_calls(calls)
    # a plan ran (--check), but the real removal (no --check) never did
    assert runs, "expected a --check plan run before the prompt"
    assert all("--check" in args for args in runs)


def test_uninstall_removes_when_confirm_accepted(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: True)

    rc = cli.cmd_uninstall(["--target", str(tmp_path)])

    assert rc == 0
    runs = _uninstall_calls(calls)
    assert any("--check" in args for args in runs), "expected a plan run"
    assert any("--check" not in args for args in runs), "expected a real removal"


def test_uninstall_yes_skips_confirm(tmp_path, monkeypatch):
    calls = []
    confirmed = []
    monkeypatch.setattr(cli, "_run_module", _recorder(calls))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: confirmed.append(True) or True)

    rc = cli.cmd_uninstall(["--yes", "--target", str(tmp_path)])

    assert rc == 0
    assert confirmed == [], "confirm must not be called when --yes is passed"
    runs = _uninstall_calls(calls)
    assert len(runs) == 1 and "--check" not in runs[0]


# --- A6: detection rationale + anti-bloat framing --------------------------


def test_detect_rationale_with_profile():
    out = cli._render_detect_rationale(
        {
            "profile_suggestion": "data-science",
            "confidence": 0.85,
            "mode": "init",
            "signals": ["pyproject.toml found", "torch in deps"],
        }
    )
    assert "data-science" in out
    assert "85%" in out
    assert "pyproject.toml found" in out
    assert "torch in deps" in out
    assert "init" in out


def test_detect_rationale_no_profile_defaults_universal():
    out = cli._render_detect_rationale({"profile_suggestion": None, "mode": "init", "signals": []})
    assert "universal-software" in out


def test_detect_rationale_tolerates_empty_dict():
    out = cli._render_detect_rationale({})
    assert isinstance(out, str) and out  # no crash, non-empty


def test_prune_footer_lists_escape_hatches():
    out = cli._render_prune_footer()
    assert "uninstall" in out
    assert "--check" in out
    assert "skill remove" in out


def test_init_prints_prune_footer_on_write(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_run_module", _recorder([]))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: True)
    cli.cmd_init(["--target", str(tmp_path)])
    out = capsys.readouterr().out
    assert "claude-bootstrap uninstall" in out


def test_init_check_omits_prune_footer(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_run_module", _recorder([]))
    monkeypatch.setattr(cli, "_confirm", lambda *a, **k: True)
    cli.cmd_init(["--check", "--target", str(tmp_path)])
    out = capsys.readouterr().out
    assert "claude-bootstrap uninstall" not in out
