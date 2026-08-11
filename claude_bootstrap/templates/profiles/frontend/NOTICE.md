# Frontend profile — provenance and licensing

> claude-bootstrap v1.0.0 bundles 7 skills in `skills/`. Each skill is redistributed under its upstream license. License files are preserved verbatim alongside the `SKILL.md` content. (`theme-factory` was de-bundled 2026-06-06 — slide-deck theming misfit.)

| Skill | Upstream | License | URL |
|---|---|---|---|
| `frontend-design` | `anthropics/skills` | Per `LICENSE.txt` (preserved) | https://github.com/anthropics/skills/tree/main/skills/frontend-design |
| `web-artifacts-builder` | `anthropics/skills` | Per `LICENSE.txt` (preserved) | https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder |
| `webapp-testing` | `anthropics/skills` | Per `LICENSE.txt` (preserved) | https://github.com/anthropics/skills/tree/main/skills/webapp-testing |
| `senior-frontend` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/skills/senior-frontend |
| `browser-automation` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/browser-automation |
| `ui-design-system` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/product-team/skills/ui-design-system |
| `full-page-screenshot` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/full-page-screenshot |

## Distribution rationale

- **Anthropic skills** here are **Apache-2.0** (verified against each `LICENSE.txt`, not inferred), which is why they may be redistributed at all — unlike `docx`/`pdf`/`pptx`/`doc-coauthoring`, which were de-bundled 2026-07-26 (see the `academic` NOTICE.md). Their `LICENSE.txt` is preserved next to `SKILL.md` and travels into your tree, satisfying Apache-2.0 §4(a). `frontend-design`'s copy is 177 lines vs 202 for the other two; the delta is only the Apache appendix boilerplate, verified by diff — the terms are identical.
- **Modification notice (Apache-2.0 §4(b))**: `web-artifacts-builder` and `webapp-testing` differ from upstream by **trailing-whitespace normalization only**, applied by this repo's pre-commit hooks. No substantive change. `frontend-design` is byte-identical to upstream.
- **alirezarezvani skills** are MIT-licensed at the repository level (`LICENSE` in repo root). MIT requires the copyright and permission notice to travel with every copy, so the full text ships as `LICENSE.txt` **inside each skill directory** — a profile-level NOTICE alone would not reach the user's tree, since `init` copies `skills/<name>/**` only.

## Binaries excluded

For installation efficiency, the following large binary assets from upstream were NOT redistributed:

- `web-artifacts-builder/scripts/shadcn-components.tar.gz` — fetched at runtime by `scripts/init-artifact.sh`

Refer to the upstream URL above to obtain the full skill bundle.

## Provenance pins (re-synced + content-verified 2026-06-03)

All 7 skills synced to upstream HEAD (full text tree) via `scripts/verify-skill-provenance.py --sync` and content-verified. Pins in [`scripts/skill-pins.json`](../../../../scripts/skill-pins.json); weekly drift check `.github/workflows/skill-drift.yml`.

- ✅ **pinned** at the `anthropics/skills` commit recorded in `scripts/skill-pins.json`: `frontend-design`, `web-artifacts-builder`, `webapp-testing`
- ✅ **pinned** at the `alirezarezvani/claude-skills` commit recorded in `scripts/skill-pins.json`: `browser-automation`, `ui-design-system`, `full-page-screenshot`, `senior-frontend` (now complete — was the 473/572 prefix; its `references/` + `scripts/` are now bundled).
