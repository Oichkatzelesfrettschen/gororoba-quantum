# Ascella perturbed-compilation run

Ascella completed the perturbed-compilation case (job-02) under the owner's
approval of its case in
[the conformance design](../../../../docs/design/ascella-signed-coherence-conformance.md#perturbed-compilation-case-job-02).
It runs theta2-x-arm0 64 times: every eighth position at compilation seed 0,
job-00's mesh, and the other 56 at the nonzero values 0 to 55 of the ANU QRNG
draw `draw-2026-10-25T182813Z.json`. The cases digest is
`1dd8ea5fda47cd135d7aae7a90206e3f62e14f12e50c72941865143788d6f99d` and the
sent body's digest without `process_id` is
`bc4b94fa06c86cc219362691e47b3f1a4f055e14f9e25d08ef3f87b4d7933380`.

| Observation | Result |
|---|---|
| Job | `788097fb-b323-4b91-908d-08c3d7f16fb0` |
| Submitted | 2026-10-25 18:47 UTC |
| Terminal status | completed |
| Settings / detected samples | 64 / 524,288; 8,192 per setting |
| Provider execution duration | 186 seconds, equal to job-00's and job-01's |
| Token-reported debit | 1.016384 free credits; zero paid credits |
| Platform at plan | available; HOM 87.02 %, g2 2.0 %, clock 13.33 MHz |
| Served meshes | 57 distinct `computed_circuit` strings: one shared by the 8 anchors and equal to job-00's for this setting, and one per perturbed seed |

The token's Ascella totals move from 9 jobs, 403 seconds and 3.065536 free
credits to 10 jobs, 589 seconds and 4.08192 free credits. A nonzero seed
costs no measurable provider time.

## Preregistered reading

[`compilation-reading.json`](../../../../docs/evidence/ascella-order-coefficients/compilation-reading.json),
from [`scripts/ascella_compilation_reading.py`](../../../../scripts/ascella_compilation_reading.py),
applies the readings of plan
[`ascella-perturbed-compilation-case`](../../../../docs/state/plans/ascella-perturbed-compilation-case.json):

| Reading | Result |
|---|---|
| R1, compilation dependence | perturbed over anchor dispersion 7.08 per degree of freedom, permutation p 0.0049: compilation dependent |
| R2, prediction of the 56 meshes by the job-00 fits | joint quadratic forms: static offsets 1150, drive-linear 649, polynomial order 1 771, harmonic order 1 201 against the 0.999 quantile 94.5; every family short |
| R3, refit with job-02 on the 19 training-only folds | X sums 377, 247, 245, 85 on 10 with median variance ratios 0.23 to 0.86: every family identified and short; Y short for three families, harmonic order 1 at 20.9 |
