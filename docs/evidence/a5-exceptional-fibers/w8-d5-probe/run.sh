#!/bin/sh
# W8 -> N- degree-5 truncated-rank cost probe at small N (build host) to size a cloud run.
set -eu
PYTHON=${PYTHON:-$HOME/.cache/gororoba-quantum/ci-py3.14.7-qiskit261/bin/python}
export PYTHON GOROROBA_WORKERS=4
H=docs/evidence/a5-exceptional-fibers/working/build/inputs/p32009-r10754/w8-nm.sing
D=docs/local/w8-d5-probe
for N in ${NS:-10 11 12}; do
  /usr/bin/time -v timeout 21600 "$PYTHON" docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v11.py \
    --quotient --max-gb 34 "$H" 5 "$N" > "$D/n$N.out" 2> "$D/n$N.err" || echo "n$N exit $?" >> "$D/events"
  echo "n$N done" >> "$D/events"
done
echo "all done" >> "$D/events"
