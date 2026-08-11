"""Tests for claude_bootstrap/detect.py."""

import json
from pathlib import Path

import pytest
from conftest import REPO_ROOT, run_python


def test_empty_dir_no_profile(tmp_project: Path):
    rc, stdout, _ = run_python("detect.py", [str(tmp_project)])
    assert rc == 1
    data = json.loads(stdout)
    assert data["profile_suggestion"] is None


def test_repo_self_scan(tmp_project: Path):
    rc, stdout, _ = run_python("detect.py", [str(REPO_ROOT)])
    # `.claude/` is gitignored so CI checkouts won't have it; mode tracks actual state.
    data = json.loads(stdout)
    expected_mode = "update" if (REPO_ROOT / ".claude").exists() else "init"
    assert data["mode"] == expected_mode
    assert "scanned_path" in data
    assert "signals" in data


def test_bib_does_not_override_code_project(tmp_project: Path):
    """A code project with a stray .bib must NOT be classified academic (fire-test Bug 4)."""
    (tmp_project / "setup.py").write_text("from setuptools import setup\nsetup(name='x')\n")
    (tmp_project / "paper.bib").write_text("@article{x, title={y}}\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() in ("data-science", "universal-software"), "stray .bib hijacked to academic"


def test_tex_is_still_academic(tmp_project: Path):
    (tmp_project / "paper.tex").write_text("\\documentclass{article}\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "academic"


def test_bib_alone_is_still_academic(tmp_project: Path):
    (tmp_project / "refs.bib").write_text("@book{x}\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "academic"


def test_csl_alone_is_academic(tmp_project: Path):
    """Any Citation Style Language file is an academic marker on its own."""
    (tmp_project / "apa.csl").write_text("<style/>\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "academic"


def test_csl_signal_is_reported(tmp_project: Path):
    """The rationale names the .csl signal, not just the verdict."""
    (tmp_project / "chicago.csl").write_text("<style/>\n")
    rc, stdout, _ = run_python("detect.py", [str(tmp_project)])
    assert rc == 0
    assert any(".csl file(s) found" in s for s in json.loads(stdout)["signals"])


def test_csl_in_a_code_project_is_not_academic(tmp_project: Path):
    """A doc pipeline vendoring a citation style must not hijack a code repo (same guard as .bib)."""
    (tmp_project / "apa.csl").write_text("<style/>\n")
    (tmp_project / "pyproject.toml").write_text('[project]\nname = "x"\n')
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "universal-software"


def test_csl_guard_covers_non_python_ecosystems(tmp_project: Path):
    """The `.csl` guard uses the wide marker list — a Go repo with a citation style is not academic.

    The narrow list (Python/Node/Rust) let a `.csl` at the root of a Go/Java/Ruby/PHP repo
    reclassify it to academic at 0.95 *exclusive*, which also skips the monorepo sub-scan.
    """
    (tmp_project / "apa.csl").write_text("<style/>\n")
    (tmp_project / "go.mod").write_text("module example.com/x\n\nrequire github.com/gin-gonic/gin v1.9.1\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() != "academic", "a .csl in a Go project hijacked detection"


def test_csl_in_an_iac_repo_is_still_devops(tmp_project: Path):
    """A `.csl` next to a Dockerfile + manifests dir must not outrank the IaC verdict."""
    (tmp_project / "apa.csl").write_text("<style/>\n")
    (tmp_project / "Dockerfile").write_text("FROM alpine\n")
    (tmp_project / "k8s").mkdir()
    (tmp_project / "k8s" / "deployment.yaml").write_text("kind: Deployment\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "devops"


def test_bib_guard_stays_narrow_for_joss_shape(tmp_project: Path):
    """`go.mod` + `paper.bib` is the standard JOSS submission shape and stays academic.

    Deliberate asymmetry with the test above: only the `.csl` term got the wide marker list,
    because widening `.bib` too would reclassify a pre-existing case this batch did not break.
    """
    (tmp_project / "paper.bib").write_text("@article{x, title={y}}\n")
    (tmp_project / "go.mod").write_text("module example.com/x\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "academic"


def test_ds_keyword_in_comment_not_data_science(tmp_project: Path):
    """A DS lib named only in a comment must NOT trigger data-science (fire-test Bug 7)."""
    (tmp_project / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["click"]\n\n[tool.ruff.lint]\n# "PD" — we are not pandas\n'
    )
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "universal-software", "DS keyword in a comment wrongly → data-science"


def test_ds_keyword_in_real_dep_is_data_science(tmp_project: Path):
    (tmp_project / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["numpy>=1.20", "pandas"]\n'
    )
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "data-science"


def test_devops_recursive_dockerfile_and_iac_dir(tmp_project: Path):
    """Dockerfile in a subdir + a `k8s-specifications/` dir → devops (fire-test Bug 5)."""
    (tmp_project / "app").mkdir()
    (tmp_project / "app" / "Dockerfile").write_text("FROM python:3.11\n")
    (tmp_project / "k8s-specifications").mkdir()
    (tmp_project / "k8s-specifications" / "deploy.yaml").write_text("kind: Deployment\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "devops"


def test_devops_terraform_files_without_docker(tmp_project: Path):
    """A pure-IaC repo (terraform `.tf` nested under a non-standard dir, no Dockerfile) is the
    canonical devops case — fire-test batch 3 (hashicorp/terraform-guides: 117 .tf, no root Docker)."""
    nested = tmp_project / "infrastructure-as-code" / "aws-vpc"
    nested.mkdir(parents=True)
    (nested / "main.tf").write_text('resource "aws_vpc" "main" {}\n')
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "devops"


def test_devops_helm_chart_without_docker(tmp_project: Path):
    """A Helm chart repo (`Chart.yaml` nested under stable/<chart>/, no Dockerfile) → devops —
    fire-test batch 3 (helm/charts: 363 Chart.yaml, dirs `stable/`/`incubator/`)."""
    chart = tmp_project / "stable" / "nginx"
    chart.mkdir(parents=True)
    (chart / "Chart.yaml").write_text("apiVersion: v2\nname: nginx\nversion: 1.0.0\n")
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert stdout.strip() == "devops"


def test_quiet_mode(tmp_project: Path):
    # Create a pyproject.toml so a profile is detected
    (tmp_project / "pyproject.toml").write_text('[project]\nname = "test"\n')
    rc, stdout, _ = run_python("detect.py", ["--quiet", str(tmp_project)])
    assert rc == 0
    profile = stdout.strip()
    assert profile in (
        "universal-software",
        "data-science",
        "frontend",
        "devops",
        "backend",
        "academic",
    )


# --- D03: multi-stack discovery (detect_stack + infer_profiles) -------------------------------


def _mk(p: Path, text: str = "x") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def test_detect_stack_tiebreak_fastapi_pandas_is_backend(tmp_path: Path):
    """WEAK-DS (pandas) + a web framework → backend, not data-science (flipped tie-break)."""
    from claude_bootstrap.detect import detect_stack

    _mk(tmp_path / "pyproject.toml", '[project]\ndependencies = ["fastapi", "pandas"]\n')
    assert detect_stack(tmp_path) == "backend"


def test_detect_stack_torch_serving_api_stays_data_science(tmp_path: Path):
    """STRONG-DS (torch) keeps data-science even with a web framework (STRONG-override)."""
    from claude_bootstrap.detect import detect_stack

    _mk(tmp_path / "pyproject.toml", '[project]\ndependencies = ["fastapi", "torch"]\n')
    assert detect_stack(tmp_path) == "data-science"


def test_detect_stack_pure_ml_is_data_science(tmp_path: Path):
    from claude_bootstrap.detect import detect_stack

    _mk(tmp_path / "requirements.txt", "torch==2.3\n")
    assert detect_stack(tmp_path) == "data-science"


def test_detect_stack_nestjs_with_tsconfig_is_backend(tmp_path: Path):
    """Node precedence: a backend framework dep → backend even with tsconfig (NOT frontend)."""
    from claude_bootstrap.detect import detect_stack

    _mk(tmp_path / "package.json", '{"dependencies": {"@nestjs/core": "^10"}}')
    _mk(tmp_path / "tsconfig.json", "{}")
    assert detect_stack(tmp_path) == "backend"


def test_detect_stack_react_stays_frontend(tmp_path: Path):
    from claude_bootstrap.detect import detect_stack

    _mk(tmp_path / "package.json", '{"dependencies": {"react": "^18", "next": "^14"}}')
    _mk(tmp_path / "tsconfig.json", "{}")
    assert detect_stack(tmp_path) == "frontend"


def test_detect_stack_express_is_backend(tmp_path: Path):
    from claude_bootstrap.detect import detect_stack

    _mk(tmp_path / "package.json", '{"dependencies": {"express": "^4"}}')
    assert detect_stack(tmp_path) == "backend"


def test_detect_stack_rails_and_go_are_backend(tmp_path: Path):
    from claude_bootstrap.detect import detect_stack

    rails = tmp_path / "rb"
    _mk(rails / "Gemfile", 'gem "rails", "~> 7.1"\n')
    assert detect_stack(rails) == "backend"
    go = tmp_path / "go"
    _mk(go / "go.mod", "module x\n\nrequire github.com/gin-gonic/gin v1.9.1\n")
    assert detect_stack(go) == "backend"


def test_detect_stack_bare_manifest_is_none(tmp_path: Path):
    """A bare manifest with no positive marker is NOT a positive stack (never universal in a set)."""
    from claude_bootstrap.detect import detect_stack

    _mk(tmp_path / "pyproject.toml", '[project]\nname = "x"\ndependencies = ["click"]\n')
    assert detect_stack(tmp_path) is None


def test_infer_profiles_monorepo_union(tmp_path: Path):
    """frontend/ + backend/(fastapi+pandas) + infra/(*.tf) → sorted union + concrete stack_paths."""
    from claude_bootstrap.detect import infer_profiles

    _mk(tmp_path / "frontend" / "package.json", '{"dependencies": {"react": "^18"}}')
    _mk(tmp_path / "frontend" / "tsconfig.json", "{}")
    _mk(tmp_path / "backend" / "pyproject.toml", '[project]\ndependencies = ["fastapi", "pandas"]\n')
    _mk(tmp_path / "infra" / "main.tf", 'resource "aws_vpc" "m" {}\n')
    profiles, stack_paths, _conf, _sig = infer_profiles(tmp_path)
    assert profiles == ["backend", "devops", "frontend"]
    assert stack_paths["frontend"] == ["frontend"]
    assert stack_paths["backend"] == ["backend"]
    assert stack_paths["devops"] == ["infra"]
    # SP-Y: root never appears as a stack_paths target
    for dirs in stack_paths.values():
        assert "." not in dirs and "" not in dirs


def test_infer_profiles_prunes_examples(tmp_path: Path):
    """A foreign marker under examples/ must NOT create a phantom stack (SP-O)."""
    from claude_bootstrap.detect import infer_profiles

    _mk(tmp_path / "pyproject.toml", '[project]\ndependencies = ["fastapi"]\n')
    _mk(tmp_path / "examples" / "react-demo" / "package.json", '{"dependencies": {"react": "^18"}}')
    _mk(tmp_path / "examples" / "react-demo" / "tsconfig.json", "{}")
    profiles, _sp, _conf, _sig = infer_profiles(tmp_path)
    assert profiles == ["backend"]
    assert "frontend" not in profiles


def test_infer_profiles_bare_python_is_universal_len1(tmp_path: Path):
    from claude_bootstrap.detect import infer_profiles

    _mk(tmp_path / "pyproject.toml", '[project]\nname = "x"\ndependencies = ["click"]\n')
    profiles, stack_paths, _conf, _sig = infer_profiles(tmp_path)
    assert profiles == ["universal-software"]
    assert stack_paths == {}


def test_infer_profiles_workspace_globs(tmp_path: Path):
    """apps/* workspace globs are discovered and mapped to concrete dirs."""
    from claude_bootstrap.detect import infer_profiles

    _mk(tmp_path / "package.json", '{"workspaces": ["apps/*"]}')
    _mk(tmp_path / "apps" / "web" / "package.json", '{"dependencies": {"react": "^18"}}')
    _mk(tmp_path / "apps" / "web" / "tsconfig.json", "{}")
    _mk(tmp_path / "apps" / "api" / "package.json", '{"dependencies": {"express": "^4"}}')
    profiles, stack_paths, _conf, _sig = infer_profiles(tmp_path)
    assert profiles == ["backend", "frontend"]
    assert stack_paths["frontend"] == ["apps/web"]
    assert stack_paths["backend"] == ["apps/api"]


def test_infer_profiles_root_stack_excluded_from_paths(tmp_path: Path):
    """A root-level stack (frontend at root) joins the set but is NOT a per-subdir target (SP-Y)."""
    from claude_bootstrap.detect import infer_profiles

    _mk(tmp_path / "package.json", '{"dependencies": {"react": "^18"}}')
    _mk(tmp_path / "tsconfig.json", "{}")
    _mk(tmp_path / "api" / "pyproject.toml", '[project]\ndependencies = ["fastapi"]\n')
    profiles, stack_paths, _conf, _sig = infer_profiles(tmp_path)
    assert profiles == ["backend", "frontend"]
    assert stack_paths.get("backend") == ["api"]
    assert "frontend" not in stack_paths  # root frontend → excluded


def test_infer_profiles_academic_is_exclusive(tmp_path: Path):
    """Academic stays a whole-repo domain — no discovery, returned alone."""
    from claude_bootstrap.detect import infer_profiles

    _mk(tmp_path / "paper.tex", "\\documentclass{article}\n")
    _mk(tmp_path / "src" / "pyproject.toml", '[project]\ndependencies = ["fastapi"]\n')
    profiles, stack_paths, _conf, _sig = infer_profiles(tmp_path)
    assert profiles == ["academic"]
    assert stack_paths == {}


# --- D04: regression sweep — single-stack repos stay len-1; reclassification delta is bounded ----

_SINGLE_STACK_SHAPES = [
    ({"pyproject.toml": '[project]\ndependencies = ["click"]\n'}, ["universal-software"]),
    ({"Cargo.toml": '[package]\nname = "x"\n'}, ["universal-software"]),
    ({"package.json": '{"dependencies": {"commander": "^11"}}'}, ["universal-software"]),
    ({"requirements.txt": "numpy>=1.20\npandas\n"}, ["data-science"]),
    ({"requirements.txt": "torch==2.3\n"}, ["data-science"]),
    ({"package.json": '{"dependencies": {"react": "^18"}}', "tsconfig.json": "{}"}, ["frontend"]),
    ({"main.tf": 'resource "aws_vpc" "m" {}\n'}, ["devops"]),
    ({"paper.tex": "\\documentclass{article}\n"}, ["academic"]),
    ({"pyproject.toml": '[project]\ndependencies = ["fastapi"]\n'}, ["backend"]),
]


@pytest.mark.parametrize("files,expected", _SINGLE_STACK_SHAPES)
def test_regression_single_stack_stays_len1(tmp_path: Path, files: dict, expected: list):
    """No single-stack repo flips to a multi-set (SP-A); each detects the expected single profile."""
    from claude_bootstrap.detect import infer_profiles

    for name, content in files.items():
        _mk(tmp_path / name, content)
    profiles, _sp, _conf, _sig = infer_profiles(tmp_path)
    assert profiles == expected
    assert len(profiles) == 1  # never single→multi


# The ONLY allowed single→single reclassifications vs the currently-shipped infer_profile, each
# justified by a web-framework marker. Anything outside this frozen set is a regression.
_RECLASSIFICATION_DELTA = {
    "universal_to_backend": (
        {"pyproject.toml": '[project]\ndependencies = ["fastapi"]\n'},
        "universal-software",
        "backend",
    ),
    "datascience_to_backend": (
        {"pyproject.toml": '[project]\ndependencies = ["fastapi", "pandas"]\n'},
        "data-science",
        "backend",
    ),
    "frontend_to_backend": (
        {"package.json": '{"dependencies": {"@nestjs/core": "^10"}}', "tsconfig.json": "{}"},
        "frontend",
        "backend",
    ),
    "none_to_backend": ({"Gemfile": 'gem "rails", "~> 7.1"\n'}, None, "backend"),
}


@pytest.mark.parametrize("case", list(_RECLASSIFICATION_DELTA))
def test_reclassification_delta_is_exactly_the_frozen_set(tmp_path: Path, case: str):
    """Each documented reclassification moves old→new exactly as frozen (advisor#1 + validator)."""
    from claude_bootstrap.detect import infer_profile, infer_profiles

    files, old, new = _RECLASSIFICATION_DELTA[case]
    d = tmp_path / case
    for name, content in files.items():
        _mk(d / name, content)
    assert infer_profile(d)[0] == old, f"{case}: old detection drifted"
    assert infer_profiles(d)[0][0] == new, f"{case}: new detection drifted"


def test_strong_ml_repo_never_reclassifies_to_backend(tmp_path: Path):
    """A STRONG-ML repo (torch) stays data-science even with a framework — NOT in the delta."""
    from claude_bootstrap.detect import infer_profiles

    _mk(tmp_path / "pyproject.toml", '[project]\ndependencies = ["fastapi", "torch"]\n')
    assert infer_profiles(tmp_path)[0] == ["data-science"]
