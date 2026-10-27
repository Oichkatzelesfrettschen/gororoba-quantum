# Measurement-sequence pinching: calibration-adaptive approval envelope

Status: design v3.3. v1 and v2 each received an adversarial self-review, a Codex (gpt-daybreak-blue-latest) review and
an advisor review (reports under the ignored `docs/local/reviews/`); v3 answers the v2 review's five P1 and eleven P2/P3
findings (A to P), v3.1 answers the scoped v3 re-check (B, C and E refuted, a new aggregate-cap P1), and v3.2 answers
the v3.1 re-check (E refuted again, a fallback falsifier that contradicted the trigger); v3.3 replaces the random
patterns, which the v3.2 re-check showed can align a neighbor's column with the target's, by an orthogonal design. The width-32 run executed on 2026-10-27 and its reset screen withheld every qubit; [the findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md) record the outcome and the margin defect. Every charge figure is the planner's unless it names a billed job, and every measurement names its record.

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

The owner approves an envelope: the dry run's `record.json`, whose `envelope` section (schema `msq-envelope-v1`) the
written case is generated from, bound by the record's sha256. It binds the experiment digest and the pinching analysis digest, the family definition (arms, N grid,
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

The fallback runs after `--collect`, as `live_run.py --envelope-fallback RUN_DIR` with attempt 1's planning flags, on
the known attempt-1 job id (Finding B). It sends attempt 2 at 50 us only when
attempt 1 is in ERROR with code 1305, its job metrics report zero or absent `circuits_execution_time_ns`, and its final
billed charge is at most 3 s (the 2.3 s planned job overhead rounded up); any other terminal state, including a 1305
with executed circuit time, ends the envelope, and a further attempt needs the owner. A 1602 or 8030 on attempt 1 also
triggers attempt 2, since both name an unsupported delay. The approval marker becomes per attempt:
`approval-consumed-attempt-1.json` before the first call, `approval-consumed-attempt-2.json` (exclusive create, naming
the attempt-1 job id, its error code, its circuit time and its billed charge) before the second. `_recovery_tags` adds
the repetition delay, the attempt index and the envelope digest to the batch identity, so the two attempts never share
a recovery tag.

A stalled attempt bills, so the envelope binds an aggregate cap, `envelope_cap = ceiling_1 + ceiling_2`, in the
record's envelope contract (new P1 of the v3 re-check). Attempt 1 is admitted when the account's remaining seconds minus the reserve
cover `envelope_cap`; attempt 2 is admitted only when the remaining seconds read by the fallback step, minus the reserve, cover
attempt 1's attributed final charge (its ceiling while the charge is unattributed) plus `ceiling_2`, and that sum stays at
most `envelope_cap`.

The per-batch eligibility gate stays, with `--max-pending` set by the owner in the case.

Doctrine: root AGENTS.md ("the fresh plan must match the record") and qpu-submission.md change for envelope records
only; every other family keeps value binding. The owner ratifies that change separately from approving a run.

Falsifiers: the envelope gate accepts a mutated member angle, a deleted member or control, a permuted classical
destination, twirling on, a deleted terminal reset, a layout other than `plan(snapshot)`'s, or a plan whose options
differ; two snapshots with the same layout and one changed constructor-relevant Target field yield different QPY
without a counted replan; a collect sends attempt 2 on an attempt-1 job that is not in ERROR, or in ERROR with a code
other than 1602, 8030 or 1305, or in ERROR 1305 with executed circuit time, an unattributed charge or a billed charge
above 3 s; a collect withholds attempt 2 from an attempt-1 job in ERROR 1602 or 8030, or in ERROR 1305 with zero or
absent circuit time and at most 3 s billed. Each conjunct of the 1305 signature has its own mutation test.

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
- time: a plan stays valid until the next send. The submit invocation plans once; a republish re-plans only when it
  moves the rule's qubit set, a dt duration the circuits carry, the capabilities or the exclusions (`envelope_drift`),
  and the pre-send check reads one snapshot in seconds. The plan must finish before the rule's set moves.

