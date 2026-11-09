#!/bin/sh
# Acceptance runs of fiber_rank_v12.py (and v11 as the baseline) on one W8 -> N- cell, p = 32009, quotient mode.
# usage: sh accept.sh ROOT TAG ENGINE D N [ENGINE_FLAGS...]
# ROOT holds docs/evidence/... (header, receipt), gororoba_quantum/ (parallel.py, modular_echelon.py), the engines
# under docs/evidence/a5-exceptional-fibers/replay/engine/, and receives exports/ and logs/.
# SINGULAR names the Singular binary; PYTHON names the interpreter (default: python3 on PATH).
set -eu
root=$1; tag=$2; engine=$3; d=$4; n=$5; shift 5
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
systemd-run --user --scope -q -p MemoryMax=20G -p MemorySwapMax=0 \
    /usr/bin/time -v -o "logs/$tag.time" \
    "$PYTHON" "$E/replay/engine/$engine" "$E/working/build/inputs/p32009-r10754/w8-nm.sing" "$d" "$n" --quotient \
    --k2-receipt "$E/working/distribute/out/a5-w8-receipt-p1/w8_p1/d2/receipt-d2.json" \
    --export-dir "exports/w8-n$n" --export-chunks 5 --dense-tables-gb 0 --singular "$SINGULAR" "$@" \
    > "logs/$tag.out" 2> "logs/$tag.err" || rc=$?
echo "exit $rc" > "logs/$tag.exit"
exit "$rc"
