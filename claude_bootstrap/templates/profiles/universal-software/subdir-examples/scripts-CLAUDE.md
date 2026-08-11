# CLAUDE.md — `scripts/`

> Loaded automatically when editing files under `scripts/`. Use this for one-off utility scripts that don't deserve the rigor of production code. See [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) for the subdirectory `CLAUDE.md` mechanism.

## Script conventions

- **Shebang + executable**: every script starts with the right shebang (`#!/usr/bin/env bash`, `#!/usr/bin/env python3`) and is `chmod +x`. Don't require `bash script.sh` to invoke.
- **Idempotent**: re-running a script in the same state should not break things. Guard destructive operations behind checks (file exists, branch matches, etc.).
- **Fail fast**: bash scripts use `set -euo pipefail`. Python scripts raise on unexpected state, don't silently swallow.
- **Self-documenting**: a `--help` flag (or the first 10 lines of comments) tells a stranger what the script does, when to use it, and what it modifies.

## What NOT to do here

- ❌ Commit a script that depends on `~/Downloads/`, `$DESKTOP`, or other operator-specific paths without making them configurable
- ❌ Run network requests without a timeout
- ❌ Mass-modify files (`find . -exec sed -i`) without a `--dry-run` mode

## When a script outgrows this directory

If a script accumulates >200 lines, multiple commands, or significant logic, promote it to a proper module under the project package and add tests. Scripts are for one-shot tasks; if you find yourself running it weekly with edge cases, it's no longer a script.
