#!/bin/bash
# lint-skills.sh — repo-level lint for the astra-methodology plugin.
#
# A single command a maintainer or CI runs from the repo root. Each check
# prints PASS / FAIL / WARN with detail. The script exits non-zero if any
# check FAILs (WARNs never fail the build). The final line is a
# machine-parseable contract line:
#
#   ASTRA_LINT_RESULT: PASS|FAIL fail=N warn=N
#
# where fail / warn count the number of *checks* in that state.
#
# No external deps beyond coreutils + jq + perl (all present on macOS/Linux CI).
# Hangul detection uses perl (BSD grep has no -P).

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || { echo "cannot cd to repo root: $REPO_ROOT" >&2; exit 2; }

FAILN=0
WARNN=0
declare -a ROWS

# row <check-label> <PASS|FAIL|WARN>
row() {
  ROWS+=("$2|$1")
  case "$2" in
    FAIL) FAILN=$((FAILN + 1)) ;;
    WARN) WARNN=$((WARNN + 1)) ;;
  esac
}

hr() { printf -- '----------------------------------------------------------\n'; }
head_check() { printf '\n[%s] %s\n' "$1" "$2"; }

# has_hangul <text> -> exit 0 if the text contains a Hangul syllable (AC00-D7A3)
has_hangul() {
  printf '%s' "$1" | perl -CSD -ne 'if(/[\x{AC00}-\x{D7A3}]/){exit 0} END{exit 1}'
}

# get_desc <file> -> prints the frontmatter description text (inline or block scalar)
get_desc() {
  awk '
    /^---[[:space:]]*$/ { d++; next }
    d==1 {
      if ($0 ~ /^description:/) {
        indesc=1
        v=$0; sub(/^description:[[:space:]]*/,"",v)
        gsub(/^"|"$/,"",v); gsub(/^'"'"'|'"'"'$/,"",v)
        if (v=="" || v ~ /^[>|][+-]?[0-9]*[[:space:]]*$/) next
        print v; next
      }
      if (indesc) {
        if ($0 ~ /^[A-Za-z0-9_-]+:/) { indesc=0; next }
        print
      }
    }
  ' "$1"
}

# fm_value <file> <key> -> prints the (trimmed) inline value of a frontmatter key
fm_value() {
  awk -v k="^$2:" '
    /^---[[:space:]]*$/ { d++; next }
    d==1 && $0 ~ k {
      v=$0; sub(/^[A-Za-z0-9_-]+:[[:space:]]*/,"",v)
      gsub(/^"|"$/,"",v)
      print v; exit
    }
  ' "$1"
}

fm_has_key() {
  awk -v k="^$2:" '
    /^---[[:space:]]*$/ { d++; next }
    d==1 && $0 ~ k { found=1 }
    END { exit(found?0:1) }
  ' "$1"
}

starts_with_frontmatter() {
  [ "$(head -1 "$1")" = "---" ]
}

