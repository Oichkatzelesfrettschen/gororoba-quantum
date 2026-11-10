#!/bin/sh
# W8 -> N- degree 5 at N = 16, p = 32029: engine v11 quotient mode restricted to the standard monomials of k[y]/K2 by
# the second prime's degree-2 membership receipt, passagemath Singular 4.4.1, export kept on disk, four workers.
set -eu
cd "$HOME/a5"
PYTHON="$HOME/venv/bin/python"
SING=$(ls "$HOME"/pmvenv/lib/python3*/site-packages/sage_wheels/bin/Singular)
export PYTHON GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=4 MALLOC_ARENA_MAX=2
"$SING" --version > out/singular-version.txt 2>&1 || true
( while :; do echo "$(date -u +%FT%TZ) $(ps -o rss= -C python3 | awk '{s+=$1} END {print s}') $(ps -o rss= -C Singular | awk '{s+=$1} END {print s}')" >> out/rss.txt; sleep 60; done ) &
sampler=$!
rc=0
/usr/bin/time -v timeout 21600 "$PYTHON" engine/fiber_rank_v11.py --quotient --max-gb 70 --singular "$SING" \
  --k2-receipt receipt-w8/receipt-d2.json --export-dir "$HOME/a5/exports/w8nm-n16-p32029" \
  inputs/w8-nm.sing 5 16 > out/w8d5-n16-p32029.out 2> out/w8d5-n16-p32029.err < /dev/null || rc=$?
kill "$sampler" 2>/dev/null || true
echo "$(date -u +%FT%TZ) w8 p32029 n16 exit $rc" >> out/events
exit "$rc"
