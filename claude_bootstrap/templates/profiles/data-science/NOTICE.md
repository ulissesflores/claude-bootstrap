# Data-science profile — provenance and licensing

> claude-bootstrap v1.0.0 bundles 6 skills in `skills/`, all MIT-licensed from
> `alirezarezvani/claude-skills` (Copyright (c) 2025 Alireza Rezvani). Redistributed under MIT.

| Skill | Upstream | License | URL |
|---|---|---|---|
| `senior-data-scientist` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/skills/senior-data-scientist |
| `senior-ml-engineer` | `alirezarezvani/claude-skills` | MIT | https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/skills/senior-ml-engineer |
| `senior-data-engineer` | `alirezarezvani/claude-skills` | MIT | https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/skills/senior-data-engineer |
| `rag-architect` | `alirezarezvani/claude-skills` | MIT | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/rag-architect |
| `sql-database-assistant` | `alirezarezvani/claude-skills` | MIT | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/sql-database-assistant |
| `senior-computer-vision` | `alirezarezvani/claude-skills` | MIT | https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/skills/senior-computer-vision |

## License notes

- **alirezarezvani skills**: MIT-licensed at repo level (`LICENSE` in repo root, Copyright (c) 2025 Alireza Rezvani). MIT requires the copyright and permission notice to travel with every copy, so the full text ships as `LICENSE.txt` **inside each skill directory** — a profile-level NOTICE alone would not reach the user's tree, since `init` copies `skills/<name>/**` only.

> `xlsx` (Anthropic) was de-bundled 2026-06-06 — its content is financial modeling, a misfit for
> data-science.

## Binaries excluded

- Upstream test files (`tests/`) and `__pycache__` — irrelevant to redistribution
- All upstream PNG/JPG/PDF reference images

Refer to upstream URLs above for the full skill bundles.

## Provenance pins (content-verified)

All 6 skills synced to upstream HEAD (full text tree) via `scripts/verify-skill-provenance.py --sync`
and content-verified. Pins in [`scripts/skill-pins.json`](../../../../scripts/skill-pins.json); weekly
drift check `.github/workflows/skill-drift.yml`.

- ✅ **pinned** at the `alirezarezvani/claude-skills` commit recorded in `scripts/skill-pins.json`: `senior-data-scientist`, `senior-ml-engineer`, `senior-data-engineer`, `sql-database-assistant`, `senior-computer-vision`, `rag-architect`
