#!/usr/bin/env bash
# firetest-harness.sh — run the full claude-bootstrap matrix against ONE cloned repo
# and print a single structured verdict line + anomalies. Used by the scrutiny campaign
# It installs nothing; it init/updates/uninstalls inside the repo
# and asserts the repo is left pristine.
#
# Usage:  firetest-harness.sh <repo_dir> <expected_profile|-> [cli_path]
# Output: one line:  <OK|ANOM> <name> profile=<p> created=<n> doctor=<p/w/f> pristine=<y/n> [anomalies...]
set -uo pipefail

R="${1:?repo dir}"; EXP="${2:--}"; CB="${3:-claude-bootstrap}"
name="$(basename "$R")"
anom=()
cd "$R" 2>/dev/null || { echo "ANOM $name profile=- created=- doctor=- pristine=n [cd-failed]"; exit 1; }

git_ok=0; base=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git_ok=1; base=$(git status --porcelain | wc -l | tr -d ' ')
fi

prof_json() { python3 -c "import json,sys;print(json.load(sys.stdin).get('$1'))" 2>/dev/null; }

# 1. detect (read-only)
det="$("$CB" detect "$R" 2>/dev/null)"
prof="$(printf '%s' "$det" | prof_json profile_suggestion)"
[ -z "$prof" ] && prof="None"
if [ "$EXP" != "-" ] && [ "$prof" != "$EXP" ]; then anom+=("detect=$prof!=$EXP"); fi
use="$prof"; [ "$use" = "None" ] && use="universal-software"

# 2. init --check → must write nothing
"$CB" init --check --non-interactive --profile "$use" --target "$R" </dev/null >/tmp/fh.check 2>&1 || anom+=("check-exit$?")
if [ "$git_ok" = 1 ]; then
  s=$(git status --porcelain | wc -l | tr -d ' ')
  [ "$s" != "$base" ] && anom+=("check-wrote")
fi
grep -qiE 'traceback|^error' /tmp/fh.check && anom+=("check-trace")

# 3. init (real)
"$CB" init --non-interactive --profile "$use" --target "$R" </dev/null >/tmp/fh.init 2>&1 || anom+=("init-exit$?")
created=$(grep -c '"status": "created"' /tmp/fh.init 2>/dev/null || echo 0)
grep -qiE 'traceback|^error:' /tmp/fh.init && anom+=("init-trace")

# 4. doctor → no FAIL
doc="$("$CB" doctor "$R" 2>/dev/null | grep -oE '[0-9]+ pass · [0-9]+ warn · [0-9]+ fail' | head -1)"
[ -z "$doc" ] && doc="?"; echo "$doc" | grep -qE '[1-9][0-9]* fail' && anom+=("doctor-fail")

# 5. idempotency → re-init creates nothing
"$CB" init --non-interactive --profile "$use" --target "$R" </dev/null >/tmp/fh.init2 2>&1
grep -q '"status": "created"' /tmp/fh.init2 && anom+=("non-idempotent")

# 6. uninstall → host left pristine
"$CB" uninstall --yes --target "$R" </dev/null >/tmp/fh.un 2>&1 || anom+=("uninstall-exit$?")
orph=$(find "$R" -maxdepth 2 -name '*.new' 2>/dev/null | wc -l | tr -d ' ')
[ "$orph" -gt 0 ] && anom+=("orphans=$orph")
# Count a surviving artifact only if the repo doesn't track it itself — a repo that
# ships its own .claude/ or PROJECT-STATE.md (e.g. valibot) must keep it; that's correct
# behaviour, not our leftover. (Our own untracked leftovers still trip the pristine check.)
leftover=0
for art in PROJECT-STATE.md .claude; do
  [ -e "$R/$art" ] || continue
  [ "$git_ok" = 1 ] && [ -n "$(git -C "$R" ls-files "$art" 2>/dev/null)" ] && continue
  leftover=$((leftover + 1))
done
[ "$leftover" -gt 0 ] && anom+=("emit-leftover=$leftover")
pristine="y"
if [ "$git_ok" = 1 ]; then
  s=$(git status --porcelain | wc -l | tr -d ' ')
  [ "$s" != "$base" ] && { pristine="n"; anom+=("git-delta=$((s-base))"); }
fi

verdict="OK"; [ "${#anom[@]}" -gt 0 ] && verdict="ANOM"
printf '%s %-26s profile=%-18s created=%-3s doctor=[%s] pristine=%s' "$verdict" "$name" "$prof" "$created" "$doc" "$pristine"
[ "${#anom[@]}" -gt 0 ] && printf ' anomalies=[%s]' "$(IFS=,; echo "${anom[*]}")"
printf '\n'
