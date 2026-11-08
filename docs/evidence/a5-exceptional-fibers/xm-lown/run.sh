#!/bin/sh
# X- -> N- at p = 32009, engine v11 quotient mode, raw (every product): degree 2 at N = 5 to 8 and degree 3 at
# N = 10 to 13, degree 4 at N = 12 to 16. Degree 2 tests whether the rank reaches HF(k[y]/K2, 2) = 51 at N = 7 with a last jump of 25, degree 3
# whether the last jump into HF = 122 is 49 split 9/12/14/14 (ledger row A5-244). Run from the repository root;
# finished cells are skipped.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
out=docs/evidence/a5-exceptional-fibers/xm-lown
hdr=docs/evidence/a5-exceptional-fibers/working/build/inputs/p32009-r10754/xm-nm.sing
engine=docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v11.py
for dn in 2:5 2:6 2:7 2:8 3:10 3:11 3:12 3:13 4:12 4:13 4:14 4:15 4:16; do
    d=${dn%%:*} n=${dn#*:}
    if [ -s "$out/xmnm_d${d}_n${n}_p32009.json" ]; then continue; fi
    rc=0
    systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 \
        timeout 900 /usr/bin/time -f "wall %e s maxrss %M KiB" -o "$out/xmnm_d${d}_n${n}_p32009.time" \
        "$PYTHON" "$engine" "$hdr" "$d" "$n" --quotient --export-dir "${TMPDIR:-/tmp}/xm-d$d-n$n" \
        > "$out/xmnm_d${d}_n${n}_p32009.json" 2> "$out/xmnm_d${d}_n${n}_p32009.err" < /dev/null || rc=$?
    echo "d=$d N=$n exit $rc" >> "$out/runs.events"
done
