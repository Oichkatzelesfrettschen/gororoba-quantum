#!/bin/sh
# E8-bar -> N- at N = 18 with engine v11, the flags of run-n17.sh with N = 18 only (quotient mode, --k2-receipt on the
# degree-2 receipt of each prime, 5 export chunks, --max-gb 50). It starts after the v8 replay unit has finished so
# the laptop carries one heavy job. Checks after each degree-5 run: every block at or above its N = 17 value
# (197, 176, 249, 249), at or below its K2 count (215, 197, 270, 270), and block 2 equal to block 3. p = 32029 runs
# runs next, here, only when p = 32009 moved off the N = 17 blocks with every invariant intact (the gate).
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/n18.events
mkdir -p out
while systemctl --user is-active --quiet a5-replay-e8n15-p1; do sleep 300; done
echo "$(date -u +%FT%TZ) replay unit finished; laptop free" >> "$ev"
"$SINGULAR" --version < /dev/null > out/n18-singular-version.txt 2>&1 || true
run() {
    p=$1 d=$2
    echo "$(date -u +%FT%TZ) start p=$p d=$d" >> "$ev"
    if /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/e8nm_d${d}_n18_p$p.time" \
        "$PYTHON" fiber_rank_v11.py "$HOME/a5/engine/v9m/e8-nm-p$p.sing" "$d" 18 --quotient \
        --export-dir "$HOME/a5/exports/e8nm-p$p-n18-v11" --export-chunks 5 \
        --k2-receipt "$HOME/a5/engine/v10/k2/p$p/receipt-d2.json" --max-gb 50 \
        > "out/e8nm_d${d}_n18_p$p.json" 2> "out/e8nm_d${d}_n18_p$p.err" < /dev/null; then
        echo "$(date -u +%FT%TZ) exit 0 p=$p d=$d r=$("$PYTHON" -c "import json,sys;print(json.load(open(sys.argv[1]))[\"r_N\"])" "out/e8nm_d${d}_n18_p$p.json")" >> "$ev"
    else
        echo "$(date -u +%FT%TZ) exit $? p=$p d=$d" >> "$ev"
        return 1
    fi
}
check() {
    "$PYTHON" - "out/e8nm_d5_n18_p$1.json" <<"PY"
import json, sys
b = [json.load(open(sys.argv[1]))["per_block"][str(i)]["r_N"] for i in range(4)]
low, up = (197, 176, 249, 249), (215, 197, 270, 270)
bad = [f"block {i} {b[i]} below N=17 {low[i]}" for i in range(4) if b[i] < low[i]]
bad += [f"block {i} {b[i]} above K2 {up[i]}" for i in range(4) if b[i] > up[i]]
bad += [f"blocks 2,3 differ {b[2]} {b[3]}"] if b[2] != b[3] else []
print("blocks", *b, "moved" if tuple(b) != low else "flat", *(["INVARIANT " + x for x in bad] or ["invariants ok"]))
PY
}
run 32009 5
echo "$(date -u +%FT%TZ) p=32009 $(check 32009)" >> "$ev"
run 32009 4
r4=$("$PYTHON" -c "import json,sys;print(json.load(open(sys.argv[1]))[\"r_N\"])" "out/e8nm_d4_n18_p32009.json")
[ "$r4" = 495 ] || { echo "$(date -u +%FT%TZ) control failed: d=4 r=$r4, expected 495" >> "$ev"; exit 1; }
if grep -q "p=32009 blocks .* moved invariants ok" "$ev"; then
    run 32029 5
    echo "$(date -u +%FT%TZ) p=32029 $(check 32029)" >> "$ev"
else
    echo "$(date -u +%FT%TZ) p=32029 skipped: p=32009 flat or an invariant failed" >> "$ev"
fi
echo "$(date -u +%FT%TZ) done" >> "$ev"
