# Hardware plan

This plan joins the project's two hardware programs -- the Cayley-Dickson
witnesses (DESIGN_NOTES.md) and hybrid Shor order finding (HYBRID_SHOR.md) --
into one submission path under the 600 s rolling QPU budget. The packed-replica
statistics and QPU-cost quantities come from
`results/live/2026-10-10T222132.627032Z` at source `02a5b4b`. Live discovery,
capability admission, filtered routing, and single-layout evidence come from
`results/live/2026-10-10T220438.712726Z` at source `0205a61`. The combined path
qualification comes from `results/live/2026-10-10T232219.919322Z` at source
`584a78d`. The fused submission-path qualification comes from
`results/live/2026-10-11T071616.724800Z` at source `b89fdf6`. All four records
are submit-free noise-model runs. The schema-5 run uses `--max-pending 300`,
selects Kingston for all seven groups, and archives the exact 14 static and six
dynamic fused PUBs. The explicit dry-run queue bound qualifies the fused
execution path but does not establish default-policy submission readiness.

The [bounded experiment-design path](QPU_OPTIMIZATION.md) adds matched
folded-QPE controls and the labeled N=21 feedback diagnostic. Its schema-7
records retain explicit observables, conditional statistical admission,
charged-time assumptions, and aggregate invocation ceilings. Historical
records below retain their original schemas and evidence scope.

The [execution and optimization roadmap](QPU_EXECUTION_ROADMAP.md) reconciles
the three pending scientific cases, current job-mode semantics, retained
QPU-second estimates, and source-grounded accuracy and runtime priorities.

## What each group claims and what refutes it

| group | claim | observable | control or null | falsifier |
|---|---|---|---|---|
| design A (1,2) | the octonion associator sign reaches the readout as a Fano Z-string | P1, ideal 1 | mirror twin; dephased null P1 = 0.5 | P1 at or below 0.5 |
| zero-divisor fringe | a sedenion zero-divisor pair annihilates in interference | dark/bright P0 ratio; fringe visibility and phase | sign-flipped bright control; eight-phase sweep; mirror twins | ratio at the bright level, or fringe phase off 0 |
| design C dim 8, 16, 32 | the associator's Walsh spectrum follows the algebra along the ladder | TVD to the true spectrum against the flipped and omitted predictions | flip and omit controls on the same layout | TVD to true at or above TVD to flip |
| folded QPE mod 15 | eigenphases of x -> 2x mod 15 read out by semiclassical phase estimation | P(correct s) per eigenstate | identity-multiplier null reading 0 | P(correct) at the uniform 0.25 |
| hybrid Shor N = 15 | faithful order finding from \|1> recovers r = 4 and the factors 3 and 5 | factor and order-recovery yield | schedule-matched identity null; exact uniform null 0.297 | the admission rule below fails |

## From calibration to circuits

1. **Discover systems.** `live_run.py` discovers every accessible system unless
   `--backends` names a bounded set. A failed probe remains an inventory entry
   and does not discard successful probes.
2. **Refresh one coherent snapshot.** The runner refreshes each backend once,
   then reads status, configuration, capabilities, the rebuilt Target, and the
   properties cached by that refresh. It excludes every qubit and CZ edge
   outside `QUALITY` or flagged faulty. Record `220438` excludes 11 qubits and
   16 directed edges on ibm_fez, 7 and 24 on ibm_kingston, and 31 and 20 on
   ibm_marrakesh. Policy thresholds identify every exclusion; faulty flags
   identify none. The eligibility gate records ibm_marrakesh as ineligible
   because its status message is `maintenance`.
3. **Admit and route logical circuits.** The runner derives width, operations,
   control flow, and static or dynamic kind from the circuits built in the
   current process. A copy of the fresh Target removes degraded placements
   before layout and routing. Eight transpiler seeds per group and backend
   compete, and the best three per backend compile the controls onto one
   layout. The planner retains those candidates for coupled selection rather
   than finalizing each group independently. Record `220438` selects
   ibm_kingston for every group.
4. **Validate routed instructions.** Recursive support checks validate fixed
   parameters and nested control-flow instructions in every routed primary,
   control, and mirror against the original fresh Target. A failure removes
   that routed candidate from the coupled search.
