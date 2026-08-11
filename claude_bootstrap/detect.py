#!/usr/bin/env python3
"""detect.py — read-only project scanner for claude-bootstrap."""

import argparse
import contextlib
import datetime
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

DATA_SCIENCE_KEYWORDS = {"pandas", "torch", "tensorflow", "scikit-learn", "jupyter", "numpy"}

# Multi-stack detection (detect_stack / infer_profiles). The DS split decides backend↔data-science:
# STRONG = unambiguous deep-learning → the project's PURPOSE is ML (keeps data-science even with a
# web framework). WEAK = routinely pulled into ordinary backends → a framework wins over them.
# (STRONG_DS | WEAK_DS == DATA_SCIENCE_KEYWORDS, preserving infer_profile's single-profile behavior.)
STRONG_DS = {"torch", "tensorflow"}
WEAK_DS = {"scikit-learn", "jupyter", "numpy", "pandas"}

# Web-framework markers — a dir is `backend` (config-only service profile) when one is present.
PY_WEB_FRAMEWORKS = {"fastapi", "flask", "django", "starlette", "sanic", "falcon", "tornado"}
NODE_BACKEND_FRAMEWORKS = {"express", "nestjs", "fastify", "koa", "hapi", "adonisjs"}
RUBY_BACKEND = {"rails", "sinatra", "hanami", "roda"}
JAVA_BACKEND = {"spring", "springframework", "quarkus", "micronaut", "javalin"}
GO_BACKEND = {"gin", "echo", "fiber", "chi", "gorilla", "fasthttp", "buffalo"}

_PY_DEP_FILES = ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile")

# Sub-project discovery: dirs never descended into / never counted (carry foreign markers → phantom
# stacks). Broadened per validator (template/boilerplate/skeleton/archive/_deprecated). Hidden
# dot-dirs are pruned generally.
_PRUNE_DIRS = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "vendor",
    "dist",
    "build",
    "examples",
    "example",
    "samples",
    "fixtures",
    "__fixtures__",
    "test",
    "tests",
    "e2e",
    "docs",
    ".next",
    "target",
    ".tox",
    "template",
    "templates",
    "boilerplate",
    "skeleton",
    "archive",
    "_deprecated",
    "__pycache__",
    ".github",
}
_WS_CONTAINERS = {"apps", "packages", "services", "libs"}


def file_contains_any(path: Path, keywords: set) -> bool:
    """True if any keyword appears as a word in path, **ignoring comment text**.

    Strips each line's `#` comment tail and matches on word boundaries so a mention
    like `# we are not pandas` (a ruff-rule note) doesn't count as a pandas dep
    (fire-test Bug 7).
    """
    try:
        raw = path.read_text(errors="ignore")
    except OSError:
        return False
    code = "\n".join(line.split("#", 1)[0] for line in raw.splitlines()).lower()
    return any(re.search(rf"\b{re.escape(kw)}\b", code) for kw in keywords)


def has_dir_pattern(root: Path, pattern: str) -> bool:
    """Check if any immediate child directory matches a regex pattern."""
    rx = re.compile(pattern)
    try:
        return any(rx.fullmatch(p.name) for p in root.iterdir() if p.is_dir())
    except OSError:
        return False


def has_file_recursive(root: Path, glob: str, *, limit: int = 20000) -> bool:
    """True if a file matching `glob` exists anywhere under `root`.

    Bounded `os.walk` (prunes VCS/dependency dirs, caps total entries, never follows
    symlinks) so it short-circuits at the first hit on IaC repos yet can't blow up on a
    huge negative tree. Used for terraform `*.tf` / Helm `Chart.yaml` detection where the
    files live many levels deep under non-standard dir names (fire-test batch 3).
    """
    skip = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".tox"}
    seen = 0
    for _dirpath, dirnames, filenames in os.walk(root):  # followlinks=False by default
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            if fnmatch.fnmatch(name, glob):
                return True
            seen += 1
            if seen > limit:
                return False
    return False


