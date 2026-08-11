#!/usr/bin/env python3
"""audit.py — machine-readable provenance + integrity report for an emitted `.claude/`.

A regulated/EEAT user attaches this to a compliance dossier: exactly what was emitted,
where each skill came from (upstream repo@SHA), and its integrity hash reconciled against
the install manifest. Offline — makes NO network call; the report is a *claim* a third
party can independently re-verify with `scripts/verify-skill-provenance.py`.

Provenance is read from the bundled profile `NOTICE.md` (owner/repo/path/url) and the
pin SHAs in `scripts/skill-pins.json`. If the pins file cannot be resolved (e.g. a
pip-installed layout where `scripts/` is not adjacent), the SHA is reported as `null`
and the skill is `unpinned` — an audit must say "unknown", never a stale-but-confident SHA.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "claude-bootstrap.audit/v1"
MANIFEST_REL = ".claude/.bootstrap-manifest.json"
PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
# Resolve pins from the canonical dev-checkout location first, then the package-data copy
# that ships in the wheel (so a pip-installed `audit` still attests pinned_sha, not null).
_PINS_CANDIDATES = (
    PACKAGE_DIR.parent / "scripts" / "skill-pins.json",
    PACKAGE_DIR / "skill-pins.json",
)

# NOTICE.md row → (skill, github tree url); tree url → (owner, repo, path).
_ROW = re.compile(r"^\|\s*`([^`]+)`.*?(https://github\.com/\S+?)\s*\|")
_TREE = re.compile(r"github\.com/([^/]+)/([^/]+)/tree/main/(.+)$")
# Kept in lockstep with `scripts/verify-skill-provenance.py::ROW_FIRST_PARTY`.
_ROW_FIRST_PARTY = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*—\s*\(first-party\)\s*\|")
_SKILL_PATH = re.compile(r"^\.claude/skills/([^/]+)/SKILL\.md$")
_RULE_PATH = re.compile(r"^\.claude/rules/(.+)$")
_SECRET_RE = re.compile(r"(?i)\.env|secret|credential|key|pem")
# content namespaces claude-bootstrap owns — walked in reverse to catch injected files
_OWNED_DIRS = ("skills", "rules", "agents", "output-styles")


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_pins() -> dict[str, str]:
    """Pin SHAs keyed by owner, or {} if unresolvable (honest-unknown, never stale)."""
    for cand in _PINS_CANDIDATES:
        if cand.is_file():
            try:
                return json.loads(cand.read_text())
            except json.JSONDecodeError:
                continue
    return {}


def _provenance_map(profile: str) -> dict[str, dict]:
    """skill name → {owner, repo, path, url, first_party} from the bundled profile NOTICE.md.

    A first-party skill gets an entry with `first_party: True` and no owner. Returning nothing
    for it would be wrong: its provenance is not *missing*, it is this repo — and `build_report`
    treats an absent entry as unprovenanced, which would sink the verdict to INCOMPLETE.
    """
    out: dict[str, dict] = {}
    notice = TEMPLATES_DIR / "profiles" / profile / "NOTICE.md"
    if not notice.is_file():
        return out
    for line in notice.read_text().splitlines():
        fp = _ROW_FIRST_PARTY.match(line)
        if fp:
            out[fp.group(1)] = {
                "owner": None,
                "repo": None,
                "path": None,
                "url": None,
                "first_party": True,
            }
            continue
        m = _ROW.match(line)
        if not m:
            continue
        tm = _TREE.search(m.group(2))
        if not tm:
            continue
        owner, repo, path = tm.groups()
        out[m.group(1)] = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "url": f"https://github.com/{owner}/{repo}/tree/main/{path}",
            "first_party": False,
        }
    return out


def build_report(target: Path) -> dict:
    target = target.resolve()
    manifest_path = target / MANIFEST_REL
    manifest_present = manifest_path.is_file()
    manifest = {}
    if manifest_present:
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError:
            manifest_present = False

    # D13: read the multi-profile set (profiles-wins), back-compat with the scalar `profile`, and
    # fall back to universal-software when a manifest records neither.
    profiles = manifest.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        scalar = manifest.get("profile")
        profiles = [scalar] if scalar else ["universal-software"]
    profile = profiles[0]  # scalar kept for back-compat report readers
    version = manifest.get("version") or "unknown"
    manifest_files = {f["path"]: f["sha256"] for f in manifest.get("files", [])}

    # Union the NOTICE maps across every active profile so a union emit resolves provenance for
    # EVERY bundled skill (not just profiles[0]'s). Surface a same-name/different-owner disagreement
    # rather than silently last-wins.
    prov: dict[str, dict] = {}
    provenance_conflicts: list[dict] = []
    for _p in profiles:
        for _name, _meta in _provenance_map(_p).items():
            _existing = prov.get(_name)
            if _existing and _existing["owner"] != _meta["owner"]:
                provenance_conflicts.append(
                    {"skill": _name, "owners": sorted({_existing["owner"], _meta["owner"]})}
                )
            prov[_name] = _meta
    pins = _load_pins()

    skills: list[dict] = []
    rules: list[dict] = []
    files_audited = 0
    files_matching = 0
    files_missing_provenance = 0

    for rel, recorded_sha in sorted(manifest_files.items()):
        cur_sha = _sha256(target / rel)
        match = cur_sha == recorded_sha
        files_audited += 1
        if match:
            files_matching += 1

        skill_m = _SKILL_PATH.match(rel)
        rule_m = _RULE_PATH.match(rel)
        if skill_m:
            name = skill_m.group(1)
            p = prov.get(name)
            first_party = bool(p) and p.get("first_party")
            pinned = bool(p) and not first_party and p["owner"] in pins
            if first_party:
                # No pin exists because there is no upstream commit to pin to. Resolved, not missing.
                source = {"owner": None, "repo": None, "pinned_sha": None, "url": None}
                provenance = "first-party"
            elif p:
                source = {
                    "owner": p["owner"],
                    "repo": p["repo"],
                    "pinned_sha": pins.get(p["owner"]),  # null when unresolvable
                    "url": p["url"],
                }
                provenance = "pinned" if pinned else "unpinned"
            else:
                source = None
                provenance = "unpinned"
            if not pinned and not first_party:
                files_missing_provenance += 1
            skills.append(
                {
                    "name": name,
                    "path": rel,
                    "sha256": cur_sha,
                    "source": source,
                    "manifest_match": match,
                    "provenance": provenance,
                }
            )
        elif rule_m:
            rules.append({"name": rule_m.group(1), "path": rel, "sha256": cur_sha, "manifest_match": match})

    # Reverse reconciliation: the manifest→disk loop alone is blind to files ADDED after
    # install. Walk claude-bootstrap's owned content namespaces for any on-disk path the
    # manifest never recorded → untracked (else an injected skill/rule/agent passes clean).
    untracked: list[str] = []
    if manifest_present:
        for owned in _OWNED_DIRS:
            base = target / ".claude" / owned
            if not base.is_dir():
                continue
            for f in sorted(base.rglob("*")):
                if not f.is_file() or "__pycache__" in f.parts or f.suffix in (".pyc", ".pyo"):
                    continue
                rel = str(f.relative_to(target))
                if rel not in manifest_files:
                    untracked.append(rel)

    settings = _load_settings(target)
    deny = settings.get("permissions", {}).get("deny", []) or []
    allow = settings.get("permissions", {}).get("allow", []) or []
    secret_deny = any(isinstance(r, str) and _SECRET_RE.search(r) for r in deny)

    if not manifest_present or files_audited == 0:
        # nothing to attest (manifest absent, or present-but-empty → not a clean tree)
        verdict = "INCOMPLETE"
    elif files_audited != files_matching or untracked:
        # a tracked file was edited, or an untracked file was injected into an owned dir
        verdict = "MODIFIED"
    elif files_missing_provenance:
        verdict = "INCOMPLETE"
    else:
        verdict = "PASS"

    return {
        "schema": SCHEMA,
        "generated_for": str(target),
        "bootstrap_version": version,
        "profile": profile,
        "profiles": profiles,
        "provenance_conflicts": provenance_conflicts,
        "skills": skills,
        "rules": rules,
        "permissions": {
            "allow_count": len(allow),
            "deny_count": len(deny),
            "secret_deny_present": secret_deny,
            "deny": deny,
        },
        "integrity": {
            "manifest_present": manifest_present,
            "files_audited": files_audited,
            "files_matching_manifest": files_matching,
            "files_missing_provenance": files_missing_provenance,
            "files_untracked": len(untracked),
            "untracked": untracked,
            "verdict": verdict,
        },
    }


def _load_settings(target: Path) -> dict:
    path = target / ".claude" / "settings.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def print_json(report: dict) -> None:
    print(json.dumps(report, indent=2))


def print_plain(report: dict) -> None:
    integ = report["integrity"]
    pins = sum(1 for s in report["skills"] if s["provenance"] == "pinned")
    print(f"# claude-bootstrap audit — {report['generated_for']}")
    print()
    print("| Item | Detail |")
    print("|---|---|")
    print(f"| profile | {report['profile']} |")
    print(f"| bootstrap version | {report['bootstrap_version']} |")
    print(f"| skills | {len(report['skills'])} ({pins} pinned) |")
    print(f"| rules | {len(report['rules'])} |")
    print(f"| files vs manifest | {integ['files_matching_manifest']}/{integ['files_audited']} match |")
    print(f"| untracked in owned dirs | {integ['files_untracked']} |")
    print(
        f"| secret-deny rules | {'present' if report['permissions']['secret_deny_present'] else 'ABSENT'} |"
    )
    print(f"| manifest present | {integ['manifest_present']} |")
    print()
    print(f"verdict: {integ['verdict']}")


def exit_code(report: dict, strict: bool) -> int:
    return 1 if strict and report["integrity"]["verdict"] != "PASS" else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="claude-bootstrap audit",
        description="Provenance + integrity report for an emitted .claude/ (offline).",
    )
    parser.add_argument("path", nargs="?", default=".", help="Project root to audit (default: cwd)")
    parser.add_argument("--json", action="store_true", dest="json_out", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if the verdict is not PASS")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.is_dir():
        print(f"ERROR: {target} is not a directory", file=sys.stderr)
        return 2

    report = build_report(target)
    if args.json_out:
        print_json(report)
    else:
        print_plain(report)
    return exit_code(report, args.strict)


if __name__ == "__main__":
    sys.exit(main())