# ---------------------------------------------------------------------------
# Check 1 — Frontmatter completeness
# ---------------------------------------------------------------------------
head_check 1 "Frontmatter completeness (skills + agents)"
c1_status=PASS
for sk in skills/*/SKILL.md; do
  [ -f "$sk" ] || continue
  dir="$(basename "$(dirname "$sk")")"
  if ! starts_with_frontmatter "$sk"; then
    echo "  FAIL  $sk does not start with '---'"; c1_status=FAIL; continue
  fi
  name="$(fm_value "$sk" name)"
  desc="$(get_desc "$sk")"
  if [ -z "$name" ]; then
    echo "  FAIL  $sk has empty name:"; c1_status=FAIL
  elif [ "$name" != "$dir" ]; then
    echo "  FAIL  $sk name '$name' != directory '$dir'"; c1_status=FAIL
  fi
  if [ -z "${desc//[[:space:]]/}" ]; then
    echo "  FAIL  $sk has empty description:"; c1_status=FAIL
  fi
done
for ag in agents/*.md; do
  [ -f "$ag" ] || continue
  if ! starts_with_frontmatter "$ag"; then
    echo "  FAIL  $ag does not start with '---'"; c1_status=FAIL; continue
  fi
  name="$(fm_value "$ag" name)"
  desc="$(get_desc "$ag")"
  [ -z "$name" ] && { echo "  FAIL  $ag has empty name:"; c1_status=FAIL; }
  [ -z "${desc//[[:space:]]/}" ] && { echo "  FAIL  $ag has empty description:"; c1_status=FAIL; }
  fm_has_key "$ag" tools    || { echo "  FAIL  $ag missing tools:"; c1_status=FAIL; }
  fm_has_key "$ag" model    || { echo "  FAIL  $ag missing model:"; c1_status=FAIL; }
  fm_has_key "$ag" maxTurns || { echo "  FAIL  $ag missing maxTurns:"; c1_status=FAIL; }
  dtools="$(fm_value "$ag" disallowedTools)"
  if [ -z "$dtools" ]; then
    echo "  FAIL  $ag missing disallowedTools:"; c1_status=FAIL
  else
    case "$dtools" in *Write*) : ;; *) echo "  FAIL  $ag disallowedTools missing Write"; c1_status=FAIL ;; esac
    case "$dtools" in *Edit*)  : ;; *) echo "  FAIL  $ag disallowedTools missing Edit";  c1_status=FAIL ;; esac
  fi
done
[ "$c1_status" = PASS ] && echo "  PASS  all skills/agents have complete frontmatter"
row "Frontmatter completeness" "$c1_status"

# ---------------------------------------------------------------------------
# Check 2 — 500-line gate (WARN only)
# ---------------------------------------------------------------------------
head_check 2 "500-line gate on SKILL.md (WARN if over)"
c2_status=PASS
for sk in skills/*/SKILL.md; do
  [ -f "$sk" ] || continue
  n="$(wc -l < "$sk" | tr -d ' ')"
  if [ "$n" -gt 500 ]; then
    echo "  WARN  $sk is $n lines (> 500)"; c2_status=WARN
  fi
done
[ "$c2_status" = PASS ] && echo "  PASS  all SKILL.md <= 500 lines"
row "500-line gate" "$c2_status"

# ---------------------------------------------------------------------------
# Check 3 — English description (no Hangul)
# ---------------------------------------------------------------------------
head_check 3 "English description (no Hangul in description:)"
c3_status=PASS
for f in skills/*/SKILL.md agents/*.md; do
  [ -f "$f" ] || continue
  desc="$(get_desc "$f")"
  if [ -n "$desc" ] && has_hangul "$desc"; then
    echo "  FAIL  $f description contains Hangul"; c3_status=FAIL
  fi
done
[ "$c3_status" = PASS ] && echo "  PASS  all descriptions are Hangul-free"
row "English description" "$c3_status"

# ---------------------------------------------------------------------------
# Check 4 — Persona guard prefix
# ---------------------------------------------------------------------------
head_check 4 "Persona guard prefix on *-persona agents"
c4_status=PASS
GUARD='[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]'
for p in tester designer developer; do
  af="agents/${p}-persona.md"
  if [ ! -f "$af" ]; then
    echo "  FAIL  $af not found"; c4_status=FAIL; continue
  fi
  first="$(get_desc "$af" | awk 'NF{print; exit}')"
  case "$first" in
    *"$GUARD"*) : ;;
    *) echo "  FAIL  $af first description line missing guard: $first"; c4_status=FAIL ;;
  esac
done
[ "$c4_status" = PASS ] && echo "  PASS  all persona agents carry the guard prefix"
row "Persona guard prefix" "$c4_status"

# ---------------------------------------------------------------------------
# Check 5 — Version sync
# ---------------------------------------------------------------------------
head_check 5 "Version sync (plugin.json == marketplace.json)"
c5_status=PASS
PV="$(jq -r '.version' .claude-plugin/plugin.json 2>/dev/null)"
MV="$(jq -r '.plugins[0].version' .claude-plugin/marketplace.json 2>/dev/null)"
if [ -z "$PV" ] || [ "$PV" = null ]; then
  echo "  FAIL  plugin.json .version is empty/null"; c5_status=FAIL
elif [ -z "$MV" ] || [ "$MV" = null ]; then
  echo "  FAIL  marketplace.json .plugins[0].version is empty/null"; c5_status=FAIL
elif [ "$PV" != "$MV" ]; then
  echo "  FAIL  version mismatch: plugin.json=$PV marketplace.json=$MV"; c5_status=FAIL
else
  echo "  PASS  both at $PV"
fi
row "Version sync" "$c5_status"

# ---------------------------------------------------------------------------
# Check 6 — Catalog drift (skills dirs + agent basenames mentioned in CLAUDE.md)
# ---------------------------------------------------------------------------
head_check 6 "Catalog drift (CLAUDE.md mentions every skill dir + agent)"
c6_status=PASS
for d in skills/*/; do
  [ -d "$d" ] || continue
  base="$(basename "$d")"
  if ! grep -qF "$base" CLAUDE.md; then
    echo "  FAIL  skill '$base' not mentioned in CLAUDE.md"; c6_status=FAIL
  fi
