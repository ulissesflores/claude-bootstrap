# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-08-11

**First public release.** The state-of-the-art publication gate (`D1-D8`) closed: licensing
resolved per skill directory (25 vendored + 5 first-party, each shipping its licence text),
provenance byte-verified against pinned upstream commits, docs bilingual (EN canonical,
PT-BR mirror), PII gate split into a structural public layer and a private local one, and
the registry live-validated. Highlights below are the entries dated 2026-08-03 through
2026-08-11; the full alpha history follows them.

### The version went 0.4.0a0 -> 1.0.0 across every surface (2026-08-11)

**Changed:**
- `pyproject.toml`, `claude_bootstrap/__version__.py`, `CITATION.cff` (version + release date),
  the marketplace + 6 plugin manifests (semver form), 6 `profile.yaml` + 6 `NOTICE.md`, the 5
  READMEs' pre-release note (now a release note), `CONTRIBUTING.md`, `AGENTS.md`, `llms.txt`,
  `docs/00/02/05/06/07` in both languages.
- The frontend Profiles row in the 5 READMEs and `docs/05` no longer stamps "(MIT)" over the
  3 Apache-2.0 `anthropics/skills` bundles.
- The tests badge is now forced by `tests/test_readme_badges.py` against live pytest
  collection — it can no longer silently rot (it had, twice).
- The registry's 13 github subpaths were re-resolved live at upstream HEAD (2026-08-11) and
  `last_validated_at` re-dated; the registry header no longer claims tiers auto-install.

### The PII gate was itself the leak; its private half now lives outside the repository (2026-08-10)

**Fixed:**
- `scripts/pii-scan.py` carried **14 person-, organisation- and host-specific literals, each with a
  caption explaining what it was**, and `ALLOWLIST = {"scripts/pii-scan.py"}` exempted the file from
  its own scan — so the gate against publishing private context passed green while being the largest
  concentration of it in the tree. The literals move to a gitignored `.pii-patterns.local`
  (`regex<TAB>reason` per line); the published script keeps only the **structural** pattern, the
  absolute-home-path regex, which identifies a developer machine for any user rather than this
  project's maintainer. The private context in the docstring and comments went with them.
- `ALLOWLIST` is **gone**, not emptied. The repo now scans with zero exemptions, and
  `tests/test_pii_scan.py::test_no_tracked_file_carries_a_home_path` holds it there — which is also
  the proof that nothing was hiding behind the old self-exemption.

**Changed:**
- The success line names which layers ran — `[structural only; no .pii-patterns.local]` versus
  `[+N local pattern(s) from .pii-patterns.local]`. Without it a fresh clone prints the same `clean`
  while running fewer patterns, which is a different result wearing the same words.
- A malformed line or an uncompilable regex in the local file is **fatal**. Skipping it would turn a
  typo into a silently narrower scan that still reports success.
- New `tests/test_pii_scan.py` (9 cases), scoped to the structural layer on purpose: a committed test
  that embedded the private literals to prove they are caught would recreate the leak. Those are
  covered by a manual canary instead — plant, stage, confirm `rc 1`, remove.

### The `superpowers` star count re-pinned in a single sweep (2026-08-10)

**Changed:**
- `obra/superpowers` measured at **270,213** stars through the GitHub API (2026-08-10) and written as
  `~270k` in all six copies that quote it — `docs/00-overview.md`, `docs/02-state-of-the-art.md`
  (§2, §4 ×2, §7) and `docs/07-glossary.md`, plus the three PT-BR mirrors. The previous value
  (`~263k`, measured 2026-07-29) was not false, because it was dated; the sweep exists so that the
  six copies carry **one** date instead of diverging every time a commit touches a single file.
- Two lines a number-only sweep would have left false were rewritten rather than substituted. The
  `02` header declared "the star counts in §4 and §7.1 were re-measured 2026-08-02", and the
  `superpowers` row in §4 is now 2026-08-10. The §4 note read "except `obra/superpowers` (~263k),
  measured **2026-07-29**" — that exception **inverts**, since the value becomes the newest figure in
  the file rather than the oldest. The note now also names `00-overview.md` alongside the glossary as
  a copy kept in sync.
- The §2 cell gained its date inline (`~270k stars (measured 2026-08-10)`). It was the file's only
  star count outside the scope the header declares, and therefore the only undated one.

### Link checking widened past `docs/`, and its transient-code guard turned out to be vacuous (2026-08-10)

**Fixed:**
- `scripts/validate-refs.sh` scored **every curl timeout as a dead link**. On failure curl still
  writes its own `000` through `-w "%{http_code}"`, without a trailing newline, so
  `code=$(curl ... || echo "000")` produced the literal string `000000`, which never matched the
  `429|503|000` transient list. The fallback now sits on the assignment (`code=$(curl ...) ||
  code="000"`), canary-verified against a forced failure: old form `[000000]` → DEAD, new form
  `[000]` → WARN. This is the real cause of the exit-code non-determinism previously attributed to
  slow third-party hosts.

**Changed:**
- The scan set grows from README/AGENTS/CLAUDE/CHANGELOG/llms.txt + `docs/**` (25 files, 80 URLs) to
  **37 files, 89 URLs**: the four translated READMEs, `.github/*.md`, and the five **first-party**
  bundled skills. A skill counts as first-party when its `LICENSE.txt` is byte-identical to this
  repo's `LICENSE` — the same set `verify-skill-provenance.py` reports as `FIRST-PARTY`. The 25
  vendored skills stay out on purpose: they are byte-pinned upstream copies carrying placeholder
  URLs (`localhost`, `example.com`, `doi.org/10.XXXX/YYYY`) that are dead by design and cannot be
  edited without breaking the provenance byte-compare.
- Two guards against a vacuous scan: every scan target must exist, and the first-party selector must
  match at least one skill; both exit 99, outside the dead-count range.
- Dead URLs go 2 → 3. The third is `.github/SECURITY.md`'s advisory link, 404 only because the
  repository is private — the same path on a public repository answers 200 to an anonymous request
  (measured 2026-08-10). All three clear when the repo flips public.
- `llms.txt` is now English, matching the canonical `docs/`, with a pointer to the `docs/pt-br/`
  mirror. `README.pt-br.md`'s 12 documentation links retarget to `docs/pt-br/`; the `docs/assets/`
  image paths stay, since the assets have no mirror.

### `graphify` removed from the registry: it had stopped installing, and `skill list` said otherwise (2026-08-03)

The registry's only tier 3 and only `user-invocable` entry pointed at `skills/graphify` in
`obra/superpowers`. Measured: the recursive git tree at `HEAD` holds 234 paths, is not truncated,
and contains no such subpath — so `skill add graphify` returned `subpath-missing`, exit code 1.

The defect worth recording is not the dead subpath, it is that **`skill list` printed the entry as
`available` the entire time.** `fmt_status` (`skill.py:59`) answers "is this installed in the
target", never "does this source resolve", so the one surface a user reads asserted the opposite of
the truth. The entry's `unstable: true` flag did not compensate: that field is documentation only,
read by no code. Same failure class that de-bundled `release-manager` on 2026-06-29, on the axis
where nothing re-checks it — `validate` resolves no remote URLs by design, and no test resolves a
github subpath.

