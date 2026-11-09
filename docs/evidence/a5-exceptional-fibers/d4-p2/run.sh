#!/bin/sh
# Degree 4 at p = 32029 (canonical headers p32029-r9115), engine v11 quotient mode, raw: X- at N = 14 and 15 (the
# p = 32009 ladder closes at N = 15 with 240, blocks 68/66/53/53) for ledger row A5-171, and E8-bar -> VB at N = 12 to
# 15 for A5-111 (target HF(k[y]/K2, 4) = 155). Run from the repository root; finished cells are skipped. Cells run one
# after another because each runs the engine's own process pool; the runner exits with the first nonzero cell status.
set -eu
PYTHON=${PYTHON:-${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python}
export PYTHON GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
out=docs/evidence/a5-exceptional-fibers/d4-p2
in=docs/evidence/a5-exceptional-fibers/working/build/inputs/p32029-r9115
engine=docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v11.py
# capped GIB CMD...: a cgroup scope (MemoryMax, no swap) where the user bus answers, else prlimit --as, which caps
# each process's virtual address space; a process pool under it can hold several times GIB of resident memory.
capped() {
    gib=$1
    shift
    if [ -S "${XDG_RUNTIME_DIR:-/nonexistent}/bus" ]; then
        systemd-run --user --scope -q -p MemoryMax="${gib}G" -p MemorySwapMax=0 "$@"
    else
        prlimit --as=$((gib * 1073741824)) "$@"
    fi
}
# usage: sh run.sh HEADER_STEM:N ...  (for example xm-nm:15 e8-vb:13)
for cell in "$@"; do
    stem=${cell%%:*} n=${cell#*:}
    tag=$(printf %s "$stem" | tr -d -)_d4_n${n}_p32029
    if [ -s "$out/$tag.json" ]; then continue; fi
    rc=0
    capped 16 timeout 1800 /usr/bin/time -f "wall %e s maxrss %M KiB" -o "$out/$tag.time" \
        "$PYTHON" "$engine" "$in/$stem.sing" 4 "$n" --quotient --export-dir "${TMPDIR:-/tmp}/d4p2-$tag" \
        > "$out/$tag.json" 2> "$out/$tag.err" < /dev/null || rc=$?
    echo "$tag exit $rc" >> "$out/runs.events"
    [ "$rc" -eq 0 ] || exit "$rc"
done
