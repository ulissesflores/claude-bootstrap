<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <img src="docs/assets/logo-light.svg" alt="claude-bootstrap" width="430">
</picture>

### Detect, scaffold, and reverse a complete Claude Code setup — in one command.

`claude-bootstrap` inspects your project, tells you **why** it picked a profile, shows the plan, asks once — then emits a full `.claude/` tree: a permissions baseline, curated **license-audited** skills, and path-scoped rules. Idempotent, with `--check` and a real `uninstall`.

![status](https://img.shields.io/badge/status-stable-3fb950?style=flat-square)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21894809.svg)](https://doi.org/10.5281/zenodo.21894809)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)
![tests](https://img.shields.io/badge/tests-271%2F271-3fb950?style=flat-square)
![skills](https://img.shields.io/badge/skills-30%20provenance--verified-7C5CFF?style=flat-square)

[Why](#why-it-exists) · [Install](#install) · [Quick start](#quick-start) · [Profiles](#profiles) · [What you get](#what-you-get) · [Docs](docs/) · [Contributing](CONTRIBUTING.md)

<br/>

<img src="docs/assets/demo.gif" alt="claude-bootstrap init: detect → plan → emit → reversible uninstall" width="860">

🌐 [English](README.md) · [Português](README.pt-br.md) · [Español](README.es.md) · [Italiano](README.it.md) · [עברית](README.he.md)

</div>

<!-- Badges to enable post-release (the PyPI ones need the package on PyPI):
![PyPI](https://img.shields.io/pypi/v/claude-bootstrap?style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/claude-bootstrap?style=flat-square)
![CI](https://img.shields.io/github/actions/workflow/status/ulissesflores/claude-bootstrap/ci.yml?branch=main&style=flat-square)
-->

> [!NOTE]
> **`v1.0.0` — first public release (2026-08-11).** Install from a clone or with `pip install git+https://github.com/ulissesflores/claude-bootstrap` ([Install](#install)). The PyPI package name follows via the release workflow.

---

## Why it exists

Claude Code ships its own `/init` — and an interactive setup behind `CLAUDE_CODE_NEW_INIT=1` — that writes a `CLAUDE.md`. `claude-bootstrap` is **not a replacement**; it's complementary, and deliberately does more on the axes that matter for a reproducible, auditable setup you re-run across many repos:

| | Native `claude /init` | `claude-bootstrap` |
|---|---|---|
| **Writes** | `CLAUDE.md` (conversational; explores your code) | the whole `.claude/` tree from a **detected profile** |
| **Permissions** | does **not** touch `settings.json` | emits a `settings.json` allow/deny **baseline** |
| **Skills / rules** | — | license-audited, **provenance-verified** skill bundles + path-scoped rules |
| **Re-run** | per session | **idempotent**, with `--check`, full `uninstall`, per-file manifest |
| **Confidence** | — | shows *why* the profile was chosen, asks before writing, every artifact prunable |

Use native `/init` for a quick conversational `CLAUDE.md`. Reach for `claude-bootstrap` when you want a **reproducible, auditable, profile-based** `.claude/` baseline. (More: [`docs/02-state-of-the-art.md`](docs/02-state-of-the-art.md) §7.2.)

---

## What you get

- 🔎 **Detect, then explain.** Scans the project and prints the *evidence* for the profile it picks (e.g. `pyproject.toml found, torch in deps → data-science`) — never a black box.
- ✋ **Confirm before write.** Shows the plan via `--check`, asks `[y/N]`, writes nothing on decline. Skippable with `--yes`/`--non-interactive` for CI.
- 🧱 **A real `.claude/` tree.** `CLAUDE.md` (≤60-line policy), `PROJECT-STATE.md`, a `settings.json` permissions baseline, profile skills + path-scoped rules, and subdirectory `CLAUDE.md` files where a folder has a distinct role.
- ♻️ **Idempotent + reversible.** Re-running never clobbers your edits (create-only; `<file>.new` on `update`). A manifest records every emitted file so `claude-bootstrap uninstall` reverses the whole thing — and **keeps any file you modified**.
- 📦 **License-audited skills with verified provenance.** 30 bundled skills across profiles: 25 vendored, each pinned to an upstream commit and **content-verified** (`scripts/verify-skill-provenance.py`; a weekly CI job flags drift), plus 5 **first-party** skills authored in this repository under its own MIT licence. Every bundled skill carries a redistribution licence we actually read — MIT or Apache-2.0 — with its full text shipped alongside. Four Anthropic skills were **de-bundled 2026-07-26** because they carry no such grant; we point at upstream instead of redistributing them.
- 🧹 **Anti-bloat by design.** Everything is plain Markdown/JSON you can read, edit, or delete — and the tool tells you how (`--check`, `skill remove`, `uninstall`).

---

## Install

> [!IMPORTANT]
> Not on PyPI yet — install from a clone:
>
> ```bash
> git clone https://github.com/ulissesflores/claude-bootstrap
> cd claude-bootstrap
> bin/bootstrap.sh init --profile=universal-software      # or: uv run -m claude_bootstrap.cli init
> ```

The curl method is live now; `uv` / `pipx` / `pip` activate when the package lands on PyPI:

| Method | Command |
|---|---|
| uv (recommended) | `uv tool install claude-bootstrap` |
| pipx | `pipx install claude-bootstrap` |
| pip | `pip install claude-bootstrap` |
| curl | `curl -LsSf https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh \| bash` |

Verify: `claude-bootstrap version` → `v1.0.0` or later. Requires **Python 3.11+**.

---

## Quick start

```bash
# 1. (optional) see what kind of project this is — read-only
claude-bootstrap detect

# 2. scaffold: detect → rationale → plan → confirm → emit
claude-bootstrap init --profile data-science

# 3. health-check the install (13 checks)
claude-bootstrap doctor

# changed your mind? reverse the whole emit (keeps files you edited)
claude-bootstrap uninstall
```

> [!TIP]
> `claude-bootstrap init --check` prints the full action plan and writes nothing — the safest way to preview.

---

## Profiles

Single-stack repos get one profile; **monorepos get a union of all detected code stacks**. Adding a profile is zero-touch on the others. Each bundles skills with per-skill provenance in its `NOTICE.md`.

| Profile | Bundled skills | Upstream |
|---|---|---|
| `universal-software` | 5 | — (first-party, MIT) |
| `academic` | 3 | `K-Dense-AI/scientific-agent-skills` (MIT) |
| `data-science` | 6 | `alirezarezvani/claude-skills` (MIT) |
| `frontend` | 7 | `anthropics/skills` (Apache-2.0) + `alirezarezvani/claude-skills` (MIT) |
| `devops` | 5 | `alirezarezvani/claude-skills` (MIT) |
| `backend` | 4 | `alirezarezvani/claude-skills` (MIT) |

`detect` scans filesystem signals (`*.tex` → academic, `torch`/`tensorflow` in deps → data-science, `package.json`+`tsconfig` → frontend, a web framework → backend, `*.tf`/`Chart.yaml` → devops). A **monorepo** with several stacks in sub-projects (e.g. `frontend/` + `backend/`) emits a single root `.claude/` **union** — union permissions + all skills + path-scoped `rules/<stack>.md` — plus a thin `<subdir>/CLAUDE.md` per sub-project. `academic` stays exclusive (whole-repo). Details: [`docs/05-profiles.md`](docs/05-profiles.md).

<div align="center"><img src="docs/assets/detect.gif" alt="claude-bootstrap detect across four project types" width="640"></div>

---

## What gets installed

```
your-project/
├── CLAUDE.md                      # project instructions (≤60-line policy)
├── PROJECT-STATE.md               # curated state (you edit; not Claude's auto-memory)
├── .gitignore                     # soft-merged with yours
└── .claude/
    ├── settings.json              # permissions allow/deny + env (profile-merged)
    ├── skills/<name>/             # curated, license-audited skills
    ├── rules/<name>.md            # path-scoped rules
    └── .bootstrap-manifest.json   # records the emit so `uninstall` reverses it safely
```

All files are **create-only**: re-running won't overwrite your edits; `update` writes `<file>.new` for review. **It's just files — prune freely.**

---

## Distribution

Beyond the CLI, each curated profile is also packaged as a **Claude Code plugin** via a [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) — so the bundles can be pulled with `/plugin install`.

---

## Docs

Organized by intent — start where your need is. Full index: [`docs/`](docs/).

| You want to… | Read |
|---|---|
| Understand the architecture & flow | [`00-overview`](docs/00-overview.md) · [`06-bootstrap-flow`](docs/06-bootstrap-flow.md) |
| Match the current Claude Code spec | [`01-canonical-anthropic`](docs/01-canonical-anthropic.md) · [`02-state-of-the-art`](docs/02-state-of-the-art.md) |
| Avoid common mistakes | [`03-anti-patterns`](docs/03-anti-patterns.md) |
| Work with skills & profiles | [`04-skills-curated`](docs/04-skills-curated.md) · [`05-profiles`](docs/05-profiles.md) |
| Look up a term / get unstuck | [`07-glossary`](docs/07-glossary.md) · [`08-faq`](docs/08-faq.md) |

---

## Contributing

Issues and PRs welcome. Dev setup is one command (`uv sync`), commits follow [Conventional Commits](https://www.conventionalcommits.org), and everything is gated by `pytest` + `pre-commit`. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md).

---

## License

[MIT](LICENSE) © Carlos Ulisses Flores. Bundled third-party skills retain their upstream licenses (MIT or Apache-2.0) — see each profile's `NOTICE.md` and the `LICENSE.txt` that ships inside every skill directory. The first-party skills in `universal-software` are MIT under this project's own license. Built one layer above [`superpowers`](https://github.com/obra/superpowers); declares the dependency, never duplicates it.
