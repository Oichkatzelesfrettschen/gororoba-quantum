#!/bin/sh
# Replay E8-bar -> N- d = 4, N = 15, p = 32009 with engine v8 (expected r_N = 495); v8 limits, not the v11 timings.
set -eu
export PATH="$HOME/a5env/bin:$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq"
cd "$HOME/a5/replay"
mkdir -p out/e8n15-p1
rc=0
/usr/bin/time -f "wall %e s maxrss %M KiB" -o out/e8n15-p1/time timeout -k 30 43200 "$HOME/a5env/bin/python" \
  a5-exceptional-fibers/replay/engine/fiber_rank_v8.py a5-exceptional-fibers/working/build/inputs/p32009-r10754/e8-nm.sing 4 15 \
  --quotient --max-gb 50 > out/e8n15-p1/out.json 2> out/e8n15-p1/err < /dev/null || rc=$?
echo "exit $rc" > out/e8n15-p1/exit