done
for ag in agents/*.md; do
  [ -f "$ag" ] || continue
  base="$(basename "$ag" .md)"
  if ! grep -qF "$base" CLAUDE.md; then
    echo "  FAIL  agent '$base' not mentioned in CLAUDE.md"; c6_status=FAIL
  fi
done
[ "$c6_status" = PASS ] && echo "  PASS  every skill dir and agent is referenced in CLAUDE.md"
row "Catalog drift" "$c6_status"

# ---------------------------------------------------------------------------
# Check 7 — Verifier sync (verdict invariant + tail-line grammar)
# ---------------------------------------------------------------------------
head_check 7 "Verifier sync (invariant + tail-line grammar, producers + consumers)"
c7_status=PASS
INVARIANT='Overall Score ≥ 90 **AND** P0 count == 0'
LOOP_GRAMMAR='ASTRA_LOOP_RESULT: score=N verdict=PASS|FAIL p0=N iter=I'
SCREEN_GRAMMAR='ASTRA_SCREEN_RESULT: score=N verdict=PASS|FAIL p0=N iter=I'

for vf in agents/loop-verifier.md agents/screen-verifier.md; do
  if ! grep -qF "$INVARIANT" "$vf"; then
    echo "  FAIL  $vf missing verdict invariant: $INVARIANT"; c7_status=FAIL
  fi
done
grep -qF "$LOOP_GRAMMAR"   agents/loop-verifier.md   || { echo "  FAIL  agents/loop-verifier.md missing tail grammar: $LOOP_GRAMMAR"; c7_status=FAIL; }
grep -qF "$SCREEN_GRAMMAR" agents/screen-verifier.md || { echo "  FAIL  agents/screen-verifier.md missing tail grammar: $SCREEN_GRAMMAR"; c7_status=FAIL; }

# Consumers must carry a grammar-bearing RESULT line (tolerant of N vs [0-9]+ forms).
consumer_has() { # <file> <prefix>
  grep -Eq "$2: score=[^ ]+ verdict=[^ ]+ p0=[^ ]+ iter=" "$1"
}
consumer_has skills/loop/SKILL.md                       ASTRA_LOOP_RESULT   || { echo "  FAIL  skills/loop/SKILL.md missing ASTRA_LOOP_RESULT grammar"; c7_status=FAIL; }
consumer_has skills/screen-quality-loop/SKILL.md        ASTRA_SCREEN_RESULT || { echo "  FAIL  skills/screen-quality-loop/SKILL.md missing ASTRA_SCREEN_RESULT grammar"; c7_status=FAIL; }
consumer_has skills/sprint-init/references/auto-pipeline.md ASTRA_LOOP_RESULT || { echo "  FAIL  auto-pipeline.md missing ASTRA_LOOP_RESULT grammar"; c7_status=FAIL; }
consumer_has skills/autorun/SKILL.md                    ASTRA_LOOP_RESULT   || { echo "  FAIL  skills/autorun/SKILL.md missing ASTRA_LOOP_RESULT grammar"; c7_status=FAIL; }
[ "$c7_status" = PASS ] && echo "  PASS  verifiers + consumers share the invariant and tail-line grammar"
row "Verifier sync" "$c7_status"

# ---------------------------------------------------------------------------
# Check 8 — Contract-line inventory (ASTRA_TEST_RESULT skipped= field)
# ---------------------------------------------------------------------------
head_check 8 "Contract-line inventory (ASTRA_TEST_RESULT producer + skipped=)"
c8_status=PASS
PRODUCER='ASTRA_TEST_RESULT: $RESULT passed=$PASSED failed=$FAILED total=$TOTAL skipped=$SKIPPED'
grep -qF "$PRODUCER" skills/test-run/SKILL.md || { echo "  FAIL  skills/test-run/SKILL.md missing producer echo: $PRODUCER"; c8_status=FAIL; }
for cf in skills/sprint-init/references/auto-pipeline.md skills/autorun/SKILL.md; do
  if ! grep -q 'ASTRA_TEST_RESULT' "$cf"; then
    echo "  FAIL  $cf does not mention ASTRA_TEST_RESULT"; c8_status=FAIL
  elif ! grep -q 'skipped=' "$cf"; then
    echo "  FAIL  $cf mentions ASTRA_TEST_RESULT but omits skipped="; c8_status=FAIL
  fi
done
[ "$c8_status" = PASS ] && echo "  PASS  producer + consumers all carry the skipped= field"
row "Contract-line inventory" "$c8_status"

# ---------------------------------------------------------------------------
# Check 9 — zsh-safety smell (bash-isms inside code fences, non-comment lines)
# ---------------------------------------------------------------------------
head_check 9 "zsh-safety smell (ls -td / ls -d .* / mapfile / readarray in code)"
c9_status=PASS
SMELLS="$(find skills commands agents -name '*.md' 2>/dev/null -exec awk '
  FNR==1 { infence=0 }
  /^[[:space:]]*```/ { infence=!infence; next }
  infence && $0 !~ /^[[:space:]]*#/ && \
    ($0 ~ /ls -d \.\* 2>\/dev\/null/ || $0 ~ /ls -td/ || $0 ~ /mapfile/ || $0 ~ /readarray/) {
      printf "%s:%d:%s\n", FILENAME, FNR, $0
  }
' {} +)"
if [ -n "$SMELLS" ]; then
  printf '%s\n' "$SMELLS" | while IFS= read -r line; do echo "  FAIL  $line"; done
  c9_status=FAIL
else
  echo "  PASS  no zsh-unsafe bash-isms in executable code fences"
fi
row "zsh-safety smell" "$c9_status"

# ---------------------------------------------------------------------------
# Check 10 — Stale-flow phrases (WARN only)
# ---------------------------------------------------------------------------
head_check 10 "Stale-flow phrases (worktree-first / 5-pass auto-debug)"
c10_status=PASS
STALE="$(grep -rnE 'worktree-first|5-pass auto-debug' skills/ 2>/dev/null)"
if [ -n "$STALE" ]; then
  printf '%s\n' "$STALE" | while IFS= read -r line; do echo "  WARN  $line"; done
  c10_status=WARN
else
  echo "  PASS  no stale-flow phrases"
fi
row "Stale-flow phrases" "$c10_status"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
hr
printf '  %-6s %s\n' "STATUS" "CHECK"
hr
for r in "${ROWS[@]}"; do
  st="${r%%|*}"; nm="${r#*|}"
  printf '  %-6s %s\n' "$st" "$nm"
done
hr

if [ "$FAILN" -gt 0 ]; then
  VERDICT=FAIL
else
  VERDICT=PASS
fi
echo ""
echo "ASTRA_LINT_RESULT: $VERDICT fail=$FAILN warn=$WARNN"

[ "$VERDICT" = PASS ] && exit 0 || exit 1
