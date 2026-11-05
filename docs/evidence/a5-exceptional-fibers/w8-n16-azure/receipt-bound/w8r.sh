#!/bin/sh
# W8 -> N- degree 5 at N = 16, p = 32009, engine v11 quotient mode restricted to the standard monomials of k[y]/K2 by
# the degree-2 membership receipt (4,116 representatives instead of 98,280 products, nonstandard products inserted
# after the rank as the check), passagemath Singular 4.4.1, export kept on disk. Runs beside the Iso radical: two
# export workers, so the two physical cores carry the Iso Singular and this engine.
set -eu
cd "$HOME/a5"
PYTHON="$HOME/venv/bin/python"
SING="$HOME/pmvenv/lib/python3.12/site-packages/sage_wheels/bin/Singular"
export PYTHON GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=2 MALLOC_ARENA_MAX=2
rc=0
/usr/bin/time -v timeout 43200 "$PYTHON" engine/fiber_rank_v11.py --quotient --max-gb 70 --singular "$SING" \
  --k2-receipt receipt-w8/receipt-d2.json --export-dir "$HOME/a5/exports/w8nm-n16-rcpt" \
  inputs/w8-nm.sing 5 16 > out/w8d5-n16-rcpt.out 2> out/w8d5-n16-rcpt.err < /dev/null || rc=$?
echo "w8r n16 exit $rc" >> out/events
