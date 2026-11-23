#!/bin/sh
# Invariants of five retained quadric ideals in Macaulay2; run from the repository root with M2 on PATH.
# Exits nonzero unless the RESULT lines equal expected-results.txt.
set -eu
D=docs/evidence/a5-exceptional-fibers/working/runs/quadric-ideals-macaulay2-p32009
K=docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-kcompare-p32009
M2 --version > "$D/m2-version.txt"
[ "$(cat "$D/m2-version.txt")" = 1.25.11 ]
for c in "KA-e8-nm 21" "KA-e8-np 21" "KH-e8-nm 21" "KH-e8-np 21" "KA-iso-nm 17"; do
  set -- $c
  M2 --script "$D/quadric_invariants.m2" "$1" "$K/$1.sing" "$2" > "$D/$1.log" 2>&1
done
cat "$D"/KA-e8-nm.log "$D"/KA-e8-np.log "$D"/KH-e8-nm.log "$D"/KH-e8-np.log "$D"/KA-iso-nm.log | grep -E '^(RESULT|DONE) ' > "$D/results.txt"
cmp "$D/results.txt" "$D/expected-results.txt"
echo "run_m2: PASS"
