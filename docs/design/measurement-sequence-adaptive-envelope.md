# Measurement-sequence pinching: calibration-adaptive approval envelope

Status: design under review. Nothing here has run; the numbers are planner prices and retained measurements, each
named with its source.

## Problem

A Heron r2 approval binds the dry run's calibration values (`docs/notes/ibm_quantum/qpu-submission.md`: the fresh plan
must match the record in layouts, calibration values at the refresh and at each batch, and QPY bytes). ibm_kingston
republishes its calibration every 30 to 40 minutes and changes values on some layout qubits at most republishes, so
an approval outlives one calibration window only by luck. Three approved submissions of the main pinching case on
2026-10-26 sent nothing:

| Record | Refusal | Cause |
|---|---|---|
| `results/live/2026-10-26T041541.662284Z` | `--max-pending 25` (31 pending) | queue gate |
| `results/live/2026-10-26T044116.003197Z` | values changed between the check and the first batch | a 33-minute serial compiled-ideal proof (fixed in 879d679) |
| `results/live/2026-10-26T083800.427156Z` | values changed since the dry run | 2.7 hours between the dry run and the approval |

The repetition delay dominates the charge. The 2026-10-26T083828.143913Z dry run prices 50 PUBs at 8192 shots: the
circuits last 4 to 72 us (the T1 series up to 204 us), and the shot loop costs 113.9 s at the 250 us default, 32.0 s at
50 us and 19.7 s at 20 us, plus 2.3 s per job. A fused PUB lasts about one repetition cycle per shot whatever its
qubit count, so qubits added to the layout cost almost nothing.

## Approval contract

The owner approves an envelope instead of a calibration. The envelope binds:

- the source and analysis digests (`live_run.experiment_digest`, the pinching analysis digest), the family definition
  (arms, N grid, signs, member list), the shots (8192), the IBM Cloud instance (`instance_sha256_12`) and the
  dependency versions;
- the allowed backends (ibm_kingston; ibm_fez as the second, which the owner may strike);
- the layout rule below and its bounds (at least 8 and at most `MAX_QUBITS` qubits);
- the repetition-delay schedule below;
- the per-attempt service ceiling and the total ceiling over every attempt;
- the analysis rule, including the in-job floor below.

At submit time `live_run` takes a fresh snapshot, applies the layout rule to it, compiles, proves the compiled ideals,
and re-reads the calibration within seconds of the batch. The submission invariant is that the layout it sends
satisfies the rule against that last snapshot and the priced charge fits the ceilings. It does not require the layout
to equal the dry run's. A republish between the plan and the batch re-plans inside the same envelope (at most
`MAX_REPLANS` times) instead of refusing, because the approval names no calibration value. The record stores the
envelope digest, every snapshot, the layout the rule chose and the values it read, so the run stays reproducible.

The first attempt writes `approval-consumed.json` with its job ids; a fallback attempt appends to it, and a third
invocation sends nothing. The queue gate becomes a wait: the submission sends whatever the queue length, because an
envelope approval cannot go stale while a job waits, and the in-job controls below calibrate the job at its execution
time.

Falsifier: a submission whose sent layout violates the rule against the last snapshot, or whose charge exceeds a
ceiling, is a defect; the record holds both, and a gate re-applies the rule to the recorded snapshot.

This contract departs from the root AGENTS.md text "the fresh plan must match the record" and from
qpu-submission.md; the change that implements it rewrites both for envelope records and keeps value binding for every
other family.

## Layout rule

Eligible: not excluded by the live Target, readout error at most 0.01, sx error at most 1e-3, T1 and T2 at least
20 us (`measurement_sequence_scatter.eligible`). Scan the eligible qubits in ascending readout error, ties by index,
and keep a qubit coupled to no kept qubit, up to `MAX_QUBITS`. On the 2026-10-26 11:06 PDT Kingston calibration the
rule keeps 50 of 73 eligible qubits (ibm_fez 53, ibm_marrakesh 40).

The eight qubits of the earlier main design (91, 118, 95, 61, 147, 151, 59, 89) carry no special standing: the floor
below is measured in the job, so the analysis needs no fixed population.

`MAX_QUBITS` is the largest count whose results stay inside the service's result buffer (error 8045). The measure arm
at N = 16 writes 16 bits per qubit per shot (17 with the herald below), so 50 qubits and 8192 shots write about
7 Mbit per dynamic PUB. No IBM page states the buffer limit; the dry run cannot test it. Falsifier: an 8045 failure on
the first attempt, which the fallback answers by halving the qubit count at the same delay.

## Repetition delay

Attempt 1 runs at 20 us, attempt 2 at 50 us. The fallback fires on a job error 1602 or 8030 (delay refused), 1305
(the job ran past its ceiling; at 20 us the 2026-10-18 n21 controls ended this way, `REP_DELAY_ZERO_CONTROL_FINDINGS.md`),
8038 (timing error) or 8045 (result buffer; it also halves the qubit count). A 20 us attempt that completes is the run.

Each attempt's ceiling is its planner charge times 1.5, rounded up: about 37 s at 20 us and 55 s at 50 us for the
current member list. The total ceiling is their sum, the worst case where the first attempt bills its full ceiling and
fails. Falsifier: a billed attempt above its ceiling.

