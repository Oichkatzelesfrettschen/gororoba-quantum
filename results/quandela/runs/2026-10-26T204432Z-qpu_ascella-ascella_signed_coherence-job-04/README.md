# Ascella new-seed run (job-04)

Ascella completed the first job of the new-seed meshes case under the owner's
approval of its case in
[the conformance design](../../../../docs/design/ascella-signed-coherence-conformance.md#new-seed-meshes-case-job-04-and-job-05).
It runs theta2-x-arm0 80 times at 32,768 samples: the seed-0 mesh of job-00 at
every eighth position (10 anchors) and 70 new compilation seeds, the usable
values 0 to 69 of the ANU QRNG draw `draw-2026-10-26T174307Z.json`. The cases
digest is `abbe4e5a3bf69ae8fbceefe5607b862fed4a0afdf31276582cc587e8f85718be`.

| Observation | Result |
|---|---|
| Job | `be11a4b0-ac35-4c6f-bfd0-689a13ac6b27` |
| Started | 2026-10-26 22:30 UTC |
| Terminal status | completed |
| Settings / detected samples | 80 / 2,621,440; 32,768 per setting |
| Provider execution duration | 243 seconds, 3.04 s per iteration against the 2.906 s that 64 iterations in 186 s bound under a linear model |
| Token-reported debit | 1.032768 free credits; zero paid credits |
| Platform at plan | available; HOM 86.86 %, g2 2.1 %, clock 13.33 MHz |
| Served meshes | 70 distinct perturbed meshes, none served by jobs 00 to 03 |

The token's Ascella totals move from 11 jobs, 775 seconds and 5.114688 free
credits to 12 jobs, 1,018 seconds and 6.147456 free credits. Under the frozen
rule 8 floor(min(96, 279 * 80 / d4) / 8), the 243-second duration admitted the
88-iteration job-05 variant, which ran next.

The preregistered score reads this run with job-05-i88:
[`new-seed-score.json`](../../../../docs/evidence/ascella-order-coefficients/new-seed-score.json).
