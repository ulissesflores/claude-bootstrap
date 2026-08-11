# Curated skills — `claude-bootstrap`

> Catalogue of the 13 audited skills in `claude_bootstrap/registry/skills.yaml`, installable one at a time via `claude-bootstrap skill add`.
>
> 🇧🇷 [Versão em português](pt-br/04-skills-curated.md)

> [!IMPORTANT]
> **Two distinct skill mechanisms, and they do not touch each other.**
> (a) **Registry** (this doc): a catalogue of 13 skills installed one at a time with `claude-bootstrap skill add`, classified into tiers 1/2/3.
> (b) **Profile bundles** ([05-profiles.md](05-profiles.md)): 30 skills shipped inside `templates/profiles/<p>/skills/` and installed as a block by `claude-bootstrap init --profile <p>`, with per-skill provenance in each `NOTICE.md`. 25 are vendored (`anthropics/skills`, `alirezarezvani/claude-skills`, `K-Dense-AI/scientific-agent-skills`), content-verified against upstream by `scripts/verify-skill-provenance.py`; the 5 in `universal-software` are **first-party** — written in this repo, with no upstream to pin, reported as `FIRST-PARTY`.
> **Measured, not asserted:** the two name sets are disjoint. `install.py` never reads the registry, and none of the 13 registry names appears in any profile's `skills:` list. Installing a profile installs zero registry skills, and `skill add` installs zero bundled skills.

---

## 1. Registry schema

Every entry in `claude_bootstrap/registry/skills.yaml` follows the schema below. Fields not marked required are optional.

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Unique kebab-case identifier. Used as the installed directory name. |
| `description` | string | yes | Semantic trigger: when the model should activate the skill. Should be a prescriptive sentence ("Use when…"). |
| `source.type` | enum | yes | `local` or `github` — determines how it is installed. See §3. |
| `source.url` | string | if github | Git repository URL. Cloned with `--depth 1 --no-tags`. |
| `source.path` | string | if github/local | Subpath inside the repo (github) or inside the **installed `claude_bootstrap/` package** (local). See §3. |
| `tier` | int | yes | 1, 2 or 3 — an advisory label plus a `skill list --tier` filter. See §2.1. |
| `profiles` | list[string] | yes | Which profiles the skill is *offered* for. Example: `[universal-software, academic]`. This filters `skill list --profile`; it does **not** install anything. See §2.1. |
| `invocation` | enum | no | `model-decided` (default) or `user-invocable` (requires an explicit user command). Documentation only — read by no code. |
| `evidence_url` | string | no | Link to a repo or doc showing the skill exists and works. Documentation only — read by no code. |
| `last_validated_at` | date | no | ISO date of the last manual audit (`YYYY-MM-DD`). Read by `validate`. |
| `version` | string | no | Skill semver, if the source exposes versioning. |
| `unstable` | bool | no | `true` on tier 3 — signals that the skill's API may change without notice. Documentation only — read by no code. |

`claude-bootstrap skill validate` checks four things: every required field is present, no two entries share a `name`, every `local` source path exists on disk, and every `github` source carries both `url` and `path`. It also warns when `last_validated_at` is older than `STALE_DAYS = 90` (`skill.py:236`). It does **not** check the `tier` range, and it does not resolve remote URLs (network cost) — so a `github` subpath that has disappeared upstream passes validation and fails only at `skill add`. §6 documents a live instance.

---

## 2. Curation criteria

Two mechanisms, two different questions, so two sets of criteria. §2.1 governs the registry (this doc); §2.2 governs the profile bundles ([05-profiles.md](05-profiles.md)).

### 2.1 Registry: what a tier actually is

**A tier is an advisory label, not an installation policy.** It has exactly two effects in the code: it is a required field, and it is the `skill list --tier <n>` filter (`skill.py:55`). Nothing installs a skill because of its tier. Likewise `profiles:` narrows `skill list --profile <p>` and nothing else — every registry skill, in every tier, reaches a project only through an explicit `claude-bootstrap skill add <name>`.

