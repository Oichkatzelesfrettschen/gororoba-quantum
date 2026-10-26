# Ascella seed-repeat run

Ascella completed the seed-repeat case (job-03) under the owner's approval of
its case in
[the conformance design](../../../../docs/design/ascella-signed-coherence-conformance.md#seed-repeat-case-job-03).
It runs job-02's 64 settings of theta2-x-arm0 with job-02's compilation seeds
and circuit parameters: the 8 seed-0 anchors at every eighth position, and the
56 perturbed meshes in the order of values 0 to 55 of the ANU QRNG draw
`draw-2026-10-26T033936Z.json`. The cases digest is
`2fec6bf15d642a930b46c10a3d7c3f641368c18198926ea4166bb90f7fcc062e` and the
frozen body's digest is
`64de4fe523488b773d25a66733917847268e396b111e4c1bf711b486ccc6707c`.

| Observation | Result |
|---|---|
| Job | `e2f30d83-17b1-402e-8b2f-319bb5a86f91` |
| Submitted | 2026-10-26 03:57 UTC, after the platform left a calibration state it reported at 03:50 UTC |
| Terminal status | completed |
| Settings / detected samples | 64 / 1,048,576; 16,384 per setting |
| Provider execution duration | 186 seconds, equal to jobs 00, 01 and 02 |
| Token-reported debit | 1.032768 free credits; zero paid credits |
| Platform at plan | available; HOM 87.02 %, g2 2.0 %, clock 13.33 MHz |
| Served meshes | every setting's `computed_circuit` equals job-02's under the same name |

The token's Ascella totals move from 10 jobs, 589 seconds and 4.08192 free
credits to 11 jobs, 775 seconds and 5.114688 free credits.

## Preregistered reading

[`seed-repeat-reading.json`](../../../../docs/evidence/ascella-order-coefficients/seed-repeat-reading.json),
from [`scripts/ascella_seed_repeat_reading.py`](../../../../scripts/ascella_seed_repeat_reading.py),
applies the readings of plan
[`ascella-seed-repeat-case`](../../../../docs/state/plans/ascella-seed-repeat-case.json):

| Reading | Result |
|---|---|
| M, mesh identity | 8 of 8 anchors and 56 of 56 perturbed meshes equal job-02's |
| A, anchor control | anchor mean X 0.8858 against job-02's 0.8829, +1.48 standard errors: steady |
| P1, reproduction | per-mesh X correlation r 0.885 between the jobs, permutation p 5e-5, against the fully-fixed ceiling 0.880 and its 0.01 lower bound 0.784: fixed per mesh |
| P2, replicated dependence | perturbed over anchor dispersion 36.8 per degree of freedom, p 0.00025: compilation dependent |

Exploratory: the perturbed meshes' dark-output (mode 2) fractions correlate
with rho 0.18 (p 0.18) between the jobs, and each mesh's X change follows the
change of its predecessor's phase distance with rho 0.06 (p 0.67). The
perturbed mean X reads 0.8868 in job-02 and 0.8869 here.
