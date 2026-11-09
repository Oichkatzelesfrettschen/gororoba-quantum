#!/bin/sh
# Iso -> N- degree 6, engine v11 quotient mode, raw (no receipt): first N = 18 at p = 32009 (tests that h_6 is reached
# at exactly N = 19 and the predicted r_18 = 2,253, last jump 169 split 49/42/39/39), then N = 19 at p = 32029
# (second prime, target HF(k[y]/K2, 6) = 2,422). Each run records its exit in out/iso6b.events; the runner exits with
# the first nonzero engine status.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=8
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/iso6b.events
run() {
    hdr=$1 n=$2 p=$3
    echo "$(date -u +%FT%TZ) start iso d=6 N=$n p=$p raw" >> "$ev"
    rc=0
    /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/isonm_d6_n${n}_p$p.time" \
        timeout 43200 "$PYTHON" fiber_rank_v11.py "$hdr" 6 "$n" --quotient \
        --export-dir "$HOME/a5/exports/isonm-p$p-n$n-v11" --export-chunks 5 --dense-tables-gb 0 --max-gb 47 \
        > "out/isonm_d6_n${n}_p$p.json" 2> "out/isonm_d6_n${n}_p$p.err" < /dev/null || rc=$?
    echo "$(date -u +%FT%TZ) exit $rc iso d=6 N=$n p=$p" >> "$ev"
    return "$rc"
}
run isop1/iso-nm.sing 18 32009
run isop2/iso-nm.sing 19 32029
