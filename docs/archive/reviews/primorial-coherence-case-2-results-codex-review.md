# Adversarial review: primorial coherence case 2 results and the case-3 choice

## Scope and verdict

The reviewed artifacts are a retained IBM Heron r2 acquisition, its raw shot archive, a simulator-derived
prediction, and a statistical falsification decision. The relevant fields are statistical coverage, noise-model
conformance, calibration provenance, and reproducible evidence retention. I read every path named by the brief,
including every JSON and QPY file below each named result directory, and traced the relevant implementation in
`scripts/primorial_probe_case.py`, `gororoba_quantum/primorial_tomography.py`,
`gororoba_quantum/dynamic_density.py`, and the collection calibration path in `gororoba_quantum/live_run.py`.

Case 2 is sound as a retained descriptive result and as a falsification of the case-2 prediction procedure. Case 2
does not identify the proposed physical preparation-excitation mechanism. The principal defect is statistical, not
cosmetic: the prediction uses a simultaneous one-sided upper confidence bound as though it were the true channel
probability, then centers a two-sided prediction band on the resulting simulation. The three large positive band
centers are therefore substantially constructed by the conservative bound. The later calibration mismatch supplies
an independent reason to keep the result descriptive. `falsify` applies that final safeguard correctly.

## Findings

### P1 — The band treats an upper confidence bound as a generative parameter, so its advertised coverage does not apply to the unknown physical channel

`state-prep-excess.json` explicitly defines `eps` from 138 one-sided Clopper-Pearson bounds at family-wise alpha
0.01 (`results/live/2026-10-26T215024.737181Z/state-prep-excess.json:4457-4537`).
`path_excitation` then chooses the largest of the three qubit bounds for a path
(`scripts/primorial_probe_case.py:1113-1134`). `ExcitedArmLaw` uses that scalar as an X-error probability on every
active qubit (`scripts/primorial_probe_case.py:851-866`), and `decide_many` places the resulting signed incoherent
shift in the band center (`scripts/primorial_probe_case.py:989-1012`). A confidence limit is a set boundary, not a
point estimate. Conditional Gaussian coverage around the simulation at the upper boundary does not establish
family-wise coverage for the unknown nuisance probability inside the confidence set.

The retained numbers make the consequence measurable:

| path | retained path `eps` | `01` center | observed `01` | zero-`eps` simulated `01` shift | retained-`eps` simulated `01` shift |
| --- | ---: | ---: | ---: | ---: | ---: |
| 58-71-72 | 0.110066 | 0.124743 | 0.010099 | 0.000354 | 0.124800 |
| 15-19-35 | 0.072675 | 0.081360 | 0.001473 | 0.000389 | 0.081367 |
| 100-101-102 | 0.050020 | 0.055827 | -0.011154 | 0.000529 | 0.055749 |
| 132-133-134 | 0.050628 | 0.056210 | 0.027628 | 0.000663 | 0.056544 |

The local regression reproduces the brief's diagnostic. For the path-wire `01` Walsh coefficient, the band-center
regression against `eps` has slope 1.12651 and r = 0.999862, while the hardware regression has slope -0.02840,
r = -0.06935, and p = 0.765. For the path-wire `02` coefficient, the corresponding values are 0.71793 and
r = 0.99899 for the center, versus 0.16703, r = 0.40081, and p = 0.0718 for hardware. The near-perfect center
correlation is an implementation consequence, not evidence that hardware follows the channel.

The remedy is to propagate the simultaneous control confidence set through the simulator. A defensible prediction
band takes the union or calibrated envelope of stage-2 predictive intervals over the allowed nuisance values. A
point-centered alternative may use a point estimate only if its uncertainty enters the prediction distribution.
Case 3 should also use three qubit-specific probabilities rather than the path maximum. For the four paths in the
table, applying the maximum to all three qubits inflates the expected initial-X count by factors 2.19 to 2.71 over
the sum of the three retained per-qubit bounds.

### P2 — The implemented channel is internally clear, but the controls do not identify that channel uniquely

`path_budgets` includes gap-88 arms, null arms, and all `readout3` basis-preparation arms, then sends every one
through the same leading-X channel (`scripts/primorial_probe_case.py:876-902`). `gradient_analysis` estimates
`p(1|0)` and `p(0|1)` from those simulated `readout3` arms and applies the resulting assignment inversion to the
gap-88 and null readings (`gororoba_quantum/primorial_tomography.py:129-145,224-249`). The simulator therefore
absorbs part of its own leading-X channel into an effective assignment channel. That construction is a coherent
effective SPAM model, but prep0 approximately equalling x_history does not distinguish a readout flip from a
history-independent initialization error, thermal population, or drift. The retained controls identify observed
fractions after a complete preparation-and-measurement pipeline, not the location of the error in that pipeline.

