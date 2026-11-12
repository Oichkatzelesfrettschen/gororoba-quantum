#!/bin/sh
# Run one analysis script of this directory under the memory cap and the 4-worker limit.
set -eu
PYTHON=${PYTHON:-python3}
HERE=$(cd "$(dirname "$0")" && pwd)
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHONDONTWRITEBYTECODE=1 GOROROBA_WORKERS=4 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd "$HERE"
systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 "$PYTHON" -B "$@"
