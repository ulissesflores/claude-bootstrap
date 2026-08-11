# Contributing to claude-bootstrap

Thanks for being here. Whether you're fixing a typo, curating a skill, or adding a profile — contributions are welcome, and this guide makes the path obvious.

> [!NOTE]
> `v1.0.0`: the repository is public — the issue/PR links below are live.

## Ways to contribute

- 🐛 **Report a bug** — [bug report template](https://github.com/ulissesflores/claude-bootstrap/issues/new?template=bug_report.yml) (include `claude-bootstrap version` + `doctor` output).
- 💡 **Propose a feature** — [feature request](https://github.com/ulissesflores/claude-bootstrap/issues/new?template=feature_request.yml) **before** coding; describe the *problem*, not just the solution.
- ✨ **Good first issues** — look for the [`good first issue`](https://github.com/ulissesflores/claude-bootstrap/labels/good%20first%20issue) label.
- 📚 **Improve docs** — corrections and clarity wins are always welcome.
- 🧩 **Add a profile or skill** — see the how-tos below.

## Dev setup

Requires **Python 3.11+** and [`uv`](https://docs.astral.sh/uv/) (recommended).

```bash
git clone https://github.com/ulissesflores/claude-bootstrap
cd claude-bootstrap
uv sync --extra dev          # installs the package + jinja2/pyyaml/questionary/rich + pytest/pre-commit

uv run pytest                # the test suite (expect green)
uv run pre-commit run --all-files
uv run claude-bootstrap init --profile=universal-software --check   # dry-run the CLI
```

No `uv`? `pip install -e ".[dev]"` works too.

## Pull requests

1. **Open an issue first** for non-trivial changes (>20 lines or new behavior) — avoid surprise PRs.
2. **Branch from `main`**: `git checkout -b feat/your-feature`.
3. **Write tests** for new behavior (we use TDD; don't lower coverage).
4. **Run the gates locally** before pushing (see checklist).
5. **[Conventional Commits](https://www.conventionalcommits.org/)**: `feat:` · `fix:` · `docs:` · `refactor:` · `chore:` · `test:`.

### PR checklist

- [ ] `uv run pytest` — all green
- [ ] `uv run pre-commit run --all-files` — clean
- [ ] `bash scripts/validate-refs.sh` — no new dead links (run with network access)
- [ ] Touched anything under `claude_bootstrap/templates/`? `uv build && python3
      scripts/verify-wheel-tracked.py` — the build reads the filesystem, not git, so an
      untracked leftover there would be published unattributed
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] Docs updated if behavior changed
- [ ] Conventional Commit message

## Style guide

| Area | Rule |
|---|---|
| Python | `ruff` + `ruff-format`, `line-length = 110`, target `py311` (pre-commit enforces) |
| Shell | `shellcheck`-clean; no `set +e` without justification |
| Markdown | GFM / Typora-friendly; pipe tables only, **no box-drawing ASCII**; GitHub callouts (`> [!NOTE]`) |
| Identifiers | English (`def install_profile`, not `def instala_perfil`) |
| Prose | English default; PT-BR allowed for project-specific context |
| Refs | every external claim has a verifiable URL — `scripts/validate-refs.sh` must pass |
| `CLAUDE.md` | ≤60 lines when possible, ~140-150 max — split into `.claude/rules/<scope>*.md` if it grows |

## Adding a profile

Full guide: [`docs/05-profiles.md`](docs/05-profiles.md) §7. In short:

1. Create `claude_bootstrap/templates/profiles/<name>/profile.yaml` (`name`, `description`, `version` required; `skills`/`rules`/`settings_overrides` optional).
2. Bundle skills under `skills/` with a `NOTICE.md` (per-skill provenance) if redistributing.
3. Register the detection heuristic in `claude_bootstrap/detect.py` (`infer_profile`) and the name in `interview.py` (`PROFILES`).
4. Add a `test_init_with_<name>_profile` mirroring the existing ones in `tests/test_install.py`.

## Adding a skill

Full guide: [`docs/04-skills-curated.md`](docs/04-skills-curated.md) §7.

1. Add the entry to `claude_bootstrap/registry/skills.yaml` (`name`, `description`, `source`, `tier`, `profiles`, `last_validated_at`).
2. `local` source → add `SKILL.md` under the profile; `github` source → ensure URL + path resolve.
3. Validate: `uv run claude-bootstrap skill validate` + `bash scripts/validate-refs.sh`.
4. If bundling from upstream, pin + content-verify via `scripts/verify-skill-provenance.py` and record provenance in the profile `NOTICE.md`.

## Release process

Maintainer-only: see [`RELEASE.md`](RELEASE.md).

## Code of Conduct & security

By participating you agree to the [Contributor Covenant](.github/CODE_OF_CONDUCT.md). For confidential security reports, see [`SECURITY.md`](.github/SECURITY.md).

## Questions

[GitHub Discussions](https://github.com/ulissesflores/claude-bootstrap/discussions) for questions, ideas, or showing what you built.
