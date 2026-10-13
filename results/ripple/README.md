# Finite Cayley-Dickson ripple evidence

The [measured explorer](measured-cayley-dickson-ripples.html) now contains
the completed ripple and rank-sector counts: 66 and 31 final charged QPU
seconds, respectively. The [campaign findings](../live/CAMPAIGN_FINDINGS.md)
separate registered contrast signs, unresolved packing comparisons and the
large walk-control/model discrepancy. The original ideal explorer and
preparation cases below retain their historical interpretation.

The [fresh campaign preparation](CAMPAIGN_PREPARATION.md) qualifies a
106.290103040-second nominal QPU estimate and a 118.445463040-second declared
stress scenario. Five jobs have service ceilings totaling 170 seconds:
30 for correction, 80 for ripple and 60 for rank-sector. The ceilings fit the
user's 180-second total limit with ten seconds unallocated. Queue and local
preparation time are excluded; the stress scenario is a sensitivity assumption.
The [independent audit](fresh-campaign-preparation-audit.json) passes source,
model-denominator, circuit, endpoint, allocation, case and budget checks.

Correction runs first. Planning qualification retains every original row,
control and within-PUB shot vector; each Runtime job uses one homogeneous shot
count. Execution still requires clean current-head Copilot review, passing
checks, merged changes, fresh approval bindings and independent execution
admission for each family under the
[practical accuracy protocol](STATIC_PACKING_ACCURACY.md). The
[integrated campaign directive](../../gororoba_quantum/RIPPLE_CAMPAIGN.md)
records the user's conditional execution authority and the Copilot-plus-checks
substitution while Codex review quota is exhausted. The three completed
hardware jobs already charged 49 seconds: the original acquisition charged
9 seconds, and the later folded pair charged 29 and 11 seconds. Those measured
charges precede the remaining campaign budget.

The [historical execution preparation summary](PREPARATION.md) retains the
earlier ripple and rank-sector cases, 197.022-second nominal estimate and
proposed 240-second combined ceiling. Those records remain
`historical_renewal_required`; the fresh campaign cases carry the renewed
planning qualification. The
[fixed shot allocation](../../gororoba_quantum/PACKED_ALGEBRA.md#fixed-shot-allocation)
preserves all static rows and compares complete shot-tier assignments with
eligible uniform baselines. Historical minimum-tier planning arithmetic gives
a 118.437402112-second stress estimate; the fresh audit above supplies the
current estimate. The separate 4096-shot evaluation
distributions remain distinct from the higher-shot planning model summaries.

[Open the standalone explorer](cayley-dickson-ripples.html) in a browser after
downloading or cloning the repository. The HTML embeds all data and needs
neither a server nor network access. Its controls explore exact walk frames
and signed box-kite fringes, with the proposed hardware depths labeled.

- `evidence.json` contains exact probabilities through depth 30, finite
  recurrence certificates, signed graphs, all 336 zero-product rows, 672
  phase checks. `execution_metadata` records numerical
  residuals and dependency versions separately from the exact payload.
- `single-job-proposal.json` retains the 55-logical-qubit, 146-row design
  with current state `historical_renewal_required`. The preparation summary
  preserves statistical admission and calibration at the recorded revision.
  Retained native attempts leave scheduler timing unqualified. The historical
  157.0873-second nominal estimate superseded the 35-second illustration;
  the fresh campaign audit supplies the renewed estimate.
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
  export PYTHONDONTWRITEBYTECODE=1
  "$PYTHON" gororoba_quantum/ripple_dynamics.py \
    --check results/ripple/evidence.json
  "$PYTHON" scripts/render_ripple_visualization.py \
    --evidence results/ripple/evidence.json \
    --out results/ripple/cayley-dickson-ripples.html --check
)
```

To regenerate after reviewing a scientific-source change, replace the
verifier's `--check` with `--out` and remove the renderer's `--check`.
The verifier compares the complete scientific payload;
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
its input SHA-256. Its supported input is the sixteen-member, twelve-contrast
folded audit. Qualification requires the complete named audit checks,
integer-count marginals, confidence declarations, and consistent job/PUB
metadata. Captions derive charges, routing, readout sites, execution windows,
and interval conclusions from that qualified evidence. The renderer checks
internal consistency; raw provenance still requires the independent audit.

Run `"$PYTHON" scripts/check_render_folded_job_review.py` and its `-O` variant
to exercise malformed-input rejection and changed-caption evidence. Both checks
and byte-for-byte image reproduction belong to the required repository gates.
Regeneration changes derived images; the raw archive stays under its original
evidence owner. The [validation receipt](folded-renderer-validation.json)
binds the tested source, image hashes, regression counts and full-gate result.

Report destinations must stay outside the retained run and identify separate
JSON and Markdown files. The folded renderer requires distinct evidence, SVG
and PNG paths; the rank renderer requires distinct SVG and PNG paths. The
interactive ripple renderer protects its evidence and template from aliased
HTML output paths. Each command rejects canonical, symbolic-link and hardlink
aliases before writing, including in `--check` mode. The output-admission
checks run under normal and optimized Python through `scripts/check_review_folded_jobs.py`,
`scripts/check_render_folded_job_review.py`,
`scripts/check_render_rank_sector_norms.py`, and
`scripts/check_render_ripple_visualization.py`. Their fixtures verify retained
bytes after rejection and exercise supported separate destinations.

## Measured static algebra explorer

The measured extractor binds collected ripple and rank-sector data to their
approved records, QPY bytes, immutable raw registers and retained analyses.
The portable HTML links box-kite phase fringes, measured associator depths,
rank-sector probe norms, full outcome distributions, same-PUB event covariance,
shot-order blocks and provenance. Exact algebra supplies the coordinates;
integer counts supply the measured quantities. Preparation predictions and
execution-calibration replay appear as separately labeled residuals.

After collection, set `RIPPLE_RUN` and `RANK_RUN` to the respective retained run
directories and choose new output paths outside those directories:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" \
  scripts/extract_measured_ripple.py --run "$RIPPLE_RUN" \
  --out results/ripple/measured-ripple.json
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" \
  scripts/extract_measured_ripple.py --run "$RANK_RUN" \
  --out results/ripple/measured-rank-sector.json
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" \
  scripts/render_measured_ripple.py \
  --evidence results/ripple/measured-ripple.json \
  --evidence results/ripple/measured-rank-sector.json \
  --out results/ripple/measured-cayley-dickson-ripples.html
```

The renderer accepts either family independently. Add `--check` to reproduce
and compare an existing output without writing. Both commands install complete
new outputs atomically and reject replacement or input aliases. The extractor's
public acquisition command rejects synthetic fixtures. Test fixtures carry a
visible synthetic banner and supply software validation only.

Shared observations use `(job_id, PUB, shot_index)`. Stochastic outcomes support
descriptive event covariance; deterministic expected outcomes also support
error covariance. Different PUBs retain separate observation identities.
Retained inference gates control interval visibility, and missing or straddled
execution calibration withholds replay. Rank probe norms do not directly
measure exact rank or topology. Occupancy rates use settled actual QPU charge
and retain unavailable values until that charge is verified; they quantify
measurement volume rather than fidelity or independent information.
