#!/bin/sh
# The induced slice map of E8-bar -> N+- over Q(i) and its reduction checks; run from the repository root.
# Needs Singular on PATH and sympy and python-flint in $PYTHON. Exits nonzero unless both records pass and all six
# reduction checks print their PASS verdict.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-induced-slice-map
W=docs/evidence/a5-exceptional-fibers/working
K=$W/runs/e8-rees-fibers-v2-kcompare-p32009
T=docs/evidence/a5-exceptional-fibers/third-prime
sing() {
  Singular -q --no-warn --no-rc "$1" < /dev/null > "$2" 2>&1
  if grep -q '^ *?' "$2"; then
    echo "run_induced: Singular error line in $2" >&2
    exit 1
  fi
}
for t in nm np; do
  o=N-
  [ "$t" = np ] && o=N+
  for mode in map relations; do
    "$PYTHON" "$D/induced_slice_map.py" --emit "$o" 0 0 "$mode" > "$D/$mode-$t-qi.sing"
    sing "$D/$mode-$t-qi.sing" "$D/$mode-$t-qi.log"
  done
  "$PYTHON" "$D/induced_slice_map.py" --emit "$o" 0 0 high > "$D/high-$t-qi.sing"
  sing "$D/high-$t-qi.sing" "$D/high-$t-qi.log"
  grep -q '^RESULT header_high_weight_outside 0$' "$D/high-$t-qi.log"
  "$PYTHON" "$D/induced_slice_map.py" --collect "$D/map-$t-qi.log" "$D/relations-$t-qi.log" "$o" "$D/induced-$t.json"
done
check() { # cell prime root header-relations [weight-relations]
  s="$D/check-$1-p$2-r$3"
  "$PYTHON" "$D/induced_slice_map.py" --check "$D/induced-$1.json" "$2" "$3" "$4" ${5:-} > "$s.sing"
  sing "$s.sing" "$s.log"
  grep -q "^INDUCED VERDICT p $2 root $3 PASS$" "$s.log"
}
R3=$(sed -n 's/^number I=\([0-9]*\);$/\1/p' "$T/inputs/p32057-r8059/e8-nm.sing")
check nm 32009 10754 "$K/KH-e8-nm.sing" "$K/KA-e8-nm.sing"
check np 32009 10754 "$K/KH-e8-np.sing" "$K/KA-e8-np.sing"
check np 32009 21255 "$W/runs/e8np-d2-receipt-p32009-r21255/KH-e8-np-r21255.sing"
check nm 32029 9115 "$W/distribute/out/a5-e8-d2/e8nm_p2/d2/relations-upto-d2.rel"
check np 32029 9115 "$W/distribute/out/a5-e8-d2/e8np_p2/d2/relations-upto-d2.rel"
check nm 32057 "$R3" "$T/relations/e8-nm/d2/relations-upto-d2.rel"
echo "run_induced: PASS"