def _is_software_project(root: Path, has_code_project: bool) -> bool:
    """Wider "this root belongs to a software/infra repo" predicate than `has_code_project`.

    Guards the `.csl` academic signal only. A citation style is a pandoc/Quarto/R-Markdown
    doc-pipeline artifact that routinely sits at the root of a repo in ANY ecosystem, so the
    narrow Python/Node/Rust list let a Go/Java/Ruby/PHP/.NET or IaC repo reclassify to
    `academic` at 0.95 — and `infer_profiles` short-circuits on academic, so it also skipped
    the per-subdir monorepo scan. `.bib` deliberately keeps the narrow list: `go.mod` +
    `paper.bib` is the standard JOSS submission shape and must stay academic.

    Called only when a root `.csl` exists, so the bounded IaC walk stays off the hot path.
    """
    if has_code_project:
        return True
    if any(
        (root / f).exists()
        for f in ("go.mod", "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile", "composer.json")
    ):
        return True
    if list(root.glob("*.csproj")):
        return True
    return _devops_signal(root, deep=True)


def infer_profile(root: Path):
    """Return (profile_suggestion, confidence, signal_notes)."""
    signals = []

    # Code-project signals — keep a stray .bib from hijacking detection (fire-test Bug 4).
    has_code_project = any(
        (root / f).exists()
        for f in ("pyproject.toml", "setup.py", "requirements.txt", "package.json", "Cargo.toml")
    )

    # 1. Academic — LaTeX (`.tex`) is the strong signal; a bare `.bib`/`.csl` only counts
    #    when there's no code project (a `paper.bib` is common in scientific Python libs,
    #    and doc pipelines vendor a `.csl` citation style next to real source).
    tex_files = list(root.glob("*.tex"))
    bib_files = list(root.glob("*.bib"))
    csl_files = list(root.glob("*.csl"))
    if (
        tex_files
        or (bib_files and not has_code_project)
        or (csl_files and not _is_software_project(root, has_code_project))
    ):
        if tex_files:
            signals.append(f"{len(tex_files)} .tex file(s) found")
        if bib_files:
            signals.append(f"{len(bib_files)} .bib file(s) found")
        if csl_files:
            signals.append(f"{len(csl_files)} .csl file(s) found (citation style)")
        return "academic", 0.95, signals

    # 2. Rust (Cargo.toml)
    if (root / "Cargo.toml").exists():
        signals.append("Cargo.toml found (rust project — using universal-software fallback)")
        return "universal-software", 0.6, signals

    # 3. Python
    py_files = [root / f for f in ("pyproject.toml", "requirements.txt", "setup.py")]
    found_py = [f for f in py_files if f.exists()]
    if found_py:
        for f in found_py:
            signals.append(f"{f.name} found")
        ds_hit = any(file_contains_any(f, DATA_SCIENCE_KEYWORDS) for f in found_py)
        if ds_hit:
            matched = next(kw for f in found_py for kw in DATA_SCIENCE_KEYWORDS if file_contains_any(f, {kw}))
            signals.append(f"{matched} in deps")
            return "data-science", 0.85, signals
        return "universal-software", 0.7, signals

    # 4. Frontend (package.json + tsconfig.json)
    has_pkg = (root / "package.json").exists()
    has_ts = (root / "tsconfig.json").exists()
    if has_pkg and has_ts:
        signals.append("package.json found")
        signals.append("tsconfig.json found")
        return "frontend", 0.85, signals

    # 5. Node-only (package.json, no tsconfig)
    if has_pkg:
        signals.append("package.json found (could be node-backend; ask user)")
        return "universal-software", 0.7, signals

    # 6. DevOps — Infrastructure-as-Code. Two ways in:
    #    (a) strong IaC files anywhere (terraform `*.tf` / Helm `Chart.yaml`) — the canonical
    #        case; these live deep under non-standard dirs and often ship no Dockerfile
    #        (fire-test batch 3: hashicorp/terraform-guides, helm/charts).
    #    (b) containerization + a manifest dir, where the Dockerfile may be in a subdir and
    #        the dir is named variously, e.g. `k8s-specifications/` (fire-test Bug 5).
    has_tf = has_file_recursive(root, "*.tf")
    has_helm = has_file_recursive(root, "Chart.yaml")
    has_docker = (root / "Dockerfile").exists() or bool(list(root.glob("*/Dockerfile")))
    iac_dir = has_dir_pattern(
        root, r"(terraform|ansible|kubernetes|k8s.*|helm|charts|manifests|deploy(ment)?s?)"
    )
    if has_tf or has_helm or (has_docker and iac_dir):
        if has_tf:
            signals.append("terraform (*.tf) files found")
        if has_helm:
            signals.append("Helm Chart.yaml found")
        if has_docker and iac_dir:
            signals.append("Dockerfile + IaC/manifests directory found")
        return "devops", 0.8, signals

    return None, 0.0, signals


