#!/bin/sh
# W8 -> N- degree-5 truncated rank at N = 16, p = 32009: engine v11 quotient mode, passagemath Singular 4.4.1. The
# quotient products and closure are serial, so the 8-vCPU size is for its 168 GB of memory; --max-gb 130 clears the
# measured 97.8 GiB preflight with room below the VM.
set -eu
cd "$HOME/a5"
PYTHON="$HOME/venv/bin/python"
SING="$HOME/venv/lib/python3.12/site-packages/sage_wheels/bin/Singular"
export PYTHON GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=4 MALLOC_ARENA_MAX=2
"$SING" --version < /dev/null > out/singular-version.txt 2>&1 || true
rc=0
/usr/bin/time -v timeout 43200 "$PYTHON" engine/fiber_rank_v11.py --quotient --max-gb 130 --singular "$SING" \
  inputs/w8-nm.sing 5 16 > out/w8d5-n16.out 2> out/w8d5-n16.err < /dev/null || rc=$?
echo "w8 n16 exit $rc" >> out/events
echo "all done" >> out/events