5. **Allocate one placement pool.** `packing.py` enumerates each candidate
   pattern's floor-qualified embeddings in the admitted CZ graph. A finite
   best-first search ranks candidate combinations by their combined log score
   and advances to the next combination when exact joint placement or fusion
   fails. A round-fair backtracking allocator gives every same-backend,
   same-kind group the two placements needed for its replica-0 reference.
   The search considers all required placements together before committing
   any placement, then allocates surplus rounds. Replicas of one group stay
   one CZ hop apart in the admitted routing graph. The default
   `cross_group_buffer=true` also excludes every physical CZ neighbor of a
   different group's qubits, including couplers excluded from routing, so
   groups that share a PUB remain disjoint and nonadjacent. An explicit
   `--no-cross-group-buffer` changes that cross-group policy. The record
   binds the selected policy and retains candidate indices, scores, attempted-combination
   count, and a bounded rejection sample. An explicit
   `--replica-floor` governs every group; otherwise a group's declared floor
   applies, with 0.9 as the default and 0.8 for hybrid Shor.
6. **Fuse the execution PUBs.** Row zero combines every group's packed
   primary. When isolated references are enabled and placement provides more
   than one replica, row one combines each group's primary on replica 0,
   forming one shared global reference workload. Later rows align the
   remaining members and mirrors in group order. Stable outer register
   prefixes preserve each component and replica boundary. The full default
   surface therefore maps 29 logical static entries to 14 static PUBs and 9
   logical dynamic entries to 6 dynamic PUBs when all groups of a kind select
   one backend.
7. **Derive and bind execution requirements.** The record retains the logical
   entry requirements, joint-placement evidence, fused-PUB cardinalities, and
   ordered PUB-to-component manifests. `isa.qpy` contains the exact fused
   circuits sent to Runtime. One result-complete backend-and-kind cluster must
   fit the 10-million-execution Sampler job bound. Runtime 0.50's deprecated
   `IBMBackend.max_circuits` property always returns `None` and does not define
   an additional submission limit.
8. **Revalidate live configuration.** Before a ledger becomes immutable,
   `--submit` repeats cross-system discovery and deterministic selection. Any
   change to the approved backend, layout, replica maps, packed circuits,
   capabilities, exclusions, or used calibration values writes a revised
   submit-free record and QPY archive, then stops for a new written case and
   explicit user approval. An unchanged approved plan refreshes again
   immediately before every batch and stops the affected and later batches when
   the admitted execution surface moves.

## Statistics that decide a result

- **Variance.** Each member's per-shot score splits into shot and layout
  variance with a chi-squared test across replicas; folded QPE adds an
  instance axis. The noise model predicts layout variance of 2e-5 to 4e-4 in
  the primaries, and 3.1e-5 in Shor factor yield, within shot noise (p 0.17).
- **Global packing crosstalk.** One PUB runs all packed primaries and the shared
  reference PUB runs all groups on replica 0. The per-group score difference
  measures the global packed workload against the global replica-0 workload;
  it does not attribute crosstalk to one group. The noise model carries no
  crosstalk, so its difference is shot noise: each replica draws from the
  seed of its position in one batched Aer run. `packing_schedule` compares the
  two PUBs' scheduler residuals as a global packing scheduling cost: the
  packed PUB adds every replica's whole circuit, so measurement, reset,
  pulse-channel, and other controller resources scale with replica count
  alongside feed-forward, and a larger packed residual is attributed to none
  of them without a matched non-feed-forward control.
- **ODR.** The pooled value averages each replica's witness over its own twin
  and needs 16384 shots over all replicas, so packing meets it at the default
  4096 shots for every mirrored group: design A pools 86,016 shots over 21
  replicas (P1_ODR 0.989 in the noise model) and the fringe 24,576 over 6
  (ratio_ODR 0.0064, visibility_ODR 0.988).
- **Admission.** hybrid Shor is interpreted only through its admission rule:
  the primary factor-yield lower bound must exceed the exact uniform null
  (0.297) and the identity-null upper bound must stay below that lower bound.
  The noise model gives [0.483, 0.501] against an identity-null upper bound of
  0.013. Each bound is the union of the replicate t interval and a Wilson
  interval over the pooled shots; Shor's seven replicas put the t multiplier
  at 2.45, where three gave 4.30.

## QPU cost

