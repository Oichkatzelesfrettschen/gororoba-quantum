# N=21 feedback-encoded run: QPU usage budget

The n21-feedback-encoded family runs two dynamic circuits on seven qubits:
two-round order finding for N=21, a=4, under the GL(5,2) work-register
encoding of coset 15265, with (`n21_encoded_feedback`) and without
(`n21_encoded_no_feedback`) the semiclassical phase correction that an
`if_else` applies from the first round's mid-circuit measurement. Their
ideal labeled laws are (3, 2, 1, 2)/8 and (3, 1, 1, 3)/8. The run asks one
question: does the feed-forward arm's two-bit distribution differ from the
control arm's as predicted? `diagnostic_experiments.family_contracts` turns
it into one directional endpoint, the signed-contrast difference
(p01 - p11)_ff - (p01 - p11)_noff, ideal 1/4, tested one-sided at alpha 0.05
with power 0.8 against the modeled effect that survives the simulation
allowance.

This note decomposes the run's QPU seconds from IBM's usage model and the
repository's retained jobs, ranks every lever by the seconds it saves, and
names the cheapest configuration the admitted planning contract accepts.
Every number in the generated block below comes from
`scripts/n21_usage_budget.py`, which gate core-484 replays. The billing fit
reads the 23 jobs `BILLING_JOBS` pins by run, job id and raw index sha256,
with every file it reads checked against that index, so a job retained later
leaves the block unchanged until the list and the block change together.

## Usage model

IBM bills QPU lock time (docs/notes/ibm_quantum/estimate-job-run-time.md):
about 2 s per sub-job plus (rep_delay + circuit length) x executions, where
executions are shots summed over the job's PUBs and circuits run column-wise
over shots (repetition-rate-execution.md). The pinned jobs fix both terms
exactly: the metered `circuits_execution_time_ns` equals the sum over PUBs of
shots x (rep_delay + scheduler circuit duration), and the integer
`qpu_charge_time_seconds` equals the ceiling of that time plus a constant
near 1.7 s. The scheduler duration exceeds the Target gate-time bound that
live_run plans with by a constant 2246 dt (9.0 us) on ibm_kingston plus
about 133 dt per feed-forward stage, so live_run's declared 20 us per stage
and 2.3 s per job land within 1.5 us per pair of shots and within one second
per job of the metered charge.

For this pair the circuit length is 69 us per arm; the 250 us default
repetition delay is 78 percent of every execution. Seconds are therefore
linear in shots per arm, n: planner charge = 2.3 s + n x 657.5 us at the
default delay.

## Statistical cost

`experiment_optimizer.evaluate_candidate` admits a plan when the modeled
contrast minus the simulation allowance covers the detection radius at
alpha plus the power radius at 1 - power, each summed over the two PUBs
(union bound, no independence between PUBs assumed). Shots therefore scale
as (K / c)^2 for modeled contrast c.

- **QPU radius.** Hoeffding per PUB: span x sqrt(ln(1/t) / (2n)), span 2 for
  the signed score (0, 1, 0, -1), t = alpha/2 for detection and 0.1 for power.
  Detection plus power is K / sqrt(n) with K = 9.724. Replicas averaged
  inside one shot keep the span at 2, so without a covariance bound they buy
  nothing.
- **Declared covariance.** A PSD bound V on per-replica score variance with
  independent replicas gives the Cantelli radius sqrt(V / (R n) x (1 - t) / t),
  taken when smaller than Hoeffding's. The score variance is
  P(s != 0) - E[s]^2, at most P(bit 0 = 1), 0.49 to 0.51 in the Kingston
  model; the declared V is 0.55, and the planner refuses a V below any
  replica's modeled variance. At R = 2 the power radius switches to Cantelli
  and K falls to 8.578; detection stays Hoeffding until R reaches 3.
- **Simulation allowance.** A sampled model of m shots adds
  2 x 2 x sqrt(ln(2C / 0.01) / (2m)) for the two members, where C counts
  every scored marginal across the whole candidate search. The dry run of
  2026-10-17T003834Z scored C = 48 marginals (six routed sets, three of them
  duplicates from replica caps the 0.9 floor collapsed, times four shot
  tiers) at m = 65,536: allowance 0.0335 against a predicted contrast of
  0.0343. That allowance, not the QPU radius, made the run infeasible.
  `family_candidates` now enters one copy of caps that place the same
  replicas.

