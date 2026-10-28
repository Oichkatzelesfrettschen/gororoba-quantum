#!/bin/sh
set -eu

export PYTHON="${PYTHON:-/usr/bin/python3}"
export QUANDELA_TOKEN_FILE="${QUANDELA_TOKEN_FILE:-$HOME/.config/quandela/cloud-token}"
export GLIBC_TUNABLES="${GLIBC_TUNABLES:-glibc.rtld.optional_static_tls=4096}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 GOROROBA_WORKERS=4

exec "$PYTHON" scripts/ascella_transition_day_repeat.py --run --approval \
    'Afterward: test independent compiled meshes and output-port permutations, then repeat selected matched meshes tomorrow to measure drift.'