QPU time scales with PUBs times shots; replicas and cross-group components ride
along inside a PUB at no extra shots. Each collected job measures its own
rate: collection divides the submitted PUB shots (PUB count times shots per
PUB) by the job's final QPU charge from job.usage(partial=False), in submitted
PUB shots per QPU charge second. A measured rate bounds only the workload it
came from; the static job keeps the literature range below until its own
job is collected. Fusion reduces the full program from 38
logical execution entries to 20 PUBs, 14 static and 6 dynamic, so 4096 shots
per PUB produce 81,920 executions. The dynamic job measured 2,730.7
submitted PUB shots per QPU charge second (record
`results/live/2026-10-11T152922.787095Z`: 24,576 PUB shots, 9 s charge),
inside the literature range of about 1,000 shots/s for many-twirl runs
(docs/notes/2505.22629.md) to 4,900 shots/s derived from
docs/notes/2507.08088.md. The job's metrics decompose the charge:
circuit execution took 272.9 us per shot, the backend's 250 us default
repetition delay plus the 22.9 us mean scheduled circuit, and 2.3 s of the
9 s charge lay outside circuit execution. IBM's own estimate for a job
(quantum.cloud.ibm.com/docs/guides/estimate-job-run-time) adds circuit
duration, repetition delay, and per-job overhead, so the static workload is
priced by that model with its own scheduled durations, not by the dynamic
rate; the literature range stays its conservative bound.

| job | groups | PUBs | shots | at 4,900/s | at 1,000/s | measured |
|---|---|---:|---:|---:|---:|---:|
| dynamic | folded QPE, hybrid Shor | 6 | 24,576 | 5.0 s | 25 s | 9 s |
| static | design A, fringe, design C 8/16/32 | 17 | 69,632 | 14 s | 70 s | not run |

The static row uses the two-backend dry run
`results/live/2026-10-11T203535.690679Z`. Its
[written case](../results/live/2026-10-11T203535.690679Z/STATIC_CASE.md)
estimates about 23 s across two jobs. The service ceiling is 90 s per job,
so the two ceilings total 180 s; 90 s does not cap the combined invocation.

## Submission controls

1. **Default-policy refresh.** Run the schema-7 fused-PUB path under
   `--max-pending 25`. The dry run records the selected groups, live
   calibration, exact circuits, and per-job execution ceiling for the case.
   Retained default and static dry runs qualify their recorded plans;
   submission requires a fresh match to the approved record.
2. **Written case.** The case states the job split, fused PUB count, model
   predictions, expected seconds, and per-job ceilings with their combined
   maximum. The `--submit` command names the dry run with `--approved-record`,
   its digest with `--approved-record-sha256`, and the per-job ceiling with
   `--max-execution-seconds`. `--max-total-execution-seconds` caps the sum
   of every backend/kind job's ceiling; `--reserve-seconds` retains quota
   beyond that sum. Diagnostic families also bind their exact signed
   observables, statistical thresholds, and cost assumptions. The fresh
   plan must match the record in digest,
   shots, policy, versions, instance, groups, backends, seeds, layouts,
   replica qubits, fused PUB manifests, calibration at refresh and every
   batch, and QPY bytes. A mismatch writes an `approval_required` record.
   The first batch consumes the approved record's one-attempt authorization.
   Every hardware case requires explicit owner approval.

## Hardware evidence and next cases

The first dynamic job is complete (record
`results/live/2026-10-11T152922.787095Z`, interpreted in its
[adjudication](../results/live/2026-10-11T152922.787095Z/ADJUDICATION.md)).
Hybrid Shor meets its factor-yield admission rule, but order 4 produces the
same yield with and without feed-forward. Folded QPE supplies the recorded
semiclassical inverse-QFT test. The preregistered packing interval reports
equivalence within the margin on one layout; the scheduled feed-forward
round trip is 540 to 584 dt. Folded QPE reads 0.715 against the model's
0.899. Schedule-aware replay explains about a quarter of the gap, leaving
its remaining mechanism to the matched diagnostic experiment.

The hardware queue has three separate cases:

1. **Folded-QPE mechanism ladder.** `--family folded-qpe --optimize`
   compiles four controls for every eigenstate label on a shared initial
   control/work mapping. Exact branch checks validate all sixteen labeled
   laws. The optimizer requires simultaneous precision for twelve raw
   terminal-bit contrasts and accounts for twelve dynamic and four static
   PUBs across two jobs. A fresh admitted dry run and its written
   measurement, control, and time case remain prerequisites for owner
   approval. [QPU_OPTIMIZATION.md](QPU_OPTIMIZATION.md) defines the delay
   intervention and the limits of causal attribution.
2. **N = 21, a = 4 at two phase bits.** `--family n21-feedback --optimize`
   compares the labeled laws `(3, 2, 1, 2)/8` with feed-forward and
   `(3, 1, 1, 3)/8` without it. `qpe_diagnostics.py` verifies those exact
   laws against circuit branches and seeded labeled samples, and rejects
   a swapped-register mutation. The signed score `(0, 1, 0, -1)` gives a
   difference of 1/4; the laws differ by 1/8 in total variation. Order
   recovery remains zero at this resolution. The conditional power gate
   can reject every supplied design, preserving a `design_infeasible`
   record rather than manufacturing hardware readiness. A fresh admitted
   dry run, written distribution-test case, time bounds, and owner approval
   remain necessary before hardware execution.
