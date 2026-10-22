#!/bin/sh
set -eu
export PYTHON="${PYTHON:-python3}"
: "${QI_PYTHON:?export the pinned Quantum Inspire interpreter}"
export QI_PYTHON
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 GOROROBA_WORKERS=1
export PYTHONPATH=gororoba_quantum:scripts
exec nice -n 14 timeout 1800 "$PYTHON" scripts/local_photonic_compiler_crosscheck.py --out "${1:?name a fresh output directory}"
