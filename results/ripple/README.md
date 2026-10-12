# Finite Cayley-Dickson ripple evidence

[Open the standalone explorer](cayley-dickson-ripples.html) in a browser after
downloading or cloning the repository. The HTML embeds all data and needs
neither a server nor network access. Its controls explore exact walk frames
and signed box-kite fringes, with the proposed hardware depths labeled.

- `evidence.json` contains exact probabilities through depth 30, finite
  recurrence certificates, signed graphs, all 336 zero-product rows, 672
  phase checks and source hashes. `execution_metadata` records numerical
  residuals and dependency versions separately from the exact payload.
- `single-job-proposal.json` records the candidate 43-logical-qubit,
  116-setting experiment and the assumptions behind its approximately
  35-second QPU estimate. Live calibration and placement remain required.
- `cayley-dickson-ripples.html` is generated from the evidence and the
  repository HTML template. All displayed distributions are ideal local
  predictions. A measured rendering requires a separately approved QPU run.

The [derivation and interpretation](../../gororoba_quantum/RIPPLE_DYNAMICS.md)
state the mathematical and physical claim boundaries. The
[previous hardware adjudication](../live/2026-10-11T152922.787095Z/ADJUDICATION.md)
supplies historical timing context only.

## Reproduce and check

Install `requirements.txt` into the intended environment and set `PYTHON`
to its interpreter. The retained record uses the repository pins, including
NumPy 2.5.3 and Qiskit 2.5.2. From the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  export PYTHONDONTWRITEBYTECODE=1 GOROROBA_WORKERS=4
  "$PYTHON" gororoba_quantum/ripple_dynamics.py \
    --check results/ripple/evidence.json
  "$PYTHON" scripts/render_ripple_visualization.py \
    --evidence results/ripple/evidence.json \
    --out results/ripple/cayley-dickson-ripples.html --check
)
```

To regenerate after reviewing a scientific-source change, replace the
verifier's `--check` with `--out` and remove the renderer's `--check`.
The verifier compares the complete scientific payload and source hashes;
retained numerical residuals must be finite and below the fixed tolerance.
Dependency versions record provenance and can differ on a replay. The
renderer checks data consistency and exact HTML reproduction; it relies on
the preceding verifier for independent scientific validation.

The verifier's built-in negative controls reject invalid depths, unsupported
pairs, mutated algebra signs, failed normalization and confusion between a
state return and an operator return. Serial execution with optimized Python
and parallel execution produced identical retained payloads during
integration. Additional mutation probes rejected changed source hashes,
probabilities, edge counts, triangle data and invalid numerical residuals.
