"""Tests for claude_bootstrap.uninstall — manifest-driven reverse of an emit."""

import json
from pathlib import Path

from conftest import run_python
from test_install import VARS_UNIVERSAL


def _install(tmp: Path):
    rc, _, err = run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp)])
    assert rc == 0, err
    assert (tmp / ".claude" / ".bootstrap-manifest.json").exists()


def test_uninstall_removes_emitted_files(tmp_project: Path):
    _install(tmp_project)
    rc, stdout, _ = run_python("uninstall.py", ["--target", str(tmp_project)])
    assert rc == 0
    assert not (tmp_project / "CLAUDE.md").exists()
    assert not (tmp_project / "PROJECT-STATE.md").exists()
    assert not (tmp_project / ".claude" / "settings.json").exists()
    # manifest itself is gone, and the emptied .claude dir is pruned
    assert not (tmp_project / ".claude" / ".bootstrap-manifest.json").exists()
    assert not (tmp_project / ".claude").exists()


def test_uninstall_preserves_modified_file(tmp_project: Path):
    _install(tmp_project)
    claude_md = tmp_project / "CLAUDE.md"
    claude_md.write_text(claude_md.read_text() + "\n# user edit\n")
    rc, stdout, _ = run_python("uninstall.py", ["--target", str(tmp_project)])
    assert rc == 0
    # user-modified file kept; reported as modified-kept
    assert claude_md.exists()
    assert "user edit" in claude_md.read_text()
    actions = {a["path"]: a["action"] for a in json.loads(stdout)["files"]}
    assert actions["CLAUDE.md"] == "modified-kept"
    # an untouched file is still removed
    assert not (tmp_project / "PROJECT-STATE.md").exists()


def test_uninstall_check_removes_nothing(tmp_project: Path):
    _install(tmp_project)
    rc, stdout, _ = run_python("uninstall.py", ["--target", str(tmp_project), "--check"])
    assert rc == 0
    assert (tmp_project / "CLAUDE.md").exists()
    assert (tmp_project / ".claude" / ".bootstrap-manifest.json").exists()
    # plan reports a removal without performing it
    actions = {a["path"]: a["action"] for a in json.loads(stdout)["files"]}
    assert actions["CLAUDE.md"] in ("would-remove", "remove")


def test_uninstall_no_manifest_errors(tmp_project: Path):
    rc, _, stderr = run_python("uninstall.py", ["--target", str(tmp_project)])
    assert rc == 1
    assert "manifest" in stderr.lower()


def test_uninstall_after_update_divergence_removes_all(tmp_project: Path):
    """A diverged update leaves the original + a .new; uninstall must remove both (Bug 2 + 3)."""
    base = json.loads(VARS_UNIVERSAL)
    a = json.dumps({**base, "project_name": "alpha-proj"})
    b = json.dumps({**base, "project_name": "beta-proj"})
    run_python("install.py", ["--vars-json", a, "--target", str(tmp_project)])
    run_python("install.py", ["--vars-json", b, "--target", str(tmp_project), "--update"])
    assert (tmp_project / "CLAUDE.md").exists() and (tmp_project / "CLAUDE.md.new").exists()
    rc, _, _ = run_python("uninstall.py", ["--target", str(tmp_project)])
    assert rc == 0
    assert not (tmp_project / "CLAUDE.md").exists(), "original (still ours) must be removed (Bug 2)"
    assert not (tmp_project / "CLAUDE.md.new").exists(), ".new orphan must be removed (Bug 3)"


def test_uninstall_byte_restores_gitignore_with_trailing_blank(tmp_project: Path):
    """A .gitignore ending in a trailing blank line must be byte-restored on uninstall (Bug 6b)."""
    original = "# my project\nnode_modules/\n\n"  # note the trailing blank line
    (tmp_project / ".gitignore").write_text(original)
    run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    run_python("uninstall.py", ["--target", str(tmp_project)])
    assert (tmp_project / ".gitignore").read_text() == original, "gitignore not byte-restored"


def test_uninstall_byte_restores_crlf_gitignore(tmp_project: Path):
    """A CRLF .gitignore must be byte-restored (no LF conversion) on uninstall (Bug 6c)."""
    original = b"# windows\r\nnode_modules/\r\n*.log\r\n"
    (tmp_project / ".gitignore").write_bytes(original)
    run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    run_python("uninstall.py", ["--target", str(tmp_project)])
    assert (tmp_project / ".gitignore").read_bytes() == original, "CRLF gitignore not byte-restored"


def test_uninstall_preserves_preexisting_gitignore_lines(tmp_project: Path):
    """Uninstall must not delete the user's own .gitignore entries that overlap ours (Bug 6)."""
    (tmp_project / ".gitignore").write_text("# my project\n__pycache__/\nmy-secret-dir/\n")
    run_python("install.py", ["--vars-json", VARS_UNIVERSAL, "--target", str(tmp_project)])
    run_python("uninstall.py", ["--target", str(tmp_project)])
    gi = (tmp_project / ".gitignore").read_text()
    assert "my-secret-dir/" in gi, "user's custom line lost"
    assert "__pycache__/" in gi, "user's pre-existing line (overlaps managed) wrongly stripped (Bug 6)"
    assert "Added by claude-bootstrap" not in gi, "our appended block should be gone"


def test_uninstall_reverts_gitignore(tmp_project: Path):
    _install(tmp_project)
    assert ".DS_Store" in (tmp_project / ".gitignore").read_text()
    rc, stdout, _ = run_python("uninstall.py", ["--target", str(tmp_project)])
    assert rc == 0
    gi = tmp_project / ".gitignore"
    # fresh-project .gitignore was wholly ours → removed (or at least our lines stripped)
    remaining = gi.read_text() if gi.exists() else ""
    assert ".DS_Store" not in remaining
    assert "node_modules/" not in remaining
