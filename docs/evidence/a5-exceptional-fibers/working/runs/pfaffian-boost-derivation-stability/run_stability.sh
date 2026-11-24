#!/bin/sh
# Stability of the degree-5 span of the ten-Pfaffians of C(z) under linear vector fields, modulo 32009 and over
# Q(i); with the argument algebra, the W8 and Iso stabilizer algebras modulo 32009 as well. Run from the repository
# root with Singular on PATH and sympy in $PYTHON. Exits nonzero unless both stability logs carry the expected
# RESULT lines and no log holds a Singular error line. The stability logs are rewritten with the bytes sha256.txt
# pins; the algebra path writes alg-w8-iso-p32009.* and leaves the retained five-closure alg-p32009.log alone.
# The two stability units run through gororoba_quantum/run_commands.py (parallel.ordered_map), the Q(i) unit first;
# GOROROBA_WORKERS caps the units running at once (default the available CPUs). A unit is
# "sh run_stability.sh unit STEM", where STEM is stab-p32009 or stab-qi.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability
A=docs/evidence/a5-kernel-attachments
sing() { # stem: run one generated script; the log ends with the exit line the retained logs carry
  rc=0
  Singular -q --no-warn --no-rc "$D/$1.sing" > "$D/$1.log" < /dev/null || rc=$?
  echo "EXIT $rc" >> "$D/$1.log"
  if grep -q '^ *?' "$D/$1.log"; then
    echo "run_stability: Singular error line in $1.log" >&2
    exit 1
  fi
  [ "$rc" -eq 0 ]
  grep -q '^RESULT done 1$' "$D/$1.log"
}
if [ "${1:-}" = unit ]; then
  case "$2" in
    stab-p32009) "$PYTHON" "$D/derivation_stability.py" "$A" 32009 10754 > "$D/$2.sing" ;;
    stab-qi) "$PYTHON" "$D/derivation_stability.py" "$A" 0 0 > "$D/$2.sing" ;;
    *) echo "run_stability: unknown unit $2" >&2; exit 2 ;;
  esac
  sing "$2"
  grep '^RESULT' "$D/$2.log" | cmp -s - "$D/expected-results.txt"
  exit 0
fi
me=$0
"$PYTHON" gororoba_quantum/run_commands.py "sh $me unit stab-qi" "sh $me unit stab-p32009"
if [ "${1:-}" = algebra ]; then
  "$PYTHON" "$D/derivation_stability.py" "$A" 32009 10754 alg w8,iso > "$D/alg-w8-iso-p32009.sing"
  sing alg-w8-iso-p32009
  grep -q '^RESULT algebra global dimension 15$' "$D/alg-w8-iso-p32009.log"
  grep -q '^RESULT algebra w8 closure_stabilizer 59 pair_stabilizer 31 boost_inside 1$' "$D/alg-w8-iso-p32009.log"
  grep -q '^RESULT algebra iso closure_stabilizer 40 pair_stabilizer 31 boost_inside 1$' "$D/alg-w8-iso-p32009.log"
fi
echo "run_stability: ok"
