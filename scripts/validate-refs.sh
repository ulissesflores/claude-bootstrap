#!/usr/bin/env bash
# validate-refs.sh — check external URLs in markdown docs are reachable.
#
# Usage:
#   bash scripts/validate-refs.sh           # verbose (prints OK and DEAD)
#   bash scripts/validate-refs.sh --quiet   # only DEAD lines
#
# Exit code = number of dead URLs (0 = all alive).
#
# Cron-able: run weekly via GitHub Actions or local crontab to detect drift.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUIET="${1:-}"

# Files to scan (user-facing markdown only).
SCAN=(
    "$ROOT/AGENTS.md"
    "$ROOT/CLAUDE.md"
    "$ROOT/CHANGELOG.md"
    "$ROOT/llms.txt"
)
# All five READMEs, not just the English one: the four translations carry the same badge and
# install URLs today (so they add no runtime), but a URL introduced in a translation alone would
# otherwise ship unchecked.
while IFS= read -r f; do SCAN+=("$f"); done < <(find "$ROOT" -maxdepth 1 -name 'README*.md')
[[ -d "$ROOT/docs" ]] && while IFS= read -r f; do SCAN+=("$f"); done < <(find "$ROOT/docs" -name '*.md')
# .github/ is user-facing too — SECURITY.md's advisory link and the Contributor Covenant URLs were
# outside the scan until now.
[[ -d "$ROOT/.github" ]] && while IFS= read -r f; do SCAN+=("$f"); done < <(find "$ROOT/.github" -name '*.md')

# Bundled skills: FIRST-PARTY ONLY. A skill is first-party iff its LICENSE.txt is byte-identical to
# this repo's own LICENSE — the same discriminator scripts/verify-skill-provenance.py reports as
# FIRST-PARTY, and it self-maintains as skills are added. The vendored ones are deliberately out:
# they are byte-pinned copies of upstream (editing one turns verify-skill-provenance.py red), and
# their SKILL.md files carry placeholder URLs — localhost, example.com, doi.org/10.XXXX/YYYY — that
# are dead by design. Scanning them would make this script's exit code permanently non-zero for
# something the repo cannot fix, destroying the honest signal described in skill-drift.yml.
first_party=0
for lic in "$ROOT"/claude_bootstrap/templates/profiles/*/skills/*/LICENSE.txt; do
    if cmp -s "$lic" "$ROOT/LICENSE"; then
        SCAN+=("${lic%/LICENSE.txt}/SKILL.md")
        first_party=$((first_party + 1))
    fi
done

# Fail loudly rather than scan nothing. `grep ... 2>/dev/null` below swallows missing paths and
# ${#SCAN[@]} would still print a plausible-looking total — a vacuous green. Exit 99 is outside the
# dead-URL exit range on purpose.
for f in "${SCAN[@]}"; do
    [[ -f "$f" ]] || {
        echo "BUG: scan target does not exist: $f" >&2
        exit 99
    }
done
((first_party > 0)) || {
    echo "BUG: no bundled skill matched $ROOT/LICENSE — the first-party discriminator broke" >&2
    exit 99
}

# Extract unique http(s) URLs. Stop at whitespace, ), >, ", `, or end of line.
urls=$(grep -hoE 'https?://[^[:space:])>"`]+' "${SCAN[@]}" 2>/dev/null \
    | sed 's/[.,;:]$//' \
    | sort -u)

# Domains known to bot-block — return 4xx to curl but work in browser.
BOT_BLOCKED='marketplace\.visualstudio\.com|medium\.com|uxplanet\.org|claude\.ai|chromewebstore\.google\.com|plugins\.jetbrains\.com'

# Transient by definition: 429 = rate-limited, 503 = temporarily unavailable, 000 = curl could not
# complete the request (timeout, DNS, reset). Counting these as DEAD makes the exit code
# non-deterministic, which would redden CI on an unrelated day for a link that is fine.
TRANSIENT_CODES='429|503|000'

dead=0
warn=0
checked=0
for url in $urls; do
    checked=$((checked + 1))
    # `|| code="000"` on the assignment, NOT `|| echo` inside it: on failure curl still writes its
    # own "000" via -w, with no trailing newline, so the old `$(curl ... || echo "000")` yielded the
    # literal string "000000" — which never matched TRANSIENT_CODES and scored the URL DEAD. That is
    # what made the exit code non-deterministic; adding 000 to the list in F2 was a vacuous fix.
    code=$(curl -sLI -A "Mozilla/5.0" -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null) || code="000"
    if [[ "$code" =~ ^[23] ]]; then
        [[ "$QUIET" != "--quiet" ]] && echo "OK   [$code] $url"
    elif [[ "$code" =~ ^($TRANSIENT_CODES)$ ]]; then
        echo "WARN [$code] $url (rate-limited/unavailable, retry later)"
        warn=$((warn + 1))
    elif [[ "$url" =~ $BOT_BLOCKED ]]; then
        echo "WARN [$code] $url (bot-blocked, verify in browser)"
        warn=$((warn + 1))
    else
        echo "DEAD [$code] $url"
        dead=$((dead + 1))
    fi
done

echo
echo "Checked: $checked URLs across ${#SCAN[@]} files. Dead: $dead. Warnings: $warn."
exit "$dead"
