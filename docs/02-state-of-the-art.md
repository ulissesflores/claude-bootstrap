# State of the art: Claude Code practices (Jan/2025 – Jun/2026)

> Canonical project documentation. External sources last validated **2026-06-02** (the Jun/2026 SOTA refresh — see §7.2); the GitHub star counts in §4 and §7.1 were re-measured **2026-08-02** via the GitHub API (`obra/superpowers` re-measured **2026-08-10**). 36 unique sources, listed in §8: Anthropic docs, Reddit, HN, X, Medium, GitHub, TechCrunch.
>
> 🇧🇷 [Versão em português](pt-br/02-state-of-the-art.md)

---

## 1. Consensus practices (>70% of sources)

| Practice | Consensus | Sources |
|---------|----------|--------|
| **CLAUDE.md as the foundation** | A single markdown file of ~100-300 lines, loaded every session, holding stable instructions (code, workflow, gotchas) | [Official docs](https://code.claude.com/docs/en/best-practices), [Bruniaux 2026](https://github.com/FlorianBruniaux/claude-code-ultimate-guide), [Marmelab 2026](https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html) |
| **The `.claude/` hierarchy** | `~/.claude/CLAUDE.md` (global) + `./CLAUDE.md` (project) + `./CLAUDE.local.md` (gitignored); subdirectories: agents/, skills/, hooks/, commands/, plugins/ | [Claude Directory docs 2026](https://code.claude.com/docs/en/claude-directory), [codewithmukesh 2026](https://codewithmukesh.com/blog/anatomy-of-the-claude-folder/) |
| **Concision is critical** | Remove any line Claude would not have violated anyway; past ~300 lines Claude starts ignoring rules; ~100 lines is the Karpathy/Cherny style | [Official docs](https://code.claude.com/docs/en/best-practices), [mindwiredai 2026](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/) |
| **Plan mode by default** | Use `/plan` for anything 3+ steps; separate exploration → planning → implementation | [Official best practices](https://code.claude.com/docs/en/best-practices), [shanraisshan 2026](https://github.com/shanraisshan/claude-code-best-practice) |
| **Self-sufficient verification** | Claude checks its own work with tests, screenshots and linters; described as the highest-leverage pattern | [Official docs](https://code.claude.com/docs/en/best-practices), [Marmelab 2026](https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html) |
| **Four-layer memory** | CLAUDE.md (stable) + auto-memory (current) + a state layer (`MEMORY.md` by community convention; `claude-bootstrap` emits `PROJECT-STATE.md` to avoid the collision — see §7.2, Auto-memory) + CONTEXT.md (handoff) | [Knight 2026](https://www.knightli.com/en/2026/04/23/claude-code-claude-md-rules-memory-hooks-guide/) |
| **Hooks for enforcement** | `.claude/settings.json` with PreToolUse/PostToolUse/Stop; deterministic (exit 0/2), not advisory | [Hooks guide](https://code.claude.com/docs/en/hooks-guide), [MindStudio 2026](https://www.mindstudio.ai/blog/self-evolving-claude-code-memory-obsidian-hooks) |
| **Subagents for isolation** | `/agents` for complex delegation; fresh context, tool restrictions declared in YAML frontmatter | [Subagents docs](https://code.claude.com/docs/en/sub-agents), [Anthropic whitepaper 2026](https://resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns_%20Subagents,%20MCP,%20and%20Scaling%20to%20Real%20Codebases.pdf) |
| **MCP as the external bridge** | Model Context Protocol as the USB-C of AI; official and open; connects databases, APIs, Notion, Figma, CLI tools | [MCP docs](https://code.claude.com/docs/en/mcp), [Anthropic engineering 2026](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) |
| **Integrated git workflow** | Commit early, check with git status, use `/pr` for pull requests | [Best practices docs](https://code.claude.com/docs/en/best-practices) |

---

## 2. Emerging practices (30-50% adoption)

| Practice | Status | Note | Source |
|---------|--------|-----------|-------|
| **Skills as modularity** | Maturing; the debate is that Claude does not always invoke them (invocation is probabilistic) | SKILL.md under `.claude/skills/`; useful once CLAUDE.md stops scaling; the reliability gap is the weak point | [MindStudio 2026](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared), [Hightower 2026](https://medium.com/@richardhightower/save-hours-stop-repeating-yourself-to-claude-skills-rules-memory-and-when-to-use-each-93ce3cf83aa8) |
| **Auto-memory persistence** | Experimental; the `/memory` command; not yet universal | Some projects wire Obsidian + hooks for automatic capture; no official standard | [MindStudio hooks 2026](https://www.mindstudio.ai/blog/self-evolving-claude-code-memory-obsidian-hooks), [johnoct 2026](https://johnoct.com/blog/2026/02/14/claude-mem-persistent-memory-for-claude-code/) |
| **Plugins as composable extensions** | Being adopted; ~5k+ in the Anthropic registry as of May/2026 | Bundle skills + hooks + MCP; one-click install through `/plugin` | [Official Anthropic plugins](https://github.com/anthropics/claude-plugins-official), [Plugins docs](https://code.claude.com/docs/en/plugins) |
| **Agentic engineering patterns** | Documentation under way; Simon Willison leading | Patterns kept alive rather than frozen at release time | [simonwillison.net agentic patterns](https://simonw.substack.com/p/agentic-engineering-patterns) |
| **Session renaming + resumption** | Low-friction branching; `/rename` + `claude --continue` | A branch-like workflow across multiple threads | [Sessions docs](https://code.claude.com/docs/en/sessions) |
| **Sandbox mode** | Shipped in the Jun/2026 window; still maturing | OS-level isolation, `claude --sandbox` | [Permission modes docs](https://code.claude.com/docs/en/permission-modes) |
| **The superpowers framework** | ~270k stars (measured 2026-08-10); cross-tool (Cursor, Codex, Gemini) | An agentic skills framework and methodology; became the de facto standard | [Medium, Anil Mathew, Apr/2026](https://medium.com/@anilmathewm/i-gave-claude-code-a-brain-its-called-superpowers), [GitHub obra/superpowers](https://github.com/obra/superpowers) |

---

## 3. Anti-patterns (rejected or ineffective)

| Anti-pattern | Why it fails | Source |
|--------------|---------------|-------|
| **CLAUDE.md over 500 lines** | Important rules get lost in the noise and Claude ignores them | [Best practices docs](https://code.claude.com/docs/en/best-practices), [Babich, UXPlanet 2026](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c) |
| **The "kitchen sink session"** | Mixing 3+ unrelated tasks pollutes the context | [Best practices docs](https://code.claude.com/docs/en/best-practices); the fix is `/clear` between tasks |
| **The endless fix-fail-propose cycle** | Claude proposes new bugs for the same issue, so the bug list grows and progress is zero | [GitHub issue #51856](https://github.com/anthropics/claude-code/issues/51856) |
| **Negation in CLAUDE.md** | "Do NOT use semicolons" activates the concept; the model struggles with negation | [Knightli 2026](https://www.knightli.com/en/2026/04/19/karpathy-claude-md-ai-coding-rules/); use the positive form, "Use ASI instead" |
| **Over-engineering patterns** | The model turns simple problems into complex ones — factory patterns and unnecessary abstract classes become tech debt | [Dev.to 2026](https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh) |
| **Skills as a silver bullet** | A skill may not be invoked (invocation is probabilistic); reported under 70% reliability for a natural-language pattern | [MindStudio memory comparison 2026](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared) |
| **An unintegrated memory system** | Mixing CLAUDE.md + MEMORY.md + auto-memory with no clear hierarchy produces conflicts | [Amit Ray 2026](https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/) |
| **Hooks without exit codes** | A script with no validation yields false positives and weakens security | [Hooks guide](https://code.claude.com/docs/en/hooks-guide) |

---

## 4. Emerging frameworks and templates

| Name | Repo | Stars | Focus | Status |
|------|------|-------|------|--------|
| **Superpowers** | [obra/superpowers](https://github.com/obra/superpowers) | ~270k | Agentic skills framework + methodology; cross-tool | Active, growing fast |
| **Awesome Claude Code Toolkit** | [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 2,433 | 135 agents, 35 skills, 176+ plugins, 20 hooks, 7 templates | Active, curated |
| **Claude Code Best Practice** | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | 63,896 | Vibe coding → agentic engineering patterns | Active |
| **Claude Code Ultimate Guide** | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | 5,639 | Production-ready templates, quizzes, cheatsheet | Active |
| **VILA-Lab / Dive into Claude Code** | [VILA-Lab/Dive-into-Claude-Code](https://github.com/VILA-Lab/Dive-into-Claude-Code) | 2,015 | Systematic analysis of Claude Code's design | Active |
| **dotclaude** | [poshan0126/dotclaude](https://github.com/poshan0126/dotclaude) | 839 | A standard `.claude/` folder structure | Active |

Star counts measured 2026-08-02 through the GitHub API, except `obra/superpowers` (~270k), re-measured 2026-08-10 and kept in sync with [`07-glossary.md`](07-glossary.md) and [`00-overview.md`](00-overview.md). A star count is a dated fact, not a property of the project — re-measure before quoting it anywhere else.

---

## 5. Canonical resources (relevance tiers)

### Tier 1: Official Anthropic documentation
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — updated May/2026
- [Claude Code Memory Guide](https://code.claude.com/docs/en/memory) — the official four-layer model
- [Subagents Guide](https://code.claude.com/docs/en/sub-agents) — official patterns
- [MCP Documentation](https://code.claude.com/docs/en/mcp) — the Model Context Protocol spec
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide) — lifecycle event automation
- [Plugins Marketplace](https://github.com/anthropics/claude-plugins-official) — the official registry

### Tier 2: High-authority community sources
- [Simon Willison / Agentic Engineering Patterns](https://simonw.substack.com/p/agentic-engineering-patterns) — living documentation
- [Anthropic Advanced Patterns Whitepaper](https://resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns_%20Subagents,%20MCP,%20and%20Scaling%20to%20Real%20Codebases.pdf) — the official technical deep dive
- [Superpowers Framework](https://github.com/obra/superpowers) — the de facto cross-tool standard
- [Claude Code Ultimate Guide (Bruniaux)](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) — comprehensive

### Tier 3: Specialised posts and analyses
- [Marmelab: Claude Code Tips I Wish I'd Had](https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html) — Apr/2026
- [MindStudio Memory Systems Comparison](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared)
- [DEV Community: 5 Patterns That Make Claude Code Follow Rules](https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh)
- [Amit Ray: Claude.md vs Agents.md vs Memory.md Hierarchy](https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/)

### Tier 4: Statistical data
- [Pragmatic Engineer Survey, Feb 2026](https://claude5.ai/news/developer-survey-2026-ai-coding-73-percent-daily) — 15k developers, 73% daily usage, Claude Code at 46% "most loved" (figures as published Feb/2026; not re-verified here)
- [Claude Code Statistics 2026](https://www.gradually.ai/en/claude-code-statistics/) — market data, ARR of $2.5B (as published; not re-verified here)

---

## 6. Unresolved tensions and open debates

1. **Skill reliability**: skills are probabilistic, and the community argues over whether a well-written CLAUDE.md is enough versus the overhead of skills. No standard has emerged; it stays case-by-case.

2. **Memory hierarchy trade-offs**: the field converges on four layers but there is no consensus on the optimal order or precedence.

3. **Hooks versus permission allowlists**: enforcement through hooks (deterministic) versus auto mode plus allowlists (better UX, weaker security). Neither has won.

4. **Subagent overhead**: subagents isolate context (good) but add latency and complexity. The "when to use one" metrics are still empirical.

5. **MCP server discovery**: 5k+ servers in the registry as of May/2026, and the community wants official curation or recommendations. The current state is high noise.

6. **Non-interactive automation at scale**: Claude Code parallelises well (multi-session, fan-out) but cost is a barrier — the May/2026 sources put heavy users at roughly $15-20/day.

7. **Agentic patterns diverging from traditional software engineering**: SOLID and DRY sometimes conflict with agentic needs (explicit over implicit). The community is still exploring a new ruleset.

8. **Plugins versus skills versus subagents taxonomy**: the distinctions are fuzzy and the community keeps asking for clarity on "when to use which".

---

## 7. Summary: converged versus still in flux

**Converged (>85% consensus as of May/2026):**
- CLAUDE.md at ~100-300 lines is the gold standard
- The `.claude/` hierarchy with agents/, skills/, hooks/ is canonical
- Plan mode for anything 3+ steps
- Four memory layers
- Hooks for deterministic enforcement
- Subagents for isolation
- MCP as the official external bridge

**Still emerging (30-50%):**
- Skill trigger reliability
- Auto-memory persistence
- Plugin market saturation
- An agentic patterns framework

**The wider picture:**
The community moved from "vibe coding" (Jan/2025) to a **structured agentic methodology** (May/2026). Superpowers (~270k stars, measured 2026-08-10) became the lingua franca. Anthropic made skills official (Oct/2025), then plugins (Mar/2026), then MCP. The tension between simplicity (plain CLAUDE.md) and modularity (skills and plugins) has no definitive resolution.

---

## 7.1. The community-curated skills ecosystem (May/2026)

Beyond `anthropics/skills` (the canonical upstream), the community produced MIT-redistributable collections that serve as the base for specialised profiles:

| Collection | Stars | Skills (count) | Domain | Licence | Citation |
|---|---|---|---|---|---|
| `forrestchang/andrej-karpathy-skills` | 198,785 | 1 (`karpathy-guidelines`) | LLM coding behaviour meta | MIT | https://github.com/forrestchang/andrej-karpathy-skills |
| `K-Dense-AI/scientific-agent-skills` | 32,404 | 137 (under `scientific-skills/`) | Scientific research, chemistry, biology, citation, IMRAD | MIT | https://github.com/K-Dense-AI/scientific-agent-skills |
| `alirezarezvani/claude-skills` | 23,658 | 625 total; 41 engineering/, 32 engineering-team/, 16 ra-qm-team/ | DevOps, frontend, data science, ML, security, compliance | MIT | https://github.com/alirezarezvani/claude-skills |

**Curated indices** (not consumed directly as skills; cited as ecosystem reference):

| Index | Stars | Focus | Citation |
|---|---|---|---|
| `Shubhamsaboo/awesome-llm-apps` | 129,840 | 100+ ready-to-run AI agent / RAG apps | https://github.com/Shubhamsaboo/awesome-llm-apps |
| `punkpeye/awesome-mcp-servers` | 91,737 | A collection of MCP servers | https://github.com/punkpeye/awesome-mcp-servers |
| `hesreallyhim/awesome-claude-code` | 51,537 | Curated index: skills, hooks, slash commands, plugins | https://github.com/hesreallyhim/awesome-claude-code |

**Notable MCP servers** (Q2/2026):

- `ChromeDevTools/chrome-devtools-mcp` (48,388 stars) — Chrome DevTools for coding agents

Star counts in this section were measured 2026-08-02 through the GitHub API. The skill counts come from the May/2026 survey and were not re-counted.

`claude-bootstrap` v1.0.0 incorporates selected skills from these sources into the `frontend`, `data-science`, `devops`, `backend` and `academic` profiles — always preserving the original licence and attribution in the copied SKILL.md frontmatter (MIT compliance).

---

## 7.2. June/2026 updates (SOTA refresh)

Validated primarily against `code.claude.com/docs/en` (Jun/2026). What was new since May/2026 and relevant to positioning a bootstrap tool:

| Feature | What it is | Impact on scaffolders |
|---|---|---|
| **Interactive `/init`** (`CLAUDE_CODE_NEW_INIT=1`) | Multi-phase: interview + subagent exploration + a reviewable CLAUDE.md/skills/hooks proposal; idempotent | A **direct competitor** to bootstrap tools; still opt-in (env-gated), not the default |
| **Agent teams + background agents** | A lead coordinates subagents; parallel sessions are monitored (`/agent-view`) | Native orchestration; reduces the need for external wrappers |
| **Forked subagents** | `context: fork` (skills) + forking the current conversation | — |
| **Bundled skills `/run`, `/verify`, `/run-skill-generator`** | Run and verify the app; record the recipe under `.claude/skills/run-<name>/` (v2.1.145+) | The "watch it run" UX is now native |
| **Auto permission mode** | A background classifier evaluates commands and writes | An alternative to static allowlists |
| **MCP Tool Search** | On by default; tools are deferred and loaded on demand (`ENABLE_TOOL_SEARCH`) | Scales MCP without inflating the context |
| **Routines + `/loop`** | An Anthropic-managed cron (`/schedule`) + in-session polling | — |
| **Channels** | Telegram, Discord and webhooks push events into a session | — |
| **Auto-memory** (v2.1.59+) | Claude writes `~/.claude/projects/<project>/memory/MEMORY.md` | A name collision with the `MEMORY.md` scaffolders emit — `claude-bootstrap` resolves it by emitting `PROJECT-STATE.md` (a distinct name) |

Model lineup as recorded at the 2026-06-29 check: Opus 4.8 (`claude-opus-4-8`), Sonnet 4.6 (`claude-sonnet-4-6`) and Haiku 4.5 (`claude-haiku-4-5-20251001`), with Fable 5 and Mythos 5 (`claude-fable-5` / `claude-mythos-5`) reaching general availability on 2026-06-09. Treat that as a snapshot rather than as the current lineup: it moves faster than this document is revalidated, and `claude-bootstrap` deliberately pins no model. The `--model` flag aliases are in `01-canonical-anthropic.md` §4; the authoritative live list is the Anthropic model documentation, or `GET /v1/models`.

> **Implication for `claude-bootstrap`**: the differentiator is not "generate a CLAUDE.md" (the native `/init` already does that), it is opinionated profiles + audited MIT bundles + a permissions baseline + distribution through a plugin marketplace.

---

## 8. Sources

36 unique validated URLs.

1. https://code.claude.com/docs/en/best-practices
2. https://github.com/FlorianBruniaux/claude-code-ultimate-guide
3. https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html
4. https://code.claude.com/docs/en/claude-directory
5. https://codewithmukesh.com/blog/anatomy-of-the-claude-folder/
6. https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/
7. https://github.com/shanraisshan/claude-code-best-practice
8. https://www.knightli.com/en/2026/04/23/claude-code-claude-md-rules-memory-hooks-guide/
9. https://code.claude.com/docs/en/hooks-guide
10. https://www.mindstudio.ai/blog/self-evolving-claude-code-memory-obsidian-hooks
11. https://code.claude.com/docs/en/sub-agents
12. https://resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns_%20Subagents,%20MCP,%20and%20Scaling%20to%20Real%20Codebases.pdf
13. https://code.claude.com/docs/en/mcp
14. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
15. https://www.mindstudio.ai/blog/claude-code-memory-systems-compared
16. https://medium.com/@richardhightower/save-hours-stop-repeating-yourself-to-claude-skills-rules-memory-and-when-to-use-each-93ce3cf83aa8
17. https://simonw.substack.com/p/agentic-engineering-patterns
18. https://medium.com/@anilmathewm/i-gave-claude-code-a-brain-its-called-superpowers
19. https://github.com/obra/superpowers
20. https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh
21. https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/
22. https://github.com/anthropics/claude-plugins-official
23. https://claude5.ai/news/developer-survey-2026-ai-coding-73-percent-daily
24. https://github.com/VILA-Lab/Dive-into-Claude-Code
25. https://github.com/anthropics/skills
26. https://github.com/K-Dense-AI/scientific-agent-skills
27. https://github.com/alirezarezvani/claude-skills
28. https://github.com/forrestchang/andrej-karpathy-skills
29. https://github.com/hesreallyhim/awesome-claude-code
30. https://github.com/Shubhamsaboo/awesome-llm-apps
31. https://github.com/punkpeye/awesome-mcp-servers
32. https://github.com/ChromeDevTools/chrome-devtools-mcp
33. https://github.com/langchain-ai/langchain
34. https://github.com/crewAIInc/crewAI
35. https://github.com/ollama/ollama
36. https://github.com/qdrant/qdrant