**Removed:**
- `graphify` from `claude_bootstrap/registry/skills.yaml`. The registry is now **13 skills**
  (tier 1: 8, tier 2: 5, tier 3: **0**). `skill list --tier 3` returns an empty list, not an error,
  and §6 of `docs/04-skills-curated.md` keeps the tier defined for the next experimental entry.

**Changed:**
- The 14 → 13 count propagated across every surface that stated it: `AGENTS.md`, `docs/README.md`,
  `docs/00-overview.md`, `docs/04-skills-curated.md`, `docs/07-glossary.md`, their four PT-BR
  mirrors and `tests/test_skill.py`.
- `docs/04-skills-curated.md` §4 said "8 of the 14 individually installable skills whose `profiles:`
  field includes `universal-software`". Measured: **all 13 entries list `universal-software`** — the
  8 is the tier 1 count, not a per-profile filter. Corrected in both copies.

### OSS hygiene: licence precision in the 5 READMEs, a measured coverage floor in CI (2026-08-03)

**Changed:**
- The READMEs claimed bundled skills keep upstream licences "(MIT / Anthropic)". Anthropic is not a
  licence: measured across the 30 bundled skill directories, the set is **MIT or Apache-2.0**, with
  30 of 30 shipping the full text as `LICENSE.txt`. The sentence also swallowed the 5 first-party
  skills, which carry this project's own MIT and have no upstream. Corrected in all five languages,
  stating the licence *set* rather than counts that rot on the next de-bundle.
- `.github/SECURITY.md` no longer pins a supported-version table. It was a fourth version surface
  held by no test, and the `0.4.0a0` → `1.0.0` bump would have made it declare the shipping version
  unsupported; the rule above it already said the same thing without numbers.

**Added:**
- `pytest-cov` and a `--cov-fail-under=30` floor on the CI test job, against a measured **35%**
  (1 660 statements, identical on Python 3.11 and 3.13). `skill.py` and `uninstall.py` report 0%
  because the subprocess tests spawn `uv run --no-project`, where the tracer never loads — the true
  figure is higher, and the caveat is stated in `ci.yml` and `pyproject.toml` rather than left for a
  reader to infer.

### The default profile stops shipping empty: 5 first-party skills + a `FIRST-PARTY` provenance class (2026-07-28)

`universal-software` is the profile most users land on by detection, and it bundled **zero
skills** — the likeliest path through the tool was the poorest one. It now ships 5 skills written
in this repository (skills 25 → **30**), which also dilutes a concentration risk: 19 of the
previous 25 came from a single third-party repository.

**Added:**
- **5 first-party skills** in `universal-software/skills/`, each with the full MIT text as
  `LICENSE.txt` inside its own directory:
  - `newproj` — prevention loop before new code: intent, then mandatory prior art, then a gated plan.
  - `ponytail` — review lens for reuse and minimalism, applied from line to architecture.
  - `recover` — post-crash session recovery from on-disk evidence only, persisting state before resuming.
  - `refactor` — healing loop driven by churn × size data rather than by hunch.
  - `vetting-agent-skills` — security gate for adopting a third-party `SKILL.md`, treating it as
    untrusted *instructions* with persistence, not merely as an untrusted dependency. Its
    allowlist is explicitly an **identity** allowlist: a trusted owner is not a licence, and the
    skill says so with the measurement behind it — 2 of the 7 well-known skill repositories it
    lists have no root `LICENSE` at all. That is the same conflation that produced this project's
    own 2026-07-24 P0, so shipping the gate without it would have contradicted the CHANGELOG entry
    directly below this one.
- **A `FIRST-PARTY` provenance verdict**, third alongside `EXACT` and `WS-ONLY`. A skill authored
  here has no upstream, therefore no commit to pin, no HEAD to diff, and nothing to fetch — that is
  a distinct class, not a missing one. `rows()` gained a second pattern returning `owner is None`,
  and all four of its consumers were taught the class: `do_currency()` skips it (no HEAD to
  compare), `do_verify()` reports it while still asserting `SKILL.md` is on disk, and
  `audit.py::_provenance_map()` reports `provenance: "first-party"` instead of counting it in
  `files_missing_provenance`. `do_sync()` skips it as a **data-loss guard**: `copytree(...,
  dirs_exist_ok=True)` over an authored directory would overwrite the work it was meant to update.
- **`universal-software/.claude-plugin/plugin.json`** and its `marketplace.json` entry — the
  profile had neither, which silently made `test_advertised_skill_counts_match_disk` **vacuous**
  for it (the marketplace check is scoped by a per-profile regex and the manifest check is guarded
  by `is_file()`, so zero assertions ran). `test_plugin_manifest.py::PROFILE_NAMES` now includes the
  profile, so its manifest is held to the same full structural contract as the other five.
- **`test_license_reaches_the_users_tree_on_emit`** — every other redistribution test inspects
  `templates/`, which left the load-bearing step unasserted: whether `install.py` actually copies
  `LICENSE.txt` into the target. A packaging change that dropped it would ship an unlicensed skill
  with the suite green. Scoped to `universal-software` — the default profile, and the one whose
  licence obligation is this project's own. Mutation-tested: removing one `LICENSE.txt` turns it red.
- **7 patterns in `scripts/pii-scan.py`** covering the private-context name classes the source
  skills referenced. The genericisation is manual work, so the check that it happened must not be:
  each pattern was mutation-tested to fire on the real strings and to stay silent on benign
  near-miss words.

**Changed:**
- Advertised counts propagated 25 → 30 across every surface: the badge and profile table in all 5
  READMEs, `AGENTS.md`, `llms.txt`, `docs/00-overview.md`, `docs/04-skills-curated.md`,
  `docs/05-profiles.md`.
- The bundle is now described as **`provenance-verified`** rather than `provenance-pinned`,
  in all 10 places across the 5 READMEs (badge, comparison-table row, feature bullet). With 5
  first-party skills in it, "30 provenance-pinned" would be false for a sixth of the bundle —
  nothing pins a skill that has no upstream. Every one of the 30 is provenance-*verified*, and
  the READMEs now state the 25 / 5 split explicitly.
- `docs/04-skills-curated.md` §4's heading now says "tier 1 **do registry**". It counts 8 skills
  eligible for `universal-software` on the *registry* axis, which read as a contradiction next to
  the new "5 bundled" line in the same file.
- `tests/test_settings_tiers.py::test_strict_source_file_does_not_leak_into_emit` asserted the
  emitted `.claude/` was exactly `{settings.json, .bootstrap-manifest.json}` — which silently
  depended on `universal-software` shipping no skills. `skills` was added to the expected set,
  kept exact so a stray artifact still fails it.

### Third-party redistribution rights: 4 skills de-bundled, 22 licence notices shipped (2026-07-26)

A publication audit found the package was shipping **55 files it held no right to redistribute**,
inside a wheel declared `license: MIT` and bound for PyPI and a permanent Zenodo DOI. Every bundled
skill was then resolved to its upstream licence by reading the source at the pinned commit — root
licence, per-skill override, and `SKILL.md` frontmatter — rather than by inference.

**Removed** (skills 29 → **25**; `academic` 7 → **3**):
- **`docx`, `pdf`, `pptx`** (`anthropics/skills`) — their `LICENSE.txt` is a pure restriction list
  with **no grant clause**: it forbids retaining copies outside Anthropic's Services, reproducing,
  creating derivative works, and distributing to third parties.
