#!/bin/sh
# The induced slice map of X- -> N- and X+ -> N+ over Q(i) and its reduction checks; run from the repository root.
# Needs Singular on PATH and sympy and python-flint in $PYTHON. Exits nonzero unless both records pass, all six
# reduction checks print their PASS verdict and all six reductions at the other root of -1 print FAIL with nonzero
# remainders in both directions. The runs of each stage go through parallel.ordered_map.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
exec "$PYTHON" docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map/x_induced_slice_map.py --run
