# Canonical Anthropic Claude Code standard

> The Claude Code spec this project targets. Translated and internally reconciled on
> **2026-08-03**; each section carries the date of its own verification against upstream
> (§5 hooks: 2026-06-08). Source: https://code.claude.com/docs/en — the live page always wins.
>
> 🇧🇷 [Versão em português](pt-br/01-canonical-anthropic.md)

---

## 1. Memory system — CLAUDE.md + Auto-Memory

**Source**: https://code.claude.com/docs/en/memory

- **Two complementary layers**:
  - `CLAUDE.md` (you write it — persistent instructions)
  - Auto-memory (Claude writes it — lessons from corrections)

- **Scope hierarchy** (more specific wins):
  1. `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS managed policy, org-wide)
  2. `./CLAUDE.md` or `./.claude/CLAUDE.md` (project, checked into git)
  3. `~/.claude/CLAUDE.md` (user, all projects)
  4. `./CLAUDE.local.md` (personal, project-only, gitignored)

- **Loading behaviour**: walks up the directory tree from the CWD, then descends into subdirectories on demand
- **Size**: keep it concise (context costs tokens) — this project's policy: **≤60 lines where possible, ~140-150 max**; past that use `@path/to/file` imports or `.claude/rules/*.md` path-scoped rules
- **Auto-memory location**: `~/.claude/projects/.../memory/` (the first 200 lines or 25KB load per session)
- **Imports**: `@relative/path` syntax, at most 4 hops of recursion, resolved relative to the importing file

---

## 2. Skills — Agent Skills Open Standard

**Source**: https://code.claude.com/docs/en/skills

- **Definition**: `.claude/skills/<name>/SKILL.md` or `~/.claude/skills/<name>/SKILL.md`
- **Scope hierarchy**:
  - Enterprise (managed settings)
  - Personal (`~/.claude/skills/`)
  - Project (`.claude/skills/`)
  - Plugin (`<plugin>/skills/`)

- **Skills bundled with the client**: Claude Code ships a set of its own (`/simplify`, `/loop` and `/claude-api` among them) that **changes from release to release**; `disableBundledSkills` turns the whole set off. Enumerating it here would only produce a rotting list — the current set comes from `/help` or the live docs

- **Frontmatter (YAML)**:
  ```yaml
  name: skill-name                    # lowercase, max 64 chars
  description: What it does           # critical for auto-invocation
  when_to_use: Trigger phrases        # appended to description
  argument-hint: [arg1] [arg2]        # autocomplete
  arguments: arg1 arg2                # named positional args
  disable-model-invocation: false     # true = manual-only (/name)
  user-invocable: true                # false = hidden from the / menu
  allowed-tools: Read Grep            # space-separated, no permission prompts
  model: sonnet|opus|haiku|inherit    # alias, full model ID, or inherit (default)
  effort: low|medium|high|xhigh|max
  context: fork                       # run in an isolated context
  ```

- **File layout** (`my-skill/`):
  - `SKILL.md` — required: frontmatter + instructions
  - `template.md` — optional, a template for Claude to fill in
  - `examples/sample.md` — optional, examples
  - `scripts/validate.sh` — optional, an executable Claude may run

- **Live reload**: changes under `.claude/skills/` are picked up in the same session (except a brand-new top-level directory)
- **Nested discovery**: in a monorepo, `packages/frontend/.claude/skills/` is auto-discovered when you edit inside that tree
- **Plugin skills**: namespaced as `plugin-name:skill-name` (no collisions)
- **Governance (settings.json)**: `disableBundledSkills` (turns off the bundled `/simplify` and friends), `disableSkillShellExecution` (forbids executables under `scripts/`), `maxSkillDescriptionChars` / `skillListingBudgetFraction` (the listing budget; `description` + `when_to_use` ≤1,536 chars), `skillOverrides` (override one skill by name).

---

## 3. Slash commands vs Skills

**Source**: https://code.claude.com/docs/en/slash-commands

- **Skills (preferred)**: `.claude/skills/<name>/SKILL.md` — model-invoked, contentful
- **Commands (legacy)**: `.claude/commands/<name>.md` — **subsumed by skills**: `.claude/commands/deploy.md` is equivalent to `.claude/skills/deploy/SKILL.md`, and both resolve `/deploy` (when both exist, the skill wins). `claude-bootstrap` emits **SKILL.md**, never `commands/*.md`.
- **The distinction**: skills are "smart" (Claude decides when to use them); commands are fixed logic or triggers

---

## 4. Subagents — specialized AI assistants

**Source**: https://code.claude.com/docs/en/sub-agents

- **Built-in subagents**:
  - **Explore**: read-only tools, for searching and analysing codebases
  - **Plan**: the session's model, read-only (gather context before writing a plan)
  - **General-purpose**: all tools (multi-step research plus action)
  - **statusline-setup, claude-code-guide**: narrow helpers

- **Definition**: markdown + YAML frontmatter in `.claude/agents/<name>.md`

- **Scope hierarchy**:
  1. Managed settings (organisation)
  2. `--agents` CLI flag (session-only JSON)
  3. `.claude/agents/` (project)
  4. `~/.claude/agents/` (user, all projects)
  5. Plugin `agents/` directory

- **Frontmatter**:
  ```yaml
  description: When to use this agent
  prompt: System prompt / instructions
  tools: [Read, Grep, Bash]  # or disallowedTools
  model: sonnet|opus|haiku   # alias, a full model ID, or inherit (default)
  permissionMode: auto|ask|deny
  mcpServers: [list]
  hooks: {...}
  maxTurns: 10
  skills: [skill1, skill2]
  initialPrompt: Auto-sent on spawn
  memory: true               # persistent auto-memory per worktree
  effort: low|medium|high
  background: false|true
  isolation: none|worktree   # filesystem isolation
  color: blue                # UI display color
  ```

> **The `model` field** (skill and subagent frontmatter) takes an **alias**, a **full model ID**, or **`inherit`** (the default — the same model as the session). **`inherit` is frontmatter-specific; it is NOT an alias of the `--model` flag.**
>
> The top-level **`--model`** flag/config takes the aliases `default`, `best`, `fable`, `sonnet`, `opus`, `haiku`, `sonnet[1m]`, `opus[1m]`, `opusplan`, or a full model ID (source: https://code.claude.com/docs/en/model-config). The alias **names** are stable; **which concrete model each one resolves to is not** — `best` resolves to the best model the organisation has access to, and each family resolves to its current member. A freshly launched alias usually requires a client above some minimum version.
>
> **This page deliberately records no model lineup.** It moves faster than this page is revalidated, and `claude-bootstrap` pins no model at all. The live, authoritative list is Anthropic's model documentation, or `GET /v1/models`.

- **Invocation**: Claude auto-delegates when a task matches the description; manually via `/agents` or `--agents` JSON
- **Persistence**: each subagent keeps its own auto-memory per worktree

---

## 5. Hooks — lifecycle event handlers

**Source**: https://code.claude.com/docs/en/hooks

- **Events** (complete lifecycle — **30**, verified against `/docs/en/hooks` on 2026-06-08):
  - **Session**: `SessionStart`, `SessionEnd`, `Setup`
  - **Turn**: `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`
  - **Tool**: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`
  - **Permission**: `PermissionRequest`, `PermissionDenied`
  - **Subagent/Task**: `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`
  - **Display/Notify**: `Notification`, `MessageDisplay`, `Elicitation`, `ElicitationResult`
  - **Env/FS/Worktree**: `ConfigChange`, `CwdChanged`, `FileChanged`, `InstructionsLoaded`, `WorktreeCreate`, `WorktreeRemove`
  - **Compact**: `PreCompact`, `PostCompact`

- **Handler types** (5): `command` (shell), `http` (JSON POST), `mcp_tool` (calls a tool on an MCP server), `prompt` (model evaluation), `agent` (spawns a verifier subagent)

- **Exit codes** (the `command` handler):

  | Code | Effect |
  |---|---|
  | `0` | Success; stdout is parsed as JSON. On `UserPromptSubmit` / `UserPromptExpansion` / `SessionStart`, stdout becomes context Claude sees |
  | `2` | **Blocking**: stderr goes to Claude; what it blocks depends on the event (`PreToolUse` blocks the tool, `UserPromptSubmit` rejects the prompt, `Stop` prevents stopping, …) |
  | anything else (`1`, `3+`) | Non-blocking — execution continues. **Exception**: `WorktreeCreate` aborts on any non-zero code |

- **Configuration** in `settings.json`:
  ```json
  {
    "hooks": {
      "PreToolUse": [{
        "matcher": "Bash",
        "if": "Bash(rm *)",
        "type": "command",
        "command": "./.claude/hooks/block-rm.sh"
      }]
    }
  }
  ```

- **Matcher syntax**:
  - `"*"` = all tools
  - `"Tool1|Tool2"` = exact tool names
  - A JS regex against the tool_name field

- **Where they live**:
  - `~/.claude/settings.json` (user, all projects)
  - `.claude/settings.json` (project, shared)
  - `.claude/settings.local.json` (project, personal)
  - Managed settings (org)
  - Plugin `hooks/hooks.json`
  - Skill / agent frontmatter

---

## 6. MCP — Model Context Protocol

**Source**: https://code.claude.com/docs/en/mcp

- **Transports**:
  - HTTP (recommended for cloud): `claude mcp add --transport http <name> <url>`
  - SSE (streaming): `claude mcp add --transport sse <name> <url>`
  - Stdio (local processes): `claude mcp add --transport stdio <name> -- <command> [args]`

- **Scopes**:
  - **Local** (default): a per-project entry in `~/.claude.json`, private
  - **Project**: `.mcp.json` at the root, shared through git
  - **User**: `~/.claude.json`, global

- **Configuration** (`.mcp.json`):
  ```json
  {
    "mcpServers": {
      "server-name": {
        "command": "/path/to/server",
        "args": ["--flag"],
        "env": {"VAR": "value"}
      }
    }
  }
  ```

- **Plugin MCP servers**: bundled in a plugin's `.mcp.json` or `plugin.json`, auto-started when the plugin is enabled
- **Dynamic updates**: MCP `list_changed` notifications refresh the tool list without reconnecting
- **Auto-reconnect**: HTTP/SSE retries up to 5 times with exponential backoff (1s → 2s → 4s → 8s → 16s)
- **Managed config**: admin-controlled in `managed-mcp.json` with `allowedMcpServers` / `deniedMcpServers`

---

## 7. Plugins — reusable extensions (v2025+)

**Source**: https://code.claude.com/docs/en/plugins

- **Definition**: a directory carrying a `.claude-plugin/plugin.json` manifest

- **Manifest** (`.claude-plugin/plugin.json`):
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
    "name": "my-plugin",
    "displayName": "My Plugin",
    "description": "What it does",
    "version": "1.0.0",
    "author": {"name": "Your Name"},
    "homepage": "url",
    "repository": "url",
    "license": "MIT",
    "keywords": ["claude-code", "domain"],
    "defaultEnabled": false,
    "userConfig": {}
  }
  ```
  - Only `name` is required. `displayName` (≥2.1.143, may contain spaces) · `defaultEnabled` (≥2.1.154, defaults to `true`; `false` installs it disabled, opt in through `/plugin` or `claude plugin enable`) · `keywords[]` (discovery) · `userConfig` (entries marked `sensitive` go to the keychain) · `$schema` (ignored at load, editor support only).

- **Components** (all optional, under the plugin root):
  - `.claude-plugin/plugin.json` — the manifest
  - `skills/<name>/SKILL.md` — skills
  - `commands/*.md` — slash commands (legacy)
  - `agents/` — subagent definitions
  - `hooks/hooks.json` — event handlers
  - `.mcp.json` — MCP server configs
  - `.lsp.json` — language server configs
  - `monitors/monitors.json` — background log watchers (v2.1.105+)
  - `themes/` — `experimental.themes` (colour tokens)
  - `output-styles/` — `outputStyles` (response style presets)
  - `bin/` — executables added to the Bash PATH
  - `settings.json` — default settings (`agent`, `subagentStatusLine`)
  - `README.md` and any supporting files
  - **Skills-dir plugin**: a folder holding `.claude-plugin/plugin.json` under a skills directory loads as `<name>@skills-dir` (no marketplace involved). Top-level `themes` / `monitors` still work, but `claude plugin validate` warns — migrate them to `experimental.*`.

- **Versioning**: an explicit `version` field, or auto-derived from the git commit SHA
- **Local testing**: `claude --plugin-dir ./my-plugin` (overrides the marketplace)
- **Reload**: `/reload-plugins` picks up skill / agent / hook / MCP / LSP changes without a restart
- **Namespacing**: plugin skills appear as `/plugin-name:skill-name` (no collisions)
- **Marketplace**: built-in discovery and install (community-driven)

---

## 8. Settings hierarchy — configuration scopes

**Source**: https://code.claude.com/docs/en/settings

- **Priority** (high → low):
  1. **Managed** (IT-deployed, unoverridable): OS registry, plist, `/etc/claude-code/managed-settings.json`, `managed-settings.d/*.json`
  2. **CLI flags** (session-only)
  3. **Local** (`.claude/settings.local.json`, gitignored)
  4. **Project** (`.claude/settings.json`, team-shared)
  5. **User** (`~/.claude/settings.json`, all projects)

- **Key settings**:
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "permissions": {
      "allow": ["Bash(npm test)", "Read(~/.zshrc)"],
      "deny": ["Bash(curl *)", "Read(./.env)"]
    },
    "env": {"CLAUDE_CODE_ENABLE_TELEMETRY": "1"},
    "companyAnnouncements": ["Welcome message"],
    "hooks": {...},
    "allowManagedHooksOnly": false,
    "allowManagedMcpServersOnly": false,
    "allowManagedPermissionRulesOnly": false
  }
  ```

- **What gets loaded**:
  - `CLAUDE.md` / `CLAUDE.local.md`
  - Subagents (`.claude/agents/`, `~/.claude/agents/`)
  - MCP servers (`.mcp.json`, `~/.claude.json`)
  - Plugins (those enabled in settings)
  - Skills (`.claude/skills/`, `~/.claude/skills/`)

- **`claudeMdExcludes`** — glob patterns or absolute paths of `CLAUDE.md` files to **skip** when loading memory (for example `"claudeMdExcludes": ["**/vendor/**/CLAUDE.md"]`). Matched against the absolute path; applies to user/project/local only — managed policy **cannot** be excluded. In a monorepo it stops vendored subprojects' `CLAUDE.md` from loading.

