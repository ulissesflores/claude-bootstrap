# demo.tape — source for docs/assets/demo.gif (regenerated in CI by .github/workflows/demo.yml).
# Run locally: `vhs docs/assets/demo.tape` (needs `claude-bootstrap` on PATH).
# Uses --non-interactive so the questionary interview never blocks vhs; still shows the
# real flow: detect rationale → dry-run plan → emit + anti-bloat footer → reversible uninstall.

Output docs/assets/demo.gif

Set Shell bash
Set FontSize 18
Set Width 1180
Set Height 720
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 45ms

# hidden setup: a throwaway sample project so detect has real signals.
# The dir name is FIXED, not `mktemp -d`: `detect` prints the resolved `scanned_path` into the
# JSON, and macOS's mktemp returns $DARWIN_USER_TEMP_DIR — an opaque per-user handle that a
# local render would bake into this public artifact.
Hide
Type `d=/tmp/claude-bootstrap-demo; rm -rf "$d"; mkdir -p "$d"; cd "$d"`
Enter
Type `printf '[project]\nname = "demo"\ndependencies = ["torch", "pandas"]\n' > pyproject.toml && clear`
Enter
Show

Type "claude-bootstrap detect ."
Sleep 500ms
Enter
Sleep 2.5s

Type "claude-bootstrap init --check --non-interactive --profile data-science  # dry-run"
Sleep 500ms
Enter
Sleep 2.5s

Type "claude-bootstrap init --non-interactive --profile data-science"
Sleep 500ms
Enter
Sleep 3s

Type "claude-bootstrap uninstall --yes   # reverse it — keeps any file you edited"
Sleep 500ms
Enter
Sleep 3s
