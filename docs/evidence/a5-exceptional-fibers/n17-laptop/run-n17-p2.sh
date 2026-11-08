#!/bin/sh
# E8-bar -> N- degree 5 at N = 17, p = 32029, beside the p = 32009 run: the std and tables (--export-only, a few hundred
# MB) run at once; the products wait until unit a5-v11-e8nm-n17 has finished so two product stages never share RAM.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/n17-p2.events
p=32029
args="$HOME/a5/engine/v9m/e8-nm-p$p.sing 5 17 --quotient --export-dir $HOME/a5/exports/e8nm-p$p-n17-v11 --export-chunks 5 --k2-receipt $HOME/a5/engine/v10/k2/p$p/receipt-d2.json --max-gb 50"
echo "$(date -u +%FT%TZ) start export p=$p" >> "$ev"
# shellcheck disable=SC2086
"$PYTHON" fiber_rank_v11.py $args --export-only > out/e8nm_export_n17_p$p.json 2> out/e8nm_export_n17_p$p.err \
    || { echo "$(date -u +%FT%TZ) export exit $? p=$p" >> "$ev"; exit 1; }
echo "$(date -u +%FT%TZ) export done p=$p; waiting for a5-v11-e8nm-n17" >> "$ev"
while systemctl --user is-active -q a5-v11-e8nm-n17; do sleep 300; done
echo "$(date -u +%FT%TZ) start products p=$p" >> "$ev"
# shellcheck disable=SC2086
if /usr/bin/time -f "wall %e s maxrss %M KiB" -o out/e8nm_d5_n17_p$p.time "$PYTHON" fiber_rank_v11.py $args \
    > out/e8nm_d5_n17_p$p.json 2> out/e8nm_d5_n17_p$p.err; then
    echo "$(date -u +%FT%TZ) exit 0 p=$p d=5 r=$("$PYTHON" -c 'import json,sys;print(json.load(open(sys.argv[1]))["r_N"])' out/e8nm_d5_n17_p$p.json)" >> "$ev"
else
    echo "$(date -u +%FT%TZ) exit $? p=$p d=5" >> "$ev"
fi
echo "$(date -u +%FT%TZ) done" >> "$ev"
