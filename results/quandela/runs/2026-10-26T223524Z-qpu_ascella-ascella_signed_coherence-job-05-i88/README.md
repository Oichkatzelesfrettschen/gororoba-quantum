# Ascella new-seed run (job-05-i88)

Ascella completed the second job of the new-seed meshes case, the variant that
job-04's 243-second duration admitted under the frozen duration rule of
[the conformance design](../../../../docs/design/ascella-signed-coherence-conformance.md#new-seed-meshes-case-job-04-and-job-05).
It runs theta2-x-arm0 88 times at 32,768 samples: 11 seed-0 anchors at every
eighth position and 77 new compilation seeds, the usable values 70 to 146 of
the ANU QRNG draw `draw-2026-10-26T174307Z.json`. The cases digest is
`87a926b794dba5be551293013e85c4f151cffba4b147656849bc352803de576b`.

| Observation | Result |
|---|---|
| Job | `690c6e49-b4e7-4907-9fe3-54414d24a515` |
| Started | 2026-10-26 22:36 UTC |
| Terminal status | completed |
| Settings / detected samples | 88 / 2,883,584; 32,768 per setting |
| Provider execution duration | 265 seconds, within 2 s of the 267 s that job-04's rate projects |
| Token-reported debit | 1.032768 free credits; zero paid credits |
| Platform at plan | available; HOM 86.86 %, g2 2.1 %, clock 13.33 MHz |
| Served meshes | 77 distinct perturbed meshes, none served by jobs 00 to 04 |

The token's Ascella totals move from 12 jobs, 1,018 seconds and 6.147456 free
credits to 13 jobs, 1,283 seconds and 7.180224 free credits.

The preregistered score reads this run with job-04:
[`new-seed-score.json`](../../../../docs/evidence/ascella-order-coefficients/new-seed-score.json).