> [!WARNING]
> **Correcting a claim earlier versions of this document made.** Until this revision §2 stated that tier 1 was *"auto-included when the profile is installed"*. That is false and appears to never have been true in this codebase: `install.py` does not read the registry at all, and the intersection between the 13 registry names and the six profiles' `skills:` lists is empty. Profile installation reads `templates/profiles/<p>/profile.yaml` and copies `skills/<name>/` from the profile directory (`install.py:315`). If you arrived here from a cached copy, this is the corrected version.

With that removed, the tiers still carry the entry bar they were written for — as an editorial recommendation about *when a skill is worth adopting*, not as a mechanism:

**Tier 1 — core/essential.** Broadly useful enough that adding it to almost any project is a rounding error. Entry bar: manually audited, well-defined trigger, no destructive side effects, evidence of real use.

**Tier 2 — recommended.** Consolidated but scoped to specific workflows (parallelism, worktrees, meta-skills for writing skills). The learning overhead does not pay off in a simple project.

**Tier 3 — experimental.** Carries `unstable: true`. The skill's API may change between `claude-bootstrap` versions. Use where the potential benefit justifies the breakage risk.

Never promote a tier 3 skill to tier 1/2 without a field audit plus a valid `evidence_url`. The cost of a bad always-suggested skill is high.

### 2.2 Bundles: what "curated" is claiming

This is the axis the README's "curated, license-audited skills" claim is about, and it is worth being precise, because *curated* is a word that invites more credit than the work supports.

**What is claimed:** every bundled skill has passed four exclusion gates, each of which has removed real skills from real releases. The gates are evidence-driven, applied to the skill as it exists at the pinned upstream commit.

1. **Redistribution right, resolved per skill directory.** A skill ships only if a licence grants redistribution — read from the source at the pinned commit (root licence, per-skill override, `SKILL.md` frontmatter), never inferred. Removed 2026-07-26 (29 -> 25): `docx`, `pdf`, `pptx` (`anthropics/skills`), whose `LICENSE.txt` is a restriction list with no grant clause; and `doc-coauthoring`, which has no licence at all — absence of a licence is default copyright, not a permissive default.
2. **Provenance verifiable against a pinned commit.** Bundled content is byte-compared to its upstream by `scripts/verify-skill-provenance.py`. A skill that disappears from upstream can no longer be verified, so it cannot stay. Removed 2026-06-29: `release-manager` (`devops`).
3. **The `SKILL.md` must describe machinery that ships.** A skill that instructs the model to use files or flags the bundle does not contain is broken on arrival. Removed 2026-06-06: `senior-devops`, three identical no-op stub scripts whose `SKILL.md` documents flags the script rejects; and `theme-factory`, which mandates a `theme-showcase.pdf` that was never bundled. This is the same rule the bundled `vetting-agent-skills` applies to third-party skills.
4. **Domain fit with the profile that carries it.** Removed 2026-06-06: `xlsx`, a financial-modelling skill sitting in `data-science`.

A fifth gate governs what may enter at all: nothing institution-specific or person-specific. An entire institution-tied profile was removed on 2026-07-23, and `scripts/pii-scan.py` now runs over every tracked file as a gate.

**What is not claimed:** no systematic quality review of the instruction text of all 30 bundled skills. Gates 1-3 are objective and machine-rechecked; gate 4 is a judgement call made per skill as it was added. "Curated" here means *these exclusions were applied and are re-verified on every run*, not *every sentence in every bundled skill was reviewed and endorsed*.

Two of the gates are re-checked by machine rather than trusted: `scripts/verify-skill-provenance.py` re-runs **gate 2** on every invocation (it byte-compares content against the pinned commit; it does not read licences), and `tests/test_redistribution_rights.py` encodes **gate 1** — no skill without a licence, the grant text ships inside the skill directory, and a de-bundled skill cannot reappear. Gates 3 and 4 are judgements made per skill at the time it was added, and nothing re-checks them.

---

## 3. Supported source types

### `local`

A path resolved against the **installed `claude_bootstrap/` package directory** (`REPO_ROOT` at `skill.py:27`, used at `skill.py:98`), not against the repository root. Used for skills specific to one profile that live inside the package itself.

```yaml
source:
  type: local
  path: templates/profiles/academic/skills/citation-management
```

