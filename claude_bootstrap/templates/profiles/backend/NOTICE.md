# Backend profile — provenance and licensing

> claude-bootstrap v1.0.0 bundles 4 skills in `skills/`, all from `alirezarezvani/claude-skills`
> (MIT). Each `SKILL.md` (and its bundled references/scripts/assets) is redistributed under that
> license; this NOTICE.md is the redistribution attribution. Operator-approved set (2026-06-30):
> API review + API testing + database schema + migration safety — a coherent backend/service set,
> no overlap with other profiles' skills. Pinned via `scripts/skill-pins.json`.

| Skill | Upstream | License | URL |
|---|---|---|---|
| `api-design-reviewer` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/api-design-reviewer |
| `api-test-suite-builder` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/api-test-suite-builder |
| `database-schema-designer` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/database-schema-designer |
| `migration-architect` | `alirezarezvani/claude-skills` | MIT (Alireza Rezvani, 2025) | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/migration-architect |

## Distribution rationale

- **alirezarezvani skills** are MIT-licensed at the repository level (`LICENSE` in repo root:
  "MIT License, Copyright (c) 2025 Alireza Rezvani"). We bundle the skill subtree (SKILL.md +
  references/scripts/assets) verbatim and add this NOTICE.md as the attribution. The MIT license
  requires the copyright and permission notice to travel with every copy, so the full text ships as
  `LICENSE.txt` **inside each skill directory** — a profile-level NOTICE alone would not reach the
  user's tree, since `init` copies `skills/<name>/**` only.
- Content is pinned and content-verified: `scripts/verify-skill-provenance.py` compares each bundled
  `SKILL.md` against `alirezarezvani/claude-skills` at the pinned SHA.

## Config-only note

These skills are **guidance/tooling** (API linting, test-suite scaffolding, schema/migration design).
Bundling them ships config only — claude-bootstrap never installs their dependencies or runs their
scripts during install (`install.py` shells no package manager).
