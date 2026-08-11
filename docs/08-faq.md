# FAQ — `claude-bootstrap`

> Last updated: 2026-07-29. For deeper questions see [`00-overview.md`](00-overview.md) (the big picture) or [`06-bootstrap-flow.md`](06-bootstrap-flow.md) (the detailed flow).
>
> 🇧🇷 [Versão em português](pt-br/08-faq.md)

---

## Positioning

### Q: Why not just use `superpowers`?

`superpowers` solves the primitives — modular skills, commands, methodology — but it does not do adaptive bootstrapping, does not curate skills by tier, and does not generate a `CLAUDE.md` configured for your project's type. `claude-bootstrap` is the orchestration layer above it, not a replacement. See [`00-overview.md` §3](00-overview.md#3-architecture--3-layers).

### Q: How does `claude-bootstrap` differ from other frameworks (`claude-code-ultimate-guide`, `awesome-claude-code-toolkit`, `dotclaude`)?

Those projects are curated collections or manual checklists. `claude-bootstrap` has an **idempotent engine** (`bin/bootstrap.sh`) that detects the project, runs an interview and installs configuration through Jinja templates. It is executable, not just reference material. See [`02-state-of-the-art.md`](02-state-of-the-art.md) for the comparison against 36 sources.

### Q: Why Python rather than pure shell or TypeScript?

Pure shell is limiting for YAML parsing (`registry/skills.yaml`) and for an interactive interview. TypeScript would require a Node runtime — less universal in academic and devops environments. Python 3.11+ is everywhere and the stack (`questionary`, `jinja2`, `pyyaml`, `rich`) is mature.

---

## Practical use

### Q: How do I run `bootstrap.sh init` on an existing project?