## State preparation at a short delay

`init_qubits` stays true. At 50 us the Kingston control measured the excitation left after a shot ending in `|1>` at
an upper bound of 0.0144 on its worst qubit, against 0.0157 at 250 us
(`results/live/N21_STATE_PREP_CONTROL_CASE.md`). At 20 us nothing is measured on this account.

The pinching analysis corrects the initial state through q, one value per qubit fitted from ro0 and the T1 series.
Execution iterates column-wise over the circuits of a job, so each circuit's predecessor on a qubit is a different
circuit, and an excitation that depends on the predecessor's final state differs between arms, which a single q cannot
absorb. The measure arm's N = 16 P0 departs the ideal by the excitation times the arm's contrast, so a 0.01
predecessor-dependent excitation can move the departure by up to about 0.01, half the 0.0188 floor.

Every member therefore begins with a herald: a measurement of each qubit before the first pulse, in its own classical
register. The analysis keeps the shots whose herald reads 0 on that qubit and reports the herald's excited fraction
per member. The herald measures the initial excitation of every circuit under its actual predecessor, so the
preregistered departure test runs on postselected counts and the predecessor dependence leaves the estimate. The cost
is one measurement per member (about 1.6 us) and a shot fraction near the excitation. Every member then contains a
mid-circuit measurement, so the whole family runs as one dynamic job, which saves one 2.3 s job overhead.

The herald changes the circuits and the analysis, so the analysis rule is preregistered again here: the ro0 and ro1
readout correction, the T1 series fit, the mutation test and the departure test run unchanged on the postselected
counts, with q fitted from the postselected ro0 and T1 series.

Falsifiers: a herald excited fraction above 0.05 on a qubit makes that qubit uninformative (the postselection then
discards enough shots to move the per-qubit precision); a herald excited fraction that differs between arms of one
qubit beyond 3 standard errors is reported as a measured history effect.

## Floor

The bound floor (0.0188, `docs/evidence/measurement_sequence/scatter-floor.json`) was measured at 250 us on 38 Kingston
qubits in one calibration window. Every qubit of the main family already runs the unitary N = 16 member, the circuit
the diagnostic measured. The departure floor of a run becomes the root-mean-square over its informative qubits of the
readout-corrected unitary N = 16 residual of that run, the diagnostic's rule applied in the job. The bound floor stays
as a lower limit on Kingston: the floor is the larger of the two. On ibm_fez the in-job floor stands alone.

With about 50 qubits the in-job floor has a relative sampling error near 1/sqrt(100) = 0.10. Falsifier: fewer than 20
informative qubits withholds the floor and the analysis, as the diagnostic rule does.

## Scaling to about 50 qubits

- Compiled-ideal proof. The proof enumerates 2^17 branches for each N = 16 measure or settle member, about 3.3 s a
  replica; 879d679 pools it. At 50 qubits the replica count rises about sixfold. Members on different physical qubits
  that compile to the same instruction stream up to qubit relabeling share one proof; the dry run reports the proof
  time, and a proof time above 300 s fails the design review.
- Admission. The self-test admits 8192 shots for 1 to 14 qubits; the family-wise alpha splits over 17 endpoints per
  qubit, so 50 qubits divide it 50 ways. The dry run decides whether 8192 admits; the departure standard error is
  floor-dominated (0.0188 against 0.0024 statistical), so a larger shot tier buys nothing, and a refused admission
  lowers the qubit count instead of raising the shots.
- Device rule. "Two informative qubits agree or the pooled z reaches 3" was sized for 8 qubits. The diagnostic's
  residual has a positive mean (+0.011 on 32 of 38 qubits), so a shared model offset can align many qubits. The device
  verdict at about 50 qubits fires on the pooled z at 3 with the floor added in quadrature, and the count rule requires
  max(2, 10 percent of the informative qubits).

## Shots

8192 per member. The departure test's standard error is set by the floor, so the savings of the short delay go to
qubits, not shots.

## Charge

| Delay | Shot loop | Jobs | Charge |
|---|---|---|---|
| 250 us (the approved main design) | 113.9 s | 2 | 118.5 s |
| 50 us | 32.0 s | 1 | 34.3 s |
| 20 us | 19.7 s | 1 | 22.0 s |

The herald adds about 1.6 us a member, under 0.1 s at 8192 shots. The backup instance reports 412 s remaining; another
session's run (`results/live/2026-10-26T045124.175747Z` on the primorial-coherence branch, job dbfdotnpc3tc739n8nm0,
23 s) shares that instance, and the branch that merges second regenerates the instance's job inventory.

## Sequence

1. Reviews of this design (adversarial self-review, Codex, advisor) and their resolution.
2. Implementation: the envelope record and its submit path in live_run and qpu_planning, the layout rule, the delay
   schedule and fallback, the herald members, the postselected analysis and the in-job floor, the doctrine edits, and
   gates for the rule's re-application and the analysis.
3. An envelope dry run on the latest calibration and the written case.
4. The owner's approval of the envelope, then the submission on whatever calibration is live, the collection and the
   preregistered analysis.
