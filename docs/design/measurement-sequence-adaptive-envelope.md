# Measurement-sequence pinching: calibration-adaptive approval envelope

Status: design v3.1. v1 and v2 each received an adversarial self-review, a Codex (gpt-daybreak-blue-latest) review and
an advisor review (reports under the ignored `docs/local/reviews/`); v3 answers the v2 review's five P1 and eleven P2/P3
findings (A to P), and v3.1 answers the scoped v3 re-check (B, C and E refuted, a new aggregate-cap P1). Nothing here has run. Every charge figure is the planner's, and every measurement names its record.

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

The owner approves an envelope: a versioned, machine-readable `envelope.json` that a dry run writes and the written case
is generated from. It binds the experiment digest and the pinching analysis digest, the family definition (arms, N grid,
signs, member list and order, control members), shots, seeds (`seed_transpiler` 20261010 and its count, the simulator
seed), Sampler policy (twirling and dynamical decoupling off, `init_qubits` true), the repetition delay and its
fallback, the IBM Cloud instance, the dependency versions, the backend (ibm_kingston only), the layout function and its
width tiers, the replan bound, the per-attempt ceilings, and the code digest of the constructor.

The constructor is a pure function `plan(snapshot)` of one canonical snapshot: the backend configuration and properties
JSON exactly as the service returns them, plus the pending-job count, serialized sorted and compact. Its output is the
full submission plan: the ordered layout, QPY bytes, the PUB, batch and classical-register manifest, the effective
Sampler options, shots, the repetition delay, the planner price and the ceiling. The plan digest is the sha256 of that
plan's canonical serialization.

At submit time live_run takes a snapshot, computes `plan(snapshot)`, proves its compiled ideals, re-reads the
calibration and recomputes the plan on the fresh snapshot. The submission invariant is equality: the sent bytes and
options equal `plan` of the last snapshot taken before the call. Any change of the plan digest between consecutive
snapshots, whether it moves the layout, the QPY, the manifest, the options or the price, counts as a replan; the run
re-plans at most 3 times and refuses on a fourth change (Finding A). The record keeps every snapshot's canonical bytes,
every plan and its digest, and the envelope digest. A gate rebuilds the Target from each retained snapshot, re-applies
`plan` and compares its QPY and manifest with the sent bytes byte for byte; a rebuild that differs fails the gate, which
is also the falsifier of the snapshot serializer (Findings A and N).

No provider code separates a refused repetition delay from an overrun ceiling. The retained Kingston failures all
report 1305 (`results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md`): the two 0 us jobs (`2026-10-18T201601.788510Z`,
`201618.987131Z`) ran no circuit, reported zero `circuits_execution_time_ns` and billed 2 s under a 5 s ceiling, while
the two 20 us jobs at 100,000 shots (`2026-10-18T213733.601097Z`, `213828.038774Z`) executed shots and billed 5 s
against a 6 s ceiling, an overrun of about 6 s of shot loop. At 32768 shots the two 20 us controls completed with about
1.02 s of circuit time each (job metrics under their `raw/`). The retained evidence therefore separates the two cases by
execution, not by code, on two jobs each.

The fallback runs in `--collect` on the known attempt-1 job id (Finding B). Collect sends attempt 2 at 50 us only when
attempt 1 is in ERROR with code 1305, its job metrics report zero or absent `circuits_execution_time_ns`, and its final
billed charge is at most 3 s (the 2.3 s planned job overhead rounded up); any other terminal state, including a 1305
with executed circuit time, ends the envelope, and a further attempt needs the owner. A 1602 or 8030 on attempt 1 also
triggers attempt 2, since both name an unsupported delay. The approval marker becomes per attempt:
`approval-consumed-attempt-1.json` before the first call, `approval-consumed-attempt-2.json` (exclusive create, naming
the attempt-1 job id, its error code, its circuit time and its billed charge) before the second. `_recovery_tags` adds
the repetition delay, the attempt index and the envelope digest to the batch identity, so the two attempts never share
a recovery tag.

A stalled attempt bills, so the envelope binds an aggregate cap, `envelope_cap = ceiling_1 + ceiling_2`, in
`envelope.json` (new P1 of the v3 re-check). Attempt 1 is admitted when the account's remaining seconds minus the reserve
cover `envelope_cap`; attempt 2 is admitted only when the remaining seconds read at collect, minus the reserve, cover
attempt 1's attributed final charge (its ceiling while the charge is unattributed) plus `ceiling_2`, and that sum stays at
most `envelope_cap`.

The per-batch eligibility gate stays, with `--max-pending` set by the owner in the case.

Doctrine: root AGENTS.md ("the fresh plan must match the record") and qpu-submission.md change for envelope records
only; every other family keeps value binding. The owner ratifies that change separately from approving a run.

Falsifiers: the envelope gate accepts a mutated member angle, a deleted member or control, a permuted classical
destination, twirling on, a deleted terminal reset, a layout other than `plan(snapshot)`'s, or a plan whose options
differ; two snapshots with the same layout and one changed constructor-relevant Target field yield different QPY
without a counted replan; a collect on an attempt-1 job in DONE or in ERROR with any code other than 1602 or 8030 sends
attempt 2.