- **`doc-coauthoring`** (`anthropics/skills`) — **no licence at all**. That repo has no root
  `LICENSE`, and this was the only 1 of 17 skill directories there without its own `LICENSE.txt`.
  Absence of a licence is default copyright, not a permissive default. It had been recorded as
  "Per upstream"; there is no upstream to defer to.
- The empty `data-science/skills/xlsx/` shell left over from its 2026-06-06 de-bundling.

We deliberately do **not** auto-fetch these instead: that would only move the copying onto the
user's machine. `academic/NOTICE.md` points at Anthropic directly.

**Added:**
- **The full MIT licence text inside each of the 22 MIT-licensed skill directories** (19
  `alirezarezvani` + 3 `K-Dense-AI`). MIT requires the copyright and permission notice to travel
  with every copy, and `install.py` copies `skills/<name>/**` only — so a profile-level `NOTICE.md`,
  which is what we had, never reached the user's tree at all. `devops/NOTICE.md` had additionally
  been eliding the notice with `...`; it now carries the unabridged text.
- **`tests/test_redistribution_rights.py`** — the class of defect that survived five model audits,
  encoded as an executable gate. Two independent questions: do we hold the right (no skill without
  a licence; the de-bundled set stays out), and do we meet its conditions (the grant text ships
  inside the skill directory). The reappearance guard imports `verify-skill-provenance.py::rows()`
  rather than reimplementing it, because `--sync` rebuilds the tree from `NOTICE.md` rows, not from
  the filesystem — deleting a directory without deleting its row silently re-vendors it.
- **Apache-2.0 §4(b) modification notice** in `frontend/NOTICE.md`: `web-artifacts-builder` and
  `webapp-testing` differ from upstream by trailing-whitespace normalisation only.

**Fixed:**
- `academic/NOTICE.md` provenance pins were stale (`anthropics/skills@da20c92`,
  `K-Dense-AI@9312485`) against the actual `skill-pins.json`.

### Publishability: institution-specific profile removed + PII gate (2026-07-23)

**Removed:**
- **The deprecated institution-specific academic profile** — the whole
  `templates/profiles/_deprecated/` tree (profile + 5 skills + 3 rules), its 5 registry
  Tier-1 entries, and the `install.py:_profile_dir()` fallback that resolved it. It encoded
  one institution's pedagogical workflow and had no place in a universal tool. Projects that
  used it move to `academic`. Registry catalogue: 19 → **14** skills.
- **`interview.py`**: `DEPRECATED_PROFILES` / `ALL_PROFILES` gone; `--profile` now accepts
  the 6 live profiles only.

**Changed:**
- **`detect.py` academic heuristic is generic** — any `*.csl` (Citation Style Language) file
  is now an academic marker, replacing a hard-coded institution-specific filename; the
  institution's `MIT<n>/` module-directory convention was dropped (it detected nothing that
  `*.tex` / `*.bib` / `*.csl` don't already cover). `.csl` is guarded by the same
  no-code-project rule as `.bib`, so a doc pipeline vendoring a citation style can't hijack a
  source repo. Academic detection stays at 0.95.
- **`marketplace.json`**: the `devops` plugin description no longer advertises "release
  management" — `release-manager` was de-bundled 2026-06-29.
- **i18n re-sync (ES / IT / HE)**: badges, skill counts, the `backend` profile row, the
  shipped monorepo-union wording, and the doctor check count were all stale. The Hebrew
  README's six in-document nav anchors pointed at English heading slugs and were dead —
  repointed at the Hebrew headings.

**Added:**
- **`scripts/pii-scan.py`** — a gate that scans `git ls-files` for personal or
  institution-identifying strings (absolute home paths, private workspace names, coursework
  codes, institution acronyms) and fails on any hit. Wired into `.pre-commit-config.yaml` and
  the `lint` CI job. Authorship metadata (`CITATION.cff`, `pyproject.toml`) is deliberately
  out of scope.
- **`tests/test_metadata_currency.py`** — asserts that what the repo *declares* exists on
  disk: version sync across `pyproject.toml` / `CITATION.cff` / `__version__`; every offered
  profile has a `profile.yaml` and every `profile.yaml` is offered; every declared skill and
  rule is present; every bundling profile has a `NOTICE.md`; every registry entry targets a
  real profile and resolves its `local` source. Deliberately free of hardcoded inventory
  counts, so ordinary growth never reddens it.
- **CI/release hardening** — `ruff check` + `ruff format --check` replace the old
  `ast.parse` loop (strict superset; vendored `templates/` excluded via `[tool.ruff]
  extend-exclude`), `cffconvert --validate` runs in CI, and `release.yml` gains a `test` job
  that `publish-pypi` and `github-release` now depend on, so a release cannot ship past a red
  suite. Ruff and cffconvert are pinned in CI and present in the `dev` extra.
- Internal working material (`tasks/`, `.kickoff/`, audit reports) is now gitignored — it
  stays on disk but is no longer tracked, and the docs no longer link into it.

### Adversarial-audit remediation (2026-07-24)

**Fixed:**
- **`detect.py`: the `.csl` guard covers every ecosystem.** It reused the `.bib` guard, whose
  marker list is Python/Node/Rust only, so a Go/Java/Ruby/PHP/.NET or IaC repo with a root
  citation style reclassified to `academic` at 0.95 — and because `academic` is exclusive,
  that also skipped the per-subdir monorepo scan. `.bib` deliberately keeps the narrow list:
  `go.mod` + `paper.bib` is the standard JOSS submission shape and stays academic.
- **`pii-scan.py`: the case/boundary hardening now covers every literal pattern.** Only two of
  the five had it, so a lowercased path form, a lowercased run-together spelling, and an
  underscore-separated variant of the remaining three all evaded the gate — the same defect
  class that had already been caught leaking twice. The home-path rule also reaches Linux
  (`/home/<user>/`) and usernames with digits, dots or hyphens, exempting the
  `user`/`usuario` placeholder the docs use when teaching that absolute paths are an
  anti-pattern.
- **`install.py`: `load_profile()`'s docstring** no longer advertises the `_deprecated/`
  fallback removed above — a false claim that shipped inside the wheel.
- **`doctor`, `detect` and `audit` `--help`** printed `usage: doctor.py` instead of their real
  invocation, leaking the module filename.
- **`validate-refs.sh`: 429/503 are WARN, not DEAD.** Counting a rate-limit as a dead link made
  the exit code non-deterministic by construction.
- **Test coverage that had gone hollow** — the subdir-examples test was retargeted to an
  unresolvable profile name, so it returned before the branch it names and would have stayed
  green with that branch deleted; it now runs against a synthesized templates tree, with the
  unknown-profile contract split into its own test. `test_metadata_currency.py` imports
  `PROFILES` instead of scraping the literal out of `interview.py`, which broke the moment
  `ruff format` exploded the list past `line-length` — the exact "adding a profile must not go
  red" case the file promises to tolerate.

**Added:**
- **`scripts/verify-wheel-tracked.py`** — every file inside the built wheel must be tracked in
  git. `MANIFEST.in` recursive-includes `templates/` and the build reads the filesystem, so an
  untracked leftover (a stale skill dir, an editor backup, half a rename) would be published
  and DOI-archived carrying no NOTICE row or licence attribution. Every existing gate reads a
  different source — git, `NOTICE.md`, `profile.yaml` — and none reads the artifact's own file
  list. Wired into `release.yml`'s `build` job.