3. **Static witnesses.** Renew the packed algebraic case independently of the
   folded-QPE diagnostic and N21 admission. Ripple and rank-sector families
   receive complete controls, fresh calibration, statistical admission, and
   separate written cases. Twirling and DD remain off in the matched plans,
   so each static workload tests its own calibration-derived model.
   A changed mitigation policy requires a matching dry run and case.
   Different circuits and placements prevent the static comparison from
   isolating the mechanism of the folded-QPE gap.

## Runtime source authority

- [IBMBackend API](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/ibm-backend)
  defines status, cached versus refreshed properties, Target history,
  `refresh()`, and the removed backend circuit-limit semantics.
- [IBMBackend 0.50 source](https://github.com/Qiskit/qiskit-ibm-runtime/blob/stable/0.50/qiskit_ibm_runtime/ibm_backend.py)
  grounds the refresh and cached-property behavior used by the coherent
  snapshot.
- [Dynamic circuits and control flow](https://quantum.cloud.ibm.com/docs/en/guides/classical-feedforward-and-control-flow)
  grounds the feed-forward circuit surface.
- [Client-side Sampler migration](https://quantum.cloud.ibm.com/docs/en/guides/migrate-to-client-side-primitives)
  grounds the Executor-backed Runtime 0.50 submission path.
- [Qiskit Target API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.Target)
  grounds recursive instruction-support validation.

## Risks

- **Parallel feed-forward.** Measured once: nine concurrent streams against
  two cost 187 dt of schedule on every replica-0 qubit, which the backend
  scheduler tables attribute to 23 dt of initialization alignment, 44 dt of
  broadcast width, and 120 dt of reset stagger on shared readout channels,
  with no measurable fidelity cost on the shared layout. The fidelity
  comparison reports the packed-minus-reference difference with a 95
  percent interval and a two-one-sided equivalence test against a
  preregistered margin of 0.03, beside the distribution-free Hoeffding view
  of the same difference; a run either detects a packing cost, establishes
  equivalence within the margin, or states that it resolved neither, and a
  three-sigma result alone detects a difference and never establishes
  equivalence. Neither comparison attributes a cost to one group.
- **The model-hardware gap.** The calibration-derived Pauli model with
  readout error predicted folded QPE at 0.899 and hardware read 0.715, with
  the excess error in both semiclassical rounds (2.5 and 3.2 times the
  model's). Idle T1 and T2 during the scheduled measurement, round trip, and
  reset, charged by the schedule-aware replay, explain a quarter. The
  remaining discrepancy also varies with layout: two of six hybrid-Shor
  layouts carry a coherent second-bit bias. The diagnostic ladder pins a
  shared initial work-register mapping: (a) the archived circuit; (b) the
  mid-circuit measurement replaced by a calibrated delay with the
  conditional phase applied unconditionally for a prepared label; (c) the
  measurement kept and the feed-forward removed; (d) two-control-qubit phase
  estimation with terminal measurements. Rung (b) against (a) probes both
  measurement backaction and the measurement-dependent correction path,
  including incorrect recorded bits. Rung (d) against (a) compares the
  dynamic segment with a coherent implementation whose added control, gates,
  routing, and terminal readout sites require separate accounting. Each
  prepared phase uses the compiled archived arm's first measurement writer
  to obtain a fresh Target duration, rounded up to timing granularity. The
  compiler verifies that the matching delay uses the same physical writer;
  the record retains per-phase delays and every arm's measurement sites.
  Rung (a) against schedule-aware replay
  measures the residual model error. The case must state these control
  assumptions before attributing a difference to a single mechanism. The
  implemented ladder has sixteen PUBs across separate dynamic and static
  jobs, with one uniform shot tier chosen from the bounded design search.
  Compilation and a submit-free dry run retain Target duration bounds and
  explicit latency/overhead assumptions. Collected backend scheduler
  metadata supplies executed schedules after separately approved hardware
  execution.
- **Drift during the job.** A calibration update inside a PUB's execution
  span removes its replayed and corrected views; packing shortens the job and
  so narrows that window.
- **Layout structure the model omits.** Measured layout variance above the
  prediction, or a flagged replica, marks hardware the exclusion policy
  missed; the replicas still report, and the flag names the qubits.