## Exact model

`dynamic_density.py` evolves the classical-quantum state of each dynamic
circuit exactly under live_run's Aer noise channels: one density matrix per
recorded classical value, measurement projecting on the true outcome and
recording through the readout matrix, reset followed by its local error, and
the `if_else` selecting branches by the recorded bit with noise on its body
gates. With `--model-method exact` the planner passes `simulation_shots=None`
and the allowance is zero. Evidence that the exact law is Aer's law:

- gate core-480: a three-qubit fixture with exaggerated errors matches
  400,000 Aer density-matrix shots within 0.001 (radius 0.0047), and each
  alternative ordering (no body noise, reset error before the reset,
  condition on the true outcome) lies outside 3 radii;
- every exact dry run compares each replica's exact law with its own
  65,536-shot sampled marginal and stops on a gap beyond the simultaneous
  radius (`n21_exact_planning.exact_predictions`); the reference run's
  largest gap is 0.0047 against a radius of 0.0078;
- gate core-485: the retained Kingston ISA under the 2026-10-16 12:13
  snapshot, sampled on three Kaggle CPU kernels (589,824 shots per arm),
  agrees with the exact law within 0.0016 against a pooled radius of 0.0029
  (docs/evidence/n21_exact_model/).

The exact law costs about 3 s of CPU per circuit against about 50 s for
65,536 sampled shots on 12 threads.

## Calibration drift

The exact contrast of the same family on ibm_kingston fell from 0.0308
(12:13 snapshot) through 0.0297 (01:53) to 0.0248 (02:30) within fourteen
hours, and the 02:30 calibration moved the best placement from qubits
104-105-117-124-125-126-127 to 104-105-106-107-117-125-126. Seconds scale as
c^-2, so the same one-replica design needs 67.7, 72.9 and 103.7 s at those
three calibrations (generated table). A case sized at one calibration is
re-planned at submission: the runner compares the fresh plan with the
approved record and stops for renewed approval when it differs.

## Levers, ranked by seconds saved

Seconds below are planner charges at the reference contrast 0.0248 (dry run
2026-10-17T101105Z); the generated table carries every row.

1. **Simulation allowance: exact model.** The sampled search is infeasible at
   any shot count at 65,536 model shots; the 589,824 sampled shots the
   Kaggle validation ran would leave a 0.0090 allowance and 253.0 s. The
   exact model needs 154,202 shots per arm (103.7 s) with one replica. Cost
   to the inference: none beyond the noise model the sampled path already
   assumed; control: the sampled falsifiers above.
2. **Contract choice (a change to the preregistered test).** Hoeffding over a
   span-2 score costs 15 times the shots of a normal-approximation test at
   the same contrast (9,979 shots, 8.9 s). Bernstein with the declared
   variance bound keeps a finite-sample guarantee and needs 86,097 shots
   (58.9 s); Hoeffding over independent replicas at R = 2 needs 74,736
   (51.4 s). experiment_optimizer implements none of the three; each needs
   the owner's sign-off.
3. **Repetition delay.** 250 to 100 us saves 46 s (57.4 s), to 50 us saves
   62 s (42.0 s), on the Heron r2 range 0 to 2 ms. Cost: state-preparation
   error rises as the delay falls and Aer does not model it, so the power at
   a shorter delay is unverified. Control: a prepare-and-measure null PUB on
   the seven qubits in the same job measures the excited-state population at
   that delay and the power is recomputed with it; rep_delay is one value per
   job, so a 250 us reference costs a second job.
4. **Replicas.** Disjoint one-hop-buffered placements of the encoded pattern
   on ibm_kingston scored 1, 0.598, 0.562, 0.332 and 0.325 of the best at the
   01:53 calibration; floor 0.55 admits the three above the gap between
   0.562 and 0.332. Layout score is a poor contrast proxy: at 02:30 the
   second placement (qubits 57, 65-70, score 0.67 of the best) models a
   contrast of 0.0255 against 0.0248 for the first. Two replicas with the
   declared bound need 116,331 shots (78.8 s) against 154,202 (103.7 s) for
   one: 25 s saved. The optimizer chose R = 2 at the 118,784 tier (80.4 s).
   Four equal replicas would need 52.7 s; the chip offers no such set.
   Control: collection tests the declared bound on the retained shot-ordered
   replica registers before it applies it
   (`n21_exact_planning.COVARIANCE_FALSIFIER`, recorded in record.json and
   the case): the sample variance of each PUB's replica-average score must
   stay within the declared projection 0.275 plus a Hoeffding allowance
   (0.0308 at 118,784 shots). A failure analyzes the endpoint under the
   arbitrary-dependence Hoeffding radius, which at the same shots leaves it
   underpowered; collect.json records the branch, and
   `scripts/n21_replica_covariance.py --run-dir` replays it from the raw
   files.
