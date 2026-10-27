# Ascella replication run (job-07)

Ascella completed the second job of the replication case, which the owner
approved, under plan
[`ascella-replication-meshes-case`](../../../../docs/state/plans/ascella-replication-meshes-case.json).
Job-06 completed all 96 of its iterations, so the frozen rule admitted
`job-07-i96`. The job ran theta2-x-arm0 96 times at 32,768 samples:
- 12 seed-0 anchors, at every eighth position;
- 84 new compilation seeds, the usable values 84 to 167 of the ANU QRNG draw
  `draw-2026-10-27T003715Z.json`.

The cases digest is
`0b8d9e8f25addd44cbae413d08861c7b580416321048e8991c61db32d4ac5c10`.

| Observation | Result |
|---|---|
| Job | `f27ad639-d947-4b99-84d6-42a9b6536d40` |
| Submitted | 2026-10-27 00:49 UTC |
| Terminal status | completed |
| Settings / detected samples | 96 / 3,145,728; 32,768 per setting |
| Provider execution duration | 289 s, 1 s above job-06's 288 s |
| Token-reported debit | 1.032768 free credits; zero paid credits |
| Platform at plan | available; HOM 87.16 %, g2 2.0 %, clock 13.33 MHz |
| Served meshes | 84 distinct perturbed meshes, none served by jobs 00 to 06 |

The token's Ascella totals moved to 15 jobs, 1,860 seconds and 9.24576 free
credits. The preregistered score reads this run with job-06 in
[`replication-score.json`](../../../../docs/evidence/ascella-order-coefficients/replication-score.json).

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
