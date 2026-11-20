#!/bin/sh
# Degree 5 of E8-bar -> N- at N = 15 with engine v10 on the merged-v9 N = 15 exports, after the reproductions finish:
# p = 32009 degree 5, p = 32009 degree 4 (must equal blocks 158, 137, 100, 100), then p = 32029 degree 5.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v10"
ev=out/d5.events
mkdir -p out
while systemctl --user is-active -q a5-v9m-e8nm-n15-repro; do sleep 300; done
echo "$(date -u +%FT%TZ) reproductions ended: $(cat "$HOME/a5/engine/v9m/out/repro.events" | tr '\n' ' ')" >> "$ev"
run() {
    p=$1 d=$2
    echo "$(date -u +%FT%TZ) start p=$p d=$d" >> "$ev"
    /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/e8nm_d${d}_n15_p$p.time" \
        "$PYTHON" fiber_rank_v10.py "$HOME/a5/engine/v9m/e8-nm-p$p.sing" "$d" 15 --quotient \
        --export-dir "$HOME/a5/exports/e8nm-p$p-n15-v9m" --k2-receipt "k2/p$p/receipt-d2.json" --max-gb 50 \
        > "out/e8nm_d${d}_n15_p$p.json" 2> "out/e8nm_d${d}_n15_p$p.err" \
        && echo "$(date -u +%FT%TZ) exit 0 p=$p d=$d" >> "$ev" || echo "$(date -u +%FT%TZ) exit $? p=$p d=$d" >> "$ev"
}
run 32009 5
run 32009 4
run 32029 5
echo "$(date -u +%FT%TZ) done" >> "$ev"
