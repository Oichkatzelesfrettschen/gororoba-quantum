#!/bin/sh
# E8-bar -> N- degree-4 control at N = 18, p = 32029: the run-n18.sh flags for that single run (quotient mode,
# --k2-receipt on the p = 32029 degree-2 receipt, 5 export chunks, --max-gb 50). Prediction committed with the
# p = 32029 degree-5 run: r = 495.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/n18.events
p=32029 d=4
echo "$(date -u +%FT%TZ) start p=$p d=$d" >> "$ev"
if /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/e8nm_d${d}_n18_p$p.time" "$PYTHON" fiber_rank_v11.py "$HOME/a5/engine/v9m/e8-nm-p$p.sing" "$d" 18 --quotient --export-dir "$HOME/a5/exports/e8nm-p$p-n18-v11" --export-chunks 5 --k2-receipt "$HOME/a5/engine/v10/k2/p$p/receipt-d2.json" --max-gb 50 > "out/e8nm_d${d}_n18_p$p.json" 2> "out/e8nm_d${d}_n18_p$p.err" < /dev/null; then
  echo "$(date -u +%FT%TZ) exit 0 p=$p d=$d r=$("$PYTHON" -c "import json,sys;print(json.load(open(sys.argv[1]))[\"r_N\"])" "out/e8nm_d${d}_n18_p$p.json")" >> "$ev"
else
  echo "$(date -u +%FT%TZ) exit $? p=$p d=$d" >> "$ev"
fi