That value is correct as written: it resolves to `claude_bootstrap/templates/profiles/academic/skills/citation-management`. Do not add a `claude_bootstrap/` prefix to the YAML value — it would resolve to `claude_bootstrap/claude_bootstrap/…` and fail. Shell paths in §7 are a different matter and do carry the prefix.

`claude-bootstrap skill add` copies the directory straight into `<target>/.claude/skills/<name>/`. No network involved. `validate` checks the path exists on disk.

> [!NOTE]
> No entry in the current registry uses `local` — all 13 are `github`. The type is supported and tested (`tests/test_skill.py`), but the `validate` check for it is vacuous against the shipped registry.

### `github`

Clones the git repository with `--depth 1 --no-tags` into a temporary directory (60 s timeout), extracts `path`, copies it to the destination and discards the clone. Requires `git` on `PATH`. The destination is deleted only **after** the clone succeeds (`skill.py:139`), so a network failure leaves an already-installed skill intact.

```yaml
source:
  type: github
  url: https://github.com/obra/superpowers
  path: skills/brainstorming
```

> [!NOTE]
> `claude-bootstrap skill update [--name <name>]` re-extracts (force) the already-installed github skills from the registry's current sources. `skill add <name> --force` does the same for one named skill. See the caveat in §8 before running `update` without `--name`.

---

## 4. Registry tier 1 skills — offered to `universal-software` (8)

> The **registry** axis, not the bundle: these are the **8 tier-1 entries**. Measured 2026-08-03:
> all 13 registry entries list `universal-software` in `profiles:`, so this section is the tier-1
> slice of the catalogue, not a per-profile filter — `skill list --profile universal-software`
> returns all 13. Do not confuse them with the **5 first-party
> skills bundled** into that profile (§(b) above), which arrive with `init` and need no `skill add`.
> Neither set installs the other; "offered" means `skill list --profile universal-software` shows
> them, and nothing more.

