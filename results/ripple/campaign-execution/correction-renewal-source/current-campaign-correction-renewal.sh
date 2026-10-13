#!/bin/bash
set -eu
trap 'printf "%s\n" "$?" > /tmp/current-campaign-correction-renewal.exit' EXIT
export PYTHON=/tmp/quantum-ripple-validation-venv/bin/python
export PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error
export GOROROBA_WORKERS=2 QISKIT_NUM_PROCS=2 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
export MPLCONFIGDIR=/tmp/quantum-ripple-render-mpl
cd @HOME@/.codex/worktrees/cayley-dickson-ripple-evidence/IBMQuantum || exit 1
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family folded-correction \
  --objective minimum_charge \
  --cost-scenario controller-stress:4.6:40.0 \
  --local-compute cpu \
  --simulation-threads 2 \
  --simulation-memory-mb 512 \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 8192 \
  --seeds 6 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 8192 \
  --replica-tiers 1 \
  --optimizer-candidates 6 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 30.0 \
  --out ../results/live

