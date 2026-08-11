# Glossary — `claude-bootstrap`

> Canonical Claude Code domain terms plus this project's own vocabulary. When in doubt about naming, look here before inventing a new one. For the full Anthropic standard, see [`01-canonical-anthropic.md`](01-canonical-anthropic.md).
>
> 🇧🇷 [Versão em português](pt-br/07-glossary.md)

---

## Canonical Anthropic terms

### CLAUDE.md
Markdown file of persistent instructions loaded in every Claude Code session. Scope hierarchy: managed (org) > project (`./CLAUDE.md`) > user (`~/.claude/CLAUDE.md`) > local (`./CLAUDE.local.md`, gitignored). This project's policy: **≤60 lines where possible, ~140-150 max**; past that, split into [`.claude/rules/<scope>*.md`](https://code.claude.com/docs/en/memory) (path-scoped, the Q2/2026 standard). See [`01-canonical-anthropic.md` §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory).

### Skill
A modular capability Claude can invoke. Defined in `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (user). YAML frontmatter plus a markdown body. Can be model-invoked (Claude decides) or user-invocable (`/skill-name`). See [`01-canonical-anthropic.md` §2](01-canonical-anthropic.md#2-skills--agent-skills-open-standard).

### Agent (subagent)
A specialised AI assistant with fresh context and a restricted toolset. Defined in `.claude/agents/<name>.md`. Built-ins: `Explore` (read-only, for search), `Plan` (read-only, for planning), `general-purpose` (all tools). Each subagent keeps its own auto-memory per worktree. See [`01-canonical-anthropic.md` §4](01-canonical-anthropic.md#4-subagents--specialized-ai-assistants).

### Hook
A lifecycle event handler (session, turn, tool, permission). Configured in `settings.json`. Five handler types: `command` (shell), `http` (JSON POST), `mcp_tool`, `prompt` (LLM-based), `agent` (spawns a verifier subagent). Deterministic — exit 0 = pass, exit 2 = block. See [`01-canonical-anthropic.md` §5](01-canonical-anthropic.md#5-hooks--lifecycle-event-handlers).

### MCP (Model Context Protocol)
An open protocol for connecting Claude to external systems (databases, APIs, CLI tools, Notion, Figma). Transports: HTTP, SSE, stdio. Configured in `.mcp.json` (project) or `~/.claude.json` (user). 5k+ servers in the registry as of May 2026. Often described as "USB-C for AI". See [`01-canonical-anthropic.md` §6](01-canonical-anthropic.md#6-mcp--model-context-protocol).

### Plugin
A reusable extension that bundles skills, commands, agents, hooks and MCP servers. Manifest at `.claude-plugin/plugin.json`. Discovery through a marketplace plus `/plugin install`. A plugin's skills are namespaced `plugin-name:skill-name`. See [`01-canonical-anthropic.md` §7](01-canonical-anthropic.md#7-plugins--reusable-extensions-v2025).

### Settings hierarchy
Priority order for `settings.json` (high → low): managed (IT-deployed) > CLI flags > local (`.claude/settings.local.json`, gitignored) > project (`.claude/settings.json`) > user (`~/.claude/settings.json`). More specific wins. See [`01-canonical-anthropic.md` §8](01-canonical-anthropic.md#8-settings-hierarchy--configuration-scopes).

### Plan mode
A Claude Code operating mode (`/plan`) in which only read-only tools are permitted. Used to explore a codebase and present a plan before implementing. The gold standard for anything 3+ steps. See [`02-state-of-the-art.md` §1](02-state-of-the-art.md#1-consensus-practices-70-of-sources).

### Auto-memory
Memory Claude writes on its own (lessons from corrections) under `~/.claude/projects/<path>/memory/`. The first 200 lines or 25KB are loaded per session. Distinct from `CLAUDE.md`, which you write. See [`01-canonical-anthropic.md` §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory).

---

## Terms specific to this project

### Profile
An opinionated set of templates, skills, rules and settings for one kind of project. Defined in `templates/profiles/<name>/profile.yaml`. Populated profiles (v1.0.0): `frontend` (7 skills), `data-science` (6), `universal-software` (default, 5), `devops` (5), `backend` (4), `academic` (3) — 30 bundled skills in total. Adding a new profile is zero-touch for the others (the profile-based principle).

### Registry
`claude_bootstrap/registry/skills.yaml` — a curated catalogue of 13 skills, installable one at a time via `claude-bootstrap skill add`. Each entry carries `name`, `source` (a git URL or `local`), `path`, `tier` (1-3), applicable `profiles`, `description`, `evidence_url` and `last_validated_at`. Distinct from the **profile bundles** (skills shipped inside `templates/profiles/<p>/skills/`, commit-pinned in `scripts/skill-pins.json`) — see [04-skills-curated.md](04-skills-curated.md).

### Tier (of a skill)
A skill's confidence/maturity level in the registry — an advisory label, not an installation policy. **No tier installs anything**: every registry skill, in every tier, reaches a project only through an explicit `claude-bootstrap skill add <name>`. In code, `tier` is a required field plus the `skill list --tier` filter.
- **Tier 1 (core)**: broadly useful, manually audited, well-defined trigger, no destructive side effects, evidence of real use
- **Tier 2 (recommended)**: consolidated, but scoped to specific workflows whose learning overhead does not pay off everywhere
- **Tier 3 (experimental)**: marked `unstable: true` — the API may change between `claude-bootstrap` versions

Full criteria, and the separate criteria governing the profile bundles, in [04-skills-curated.md](04-skills-curated.md) §2.

### Idempotent
An operating principle: re-running `bootstrap.sh init` on an already-configured project **breaks nothing and duplicates nothing**. The check: run `init` twice in a row → `git diff` is empty.

### Detective before prescriptive
An operating principle: `detect.py` scans the project (heuristics in [`00-overview.md` §4](00-overview.md#4-the-claude-bootstrap-init-flow)) before `interview.py` asks anything. This cuts friction — the system knows what it can see and only asks about what it cannot.

### Profile-based, not monolithic
An architectural principle: the bootstrap logic stays generic and specialisation lives in `templates/profiles/<name>/`. Adding a new profile is zero-touch for existing ones.

---

## Ecosystem terms

### Superpowers
A skills + commands + methodology framework created by @obra (https://github.com/obra/superpowers). ~270k stars (measured 2026-08-10). A cross-tool lingua franca (Cursor, Codex, Gemini, Claude Code). `claude-bootstrap` declares a dependency on `superpowers` and does **not** bundle a copy; if it is absent from `~/.claude/superpowers/`, the tool offers to `git clone` it.

### Agentic-stack
A convention set some Claude Code users implement under `~/.agent/`: episodic and semantic memory, a dream cycle, a review queue, host-agent CLI tools in Python, documented in that directory's own `AGENTS.md`. In `claude-bootstrap` it is a **detected interop flag** (`agentic_stack_interop`) and not a profile: `detect` finds `~/.agent/` (or `.agent/`) and the emitted `CLAUDE.md` points at the stack instead of duplicating it.

---

## Operational terms

### Conventional Commits
A commit-message convention: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`, `build:`, `ci:`, `perf:`, `style:`. Adopted in this repo from the first commit. Reference: https://www.conventionalcommits.org/

### Path-scoped rules
The Anthropic Q2/2026 standard: `.claude/rules/<path>*.md` applies only while Claude is editing files under that path. It replaces a monolithic `CLAUDE.md` once that file passes ~150 lines. Example: `.claude/rules/frontend*.md` loads only when working inside `packages/frontend/`.

### PII scan
The gate in [`scripts/pii-scan.py`](../scripts/pii-scan.py) that sweeps tracked files (`git ls-files`) for personal or machine-identifying context. It runs pre-commit and in CI, and fails the build on any hit. Two layers: the **structural** patterns ship in the script (absolute home paths, which identify a developer machine for any user), while patterns naming a specific person, organisation or private host are read from a gitignored `.pii-patterns.local` — one `regex<TAB>reason` per line — so the list itself is never published. The success line names which layers ran, because a clean result from fewer patterns is not the same result. **Authorship** metadata (name, ORCID, e-mail in `CITATION.cff` / `pyproject.toml`) is deliberate attribution and is out of scope.