## Layout rule and width

`rule(snapshot)`: eligible qubits are those the Target does not exclude with readout error at most 0.01, sx error at
most 1e-3, T1 and T2 at least 20 us, and `prob_meas1_prep0` at most 0.02; scan them in ascending readout error with ties
by index and keep a qubit at coupling-graph distance at least 3 from every kept qubit, until W are kept. Fewer than W
eligible qubits refuses.

Distance 3 is a property of the Target's CZ coupling graph only: no two kept qubits are adjacent or share a neighbor.
It claims nothing about readout-resonator, control-line or frequency-collision topology, which the in-job crosstalk
members below measure instead (Finding M). `prob_meas1_prep0` is the calibration's ground-state readout error, a
readout-channel screen; the shot-history bound comes from the in-job reset controls below, not from this threshold
(Finding F).

W is the largest tier of 32, 24 and 16 that satisfies all of:
- admission: at 8192 shots and 17 endpoints per qubit the measure-minus-unitary contrast radius reaches its 0.055
  half-width at 44 qubits, so every tier passes;
- size: every tracked file the run writes (`record.json`, the plan and snapshot files, `collect.json`) stays under 45 MB
  and the run directory, raw shot files included, under 400 MB (the 8-qubit dry run writes a 17.9 MB `record.json`;
  GitHub refuses files over 100 MB);
- time: the whole submit invocation, three replans at the measured per-plan proof time included, fits in 20 minutes,
  under the 30 to 40 minute republish cadence.

The envelope dry run measures each tier on the live Kingston calibration with the implemented workload (end reset and
control members included) and records the chosen tier and the losing tiers' measured limits (Findings I, J, K). A tier
rule replaces an integer search because the size and time limits move with the workload, not with one qubit.

What width buys. `pooled_z` adds the gate-model systematic linearly (shared across qubits), so the pooled departure
standard error is flat in width (0.0168 at 8 qubits, 0.0167 at 44). Width buys per-qubit coverage and the count rule.
Splitting the systematic into a shared offset (the diagnostic's mean residual +0.011) and an independent part (about
0.0105) would make width buy pooled power; that is a new preregistered model with its own null calibration and is not
part of this envelope.

## Repetition delay, shot history and reset controls

Attempt 1 runs at 20 us; 50 us only as the collect-time fallback above. Two Kingston controls ran at 20 us
(`results/live/2026-10-18T214519.655411Z` x_history and `2026-10-18T220218.089776Z` prep0, 148 qubits, 32768 shots,
billed 3 s each under an 8 s ceiling). Their readout-corrected difference, the effect of the preceding shot ending in
`|1>`, has mean -0.0003 and median +0.0006; five qubits exceed 0.01 (q62 +0.054). The two jobs ran 17 minutes apart, so
the spread also carries drift. At 50 us the spread is about a third as large; at 250 us it vanishes.

Execution iterates column-wise over a job's circuits and IBM guarantees no circuit order, so a circuit's predecessor is
unknown. Every member therefore ends with a `reset` of each measured qubit after its final measurement, and
`init_qubits` adds the service's own initialization before the next shot. The reset follows the recorded readout, so the
arms' physics before the final measurement is unchanged, and the exact oracle already enumerates reset branches without
adding classical bits. Every member then holds a mid-circuit operation, so the family runs as one dynamic job.

The erasure is measured, not assumed (Finding C). Two control members run on every selected qubit in the same fused
PUBs: `x; measure; reset; measure` and `measure; reset; measure`. Each control's second bit is the reset residual from a
`|1>` and a `|0>` start on that qubit, read inside the same job and independent of circuit order; their readout-corrected
difference bounds the history a terminal reset passes on, conservatively, since `init_qubits` resets again before the
next shot. The screen is an equivalence rule (Finding C): a qubit stays usable only if the upper end of its two-sided
confidence interval on the absolute readout-corrected residual difference, at family alpha 0.05 Bonferroni-split over the
W qubits, lies below 0.0094, half the 0.0188 bound floor; every other qubit is withheld and reported. The margin uses the
fixed bound floor, not the departure floor, because the departure floor's in-job term moves with the residuals the
screen protects. At 8192 shots and a 1% residual the difference's standard error is about 0.0016 before readout
correction, so the bound passes a qubit whose residual difference is below about 0.004 at W = 32; the envelope dry run
reports the readout-corrected standard error per qubit before the tier is chosen. A gate requires every member's compiled QPY to retain its
terminal resets and controls, and a reset-deletion mutation fails it.

The ro0 member's excited fraction stays a reported readout check against `prob_meas1_prep0`, not the history bound
(Finding G).

## Floor, device rule and crosstalk

