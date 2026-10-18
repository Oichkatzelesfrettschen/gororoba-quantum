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
near 1.7 s; metered minus modeled is a per-job constant of one 250 us
rep_delay plus 9 to 22 us, whatever the executions. The scheduler duration exceeds the Target gate-time bound that
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
  and K falls to 8.578; detection stays Hoeffding until R reaches 3. The
  R = 2 rejection threshold therefore needs no replica assumption, while
  its power, and the shots that buy it, rest on the projection
  w' V w = 0.55 / 2, which needs both the variance bound and zero
  off-diagonals (independence). Per PUB at R = 2, n x radius^2 is
  (V / R)(1 - t) / t for Cantelli, 10.7 at the detection tail and 2.5 at
  the power tail, against 2 ln(1/t) for Hoeffding, 7.4 and 4.6.
- **Variance upper confidence limit.** Failing to reject a declared
  variance does not establish it, so the radius never reads the bare
  declaration. Collection measures each bound's sample variance and adds
  the allowance eps2 + D eps1 at tail 1e-3 / 2 per PUB (D = 2, about
  0.030 at 122,880 shots): the radius reads the declared projection 0.275
  only when that upper confidence limit (UCL) stays at or below it, and the
  UCL otherwise, through Cantelli only where that beats Hoeffding. The
  falsifier tail comes out of the endpoint's alpha, 0.05 = 0.001 + 0.049,
  so the confidence and detection radii run at 0.049; the power tail stays
  0.2. Planning sizes the run on the same rule: each bound's projection is
  0.275 plus the allowance at the planned shots, the variance collection
  reads when the sample variance meets the declaration, at alpha 0.049. At
  the reference calibration that rule needs 120,625 shots per arm at R = 2
  against 115,591 for the bare declaration (78.3 s, the earlier rule's
  row), 3.3 s more; the R = 1 Hoeffding design reads no bound and keeps
  alpha 0.05.
- **Empirical-Bernstein detection (`--empirical-bernstein`).** The score
  (0, 1, 0, -1) has variance P(s != 0) - E[s]^2, near 0.5 against the
  span-2 maximum of 1, so Hoeffding pays for a range the score barely
  uses. With the opt-in each PUB's confidence and detection radius is the
  smaller of the Hoeffding radius and the Maurer-Pontil radius
  sqrt(2 V_n ln(2/t) / n) + 14 ln(2/t) / (3 (n - 1)), V_n the sample
  variance, each at half of alpha: 0.05 = 0.025 + 0.025, t = 0.0125 per
  PUB for detection (QPU_OPTIMIZATION.md, "Statistical admission"). The
  union bound over the two methods keeps coverage at 0.05 whatever the
  variance. Planning reads the exact law's per-PUB variance raised by
  Maurer-Pontil Theorem 10 (4) at total tail 0.001, 2 sqrt(2 ln(2000) /
  (n - 1)) = 0.0260 on the standard deviation at 90,112 shots (variance
  0.508 modeled, 0.546 planned), and spends that 0.001 from the miss
  probability: power radius at tail 0.199. A sample variance above that limit widens the collected radius
  and costs power, never coverage. At 90,112 shots per arm the detection
  radius falls from 0.01810 (Hoeffding at 0.05) to 0.01620; the power
  radius rises from 0.01430 to 0.01431. Detection plus power times sqrt(n)
  is 9.16 against Hoeffding's 9.72 at that n (the 1/n term makes it grow
  slowly as n falls), so shots fall by about 11 percent.
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
  65,536-shot sampled marginal (`n21_exact_planning.validate_exact`): every
  probability within the simultaneous radius, and each arm's signed score
  and the endpoint contrast within their own Bernstein radii; a candidate
  that fails leaves the search with its reason in the trace. The reference
  run's largest probability gap is 0.0044 against 0.0078, and its contrast
  reads 0.0252 exact against 0.0240 sampled, inside a contrast radius of
  0.0208. At 65,536 model shots that radius is about the effect itself, so
  the in-run check cannot see a bias of 10 percent of the contrast;
