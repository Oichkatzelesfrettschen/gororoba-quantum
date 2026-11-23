#!/bin/sh
# Stability of the degree-5 span of the ten-Pfaffians of C(z) under linear vector fields, modulo 32009 and over
# Q(i); with the argument algebra, the stabilizer algebras modulo 32009 as well. Run from the repository root with
# Singular on PATH and sympy in $PYTHON. Exits nonzero unless both stability logs carry the expected RESULT lines
# and no log holds a Singular error line.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability
A=docs/evidence/a5-kernel-attachments
gate() { # log: no Singular error line, a terminal marker, the expected RESULT lines
  if grep -q '^ *?' "$D/$1"; then
    echo "run_stability: Singular error line in $1" >&2
    exit 1
  fi
  grep -q '^RESULT done 1$' "$D/$1"
  grep '^RESULT' "$D/$1" | cmp -s - "$D/expected-results.txt"
}
"$PYTHON" "$D/derivation_stability.py" "$A" 32009 10754 > "$D/stab-p32009.sing"
"$PYTHON" "$D/derivation_stability.py" "$A" 0 0 > "$D/stab-qi.sing"
Singular -q --no-warn --no-rc "$D/stab-p32009.sing" > "$D/stab-p32009.log" < /dev/null
Singular -q --no-warn --no-rc "$D/stab-qi.sing" > "$D/stab-qi.log" < /dev/null
gate stab-p32009.log
gate stab-qi.log
if [ "${1:-}" = algebra ]; then
  "$PYTHON" "$D/derivation_stability.py" "$A" 32009 10754 alg w8,iso > "$D/alg-p32009.sing"
  Singular -q --no-warn --no-rc "$D/alg-p32009.sing" > "$D/alg-p32009.log" < /dev/null
  if grep -q '^ *?' "$D/alg-p32009.log"; then
    echo "run_stability: Singular error line in alg-p32009.log" >&2
    exit 1
  fi
  grep -q '^RESULT algebra w8 closure_stabilizer 59 pair_stabilizer 31 boost_inside 1$' "$D/alg-p32009.log"
  grep -q '^RESULT algebra iso closure_stabilizer 40 pair_stabilizer 31 boost_inside 1$' "$D/alg-p32009.log"
fi
echo "run_stability: ok"
