# Security Policy

## Reporting a vulnerability

**Do not open a public GitHub issue for security bugs.**

Use one of these private channels instead:

1. **GitHub private vulnerability reporting** (preferred): https://github.com/ulissesflores/claude-bootstrap/security/advisories/new
2. **Email**: c.ulisses@gmail.com with subject `[SECURITY] claude-bootstrap: <short description>`

Include:

- Affected version (`claude-bootstrap version`)
- Reproduction steps (minimal repro preferred)
- Impact assessment (what an attacker could do)
- Suggested fix (if you have one)

## Response timeline

- **Acknowledgement**: within 72 hours of report
- **Initial assessment**: within 7 days
- **Patch release**: target 30 days for high/critical, 90 days for medium/low
- **Public disclosure**: coordinated; we credit the reporter unless requested otherwise

## Supported versions

Only the latest released minor receives security patches; everything before it is unsupported. Alpha and beta releases are not under SLA, but reports against them are welcome.

The rule is stated rather than tabulated on purpose: a pinned version table here would be a fourth version surface, and nothing keeps it in sync with `pyproject.toml`, `CITATION.cff` and `claude_bootstrap/__version__.py` (which `tests/test_metadata_currency.py` does hold together).

## Threat model — out of scope

Some classes of issues we do not consider vulnerabilities:

- **Bypassing `permissions.deny` in `.claude/settings.json`** by editing local files. Settings are guidance, not isolation. Use OS-level sandboxing for adversarial code.
- **Untrusted profile.yaml execution**. We use `yaml.safe_load`, but a malicious profile name could still resolve to attacker-controlled `templates/profiles/<name>/`. Don't run `claude-bootstrap` against repos you don't trust.
- **Outbound HTTP from `skill add` (github source)**. We `git clone --depth 1` — but git itself talks to the URL. Don't add untrusted URLs.

## Hardening recommendations

- Run `claude-bootstrap` only in trusted directories (similar to `git`).
- Review profile.yaml before installing custom profiles.
- Audit `.claude/settings.json` after `update` (especially after a `--force`).
- Verify wheel signatures when published to PyPI: `pip install --require-hashes ...`.
