# Release Process — claude-bootstrap

This doc covers how to cut a new release. **Maintainer-only**.

---

## One-time PyPI setup (already done if `claude-bootstrap` exists on PyPI)

1. Create PyPI account: https://pypi.org/account/register/
2. Configure trusted publishing (no token needed):
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher:
     - **PyPI Project Name**: `claude-bootstrap`
     - **Owner**: `ulissesflores`
     - **Repository name**: `claude-bootstrap`
     - **Workflow name**: `release.yml`
     - **Environment name**: `pypi`
3. In GitHub repo Settings → Environments → create environment `pypi` (no secrets required; OIDC handles auth)

After first publish completes, the pending publisher becomes a real one.

---

## Release checklist

For each release tagged `vX.Y.Z`:

### 1. Pre-release verification (on `main`)

```bash
# Checkout main and pull latest
git checkout main && git pull

# Tests pass
uv run --with pytest --with jinja2 --with pyyaml --with rich --with questionary --no-project pytest tests/

# Pre-commit clean
uv run --with pre-commit --no-project pre-commit run --all-files

# CI is green
gh run list --limit 3 --json conclusion --jq '.[].conclusion' | grep -c success  # should be 3

# Refs not broken
bash scripts/validate-refs.sh

# Wheel + sdist build
uv run --with build --no-project python -m build
ls dist/  # should have .whl + .tar.gz

# Smoke test wheel install
python3 -m venv /tmp/release-test
/tmp/release-test/bin/pip install dist/*.whl
/tmp/release-test/bin/claude-bootstrap version  # should print expected version
rm -rf /tmp/release-test dist build *.egg-info
```

### 2. Bump version

Update `claude_bootstrap/__version__.py`:

```python
__version__ = "X.Y.Z"  # PEP 440: 0.3.0, 0.4.0a0, 1.0.0rc1, etc.
```

Update `pyproject.toml` `version = "X.Y.Z"` to match.

### 3. Update CHANGELOG.md

Move `[Unreleased]` content to a new section `[X.Y.Z] - YYYY-MM-DD`. Keep `[Unreleased]` as a placeholder.

### 4. Commit + tag + push

```bash
git add claude_bootstrap/__version__.py pyproject.toml CHANGELOG.md
git commit -m "release: vX.Y.Z

Highlights:
- ...

Full changelog: https://github.com/ulissesflores/claude-bootstrap/blob/main/CHANGELOG.md"

# Sign the tag (recommended)
git tag -s -a vX.Y.Z -m "Release vX.Y.Z"
# Or unsigned (still works):
# git tag -a vX.Y.Z -m "Release vX.Y.Z"

# Push commit + tag
git push origin main
git push origin vX.Y.Z
```

### 5. Create GitHub Release

The tag push triggers `.github/workflows/release.yml`, which:

1. Builds wheel + sdist
2. Publishes to PyPI via OIDC trusted publishing
3. Uploads wheel + sdist to the GitHub Release

Manually create the GitHub Release if not auto-created:

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes-file <(awk '/^## \[X.Y.Z\]/,/^## \[/' CHANGELOG.md | head -n -1)
```

### 6. Post-release verification

```bash
# Wait ~5 min for PyPI propagation, then:
pip install --upgrade claude-bootstrap
claude-bootstrap version  # should print vX.Y.Z

# Verify install.sh works against PyPI
bash <(curl -sSL https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh)
```

### 7. Update HANDOFF / docs

If significant changes for next session/contributor:
- Tweet / post in Discussions if appropriate

---

## Versioning rules

[Semantic Versioning](https://semver.org/):

- `vX.0.0` — major: breaking API changes, removal of features, rename of CLI commands
- `v0.X.0` — minor: new feature, new profile, new flag (backward compatible)
- `v0.0.X` — patch: bug fix, doc fix, refactor (no behavior change)

Pre-1.0:
- All `0.X.0` releases may have breaking changes (alpha state)
- Use `0.X.0aN` (alpha), `0.X.0bN` (beta), `0.X.0rcN` (release candidate)
- Tag format: `v0.3.0a0` → publishes as PyPI `0.3.0a0`

---

## Hotfix process (urgent fix on already-released version)

```bash
# Branch from the tag
git checkout -b hotfix/X.Y.Z+1 vX.Y.Z

# Apply fix + test
# ...

# Bump version to X.Y.(Z+1)
# Follow steps 4-6 above with the new version
```

Then merge hotfix branch back to `main`.

---

## Yanking a bad release (emergency)

If a release is broken (security, data loss, build failure):

1. **PyPI yank** (does NOT delete; marks as not for new installs):
   ```bash
   # Via web UI: pypi.org/project/claude-bootstrap → Manage → Yank
   # Or via twine: twine upload not supported for yanking — use web UI.
   ```
2. Delete GitHub Release tag (only if no one has pulled):
   ```bash
   gh release delete vX.Y.Z --cleanup-tag
   ```
3. Cut hotfix `vX.Y.(Z+1)` immediately. Document the yank in CHANGELOG.

---

## Release roles

For solo maintainer (current state): all of the above is done by `@ulissesflores`.

For multi-maintainer future:
- **Author**: prepares the PR with version bumps + CHANGELOG
- **Reviewer**: approves the release PR
- **Releaser**: tags + pushes (triggers automation)