- gate core-485: the retained Kingston ISA under the 2026-10-16 12:13
  snapshot, sampled on three Kaggle CPU kernels (589,824 shots per arm),
  agrees with the exact law within 0.0016 per probability against a pooled
  radius of 0.0029, and the same arm and contrast checks pass, but the
  sampled contrast 0.0282 sits 2.04 standard deviations below the exact
  0.0308, both arms shrinking toward zero (docs/evidence/n21_exact_model/).

**Bias sensitivity.** If the device-calibration model's true contrast were
the Kaggle pool's fraction 0.914 of the exact one, the reference plan's
effect would fall from 0.0252 to 0.0231 while its detection plus power
radius at 122,880 shots is 0.0250: power 0.8 would then need about 144,353
shots per arm, 97.3 s, above the 95 s job ceiling. The Kaggle pool used the
12:13 snapshot, not the reference calibration, and cannot separate that bias
from sampling noise; a pool about four times larger would.

The exact law costs about 3 s of CPU per circuit against about 50 s for
65,536 sampled shots on 12 threads.

## Calibration drift

The exact contrast of the same family on ibm_kingston fell from 0.0308
(12:13 snapshot) through 0.0297 (01:53) and 0.0248 (02:30) to 0.0229 (03:41,
unchanged at 04:20) and rose to 0.0249 at 05:40, within eighteen hours; the
02:30 calibration moved the best placement from qubits
104-105-117-124-125-126-127 to 104-105-106-107-117-125-126. Seconds scale as
c^-2, so the same one-replica design needs 67.8, 72.9, 103.7, 120.8 and
102.4 s at those five calibrations (generated table). A case sized at one calibration is
re-planned at submission: the runner compares the fresh plan with the
approved record and stops for renewed approval when it differs.

## Levers, ranked by seconds saved

Seconds below are planner charges at the reference contrast 0.0249 (dry run
2026-10-17T130242Z, Kingston calibration 05:40); the generated table carries
every row.

1. **Simulation allowance: exact model.** The sampled search is infeasible at
   any shot count at 65,536 model shots; the 589,824 sampled shots the
   Kaggle validation ran would leave a 0.0090 allowance and 248.0 s. The
   exact model needs 152,183 shots per arm (102.4 s) with one replica. Cost
   to the inference: none beyond the noise model the sampled path already
   assumed and the bias sensitivity above; control: the sampled falsifiers
   above.