- **AGENTS.md interop** — `claude-bootstrap` emits `@AGENTS.md` in the root `CLAUDE.md` **when the repo already has an `AGENTS.md`** (detected at emit time; `@path` imports resolve up to 4 hops, relative to the importing file). The import-free alternative, when `AGENTS.md` must be the single source: symlink it with `ln -s AGENTS.md CLAUDE.md`.

- **Permission modes** (`--permission-mode`, or the Shift+Tab cycle; full table at `/docs/en/permission-modes`): `default`, `acceptEdits`, `plan`, `auto` (v2.1.83+, a background safety classifier), `dontAsk` (auto-denies anything not pre-approved; the CI-locked mode), `bypassPermissions`. `disableAutoMode: "disable"` removes `auto` from the cycle. Managed-only: `allowManagedHooksOnly` / `allowManagedMcpServersOnly` / `allowManagedPermissionRulesOnly`.

- **Newer settings keys (jun/2026, as of the 2026-06-29 check)**: `fallbackModel` (v2.1.166 — a **list** of up to 3 models to degrade to when the preferred one is unavailable), `enforceAvailableModels` / `requiredMinimumVersion` / `requiredMaximumVersion` (managed), `disableBundledSkills`, `respondToBashCommands`, `teammateMode`, `footerLinksRegexes`, `autoMode.classifyAllShell`. `claude-bootstrap` does **not** emit these by default; they are documented for reference.

