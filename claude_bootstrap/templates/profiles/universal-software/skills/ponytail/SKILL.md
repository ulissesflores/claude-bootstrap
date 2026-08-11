---
name: ponytail
description: Review lens for reuse and minimalism — runs a diff or a set of files down the reuse ladder (YAGNI → this codebase → stdlib → platform native → dependency already installed → one line → minimal own code) and points out where the code reinvented something that already exists, added an abstraction with no second use, or spent two lines where one clear line does. Use before declaring code "done", when reviewing or simplifying, or when asked to "apply ponytail". NOT a bug hunt (use a code-review skill for that), and it NEVER cuts validation, error handling, security, or accessibility.
license: MIT
---

# ponytail — a quality gate for how code is written and structured

The best code is the code that did not need to exist; the second best reuses what already
does. The ladder applies at every scale — line, function, module, architecture.

## Target

- Default: the working-tree diff (`git diff` plus `git diff --staged`). Outside a git repo,
  the files touched in the current conversation.
- With an argument: the paths (or pull request) you name.

## The ladder, as review questions

Ask them in order and stop at the first rung that resolves the code.

1. **Does it need to exist?** Code with no real caller, a speculative feature, configuration
   for an imagined future → delete it (YAGNI).
2. **Does the codebase already do this?** An equivalent helper, function, or pattern already
   exists → reuse it. Grep for the candidates *before* making the accusation — an accusation
   without a grep is a guess.
3. **Does the standard library do this?** A hand-rolled parser, date handling, path
   manipulation, collection utility, or HTTP client → swap it out.
4. **Does the platform do this?** A native feature of the OS, framework, or database covers
   it → use that.
5. **Does an already-installed dependency do this?** Do not add a new library for something a
   present one covers.
6. **Does one line do it?** Gratuitous indirection, a wrapper around a wrapper, a class where
   a function suffices, two lines where one *clear* line resolves it.
7. **Is there own code left?** Then write the minimum that works — and that reads.

## Architecture — the same ladder, one scale up

- A layer, service, or pattern (factory, strategy, event bus, plugin system) with no concrete
  **second** use today → flatten it.
- An abstraction added "for when we need it" violates rung 1. That is not foresight.

## The floor — never counts as excess

Input validation, error handling, security, accessibility, and whatever the user explicitly
asked for. Shortening code by removing these is not ponytail; it is unfinished work.

A cryptic one-liner that has to be decoded LOSES to two readable lines: understand the code
before shortening it, and give any non-obvious simplification a comment explaining why it is
the minimum.

## Output

A table:

| Where | Rung violated | Minimal fix | Priority |
|---|---|---|---|

Give `file:line`, the rung (1–7, or "architecture"), and the fix — ordered deletion >
substitution > addition. Close with the delta: lines removable, dependencies avoided.

No findings → answer "ponytail clean" and stop.

## Rules

- Surgical: only the diff or named target. Do not refactor adjacent code and do not propose a
  general overhaul.
- A `ponytail:` marker in the code means the debt is **accepted and documented**. Do not
  re-flag it.
- A bug or wrong behaviour belongs in code review; this gate is about reuse, minimalism, and
  structure.
- The default output is the **report**. Only apply the fixes if the user explicitly asks.