- **`skill-drift.yml` gains a `link-check` job** running `validate-refs.sh` weekly. Kept out of
  the blocking `lint` job because it is network-dependent.

**Changed:**
- **`.pre-commit-config.yaml`**: the three rewriting hooks (`trailing-whitespace`,
  `end-of-file-fixer`, `mixed-line-ending`) now skip `claude_bootstrap/templates/`, matching
  the ruff hooks. Those bytes are vendored upstream skills redistributed verbatim under their
  own licence; normalizing them is what breaks provenance, and
  `verify-skill-provenance.py` only byte-compares `SKILL.md`, so a rewrite under `references/`
  or `scripts/` would pass the gate silently.

**Removed:**
- **`docs/assets/demo.svg`** — a hand-authored illustration referenced by no file, depicting a
  CLI flow that no longer exists.

### Multi-profile monorepos (DB-a, 2026-07-01) — Model-A union + per-subdir CLAUDE.md

**Added:**
- **Multi-stack detection** — `detect` now discovers sub-projects (bounded workspace-aware
  enumeration + prune-list) and returns `profiles: [...]` + `stack_paths: {profile: [dir]}` for a
  monorepo, keeping `profile_suggestion` for back-compat. A repo with several stacks in subdirs
  (e.g. `frontend/` + `backend/`) detects the whole set instead of one. `academic` stays exclusive.
- **New `backend`/service profile** (config-only) — detects a web framework
  (FastAPI/Flask/Django/Express/NestJS/Rails/Spring/…) and emits guidance + a permission baseline +
  4 curated skills (`api-design-reviewer`, `api-test-suite-builder`, `database-schema-designer`,
  `migration-architect`; `alirezarezvani/claude-skills`, MIT) + a path-scoped rule. **Never installs
  dependencies** — the enforced guarantee is tool-side (`install.py` shells no package manager).
- **Model-A union emit** — a monorepo emits one root `.claude/`: union permissions (sorted-iteration
  merge, byte-stable), all profiles' skills (with same-name/different-content collision surfacing),
  and a `rules/<stack>.md` per profile with `paths:` derived from the discovered dirs.
- **Per-subdir `CLAUDE.md`** — a thin directory-scoped `CLAUDE.md` per discovered sub-project, riding
  native on-demand subtree loading; root-filtered (never clobbers the root union file, hardened
  against `..`-overshoot / absolute-path escapes), manifest-tracked + uninstall-reversible.
- **`--profile` is repeatable** — pass it more than once for a manual multi-profile union; the
  non-interactive default is the detected set.
- `audit` is union-aware (reads `profiles[]`, unions NOTICE maps across profiles, reports the set);
  `doctor` matches a plural `profiles:` footer + reports rules-present (13 checks).

**Unchanged (invariant):** single-profile repos emit **byte-identically** (singular `profile:` footer,
static subdir-examples, extension-scoped rules, scalar `profile` manifest). Release stays deferred.

### SOTA refresh (2026-06-29) — currency + security + 3 opt-in features

**Added** (opt-in, off-by-default, manifest-tracked, TDD):
- **Model resilience** — `--fallback-model` emits `fallbackModel: "sonnet"` (graceful degrade if the primary model is unavailable, e.g. the Fable 5 export-suspension). Absent by default.
- **Conservative hooks bundle** — `--hooks` now also emits a `UserPromptSubmit` forced-eval skill-dispatch nudge (skills under-fire without one; empirical ja/ko/zh ~25%→~84-100%), alongside the existing warn-only `PreToolUse` hook. Inline, exit 0, default-absent. (A `PreCompact` reminder was prototyped but dropped — PreCompact command-hooks have no context-injection channel, so the echo never reached the model; compaction-preserve, if wanted, belongs in a CLAUDE.md directive.)
- **`docs/01 §13` Security & trust boundary** — pre-trust-dialog risk class (CVE-2025-59536), recommended current-stable Claude Code min-version, a deny-baseline audit, and the skills supply-chain risk (ToxicSkills/Snyk). Defensive guidance — not a vuln in our benign emit.

**Changed** (currency — live re-verified vs `code.claude.com/docs`, 2026-06-29):
- **Model lineup** dated 2026-06-29: Opus 4.8 = top usable default; Fable 5/Mythos 5 GA'd 2026-06-09 then **export-suspended** 2026-06-12; Opus 4/Sonnet 4 retired. `--model` alias table corrected (`default·best·fable·opus·sonnet·haiku·opusplan·[1m]`); **`inherit` reclassified** as a subagent-frontmatter value (not a top-level `--model` alias).
- **`docs/01`**: sandbox schema gains `credentials`/`allowAppleEvents` + network keys; new settings keys noted (`fallbackModel` et al.); Workflows wording drops "research preview"; skills≡commands + governance gates; glossary handler-types fixed to 5.
- **Schema pins** re-verified live (9/9 LIVE) and dated 2026-06-29.
- **Skills re-synced to upstream HEAD** (`verify-skill-provenance.py --sync`; 3/3 CURRENT); license + bandit re-checked (no new HIGH).

**Removed:**
- **De-bundled `release-manager`** from `devops` — removed from upstream HEAD (no longer provenance-verifiable). `devops` → **5** skills, total bundled → **25**. Counts updated across docs + 5 READMEs + tests.

### Added (SOTA readiness campaign — jun/2026; all opt-in / off-by-default, manifest-tracked, TDD, schema-verified live vs official docs)
- **`.claude/agents/` subagents** (D05): one descriptive (non-auto-spawn) subagent per code profile, manifest-tracked.
- **`.mcp.json.example`** (D06): opt-in, project-scoped MCP template (pending-approval by design).
- **Schema drift-guard** (D00): `scripts/schema-sources.json` + `scripts/verify-schema-currency.py` (`--check` flags any pinned schema older than 90 days) + a weekly `schema-currency` CI job — the tool's identity is currency, so every emitted schema is now watched.
- **Permission tiers** (`--tier lax|strict`, D01): a `strict` baseline with a narrow allow-list and `deny ⊇ lax`; default stays `lax` and byte-identical.
- **Opt-in sandbox** (`--sandbox`, D02): emits a `sandbox` block with `denyRead` for `~/.aws`/`~/.ssh` (closes the documented default-read gap); absent by default.
- **Opt-in hooks** (`--hooks`, D04): a conservative warn-only `PreToolUse` Bash hook (inline command, never `exit 2`); absent by default.
- **Plugin-manifest expansion** (D07): the 4 profile `plugin.json` gain `$schema`, `displayName`, `defaultEnabled: false` (opt-in bundles), and extended `keywords` — validated by `claude plugin validate`.
- **AGENTS.md interop** (D09): when a repo already ships an `AGENTS.md`, the emitted root `CLAUDE.md` adds an `@AGENTS.md` import (detected at emit time; absent otherwise).
- **Opt-in `statusLine` + output styles** (D11): a profile can declare a `statusLine` settings-override and ship `.claude/output-styles/<name>.md`; the `academic` profile opts into a `concise-academic` style. Off by default for every other profile.
- **`claude-bootstrap audit` subcommand** (D13a): an offline provenance + integrity report (`claude-bootstrap.audit/v1`) — per-skill upstream `source{owner,repo,pinned_sha,url}`, on-disk-vs-manifest `manifest_match`, permission summary, and a `PASS|MODIFIED|INCOMPLETE` verdict (`--json`, `--strict`). A tampered emit flips to `MODIFIED`.
- **Skills currency check** (D13b): `verify-skill-provenance.py --check-currency` compares each bundled pin against the upstream HEAD (length-agnostic prefix match) — `CURRENT|STALE|UNKNOWN`, exit 1 on any `STALE`.

