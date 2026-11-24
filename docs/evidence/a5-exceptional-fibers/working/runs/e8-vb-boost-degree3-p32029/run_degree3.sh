#!/bin/sh
# Degree-3 relation counts of E8-bar -> VB along the boost at the A5-600 sample values of w, modulo 32029; run from the
# repository root with Singular on PATH and sympy and python-flint in $PYTHON. Each value takes about 37 min on one
# core; JOBS (default 4) values run at once. With the argument check it reads the retained logs instead of running
# Singular, after requiring each retained script to equal a fresh emission. Exits nonzero unless every value reports 220
# targets and 140 relations, and the count check rejects a log whose relation count is altered.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-vb-boost-degree3-p32029
JOBS=${JOBS:-4}
VALUES="1 2 3 2/3 5 7 11 -3 1/4 1000 12345 9115"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
tag() { echo "w$1" | tr '/-' 'dm'; }
counted() { # log: 0 when the log shows 220 targets, 140 relations and a finished run
  grep -q '^RESULT targets 220$' "$1" && grep -q '^RESULT relations 140$' "$1" && grep -q '^RESULT done 1$' "$1"
}
for v in $VALUES; do
  "$PYTHON" "$D/boost_degree3.py" --emit "$v" > "$scratch/d3-$(tag "$v").sing"
  if [ "${1:-}" = check ]; then cmp "$scratch/d3-$(tag "$v").sing" "$D/d3-$(tag "$v").sing"; fi
done
if [ "${1:-}" != check ]; then
  for v in $VALUES; do cp "$scratch/d3-$(tag "$v").sing" "$D/"; done
  # shellcheck disable=SC2016
  printf '%s\n' $VALUES | xargs -P "$JOBS" -I{} sh -c 't=$(echo "w{}" | tr "/-" "dm"); Singular -q --no-warn --no-rc "$1/d3-$t.sing" < /dev/null > "$1/d3-$t.log" 2>&1' _ "$D"
fi
: > "$D/counts.txt"
for v in $VALUES; do
  t=$(tag "$v")
  counted "$D/d3-$t.log"
  echo "$v $(grep '^RESULT targets' "$D/d3-$t.log" | cut -d' ' -f3) $(grep '^RESULT relations' "$D/d3-$t.log" | cut -d' ' -f3)" >> "$D/counts.txt"
done
sed 's/^RESULT relations 140$/RESULT relations 139/' "$D/d3-w2.log" > "$scratch/mutant.log"
if counted "$scratch/mutant.log"; then
  echo "run_degree3: the count check accepted an altered log" >&2
  exit 1
fi
echo "run_degree3: PASS"
