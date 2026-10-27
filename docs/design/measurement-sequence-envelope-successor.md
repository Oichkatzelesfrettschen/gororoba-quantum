# Measurement-sequence envelope successor: relaxation to the ground state, tested in the job

Status: design v3.1, after the adversarial review and the advisor review of v3; Codex review pending. The width-32
envelope run of 2026-10-27 (`results/live/2026-10-27T014422.881898Z`) executed as planned, billed 38 s, and returned
no device verdict because its reset screen withheld all 32 qubits
([findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)). This successor keeps the envelope contract
of [measurement-sequence-adaptive-envelope.md](measurement-sequence-adaptive-envelope.md): the layout rule and width
tiers, the 20 us repetition delay with the 50 us fallback, one client-side Sampler job per attempt, the aggregate cap
and the replan bound. It fixes the relaxation target the departure prediction rests on, tests that target inside the
job, measures carryover inside the job, and replaces the reset screen.

## What the retained run established

The run's shot-order diagnostics
([findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md#shot-order-diagnostics-not-preregistered),
[envelope-run-raw-diagnostics.json](../evidence/measurement_sequence/envelope-run-raw-diagnostics.json)) read the
shot-ordered bits under `raw/`:

- Execution is column-wise: a row's final bit correlates with the previous PUB's at the same shot index (rms z 3.37)
  and not one column away (rms z 1.19 and 1.20); the executor reported one chunk holding all 88 PUBs.
- Carryover through the terminal reset, the repetition delay and `init_qubits` is +0.00020 +- 0.00006 over the 26
  qubits that pass the pattern screen; readout crosstalk inflates it on the six the screen flags.
- The analysis's (T1, q) fit reads the in-job T1 series with a relaxation target q near 0.7 and converts it into a
  negative initialization excitation. Fixing q = 1, the physical value, moves the N = 16 measure residual from
  +0.0185 to +0.0089, level with the unitary arm's +0.0109 gate-model residual, and the settle gap from +0.0198
  (pooled z 18.7) to -0.0002 (one qubit, q62, at |z| >= 3). The departure offset and the settle excess were the same
  plateau artifact; the run shows no measurement-induced departure at the scale of the 0.0188 floor.
- The T1 series is fitted better by a decay rate that fluctuates faster than the job resolves (gamma-distributed,
  shape median 3.5) than by one exponential to the ground state (25 against 14 qubits at p >= 0.01), but the N = 16
  arms cannot tell that rate spread from one exponential at its mean lifetime: the two chains differ by at most
  4.1e-4 on the measure arm, because over the arm's microseconds any rate mixture decays as 1 - mu t.
- Phase-sensitive rows correlate across consecutive circuits about 50 us apart and decorrelate within a column, and
  the delay arm stands +0.115 above an idle model that takes the calibrated Hahn-echo T2 for free evolution: qubit
  frequency fluctuates on sub-millisecond time scales. The delay arm stays descriptive.

## Relaxation model and its assumption

Every model chain of `measurement_sequence_analysis` (the arm tables, `implied_loss`, the settle prediction, the
gate-model curves, `fit_eps`) runs as now, with q fixed at 1 and T1 the mean lifetime T of a gamma-rate fit of the
in-job series. The fit scans a fixed geometric shape grid (0.25 to 1000, with the exponential limit as the grid's
upper edge, reached by q86 on the retained run), profiles T at each shape by the bounded Brent search `fit_t1`
already uses, and refines the best interval by golden-section search in log k with the same nested profile, so T is
continuous in the counts that `propagate_many` differentiates. The shape enters no prediction; the rate-averaged
chain's departure from the exponential chain at T, at most 4.1e-4 on the retained run, adds as a stated systematic in
quadrature to the departure's standard error. The (T1, q) outputs `q`, `p_init` and `p_init_se` leave the record; the
fitted `t1_s` becomes T, and the record adds the shape, the fit's chi-square and its p-value.

q = 1 is the decisive assumption. q = z_eq / (1 - 2 p_init) in corrected units, so the retained fit's q near 0.7 with
ro0 P1 near 0.006 would need an equilibrium excited population near 14 %, roughly ten times what a transmon at its
operating temperature holds. Two in-job tests check it, and either withholds the departure verdict:

- Equilibrium row. A new member idles 400 us from the initialized state and reads, so its bracket-corrected z reads the
  relaxation target directly. q = 1 predicts an excited population near the ro0 level; the retained fit's q near 0.7
  predicts about 0.12 after 400 us at T near 250 us, more than twenty standard errors of an 8192-shot row. A qubit
  whose corrected equilibrium excitation exceeds 0.03 (q below 0.94) at its upper confidence bound is withheld from
  the departure verdict.
- Settle gap. The settle arm differs from the measure arm only by sixteen 2 us idles near the ground state, so the
  settle gap at the measure arm's implied loss reads the relaxation target over those idles. It becomes a
  preregistered gate on the departure verdict, not a pinching verdict of its own: a pooled settle z beyond 3 in
  either direction, with a device-scatter term sized from the retained run (0.0019 per qubit with q62 excluded,
  0.0035 with it), withholds the departure verdict, and a qubit whose own settle z exceeds 3 is withheld.

The planning model's own q is 1 / (1 - 2 x 0.015745) = 1.032; a q error of that size moves the measure prediction by
0.034 x 0.032 = 0.0011, with the same sign on every qubit, and the case states it beside the departure.

## Admission gate

A qubit's T1 series enters the analysis when the gamma-rate fit's chi-square, with dof equal to the delays after the
bracket minus 2, has a p-value at or above 0.01 / W. On the retained run 28 of 30 informative qubits pass. The gate
rejects fast-decay components and other shapes no rate mixture produces; it does not test q, which the equilibrium row
and the settle gap carry. The T1 delays stay at 0, 20, 50, 100 and 200 us.

## Carryover inside the job

The pattern rows measure D_q, the excitation an |1> end state leaves at the next shot's start. Each pattern row
prepares a fixed bit on each qubit (x or nothing, then read), and under column-wise execution consecutive pattern rows
run at the same shot index one circuit apart. A qubit's P1 on rows that read ground after a row that prepared 1, minus
after a row that prepared 0, is D_q; on rows that prepare 1 the x flips the carried excitation, which enters with the
opposite sign; the two combine by inverse variance (`pattern_carryover` in `scripts/msq_envelope_raw_diagnostics.py`).
Each difference takes the larger of its binomial and between-row standard errors, because a neighbor's current bit is
not balanced across the two conditioning classes of the 35 consecutive pairs and readout crosstalk adds row-to-row
scatter.

Screen: a qubit stays usable when B_q = A_q * U_q lies below 0.25 * 0.0188 = 0.0047, with U_q the one-sided upper
confidence bound of |D_q| (Bonferroni over W) and A_q the qubit's departure shift per unit excitation at the
allocation vertex. The vertex is chosen from the signs of single-class sensitivities, then the procedure plants U_q
at that vertex and its mirror, refits the analysis on the run's own counts, and takes the larger absolute shift
(`scripts/msq_carryover_sensitivity.py` gains this vertex mode at q = 1). On the retained run, with the (T1, q)
allocation coefficients, 29 of 30 informative qubits pass (q100 reaches 0.0051) and 25 pass this screen and the
pattern screen together. The carryover screen replaces `msq_envelope_analysis.reset_screen` as a gate; the in-job
reset controls rc1 and rc0 stay as a reported diagnostic.

The estimator reads about zero under any order but column-wise, so it needs the order established, and it cannot check
its own order. Two preregistered conditions establish it and fail closed (the carryover screen withholds every qubit
when either fails): the executor's `chunk_timing` reports one chunk holding every PUB, and the same-shot conditional
differences of consecutive delay-arm rows exceed their one-column-misaligned counterparts at pooled one-sided z above
3 (57.9 on the retained run, 29.6 on a quarter of its shots).

## Verdicts

- Execution-time eligibility, the pattern screen, the admission gate, the carryover screen and the equilibrium-row
  test select the qubits; the settle gap gates the device-level departure verdict as above.
- Departure and count rule: preregistered on the selected qubits, with the gate-model systematic of `evaluate_qubit`,
  the rate-average systematic and the device-scatter widening as before. The device verdict needs 8 selected qubits;
  below 8 the analysis reports every kept qubit's pinching result and withholds only the device verdict.
- Mutation test: preregistered, unchanged.
- Delay arm: descriptive, with the free-evolution dephasing time it implies reported beside the calibrated echo T2.

## Null calibration

`msq_envelope_null.py` is the batched estimator of issue #579 (pull request #589), extended to the gamma-rate fit:
the shape scan, the nested Brent profile (its masked port already exists) and the golden-section refinement, with the
scalar bit-identity gate. With q fixed and the shape out of the chains, every chain stays the exponential one the
batched path already computes, so a replicate costs about what it does now. Each replicate draws, per qubit, a
calibration resampled from the retained run's 30 informative qubits (T1, T2, readout errors, sx error), a rate shape
resampled from the retained run's admitted shapes with mean lifetime equal to that calibration's T1, the sx-error
residual as before (common +0.011, independent SD 0.0105), and carryover at the screen's acceptance limit at the
allocation vertex, with one sign shared by every qubit and the sign alternating between replicates. Every replicate
runs device counts with binomial shot noise, the pattern screen, the admission gate, the carryover screen, the
equilibrium-row test, the settle gate, and the departure, count-rule and mutation verdicts. The family-wise false-fire
rate's one-sided 95 % Clopper-Pearson bound must stay below 0.01.

A second arm draws the retained (T1, q) values as the truth, q near 0.7, and must show the equilibrium-row test and
the settle gate withholding the departure verdict; that arm is the evidence those gates do work. The order conditions
gate data validity rather than a verdict and stay out of the null: a member-count simulator has no shot order, and the
run shows no model of the frequency fluctuation that produces the adjacency signal.

## Cost, size and approval scope

The equilibrium row costs about 8192 x (400 + 20 + 9) us = 3.5 s, so attempt 1 at width 32 expects about 41 s; the
dry run's planner sets the ceilings (on the retained dry run: attempt 1 57 s, fallback 90 s, 147 s for both) and the
case quotes the expected charge against attempt 1's ceiling. `collect.json` grows by about 0.5 MB from 42.4 MB, under
the 45 MB limit; the dry run measures record, collection and raw sizes before the case. An attempt stays one job, and
the change is a constructor and analysis change inside the `msq-envelope-v1` contract, which binds both by digest.

## Sequence

1. Reviews of v3.1: the adversarial review skill and the advisor (done on v3), then Codex gpt-daybreak-blue in tmux.
2. Pull request #589 (the batched null) merges; then its gamma-rate extension.
3. Implementation: the gamma-rate fit at q = 1, the equilibrium row, the settle gate, the admission gate, the order
   conditions, the pattern-row carryover screen with its vertex sensitivity, descriptive delay; tests and lanes.
4. A sizing replay of every successor screen and verdict over the retained run's counts (no equilibrium row there),
   then the null at the chosen width with both arms.
5. Dry run on the live calibration, the written case, approval, run.

Falsifiers: the equilibrium row reading an excited population above 0.03 on most qubits (q = 1 is then wrong, and the
departure verdict is withheld); a pooled settle z beyond 3; fewer than 8 selected qubits (the device verdict is
withheld); either order condition failing (every qubit is withheld); a gamma-arm null bound at or above 0.01; a
plateau-arm null in which the gates fail to withhold.

## Superseded designs

- v1 bounded carryover with two single-circuit history-control jobs. Review found the single-class coefficient
  understated the allocation bias, the control jobs measured drift larger than the margin, and the null planted a T2
  error the model shows cannot move the settle gap.
- v2 equalized every member's end state with an `sx; measure; reset` coin. Codex found the departure verdict resting
  on the (T1, q) fit and a pooled coin statistic that cannot bound per-class bias; the raw diagnostics then measured
  carryover at about 0.0002, so the coin answered a bias the device does not show.
- v3 averaged every chain over the gamma rate distribution and added a 400 us T1-series delay. Review found the shape
  never reaches the N = 16 prediction, the verdict moving with q, which the admission gate and the tail delay cannot
  test, and the settle arm demoted although it tests q.