`claude-bootstrap init` (or `bin/bootstrap.sh init`) detects an existing `.claude/` and reports `mode: update`. The semantics are **create-only**: existing files are never overwritten. With `claude-bootstrap update`, a diverged file is written as `<path>.new` for review rather than overwritten. By default `init` shows the plan and asks `[y/N]` before writing anything. Details in [`00-overview.md` §4](00-overview.md#4-the-claude-bootstrap-init-flow).

### Q: Will it overwrite my `CLAUDE.md`?

No. The semantics are **create-only**: if `CLAUDE.md` already exists, `init` skips it (status `exists-skipped`) and only creates it when absent. `update` writes a `CLAUDE.md.new` alongside for you to diff. `--force` does overwrite — use it deliberately. And the `[y/N]` confirm-before-write precedes any write at all. See principle 1 in [`CLAUDE.md`](../CLAUDE.md).

### Q: How do I create a custom profile?

Create `templates/profiles/<name>/` with a `profile.yaml` (required: `name`, `description`, `version`; optional: `skills`, `rules`, `settings_overrides`). `_base/` is always applied and the profile layers on top. Register the heuristic in `claude_bootstrap/detect.py` and the name in `interview.py`. Zero-touch for the other profiles (principle 3). Step by step in [`05-profiles.md` §7](05-profiles.md).

### Q: How do I add a skill to the registry?

Edit `claude_bootstrap/registry/skills.yaml` with `name`, `source` (`local` or `github`), `path`, `tier` (1-3) and `profiles`. Validate with `claude-bootstrap skill validate` and test with `claude-bootstrap skill add <name> --target /tmp/x`. See [`04-skills-curated.md` §7](04-skills-curated.md). (This is distinct from the profile bundles — covered there.)

### Q: How do I dry-run without writing?

Pass `--check` to `claude-bootstrap init` (or `update`). It prints the action plan (`would-create` / `would-overwrite` / …) without touching disk and without recording a manifest. It is also what confirm-before-write uses to show you the plan ahead of the `[y/N]`.

---

## Profiles

### Q: Which profile should an academic project use?

`academic`, detected by `*.tex`, `*.csl` or `*.bib` with no code project present: **3 curated skills, all from `K-Dense-AI/scientific-agent-skills` (MIT)**. Four `anthropics/skills` skills were bundled here until 2026-07-26 and were de-bundled — their `LICENSE.txt` is a restriction list with no grant clause, and one had no licence at all; `NOTICE.md` keeps the record of why. `universal-software` is the default for everything else. Heuristics in [`05-profiles.md` §3](05-profiles.md).

### Q: Is the `data-science` profile ready?

Yes. `data-science` (6 skills), `frontend` (7), `devops` (5) and `backend` (4) are **populated** with curated, content-verified skills — see each profile's `NOTICE.md`. All 6 profiles are ready; see [`05-profiles.md` §6](05-profiles.md).

### Q: Can I have more than one profile active?

Yes, in **monorepos**. A single-stack repo gets one profile; a monorepo with several stacks (say `frontend/` React + `backend/` FastAPI + `infra/` terraform) gets the **union** of the detected stacks — `--profile` is repeatable, and `detect` finds sub-projects on its own. `academic` is exclusive: it claims a whole repo and never joins a union. Details in [`05-profiles.md` §10](05-profiles.md).

---

## Skills and superpowers

### Q: Do the bundled skills duplicate what `superpowers` already has?

No, and there is no copied content. The `superpowers` skills are a **declared dependency**, never vendored. What ships inside profiles is a different set: `universal-software` bundles **5 first-party skills written for this project** (MIT, `LICENSE.txt` in each), and the domain profiles (`academic`, `data-science`, `frontend`, `devops`, `backend`) bundle curated skills from MIT-licensed upstreams, with per-skill provenance in each `NOTICE.md` and commit pins in `scripts/skill-pins.json`. See principle 5 in [`CLAUDE.md`](../CLAUDE.md).

### Q: What happens if `superpowers` is not installed?

`detect` / `interview` checks for it at `~/.claude/skills/superpowers` (or `~/.claude/superpowers`) and records the `superpowers_available` flag, which the emitted `CLAUDE.md` references. It does **not** install `superpowers` for you — install it yourself, since it is a declared dependency rather than a bundled copy. See [`00-overview.md` §3](00-overview.md#3-architecture--3-layers).

### Q: Are the skills versioned?

Yes, two different ways. Registry skills: `claude-bootstrap skill update` re-extracts the installed ones from their current sources. **Profile-bundle** skills: pinned to upstream commits in `scripts/skill-pins.json`, with `scripts/verify-skill-provenance.py` comparing content against the pin (`--sync` updates it) and the `skill-drift.yml` workflow checking weekly. First-party skills have no upstream to pin, so they verify as `FIRST-PARTY` — weaker evidence than a byte comparison, and deliberately labelled as such.

---

## Memory and instructions

### Q: Why keep `CLAUDE.md` short (≤60 lines)?

Large files in the session context cost tokens and add read latency. This project's policy: **≤60 lines where possible, ~140-150 max**; anything path-specific goes to `.claude/rules/<scope>*.md` and anything sub-directory-specific to `<subdir>/CLAUDE.md`, both of which load on demand. Source: `docs/01-canonical-anthropic.md`. The rule itself is stated in [`CLAUDE.md`](../CLAUDE.md).

### Q: When should I use `.claude/rules/<scope>*.md` instead of `CLAUDE.md`?

Use `rules/` when a rule applies to a subset of paths (for example `rules/python-*.md` activating only on `.py` files), or when `CLAUDE.md` is already near ~150 lines. Path-scoped rules load by context, so fewer tokens go to waste. This is the Anthropic Q2/2026 standard, described in [`01-canonical-anthropic.md`](01-canonical-anthropic.md).

### Q: How does auto-memory work?

`claude-bootstrap` implements no memory of its own. If you use the `agentic-stack` conventions (`~/.agent/`), `detect` finds the directory, records the `agentic_stack_interop` flag, and the generated `CLAUDE.md` points at the stack. For projects without it, memory lives in `CLAUDE.md`, in `PROJECT-STATE.md` and in `.claude/rules/`. See the heuristics in [`05-profiles.md` §3](05-profiles.md).

---

## Contributing

### Q: How do I report a bug?

Use GitHub Issues — the templates are in `.github/ISSUE_TEMPLATE/` (bug report, feature request), and security reports go through the private channel described in `.github/SECURITY.md`, never a public issue.

### Q: How do I add a new profile?

1. Create `templates/profiles/<name>/` with a `profile.yaml` (plus `skills/`, `rules/` and a `NOTICE.md` if you bundle skills).
2. Add the heuristic to `claude_bootstrap/detect.py` (`infer_profile`) and the name to `interview.py` (`PROFILES`).
3. Document it in [`docs/05-profiles.md`](05-profiles.md) and add a `test_init_with_<name>_profile` test.
4. Zero-touch for the other profiles — do not edit `_base/` without discussion.

### Q: Can I publish this in my own fork?

Yes, it is MIT. One request: keep the credit to `superpowers` (obra/superpowers) as a dependency. Positioning this as a layer above rather than a competitor is deliberate, and it avoids confusing the community. See [`LICENSE`](../LICENSE) and [`README.md`](../README.md#license).
