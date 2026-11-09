#!/bin/sh
# X- -> N- at p = 32009, engine v11 quotient mode, raw (every product): degree 2 at N = 5 to 8 and degree 3 at
# N = 10 to 13, degree 4 at N = 12 to 16. Degree 2 tests whether the rank reaches HF(k[y]/K2, 2) = 51 at N = 7 with a last jump of 25, degree 3
# whether the last jump into HF = 122 is 49 split 9/12/14/14 (ledger row A5-244). Run from the repository root;
# finished cells are skipped. Each cell runs the engine's own process pool (GOROROBA_WORKERS), so the cells run one
# after another; the runner exits with the first nonzero cell status.
set -eu
PYTHON=${PYTHON:-${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python}
export PYTHON GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
out=docs/evidence/a5-exceptional-fibers/xm-lown
hdr=docs/evidence/a5-exceptional-fibers/working/build/inputs/p32009-r10754/xm-nm.sing
engine=docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v11.py
# capped GIB CMD...: a cgroup scope (MemoryMax, no swap) where the user bus answers, else prlimit --as, which caps
# each process's virtual address space; a process pool under it can hold several times GIB of resident memory.
capped() {
    gib=$1; shift
    if [ -S "${XDG_RUNTIME_DIR:-/nonexistent}/bus" ]; then
        systemd-run --user --scope -q -p MemoryMax="${gib}G" -p MemorySwapMax=0 "$@"
    else
        prlimit --as=$((gib * 1073741824)) "$@"
    fi
}
for dn in 2:5 2:6 2:7 2:8 3:10 3:11 3:12 3:13 4:12 4:13 4:14 4:15 4:16; do
    d=${dn%%:*} n=${dn#*:}
    if [ -s "$out/xmnm_d${d}_n${n}_p32009.json" ]; then continue; fi
    rc=0
    capped 8 timeout 900 /usr/bin/time -f "wall %e s maxrss %M KiB" -o "$out/xmnm_d${d}_n${n}_p32009.time" \
        "$PYTHON" "$engine" "$hdr" "$d" "$n" --quotient --export-dir "${TMPDIR:-/tmp}/xm-d$d-n$n" \
        > "$out/xmnm_d${d}_n${n}_p32009.json" 2> "$out/xmnm_d${d}_n${n}_p32009.err" < /dev/null || rc=$?
    echo "d=$d N=$n exit $rc" >> "$out/runs.events"
    [ "$rc" -eq 0 ] || exit "$rc"
done