def _devops_signal(d: Path, *, deep: bool) -> bool:
    """IaC signal for one dir. `deep` does a bounded-recursive `*.tf`/`Chart.yaml` walk (the
    root back-compat backstop); otherwise it is dir-local (+ one-level `*/` glob)."""
    if deep:
        if has_file_recursive(d, "*.tf") or has_file_recursive(d, "Chart.yaml"):
            return True
    elif list(d.glob("*.tf")) or (d / "Chart.yaml").exists() or list(d.glob("*/Chart.yaml")):
        return True
    has_docker = (d / "Dockerfile").exists() or bool(list(d.glob("*/Dockerfile")))
    iac_dir = has_dir_pattern(
        d, r"(terraform|ansible|kubernetes|k8s.*|helm|charts|manifests|deploy(ment)?s?)"
    )
    return has_docker and iac_dir


def detect_stack(d: Path, *, deep_iac: bool = False) -> str | None:
    """Pure per-directory stack detector → one of frontend/data-science/backend/devops or None.

    Language detection is dir-local; the devops/IaC check recurses only when `deep_iac=True`
    (the root-level back-compat backstop) so per-subdir calls stay cheap and non-overlapping.
    Returns exactly ONE profile per dir — a language stack wins over devops within the same dir —
    so each discovered dir maps deterministically to one body (per-subdir invariant). Never returns
    a fallback (`universal-software`): a bare manifest with no positive marker yields None.
    """
    py = [d / f for f in _PY_DEP_FILES if (d / f).exists()]
    if py:
        if any(file_contains_any(f, STRONG_DS) for f in py):
            return "data-science"
        if (d / "manage.py").exists() or any(file_contains_any(f, PY_WEB_FRAMEWORKS) for f in py):
            return "backend"
        if any(file_contains_any(f, WEAK_DS) for f in py):
            return "data-science"
        # bare python → fall through to the devops backstop
    elif (d / "package.json").exists():
        if file_contains_any(d / "package.json", NODE_BACKEND_FRAMEWORKS):
            return "backend"
        if (d / "tsconfig.json").exists():
            return "frontend"
        # bare node → fall through
    elif (d / "Gemfile").exists():
        if (d / "config.ru").exists() or file_contains_any(d / "Gemfile", RUBY_BACKEND):
            return "backend"
    elif any((d / f).exists() for f in ("pom.xml", "build.gradle", "build.gradle.kts")):
        jf = next(d / f for f in ("pom.xml", "build.gradle", "build.gradle.kts") if (d / f).exists())
        if file_contains_any(jf, JAVA_BACKEND):
            return "backend"
    elif (d / "go.mod").exists():
        if file_contains_any(d / "go.mod", GO_BACKEND):
            return "backend"

    if _devops_signal(d, deep=deep_iac):
        return "devops"
    return None


def _child_dirs(d: Path) -> list[Path]:
    try:
        return sorted(
            (
                p
                for p in d.iterdir()
                if p.is_dir() and not p.name.startswith(".") and p.name not in _PRUNE_DIRS
            ),
            key=lambda p: p.name,
        )
    except OSError:
        return []


def _workspace_glob_dirs(root: Path) -> list[Path]:
    """Dirs from a workspace declaration (`package.json` workspaces / `pnpm-workspace.yaml`),
    so discovery is layout-accurate instead of guessing."""
    globs: list[str] = []
    pkg = root / "package.json"
    if pkg.exists():
        with contextlib.suppress(json.JSONDecodeError, OSError):
            data = json.loads(pkg.read_text(errors="ignore"))
            ws = data.get("workspaces")
            if isinstance(ws, dict):
                ws = ws.get("packages")
            if isinstance(ws, list):
                globs += [g for g in ws if isinstance(g, str)]
    pnpm = root / "pnpm-workspace.yaml"
    if pnpm.exists():
        with contextlib.suppress(OSError):
            for line in pnpm.read_text(errors="ignore").splitlines():
                m = re.match(r"\s*-\s*['\"]?([^'\"]+?)['\"]?\s*$", line)
                if m:
                    globs.append(m.group(1))
    out: list[Path] = []
    for g in globs:
        g = g.strip().rstrip("/")
        if not g or g.startswith("!"):
            continue
        with contextlib.suppress(ValueError, OSError):
            out += [p for p in root.glob(g) if p.is_dir() and p.name not in _PRUNE_DIRS]
    return out


