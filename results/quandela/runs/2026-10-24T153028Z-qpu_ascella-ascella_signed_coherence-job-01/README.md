# Ascella signed-coherence permuted repeat

Ascella completed the permuted repeat (job-01) of the 64-setting
signed-coherence request under the owner's approval of its case in
[the conformance design](../../../../docs/design/ascella-signed-coherence-conformance.md#permuted-repeat-job-01).
It runs job-00's circuits in the order values 0 to 63 of the ANU QRNG draw
`draw-2026-10-18T083846Z.json` fix, at twice job-00's samples. The cases
digest is `cc5febbefe4af6b55ab364b79909fbb0f995d66774d98dabeffda2f16aaad5cb`
and the sent body's digest without `process_id` is
`23947078d4604bf1f247ab805cbdfd87832acdeb0681bfe03bdaf9bbf8e2ffea`.

| Observation | Result |
|---|---|
| Job | `6ef8e8db-6f62-4d55-b1c2-680be0685d85` |
| Submitted | 2026-10-24 15:31 UTC |
| Terminal status | completed |
| Settings / detected samples | 64 / 1,048,576; 16,384 per setting |
| Provider execution duration | 186 seconds, equal to job-00's at half the samples |
| Token-reported debit | 1.032768 free credits; zero paid credits |
| Platform at plan | available; HOM 87.46 %, g2 2.0 %, clock 13.33 MHz |
| Compiled circuits | all 64 `computed_circuit` strings equal job-00's for the same setting |

The token's Ascella totals move from 8 jobs, 217 seconds and 2.032768 free
credits to 9 jobs, 403 seconds and 3.065536 free credits.

## Registered endpoints

[`ascella_coherence_repeat.py --analyze`](../../../../scripts/ascella_coherence_repeat.py)
writes [analysis.json](analysis.json). All 27 endpoints qualify again. With
the radii about 0.7 of job-00's, eight intervals exclude their exact ideal
while conforming, among them the X sign-odd constant (0.4719, radius 0.0072)
and the Y sign-odd sin(2 theta) coefficient (0.4768, radius 0.0102).

## Preregistered comparison with job-00

[`repeat-comparison.json`](../../../../docs/evidence/ascella-order-coefficients/repeat-comparison.json)
holds the comparison the design registers:

| Question | Statistic | Reading |
|---|---|---|
| Fixed per-setting cause of outside-block clicks | Spearman -0.075, p 0.56 | not supported |
| Alternation in execution order | lag-1 autocorrelation -0.653, p below 1e-4 | supported |
| Reconfiguration size | Spearman 0.121, p 0.35 | not supported |
| Sample-budget scaling | log2 median ratio 0.83 | acquisition-proportional |
| Static X errors | residual Pearson 0.974, p below 1e-4 | reproduces |
| Static Y errors | residual Pearson 0.802, p below 1e-4 | reproduces |
| Contrast stability | V 0.9719 against 0.9699 (X), 0.9669 against 0.9702 (Y) | within one standard error (0.013) |

The outside-block clicks therefore follow the execution sequence: a high and
a low iteration alternate whatever setting runs, and the clicks grow with the
samples an iteration takes (13,268 of 1,048,576 against 6,659 of 524,288).
The analyzer residuals belong to the settings: the same configurations err
the same way six hours and several hourly recalibrations apart, at a stable
contrast of 0.97. The equal 186-second durations put the cost of 524,288
further samples below the duration's one-second resolution, so iterations,
not samples, set the job's time.

[`job-01-diagnostics.json`](../../../../docs/evidence/ascella-order-coefficients/job-01-diagnostics.json)
holds the exploratory reading of this run alone.