5. **CZ count.** Removing k routed CZ multiplies the contrast by rho^-k,
   rho between 0.99687 and 0.99745, so shots scale by rho^(2k): 100 fewer CZ
   save 40 to 47 s, 200 fewer save 65 to 72 s (one replica). With a sampled
   model of allowance a the required shots are (K / (c rho^-k - a))^2.
6. **Backend.** Under the 2026-10-16 midday snapshots the encoded pair's
   modeled contrast is 0.0417 on Kingston, 0.0198 on Fez and 0.0135 on
   Marrakesh (docs/evidence/linear_conjugation/README.md, sampling error
   0.0055); shots scale as contrast^-2, so Fez needs 4.4 and Marrakesh 9.5
   times Kingston's seconds.
7. **Job shape.** One dynamic job, two PUBs, uniform shots (qiskit-ibm-runtime
   0.48 deprecates differing `pub.shots` within a job), one sub-job: each
   added job or sub-job costs another 1.7 to 2.3 s. `measure_2` and
   `reset_2` shorten the mid-circuit readout and reset by 0.8 us each on
   Kingston, 3.2 us per pair (0.5 percent, 0.4 s at 120,000 shots), at a
   higher assignment error (median 0.0107 against 0.0096) that Aer cannot
   represent; the saving does not pay for its control.

## Minimum

At the 02:30 Kingston calibration the admitted contract's cheapest
configuration is the exact model, two replicas (qubits 104-105-106-107-117-
125-126 and 57-65-66-67-68-69-70) under the declared variance bound 0.55,
250 us repetition delay, one job of two PUBs: 116,331 shots per arm at the
minimum, 118,784 at the dry run's tier, 80.4 s planner charge against a 95 s
job ceiling. Without the replica-independence assumption the same contract
needs one replica and 103.7 s. The written case is
`results/live/2026-10-17T101105.548987Z/UNAPPROVED_CASE.md`.

<!-- n21-usage-budget:begin -->

Generated by `scripts/n21_usage_budget.py --write`; reference record `results/live/2026-10-17T101105.548987Z/record.json` (ibm_kingston, calibration 2026-10-17T02:30:44-07:00).

**Metered billing (retained jobs).**

- Jobs: 23, one sub-job each; executions 1,024 to 122,880.
- `circuits_execution_time_ns` equals sum(shots x (rep_delay + scheduler circuit duration)) within 0.25 us per execution on every job.
- `qpu_charge_time_seconds` is an integer, equal to ceil(execution + c) on every job for c in (1.672, 1.725] s.
- ibm_kingston scheduler duration minus the Target gate-time bound: 0 feed-forward stage(s): 2245 to 2247 dt (median 2246.0); 1 feed-forward stage(s): 2379 to 3557 dt (median 2379.0).
- rep_delay_range: ibm_fez 0 to 2000 us, default 250 us; ibm_kingston 0 to 2000 us, default 250 us; ibm_marrakesh 0 to 2000 us, default 250 us.

**Per-shot cost of the pair (one shot of each arm).**

| PUB | Target gate time (us) | feed-forward stages |
| --- | --- | --- |
| ibm_kingston_dynamic_pub_01 | 68.632 | 1 |
| ibm_kingston_dynamic_pub_02 | 68.916 | 0 |

| rep_delay (us) | planner seconds per pair (us) | measured-model seconds per pair (us) |
| --- | --- | --- |
| 250 | 657.5 | 656.0 |
| 100 | 357.5 | 356.0 |
| 50 | 257.5 | 256.0 |
| 0 | 157.5 | 156.0 |

**Calibration drift of the exact contrast (one replica, Hoeffding, 250 us).**