### 8.1 Sandbox (`settings.json` → `sandbox`, **off by default**)

**Source**: https://code.claude.com/docs/en/sandboxing

```json
{
  "sandbox": {
    "enabled": true,
    "excludedCommands": ["docker *"],
    "filesystem": { "denyRead": ["~/.aws", "~/.ssh"], "allowWrite": ["/tmp/build"] },
    "network": { "allowedDomains": ["registry.npmjs.org"], "httpProxyPort": 8080 }
  }
}
```

- ⚠️ **The default still permits reading `~/.aws/credentials` and `~/.ssh/`** — add them to `denyRead` to block it (the default policy is "read the whole machine except the denied directories").
- `filesystem`: `denyRead` / `denyWrite` / `allowWrite` / `allowRead` / `allowManagedReadPathsOnly`. `network`: `allowedDomains` / `deniedDomains` / `httpProxyPort` / `socksProxyPort` / `allowManagedDomainsOnly` / `enableWeakerNetworkIsolation` / `allowUnixSockets`. Others: `failIfUnavailable`, `allowUnsandboxedCommands` (`false` = strict), `excludedCommands`.
- **Newer (jun/2026)**: `sandbox.credentials` (v2.1.187, 2026-06-23 — blocks file reads and unsets env vars for sandboxed commands: `{path,mode:"deny"}` / `{name,mode:"deny"}`); `sandbox.allowAppleEvents` (v2.1.181, 2026-06-17, macOS). Network host approvals are remembered for the session (v2.1.191).
- Platforms: macOS **Seatbelt**; Linux/WSL2 **bubblewrap** (plus `socat` for networking). **Native Windows is not supported.** Turn it on with `/sandbox` or `sandbox.enabled = true`.