### Changed (currency — D08, D10)
- **Emitted `CLAUDE.md` reconciles with Claude Code auto-memory**: the `## Memory` block now names `~/.claude/projects/<proj>/memory/MEMORY.md` (≤200 lines/25 KB, written by Claude) distinctly from the human-curated `PROJECT-STATE.md`, and states claude-bootstrap never writes into the auto-memory dir.
- **`docs/01` currency sweep** (verified live vs `code.claude.com/docs`, 2026-06-08): all 30 hook events + 5 handler types + exit-code table; the 6 permission modes; a new Sandbox section (with the `~/.aws`/`~/.ssh` `denyRead` warning); expanded plugin-manifest fields + component types; and the explicit Workflows/Routines non-emittable boundary (§11.1, D12).

### Fixed
- **`init` crashed from the pip-installed wheel** (release-blocker, Bug 11). `pip install` byte-compiles
  bundled skill `.py` into `__pycache__/*.pyc`; `install_profile_assets` read every file as UTF-8 text and
  hit a `.pyc` binary → `UnicodeDecodeError`. Now skips compiled bytecode + reads sources as explicit
  UTF-8. Proven on a clean Python 3.14 venv. Caught by the publication-gate's pip-wheel E2E (the fire-test
  campaign used `uv tool install`, which doesn't byte-compile the data dir, so it never saw it).
- `CLAUDE.md` no longer ships a `> (no description)` placeholder in `--non-interactive` runs.
- CI `demo.yml` (GIF regen) now installs `ffmpeg` explicitly; removed a dead doc reference.

### Changed (emitted-content quality — from the frente-2 audit)
- **devops permission baseline hardened**: deny `Read(**/*.tfstate)`/`Read(**/*.tfvars)` (plaintext
  secrets), `terraform state rm/mv`/`import`/`taint` (state surgery), `docker system prune`/`volume rm`;
  allow `terraform init`.
- **Path-scoped `rules/` authored** for `devops` (IaC: plan-before-apply, never hand-edit tfstate, pin
  image tags), `data-science` (data hygiene + train/test leakage; complements `notebooks/CLAUDE.md`),
  `frontend` (types, a11y, no client secrets; glob covers `.tsx/.ts/.jsx/.vue/.svelte/.astro`), and
  `academic` (`**/*.tex`/`**/*.bib`: one-claim-one-citation, `\label`/`\ref`, `latexmk`) — `.claude/rules/`
  was empty before.
- **Base `.gitignore`** now ignores ML artifacts (`mlruns/`, `.ipynb_checkpoints/`, `*.pkl`/`.pt`/`.ckpt`)
  and LaTeX build artifacts (`*.aux`/`*.bbl`/`*.synctex.gz`/`*.fdb_latexmk`/…).
- **`.env` Read-deny is now recursive** (`Read(**/.env)`) — a monorepo `packages/app/.env` no longer
  slips past the old root-anchored deny.
- **README is now 5-language**: English (primary) + Português + Español + Italiano + עברית (RTL), shared
  language nav; all `docs/` remain English.