The width-32 dry run on the live Kingston calibration (implemented workload, end reset and control members included)
planned in 19.3 min of wall time and 773 s of CPU on a host at load average 21 over 12 CPUs, after the compiled-ideal
proof, the noise simulation, the record encoding and the delay-noise assembly were made parallel or memoized (from
41 min). The rule's qubit set at widths 16, 24 and 32 was the same on the 15:18 and 17:47 PDT calibrations of
2026-10-26, while the width-16 set computed on the 11:06 PDT calibration differs from the 15:18 one in four qubits: the
set moves on a scale of hours. A move during a plan costs a re-plan, and a fourth move refuses before the approval
marker is written, so it spends time, not quota. Width 32 passes every limit, so the tier rule selects it and the
smaller tiers are not measured (Findings I, J, K).

Before each send, `envelope_drift` with the run's arguments recompiles the family on the pre-send snapshot and
compares the fused PUB circuits' QPY digest and manifests with the planned ones; any difference raises a re-plan, so
the sent bytes are the constructor's output on the last snapshot (Finding A). Two reads of one calibration rebuild
identical bytes.

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

Null calibration (Finding D). A preregistered stochastic null (`gororoba_quantum/msq_envelope_null.py`) replays the
complete decision pipeline at the chosen W: binomial shot noise on every member and control, a unitary residual of
+0.011 common to all qubits plus an independent normal part of SD 0.0105 (realized through each qubit's sx error, the
even-under-sign gate error the model propagates), the same-run rms floor, the informative filter, the reset and pattern
withholding, and both verdict directions of both the pooled test and the count rule. Null devices pass execution-time
eligibility by construction, so that screen only removes qubits and is left out. Its seed is ANU QRNG draw
2026-10-26T220128Z index 1; each replicate runs the scalar pipeline under its own `SeedSequence` child, and the
replicates map through the pool. The per-qubit fits keep the replicates from a numpy batch, so the batched-estimator
rule of AGENTS.md does not apply to this null. Its result is the one-sided 95 % Clopper-Pearson upper bound on the
family-wise false-fire rate, which must lie below 0.01: 299 clean replicates reach it. An exploratory unseeded run of the
pooled test and count rule alone fired zero times in 20000 replicates per cell at W = 8 to 44 (95% upper bound 1.5e-4);
the preregistered replay replaces it.

Readout crosstalk (Finding E). The screen asks one question: does a qubit's final readout depend on the states of the
other selected qubits, at fixed own state? K pattern members each prepare every selected qubit in `|0>` or `|1>` and
measure all of them. The pattern bits are the non-constant columns of a normalized Hadamard matrix of order K, the
smallest Paley order above the width tier (K = 20, 28 and 36 for W = 16, 24 and 32;
`diagnostic_experiments.MSQE_PATTERN_DESIGNS`). Every column holds K/2 ones and every two columns agree in exactly K/2
rows, so within the K/2 patterns of either own state of a qubit, every other selected qubit sits in `|1>` in exactly K/4
of them: no neighbor's column can coincide with or complement the target's, which independent random columns allowed
with probability 2/C(12,6) per pair. A QRNG draw (`MSQE_PATTERN_SEED`) permutes the columns over the layout ranks and
the rows into execution order. The analysis tests each own state separately, so the asymmetric channels P(1|0) and
P(0|1) never mix: within the K/2 patterns of one own state, the qubit's error counts against the binomial dispersion of
their pooled rate, a chi-square test with K/2 - 1 degrees of freedom at family alpha 0.05 Bonferroni-split over the 2W
(qubit, own state) tests. A failing qubit is withheld before the device test reads any measure-member outcome, so the
device verdict's selection uses only the readout and pattern members. A gate checks the realized pattern matrix: every
column balanced, every column pair orthogonal, every other rank at K/4 within each (rank, own state) stratum.

