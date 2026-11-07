#!/bin/sh
# E8-bar -> N- at N = 17 with merged engine v11: p = 32009 degree 5 (std of J + m^17 and tables exported), the
# degree-4 control on the same export (must give r 495), then p = 32029 degree 5 only when p = 32009 reaches 952.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/n17.events
mkdir -p out
run() {
    p=$1 d=$2
    echo "$(date -u +%FT%TZ) start p=$p d=$d" >> "$ev"
    if /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/e8nm_d${d}_n17_p$p.time" \
        "$PYTHON" fiber_rank_v11.py "$HOME/a5/engine/v9m/e8-nm-p$p.sing" "$d" 17 --quotient \
        --export-dir "$HOME/a5/exports/e8nm-p$p-n17-v11" --export-chunks 5 \
        --k2-receipt "$HOME/a5/engine/v10/k2/p$p/receipt-d2.json" --max-gb 50 \
        > "out/e8nm_d${d}_n17_p$p.json" 2> "out/e8nm_d${d}_n17_p$p.err"; then
        echo "$(date -u +%FT%TZ) exit 0 p=$p d=$d r=$("$PYTHON" -c 'import json,sys;print(json.load(open(sys.argv[1]))["r_N"])' "out/e8nm_d${d}_n17_p$p.json")" >> "$ev"
    else
        echo "$(date -u +%FT%TZ) exit $? p=$p d=$d" >> "$ev"
        return 1
    fi
}
run 32009 5
run 32009 4
r4=$("$PYTHON" -c 'import json,sys;print(json.load(open(sys.argv[1]))["r_N"])' "out/e8nm_d4_n17_p32009.json")
[ "$r4" = 495 ] || { echo "$(date -u +%FT%TZ) control failed: d=4 r=$r4, expected 495" >> "$ev"; exit 1; }
r5=$("$PYTHON" -c 'import json,sys;print(json.load(open(sys.argv[1]))["r_N"])' "out/e8nm_d5_n17_p32009.json")
if [ "$r5" = 952 ]; then run 32029 5; else echo "$(date -u +%FT%TZ) p=32029 skipped: p=32009 d=5 r=$r5 below 952" >> "$ev"; fi
echo "$(date -u +%FT%TZ) done" >> "$ev"
