#!/bin/sh
# W8 -> N- degree 6 at N = 19, p = 32009: engine v11 quotient mode with the degree-2 receipt (6e464db6...). --max-gb 1
# stops after the degree-independent Singular export and prints the selected-array estimate, the preflight figure that
# sizes the full rank run; the export in exports/w8nm-p32009-n19-v11 is kept for that run to reuse.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=8
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/w8d6.events
echo "$(date -u +%FT%TZ) start w8 d=6 N=19 export probe" >> "$ev"
rc=0
/usr/bin/time -f "wall %e s maxrss %M KiB" -o out/w8nm_d6_n19_p32009.time \
    timeout 43200 "$PYTHON" fiber_rank_v11.py w8p1/w8-nm.sing 6 19 --quotient \
    --export-dir "$HOME/a5/exports/w8nm-p32009-n19-v11" --export-chunks 5 \
    --k2-receipt w8p1/receipt-d2.json --max-gb 1 \
    > out/w8nm_d6_n19_p32009.json 2> out/w8nm_d6_n19_p32009.err < /dev/null || rc=$?
echo "$(date -u +%FT%TZ) exit $rc w8 d=6 N=19 export probe" >> "$ev"
