"""Third-party redistribution gate: do we hold the right, and do we meet its conditions?

Publication audit 2026-07-24 found a P0 blocker that five model audits had missed: the wheel
shipped 55 files nobody was licensed to redistribute. Nothing was looking for it, because the
question was never encoded as a check. It is now — as two separate assertions, because *holding*
a right and *satisfying its conditions* fail independently:

  test_every_bundled_skill_carries_a_license   -- rights: no skill ships without a license
  test_no_de_bundled_skill_reappears           -- rights: the known-bad set stays out
  test_license_text_travels_with_the_skill     -- conditions: MIT/Apache notice reaches the user

The third one exists because `install.py` copies `skills/<name>/**` only, so a profile-level
NOTICE.md never reaches the user's tree. A license named in NOTICE.md but absent from the skill
directory satisfies nobody.

The reappearance guard is not hypothetical: `verify-skill-provenance.py --sync` builds its work
list from each profile's NOTICE.md (not the filesystem) and `copytree` does not exclude `.txt`,
so a stale NOTICE row silently re-vendors a de-bundled skill, LICENSE.txt included.
"""

from __future__ import annotations

import importlib.util
import json
import re
import tempfile
from pathlib import Path

from conftest import run_python

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES = REPO_ROOT / "claude_bootstrap" / "templates" / "profiles"
SCRIPT = REPO_ROOT / "scripts" / "verify-skill-provenance.py"


