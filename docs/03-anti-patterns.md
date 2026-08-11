# Claude Code anti-patterns

> The canonical list of practices to avoid. External sources last validated 2026-05-05; item 10 was corrected against this repo's own code on 2026-07-29. Primary source: [02-state-of-the-art.md §3](02-state-of-the-art.md#3-anti-patterns-rejected-or-ineffective).
>
> 🇧🇷 [Versão em português](pt-br/03-anti-patterns.md)

---

## 1. A `CLAUDE.md` over 500 lines

**Why it fails**: Claude loads the whole file into context, but past ~300 lines attention to the content degrades sharply — critical rules get lost in the noise of trivial ones. At 500+ lines you are guaranteeing that most of your instructions are ignored in practice.

**Symptom**: Claude violates rules that are written down explicitly; you find yourself repeating in the prompt what `CLAUDE.md` already says; the file grows every session because "maybe this time it will stick".

**How to avoid it**: Keep `CLAUDE.md` lean (~60 lines, ~140-150 max) and limited to what Claude would get wrong without being told. Move domain-specific rules to `.claude/rules/<scope>*.md` (path-scoped, the Q2/2026 standard — see [01-canonical-anthropic.md §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory)). Delete any line describing behaviour Claude would have produced anyway.

**Sources**: [official best-practices docs](https://code.claude.com/docs/en/best-practices), [Babich, UXPlanet 2026](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c)

---

## 2. The kitchen-sink session (context pollution)

**Why it fails**: Claude holds the state of the entire conversation. Mixing three or more unrelated tasks contaminates it: variables from one task leak into another, the working plan blurs across objectives, and error output from task A interferes with reasoning about task B.

**Symptom**: Claude starts crossing wires — citing files from the previous task while working on the current one; suggestions turn generic; a long session produces steadily less coherent output.

**How to avoid it**: One session, one coherent task. Use `/clear` between unrelated tasks. For genuinely parallel work use subagents with isolated context (see [01-canonical-anthropic.md §4](01-canonical-anthropic.md#4-subagents--specialized-ai-assistants)) or `claude --continue` with distinct named sessions.

**Source**: [official best-practices docs](https://code.claude.com/docs/en/best-practices)

---

## 3. The infinite fix-fail-propose loop

**Why it fails**: When Claude cannot resolve a bug in two or three attempts, it shifts into hypothesis-exploration mode, which frequently introduces new problems while chasing the original. The bug list grows and net progress is zero or negative.

**Symptom**: You are 20+ turns into the same error; each "fix" spawns two new problems; Claude starts proposing architectural changes for a typing bug.

**How to avoid it**: Set an explicit stopping rule before you start iterating — "three attempts maximum; if it still fails, roll back and reopen as `/plan`". Use `/clear` plus a minimal reproducible context. If it survives three exchanges, write a test that reproduces the bug before attempting another fix. See [07-glossary.md §Plan mode](07-glossary.md#plan-mode).

**Source**: [GitHub issue #51856](https://github.com/anthropics/claude-code/issues/51856)

---

## 4. Negation in `CLAUDE.md` ("Do NOT")

**Why it fails**: Language models process negation unstably — "Do NOT use semicolons" activates the concept *semicolons* in reasoning before negating it. In long contexts or complex tasks the negation is dropped and the forbidden behaviour occurs. The more negations in the file, the higher the risk of internal conflict.

**Symptom**: "Do NOT X" rules are violated far more often than affirmative ones; you find the forbidden behaviour precisely where the most prominent negative instruction was.

**How to avoid it**: Rewrite every negative instruction as an affirmative statement of the desired behaviour. Instead of "Do NOT use semicolons" → "Use ASI (Automatic Semicolon Insertion) — omit trailing semicolons". Instead of "Do NOT commit to main" → "Always commit to feature branches". See [07-glossary.md §CLAUDE.md](07-glossary.md#claudemd).

**Source**: [Knightli 2026](https://www.knightli.com/en/2026/04/19/karpathy-claude-md-ai-coding-rules/)

---

## 5. Over-engineering (unnecessary complexity)

**Why it fails**: Claude is biased toward "well-structured" patterns — factory methods, abstract classes, dependency injection — because those dominate the large codebases in its training data. For a simple problem the model reaches for the most *correct* pattern it knows rather than the simplest one that works.

**Symptom**: A ten-line function becomes a class hierarchy; a hardcoded config becomes a plugin system; a throwaway script gets enterprise-grade error handling. Technical debt grows without matching capability.

**How to avoid it**: Say it explicitly in the project's `CLAUDE.md`: "Write the minimum code that solves the problem. No abstractions for single-use code. No configurability unless asked." For a specific task, anchor it in the prompt: "solve this with a function, not a class hierarchy". See [02-state-of-the-art.md §7](02-state-of-the-art.md#7-summary-converged-versus-still-in-flux) on the SOLID-versus-agentic-patterns tension.

**Source**: [DEV Community 2026](https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh)

---

## 6. Treating skills as a silver bullet (probabilistic invocation)

**Why it fails**: Claude invokes a skill when the `description` and `when_to_use` in its frontmatter semantically match the task — but that match is probabilistic, not deterministic. Claude does not read skills pre-emptively; it invokes one only if the trigger makes sense in the immediate context. Documented reliability: under 70% for natural-language patterns.

**Symptom**: You built a skill to enforce a critical rule and Claude keeps breaking the rule because it never invoked the skill. You notice the behaviour changes with how you phrase the prompt.

**How to avoid it**: For **deterministic** enforcement, use hooks (`PreToolUse`, `PostToolUse`) — see [01-canonical-anthropic.md §5](01-canonical-anthropic.md#5-hooks--lifecycle-event-handlers). Skills fit optional high-value procedures the user invokes explicitly via `/skill-name`. Do not rely on auto-invocation for security, style or compliance rules. See [07-glossary.md §Skill](07-glossary.md#skill).

**Sources**: [MindStudio memory comparison 2026](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared), [Hightower 2026](https://medium.com/@richardhightower/save-hours-stop-repeating-yourself-to-claude-skills-rules-memory-and-when-to-use-each-93ce3cf83aa8)

---

## 7. An unintegrated memory system (layer conflict)

**Why it fails**: When `CLAUDE.md`, `PROJECT-STATE.md`, auto-memory and `CONTEXT.md` all exist without a clear hierarchy, Claude faces contradictory instructions across layers. There is no native tie-break protocol — the model falls back on recency and position in the context window, which is unpredictable.

**Symptom**: Claude follows instructions from earlier sessions that should have expired; it "remembers" decisions you reversed; contradictions between files produce inconsistent behaviour within one session.

**How to avoid it**: Adopt the four-layer model with exclusive responsibilities: `CLAUDE.md` (stable instructions you write), auto-memory (lessons Claude writes), `PROJECT-STATE.md` (the current in-progress task state, overwritten every session — renamed from `MEMORY.md` precisely so it cannot collide with auto-memory), and `CONTEXT.md` (session-to-session handoff). Every layer gets an owner and a defined TTL. See [01-canonical-anthropic.md §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory) and [07-glossary.md §Auto-memory](07-glossary.md#auto-memory).

**Source**: [Amit Ray 2026](https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/)

---

## 8. Hooks without exit codes (false safety)

**Why it fails**: Hooks are the only deterministic enforcement layer in Claude Code. A hook script that ends without an explicit exit code returns `0` by default — even when it detected a violation. Claude reads `exit 0` as "approved" and proceeds. The hook looks functional (it ran, it did not error) while blocking nothing.

**Symptom**: Your validation hook runs on every `PreToolUse` and you still see the behaviour it should block; logs show the hook executing with no visible effect.

**How to avoid it**: Every enforcement hook must emit `exit 2` (block and show stderr) on a violation and `exit 0` on approval. Scripts that fail internally (an uncaught exception) need `set -e` plus a trap. Test the hook in isolation against violating input before putting it in production. See [01-canonical-anthropic.md §5](01-canonical-anthropic.md#5-hooks--lifecycle-event-handlers) and [07-glossary.md §Hook](07-glossary.md#hook).

**Source**: [hooks guide](https://code.claude.com/docs/en/hooks-guide)

---

## 9. Hard-coded paths in skills (zero portability)

**Why it fails**: A skill carrying absolute paths (`/absolute/path/of/the/author/my-project/`) or paths relative to the author's home stops working outside its original environment. Across a team, in CI/CD, or after porting the project to another workstation, every such skill breaks silently — the path is absent, the script fails, and Claude gets an error with no context.

**Symptom**: The skill works on the author's machine and fails with `FileNotFoundError` or `command not found` in CI or on a colleague's machine. Skills that call external executables or templates stop working after a `git clone` into a different path.

**How to avoid it**: A portable skill never references an absolute path. Use paths relative to `SKILL.md` (`./template.md`), environment variables (`$PROJECT_ROOT`, `$HOME`), or `$(git rev-parse --show-toplevel)` for the repo root. Worked example from this repo: two of its five first-party skills originally pointed at machinery private to their author — a personal `hotspots` binary and a personal transcript script — and both were rewritten into portable `git log` and inline equivalents before being bundled, because a skill that names machinery the reader does not have is broken for every reader but one. See [07-glossary.md §Skill](07-glossary.md#skill) and [01-canonical-anthropic.md §2](01-canonical-anthropic.md#2-skills--agent-skills-open-standard).

**Sources**: [Anthropic skills docs](https://code.claude.com/docs/en/skills), [obra/superpowers portability conventions](https://github.com/obra/superpowers)

---

## 10. Duplicating base configuration across profiles (drift)

> [!IMPORTANT]
> **This item said something false until 2026-07-29 and the correction is the interesting part.** It used to be titled "Profile without `based_on` (composition impossible)" and prescribed declaring `based_on: universal-software`, asserting that "the bootstrap engine processes inheritance: base first, then the specific profile's overlay". Measured against this repo's own code: `based_on` appears **only** in the five `profile.yaml` files that declare it and is read by **no code and no test**. It is inert declarative metadata. The doc was prescribing a mechanism the engine does not implement — see [05-profiles.md](05-profiles.md), which carries the same divergence.

**Why it fails**: If every specialised profile restates the common configuration, a change to a universal rule requires editing N files, and the copies drift apart as some get updated and others do not. This is the main source of long-term inconsistency between profiles.

**Symptom**: `data-science`, `frontend` and `devops` all replicate the same base configuration; one universal change means N edits; new profiles contributed by others start from a blank file instead of a shared floor.

**How to avoid it — as actually implemented here**: composition is real, but it comes from `_base/`, not from `based_on`. `install.py` resolves `<templates_dir>/_base` (`install.py:525`) and applies it for **every** profile; the profile then layers on top, and `profile.get("skills")` is read directly from that profile's own file with no parent merge. So the working rule is: anything universal belongs in `_base/`, and a profile declares only its delta. Adding a profile stays zero-touch for existing ones because nothing merges across siblings.

**What to do about `based_on`**: treat it as documentation of intent, not behaviour, until either the merge is implemented or the field is dropped. Do not write a profile that depends on it resolving. See [07-glossary.md §Profile](07-glossary.md#profile) and [07-glossary.md §Profile-based, not monolithic](07-glossary.md#profile-based-not-monolithic).

**Source**: measured in this repo, 2026-07-29 (`git grep based_on -- claude_bootstrap/ tests/ scripts/` returns only the five declarations)

---

## Summary: remediation table

| Anti-pattern | Key symptom | Immediate remediation | Suggested skill/rule |
|---|---|---|---|
| `CLAUDE.md` over 500 lines | Written rules being violated | Cut to ≤150 lines (≤60 ideally); move the rest to `.claude/rules/` | path-scoped rules, Q2/2026 |
| Kitchen-sink session | Generic output, crossed subjects | `/clear` between tasks | subagents for parallelism |
| Infinite fix-fail loop | Turn 20+ on the same bug | Roll back, `/plan`, reproducible test | `systematic-debugging` skill |
| Negation in `CLAUDE.md` | "Do NOT X" violated often | Rewrite as affirmative | review the whole `CLAUDE.md` |
| Over-engineering | Class hierarchies for simple problems | Anchor the prompt: "minimum code" | a `simplicity.md` rule |
| Skills as a silver bullet | Skill exists, behaviour unchanged | Move enforcement to hooks | `PreToolUse` hooks |
| Unintegrated memory | Contradictions across sessions | Adopt the four-layer model with TTLs | `PROJECT-STATE.md` template |
| Hooks without exit codes | Hook runs but blocks nothing | Add `exit 2` on error paths | hook template with `set -e` |
| Hard-coded paths in skills | Skills break off the author's machine | Relative paths or env vars | portability convention |
| Duplicated base config | Duplication and drift across profiles | Put universal content in `_base/`, profiles carry only their delta | the profile schema |
