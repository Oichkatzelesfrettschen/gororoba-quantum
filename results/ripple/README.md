# Finite Cayley-Dickson ripple evidence

[Open the standalone explorer](cayley-dickson-ripples.html) in a browser after
downloading or cloning the repository. The HTML embeds all data and needs
neither a server nor network access. Its controls explore exact walk frames
and signed box-kite fringes, with the proposed hardware depths labeled.

- `evidence.json` contains exact probabilities through depth 30, finite
  recurrence certificates, signed graphs, all 336 zero-product rows, 672
  phase checks and source hashes. `execution_metadata` records numerical
  residuals and dependency versions separately from the exact payload.
- `single-job-proposal.json` records the implemented 55-logical-qubit,
  146-row experiment. Fresh statistical admission, calibration and native
  timing determine its execution case; the earlier 35-second illustration
  is superseded.
- `cayley-dickson-ripples.html` is generated from the evidence and the
  repository HTML template. All displayed distributions are ideal local
  predictions. A measured rendering requires a separately approved QPU run.
- [rank-sector-norms.svg](rank-sector-norms.svg) plots the eight four-qubit
  sectors and all 160 acquisition values along the exact multiplication path.
  [The PNG preview](rank-sector-norms.png) carries the same explicitly ideal
  curves, exceptional parameters, and coefficient normalization.

The [derivation and interpretation](../../gororoba_quantum/RIPPLE_DYNAMICS.md)
state the mathematical and physical claim boundaries. The
[previous hardware adjudication](../live/2026-10-11T152922.787095Z/ADJUDICATION.md)
supplies historical timing context only.

## Reproduce and check

Install `requirements.txt` into the intended environment and set `PYTHON`
to its interpreter. The retained record uses the repository pins, including
NumPy 2.5.4 and Qiskit 2.5.2. From the repository root:

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

The rank-sector renderer uses the optional plotting pin `matplotlib==3.11.2`,
which is separate from the QPU dependencies in `requirements.txt`. Install
that version into the intended plotting environment with
`"$PYTHON" -m pip install "matplotlib==3.11.2"` when needed. The retained images
were generated with Matplotlib 3.11.2 and NumPy 2.5.4 using the bundled DejaVu
Sans font and the Agg backend.

The renderer constructs the 32 quartic norm numerators from each sector's
signed-permutation matrices. Five exact full 32-dimensional matrix evaluations
verify all 160 acquisition probabilities before either image is written.
The SVG embeds the rational probabilities, polynomial coefficients and probe
coordinates with relative source references. Every curve represents the ideal
model; marker locations identify proposed acquisition settings.

Regenerate both formats from the repository root:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error \
  MPLCONFIGDIR=/tmp/rank-sector-mplconfig \
  "$PYTHON" scripts/render_rank_sector_norms.py \
  --png results/ripple/rank-sector-norms.png
```

Add `--check` to render in temporary storage and compare both retained images
byte for byte without rewriting them. The check also repeats the exact-value
verification. Two renders in the recorded plotting environment produced
identical SVG and PNG bytes. Package or font changes can alter image bytes;
review and regenerate the images when the plotting environment changes.

The verifier's built-in negative controls reject invalid depths, unsupported
pairs, mutated algebra signs, failed normalization and confusion between a
state return and an operator return. Serial execution with optimized Python
and parallel execution produced identical retained payloads during
integration. Additional mutation probes rejected changed source hashes,
probabilities, edge counts, triangle data and invalid numerical residuals.

## Measured folded-QPE evidence

[The measured figure](folded-job-review.svg) and [PNG preview](folded-job-review.png)
show the two completed Kingston jobs: 16 PUBs at 8,192 shots each, charged 40 s.
[The independent audit](folded-job-review.md) reproduces all terminal estimates,
measurement mappings, and simultaneous contrast intervals from lossless raw
shots. [Its JSON table](folded-job-review.json) retains counts, predictions,
within-shot joint errors, and source hashes. The single raw archive and its
primary analysis belong to [hardware evidence PR #37](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/37).

The figure separates observed probabilities, hardware contrasts, and descriptive
hardware-minus-replay residuals. The two odd-label no-feedback outcomes exceed
the finite noise replay, while the other fourteen fall below it. Routing,
readout, prepared-label information, and execution-window differences limit
causal attribution. The contrast intervals assume independent stationary
repetitions within each PUB. Equal shot indices across different PUBs remain
unpaired.

With the raw archive available, set `FOLDED_RUN` to its directory and replay:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" \
  scripts/review_folded_jobs.py --run-dir "$FOLDED_RUN" --check
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" \
  scripts/render_folded_job_review.py --png results/ripple/folded-job-review.png --check
```

The renderer uses the same plotting pin as the rank-sector figure and embeds
its input SHA-256. Regeneration changes derived images; the raw archive stays
under its original evidence owner.
