#!/bin/sh
# X- -> N- degree 6, engine v11 quotient mode, raw, p = 32009, at the N values given as arguments (in order).
# Tests the closing-order hypothesis N = floor(7d/2) + 1 = 22 (plateau at N = 20, 21; target HF(k[y]/K2, 6) = 665,
# last jump 169 split 49/42/39/39 under ledger row A5-244). Each run records its exit in out/xm6.events; the runner
# exits with the first nonzero engine status.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=8
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/xm6.events
for n in "$@"; do
    echo "$(date -u +%FT%TZ) start xm d=6 N=$n p=32009 raw" >> "$ev"
    rc=0
    /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/xmnm_d6_n${n}_p32009.time" \
        timeout 43200 "$PYTHON" fiber_rank_v11.py xmp1/xm-nm.sing 6 "$n" --quotient \
        --export-dir "$HOME/a5/exports/xmnm-p32009-n$n-v11" --export-chunks 5 --dense-tables-gb 0 --max-gb 47 \
        > "out/xmnm_d6_n${n}_p32009.json" 2> "out/xmnm_d6_n${n}_p32009.err" < /dev/null || rc=$?
    echo "$(date -u +%FT%TZ) exit $rc xm d=6 N=$n p=32009" >> "$ev"
    [ "$rc" -eq 0 ] || exit "$rc"
done