A local factorial ablation can separate the modeling choices before another acquisition. Recompute the 21 path
budgets while crossing these frozen factors: Clopper-Pearson upper limit versus control point estimate or confidence
set; scalar path maximum versus a three-qubit vector; leading X on gradient/null arms versus leading X on
`readout3` arms as well; and the stage-1 versus stage-2 retained calibration snapshot when a complete stage-2 Target
snapshot exists. Compare `01` and `02` centers, widths, and out-of-sample residuals for every variant. The zero-versus-
retained-`eps` slice already run locally shows that retained `eps` supplies 0.12445, 0.08098, 0.05522, and 0.05588 of
the four paths' respective `01` incoherent shifts. The remaining factors must be frozen from controls and mechanism,
not selected by which variant covers the case-2 stage-2 observations.

### P2 — The acquisition-time calibration gate could not see a backfilled calibration identity; the final falsifier handled the mismatch correctly

The case states that `properties(datetime=stage1_start)` makes the exported stage-1 snapshot “what ran by
construction” (`results/live/PRIMORIAL_COHERENCE_CASE_2.md:85-91`). The retained chronology is a counterexample.
Stage 1 started at 2026-10-26T22:05:50.230450Z and collection assigned calibration
2026-10-26T14:25:32-07:00. Stage 2 started at 2026-10-26T22:20:39.165833Z and collection assigned calibration
2026-10-26T15:03:42-07:00, whose timestamp is 2026-10-26T22:03:42Z, before the stage-1 start. Both the stage-2
dry run at 22:15:14Z and submission-time read at 22:17:13Z still recorded the older calibration. The provider's
historical view therefore changed after the gate had acted.

`falsify` compares every stage-2 member's execution calibration with the decision calibration and records a reason
when they differ (`scripts/primorial_probe_case.py:1329-1345`). The retained output consequently sets
`claim: descriptive` and names the 14:25:32 versus 15:03:42 mismatch
(`docs/evidence/primorial_cover/case2/stage2-falsification.json:1-6`). A local recomputation reproduced the retained
falsification byte-for-value. That behavior is correct: the calibration mismatch does not invalidate the raw counts,
but it prevents a device-question claim tied to the stage-1 model.

A case-3 pre-submit equality check cannot by itself close this failure mode. Case 3 needs a final, post-collection
calibration adjudication after a provider-documented or empirically bounded history-stabilization interval. The gate
must re-read the historical properties and Target for both execution windows, require the same calibration identity
and digests for both stages, require `calibration_changed_during_shots=false` for every member, and void the device
claim if a later-visible calibration has a timestamp at or before either execution start. Until the repository can
bound the provider's backfill interval, the gate can authorize acquisition but cannot certify a same-calibration
claim at submission time.

The locally retained per-qubit summaries do not resolve the calibration alternative: all 63 qubits shared by stages
1 and 2 have identical recorded T1, T2, and readout values despite the changed calibration label, while the retained
stage-2 artifacts lack a complete new Target snapshot for a gate-by-gate comparison. The recalibration is therefore
a live competing explanation, not a demonstrated cause of the coefficient residuals.

### P2 — Physical qubit 147 has a decisive arm difference, but “history-dependent” remains confounded with job and time

Physical qubit 147 recorded 21/32768 excited outcomes after the near-ground-state history and 1584/32768 after the
all-excited history (`results/live/2026-10-26T215024.737181Z/state-prep-excess.json:1661-1715`). The difference is
0.047699. A two-proportion normal statistic is z = 39.50. More conservatively, using the case's per-bound alpha
0.0000724638 gives a simultaneous upper bound 0.001355 for prep0 and lower bound 0.043960 for x_history, leaving a
positive gap of at least 0.042604. Sampling noise at 32768 shots does not explain the arm difference.

The causal label still exceeds the design. The case ran prep0 and x_history in separate jobs
(`results/live/PRIMORIAL_COHERENCE_CASE_2.md:59-65`), so history, job identity, order, and elapsed time are perfectly
confounded. The retained data establish a history-arm association under those two executions. Case 3 should split
the same total shots across counterbalanced replicated jobs, such as prep0/x_history/x_history/prep0, while keeping
the calibration criterion fixed. That design can distinguish a repeatable history effect from a one-job transient.

### P2 — The retained crosstalk result tests one signal arm on one path and cannot clear crosstalk on the other falsified paths

The code compares only the group's first member on the first path with one isolated reference
(`scripts/primorial_probe_case.py:1230-1257`). The retained test compares packed and isolated `g88_0_0_X` on
58-71-72 and reports chi-square 9.3493 with 7 degrees of freedom and p = 0.2285. That result supplies evidence for
one signal arm on 58-71-72. It does not test the null half of the subtraction, 15-19-35, or 100-101-102. Calling the
single result `consistent` is acceptable as the preregistered operational label, but the result cannot eliminate
path-specific packed-execution effects as an alternative mechanism.

