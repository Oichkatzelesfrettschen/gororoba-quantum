#!/bin/sh
# One instrumented engine run under a cgroup scope. usage: sh run.sh TAG LIMIT_S WRAP_OPTS -- ENGINE_ARGS...
# Resolves paths from the worktree root; writes logs/TAG.* beside this script.
set -eu
tag=$1; limit=$2; shift 2
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../.." && pwd)
PYTHON=${PYTHON:-${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python}
export PYTHON
SINGULAR=${SINGULAR:-$(ls "$HOME"/.cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages/sage_wheels/bin/Singular)}
export SINGULAR
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_WORKERS=${GOROROBA_WORKERS:-4}
export FIBER_ENGINE="$root/docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v11.py"
PYTHONPATH=$(dirname "$FIBER_ENGINE")
export PYTHONPATH
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
mkdir -p "$here/logs"
cd "$root"
rc=0
capped 8 timeout -k 10 "$limit" /usr/bin/time -v -o "$here/logs/$tag.time" \
    "$PYTHON" "$here/wrap.py" "$tag" "$here/logs" "$@" > "$here/logs/$tag.out" 2> "$here/logs/$tag.err" || rc=$?
echo "exit $rc" > "$here/logs/$tag.exit"
exit "$rc"
