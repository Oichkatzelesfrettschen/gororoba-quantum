# Measurement-sequence envelope successor: a fluctuating-rate relaxation model with an admission gate

Status: design v3, before review. The width-32 envelope run of 2026-10-27 (`results/live/2026-10-27T014422.881898Z`)
executed as planned, billed 38 s, and returned no device verdict because its reset screen withheld all 32 qubits
([findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)). This successor keeps the envelope contract
of [measurement-sequence-adaptive-envelope.md](measurement-sequence-adaptive-envelope.md): the layout rule and width
tiers, the 20 us repetition delay with the 50 us fallback, one client-side Sampler job per attempt, the aggregate cap
and the replan bound. It replaces the relaxation nuisance model the departure prediction rests on, adds an admission
gate on that model, measures carryover inside the job, and makes the settle and delay arms descriptive.

## What the retained run established

The run's shot-order diagnostics
([findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md#shot-order-diagnostics-not-preregistered),
[envelope-run-raw-diagnostics.json](../evidence/measurement_sequence/envelope-run-raw-diagnostics.json)) read the
shot-ordered bits under `raw/`:

- Execution is column-wise: a row's final bit correlates with the previous PUB's at the same shot index (rms z 3.37)
  and not one column away (rms z 1.19 and 1.20).
- Carryover through the terminal reset, the repetition delay and `init_qubits` is +0.0000 +- 0.0006 (the ro0 row
  conditioned on its predecessor's final bit, 32 qubits).
- The in-job T1 series is not an exponential decay to the ground state. The analysis's (T1, q) fit puts the plateau q
  near 0.7 in every quarter of the job and reads it as a negative initialization excitation. A decay rate that
  fluctuates faster than the job resolves, gamma-distributed with mean mu and shape k, gives the survival
  (1 + mu t / k)^(-k) with q = 1; it fits 25 of 30 qubits against the (T1, q) fit's 23, with median shape 3.5, and its
  mean lifetime 1 / mu equals the calibrated T1 (median ratio 1.003).
- Under that model the N = 16 measure residual falls from +0.0185 to +0.0090, level with the unitary arm's +0.0109
  gate-model residual. The departure offset is nuisance model plus gate residual; the run shows no measurement-induced
  departure at the scale of the 0.0188 floor.
- Phase-sensitive rows (delay, unitary) correlate across consecutive circuits about 50 us apart and decorrelate within
  a column; the delay arm stands +0.115 above its idle model, which takes the calibrated Hahn-echo T2 for free
  evolution. Both point at qubit frequency fluctuating on sub-millisecond time scales.

## Relaxation nuisance model

`measurement_sequence_analysis` replaces the (T1, q) fit by the gamma-rate model: mean lifetime T = 1 / mu and shape
k, q fixed at 1, so the initialization excitation the chains start from is the one the ro0 bracket reads and no fitted
parameter stands for it. Every model chain the analysis evaluates (the arm tables, `implied_loss`, the settle
prediction, the gate-model curves and `fit_eps`) averages `chain_matrix` over the rate distribution at M
equal-probability midpoint quantiles; M is fixed in the analysis (64 in the diagnostics record) after a convergence
check against 2M on the fixture.

The fit scans a fixed geometric grid of shapes (0.25 to 1000, plus the exponential limit), profiles T at each shape by
the bounded Brent search `fit_t1` already uses, and refines the best grid interval by golden-section search in log k
with the same nested profile. The refinement makes the fitted values continuous in the counts, which the analysis's
numerical error propagation (`propagate_many`) differentiates; a bare grid argmin would jump between grid shapes. Both
stages are deterministic and follow the grid-then-golden-section pattern `fit_h2_batch` already batches
([vectorized-fits.md](../runbooks/vectorized-fits.md)).

The T1 series gains a 400 us delay (delays 0, 20, 50, 100, 200 and 400 us), so the lack-of-fit test has three
degrees of freedom and reaches the tail where the gamma-rate and plateau models part most: extrapolated from the
retained run's five delays, the two fitted models differ at 400 us by a median 0.018 in excited population (range
-0.008 to 0.056), about four standard errors of one 8192-shot row at P1 near 0.25. `msqe_groups` already takes the t1 delays as an argument; the envelope family passes six, and the
original family's five stay as they are.

## Admission gate

A qubit's T1 series enters the pinching analysis when the gamma-rate fit's chi-square, with dof = delays after the
bracket minus 2, has a p-value at or above 0.01 / W. A qubit that fails is reported descriptively with its fit and
excluded from every device verdict. On the retained run 25 of 30 informative qubits pass at the unadjusted 0.01.

## Carryover inside the job

The pattern rows measure D_q, the excitation an |1> end state leaves at the next shot's start, per qubit. Each pattern
row prepares a fixed bit on each qubit (x or nothing, then read), and consecutive pattern rows run at the same shot
index one circuit apart under column-wise execution. Among them, a qubit's P1 on rows that read ground after a row
that prepared 1, minus after a row that prepared 0, is D_q; on rows that prepare 1 the x flips the carried excitation,
which enters with the opposite sign; the two combine by inverse variance
(`pattern_carryover` in `scripts/msq_envelope_raw_diagnostics.py`). Conditioning on the prepared bit, not the read
bit, keeps readout misassignment out of the split. On the retained run's 35 pattern-row pairs the per-qubit standard
error is 0.0003 (median), and D reads +0.00045 +- 0.00006 pooled. The ro0 row conditioned on its predecessor reads
the same quantity with a lopsided split (93 % of predecessor shots end in 1, standard error 0.0028) and stays a
reported cross-check.

The estimator reads about zero under any order other than column-wise, so a wrong order would pass the screen
falsely. The order test is therefore preregistered and fails closed: the same-shot conditional differences of
consecutive delay-arm rows must exceed their one-column-misaligned counterparts (pooled one-sided z above 3; the
retained run gives rms z 3.37 against 1.19). If it fails, the carryover screen withholds every qubit.

Screen: a qubit stays usable when B_q = A_q * U_q lies below the margin 0.25 * 0.0188 = 0.0047, with U_q the one-sided
upper confidence bound of |D_q| (Bonferroni over W) and A_q the qubit's allocation bias per unit excitation. A_q is
evaluated at the vertex allocation itself: the sensitivity procedure plants U_q on every member class with a positive
departure coefficient and none on the others, and the reverse, refits through the gamma-rate model on the run's own
counts, and takes the larger absolute departure shift divided by U_q, so no linearization enters the bound
(`scripts/msq_carryover_sensitivity.py` gains this vertex mode and the gamma-rate model). On the retained run, with
the (T1, q) allocation coefficients, U_q has median 0.0011 and maximum 0.0050, and B_q median 0.0021 and maximum
0.0043: all 30 informative qubits pass. The sizing replay (Sequence) recomputes A_q under the gamma-rate model. The
in-job reset controls rc1 and rc0 stay as a reported diagnostic.

## Verdicts

- Departure and count rule: preregistered, on qubits that pass the admission gate, the carryover screen and the
  pattern screen, with the gate-model systematic of `evaluate_qubit` as before. The device verdict needs 8 such qubits;
  below 8 the analysis reports every kept qubit's pinching result and withholds only the device verdict.
- Mutation test: preregistered, unchanged.
- Settle arm: descriptive. The model's settle gap moves by 8.5e-5 when T2 halves on the fixture (the transverse state
  is zeroed at each pinch and only the sx maps see T2), so no idle-model parameter produces the run's settle excess,
  and no verdict reads the settle arm.
