#!/bin/sh
# E8-bar -> N- degree 4, N = 15 reproductions with merged engine v9: clean export at p = 32009, then p = 32029.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v9m"
ev=out/repro.events
for p in 32009 32029; do
    echo "$(date -u +%FT%TZ) start p=$p" >> "$ev"
    /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/e8nm_d4_n15_p$p.time" \
        "$PYTHON" fiber_rank_v9.py "e8-nm-p$p.sing" 4 15 --quotient --export-dir "$HOME/a5/exports/e8nm-p$p-n15-v9m" \
        --export-chunks 3 > "out/e8nm_d4_n15_p$p.json" 2> "out/e8nm_d4_n15_p$p.err" \
        && echo "$(date -u +%FT%TZ) exit 0 p=$p" >> "$ev" || echo "$(date -u +%FT%TZ) exit $? p=$p" >> "$ev"
done
