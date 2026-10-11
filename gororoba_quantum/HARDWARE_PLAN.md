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
`results/live/2026-10-11T062204.877756Z` at source `4b5dd78`. All four records
are submit-free noise-model runs. The schema-5 run uses `--max-pending 300`,
selects Kingston for all seven groups, and archives the exact 14 static and six
dynamic fused PUBs. The explicit dry-run queue bound qualifies the fused
execution path but does not establish default-policy submission readiness.

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
   same-kind group the two placements needed for its replica-0 reference
   before allocating surplus rounds. Replicas of one group stay one CZ hop
   apart; groups that share a PUB occupy disjoint physical qubits. The record
   retains the selected candidate indices, scores, attempted-combination
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
  it does not attribute crosstalk to one group. The noise model puts the
  difference at zero.
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
along inside a PUB at no extra shots. Fusion reduces the full program from 38
logical execution entries to 20 PUBs, 14 static and 6 dynamic, so 4096 shots
per PUB produce 81,920 executions. The project has not measured its own
shot rate; the literature bounds it between about 1,000 shots/s for many-twirl
runs (literature/notes/2505.22629.md) and 4,900 shots/s derived from
literature/notes/2507.08088.md, which puts the full program between 17 s and
82 s plus job overhead.

| job | groups | PUBs | shots | at 4,900/s | at 1,000/s |
|---|---|---:|---:|---:|---:|
| dynamic | folded QPE, hybrid Shor | 6 | 24,576 | 5.0 s | 25 s |
| static | design A, fringe, design C 8/16/32 | 14 | 57,344 | 12 s | 57 s |

## Path to the first submission

1. **Default-policy refresh.** Run the schema-5 fused-PUB path without a queue
   override when at least one system passes `--max-pending 25`. Use that record
   as the written case's current execution evidence; retain `232219` as the
   historical schema-4 qualification under its explicit 250-job dry-run bound.
2. **Written case.** The case states the job split, the fused PUB count, the
   fresh dry run's predictions, and the seconds bound from the table above,
   and waits for approval (AGENTS.md).
3. **Dynamic job first.** It is the smaller job and carries the questions only
   hardware answers: hybrid Shor admission, concurrent feed-forward across
   packed replicas (the global packing comparison), feed-forward latency from the
   execution spans, and the project's own shot rate, measured by the job's
   usage seconds. That rate replaces the literature bounds before the static
   job is costed.
4. **Static job.** Submitted with --twirl and a DD sequence only when the
   case argues that the hardware-versus-model gap with them on is the
   question; otherwise both stay off so the first static measurement compares
   directly with the noise model.

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

- **Parallel feed-forward.** Hardware handling of three or more simultaneous
  if_else branches is unmeasured; the shared replica-0 reference detects a
  global packed-workload cost without attributing it to one group.
- **Drift during the job.** A calibration update inside a PUB's execution
  span removes its replayed and corrected views; packing shortens the job and
  so narrows that window.
- **Layout structure the model omits.** Measured layout variance above the
  prediction, or a flagged replica, marks hardware the exclusion policy
  missed; the replicas still report, and the flag names the qubits.
