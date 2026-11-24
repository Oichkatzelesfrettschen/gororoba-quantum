#!/bin/sh
# Macaulay2 invariants of the W8 -> N- quadric ideal modulo 32009 and of the six Q(i) quadric ideals of the
# weight-slice fiber cones; run from the repository root with M2 on PATH. With the argument dump it first rewrites the
# Q(i) ideal files through qi_quadric_ideals.py (needs Singular and sympy in $PYTHON) and requires the same file names.
# Exits nonzero unless the RESULT lines equal expected-results.txt and a copy with one relation removed is detected.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/quadric-ideals-macaulay2-w8-qi
P=docs/evidence/a5-exceptional-fibers/working/runs/quadric-ideals-macaulay2-p32009
W=docs/evidence/a5-exceptional-fibers/working/runs/w8_a2/w8_k2.rel
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
M2 --version > "$D/m2-version.txt"
[ "$(cat "$D/m2-version.txt")" = 1.25.11 ]
if [ "${1:-}" = dump ]; then
  ls "$D"/qi-g*.txt | sed 's|.*/||' > "$scratch/before"
  "$PYTHON" "$D/qi_quadric_ideals.py" "$scratch/dump" > /dev/null
  ls "$scratch/dump" > "$scratch/after"
  cmp "$scratch/before" "$scratch/after"
  for f in $(cat "$scratch/after"); do cmp "$D/$f" "$scratch/dump/$f"; done
fi
M2 --script "$P/quadric_invariants.m2" W8-nm-p32009 "$W" 24 > "$D/W8-nm-p32009.log" 2>&1
names=W8-nm-p32009
for f in "$D"/qi-g*.txt; do
  b=$(basename "$f" .txt)
  M2 --script "$D/qi_invariants.m2" "$b" "$f" > "$D/$b.log" 2>&1
  names="$names $b"
done
: > "$D/results.txt"
for b in $names; do grep -E '^(RESULT|DONE) ' "$D/$b.log" >> "$D/results.txt"; done
cmp "$D/results.txt" "$D/expected-results.txt"
# Known-bad input: the first Iso ideal without its last relation must report 67 generators, not 68.
iso=$(ls "$D"/qi-g17-*.txt | head -n 1)
n=$(($(wc -l < "$iso") - 1))
head -n "$n" "$iso" > "$scratch/mutant.txt"
M2 --script "$D/qi_invariants.m2" mutant "$scratch/mutant.txt" > "$scratch/mutant.log" 2>&1 || true
grep -q '^RESULT mutant K generators 67 ' "$scratch/mutant.log"
grep -q '^DONE mutant$' "$scratch/mutant.log"
echo "run_m2_qi: PASS"