- Delay arm: descriptive; the analysis reports the free-evolution dephasing time the delay arm implies beside the
  calibrated echo T2.

## Null calibration

`msq_envelope_null.py` becomes the batched estimator of issue #579, extended to the gamma-rate fit (batched shape
scan, nested Brent, golden section), with the scalar bit-identity gate the repository requires. Each replicate draws,
per qubit:

- a calibration from the retained run's 30 informative qubits (T1, T2, readout errors, sx error), resampled with
  replacement;
- a rate shape from the retained run's admitted gamma-rate shapes, with mean lifetime equal to that calibration's T1;
- the sx-error residual as before (common +0.011, independent SD 0.0105);
- a carryover D at the screen's acceptance limit, allocated to the vertex that maximizes the departure bias, with the
  same sign on every qubit because each fused row is one member on all qubits.

Every replicate runs the complete pipeline: device counts with binomial shot noise, the admission gate, the order test
and carryover screen, the pattern screen, and the departure, count-rule and mutation verdicts. The family-wise
false-fire rate's one-sided 95 % Clopper-Pearson bound must stay below 0.01 (zero fires in 299 replicates suffice).
The per-component levels (admission, screen, contrast) are tuning choices; the null's bound is the error guarantee of
the whole pipeline. The case states that the live layout's calibrations fall inside the null's resampled range (T1,
T2, readout, sx error) and withholds the device verdict for any qubit outside it.

## Cost, size and approval scope

One added row at 400 us costs about 8192 x (400 + 20 + 9) us = 3.5 s, so attempt 1 at width 32 expects about 41 s;
the dry run's planner sets the ceilings (attempt 1 57 s, fallback 90 s and the 147 s two-attempt cap on the retained
dry run) and the case quotes them as attempt 1 against its ceiling. `collect.json` grows by about 0.5 MB per row from
42.4 MB, under the 45 MB limit; the dry run measures record, collection and raw sizes before the case. An attempt
stays one job and the change is a constructor and analysis change inside the `msq-envelope-v1` contract, which binds
both by digest.

## Sequence

1. Reviews of v3: the adversarial review skill, the advisor, then Codex gpt-daybreak-blue in tmux.
2. Issue #579: the batched null with its gate, then the gamma-rate extension.
3. Implementation: the gamma-rate model in the analysis and the device model, the 400 us delay, the admission gate,
   the order test and in-job carryover screen, the vertex sensitivity, descriptive settle and delay; tests and lanes.
4. A sizing replay of every successor screen and verdict over the retained run's counts (its five delays, so dof 2),
   then the null at the chosen width.
5. Dry run on the live calibration, the written case, approval, run.

Falsifiers: the order test failing on the live run (the carryover screen then withholds every qubit); fewer than 8
qubits passing the admission gate (the device verdict is withheld); the gamma-rate mean lifetime departing from the
calibrated T1 by more than a factor 1.5 at the median (reported, and the case for any further run revisits the
model); a null bound at or above 0.01; a settle or delay reading entering a device verdict.

## Superseded designs

- v1 bounded carryover with two single-circuit history-control jobs. Review found the single-class coefficient
  understated the allocation bias, the control jobs measured drift larger than the margin, and the null planted a T2
  error the model shows cannot move the settle gap.
- v2 equalized every member's end state with an `sx; measure; reset` coin. Codex found the departure verdict resting
  on the misspecified (T1, q) fit, a pooled coin statistic that cannot bound per-class bias, and the coin's register
  doubling every measured law near the collection size limit. The raw diagnostics then measured carryover at
  +0.0000 +- 0.0006, so the coin answered a bias the device does not show.