| Source | calibration | layout qubits | exact contrast | shots per arm | planner charge (s) |
| --- | --- | --- | --- | --- | --- |
| calibration snapshot, retained ISA | 2026-10-16T12:13:36-07:00 | [104, 105, 117, 124, 125, 126, 127] | 0.0308 | 99,511 | 67.7 |
| dry run 2026-10-17T091514.662497Z | 2026-10-17T01:53:33-07:00 | [104, 105, 117, 124, 125, 126, 127] | 0.0297 | 107,348 | 72.9 |
| dry run 2026-10-17T094344.639211Z | 2026-10-17T02:30:44-07:00 | [104, 105, 106, 107, 117, 125, 126] | 0.0248 | 154,202 | 103.7 |
| dry run 2026-10-17T101105.548987Z | 2026-10-17T02:30:44-07:00 | [104, 105, 106, 107, 117, 125, 126] | 0.0248 | 154,202 | 103.7 |

**Shots and seconds.** Reference modeled contrast difference 0.0248 (ideal 0.25); alpha 0.05, power 0.8, one-sided, union bound over the two PUBs, as `family_contracts` declares.

| Configuration | executions | planner charge (s) | measured-model charge (s) | smallest job ceiling (s) | power | assumptions | simulation allowance | QPU radius |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| as dry-run: sampled 65,536, 24 plans, Hoeffding, R=1 | infeasible | - | - | - | - | sampled model, 65,536 shots | 0.0335 | - |
| sampled 65,536, one plan, Hoeffding, R=1 | infeasible | - | - | - | - | sampled model, 65,536 shots | 0.0270 | - |
| sampled 589,824 (the Kaggle validation's size), one plan, Hoeffding, R=1 | 2 x 381,251 | 253.0 | 252 | 253 | 0.8, admitted contract | sampled model, 589,824 shots | 0.0090 | 0.0157 |
| exact model, Hoeffding, R=1 | 2 x 154,202 | 103.7 | 103 | 104 | 0.8, admitted contract | exact model | 0.0000 | 0.0248 |
| exact, Cantelli V=0.55, R=2 (replica contrasts 0.0248, 0.0255) | 2 x 116,331 | 78.8 | 79 | 79 | 0.8, admitted contract | exact model; independent replicas, variance <= 0.55 | 0.0000 | 0.0252 |
| exact, Cantelli V=0.55, R=4 equal replicas (hypothetical) | 2 x 76,656 | 52.7 | 53 | 53 | 0.8, admitted contract | exact model; independent replicas, variance <= 0.55; hypothetical equal replicas | 0.0000 | 0.0248 |
| exact, Hoeffding, R=1, rep_delay 100 us | 2 x 154,202 | 57.4 | 57 | 58 | unverified | exact model; state-prep error unmodeled | 0.0000 | 0.0248 |
| exact, Hoeffding, R=1, rep_delay 50 us | 2 x 154,202 | 42.0 | 42 | 43 | unverified | exact model; state-prep error unmodeled | 0.0000 | 0.0248 |
| extension: Bernstein with V=0.55, R=1 | 2 x 86,097 | 58.9 | 59 | 59 | 0.8, contract change | exact model; variance <= 0.55 | 0.0000 | - |
| extension: Hoeffding over independent replicas, R=2 (replica contrasts 0.0248, 0.0255) | 2 x 74,736 | 51.4 | 51 | 52 | 0.8, contract change | exact model; independent replicas | 0.0000 | - |
| normal approximation, one-sided alpha 0.05, pooled variance | 2 x 9,979 | 8.9 | 9 | 9 | 0.8 asymptotic, contract change | exact model; normal limit | 0.0000 | - |

Executions count shots summed over the two PUBs; replicas share a shot. The dry run selected `candidate-001-shots-118784` (2 replicas, 118,784 shots per arm, 80.4 s) under a 95 s job ceiling.

**CZ reduction (exact model, Hoeffding, R=1).** Removing k routed CZ scales the contrast by rho^-k; the two columns take rho from 1 - 4/3 x the Kingston median CZ error and from the reference contrast's own decay over its CZ count. Cells: shots per arm / planner seconds at 250 us.

| k removed | rho = 0.99745 | rho = 0.99687 |
| --- | --- | --- |
| 0 | 154,202 / 103.7 | 154,202 / 103.7 |
| 25 | 135,727 / 91.5 | 131,816 / 89.0 |
| 50 | 119,464 / 80.9 | 112,680 / 76.4 |
| 100 | 92,552 / 63.2 | 82,339 / 56.4 |
| 200 | 55,549 / 38.8 | 43,966 / 31.2 |

<!-- n21-usage-budget:end -->
