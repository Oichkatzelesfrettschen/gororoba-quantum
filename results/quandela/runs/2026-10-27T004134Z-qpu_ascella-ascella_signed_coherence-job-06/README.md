# Ascella replication run (job-06)

Ascella completed the first job of the replication case, which the owner
approved, under plan
[`ascella-replication-meshes-case`](../../../../docs/state/plans/ascella-replication-meshes-case.json)
and the
[conformance design](../../../../docs/design/ascella-signed-coherence-conformance.md#replication-case-job-06-and-job-07).
The job ran theta2-x-arm0 96 times at 32,768 samples:
- the seed-0 mesh of job-00 at every eighth position, 12 anchors in all;
- 84 new compilation seeds, the usable values 0 to 83 of the ANU QRNG draw
  `draw-2026-10-27T003715Z.json`.

That draw was retrieved after commit `bc15673` froze the predictors. The cases
digest is `d873ebbac64210b557cbdd36122d522f51bf2e38f9c6dacef10901d6d665d88a`.

| Observation | Result |
|---|---|
| Job | `d54d0e9d-0d44-421a-a67b-b422f0a8febc` |
| Submitted | 2026-10-27 00:43 UTC |
| Terminal status | completed |
| Settings / detected samples | 96 / 3,145,728; 32,768 per setting |
| Provider execution duration | 288 s, 12 s inside the 300 s max_duration and 1 s above the 287 s that the line through jobs 04 and 05 projects |
| Token-reported debit | 1.032768 free credits; zero paid credits |
| Platform at plan | available; HOM 87.16 %, g2 2.0 %, clock 13.33 MHz |
| Served meshes | 84 distinct perturbed meshes, none served by jobs 00 to 05 |

The token's Ascella free-credit total moved from 7.180224 to 8.212992. The
snapshot after the job counts 15 Ascella jobs, because job-07 had already been
submitted, while its debit had not yet posted. Job-06 completed with every
iteration counted, so the frozen rule admitted the 96-iteration job-07
variant, which ran next.

**Manifest provenance.** This run's `cases.json`, as submitted, names
`ascella-new-seed-meshes-case.json` and `new-mesh-offsets.json` under
`preregistered`, and its seed rule mentions job-02's seeds alone. The request
builder writes that block for every job seeded from a draw other than job-02's.
The bytes stay as submitted, because their digest binds the submission and the
score's acquisition check. The analysis contract is plan
[`ascella-replication-meshes-case`](../../../../docs/state/plans/ascella-replication-meshes-case.json),
with
[`replication-offsets.json`](../../../../docs/evidence/ascella-order-coefficients/replication-offsets.json)
and `scripts/ascella_replication_score.py`. The seeds skip every seed of jobs
02, 04 and 05 (`ascella_coherence_request.compilation_seeds`).
