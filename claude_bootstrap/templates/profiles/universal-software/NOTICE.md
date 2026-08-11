# Universal-software profile — provenance and licensing

> claude-bootstrap v1.0.0 bundles 5 skills in `skills/`. Unlike the other profiles, these are
> **first-party**: authored in this repository, not vendored from an upstream project. They carry
> this project's MIT licence, and the full text ships as `LICENSE.txt` inside each skill directory.

| Skill | Upstream | License | URL |
|---|---|---|---|
| `newproj` | — (first-party) | MIT (this project) | — |
| `ponytail` | — (first-party) | MIT (this project) | — |
| `recover` | — (first-party) | MIT (this project) | — |
| `refactor` | — (first-party) | MIT (this project) | — |
| `vetting-agent-skills` | — (first-party) | MIT (this project) | — |

## What "first-party" means here

Every other bundled skill is a pinned copy of someone else's work, verified byte-for-byte against
an upstream commit by `scripts/verify-skill-provenance.py`. These are not. There is no upstream
repository, so there is no commit to pin, no HEAD to check for drift, and nothing to diff against.

The provenance tooling reports them as **`FIRST-PARTY`** — a third verdict alongside `EXACT` and
`WS-ONLY`, not a failure and not an unknown. `--sync` skips them: it mirrors upstream trees over
the destination directory, which for authored content would be data loss rather than an update.

The `Upstream` and `URL` cells are deliberately `—` rather than a link back to this repository.
Verifying a file against the repository it already lives in is circular.

## Licensing

These skills are covered by the repository's own MIT licence (see [`LICENSE`](../../../../LICENSE)),
Copyright (c) 2026 Carlos Ulisses Flores. MIT requires the copyright and permission notice to
travel with every copy, and `init` copies `skills/<name>/**` only — so the notice ships **inside**
each skill directory, exactly as it does for the vendored MIT skills in the other profiles.