All originate from [github.com/obra/superpowers](https://github.com/obra/superpowers). Invocation: `model-decided` — the model decides when to apply them based on the described trigger.

### `brainstorming`

**Trigger**: before creating features or components, or modifying existing behaviour.
**Profiles**: `universal-software`, `academic`
**What it does**: forces the user's intent to be explored before any implementation. Breaks the "implement it wrong -> rewrite" loop.
**Source**: `skills/brainstorming` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `writing-plans`

**Trigger**: on receiving a spec or requirements for a multi-step task, before touching code.
**Profiles**: `universal-software`, `academic`
**What it does**: produces a structured implementation plan that can be executed in a separate session. Separates the design cycle from the execution cycle.
**Source**: `skills/writing-plans` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `executing-plans`

**Trigger**: when you have a written implementation plan to execute, in a session separate from planning.
**Profiles**: `universal-software`, `academic`
**What it does**: defines review checkpoints during execution. Partner to `writing-plans` — together they implement the plan/execute/review loop that cuts rework.
**Source**: `skills/executing-plans` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `test-driven-development`

**Trigger**: when implementing any feature or bugfix, before writing implementation code.
**Profiles**: `universal-software` (not offered for `academic`)
**What it does**: enforces the red/green/refactor cycle. Missing tests before implementation is the most common failure mode in coding agents.
**Source**: `skills/test-driven-development` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `systematic-debugging`

**Trigger**: on hitting any bug, test failure or unexpected behaviour, before proposing fixes.
**Profiles**: `universal-software`, `academic`
**What it does**: imposes hypothesis -> evidence -> fix instead of "edit and pray". Prevents the blind-patch anti-pattern.
**Source**: `skills/systematic-debugging` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `verification-before-completion`

**Trigger**: before declaring work complete, before committing or opening PRs.
**Profiles**: `universal-software`, `academic`
**What it does**: requires running verification commands and confirming the output before any success claim. Eliminates "I think it works" without evidence.
**Source**: `skills/verification-before-completion` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `requesting-code-review`

**Trigger**: on completing tasks, implementing larger features, or before merging.
**Profiles**: `universal-software` (not offered for `academic`)
**What it does**: structures how to request a code review so the reviewer has enough context. Cuts clarification round-trips.
**Source**: `skills/requesting-code-review` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `receiving-code-review`

**Trigger**: on receiving code-review feedback, before implementing the suggestions.
**Profiles**: `universal-software` (not offered for `academic`)
**What it does**: blocks performative blind agreement. Requires technical rigour: verify the suggestion is valid before applying it. See also [01-canonical-anthropic.md](01-canonical-anthropic.md) §2 (Anthropic Skills standard).
**Source**: `skills/receiving-code-review` in [obra/superpowers](https://github.com/obra/superpowers)

---

## 5. Tier 2 skills — recommended (5)

Opt-in. Install with `skill add <name>`. All from [obra/superpowers](https://github.com/obra/superpowers), invocation `model-decided`.

### `dispatching-parallel-agents`

**Trigger**: when facing 2+ independent tasks that can be worked without shared state.
**Profiles**: `universal-software`, `academic`
**What it does**: defines a protocol for dispatching subagents in parallel with correct context handoff and result collection.
**Source**: `skills/dispatching-parallel-agents` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `using-git-worktrees`

**Trigger**: when starting feature work that needs isolation from the current workspace.
**Profiles**: `universal-software`
**What it does**: guides creating git worktrees with a safety check. Avoids the problem of several agents editing the same working tree.
**Source**: `skills/using-git-worktrees` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `subagent-driven-development`

**Trigger**: when executing implementation plans whose tasks are independent, in the current session.
**Profiles**: `universal-software`
**What it does**: complements `executing-plans` for cases where the plan's subtasks are independent enough to run as subagents in the same session (rather than in separate sessions).
**Source**: `skills/subagent-driven-development` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `writing-skills`

**Trigger**: when creating new skills, editing existing ones, or verifying a skill works before deploying it.
**Profiles**: `universal-software`
**What it does**: meta-skill — defines the correct `SKILL.md` format, trigger criteria, and how to test a skill before adding it to the registry.
**Source**: `skills/writing-skills` in [obra/superpowers](https://github.com/obra/superpowers)

---

### `finishing-a-development-branch`

**Trigger**: when the implementation is complete and all tests pass, before deciding the integration strategy.
**Profiles**: `universal-software`
**What it does**: presents structured merge, PR or cleanup options. Blocks the anti-pattern of pushing straight to main without weighing the impact.
**Source**: `skills/finishing-a-development-branch` in [obra/superpowers](https://github.com/obra/superpowers)

---

## 6. Tier 3 skills — experimental (0)

The registry carries no tier 3 entry today. The tier itself stays defined (§2.1) and the next experimental skill lands here; `skill list --tier 3` returns an empty list, not an error.

> [!NOTE]
> **`graphify` was the only tier 3 entry, and it was removed on 2026-08-03 because it did not install.** Measured that day: the recursive git tree of `obra/superpowers` at `HEAD` has 234 paths, is not truncated, and contains no `skills/graphify` — the subpath the entry pointed at. The command returned `subpath-missing: skills/graphify`, exit code 1.
>
> The part worth keeping: **`skill list` printed it as `available` the whole time.** `fmt_status` (`skill.py:59`) reports whether a skill is installed *in the target*, never whether its source resolves — so "available" meant "not installed here", and the one surface a user actually reads asserted the opposite of the truth. Its `unstable: true` flag did not help either: that field is documentation only, read by no code (§1).
>
> Same failure class that de-bundled `release-manager` on 2026-06-29 (§2.2 gate 2), recurring on the registry axis, where nothing re-checks it: `validate` resolves no remote URLs by design, and no test resolves a github subpath. A registry entry is a claim about someone else's repository, and this one had been true when written.

---

## 7. How to add a skill to the registry

Steps for adding a new curated skill. Paths below are **shell paths from the repository root**, which is why they carry the `claude_bootstrap/` prefix — unlike the `source.path` value inside the YAML, which is resolved against the package directory (§3).

**1. Decide the source type**

- A new skill that only makes sense in this context: create the directory at `claude_bootstrap/templates/profiles/<profile>/skills/<name>/` and use `type: local` with `path: templates/profiles/<profile>/skills/<name>` (no `claude_bootstrap/` prefix in the YAML).
- A skill from an existing external repo: use `type: github` with a URL and a subpath.

**2. Create the skill directory (if local)**

The minimum structure of a skill is a `SKILL.md` file with:
- A trigger section (when to use it)
- Behaviour instructions

**3. Edit `claude_bootstrap/registry/skills.yaml`**

Add the entry with every required field: `name`, `description`, `source`, `tier`, `profiles`. Set `last_validated_at` to today (`YYYY-MM-DD`) — `validate` warns once it is more than 90 days old.

```yaml
- name: my-skill
  description: Use when <precise, measurable trigger>
  source:
    type: local
    path: templates/profiles/my-profile/skills/my-skill
  tier: 2
  profiles: [my-profile]
  invocation: model-decided
  last_validated_at: 2026-05-05
```

**4. Validate**

```bash
claude-bootstrap skill validate
```

The failures it actually reports: a missing required field, a duplicate `name`, a `local` path that does not exist, and a `github` source missing `url` or `path`. It does **not** validate the tier range — `tier: 0` and `tier: 9` both pass — and it does not resolve remote URLs, so step 5 is the only thing that proves a `github` entry works.

**5. Test the installation**

```bash
claude-bootstrap skill add my-skill --target /tmp/test-install
ls /tmp/test-install/.claude/skills/my-skill/
```

For a `github` source this is not optional: it is the only check that the subpath exists upstream. See §6 for an entry that passes `validate` and fails here.

**6. Commit**

```bash
git add claude_bootstrap/registry/skills.yaml claude_bootstrap/templates/profiles/<profile>/skills/<name>/
git commit -m "feat(skills): add <name> to registry (tier N)"
```

Do not commit without having run `validate`. CI does not block on it today, but a corrupt registry breaks every downstream `skill add`.

---

## 8. `claude-bootstrap skill` commands

| Command | Description | Example |
|---|---|---|
| `skill list` | Lists registry skills. Filterable by `--profile` and `--tier`. Shows installed/available status against `--target`. | `claude-bootstrap skill list --profile academic --tier 1` |
| `skill list --json` | JSON output with per-skill status. | `claude-bootstrap skill list --json \| jq '.[].name'` |
| `skill add <name>` | Installs the skill into `<target>/.claude/skills/<name>/`. Default target: `.`. Already installed without `--force` is `exists-skipped`, exit 0. | `claude-bootstrap skill add brainstorming --target ~/my-project` |
| `skill add <name> --force` | Re-installs even if already present. | `claude-bootstrap skill add writing-skills --force` |
| `skill remove <name>` | Removes `<target>/.claude/skills/<name>/` (only the named skill; to reverse an entire emit use `claude-bootstrap uninstall`). | `claude-bootstrap skill remove using-git-worktrees` |
| `skill show <name>` | Prints the full registry entry for one skill, as JSON. | `claude-bootstrap skill show brainstorming` |
| `skill validate` | Checks required fields, duplicate names, local paths and github `url`+`path`. Remote URLs are not resolved. | `claude-bootstrap skill validate` |
| `skill update [--name <name>]` | Re-installs (force) already-installed skills from the registry's current sources; without `--name`, every installed skill. | `claude-bootstrap skill update --name brainstorming` |

**Global flags**:

- `--registry <path>`: use an alternative registry (default: `claude_bootstrap/registry/skills.yaml`, injected by the CLI at `cli.py:266`)
- `--target <path>`: installation directory (default: `.`)

> [!WARNING]
> **`skill update` without `--name` exits 1 in any bootstrapped project.** It iterates over every directory in `<target>/.claude/skills/`, and the skills placed there by `init` come from the profile bundle, not the registry — so each is reported `not-in-registry` and the command exits 1 even though nothing is wrong. Measured against a target holding only bundled skills: two entries, both `not-in-registry`, rc 1. Use `skill update --name <name>` for a registry skill you actually installed.

> [!NOTE]
> The module requires `pyyaml`. The `claude-bootstrap` CLI already resolves its dependencies; to invoke the module directly: `uv run --with pyyaml --no-project python3 -m claude_bootstrap.skill <cmd>`.

---

*Cross-references: [01-canonical-anthropic.md](01-canonical-anthropic.md) §2 (Anthropic Skills standard) | [05-profiles.md](05-profiles.md) (the profiles that carry the bundles) | [07-glossary.md](07-glossary.md) (terminology)*