The patterns cover configuration dependence; they do not reproduce the measure members' state distribution (the N = 16
measure arm's final P0 is 0.89 and its mid-circuit outcomes follow a low-flip chain), and they do not supply the readout
correction, which stays with the own-state ro0 and t1 members of the base family. Each neighbor sits in `|1>` in half of
every stratum, more often than in any measure member, so a neighbor shift reaches the screen at least as strongly as it
reaches the departures. Power, with every pair exactly balanced: a single-neighbor shift of 0.005 (about a quarter of
the bound floor) at a 1% error rate and 8192 shots is detected with probability 0.996 at W = 16, and 1.000 at W = 24 and
32 (noncentral chi-square); a 0.0025 shift with 0.26 to 0.42.

Execution-time eligibility (Finding H). The analysis reads every execution start's properties that `collect` records
for every PUB that contributes to a qubit. A qubit stays usable only if it passes `rule`'s eligibility on each of them;
a missing start or a calibration that changes within the job between PUBs fails it closed. The device verdict needs at
least 8 usable qubits after every withholding step; below that the run reports per-qubit results and no device verdict
(Finding L). `msq_envelope_analysis.collected` withholds the pinching analysis entirely below 8 kept qubits rather than reporting per-qubit results; a successor implements the per-qubit report.

## Charge

Recomputed from the envelope dry run through `budget_plan` for each width tier, with the end reset, the control members
and the per-shot initialization, and filled in the table below. One client-side Sampler job per attempt; the ceiling is
the case's choice, at least `ceil(1.5 * expected charge)`. The planner prices each PUB as shots times the scheduled circuit plus the repetition delay; the two retained 20 us Kingston controls (`results/live/2026-10-18T214519.655411Z`, `2026-10-18T220218.089776Z`) ran 8.98 us per shot longer than that model, so the expected charge adds 9 us per shot. The planner charge is an estimate, not
billing: the service can split one job into sub-jobs and charge about 2 s of overhead each
(`docs/notes/ibm_heron_platform.md`), and no submit-free evidence bounds that split, so the case states the ceiling as
the bound and the planner value as the expectation (Finding O). The case also states `envelope_cap`, the two
attempts' summed ceilings, as the most the envelope can bill.

| W | Planner charge at 20 us | Ceiling 1 | Planner charge at 50 us | Ceiling 2 | envelope_cap | Largest tracked file | Run directory | Submit invocation |
|---|---|---|---|---|---|---|---|---|
| 16 | not measured | | | | | | | |
| 24 | not measured | | | | | | | |
| 32 | 31.2 s (one 88-PUB job); expected 37.7 s | 57 s | 52.8 s; expected 59.3 s | 90 s | 147 s | 15.3 MB | 20 MB | 19.3 min under load |

The collected width-32 run billed 38 s with 35.36 s of circuit time; its `collect.json` is 42.4 MB and its run directory, `raw/` included, 361 MB, so the table's size columns describe the submit-free dry run. The backup instance reported 369 s remaining at the width-32 dry run (`results/live/2026-10-27T012214.435220Z`); the primorial-coherence branch's run (`results/live/2026-10-26T045124.175747Z`,
job dbfdotnpc3tc739n8nm0, 23 s) shares the instance, and the branch that merges second regenerates its job inventory.

## Sequence

1. One Codex pass on the v3.1 dispositions of B, C, E and the aggregate cap, answered Fixed, Refuted or Boundary; the
   pieces A and D settled start implementation in parallel.
2. Implementation: the record's envelope section, the canonical snapshot and plan digest, the equality and rebuild gate,
   `rule`, the end reset, the reset and crosstalk control members, the per-attempt approval markers and recovery tags,
   the collect-time fallback, execution-time eligibility, the stochastic null, the doctrine edit, and the stale
   "eighteen endpoints" prose in `diagnostic_experiments.py` corrected to seventeen (Finding P); tests and lanes.
3. The envelope dry run on the live calibration, which fills the charge table and chooses the tier, and the null
   calibration at that tier.
4. The written case generated from the record's envelope section, with the doctrine change as its own question.
5. On approval, the submission on the live calibration, the collection and the preregistered analysis.
