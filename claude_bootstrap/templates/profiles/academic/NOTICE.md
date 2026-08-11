# Academic profile — provenance and licensing

> claude-bootstrap v1.0.0 bundles 3 skills in `skills/`, all MIT-licensed from
> `K-Dense-AI/scientific-agent-skills` (Copyright (c) 2025 K-Dense Inc.). Redistributed under MIT;
> the full license text ships as `LICENSE.txt` inside each skill directory.

| Skill | Upstream | License | URL |
|---|---|---|---|
| `citation-management` | `K-Dense-AI/scientific-agent-skills` | MIT (K-Dense Inc., 2025) | https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/citation-management |
| `exploratory-data-analysis` | `K-Dense-AI/scientific-agent-skills` | MIT (K-Dense Inc., 2025) | https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/exploratory-data-analysis |
| `exa-search` | `K-Dense-AI/scientific-agent-skills` | MIT (K-Dense Inc., 2025) | https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/exa-search |

## License notes

- **K-Dense-AI scientific-skills**: repo-level MIT license (`K-Dense-AI/scientific-agent-skills/LICENSE.md`). MIT requires the copyright and permission notice to travel with every copy, so the full text ships as `LICENSE.txt` **inside each skill directory** — a profile-level NOTICE alone would not reach the user's tree, since `init` copies `skills/<name>/**` only. Per-skill frontmatter `metadata.skill-author` is preserved.

## De-bundled 2026-07-26 — not licensed for redistribution

Four skills were removed from this profile. **None of them may be redistributed**, so shipping them in a PyPI wheel and a permanent Zenodo archive was never an option:

| Skill | Upstream | Why removed |
|---|---|---|
| `docx` | `anthropics/skills` | `LICENSE.txt` is a pure restriction list with **no grant clause** — it forbids retaining copies outside Anthropic's Services, reproducing, creating derivative works, and distributing to third parties |
| `pdf` | `anthropics/skills` | Same license, byte-identical file (sha1 `33b3a5817279`) |
| `pptx` | `anthropics/skills` | Same license, byte-identical file |
| `doc-coauthoring` | `anthropics/skills` | **No license at all**: `anthropics/skills` carries no root LICENSE, and this is the only 1 of 17 skill directories there without its own `LICENSE.txt`. Absence of a license is default copyright, not a permissive default |

These are Anthropic's own skills. If you want them, get them from Anthropic directly — <https://github.com/anthropics/skills>. We do not redistribute them, and we deliberately do not automate fetching them either: that would just move the copying onto your machine.

> `xlsx` (Anthropic) was de-bundled 2026-06-06 — its content is financial modeling, a misfit for academic/data-science work, and it carries the same non-redistributable license as `docx`.

## Binaries excluded

For installation efficiency, large binary assets from upstream are NOT redistributed:

- All `.png`/`.jpg`/`.pdf` upstream reference images

Refer to upstream URLs above for the full skill bundle.

## Migration

An earlier, institution-specific academic profile has been **removed**. New and existing academic projects should use `academic` (this profile).

Its former skills were pedagogical tooling for one institution's workflow and are **not** part of this distribution.

## Provenance pins (content-verified)

All 3 skills are synced to upstream and content-verified via `scripts/verify-skill-provenance.py`. Pins in [`scripts/skill-pins.json`](../../../../scripts/skill-pins.json); weekly drift check `.github/workflows/skill-drift.yml`.

- ✅ **all 3 pinned** at `K-Dense-AI/scientific-agent-skills@0807ddbc5c`.
