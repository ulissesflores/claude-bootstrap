# Devops profile — provenance and licensing

> claude-bootstrap v1.0.0 bundles 5 skills in `skills/`. **All 5 are MIT-licensed** from `alirezarezvani/claude-skills` (Copyright (c) 2025 Alireza Rezvani). De-bundled: `senior-devops` (2026-06-06 — no-op stub scripts); `release-manager` (2026-06-29 — REMOVED from upstream HEAD, FETCH-404 on re-sync, no longer provenance-verifiable).

| Skill | Upstream | URL |
|---|---|---|
| `ci-cd-pipeline-builder` | engineering/ | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/ci-cd-pipeline-builder |
| `kubernetes-operator` | engineering/ | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/kubernetes-operator |
| `runbook-generator` | engineering/ | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/runbook-generator |
| `observability-designer` | engineering/ | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/observability-designer |
| `secrets-vault-manager` | engineering/ | https://github.com/alirezarezvani/claude-skills/tree/main/engineering/skills/secrets-vault-manager |

## License: MIT

MIT requires the copyright and permission notice to travel with every copy, so the **full,
unabridged** text ships as `LICENSE.txt` inside each skill directory — a profile-level NOTICE alone
would not reach your tree, since `init` copies `skills/<name>/**` only. Reproduced here as well:

```
MIT License

Copyright (c) 2025 Alireza Rezvani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Upstream: https://github.com/alirezarezvani/claude-skills/blob/main/LICENSE

## Anthropic-canon note

As of the 2026-06 upstream inventory, `anthropics/skills` had **zero devops skills**. This profile is therefore 100% community-sourced. Future Anthropic devops skills (if released) should be added in a future release.

## Permissions: read-only by default

`profile.yaml` configures permissions to **allow read/plan operations** (`terraform plan`, `kubectl get`, `helm lint`) and **explicitly deny destructive operations** (`terraform apply`, `terraform destroy`, `kubectl delete`). The user/project can override locally if a CI context needs `apply` permissions, but the default protects against accidental destruction.

## Provenance pins (re-synced + content-verified 2026-06-29)

All 5 skills **re-synced to upstream HEAD** (full text tree) via `scripts/verify-skill-provenance.py --sync` and content-verified. Pin in [`scripts/skill-pins.json`](../../../../scripts/skill-pins.json); weekly drift check `.github/workflows/skill-drift.yml`.

- ✅ **all 5 pinned** at `alirezarezvani/claude-skills@4a3c05b69e`.
