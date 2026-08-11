# claude-bootstrap test suite

Integration tests for the bootstrap engine. No mocks — each test invokes the real CLI via subprocess in a `tmp_path` isolated directory.

## Running the tests

```bash
cd /path/to/claude-bootstrap
uv run --with pytest --with jinja2 --with pyyaml --with rich --with questionary --no-project pytest tests/ -v
```

## Dependencies

| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `jinja2` | Required by `install.py` for template rendering |
| `pyyaml` | Required by `install.py` and `skill.py` for profile/registry parsing |
| `rich` | Required by `doctor.py` for table output |
| `questionary` | Required by `interview.py` (interactive mode; `--non-interactive` skips it) |

## Caveats

- **`skill.py show <name>` bug**: `last_validated_at` in `claude_bootstrap/registry/skills.yaml` is parsed by PyYAML as a `datetime.date` object, which `json.dumps` cannot serialize. `test_skill_show_returns_entry` therefore tests the lookup path (skill found vs. not found) rather than asserting on the JSON output.
- Tests require `uv` on `$PATH` (used by `run_python` helper in `conftest.py`).
- `bootstrap.sh init` tests use `run_python install.py` directly (bypassing the shell wrapper) for speed and to avoid `questionary` TTY checks.
