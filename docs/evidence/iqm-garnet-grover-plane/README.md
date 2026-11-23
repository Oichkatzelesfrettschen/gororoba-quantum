# IQM Garnet Grover plane model: retained fits and checks

`fits.json` (schema `iqm-garnet-grover-plane-fits-v1`) is written by
`"$PYTHON" scripts/iqm_grover_plane_retained.py --out docs/evidence/iqm-garnet-grover-plane/fits.json`
(Python 3.14.9, qiskit 2.6.2, numpy 2.5.4, scipy 1.18.1, run in the repository's pinned environment). It holds:

- `engine_checks`: the noisy-path engine against the committed `prediction.json` (4.97e-10), the noiseless logical-frame channels
  against the Grover iteration (4.7e-15), the equality of the noisy channels of iterations two to four (3.7e-13), the affine
  closure of the model and the plane family against the noise-free coherent responses of CZ-phase and PRX-amplitude errors.
- `per_run`: the corrected marked probabilities of the line-ccz and depth runs of the Garnet Grover acquisitions
  (`results/iqm/runs/2026-11-20T230142Z-garnet-grover-line-ccz-grover`,
  `results/iqm/runs/2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover`) with the fits of the geometric and the
  rotation family.
- `joint`: the five joint fits over the four (run, mark) groups.
- `continuation_to_depth_4`: the depth-4 marked probability of the case's calibration under eps = 0 and under the fitted eps,
  with the retained uncertainty propagated by 64 unscrambled Sobol' draws.
- `mark_contrast`: the contrast of the retained depth run (marks 101 and 011) against a CZ phase and a PRX amplitude, read post hoc
  (z_PRX -3.14 from the exact fits and -2.99 from the joint fit; z_CZ -0.93), with the PRX ratio of the case's `prediction.json`.
- `priors`: the calibration infidelities and relaxation times of the path and the average-fidelity cost of a coherent error.

`complement.json` (schema `iqm-grover-plane-complement-v1`) is written by
`"$PYTHON" scripts/iqm_grover_plane_complement.py --out docs/evidence/iqm-garnet-grover-plane/complement.json` and refits the
same retained runs on all eight outcome cells (`grover_plane_complement.FullResponse`: the calibrated noisy path with the plane
rotation eps, the contraction s toward a fixed point Sigma and the offset a on every cell) under four fixed points: the uniform
state, three weights of the S3-invariant sector of the marked vertex (shell weights), per-qubit populations, and every cell free.
Each fit carries a per group offset a, a per mark s and a per mark eps; the marked-cell fit with the uniform state reproduces the
joint fit of `fits.json` (chi2 1.474, eps 0.0373 and -0.0129) and calibrates the reader. Replay: `--check` recomputes it and
compares to 1e-4 relative (gate `core-iqm-grover-plane-complement`); the depths of a group are independent, as in `fits.json`.

`billing_v4_inputs.json` pins the Garnet billing models (v3, v4_sum, v4_max, their largest leave-one-out residuals, the schedule model
and its relative errors) read from `docs/evidence/iqm-billing-v4/billing_v4.json` on branch `iqm-billing-shot-duration` at commit
7e7be1f32ed6ac6e7f0a340ad19b4fb911d1b297 (sha256 in the file). `variant_sizing.json` prices the two case variants from their circuits with
`gororoba_quantum/grover_plane_sizing.py` (written and replayed by `scripts/iqm_grover_plane_sizing.py --out / --check`, gate
`core-iqm-grover-plane-sizing`): circuits, executions, expected execution seconds, billed credits, `max_credits`, cancel threshold, the
margins at runtime overruns of 1, 1.5 and 2.2 times, the primary-test power and the `cases.json` digests.

Replay: `"$PYTHON" scripts/iqm_grover_plane_retained.py --check docs/evidence/iqm-garnet-grover-plane/fits.json` recomputes the record
and compares it with the file to 1e-6 relative (gate `core-iqm-grover-plane-retained`).

Interpretation: [the plane-model note](../../design/iqm-garnet-grover-plane-model.md).