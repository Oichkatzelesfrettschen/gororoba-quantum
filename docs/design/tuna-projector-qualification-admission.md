# Tuna projector qualification admission

The [campaign peer review](../archive/reviews/tuna-projector-campaign-review.md)
confirms the exact projector derivation and the three executed QX cases, and requires
additional admission checks before hardware acquisition. The user authorized review
followed by execution of the existing three-circuit hardware case. The authorization
covers the [frozen manifest](../../results/quantum_inspire/proposals/tuna-projector-geometry/tuna-qualification/cases.json)
with SHA-256 `d9a41a677a2a4bff4e2d3f4e10c4db2017d41ba1ee910da67960333d151dcfb2`:
all-zero, all-one and geometry, 4096 shots each, 12,288 total, zero expected credits.
The expected execution duration is 14.31264 seconds; the provider ceiling is 300 seconds
per job. Queue time is additional. The scientific question concerns the physical early
measurement register and readout response, which the completed terminal-only emulator
cases cannot measure.

This admission document makes the [design](tuna-projector-geometry.md)'s pilot checks
executable and specifies their boundaries before acquisition. It supersedes the
ambiguous phrase "exceeds the case estimate materially": actual duration is reported
against the estimate, while the provider's 300-second per-job limit is the explicit
execution check. The three source circuits, their manifest and the historical producer
retain their recorded bytes.

## Frozen decision

The analyzer requires all three completed jobs with their expected identities, circuit
hashes, 4096 width-20 ordered shot strings each, matching raw digests and histograms,
finite nonnegative execution times, and individually zero transaction changes. A failed
or incomplete job stops qualification. Collection retains raw bytes before analysis.

For each active terminal qubit in {1,3,4,6,8,9,11,13,14} and each early ancilla bit
17,18,19, the empirical assignment contrast is P(1|prepared one) - P(1|prepared zero).
A contrast of exactly 0.5 passes; a smaller contrast fails. The other eight terminal
qubits remain reported diagnostics. They do not determine admission of the nine-qubit
active instrument. The all-one circuit combines preparation, simultaneous drives,
spectator context and readout; its contrast is an instrument screen, not a pure detector
error measurement.

For each of the three ancillas in each of the three circuits, the fraction of shots
whose early and terminal bits differ must be at most 0.10. Equality passes. Integer
count comparisons determine both thresholds. The analyzer reports failure without
promoting a qualification claim, and retains the result. Failure triggers reassessment;
automatic retries and expansion into successor acquisitions are prohibited.

The source maps classical bit zero to the rightmost character. Ancillas 4,11,6 map to
early bits 17,18,19 and terminal bits 4,11,6 respectively. Manifest maps must match
those identities. A stored ordered-shot digest establishes replay identity, while
histogram agreement alone cannot certify provider shot chronology or independence.

## Admission and interpretation

Local compiler replay binds the complete normalized instruction order, targets, controls,
serializer precision, compiler configuration and implementation sources. The local replay
establishes compiler acceptance; the provider's served pulse schedule remains unknown.
Immediately before guarded submission, compare live topology, gates and compiler configuration
with frozen inputs, and check enabled status, heartbeat freshness, raw support, shot/job/time
limits, account-wide hardware pause, current queue and ledger. Retain timestamped observations.
The standard submission guard rechecks queue and pause while holding its account lock.
Structural drift or a pricing change stops execution.

The [fresh terms observation](../evidence/tuna-projector-geometry/qualification-terms-observation.json)
retains the public account and FAQ statements and the noncommercial-use condition.
The calibration datasource outage remains a limitation. Older exclusions of qubits 6
and 9 in the [experiment notes](../notes/quantum_inspire/experiments.md) and subsequent
[readout recovery](../notes/quantum_inspire/tuna-17.md) describe different observations.
The (3,6,9) triple therefore requires fresh qualification; neither historical failure
nor recovery establishes its present performance.

Passing the pilot establishes only the specified assignment and register-consistency
screens. The fixed angle-to-placement assignment, two calibration states, parallel
replicas, unknown served readout timing and unresolved temporal dependence prevent a
causal projector-geometry or backaction claim.

The historical generator's custom-angle interface and default-only metadata must not
be combined for successor acquisitions. Live admission restricts execution to the frozen
default-angle manifest. A successor must generate angles and measurement-mode metadata
together, validate labels against emitted rotations, and test all six placement permutations.
Four-state context calibration, counterbalancing, timing-matched controls, signed and
mutation controls, gap-response, spectator and leakage diagnostics, and a frozen dependence
and uncertainty model remain required before a full causal campaign.
