#!/bin/sh
# Run from the repository root; each invocation writes a new unapproved case.
set -eu
PYTHON="${PYTHON:-$(command -v python3)}"
export PYTHON PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error
export QISKIT_NUM_PROCS=2 GOROROBA_WORKERS=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
cd gororoba_quantum
"$PYTHON" -u live_run.py --family folded-qpe --optimize \
  --objective precision_at_budget --cost-scenario latency_stress:4.6:60 \
  --local-compute cpu --simulation-threads 2 --simulation-memory-mb 512 \
  --backends ibm_kingston --seeds 2 --optimizer-candidates 2 \
  --replica-tiers 1 --shot-tiers 2048,4096,8192,16384 --model-shots 4096 \
  --max-execution-seconds 60 --max-total-execution-seconds 120 \
  --reserve-seconds 60 --out ../results/live