On Kingston the departure floor is max(the bound floor, the rms of the usable qubits' readout-corrected unitary N = 16
residuals in the run); `evaluate()` already computes that maximum. The bound floor is 0.0188, the rms over the eight
main qubits of the 250 us diagnostic (0.0152 over all 38 qubits). At 20 us the unitary member carries the end reset and
a shorter delay; the in-job term measures that run's residual, and the bound term keeps the floor from falling below
the diagnostic's.

The pooled z keeps the code's convention: statistical errors in quadrature, the shared gate-model systematic linearly.
The count rule fires when at least max(2, ceil(0.1 W)) informative qubits depart in the same direction.

Null calibration (Finding D). A preregistered stochastic null replays the complete decision pipeline at the chosen W:
binomial shot noise on every member and control, a common offset of +0.011 plus an independent per-qubit part of 0.0105,
the same-run rms floor, the informative filter, execution-time withholding, the reset-control and crosstalk withholding,
and both verdict directions of both the pooled test and the count rule. The reset screen is the equivalence rule
above and the crosstalk screen the K-pattern dispersion test, each with its own shot noise in the replay. Its seed is a QRNG draw cited by index, its
replicates are numpy-batched with the scalar bit-equality gate of `docs/runbooks/vectorized-fits.md`, and its result is
a 95% upper bound on the family-wise false-fire rate, which must lie below 0.01. An exploratory unseeded run of the
pooled test and count rule alone fired zero times in 20000 replicates per cell at W = 8 to 44 (95% upper bound 1.5e-4);
the preregistered replay replaces it.

Readout crosstalk (Finding E). The measure members put each selected qubit's neighbors in mixed, shot-dependent states,
and no fixed pattern pair covers that mixture: opposite-signed neighbor effects can cancel in two checkerboards and
add in another configuration. K pattern members therefore prepare the selected qubits in states drawn independently
and uniformly from a QRNG draw cited by index, one bit per qubit per pattern, and measure all of them. Each qubit's
assignment error is then estimated over K random neighbor configurations, the same mixture the measure members present,
and the readout correction of the measure members uses that pooled estimate. A qubit's configuration dependence is
tested directly: its error count across the K patterns against the binomial dispersion its pooled rate predicts, a
chi-square test with K - 1 degrees of freedom at family alpha 0.05 Bonferroni-split over the W qubits. A failing qubit is
withheld before the device test reads any measure-member outcome, so the device verdict's selection uses only the
readout and pattern members. K is the smallest value whose planner charge adds at most 10% to the family's, with a
floor of 8; the envelope dry run prices K and records it, and the null calibration includes the pattern withholding.

Execution-time eligibility (Finding H). The analysis reads every execution start's properties that `collect` records
for every PUB that contributes to a qubit. A qubit stays usable only if it passes `rule`'s eligibility on each of them;
a missing start or a calibration that changes within the job between PUBs fails it closed. The device verdict needs at
least 8 usable qubits after every withholding step; below that the run reports per-qubit results and no device verdict
(Finding L).

## Charge

Recomputed from the envelope dry run through `budget_plan` for each width tier, with the end reset, the control members
and the per-shot initialization, and filled in the table below. One client-side Sampler job per attempt; the ceiling is
`ceil(1.5 * planner charge)`, which a gate recomputes from the retained plan. The planner charge is an estimate, not
billing: the service can split one job into sub-jobs and charge about 2 s of overhead each
(`docs/notes/ibm_heron_platform.md`), and no submit-free evidence bounds that split, so the case states the ceiling as
the bound and the planner value as the expectation (Finding O). The case also states `envelope_cap`, the two
attempts' summed ceilings, as the most the envelope can bill.

| W | Planner charge at 20 us | Ceiling 1 | Planner charge at 50 us | Ceiling 2 | envelope_cap | Largest tracked file | Run directory | Submit invocation |
|---|---|---|---|---|---|---|---|---|
| 16 | | | | | | | | |
| 24 | | | | | | | | |
| 32 | | | | | | | | |

The backup instance reports 412 s remaining; the primorial-coherence branch's run (`results/live/2026-10-26T045124.175747Z`,
job dbfdotnpc3tc739n8nm0, 23 s) shares the instance, and the branch that merges second regenerates its job inventory.

## Sequence

1. One Codex pass on the v3.1 dispositions of B, C, E and the aggregate cap, answered Fixed, Refuted or Boundary; the
   pieces A and D settled start implementation in parallel.
2. Implementation: `envelope.json` and its schema, the canonical snapshot and plan digest, the equality and rebuild gate,
   `rule`, the end reset, the reset and crosstalk control members, the per-attempt approval markers and recovery tags,
   the collect-time fallback, execution-time eligibility, the stochastic null, the doctrine edit, and the stale
   "eighteen endpoints" prose in `diagnostic_experiments.py` corrected to seventeen (Finding P); tests and lanes.
3. The envelope dry run on the live calibration, which fills the charge table and chooses the tier, and the null
   calibration at that tier.
4. The written case generated from `envelope.json`, with the doctrine change as its own question.
5. On approval, the submission on the live calibration, the collection and the preregistered analysis.