def _enumerate_subprojects(root: Path) -> list[Path]:
    """Bounded, convention-driven sub-project enumeration: root + immediate children + one level
    under apps|packages|services|libs + workspace globs. Pruned, deduped by resolved path."""
    dirs = [root]
    children = _child_dirs(root)
    dirs += children
    for c in children:
        if c.name in _WS_CONTAINERS:
            dirs += _child_dirs(c)
    dirs += _workspace_glob_dirs(root)
    seen: set = set()
    uniq: list[Path] = []
    for d in dirs:
        rp = d.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(d)
    return uniq


def infer_profiles(root: Path):
    """Multi-stack discovery → (profiles_sorted, stack_paths, confidence, signals).

    academic is exclusive (a whole-repo domain, returned alone). A positive code-stack set never
    contains a fallback (universal-software / rust-node). stack_paths maps each profile to its
    RESOLVED CONCRETE repo-relative dirs (root excluded so it can never become a per-subdir target).
    """
    single, conf, signals = infer_profile(root)
    if single == "academic":
        return [single], {}, conf, signals

    root_resolved = root.resolve()
    profiles: set = set()
    stack_paths: dict[str, list[str]] = {}
    for d in _enumerate_subprojects(root):
        is_root = d.resolve() == root_resolved
        p = detect_stack(d, deep_iac=is_root)
        if not p:
            continue
        profiles.add(p)
        if is_root:
            continue  # root never becomes a per-subdir target (SP-Y)
        rel = os.path.relpath(d.resolve(), root_resolved).replace(os.sep, "/")
        if rel and rel != ".":
            stack_paths.setdefault(p, [])
            if rel not in stack_paths[p]:
                stack_paths[p].append(rel)

    if profiles:
        ordered = sorted(profiles)
        sp = {k: sorted(v) for k, v in stack_paths.items() if v}
        if len(ordered) > 1:
            signals = signals + [f"multi-stack: {', '.join(ordered)}"]
            conf = 0.85
        return ordered, sp, conf, signals
    # fallback: the single-profile result (universal-software / None)
    return ([single] if single else []), {}, conf, signals


def check_superpowers() -> bool:
    home = Path.home()
    return (home / ".claude" / "superpowers").is_dir() or (
        home / ".claude" / "skills" / "superpowers"
    ).is_dir()


def check_agentic_stack(root: Path) -> bool:
    if (root / ".agent").is_dir():
        return True
    trigger = ".agent/"
    trigger2 = "agentic-stack"
    for candidate in [root / "CLAUDE.md", Path.home() / "CLAUDE.md"]:
        try:
            text = candidate.read_text(errors="ignore")
            if trigger in text or trigger2 in text:
                return True
        except OSError:
            pass
    return False


def scan(path: Path) -> dict:
    root = path.resolve()
    profiles, stack_paths, confidence, signals = infer_profiles(root)
    profile = profiles[0] if profiles else None  # alphabetical; == infer_profile for len-1 sets

    mode = "update" if (root / ".claude").exists() else "init"
    superpowers = check_superpowers()
    agentic = check_agentic_stack(root)
    scanned_at = datetime.datetime.now().isoformat(timespec="seconds")

    return {
        "scanned_path": str(root),
        "profile_suggestion": profile,
        "profiles": profiles,
        "stack_paths": stack_paths,
        "confidence": confidence,
        "mode": mode,
        "signals": signals,
        "superpowers_available": superpowers,
        "agentic_stack_interop": agentic,
        "scanned_at": scanned_at,
    }


def main():
    parser = argparse.ArgumentParser(
        prog="claude-bootstrap detect",
        description="Read-only project scanner — infers profile for claude-bootstrap.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to scan (default: cwd)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write JSON result to FILE instead of stdout",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only the profile name (or 'null') to stdout",
    )
    args = parser.parse_args()

    target = Path(args.path)
    if not target.is_dir():
        print(f"Error: {target} is not a directory", file=sys.stderr)
        sys.exit(2)

    result = scan(target)
    profile = result["profile_suggestion"]

    if args.quiet:
        print("null" if profile is None else profile)
        sys.exit(0 if profile is not None else 1)

    json_out = json.dumps(result, indent=2)

    if args.output:
        try:
            Path(args.output).write_text(json_out)
        except OSError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        print(json_out)

    sys.exit(0 if profile is not None else 1)


if __name__ == "__main__":
    main()
