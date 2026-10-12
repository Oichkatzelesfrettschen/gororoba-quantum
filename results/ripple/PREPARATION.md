# Packed algebra execution cases

The integrated objective joins the user's mathematical, scientific, philosophical,
and visual requests: realize exact Cayley-Dickson predictions through measured
interference; acquire the box-kite atlas, associator walks, original Design C
controls, and rank-path sectors with joint shot order; preserve uncertainty,
shared errors and model residuals in the visuals; retain source and prior-work
provenance; and maximize useful observations within charged QPU time. The
completed folded-QPE diagnostic supplies measured constraints on interpretation
and timing. Its two jobs are excluded from duplicate execution.

The two new families have completed local statistical admission. Both remain
unapproved for physical execution. They use separate static jobs because the
combined 87-qubit candidate has only a bounded infeasibility result. Each
family independently fits one job on Kingston.

| Prepared family | Active qubits | PUBs | Shots/PUB | Qualified endpoints | Nominal QPU seconds | Stress seconds | Service ceiling |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ripple atlas, walks and Design C | 55 | 146 | 4096 | 1138 / 1138 | 157.0873 | 159.3873 | 180 s |
| Rank-path sectors | 32 | 36 | 4096 | 196 / 196 | 39.9347 | 42.2347 | 60 s |
| Combined campaign | separate jobs | 182 | 4096 | 1334 / 1334 | 197.0220 | 201.6220 | 240 s |

The estimate is about 3 minutes 17 seconds of QPU usage, excluding queue and
local preparation time. Stress assumptions are named scenarios, rather than
confidence bounds on billing. The service ceilings bound each job through
`max_execution_time`. A 551-second remaining-usage observation covers the
240-second combined ceiling plus one shared 60-second reserve, leaving 251
seconds unallocated. Concurrent jobs can change that observation.

## Exact cases

- [Ripple case](../live/2026-10-12T062505.208379Z/UNAPPROVED_CASE.md):
  record SHA-256 `bbf5f4341151e62dbd5304f54baffa840c41414e6f12762ad84c5924e787a038`.
- [Rank-sector case](../live/2026-10-12T062505.552988Z/UNAPPROVED_CASE.md):
  record SHA-256 `f38dfe635415d264eea754e4d699080092ca7272f65e42304fac08f5b4f5fe7d`.
- [Machine-readable preparation summary](preparation-summary.json) binds both
  records, sources, endpoint counts, costs, ceilings and native sidecars.

Both records bind source digest
`493d6d39d1197221d1d4a9610d5b542036e67e24a1323246ba14b828bfbbe085`.
Their source-closure reports verify all 36 declared files and dependency
versions, with `sources_modified=false`. Submission refreshes calibration,
placements, QPY and quota; a mismatch requires a new case.

Kingston's physical backend is accessible, while its runtime mock configuration
returns HTTP 404. Both native attempts retained `status=unavailable`, with
zero returned mock job identities. Native scheduler timing remains unqualified.
The completed folded diagnostic charged 40 s versus 39.6324 s forecast, which
supports that workload's accounting and does not bound the new schedules.

## Placement and scientific admission

The [90-percent-floor search](routing-admission-rejection.json) rejected 256
of 4096 routed combinations before the bounded search stopped. A relative
placement-score floor of 0.8 admits more physical patches; its first routed
combination placed every ripple lane with the original physical one-hop
buffers. The quality exclusions, scientific controls, shot precision, and
spending ceilings stayed in force. Fresh noise simulation then admitted every
required endpoint. The largest simultaneous half-width is 0.074671 for ripple
and 0.068680 for rank sectors, within the requested 0.08.

Global optimality remains outside the result. Broader occupancy alone does not
prove better throughput. The [spatial assessment](spatial-packing-assessment.md)
retains the 100-row coverage failure, the corrected 110-row mathematical
construction, and the bounded placement limits of denser candidate designs.

The 1138 ripple and 196 rank endpoints have disjoint names and measurement
roles. Ripple measures sedenion fringes and associator-phase evolution; rank
sectors measure `||L_a(t)v||^2 / (alpha(t)^2 ||v||^2)` on the specified
32-dimensional path. Coincident ideal probabilities do not make those
observables interchangeable. Historical Design C measurements serve as
context; the nine repeated original members and three isolated references
control the fresh placement and neighboring workload.

## What the data will make visible

- Seven exact signed box-kites carry measured edge fringes, dark leakage,
  contrast intervals and separate hardware-minus-ideal/model residuals.
- Four-bit walk outcomes give sixteen labeled populations, fifteen Z-parities,
  Hamming shells and a classical collision estimator. Counts do not recover
  complex amplitudes. Frames represent separately prepared prefixes.
- Eight rank sectors show coefficient-normalized success and reconstructed norm
  views near exceptional parameters, with kernel and bright references.
  Finite noisy observations test bounded norm predictions rather than exact
  rank, exact zeros or global topology.
- Joint errors and covariance use complete shot vectors within each PUB.
  Equal shot indices in different PUBs remain unpaired. Resampling keeps a
  within-PUB vector intact; exploratory correlations remain descriptive until
  their uncertainty and multiplicity are qualified.

The [measured folded diagnostic](folded-job-review.md) and its
[figure](folded-job-review.svg) already demonstrate a useful result: the two
odd-label no-feedback residuals reverse the sign found in the other fourteen
arms. The [interpretation and source review](../../literature/notes/reality_ripple_measurement_design.md)
connect that observation to falsifiable model tests and the planned geometry.
A reality ripple has an operational meaning here: a controlled intervention
changes a recorded distribution relative to a specified reference. The exact
algebra predicts the field; hardware supplies its measured realization and
residuals; visual geometry makes those quantities inspectable.

Physical execution follows explicit approval of the two linked cases under
[AGENTS.md](../../AGENTS.md). Preparation submitted zero physical QPU jobs.