2. **Contract choice (a change to the preregistered test).** Hoeffding over a
   span-2 score costs 15 times the shots of a normal-approximation test at
   the same contrast (9,858 shots, 8.8 s). Bernstein with the declared
   variance bound keeps a finite-sample guarantee and needs 84,978 shots
   (58.2 s); Hoeffding over independent replicas at R = 2 needs 74,260
   (51.1 s) against the admitted 120,625 (81.6 s) at the same R. Both rows
   use independence: the extension treats the n x R replica scores as
   independent draws, so its sub-Gaussian radius shrinks as 1 / sqrt(R) on
   detection and power alike, while the admitted contract reaches
   independence only through Cantelli's heavier-tailed radius, which helps
   the power tail alone at R = 2. experiment_optimizer implements none of
   the three extensions; each needs the owner's sign-off. The
   empirical-Bernstein opt-in keeps the admitted contract's finite-sample
   coverage and needs no variance or independence assumption: at the
   13:50 Kingston calibration it plans 89,088 shots per arm at the minimum
   against 100,352 under Hoeffding (90,112 against 106,496 on the dry
   run's tiers).
3. **Repetition delay.** 250 to 100 us saves 46 s (56.8 s), to 50 us saves
   61 s (41.5 s), on the Heron r2 range 0 to 2 ms. Cost: state-preparation
   error rises as the delay falls and Aer does not model it, so the power at
   a shorter delay is unverified. Control: a prepare-and-measure null PUB on
   the seven qubits in the same job measures the excited-state population at
   that delay and the power is recomputed with it; rep_delay is one value per
   job, so a 250 us reference costs a second job.
4. **Replicas.** Disjoint one-hop-buffered placements of the encoded pattern
   on ibm_kingston scored 1, 0.598, 0.562, 0.332 and 0.325 of the best at the
   01:53 calibration; floor 0.55 admits the three above the gap between
   0.562 and 0.332. Layout score is a poor contrast proxy: at 05:40 the
   second placement (qubits 57, 65-70) models a contrast of 0.0255 against
   0.0249 for the first. Two replicas with the bound read through its UCL
   need 120,625 shots (81.6 s) against 152,183 (102.4 s) for one: 21 s
   saved, all of it through the power radius. The optimizer chose R = 2 at
   the 122,880 tier (83.1 s). Four equal replicas would need 65.3 s; the
   chip offers no such set.
   Control: collection reads each bound only through its variance UCL
   (`n21_exact_planning.COVARIANCE_FALSIFIER`, recorded in record.json and
   the case) and records the UCL, the variance used, the branch and the
   alpha split in collect.json; `scripts/n21_replica_covariance.py
   --run-dir` replays it from the raw files. A UCL above the planned
   projection widens the power radius and can leave the endpoint
   underpowered, which collect.json reports; without retained registers
   the endpoint takes the Hoeffding radius at the full alpha.
5. **CZ count.** Removing k routed CZ multiplies the contrast by rho^-k,
   rho between 0.99687 and 0.99745, so shots scale by rho^(2k): 100 fewer CZ
   save 40 to 47 s, 200 fewer save 64 to 72 s (one replica). With a sampled
   model of allowance a the required shots are (K / (c rho^-k - a))^2.
6. **Backend.** Under the 2026-10-16 midday snapshots the encoded pair's
   modeled contrast is 0.0417 on Kingston, 0.0198 on Fez and 0.0135 on
   Marrakesh (docs/evidence/linear_conjugation/README.md, sampling error
   0.0055); shots scale as contrast^-2, so Fez needs 4.4 and Marrakesh 9.5
   times Kingston's seconds.
7. **Job shape.** One dynamic job, two PUBs, uniform shots (qiskit-ibm-runtime
   0.48 deprecates differing `pub.shots` within a job), one executor chunk on
   every pinned job: each added job or sub-job costs another 1.7 to 2.3 s. `measure_2` and
   `reset_2` shorten the mid-circuit readout and reset by 0.8 us each on
   Kingston, 3.2 us per pair (0.5 percent, 0.4 s at 120,000 shots), at a
   higher assignment error (median 0.0107 against 0.0096) that Aer cannot
   represent; the saving does not pay for its control.

## Minimum

At the 05:40 Kingston calibration the admitted contract's cheapest
configuration is the exact model, two replicas (qubits 104-105-106-107-117-
125-126 and 57-65-66-67-68-69-70) under the declared variance bound 0.55
read through its UCL, 250 us repetition delay, one job of two PUBs: 120,625
shots per arm at the minimum, 122,880 at the dry run's tier, 83.1 s planner
charge against a 95 s job ceiling. The detection radius is Hoeffding's at
alpha 0.049; the power rests on the bound and replica independence. One
replica needs 102.4 s, above the ceiling. Under the same rule at the 04:20
calibration R = 2 would need 130,627 shots (88.2 s; the 131,072 tier,
88.5 s, still admits) and R = 1 180,205 (120.8 s). The written case is
`results/live/2026-10-17T130242.718497Z/UNAPPROVED_CASE.md`; the dry runs
2026-10-17T101105Z, 2026-10-17T111902Z and 2026-10-17T114216Z, planned
under the declared-variance rule, are superseded audit records.

**Under the empirical-Bernstein opt-in.** Two submit-free dry runs of the
same command with `--empirical-bernstein` and `--prep-excitation 0.01`
(`results/live/2026-10-17T214153.170495Z` at 50 us,
`results/live/2026-10-17T214839.779704Z` at 250 us) plan one replica on
qubits 104-106, 117, 124-126 of ibm_kingston, exact contrast 0.03073 with
eps = 0.01, at 90,112 shots per arm: 25.48 s at 50 us (ceiling 30 s) and
61.53 s at 250 us (ceiling 71 s). PR #229's records of the same command
under Hoeffding plan 98,304 shots, 27.73 s and 67.05 s, at the 13:18
calibration; re-planned from those records under the opt-in they need
90,112 shots, 25.61 s and 61.65 s. At the new runs' own calibration
Hoeffding needs the 106,496 tier, 29.70 s and 72.29 s, so the opt-in saves
4.2 s at 50 us and 10.8 s at 250 us at a fixed calibration. Both cases
stay unapproved sizing cases: the excitation is still the placeholder the
state-prep-control pair replaces.

<!-- n21-usage-budget:begin -->

Generated by `scripts/n21_usage_budget.py --write`; reference record `results/live/2026-10-17T130242.718497Z/record.json` (ibm_kingston, calibration 2026-10-17T05:40:42-07:00).

**Metered billing (retained jobs).**

- Jobs: 23; the result metadata's executor `chunk_timing` lists 1 chunk(s) per job; executions 1,024 to 122,880.
- `circuits_execution_time_ns` minus sum(shots x (rep_delay + scheduler circuit duration)) is a per-job constant, -272.1 to -258.6 us across those executions: one 250 us rep_delay plus 8.6 to 22.1 us.
- `qpu_charge_time_seconds` is an integer, equal to ceil(execution + c) on every job for c in (1.672, 1.725] s.
- ibm_kingston scheduler duration minus the Target gate-time bound: 0 feed-forward stage(s): 2245 to 2247 dt (median 2246.0); 1 feed-forward stage(s): 2379 to 3557 dt (median 2379.0).
- rep_delay_range: ibm_fez 0 to 2000 us, default 250 us; ibm_kingston 0 to 2000 us, default 250 us; ibm_marrakesh 0 to 2000 us, default 250 us.

**Per-shot cost of the pair (one shot of each arm).**

| PUB | Target gate time (us) | feed-forward stages |
| --- | --- | --- |
| ibm_kingston_dynamic_pub_01 | 68.916 | 1 |
| ibm_kingston_dynamic_pub_02 | 68.884 | 0 |

| rep_delay (us) | planner seconds per pair (us) | measured-model seconds per pair (us) |
| --- | --- | --- |
| 250 | 657.8 | 656.3 |
| 100 | 357.8 | 356.3 |
| 50 | 257.8 | 256.3 |
| 0 | 157.8 | 156.3 |

**Calibration drift of the exact contrast (one replica, Hoeffding, 250 us).**

| Source | calibration | layout qubits | exact contrast | shots per arm | planner charge (s) |
| --- | --- | --- | --- | --- | --- |
| calibration snapshot, retained ISA | 2026-10-16T12:13:36-07:00 | [104, 105, 117, 124, 125, 126, 127] | 0.0308 | 99,511 | 67.8 |
| dry run 2026-10-17T091514.662497Z | 2026-10-17T01:53:33-07:00 | [104, 105, 117, 124, 125, 126, 127] | 0.0297 | 107,348 | 72.9 |
| dry run 2026-10-17T094344.639211Z | 2026-10-17T02:30:44-07:00 | [104, 105, 106, 107, 117, 125, 126] | 0.0248 | 154,202 | 103.7 |
| dry run 2026-10-17T101105.548987Z | 2026-10-17T02:30:44-07:00 | [104, 105, 106, 107, 117, 125, 126] | 0.0248 | 154,202 | 103.7 |
| dry run 2026-10-17T111902.183133Z | 2026-10-17T03:41:37-07:00 | [104, 105, 106, 107, 117, 125, 126] | 0.0229 | 180,205 | 120.8 |
| dry run 2026-10-17T114216.070396Z | 2026-10-17T04:20:24-07:00 | [104, 105, 106, 107, 117, 125, 126] | 0.0229 | 180,205 | 120.8 |
| dry run 2026-10-17T130242.718497Z | 2026-10-17T05:40:42-07:00 | [104, 105, 106, 107, 117, 125, 126] | 0.0249 | 152,183 | 102.4 |

**Shots and seconds.** Reference modeled contrast difference 0.0249 (ideal 0.25); alpha 0.05, power 0.8, one-sided, union bound over the two PUBs, as `family_contracts` declares.

| Configuration | executions | planner charge (s) | measured-model charge (s) | smallest job ceiling (s) | power | assumptions | simulation allowance | QPU radius |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sampled 65,536 across the dry run's 24 plans, Hoeffding, R=1 | infeasible | - | - | - | - | sampled model, 65,536 shots | 0.0335 | - |
| sampled 65,536, one plan, Hoeffding, R=1 | infeasible | - | - | - | - | sampled model, 65,536 shots | 0.0270 | - |
| sampled 589,824 (the Kaggle validation's size), one plan, Hoeffding, R=1 | 2 x 373,449 | 248.0 | 247 | 248 | 0.8, admitted contract | sampled model, 589,824 shots | 0.0090 | 0.0159 |
| exact model, Hoeffding, R=1 | 2 x 152,183 | 102.4 | 102 | 103 | 0.8, admitted contract | exact model | 0.0000 | 0.0249 |
| exact, Cantelli V=0.55 through its UCL, R=2 (replica contrasts 0.0249, 0.0255) | 2 x 120,625 | 81.6 | 81 | 82 | 0.8, admitted contract | exact model; power radius on independent replicas, variance <= 0.55; detection radius Hoeffding | 0.0000 | 0.0252 |
| earlier rule: V=0.55 read as declared, no falsifier tail, R=2 (replica contrasts 0.0249, 0.0255) | 2 x 115,591 | 78.3 | 78 | 79 | unverified | exact model; power radius on independent replicas, variance <= 0.55; detection radius Hoeffding | 0.0000 | 0.0252 |
| exact, Cantelli V=0.55, R=4 equal replicas (hypothetical) | 2 x 95,825 | 65.3 | 65 | 66 | 0.8, admitted contract | exact model; detection and power radius on independent replicas, variance <= 0.55; hypothetical equal replicas | 0.0000 | 0.0249 |
| exact, Hoeffding, R=1, rep_delay 100 us | 2 x 152,183 | 56.8 | 56 | 57 | unverified | exact model; state-prep error unmodeled | 0.0000 | 0.0249 |
| exact, Hoeffding, R=1, rep_delay 50 us | 2 x 152,183 | 41.5 | 41 | 42 | unverified | exact model; state-prep error unmodeled | 0.0000 | 0.0249 |
| extension: Bernstein with V=0.55, R=1 | 2 x 84,978 | 58.2 | 58 | 59 | 0.8, contract change | exact model; variance <= 0.55 | 0.0000 | - |
| extension: Hoeffding over independent replicas, R=2 (replica contrasts 0.0249, 0.0255) | 2 x 74,260 | 51.1 | 51 | 52 | 0.8, contract change | exact model; independent replicas | 0.0000 | - |
| normal approximation, one-sided alpha 0.05, pooled variance | 2 x 9,858 | 8.8 | 9 | 9 | 0.8 asymptotic, contract change | exact model; normal limit | 0.0000 | - |

Executions count shots summed over the two PUBs; replicas share a shot. The dry run selected `candidate-001-shots-122880` (2 replicas, 122,880 shots per arm, 83.1 s) under a 95 s job ceiling.

**CZ reduction (exact model, Hoeffding, R=1).** Removing k routed CZ scales the contrast by rho^-k; the two columns take rho from 1 - 4/3 x the Kingston median CZ error and from the reference contrast's own decay over its CZ count. Cells: shots per arm / planner seconds at 250 us.

| k removed | rho = 0.99745 | rho = 0.99687 |
| --- | --- | --- |
| 0 | 152,183 / 102.4 | 152,183 / 102.4 |
| 25 | 133,949 / 90.4 | 130,093 / 87.9 |
| 50 | 117,900 / 79.9 | 111,209 / 75.5 |
| 100 | 91,340 / 62.4 | 81,267 / 55.8 |
| 200 | 54,822 / 38.4 | 43,398 / 30.8 |

<!-- n21-usage-budget:end -->