def _rows():
    """The REAL `--sync` work list, not a reimplementation of its parser.

    Testing a copy of the regex would pass while the actual parser disagreed. Import the one
    that ships.
    """
    spec = importlib.util.spec_from_file_location("verify_skill_provenance", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.rows()


# De-bundled 2026-07-26 — no license permits redistribution. `docx`/`pdf`/`pptx` carry an explicit
# Anthropic no-distribution clause; `doc-coauthoring` carries no license at all (absence is default
# copyright, not a permissive default). `xlsx` was de-bundled 2026-06-06 and is the same class.
DE_BUNDLED = {"docx", "pdf", "pptx", "doc-coauthoring", "xlsx"}

LICENSE_NAMES = ("LICENSE.txt", "LICENSE", "LICENSE.md")

# A license file must contain a real grant, not just a copyright line. These are the operative
# grant clauses of the licenses we accept; matching one proves the text is the license, not a stub.
#
# Apache-2.0 must match on "Grant of Copyright License" (§2 of the body) — NOT on "Licensed under
# the Apache License", which appears only in the optional APPENDIX. `frontend-design`'s upstream
# copy is 177 lines and omits that appendix, so an appendix-anchored pattern false-fails it.
GRANT = re.compile(
    r"Permission is hereby granted"  # MIT / ISC
    r"|Grant of Copyright License"  # Apache-2.0 §2
    r"|Redistribution and use in source and binary forms",  # BSD
    re.IGNORECASE,
)


def _bundled_skill_dirs() -> list[Path]:
    return sorted(p for p in PROFILES.glob("*/skills/*") if p.is_dir())


def test_bundled_skills_are_discoverable():
    """Guard the guard: if the glob silently matches nothing, every test below false-passes."""
    dirs = _bundled_skill_dirs()
    assert len(dirs) >= 20, f"expected the full bundle, found {len(dirs)}: {dirs}"


def test_no_de_bundled_skill_reappears():
    """A `--sync` driven by a stale NOTICE.md row would resurrect the blocker silently."""
    found = {p.name for p in _bundled_skill_dirs()} & DE_BUNDLED
    assert not found, (
        f"de-bundled skill(s) back in the tree: {sorted(found)}. "
        "Removing the directory is not enough — drop the NOTICE.md row and the profile.yaml "
        "entry too, or the next `--sync` re-vendors it."
    )
    # Disk state is not the real input: `--sync` rebuilds the tree from the NOTICE.md rows. Ask
    # the shipping parser what it would fetch, so a documentation table mentioning a de-bundled
    # skill stays harmless while an actual bundled-skill row does not.
    listed = {skill for _profile, skill, _o, _r, _p in _rows()}
    resurrect = listed & DE_BUNDLED
    assert not resurrect, (
        f"NOTICE.md still lists {sorted(resurrect)} as bundled — `--sync` will re-vendor it, "
        "LICENSE.txt included, and the blocker returns silently."
    )


def test_notice_rows_match_what_is_on_disk():
    """`--sync` reads NOTICE.md; `init` reads profile.yaml; the tree is what ships.

    All three must agree, or a skill is advertised but missing (or fetched but unadvertised).
    """
    listed = {(profile, skill) for profile, skill, _o, _r, _p in _rows()}
    on_disk = {(p.parent.parent.name, p.name) for p in _bundled_skill_dirs()}
    assert listed == on_disk, (
        f"NOTICE.md rows and skills/ directories disagree — "
        f"listed-but-absent: {sorted(listed - on_disk)}; present-but-unlisted: {sorted(on_disk - listed)}"
    )


def test_every_bundled_skill_carries_a_license():
    """Rights. Absence of a license is default copyright, not a permissive default."""
    missing = [
        f"{p.parent.parent.name}/{p.name}"
        for p in _bundled_skill_dirs()
        if not any((p / n).is_file() for n in LICENSE_NAMES)
    ]
    assert not missing, (
        f"bundled skill(s) with no license file: {missing}. "
        "Read the upstream source (root license, per-skill override, SKILL.md frontmatter) "
        "before bundling — do not infer a license from the skill looking like community work."
    )


def test_advertised_skill_counts_match_disk():
    """Every surface that advertises a skill count must agree with what actually ships.

    Not hypothetical: `.github/workflows/demo.yml:8` records that this repo advertised `xlsx`
    for seven weeks after removing it, and the 2026-07-26 de-bundle left six more surfaces stale
    (four translated READMEs, AGENTS.md, and the academic plugin manifest) that the initial sweep
    missed. A de-bundle is only half done when the tree is right and the shop window is not.
    """
    per_profile = {}
    for p in _bundled_skill_dirs():
        per_profile[p.parent.parent.name] = per_profile.get(p.parent.parent.name, 0) + 1
    total = sum(per_profile.values())

    wrong = []

    # Badge on every README variant (translations rot first — they are updated by hand).
    for readme in sorted(REPO_ROOT.glob("README*.md")):
        for found in re.findall(r"skills-(\d+)%20provenance", readme.read_text()):
            if int(found) != total:
                wrong.append(f"{readme.name} badge says {found}, disk has {total}")

    agents = REPO_ROOT / "AGENTS.md"
    if agents.is_file():
        for found in re.findall(r"Total embarcado: \*\*(\d+) skills\*\*", agents.read_text()):
            if int(found) != total:
                wrong.append(f"AGENTS.md total says {found}, disk has {total}")

    # Per-profile: marketplace entry + the profile's own plugin manifest.
    marketplace = (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text()
    for profile, count in sorted(per_profile.items()):
        manifest = PROFILES / profile / ".claude-plugin" / "plugin.json"
        if manifest.is_file():
            for found in re.findall(r"(\d+) skills", manifest.read_text()):
                if int(found) != count:
                    wrong.append(f"{profile}/plugin.json says {found}, disk has {count}")
        # The marketplace description names the profile, so scope the match to its own entry.
        for entry in re.findall(rf'"{profile}".*?\}}', marketplace, re.DOTALL):
            for found in re.findall(r"\((\d+) skills", entry):
                if int(found) != count:
                    wrong.append(f"marketplace[{profile}] says {found}, disk has {count}")

    assert not wrong, "advertised counts disagree with the shipped tree:\n  " + "\n  ".join(wrong)


def test_license_reaches_the_users_tree_on_emit():
    """The condition, checked where it actually binds: the user's project, not this repo.

    Every other test here inspects `templates/`. That leaves the load-bearing step — `install.py`
    copying `skills/<name>/**` into the target — asserted nowhere, so a packaging change that
    dropped `LICENSE.txt` from the copy would ship an unlicensed skill with the suite green.

    Scoped to `universal-software` because it is the default profile (most users arrive by
    detection, never naming one) and the only profile whose skills are first-party, where the
    licence obligation is this project's own.
    """
    with tempfile.TemporaryDirectory() as target:
        vars_json = json.dumps(
            {
                "project_name": "license-emit-check",
                "project_description": "does the grant reach the user",
                "primary_language": "mixed",
                "is_monorepo": False,
                "git_remote": None,
                "profile_name": "universal-software",
                "superpowers_available": False,
                "agentic_stack_interop": False,
                "extra_rules": [],
                "generated_at": "2026-07-28",
                "bootstrap_version": "0.4.0a0",
            }
        )
        rc, out, err = run_python("install.py", ["--vars-json", vars_json, "--target", target])
        assert rc == 0, out + err

        emitted = Path(target) / ".claude" / "skills"
        expected = {p.name for p in _bundled_skill_dirs() if p.parent.parent.name == "universal-software"}
        assert {p.name for p in emitted.iterdir() if p.is_dir()} == expected

        naked = [
            d.name
            for d in sorted(emitted.iterdir())
            if d.is_dir()
            and not GRANT.search(
                next(
                    (
                        (d / n).read_text(encoding="utf-8", errors="replace")
                        for n in LICENSE_NAMES
                        if (d / n).is_file()
                    ),
                    "",
                )
            )
        ]
        assert not naked, (
            f"emitted without a grant clause in the user's tree: {naked}. "
            "The license must be inside skills/<name>/ — install.py copies nothing else."
        )


def test_license_text_travels_with_the_skill():
    """Conditions. MIT and Apache-2.0 both require the notice to accompany every copy.

    `install.py` copies `skills/<name>/**`, so the license must live inside the skill directory;
    a profile-level NOTICE.md is attribution for readers of this repo, not for the user's tree.
    """
    stubs = []
    for p in _bundled_skill_dirs():
        lic = next((p / n for n in LICENSE_NAMES if (p / n).is_file()), None)
        assert lic is not None, f"{p.name}: no license (covered by the rights test)"
        if not GRANT.search(lic.read_text(encoding="utf-8", errors="replace")):
            stubs.append(f"{p.parent.parent.name}/{p.name}/{lic.name}")
    assert not stubs, (
        f"license file present but carries no grant clause: {stubs}. "
        "A copyright line or a URL is not the permission notice."
    )
