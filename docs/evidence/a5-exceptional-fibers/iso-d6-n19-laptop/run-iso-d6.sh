#!/bin/sh
# Iso -> N- degree 6 at N = 19 (the 3d + 1 law), p = 32009: engine v11 quotient mode in raw mode (no degree-2 receipt:
# the Iso receipt has never run and its relation files differ from the header by the sign of G_6..G_15). Target
# HF(k[y]/K2, 6) = 2,422; the last jump at N = 3d = 18 to 19 is predicted at (2d + 1)^2 = 169 with blocks 49/42/39/39.
# The runner exits with the engine's status.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=8
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/iso6.events
echo "$(date -u +%FT%TZ) start iso d=6 N=19 p=32009 raw" >> "$ev"
rc=0
/usr/bin/time -f "wall %e s maxrss %M KiB" -o out/isonm_d6_n19_p32009.time \
    timeout 43200 "$PYTHON" fiber_rank_v11.py isop1/iso-nm.sing 6 19 --quotient \
    --export-dir "$HOME/a5/exports/isonm-p32009-n19-v11" --export-chunks 5 --dense-tables-gb 0 --max-gb 47 \
    > out/isonm_d6_n19_p32009.json 2> out/isonm_d6_n19_p32009.err < /dev/null || rc=$?
echo "$(date -u +%FT%TZ) exit $rc iso d=6 N=19 p=32009" >> "$ev"
exit "$rc"
