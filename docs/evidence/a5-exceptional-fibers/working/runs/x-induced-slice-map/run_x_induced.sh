#!/bin/sh
# The induced slice map of X- -> N- and X+ -> N+ over Q(i) and its reduction checks; run from the repository root.
# Needs Singular on PATH and sympy and python-flint in $PYTHON. Exits nonzero unless both records pass, all six
# reduction checks print their PASS verdict and all six reductions at the other root of -1 print FAIL.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map
W=docs/evidence/a5-exceptional-fibers/working
T=docs/evidence/a5-exceptional-fibers/third-prime
sing() {
  Singular -q --no-warn --no-rc "$1" < /dev/null > "$2" 2>&1
  if grep -q '^ *?' "$2"; then
    echo "run_x_induced: Singular error line in $2" >&2
    exit 1
  fi
}
for s in xm xp; do
  for mode in map relations high; do
    "$PYTHON" "$D/x_induced_slice_map.py" --emit "$s" 0 0 "$mode" > "$D/$mode-$s-qi.sing"
    sing "$D/$mode-$s-qi.sing" "$D/$mode-$s-qi.log"
  done
  grep -q '^RESULT header_high_weight_outside 0$' "$D/high-$s-qi.log"
  "$PYTHON" "$D/x_induced_slice_map.py" --collect "$D/map-$s-qi.log" "$D/relations-$s-qi.log" "$s" "$D/induced-$s.json"
done
check() { # source prime root header-relations
  c="$D/check-$1-p$2-r$3"
  "$PYTHON" "$D/x_induced_slice_map.py" --check "$D/induced-$1.json" "$2" "$3" "$4" > "$c.sing"
  sing "$c.sing" "$c.log"
  grep -q "^INDUCED VERDICT p $2 root $3 PASS$" "$c.log"
}
refute() { # source prime other-root header-relations: the reduction at the conjugate root must differ
  c="$D/control-$1-p$2-r$3"
  "$PYTHON" "$D/x_induced_slice_map.py" --check "$D/induced-$1.json" "$2" "$3" "$4" > "$c.sing"
  sing "$c.sing" "$c.log"
  grep -q "^INDUCED VERDICT p $2 root $3 FAIL\$" "$c.log"
  if grep -q "^RESULT transported modulo header 0 header modulo transported 0\$" "$c.log"; then
    echo "run_x_induced: the conjugate root reproduces the header ideal in $c.log" >&2
    exit 1
  fi
}
for s in xm xp; do
  h1=$W/distribute/out/a5-xm-d4/xm_p1/d2
  h2=$W/distribute/out/a5-p2-small/${s}_p2/d2
  h3=$T/relations/xm-nm/d2
  if [ "$s" = xp ]; then
    h1=$W/distribute/out/a5-xp-p1-d2/xp_p1/d2
    h3=$T/relations/xp-np/d2
  fi
  check "$s" 32009 10754 "$h1/relations-upto-d2.rel"
  check "$s" 32029 9115 "$h2/relations-upto-d2.rel"
  check "$s" 32057 8059 "$h3/relations-upto-d2.rel"
  refute "$s" 32009 21255 "$h1/relations-upto-d2.rel"
  refute "$s" 32029 22914 "$h2/relations-upto-d2.rel"
  refute "$s" 32057 23998 "$h3/relations-upto-d2.rel"
done
echo "run_x_induced: PASS"