### Removed
- **De-bundled 3 misfit/low-quality skills** (skills 29 → 26): `xlsx` from `data-science` (a
  financial-modeling skill), `senior-devops` from `devops` (3 identical no-op stub scripts; SKILL.md
  documents flags the script rejects), and `theme-factory` from `frontend` (a slide-deck theming skill
  whose SKILL.md mandates an unshipped `theme-showcase.pdf`). `data-science`/`devops` → 6 skills each,
  `frontend` → 7. The underlying upstream defects (`senior-devops`, `ci-cd-pipeline-builder`) are filed
  as [`alirezarezvani/claude-skills#807`](https://github.com/alirezarezvani/claude-skills/issues/807).

## [0.4.0a0] — 2026-05-14 (real curated profiles + hierarchical CLAUDE.md)

> Phase H delivery. Replaces v0.3.0a0's placeholder profiles with real,
> evidence-backed skill bundles. Adds the Anthropic-canon subdirectory `CLAUDE.md`
> filesystem-walking mechanism. Deprecates the institution-specific academic profile in favor of generic `academic`.

### Added — Phase H

**Phase H1 — Anthropic-canon skill inventory**:
- Read-only inventory of `anthropics/skills` (17 canonical skills) + `anthropics/claude-code/plugins/` (13 plugins)
- Categorized by domain + per-profile mapping

**Phase H6 — CLAUDE.md hierarchical mechanism**:
- `_base/CLAUDE.md.j2` documents all 3 layered context mechanisms: root CLAUDE.md, path-scoped rules in `.claude/rules/`, and **subdirectory CLAUDE.md files** (filesystem walking, on-demand load)
- New `templates/profiles/<P>/subdir-examples/<subdir>-CLAUDE.md` convention; `install.py` auto-installs to `target/<subdir>/CLAUDE.md` when profile ships them
- 5 subdir examples per profile: `scripts/CLAUDE.md` (universal), `src/CLAUDE.md` (frontend), `notebooks/CLAUDE.md` (data-science), `infra/CLAUDE.md` (devops), `manuscript/CLAUDE.md` (academic)

**Phase H7 — Integrate 50 curated URLs**:
- Cross-referenced 50 URLs against local sources + Anthropic canon
- Identified 3 skill-bearing community repos with proper SKILL.md format:
  - `K-Dense-AI/scientific-agent-skills` (21.7k★, MIT, 137 scientific SKILL.md)
  - `alirezarezvani/claude-skills` (14.8k★, MIT, 73 engineering+team SKILL.md)
  - `forrestchang/andrej-karpathy-skills` (129.5k★, MIT, karpathy-guidelines meta-skill)
- `docs/02-state-of-the-art.md` updated with §7.1 ecosystem refs (12 new URLs)

**Phase H3 — Frontend profile curated (8 skills)**:
- Anthropic canon: `frontend-design`, `web-artifacts-builder`, `webapp-testing`, `theme-factory` (+ 10 themes)
- alirezarezvani MIT: `senior-frontend`, `browser-automation`, `ui-design-system`, `full-page-screenshot`
- `profile.yaml` permissions: `Bash(npm run *)`, `Bash(pnpm *)`, `Bash(playwright test *)`, etc.

**Phase H5 — Academic profile (new) + deprecate the institution-specific one**:
- New generic `academic` profile (7 skills):
  - Anthropic canon: `doc-coauthoring`, `pdf`, `pptx`, `docx`
  - K-Dense MIT: `citation-management`, `exploratory-data-analysis`, `exa-search`
- The earlier institution-specific academic profile moved to `_deprecated/` (history preserved)
- `install.py:_profile_dir()` falls back to `_deprecated/` so the deprecated name still resolves (backwards compat)
- `interview.py` gains a `DEPRECATED_PROFILES` list; `detect.py` distinguishes generic LaTeX/BibTeX (academic, 0.95) from institution-specific markers (deprecated profile, 0.85)

**Phase H2 — Data-science profile (7 skills)**:
- Anthropic canon: `xlsx`
- alirezarezvani MIT: `senior-data-scientist`, `senior-ml-engineer`, `senior-data-engineer`, `rag-architect`, `sql-database-assistant`, `senior-computer-vision`
- `profile.yaml` permissions: `Bash(jupyter *)`, `Bash(uv run *)`, `Bash(dvc *)`, `Bash(mlflow *)`

**Phase H4 — Devops profile (7 skills, 100% community MIT)**:
- alirezarezvani MIT: `ci-cd-pipeline-builder`, `kubernetes-operator`, `release-manager`, `runbook-generator`, `observability-designer`, `secrets-vault-manager`, `senior-devops`
- Security-conscious permissions: read/plan **allowed** (`Bash(terraform plan *)`, `Bash(kubectl get *)`), destructive operations **denied** (`Bash(terraform destroy *)`, `Bash(kubectl delete *)`)

**Phase H8 — Documentation alignment**:
- `README.md` + `README.pt-br.md`: profiles table reflects real skill counts (no more placeholders)
- This CHANGELOG entry
- `docs/02-state-of-the-art.md`: 12 new URL refs added

### Changed

- `claude_bootstrap/__version__.py`: `0.3.0a0` → `0.4.0a0`
- `pyproject.toml` version: `0.3.0a0` → `0.4.0a0`
- `pyproject.toml`: new `[tool.pytest.ini_options]` limits collection to `tests/`
- `claude_bootstrap/install.py:install_profile_assets` extended for `subdir-examples/`
- `claude_bootstrap/registry/skills.yaml`: 5 institution-local skill paths updated to `_deprecated/`

### Deprecated

- The institution-specific academic profile — replaced by generic `academic`. Still loadable by name (uses `_deprecated/` fallback). Removed from interactive prompt (`PROFILES`), kept in CLI choice list (`ALL_PROFILES`).

### License compliance

- All redistributed skills preserve upstream license. Per-profile `NOTICE.md` documents provenance + license.
- Binaries excluded for size (XSD schemas, PDFs, tarballs) — fetch upstream for full assets.

### Test counts

Before Phase H: 28. After Phase H: 34 (+6 profile/feature tests).

### Verification

- `pytest`: 34/34
- `pre-commit run --all-files`: 11/11 hooks pass
- `validate-refs.sh`: 74 URLs checked, 0 NEW dead (5 baseline private-repo URLs expected — will resolve when repo goes public per Phase G)
- Smoke install validated for every active profile

## [0.3.0a0] — 2026-05-07 (planned as the first public release — not shipped; the repository stayed private until v1.0.0)

### Added — Phase A through G (pre-publication hardening)

**Phase A — code quality (4 critical + 4 important fixes, 4 regression tests)**:

- `bin/skill.py:install_github`: git clone timeout=60 (was hang-forever); reorder rmtree to AFTER clone success (was data-loss on partial fail); `shutil.copytree` with `symlinks=True`
- `bin/install.py:load_vars`: try/except `json.JSONDecodeError` for 3 input paths (file/CLI/stdin) → graceful sys.exit(2)
- `bin/install.py`: helpers `_safe_write` + `_safe_read` wrap all OSError; load_profile guards yaml.safe_load with YAMLError
- `bin/skill.py:cmd_validate`: warns on `last_validated_at >90d` (STALE_DAYS const)
- `bin/interview.py:detect_git_remote`: `except (FileNotFoundError, subprocess.TimeoutExpired, CalledProcessError)` (no longer swallows KeyboardInterrupt)
- 4 new regression tests: invalid JSON vars, invalid YAML profile, readonly target, stale entries warn

**Phase B — refs migration (94 URLs audited)**:

- All 13 `docs.anthropic.com/en/docs/claude-code/X` URLs → `code.claude.com/docs/en/X` (Anthropic 301-redirected docs migration mai/2026)
- `groundy.com` 404 → replaced by `code.claude.com/docs/en/plugins`
- `scripts/validate-refs.sh` (cron-able): extracts URLs, HEAD-checks via curl with Mozilla UA, distinguishes 4xx-real from bot-blocked (medium, marketplace.visualstudio, etc)
- AGENTS.md, CLAUDE.md procedural refs updated

**Phase C — installable Python package**:

- `bin/*.py` → `claude_bootstrap/*.py` (proper package layout)
- `templates/` + `registry/` → `claude_bootstrap/templates/` + `claude_bootstrap/registry/` (bundled via MANIFEST.in for PyPI install)
- `claude_bootstrap/__version__.py`: single source of truth `__version__ = "0.3.0a0"`
- `claude_bootstrap/cli.py`: dispatcher with try/except SystemExit (modules' sys.exit no longer kills wrapper)
- `pyproject.toml`: full `[build-system]` + `[project]` + `[project.scripts]` + URLs + classifiers + dependencies
- `bin/bootstrap.sh`: thin wrapper exporting PYTHONPATH + calling `python -m claude_bootstrap.cli`
- `tests/conftest.py:run_python`: uses `python -m claude_bootstrap.<module>` with PYTHONPATH (works regardless of cwd)
- CI: paths `bin/*.py` → `claude_bootstrap/*.py`; new lint steps (build wheel + smoke pip install)

**Phase D — 3 install methods**:

- PyPI: `pip install claude-bootstrap` (after release.yml first run)
- curl installer (`install.sh`): detects Python 3.11+, prefers pipx, falls back to private venv at `$XDG_DATA_HOME/claude-bootstrap` (PEP 668 safe)
- `.github/workflows/release.yml`: triggers on `v*.*.*` tag → build wheel + sdist → publish PyPI via OIDC trusted publishing → upload artifacts to GitHub Release

**Phase E — bilingual README marketing**:

- `README.md` (EN, primary): tagline, 4 badges, install (3 methods), quick start, why, mermaid architecture, profiles table, file tree, docs index, 7 principles, develop/contribute
- `README.pt-br.md`: full PT-BR translation (não mecânica), bidirectional cross-link

**Phase F — OSS hygiene (10 files)**:

- `CONTRIBUTING.md`: dev setup, bug reporting, feature proposing, PR checklist, style guide, profile/skill addition
- `RELEASE.md`: maintainer-only release procedure (PyPI trusted publishing setup, version bump, tag, hotfix, yanking)
- `.github/SECURITY.md`: vuln reporting (private channels), 72h ack SLA, supported versions, threat model out-of-scope
- `.github/CODE_OF_CONDUCT.md`: Contributor Covenant 2.1
- `.github/CODEOWNERS`: `@ulissesflores`
- `.github/dependabot.yml`: weekly pip + github-actions updates
- `.github/PULL_REQUEST_TEMPLATE.md`: type checkboxes + checklist + test plan
- `.github/ISSUE_TEMPLATE/{bug_report,feature_request,config}.yml`: forms + Discussions/Security links

**Phase G — verification + go public + first release** (planned steps; the go-public half was deferred and executed at v1.0.0):

- E2E verified: pytest 28/28 in ~2.5s, pre-commit clean, CI 4/4 verde, wheel+sdist build, `pip install dist/*.whl` works, `claude-bootstrap init` creates 4 files, `doctor` returns 12/12 pass
- `gh repo edit --visibility public` (irreversible)
- Tag `v0.3.0a0` push triggers `release.yml` → PyPI + GitHub Release

### Changed

- Version bump: `0.2.0-alpha` → `0.3.0a0` (PEP 440 alpha format for PyPI)

### Known limitations

- 3-way merge in `update` is 2-way diff (`.new` files); 3-way needs original-render storage (planned v0.4)
- `data-science`, `frontend`, `devops` profiles still placeholders (curated content depends on demand)
- `mcp__ide__executeCode` and similar Anthropic-side features documented but not auto-installed (intentional — user opts in via skill add)

---

## [0.2.0-alpha] — 2026-05-07

### Added — v0.2 features

- `bin/install.py` — `merge_settings_overrides()` deep-merge real:
  - dicts: recurse; lists: concat + dedupe (base first, profile after); scalars: profile wins
  - `profile.yaml settings_overrides` agora ALTERA `target/.claude/settings.json` (antes era estrutura morta)
  - exemplo: o profile acadêmico adiciona `Bash(pandoc *)`, `Bash(qpdf *)` em `permissions.allow` e `CITATION_STYLE`/`RUBRICA_VERSION` em `env`
- `bin/install.py` — flag `--update`:
  - se arquivo existe e divergiu do template render: escreve `<path>.new`, retorna `diverged (.new)` (preserva user edits)
  - se inalterado: `unchanged`; com `--force` sobrescreve
- `bin/bootstrap.sh update` — implementação real (era stub `[Phase 5]`):
  - flags: `--profile`, `--non-interactive`, `--force`, `--check`
  - re-roda interview → install com `--update`; arquivos divergentes viram `.new` para revisão manual
- `bin/skill.py update` — implementação real (era stub):
  - re-pull skills instaladas das sources atuais (force overwrite, equivale a `add --force` em todas)
  - `--name X`: só uma skill; sem flag: todas em `.claude/skills/`

### Tests — 18 → 24 (+6)

- `test_settings_overrides_merged_for_academic` — verifica merge real produz allow/env corretos
- `test_settings_overrides_noop_for_universal` — universal-software com `{}` não muta env
- `test_update_writes_new_for_diverged_file` — install → modify → update → `.new` escrito, original preservado
- `test_update_unchanged_when_no_drift` — install → update → tudo `unchanged`, zero `.new`
- `test_skill_update_no_skills_dir` — early exit quando target sem `.claude/skills/`
- `test_skill_update_reinstalls_local` — install → corrupt → update → re-installed limpo

### Fixed — CI primeiro run (3 commits revelaram)

- `.github/workflows/ci.yml`:
  - `Validate registry/skills.yaml` + `Validate profile.yaml files`: `uv run` sem `--no-project` quebra (pyproject sem `[project]`)
  - `bootstrap-smoke`: `--target` ignorado (flag inexistente) → `cd /tmp/cb-smoke` antes; assertions em `.agent/AGENTS.md` (errado, era padrão agentic-stack) → CLAUDE.md, MEMORY.md, .claude/settings.json, .gitignore; `grep "12 pass"` quebra em runner sem superpowers em `~/.claude/` → `grep "0 fail"`
- `tests/test_detect.py:test_repo_self_scan` — assertia `mode == "update"` mas `.claude/` é gitignored, em CI vira mode `init`. Fix: assert dinâmico baseado em existência real de `.claude/`.
- `bin/doctor.py:117,126` — variável `l` ambígua (E741); renomeado para `line`
- `bin/interview.py:163-167` — if/else simples → ternary (SIM108)
- 11 arquivos reformatados pelo `ruff-format` (linha 110, py311)

### Decisões resolvidas

- **D1**: visibilidade git → privado em https://github.com/ulissesflores/claude-bootstrap
- **D2**: bump `0.1.0-alpha` → `0.2.0-alpha` (este release)
- **D3**: CI primeiro run → verde após 3 fixes (lint, tests, smoke)

---

## [0.1.0-alpha] — 2026-05-05 (8/8 fases iniciais)

### Added — Phase 8 (hardening: tests + CI + pre-commit + registry update)

- `tests/` — pytest suite (289 lines, 18 tests, all passing in 1.6s):
  - `conftest.py` — fixtures (`repo_root`, `tmp_project`, `run_cli`)
  - `test_interview.py` (4 tests): `--help` without questionary, JSON output keys, profile flag, output to file
  - `test_detect.py` (3 tests): empty dir → null, repo self-scan → mode=init, --quiet output
  - `test_install.py` (4 tests): init creates artefacts, idempotent re-run, academic profile (19+ files), --check dry-run
  - `test_doctor.py` (3 tests): empty dir fails, bootstrapped project passes 12/12, --json output parseable
  - `test_skill.py` (4 tests): registry validate, list, add idempotent, show
  - `tests/README.md` — how to run + caveats
- `.github/workflows/ci.yml` (116 lines, 3 jobs):
  - `lint`: shellcheck `bin/bootstrap.sh`, Python syntax, validate JSON/YAML, all profile.yaml files
  - `test`: matrix 3.11+3.12, full pytest run via `uv run --with`
  - `bootstrap-smoke` (needs lint): init → assert artefacts → doctor → skill validate
- `.pre-commit-config.yaml` (41 lines) — 4 hook repos: pre-commit-hooks (whitespace/EOL/yaml/json/merge-conflict/large-files), shellcheck-py, ruff (lint+format), actionlint
- `pyproject.toml` (10 lines) — minimal ruff config (line-length 110, py311 target, E/F/W/I/UP/B/SIM rules)
- `scripts/update-registry.sh` (~185 lines) — cron-able registry validator: runs `skill validate`, HEAD-checks github URLs, verifies local SKILL.md paths, flags entries with `last_validated_at` >90d, stamps timestamps in non-`--check` mode

### Fixed

- `bin/skill.py` — `cmd_show` and `cmd_list --json` now use `default=str` in `json.dumps` to handle `last_validated_at` parsed as `datetime.date` by pyyaml (caught by tests).

### Added — Phase 7 (profile placeholders + missing docs)

**5 new docs (1122 lines total)**:
- `docs/03-anti-patterns.md` (140 lines) — 10 anti-patterns expanded from `02-state-of-the-art.md` §3 + 2 originais (hardcoded paths em skills, profile sem `based_on`)
- `docs/04-skills-curated.md` (342 lines) — registry schema, tier criteria, source types, 19 skills documented one-by-one, `bin/skill.py` command reference
- `docs/05-profiles.md` (214 lines) — schema profile.yaml, lifecycle detect→suggest→install (mermaid), heuristics table, install_profile_assets behavior, 5 profiles status table
- `docs/06-bootstrap-flow.md` (313 lines) — full flow of bootstrap.sh + 3 mermaid diagrams (init flow, doctor exit codes, skill add flow), 6 subcommands documented
- `docs/08-faq.md` (113 lines) — 20 Q&A covering positioning, usage, profiles, skills, memory, contributing

**3 profile placeholders (75 lines total)**:
- `templates/profiles/data-science/profile.yaml` — placeholder + TODO list (jupyter-runner, pandas-helper, ml-experiment-tracker)
- `templates/profiles/frontend/profile.yaml` — placeholder + TODO list (react-component-design, a11y-audit, bundle-analyzer)
- `templates/profiles/devops/profile.yaml` — placeholder + TODO list (terraform-plan-reviewer, k8s-yaml-validator, ci-pipeline-debugger)

5 Sonnet subagents (docs) + 3 Haiku subagents (profiles) ran in parallel — peak 8 concurrent.

Registry still validates (19 skills) after profile additions.

### Added — Phase 6 (validation against a real academic project via `/tmp` clone)

- A snapshot fixture with 3 captured outputs + README (`detect`, `doctor`, `init --check`),
  taken against a read-only clone of a real academic project. Source integrity **untouched**
  (verified via `diff` against the clone post-validation; `cp -R` preserved timestamps).

### Validation results (2026-05-05)

| Engine | Outcome | Confirms |
|---|---|---|
| `detect` | suggested the academic profile at confidence 0.95 | heuristic correctness |
| `doctor` | 1 FAIL + 4 WARN flag exact gaps | engine usefulness |
| `init --check` | 19/19 skills+rules `unchanged` | profile faithfulness (the Phase 4 audited copy is byte-perfect) |

### Added — Phase 5 (registry + `bin/skill.py` + superpowers integration)

- `registry/skills.yaml` v0 — 19 curated skills:
  - **Tier 1 universal (8)**: `brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review` — all sourced from `github.com/obra/superpowers`
  - **Tier 1 institution-local (5)**: 5 local academic-workflow skills sourced from the institution-specific profile audited in Phase 4 (all removed in the Unreleased section above)
  - **Tier 2 (5)**: `dispatching-parallel-agents`, `using-git-worktrees`, `subagent-driven-development`, `writing-skills`, `finishing-a-development-branch`
  - **Tier 3 (1)**: `graphify` (experimental)
- `bin/skill.py` (220 lines) — registry CLI with subcommands `list`, `show`, `add`, `remove`, `update` (placeholder), `validate`. Source types supported: `local` (copy from repo) and `github` (`git clone --depth 1` + extract subpath). Filters: `--profile`, `--tier`, `--target`, `--json`.
- `bin/bootstrap.sh` — `skill` subcommand wired (was placeholder).

Verified end-to-end:
- `skill validate` → 19 skills validated, no errors
- `skill list --profile <academic>` → 12 skills (8 universal-software intersect + 4 profile-only + graphify)
- `skill add <local-skill> --target /tmp/X` → status `installed` (4.1K SKILL.md copied)
- 2nd `skill add` against same target → `exists-skipped` (idempotency)
- `skill list --target /tmp/X --profile <academic>` → the added skill shows `installed`, others `available`

2 Explore agents (Haiku) cataloged superpowers + sources/ in parallel; Opus consolidated into 19 entries + wrote skill.py + verified.

### Added — Phase 4 (profiles `universal-software` + an institution-specific academic one)

- `templates/profiles/universal-software/profile.yaml` — default general-purpose profile (no bundled skills/rules; relies on superpowers as declared dependency)
- A second profile bundling 5 skills + 3 rules + settings overrides (pandoc/awk/soffice/qpdf permissions, citation-style env), as a read-only audited copy of a real academic workspace's `.claude/`. Institution-specific; **removed entirely in the Unreleased section above**.
- `bin/install.py` extended: `install_profile_assets()` reads `profile.yaml` and copies `skills/`+`rules/` into `target/.claude/` with idempotent semantics (lazy pyyaml import)
- `bin/bootstrap.sh` runner now requires `jinja2 + pyyaml` (auto-detect via `uv run --with jinja2 --with pyyaml`)

Verified end-to-end: `bootstrap.sh init` with that profile in a fresh tmpdir produced 23 files; `diff` against the audited sources for all 5 skills + 3 rules → zero differences (byte-perfect copy); 2nd run reported all `exists-skipped` (idempotency).

### Added — Phase 3 (bootstrap engine MVP)

- `bin/bootstrap.sh` — dispatcher with subcommands `init|detect|doctor|skill|update|help|version`. Auto-detects Python runner with jinja2 (native `python3` → fallback `uv run --with jinja2`).
- `bin/interview.py` (177 lines) — interactive wizard collecting 11 vars for the Jinja templates. `--non-interactive`, `--profile`, `--output` flags. `questionary` is lazy-imported.
- `bin/detect.py` (191 lines) — read-only project scanner with heuristics for `academic`, `data-science`, `frontend`, `devops`, `universal-software`. JSON output, `--quiet`, `--output` flags.
- `bin/install.py` (160 lines) — render Jinja templates + install with idempotent semantics: create-only for CLAUDE.md/MEMORY.md/settings.json (preserves user edits on re-run), soft-merge for `.gitignore` (appends only missing lines).
- `bin/doctor.py` (319 lines) — health check with 12 checks (CLAUDE.md presence/size, .claude/ structure, settings.json validity + schema + secret-deny rules, .gitignore coverage, MEMORY.md, superpowers, profile metadata). Rich table or JSON output, `--quiet`/`--strict`/`--json` flags.

End-to-end verified: `bootstrap.sh init --profile=universal-software --non-interactive` in fresh tmpdir creates 4 artefacts; second run reports `exists-skipped` + `unchanged` (idempotency); `doctor` against the bootstrapped project: 12 pass · 0 warn · 0 fail · 0 skip.

### Added — Phase 2 (templates Jinja `_base/`)

- `templates/_base/CLAUDE.md.j2` — universal CLAUDE.md template (Jinja2) com placeholders para `project_name`, `project_description`, `primary_language`, `is_monorepo`, `git_remote`, `profile_name`, `superpowers_available`, `agentic_stack_interop`, `extra_rules`, `generated_at`
- `templates/_base/MEMORY.md.j2` — base curated-memory template (4 seções: project state, active goals, recent decisions, known gotchas)
- `templates/_base/.claude/settings.json` — base safe permissions (22 allow read-only/git, 16 deny destrutivo/secrets)
- `templates/_base/.gitignore` — base gitignore para projetos bootstrapped (Python, Node, Rust, Go, secrets, OS, editors)

Render verificado via `uv run --with jinja2`: cenários completo (10 vars) e mínimo (sem opcionais) ambos limpos, sem seções vazias.

## [0.1.0-alpha] - 2026-05-05

Primeira versão do esqueleto. **Fase 1/8** concluída: repositório navegável com docs canônicos prontos. Bootstrap engine ainda não existe.

### Added

- Esqueleto do repo: `README.md`, `AGENTS.md`, `CLAUDE.md`, `llms.txt`, `LICENSE` (MIT), `.gitignore`, `CHANGELOG.md`
- `docs/00-overview.md` — visão geral do projeto, arquitetura em 3 camadas, fluxo do bootstrap, fases
- `docs/01-canonical-anthropic.md` — padrão oficial Anthropic Claude Code (memória, skills, agents, hooks, MCP, plugins, settings hierarchy) validado mai/2026
- `docs/02-state-of-the-art.md` — estado da arte (jan/2025–mai/2026) com 25 fontes validadas
- `docs/07-glossary.md` — termos canônicos do domínio Claude Code
- Material de kickoff preservado localmente: a pesquisa fonte que originou o projeto (decisões travadas, plano executivo, mapa das 4 zonas do operador, padrão Anthropic, estado da arte)
