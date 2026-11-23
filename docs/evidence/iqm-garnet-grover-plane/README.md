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

Replay: `"$PYTHON" scripts/iqm_grover_plane_retained.py --check docs/evidence/iqm-garnet-grover-plane/fits.json` recomputes the record
and compares it with the file to 1e-6 relative (gate `core-iqm-grover-plane-retained`).

Interpretation: [the plane-model note](../../design/iqm-garnet-grover-plane-model.md).
