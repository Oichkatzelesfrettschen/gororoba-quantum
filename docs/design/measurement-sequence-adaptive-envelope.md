# Measurement-sequence pinching: calibration-adaptive approval envelope

Status: design v2, revised after an adversarial self-review, a Codex (gpt-daybreak-blue-latest) review and an advisor
review of v1 (reports under the ignored `docs/local/reviews/`). Nothing here has run. Every charge figure is the
planner's, and every measurement names its record.

## Problem

A Heron r2 approval binds the dry run's calibration values (`docs/notes/ibm_quantum/qpu-submission.md`: the fresh plan
must match the record in layouts, calibration values at the refresh and at each batch, and QPY bytes). ibm_kingston
republishes every 30 to 40 minutes and moves values on some layout qubits at most republishes, so a value-bound
approval survives only while the owner answers within one calibration window. Three approved submissions of the main
pinching case on 2026-10-26 sent nothing:

| Record | Refusal | Cause |
|---|---|---|
| `results/live/2026-10-26T041541.662284Z` | `--max-pending 25` at the per-batch snapshot (31 pending; the planning snapshot read 1) | queue gate |
| `results/live/2026-10-26T044116.003197Z` | values changed between the approved-record check and the first batch | a 33-minute serial compiled-ideal proof (fixed in 879d679) |
| `results/live/2026-10-26T083800.427156Z` | values changed since the dry run | 2 h 41 min between the dry run and the approval |

## Approval contract

The owner approves an envelope: one deterministic constructor with one adaptive input, the layout. The envelope binds
the experiment digest and the pinching analysis digest, the family definition (arms, N grid, signs, member list and
order), shots, seeds (`seed_transpiler` 20261010 and its count, the simulator seed), Sampler policy (twirling and
dynamical decoupling off, `init_qubits` true), the repetition delay and its fallback, the IBM Cloud instance, the
dependency versions, the backend (ibm_kingston only), the layout function and its width W, the replan bound, and the
per-attempt ceiling.

At submit time live_run takes a snapshot, computes `layout = rule(snapshot)`, constructs and compiles the members on
that layout with the bound seeds, proves the compiled ideals, prices the plan, re-reads the calibration and sends. The
submission invariant is equality, not satisfaction: the sent layout equals `rule` of the last snapshot taken before the
batch, and the sent QPY and PUB manifest equal the constructor's output on that layout and Target. If the last snapshot
changes `rule`'s output, the run re-plans on it, at most 3 times; a fourth change refuses. The record keeps every
snapshot's canonical bytes (Target and properties as live_run reads them), the layouts, the QPY per attempt and the
envelope digest, and a gate re-applies `rule` to the recorded snapshot and rebuilds the QPY bytes.

One attempt per approval. The attempt writes `approval-consumed.json` exclusively before its first remote call, as
today. If `sampler.run` raises a delay refusal (1602 or 8030) and the recovery-tag lookup finds no accepted job, the
same invocation rebuilds the plan at 50 us and sends it under the same consumed approval; any accepted job, failed or
not, ends the envelope, and a further attempt needs the owner. This removes the fallback state machine, the cumulative
budget across invocations and the 1305 trigger: a 1305 or 8045 after acceptance is reported, never retried
automatically.

The per-batch eligibility gate stays, with `--max-pending` set by the owner in the case; the 31-pending refusal shows the
queue moves inside minutes. The analysis reads the execution-start properties `collect` records and withholds every
qubit that fails the layout rule's eligibility on them (preregistered), so a job that waits in the queue analyzes only
qubits that were eligible when it ran.

Doctrine: root AGENTS.md ("the fresh plan must match the record") and qpu-submission.md change for envelope records
only; every other family keeps value binding. The owner ratifies that change separately from approving a run.

Falsifiers: an envelope gate that accepts a mutated member angle, a deleted member, a permuted classical destination,
twirling on, or a layout other than `rule(snapshot)` is defective; a recorded snapshot whose rebuilt QPY differs from the
sent QPY is defective.

## Layout rule and width

`rule(snapshot)`: eligible qubits are those the Target does not exclude with readout error at most 0.01, sx error at
most 1e-3, T1 and T2 at least 20 us, and `prob_meas1_prep0` at most 0.02 (q62, whose 20 us shot-history excess read
+0.054, falls out at 0.02 on any calibration that reports its preparation error near its control value); scan them in
ascending readout error with ties by index and keep a qubit at graph distance at least 3 from every kept qubit (no
shared neighbor), until W are kept. Distance 3 keeps the measured qubits off common couplers and spectators. Fewer than
W eligible qubits refuses.

