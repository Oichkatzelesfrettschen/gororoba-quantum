#!/bin/sh
# E8-bar -> N- at N = 16, p = 32029, degree 5: fills the per-block cell missing at the second prime.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/n16-p2.events
mkdir -p out
run() {
    p=$1 d=$2
    echo "$(date -u +%FT%TZ) start p=$p d=$d" >> "$ev"
    if /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/e8nm_d${d}_n16_p$p.time" \
        "$PYTHON" fiber_rank_v11.py "$HOME/a5/engine/v9m/e8-nm-p$p.sing" "$d" 16 --quotient \
        --export-dir "$HOME/a5/exports/e8nm-p$p-n16-v11" --export-chunks 4 \
        --k2-receipt "$HOME/a5/engine/v10/k2/p$p/receipt-d2.json" --max-gb 50 \
        > "out/e8nm_d${d}_n16_p$p.json" 2> "out/e8nm_d${d}_n16_p$p.err"; then
        echo "$(date -u +%FT%TZ) exit 0 p=$p d=$d r=$("$PYTHON" -c 'import json,sys;print(json.load(open(sys.argv[1]))["r_N"])' "out/e8nm_d${d}_n16_p$p.json")" >> "$ev"
    else
        echo "$(date -u +%FT%TZ) exit $? p=$p d=$d" >> "$ev"
        return 1
    fi
}
run 32029 5
echo "$(date -u +%FT%TZ) done" >> "$ev"
