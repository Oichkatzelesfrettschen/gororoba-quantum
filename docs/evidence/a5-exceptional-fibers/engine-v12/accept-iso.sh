#!/bin/sh
# Acceptance run of fiber_rank_v12.py on Iso -> N- degree 6 at N = 19, p = 32009, quotient mode in raw mode (no receipt).
# usage: sh accept-iso.sh ROOT TAG ENGINE [ENGINE_FLAGS...]
# ROOT holds iso/isop1/iso-nm.sing, iso/export (a finished export of the header at N = 19), gororoba_quantum/ and the
# engine under docs/evidence/a5-exceptional-fibers/replay/engine/; logs go to ROOT/logs. SINGULAR names the binary.
set -eu
root=$1; tag=$2; engine=$3; shift 3
E=docs/evidence/a5-exceptional-fibers
PYTHON=${PYTHON:-python3}
SINGULAR=${SINGULAR:?set SINGULAR to the Singular binary}
export GOROROBA_GPU_GIB=${GOROROBA_GPU_GIB:-13.4}
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_WORKERS=${GOROROBA_WORKERS:-8}
export GOROROBA_PARALLEL_DIR="$root/gororoba_quantum"
mkdir -p "$root/logs"
cd "$root"
rc=0
# Device memory in MiB every 5 s, where nvidia-smi answers (WSL keeps it under /usr/lib/wsl/lib).
smi=$(command -v nvidia-smi || echo /usr/lib/wsl/lib/nvidia-smi)
if [ -x "$smi" ]; then
    "$smi" --query-gpu=memory.used --format=csv,noheader,nounits -l 5 > "logs/$tag.gpu" 2> /dev/null &
    smi_pid=$!
    trap 'kill "$smi_pid" 2> /dev/null || true' EXIT
fi
systemd-run --user --scope -q -p MemoryMax=40G -p MemorySwapMax=0 \
    /usr/bin/time -v -o "logs/$tag.time" \
    "$PYTHON" "$E/replay/engine/$engine" iso/isop1/iso-nm.sing 6 19 --quotient \
    --export-dir iso/export --export-chunks 5 --dense-tables-gb 0 --max-gb 47 --singular "$SINGULAR" "$@" \
    > "logs/$tag.out" 2> "logs/$tag.err" < /dev/null || rc=$?
echo "exit $rc" > "logs/$tag.exit"
exit "$rc"
