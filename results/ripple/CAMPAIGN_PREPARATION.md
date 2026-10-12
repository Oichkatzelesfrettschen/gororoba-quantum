# Qualified correction and packed-algebra preparations

Three fresh preparations pass the independent source, QPY, endpoint and cost
audit. The campaign expects 106.290103040 seconds of QPU usage; the declared
stress scenarios total 118.445463040 seconds. Five service-enforced job ceilings
sum to 170 seconds, leaving 10 seconds below the user's 180-second cap. Queue
time, local compilation and rendering are separate from charged QPU usage.

| Family | PUB allocation | Nominal seconds | Stress seconds | Job ceilings | Peak participating qubits |
| --- | --- | ---: | ---: | --- | ---: |
| Correction | 4 x 8192 | 11.519211264 | 14.474571264 | 30 | 5 |
| Ripple | 120 x 1024; 26 x 4096 | 64.321793536 | 68.921793536 | 40 + 40 | 47 |
| Rank sectors | 15 x 1024; 21 x 4096 | 30.449098240 | 35.049098240 | 30 + 30 | 32 |

The [independent audit](fresh-campaign-preparation-audit.json) retains the
complete arithmetic, source hashes, endpoints, shot tiers and occupancy counts.
All cases bind runtime digest
`38487fe3aecb92eb237ef0c803d11df35198bbaec829a770b513b603a9a711fe`
at committed source `f1b9830ac5ff76c7d3fdeeffab69abf9aa2f28ed`.

| Family | Written case | record.json SHA-256 |
| --- | --- | --- |
| folded-correction | [case](../live/2026-10-12T163354.247043Z/UNAPPROVED_CASE.md) | `0ee3146cccce74abdd580380cca3d684106036d4fdc27bdc2bb4ccf340991a8a` |
| ripple | [case](../live/2026-10-12T163354.310138Z/UNAPPROVED_CASE.md) | `f0cdf8b3e69e6294878ac35a3a82e2ad3563e09e5aab3b6ba9667e79251cab87` |
| rank-sector | [case](../live/2026-10-12T163354.210407Z/UNAPPROVED_CASE.md) | `d6e778473789716b423d0941ec83b8920046a07db4f75143ab08b2576ab8f522` |

Each retained directory's SHA256SUMS binds its original record, QPY and case.
The generated case's UNAPPROVED heading records the planner's authority
boundary. The user's subsequent conditional authority is recorded separately
in the [coordination ledger](../live/qpu-coordination.json). Review and merge,
fresh source/calibration/QPY/dependency checks, quota reconciliation and
single-use approval binding remain execution gates. The shared account reserve
is 60 seconds; the preparation snapshots report 551 seconds remaining.

Correction runs first. The four-PUB pilot tests unconditional terminal success
for two supplied odd labels under a matched dynamic template. Its 88.06-percent
planning power assumes a hypothetical four-point gain; the calibrated model
predicts smaller gains. Returned schedules and raw counts gate the decision.
The pilot distinguishes an actionable correction policy for these witnesses;
its outcomes cannot identify a unique noise mechanism or certify general QPE.

The [preregistered practical accuracy protocol](STATIC_PACKING_ACCURACY.md)
classifies all 37 matched static controls against ten percent of each score
range. One weighted control cannot establish equivalence at the frozen shot
count; its practical-defect and unresolved outcomes remain informative. Ripple
and rank require separate execution admission after the correction decision. Ripple tests which interference patterns survive the calibrated
implementation and how selected packed/isolated references differ. Rank tests
dark/bright coefficient-normalized multiplication-path norms and their model
residuals. Noisy norms cannot establish exact rank or topology. Finite model
predictions omit hardware crosstalk, drift and controller/instrument effects;
their residuals make hardware acquisition scientifically informative.

Every original static row remains included. Runtime 0.50 requires homogeneous
shots within each job, so fixed tiers produce two jobs per static family.
The bounded allocator compares tier promotions and eligible uniform baselines,
including fixed job costs. It qualifies all 1138 ripple and 196 rank endpoints.
Planning simulations use 32768 and 131072 shots respectively; separate 4096-shot
evaluation summaries supply neither planning denominators nor admission.
Per-family alpha 0.05 does not establish joint 95-percent campaign coverage.

The acquisition contains 1,560,576 component shots and 6,669,312 participating-qubit
shots. Ripple reserves 55 fixed patch qubits across its family and uses up to 47
per physical shot; rank uses 32. QPY register width 156 is device capacity.
Participating wires differ from instantaneous pulse concurrency. Isolated
controls, matched companions and physical buffers retain their estimands.
The design establishes useful packing within a declared finite search;
global maximal packing and optimal information per second remain unproved.

Shared observations retain `(job_id, PUB, shot_index)`. The measured explorer
links signed box-kites, eight-phase fringes, associator depths, norm paths,
joint-event covariance, uncertainty and model residuals. Geometry identifies
the exact algebraic object; measured counts determine the visible scientific
quantities. Same-shot covariance describes dependence and establishes neither
fidelity nor causation. Actual settled charge will determine measured rates.

Three historical jobs already charge 49 seconds: 9 seconds for the initial
dynamic campaign and 29+11 seconds for the later matched ladder. Their raw
archives are reused. Circuit, layout and calibration differences prevent
indiscriminate pooling. These historical charges fall outside the new 180-second
campaign cap and already appear in account usage.
