#!/usr/bin/env bash
# update-registry.sh — validate claude_bootstrap/registry/skills.yaml freshness.
# Cron-able: run weekly to check URLs and stamp last_validated_at.
# Non-destructive in --check mode.
#
# Exit codes: 0 = all OK, 1 = >=1 FAIL
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
REGISTRY="$REPO/claude_bootstrap/registry/skills.yaml"

CHECK_MODE=false
QUIET=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --check) CHECK_MODE=true; shift ;;
        --quiet) QUIET=true; shift ;;
        --help) echo "Usage: $0 [--check] [--quiet]"; exit 0 ;;
        *) echo "WARN: unknown flag: $1" >&2; shift ;;
    esac
done

# 1. Run skill validate
[[ "$QUIET" == false ]] && echo "==> Running skill validate..."
if ! "$REPO/bin/bootstrap.sh" skill validate 2>&1; then
    echo "FAIL: skill validate failed — aborting" >&2
    exit 1
fi

# 2. Parse registry, iterate, validate URLs and local paths
RESULT=$(python3 - "$REGISTRY" "$REPO" "$CHECK_MODE" <<'PYEOF'
import sys, yaml, datetime, pathlib, urllib.request, urllib.error

registry_path = pathlib.Path(sys.argv[1])
repo_root     = pathlib.Path(sys.argv[2])
check_mode    = sys.argv[3].lower() == "true"

STALE_DAYS = 90
today = datetime.date.today()

data = yaml.safe_load(registry_path.read_text()) or []

rows = []       # (name, src_type, status, stale_flag, should_stamp)
fail_count = 0

for skill in data:
    name     = skill.get("name", "?")
    src      = skill.get("source") or {}
    src_type = src.get("type", "unknown")
    status   = "OK"
    should_stamp = False

    if src_type == "github":
        url = src.get("url", "")
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "update-registry/1.0")
            with urllib.request.urlopen(req, timeout=10) as resp:
                code = resp.status
            if code >= 400:
                status = f"WARN(HTTP {code})"
            else:
                should_stamp = True
        except urllib.error.HTTPError as e:
            status = f"WARN(HTTP {e.code})"
        except Exception as e:
            status = f"WARN({type(e).__name__})"

    elif src_type == "local":
        skill_path = repo_root / src.get("path", "") / "SKILL.md"
        if skill_path.exists():
            should_stamp = True
        else:
            status = f"FAIL(missing: {src.get('path','?')}/SKILL.md)"
            fail_count += 1

    else:
        status = f"WARN(unknown source type: {src_type})"

    # stale check
    lv = skill.get("last_validated_at")
    stale = False
    if lv:
        try:
            lv_date = datetime.date.fromisoformat(str(lv))
            stale = (today - lv_date).days > STALE_DAYS
        except ValueError:
            stale = True
    else:
        stale = True

    rows.append((name, src_type, status, stale, should_stamp))

# Print table
col_name = max(len(r[0]) for r in rows) if rows else 4
col_name = max(col_name, 4)
hdr  = f"{'NAME':<{col_name}}  {'TYPE':<7}  {'STATUS':<22}  STALE"
sep  = f"{'-'*col_name}  {'-'*7}  {'-'*22}  -----"
print(hdr)
print(sep)
stale_list = []
ok_names   = []
for (name, src_type, status, stale, should_stamp) in rows:
    stale_mark = "YES" if stale else ""
    print(f"{name:<{col_name}}  {src_type:<7}  {status:<22}  {stale_mark}")
    if stale:
        stale_list.append(name)
    if should_stamp and not check_mode:
        ok_names.append(name)

print()
total = len(rows)
warn_count  = sum(1 for r in rows if r[2].startswith("WARN"))
fail_count2 = sum(1 for r in rows if r[2].startswith("FAIL"))
print(f"Summary: {total} skills — {fail_count2} FAIL, {warn_count} WARN, {total-fail_count2-warn_count} OK")

if stale_list:
    print(f"Stale (>{STALE_DAYS}d): {', '.join(stale_list)}")

if check_mode:
    print("(dry-run: last_validated_at not updated)")
else:
    print(f"Will stamp: {', '.join(ok_names) if ok_names else 'none'}")

# Emit stamp targets for shell layer (newline-separated, prefixed OK:)
for name in ok_names:
    print(f"__STAMP__:{name}")

sys.exit(1 if fail_count2 > 0 else 0)
PYEOF
)

PY_EXIT=$?

# 3. Print output (filter __STAMP__ lines for display)
if [[ "$QUIET" == false ]]; then
    grep -v "^__STAMP__:" <<< "$RESULT" || true
fi

# 4. Apply last_validated_at stamps if not in check mode
if [[ "$CHECK_MODE" == false ]]; then
    TODAY=$(date +%Y-%m-%d)
    while IFS= read -r line; do
        [[ "$line" == __STAMP__:* ]] || continue
        skill_name="${line#__STAMP__:}"
        # Stamp only the matching entry — use Python for safe YAML in-place edit
        python3 - "$REGISTRY" "$skill_name" "$TODAY" <<'STAMP_PY'
import sys, re

registry_file = sys.argv[1]
skill_name    = sys.argv[2]
today         = sys.argv[3]

text = open(registry_file).read()
# Replace last_validated_at for the specific skill block.
# Strategy: find "- name: <skill>" then replace the next last_validated_at line within ~20 lines.
pattern = rf'(- name: {re.escape(skill_name)}\b(?:(?!\n- name:).)*?last_validated_at: )\S+'
replacement = rf'\g<1>{today}'
new_text = re.sub(pattern, replacement, text, count=1, flags=re.DOTALL)
if new_text != text:
    open(registry_file, 'w').write(new_text)
STAMP_PY
    done <<< "$RESULT"
fi

exit $PY_EXIT