---

## 9. Frontmatter canonical reference

| Type | Location | Frontmatter | Body |
|---|---|---|---|
| **SKILL.md** | `.claude/skills/<name>/` | `name`, `description`, `when_to_use`, `arguments`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context` | Instructions for Claude |
| **Agent.md** | `.claude/agents/<name>.md` | `description`, `prompt` (= body), `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`, `effort`, `background`, `isolation`, `color` | System prompt |
| **CLAUDE.md** | `./CLAUDE.md`, `./.claude/CLAUDE.md`, `~/.claude/CLAUDE.md` | None (plain markdown) | Instructions for EVERY session |
| **settings.json** | `.claude/settings.json`, `~/.claude/settings.json` | JSON keys: `permissions`, `env`, `hooks`, `agent`, `allowedChannelPlugins`, etc. | N/A |
| **plugin.json** | `.claude-plugin/plugin.json` | `name`, `description`, `version`, `author`, `homepage`, `repository`, `license` | N/A |

---

## 10. Directory hierarchy — where everything lives

**Enterprise / organisation** (managed):

- `/Library/Application Support/ClaudeCode/` (macOS)
  - `CLAUDE.md` — org-wide instructions
  - `managed-settings.json` — org policy (unoverridable)
- `/etc/claude-code/` (Linux/WSL)
- `C:\Program Files\ClaudeCode\` (Windows)

**User** (personal, all projects) — `~/.claude/`:

- `CLAUDE.md` — personal instructions
- `settings.json` — personal settings
- `skills/<name>/SKILL.md`
- `agents/<name>.md`
- `keybindings.json`
- `plugins/` — installed plugins
- `projects/<path>/` — per-project state
  - `memory/` — auto-memory
  - `mcpServers.json`

**Project** (team, current repo) — the repo root:

- `CLAUDE.md` — team instructions (checked in)
- `.claude/`
  - `settings.json` — team settings
  - `settings.local.json` — personal overrides (gitignored)
  - `CLAUDE.md` — project instructions, the alternative to the root file
  - `skills/<name>/SKILL.md`
  - `agents/<name>.md`
  - `rules/<path>*.md` — path-scoped rules (Q2/2026)
  - `hooks/*.sh`, `hooks/*.py`
  - `plugins/` — local plugin testing
- `.mcp.json` — the project's MCP servers (checked in)
- `Subdir/.claude/` — nested (monorepo)

**Local** (current session only) — at the root or in a subdirectory:

- `CLAUDE.local.md` — personal notes (gitignored)

---

## 11. Breaking changes & new features (jan/2025 – jun/2026)

**Source**: https://code.claude.com/docs/en/overview + https://code.claude.com/docs/llms.txt

- **Q4 2025 / Q1 2026**: the plugins system launched (`.claude-plugin/` manifest, marketplace discovery, namespaced skills)
- **Early 2026**: skills lifted into the Agent Skills open standard (https://agentskills.io/) — works cross-tool
- **Q2 2026**: auto-memory extended to subagents (each keeps its own memory per worktree)
- **Q2 2026**: nested `.claude/` discovery in monorepos (`packages/*/.claude/skills/` auto-loaded)
- **Q2 2026**: path-scoped rules (`.claude/rules/<path>*.md`) — the replacement for a monolithic CLAUDE.md
- **Q2 2026**: Agent SDK documentation (split from the CLI, for building production agents)
- **Q2 2026 (may–jun)**: agent teams and background agents (`/agent-view`); forked subagents; the bundled skills `/run`, `/verify`, `/run-skill-generator` (v2.1.145+); auto permission mode (background classifier); MCP Tool Search (on by default, `ENABLE_TOOL_SEARCH`); **dynamic workflows** (v2.1.154+; the live docs dropped the "research preview" label but declare no GA either): **JavaScript** scripts that orchestrate subagents at scale — Claude writes them, the user saves one from a run through `/workflows`→`s` into `.claude/workflows/` (project) or `~/.claude/workflows/` (home), and runs it as `/<name>` (`/deep-research` is the bundled one; trigger keyword `ultracode`); they are **not static markdown**, so claude-bootstrap emits no workflows. Distinct from **routines** (`/schedule`, remote agents on Anthropic infrastructure) and `/loop` (repeats a prompt in-session); channels (Telegram/Discord/webhooks); interactive `/init` behind `CLAUDE_CODE_NEW_INIT=1`; auto-memory (v2.1.59+, `~/.claude/projects/<project>/memory/MEMORY.md`)
- **Model lineup**: deliberately not recorded here — see the note in §4 and the live source. The `--model` flag aliases, which *are* stable, are in §4.
- **No breaking changes** to CLAUDE.md, skills, hooks or MCP schemas between jan/2025 and jun/2026

### 11.1 Workflows & routines — the boundary of what `claude-bootstrap` emits

- **Workflows** (`.claude/workflows/`) are **JavaScript orchestration scripts** for subagents that **Claude writes** for a task and the user saves from a run through `/workflows`→`s` (v2.1.154+; the live docs stopped labelling them "research preview" but do **not** declare GA either; available on paid plans plus API/Bedrock/Vertex; `/deep-research` is the bundled one; limits: ≤16 concurrent, 1000 agents per run). They are model-generated, **not** static templates, so **`claude-bootstrap` does not emit them** (hand-writing one would produce an invalid artifact).
- **Routines** (`/schedule`) run on Anthropic infrastructure (server-side), so they are equally **non-emittable** by a static scaffolder.
- `claude-bootstrap` emits only the **static layer** (CLAUDE.md, settings, skills/agents/rules/output-styles); workflows and routines are things the user creates on demand from inside Claude Code.

---

## 12. Documented gaps (in the official docs)

1. **Skill invocation control**: the docs mention `allowed-tools` versus the permission system, but the details are sparse
2. **Hook async patterns**: error handling and timeouts for command/HTTP handlers are under-documented
3. **Plugin marketplace**: discovery is mentioned, but no official URL or listing is documented
4. **Monorepo best practices**: nested `.claude/` discovery is described, but shared-vs-per-package patterns are not
5. **Memory size limits**: "25KB" and "200 lines" are both mentioned, and how they reconcile is unclear
6. **Subagent memory durability**: the edge cases (fork, resume, clear) are under-specified
7. **MCP server diagnostics**: the `/mcp` panel shows a tool count, but there is no guide for "tools disappearing mid-session"
8. **Managed settings distribution**: MDM templates live in a GitHub repo, with no versioning or rollback strategy

---

## 13. Security & trust boundary (jun/2026)

**Sources**: GHSA-4fgq-fpq9-mr3g (CVE-2025-59536), GHSA-jh7p-qr78-84p7 (CVE-2026-21852), adversa.ai, snyk.io.

- **Trust boundary (pre-trust-dialog)**: opening or cloning a repo makes Claude Code load `.claude/settings.json` and initialise (hooks included). CVE-2025-59536 (fixed in v1.0.111) showed execution happening **before** the trust dialog, which makes a hostile third-party `.claude/` an RCE surface. **`claude-bootstrap` emits a benign settings.json** — this is **not a vulnerability of ours**, but it is why the project (a) recommends a current Claude Code version and (b) treats a third-party `.claude/` as untrusted code.
- **Minimum recommended version**: run a **current stable** Claude Code (≥ v2.1.x; the latest stable at the 2026-06-29 check was v2.1.195). The known deny-rule bypass classes (the 50-subcommand cap, fixed in v2.1.90) and the pre-trust-dialog class were fixed well before that; keep it updated (a time-sensitive fact).
- **Deny rules are defence in depth, not a single barrier**: `Read(**/...)` rules are path-based and robust; `Bash(...)` rules depend on the client's parser (hardened in ≥v2.1.90). Combine them with `sandbox` (`denyRead` on `~/.aws` and `~/.ssh`) plus the `auto` mode hardening.
- **Skill supply chain**: 36.8% of ClawHub skills carry at least one security flaw (Snyk, feb/2026 — the first coordinated malicious-skill campaign). **Vet every third-party skill before installing it**; prefer provenance-pinned bundles. The `claude-bootstrap audit` subcommand (provenance plus integrity) and the `vetting-agent-skills` skill exist for exactly this.

---

## 14. Official URLs and entrypoints

- **Main docs**: https://code.claude.com/docs/en/overview
- **Documentation index**: https://code.claude.com/docs/llms.txt
- **Installation**: `curl -fsSL https://claude.ai/install.sh | bash` (macOS/Linux/WSL)
- **CLI install**: `brew install --cask claude-code` or `winget install Anthropic.ClaudeCode`
- **Web Claude Code**: https://claude.ai/code
- **VS Code extension**: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
- **JetBrains plugin**: https://plugins.jetbrains.com/plugin/27310-claude-code-beta-
- **Examples repo** (MDM templates and more): https://github.com/anthropics/claude-code

---

**Takeaway**: the canonical Claude Code standard rests on **hierarchical scope** (managed > user > project > local), **lazy loading** (skills and subagents load only when invoked), and **composability** (plugins aggregate skills + agents + hooks + MCP servers as reusable units). Every piece of configuration is markdown or JSON — no compiled binaries. The system reads up the tree at startup, then descends on demand into subdirectories, which is what makes monorepos and nested team structures work without explicit imports.
