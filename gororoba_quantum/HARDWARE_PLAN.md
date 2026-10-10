# Hardware plan

This plan joins the project's two hardware programs -- the Cayley-Dickson
witnesses (DESIGN_NOTES.md) and hybrid Shor order finding (HYBRID_SHOR.md) --
into one submission path under the 600 s rolling QPU budget. The packed-replica
statistics and QPU-cost quantities come from
`results/live/2026-10-10T220435.034757Z` at source `cdb37c4`. Live discovery,
capability admission, filtered routing, and single-layout evidence come from
`results/live/2026-10-10T220438.712726Z` at source `0205a61`. Both records are
submit-free noise-model runs. The records exercise divergent pre-integration
schema-3 contracts, so a schema-4 dry run must qualify the combined path before
a written submission case uses either record as current execution evidence.

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
   compete; the best three compile the controls onto one layout, and the best
   geometric-mean layout score selects the backend and layout. Record `220438`
   selects ibm_kingston for every group.
4. **Validate routed instructions.** Recursive support checks validate fixed
   parameters and nested control-flow instructions in every routed primary,
   control, and mirror against the original fresh Target. A failure advances to
   the next candidate or backend.
5. **Place replicas and references.** `packing.py` embeds the winning pattern
   in the admitted CZ graph, ranks embeddings by the same layout score, and
   places disjoint replicas one qubit apart. Each multi-replica group adds an
   isolated primary on replica 0's qubits as its crosstalk reference. Record
   `220435` places 21 replicas for design A, 18 for design C dim 8, and 3 to 6
   for the five-qubit groups.
6. **Derive execution requirements.** The runner re-derives entry count,
   classical width, static or dynamic kind, packed layouts, and reference
   requirements from the exact circuits written to `isa.qpy`. These values
   describe the execution set after mirrors, replicas, and references exist.
7. **Partition complete groups into job batches.** The partitioner keeps every
   member, mirror, and isolated reference from a group together. It uses
   `IBMBackend.max_circuits` only as a client-reported compatibility bound;
   IBM documents that the value no longer accurately represents the service
   circuit limit. Job-batch partitioning leaves every circuit as a separate
   PUB and does not perform the future PUB fusion below.
8. **Revalidate live configuration.** Before a ledger becomes immutable,
   `--submit` repeats cross-system discovery and deterministic selection until
   one pass stabilizes backend, layout, replica maps, packed circuits,
   capabilities, exclusions, and used calibration values. The runner refreshes
   again immediately before every batch and stops the affected and later
   batches when the admitted execution surface moves.

## Statistics that decide a result

- **Variance.** Each member's per-shot score splits into shot and layout
  variance with a chi-squared test across replicas; folded QPE adds an
  instance axis. The noise model predicts layout variance of 2e-5 to 4e-4 in
  the primaries and none beyond shot noise in Shor factor yield (p 0.66).
- **Crosstalk.** The primary runs alone on replica 0's qubits beside the
  packed run; the noise model puts their difference at zero, so a measured
  difference is crosstalk from packing.
- **ODR.** The pooled value averages each replica's witness over its own twin
  and needs 16384 shots over all replicas, so packing meets it at the default
  4096 shots for every mirrored group: design A pools 86,016 shots over 21
  replicas (P1_ODR 0.989 in the noise model) and the fringe 24,576 over 6
  (ratio_ODR 0.0064, visibility_ODR 0.988).
- **Admission.** hybrid Shor is interpreted only through its admission rule:
  the primary factor-yield lower bound must exceed the exact uniform null
  (0.297) and the identity-null upper bound must stay below that lower bound.
  The noise model gives [0.485, 0.510] against an identity-null upper bound of
  0.020. Each bound is the union of the replicate t interval and a Wilson
  interval over the pooled shots; with Shor's three replicas the t multiplier
  is 4.30, so the replica count is a decision for the written case.

## QPU cost

QPU time scales with PUBs times shots; replicas ride along inside a PUB at no
extra shots. The record holds 38 PUBs, 29 static and 9 dynamic, so the full
program at 4096 shots is 155,648 shots. The project has not measured its own
shot rate; the literature bounds it between about 1,000 shots/s for many-twirl
runs (literature/notes/2505.22629.md) and 4,900 shots/s derived from
literature/notes/2507.08088.md, which puts the full program between 32 s and
156 s plus job overhead.

| job | groups | PUBs | shots | at 4,900/s | at 1,000/s |
|---|---|---:|---:|---:|---:|
| dynamic | folded QPE, hybrid Shor | 9 | 36,864 | 7.5 s | 37 s |
| static | design A, fringe, design C 8/16/32 | 29 | 118,784 | 24 s | 119 s |

## Path to the first submission

1. **Combined schema-4 qualification.** A submit-free live dry run records the
   complete system inventory, logical requirements, admitted routing graph,
   packed execution set, isolated references, variance views, archive identity,
   and batch plan under `live-target-packed-replicas-v1`. Its `planned` state
   and absent `submission` object establish zero QPU jobs.
2. **PUB fusion.** Groups on one backend and job kind share PUBs: entry i of
   every group packs into one circuit on disjoint placements, so the static
   job needs as many PUBs as its largest group (14, the fringe) instead of 29,
   and the dynamic job 6 instead of 9. Placement then allocates one pool of
   admissible qubits across groups, and the per-group decoding is unchanged.
3. **Written case.** The case states the job split, the fused PUB count, the
   fresh dry run's predictions, and the seconds bound from the table above,
   and waits for approval (AGENTS.md).
4. **Dynamic job first.** It is the smaller job and carries the questions only
   hardware answers: hybrid Shor admission, concurrent feed-forward across
   packed replicas (the crosstalk reference), feed-forward latency from the
   execution spans, and the project's own shot rate, measured by the job's
   usage seconds. That rate replaces the literature bounds before the static
   job is costed.
5. **Static job.** Submitted with --twirl and a DD sequence only when the
   case argues that the hardware-versus-model gap with them on is the
   question; otherwise both stay off so the first static measurement compares
   directly with the noise model.

## Runtime source authority

- [IBMBackend API](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/ibm-backend)
  defines status, cached versus refreshed properties, Target history,
  `refresh()`, and the `max_circuits` compatibility warning.
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
  if_else branches is unmeasured; the isolated reference detects a cost.
- **Drift during the job.** A calibration update inside a PUB's execution
  span removes its replayed and corrected views; packing shortens the job and
  so narrows that window.
- **Layout structure the model omits.** Measured layout variance above the
  prediction, or a flagged replica, marks hardware the exclusion policy
  missed; the replicas still report, and the flag names the qubits.