W is the smallest of three measured limits:
- admission: at 8192 shots and 17 endpoints per qubit the measure-minus-unitary contrast radius reaches its 0.055
  half-width at 44 qubits;
- the tracked record: `record.json` stays under 45 MB (the 8-qubit dry run writes 17.9 MB; GitHub warns at 50 MB and
  refuses at 100 MB);
- the compiled-ideal proof at submit stays under 300 s.
Submit-free dry runs at 16, 24 and 32 qubits on the 2026-10-26 Kingston calibration measure the last two (table below,
filled from the runs). A record-schema deduplication that would admit more qubits is out of scope here.

What width buys. `pooled_z` adds the gate-model systematic linearly (shared across qubits), so the pooled departure
standard error is flat in width (0.0168 at 8 qubits, 0.0167 at 44). Width buys per-qubit coverage, the count rule and the
in-job floor's sampling stability (at least 20 usable qubits). Splitting the systematic into a shared offset (the
diagnostic's mean residual +0.011) and an independent part (about 0.0105) would make width buy pooled power; that is a
new preregistered model with its own null calibration and is not part of this envelope.

## Repetition delay and shot history

Attempt at 20 us; 50 us only on the synchronous refusal above. Two Kingston controls ran at 20 us
(`results/live/2026-10-18T214519.655411Z` x_history and `2026-10-18T220218.089776Z` prep0, 148 qubits, 32768 shots,
billed 3 s each under an 8 s ceiling). Their readout-corrected difference, the effect of the preceding shot ending in
`|1>`, has mean -0.0003 and median +0.0006; five qubits exceed 0.01 (q62 +0.054). The two jobs ran 17 minutes apart, so
the spread also carries drift. At 50 us the spread is about a third as large; at 250 us it vanishes.

Execution iterates column-wise over a job's circuits and IBM guarantees no circuit order, so a circuit's predecessor is
unknown. Every member therefore ends with a `reset` of each measured qubit after its final measurement, so each next
shot starts from the reset state whatever the predecessor measured, and the predecessor dependence becomes second order
(reset infidelity times the end-state contrast). The reset follows the recorded readout, so the arms' physics before
the final measurement is unchanged, and the exact oracle already enumerates reset branches without adding classical
bits. Every member then holds a mid-circuit operation, so the family runs as one dynamic job.

Falsifier: the in-job ro0 excited fraction per qubit against the calibration's `prob_meas1_prep0`; a qubit whose ro0
reads more than 3 standard errors above it, with a Bonferroni split over the W qubits, is reported and withheld.

## Floor, device rule and crosstalk

On Kingston the departure floor is max(the bound floor, the rms of the usable qubits' readout-corrected unitary N = 16
residuals in the run); `evaluate()` already computes that maximum. The bound floor is 0.0188, the rms over the eight
main qubits of the 250 us diagnostic (0.0152 over all 38 qubits). At 20 us the unitary member carries the end reset and
a shorter delay; the in-job term measures that run's residual, and the bound term keeps the floor from falling below
the diagnostic's.

The pooled z keeps the code's convention: statistical errors in quadrature, the shared gate-model systematic linearly.
The count rule fires when at least max(2, ceil(0.1 W)) informative qubits depart in the same direction. A null
calibration with the existing synthetic sweep at the chosen W and a common offset of +0.011 reports the false-fire rate
before the case is written.

Readout crosstalk: the existing `readout_crosstalk` statistic (largest absolute correlation of a qubit's final outcome
with another's) withholds a qubit from the device verdict when it exceeds its 3-sigma shot-noise band with a Bonferroni
split over the W(W-1)/2 pairs.

## Charge

Recomputed from each width's dry run through `budget_plan`, with the end reset and the per-shot initialization, and
filled in the table below. One job; the per-attempt ceiling is the planner charge times 1.5, rounded up.

| W | Charge at 20 us | Ceiling | Charge at 50 us | record.json | Proof at submit |
|---|---|---|---|---|---|
| 16 | | | | | |
| 24 | | | | | |
| 32 | | | | | |

The backup instance reports 412 s remaining; the primorial-coherence branch's run (`results/live/2026-10-26T045124.175747Z`,
job dbfdotnpc3tc739n8nm0, 23 s) shares the instance, and the branch that merges second regenerates its job inventory.

## Sequence

1. Width dry runs and the table; null calibration of the count rule at W.
2. One Codex re-review of v2 and an advisor review; another round only if a P1 survives.
3. Implementation: the envelope record and its equality gate, `rule`, the end reset, the synchronous fallback, the
   execution-time withholding, the crosstalk exclusion, the doctrine edit; tests and lanes.
4. An envelope dry run and the written case, with the doctrine change as its own question.
5. On approval, the submission on the live calibration, the collection and the preregistered analysis.