Case 3 should either retain isolated signal and null references for every primary diagnostic path, with a
simultaneous test family, or narrow the crosstalk claim to the exact arm and path tested. A failure or indeterminate
result must continue to make the scientific result descriptive.

### P3 — The “three falsified paths are the three largest-eps paths” summary is false at retained precision

The three largest retained path bounds are 58-71-72 at 0.1100658773, 15-19-35 at 0.0726750009, and 132-133-134
at 0.0506283898. Path 132-133-134 remains inside every band; its observed `01` value is 0.027628 against
[0.016672, 0.095748]. The third falsified path, 100-101-102, has the slightly smaller bound 0.0500203205 and misses
only `01` (`docs/evidence/primorial_cover/case2/stage2-falsification.json:566-613` for 100-101-102; retained
stage-1 decision values above for both bounds). The accurate statement is that two of the three largest-bound paths
falsified, while the fourth-largest-bound path supplied the third falsification. The correction weakens the proposed
rank-order story without erasing the broader high-bound concentration.

## Direct answers to the brief

1. The code implements the stated leading-X mechanism exactly, including its use in simulated `readout3` arms.
   The data do not identify that mechanism. The upper-bound-as-center construction, the scalar path maximum, the
   effective assignment inversion, the calibration mismatch, and incompletely tested crosstalk all fit the retained
   pattern. The factorial local simulator ablation described above separates the first three choices; a complete
   stage-2 Target snapshot would add the calibration factor. Its model choice must remain frozen before fresh
   stage-2 observations are read.
2. `falsify` handles the observed mismatch correctly by producing a descriptive claim. The acquisition-time gate
   does not handle delayed calibration-history visibility, because both its dry-run and submission-time reads saw
   the older calibration. Case 3 needs final post-collection, history-stabilized reconciliation; same-calibration
   certification cannot rest on the pre-submit read alone.
3. The physical-qubit-147 arm difference is far outside simultaneous-bound sampling noise. The experiment does not
   isolate history as the cause because each arm occupied a different job. Counterbalanced repeated control jobs are
   required for that causal claim.

## Local checks and evidence integrity

- Every JSON document under the named bundles parsed successfully.
- All 214 files bound by the four raw indexes matched their SHA-256 entries.
- All 206 raw publication files held internally consistent register shapes: 4,480 registers and 12,147,084 binary
  shot strings matched each register's declared bit width and shot count.
- The five named QPY archives loaded locally. They contained 1, 1, 99, 105, and 105 circuits respectively; the
  stage-2 dry-run and submitted QPY archives shared SHA-256
  `e9b40ba4102b3771453dd12a1e847fc7ee239d12e50ebed8366d1ebf50c9b415`.
- Local recomputation reproduced `retained-paths.json`, `stage2-crosstalk.json`, and
  `stage2-falsification.json` exactly.
- The numerical checks used Python 3.14.8, Qiskit 2.5.2, NumPy 2.5.4, and SciPy 1.18.1 with bytecode writes
  disabled and `GOROROBA_WORKERS=1` for the simulator ablation.
- The review made zero provider calls. The checkout retained HEAD
  `c0559f18254a251501ed480e706c19659dbe3f39`; the requested ignored report is the only checkout file created by
  the review.

## Recommendation

Choose **C: retain case 2 in a results pull request first, then build case 3**. The results pull request should call
case 2 a descriptive cross-calibration acquisition and a falsification of the upper-bound-centered band model. It
should not call the three path misses evidence for a physical preparation-excitation mechanism.

After that retention, case 3 should take the full-rerun shape of option A rather than the selected four-path shape of
option B. The 22-path set supplies low-excess negative controls and prevents selection on the case-2 misses. Before
any new stage-2 data are collected, case 3 must freeze the qubit-specific split-channel law, counterbalanced control
schedule, confidence-set propagation, calibration adjudication, and crosstalk scope.

The preregistered primary falsifier should read: using only fresh case-3 controls and stage-1 probes, construct a
simultaneous 95% predictive set for all seven coefficients on every stage-2 path under the frozen split-channel law,
with control uncertainty propagated over its simultaneous confidence set; reject the split-channel model if any
fresh stage-2 coefficient falls outside that set. A calibration-identity or crosstalk-gate failure yields a
descriptive result rather than a pass. Freeze the prediction artifact and its digest before collecting or reading
the fresh stage-2 result. Case-2 stage-2 values may motivate the law, but they must not select case-3 parameters,
variants, or thresholds.

END OF REVIEW
