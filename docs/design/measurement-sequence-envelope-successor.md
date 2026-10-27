# Measurement-sequence envelope successor: relaxation to the ground state, crosstalk-free carryover readers

Status: design v3.2, after the adversarial and advisor reviews of v3 and the Codex review of v3.1; it needs a
deduplicated `collect.json` (each PUB's placed calibration stored once), built in its own pull request first. The
width-32 envelope run of 2026-10-27 (`results/live/2026-10-27T014422.881898Z`) executed as planned, billed 38 s, and
returned no device verdict because its reset screen withheld all 32 qubits
([findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)). This successor keeps the envelope contract
of [measurement-sequence-adaptive-envelope.md](measurement-sequence-adaptive-envelope.md): the layout rule and width
tiers, the 20 us repetition delay with the 50 us fallback, one client-side Sampler job per attempt, the aggregate cap
and the replan bound. It submits through the one-command binding dry run and submit (`scripts/approved_run.sh`,
[qpu-submission.md](../notes/ibm_quantum/qpu-submission.md)).

## What the retained run established

The run's shot-order diagnostics
([findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md#shot-order-diagnostics-not-preregistered),
[envelope-run-raw-diagnostics.json](../evidence/measurement_sequence/envelope-run-raw-diagnostics.json)):

- Execution is column-wise: a row's final bit correlates with the previous PUB's at the same shot index (rms z 3.37)
  and not one column away (rms z 1.19 and 1.20); the executor reported one chunk holding all 88 PUBs.
- Carryover through the terminal reset, the repetition delay and `init_qubits` is +0.00020 +- 0.00006 over the 26
  qubits that pass the pattern screen; readout crosstalk confounds the pattern-row estimator on the others.
- The (T1, q) fit reads the in-job T1 series with a relaxation target q near 0.7. At q = 1 the N = 16 measure
  residual falls from +0.0185 to +0.0089, level with the unitary arm's +0.0109 gate-model residual, and the settle gap
  from +0.0198 (pooled z 18.7) to -0.0002. No measurement-induced departure appears at the 0.0188 floor's scale.
- A gamma-distributed decay rate fits the series better than one exponential to the ground state, and its
  inverse-mean-rate time T fixes the initial slope exactly (S'(0) = -1 / T); over the measure arm's microseconds the
  rate-averaged chain and the exponential at T differed by at most 4.1e-4 on that run.
- Phase-sensitive rows correlate across consecutive circuits about 50 us apart and decorrelate within a column, and
  the delay arm stands +0.115 above an idle model that takes the Hahn-echo T2 for free evolution.

## Relaxation model

Every model chain of `measurement_sequence_analysis` runs with q fixed at 1 and T1 replaced by T, the
inverse-mean-rate time of a gamma-rate fit of the in-job series. The fit scans a fixed geometric shape grid from 0.25
to 1000 with the exponential limit as its upper edge, profiles T at each shape by the bounded Brent search `fit_t1`
already uses, and refines the best interval by golden-section search in log k with the same nested profile, so T is
continuous in the counts `propagate_many` differentiates. The record drops `q`, `p_init` and `p_init_se`, reports T as
`t1_s`, and adds the shape, the fit's chi-square and its p-value.

The shape enters no chain. Its effect is bounded instead: at dry run the planner evaluates the signed difference
between the rate-averaged and the exponential measure-arm prediction over the admitted domain (shapes 0.25 to the
exponential edge, T over the live layout's calibrated range with a factor 2.5 either side, the live arm durations),
and binds its maximum in the dry-run record. By Jensen's inequality rate variance raises survival at every time past
zero, so the difference has one sign wherever the prediction rises with survival; the analysis adds the bound
linearly to the departure's shared systematic in `pooled_z`, not in quadrature, and the dry-run evaluation checks
the sign over the domain.
At shape 0.25 on the retained contexts it reaches 0.0017, against the 0.0188 floor.

## Admission gate

A qubit's T1 series enters the analysis when the gamma-rate fit's chi-square, with dof equal to the delays after the
bracket minus 2, has a p-value at or above 0.01 / W. On the retained run 28 of 30 informative qubits pass. The gate
rejects shapes no rate mixture produces, such as a fast-decay component; it does not test q.

## Relaxation target

q = 1 is the assumption the departure prediction rests on; a q error of dq moves the N = 16 measure prediction by
about 0.034 dq (median over the retained contexts). q near 0.7 would need an equilibrium excited population near 14 %.
One row estimates q, and the settle arm vetoes inconsistency.

Equilibrium row. A new member idles 400 us from the initialized state and reads. With the ro0/t1-0 bracket
correction, a ground-start row at time t reads the corrected excitation e(t) = (1 - q)(1 - S(t)) / 2, so the analysis
estimates q_hat = 1 - 2 e(400 us) / (1 - S(400 us; T, k)) with the qubit's own fitted gamma survival, and
`propagate_many` carries the shared brackets and the fitted (T, k) into its standard error. The departure tolerates
a q error of 0.25 x 0.0188 / 0.034 = 0.14, so a qubit whose q_hat lower confidence bound (one-sided, Bonferroni over W)
lies below 0.86 is withheld. The rule needs no power against a 1 to 3 % thermal population, which gives q of at least
0.94 and a departure shift below 0.002; against q near 0.7 the row reads e near 0.12 at T near 250 us, more than
twenty standard errors from q = 1. The row runs directly after a carryover reader (below), whose predecessor-
conditioned excitation the readers measure, so a hot predecessor cannot fake a low q beyond the measured carryover.
The analysis reports q_hat as a job-local effective relaxation target, not as a thermal population.

Settle veto. The settle arm differs from the measure arm by sixteen 2 us idles placed after each pinch and before
the next rotation, so its gap at the measure arm's implied loss moves with q and also with the uncharacterized
post-measurement channel the constructor's 2 us gap was built to probe (residual readout photons, detuning during the
next rotation; [heron-r2-readout-resonator.md](../notes/ibm_quantum/heron-r2-readout-resonator.md)). It is a
composite q-consistency veto, not an estimate of q: a pooled settle z beyond 3 in either direction withholds the
device-level departure verdict, and a qubit whose own settle z exceeds 3 is withheld. The settle standard error adds
an independent per-qubit device-scatter term tau, estimated in the job by solving sum g^2 / (s^2 + tau^2) = n over the
qubits that pass every gate independent of settle (eligibility, pattern, admission, carryover, equilibrium), and
floored at 0.0019, the retained run's pilot value on the qubits that pass its pattern screen.

## Carryover readers

Twelve new members read ground only: measure, then the terminal reset. Each runs directly after a measure-arm row
that ends near 50/50 (four after the N = 2 rows, P1 near 0.47; four after N = 4, P1 near 0.31; four after N = 8, P1
near 0.18). Under column-wise execution a reader's shot j follows the predecessor's shot j, so a qubit's reader P1
after a predecessor final 1, minus after a final 0, divided by the qubit's readout contrast, is D_q, the excitation
an |1> end state leaves at the next shot's start. Every qubit reads ground in both conditioning classes, so readout
crosstalk cannot enter the contrast, and conditioning on the measured bit only dilutes D by the contrast the analysis
divides out. Sized from the retained run's ro0 P1 (0.006) at 8192 shots, the twelve readers give a per-qubit standard
error near 0.00056.

Screen: a qubit stays usable when B_q = A_q * U_q lies below 0.25 * 0.0188 = 0.0047, with U_q the one-sided upper
confidence bound of |D_q| (Bonferroni over W) and A_q the qubit's departure shift per unit excitation at the
allocation vertex: the vertex is chosen from the signs of single-class sensitivities, then
`scripts/msq_carryover_sensitivity.py` (gaining this vertex mode at q = 1) plants U_q at the vertex and its mirror,
refits on the run's own counts and takes the larger absolute shift. At D near 0.0002, B reaches about 0.0029 at the
retained run's median allocation coefficient (1.59) and 0.0043 at its largest (2.31). The pattern-row estimator stays
a reported cross-check. The carryover screen replaces `msq_envelope_analysis.reset_screen` as a gate; the reset
controls rc1 and rc0 stay as a reported diagnostic.

Order. The readers read about zero under any order but column-wise, so two preregistered conditions establish the
order and fail closed, withholding every qubit when either fails: the executor's `chunk_timing` reports one chunk
holding every PUB, and order sentinels pass in each third of the job. The constructor places pairs of consecutive
delay-arm rows (phase-sensitive, the strongest adjacency signal) at the head, between the reader blocks and among the
pattern rows at the tail; each segment's same-shot conditional differences must exceed their one-column-misaligned
counterparts at pooled one-sided z above 3 (the retained run's head segment gives 57.9).

## Verdicts

- Execution-time eligibility, the pattern screen, the admission gate, the carryover screen and the equilibrium-row
  bound select the qubits; the settle veto withholds the device-level departure verdict or a qubit as above.
- Departure and count rule: preregistered on the selected qubits, with the gate-model systematic of `evaluate_qubit`,
  the shape systematic as a shared term, and the device-scatter widening as before. The device verdict needs 8
  selected qubits; below 8 the analysis reports every kept qubit's pinching result and withholds only the device
  verdict.
- Mutation test: preregistered, unchanged.
- Delay arm: descriptive, with the free-evolution dephasing time it implies reported beside the calibrated echo T2.

## Null calibration

`msq_envelope_null.py` is the batched estimator of #589, extended to the gamma-rate fit (shape scan, nested Brent
profile, golden-section refinement) with scalar bit-identity tests at an interior shape, the 0.25 lower edge and the
exponential edge, and a 400-replicate width-32 benchmark before any cost is quoted. Each replicate draws, per qubit, a
calibration resampled from the retained run's 30 informative qubits (T1, T2, readout errors, sx error), a rate shape
resampled from the retained run's admitted shapes with T equal to that calibration's T1, the sx-error residual as
before (common +0.011, independent SD 0.0105), and a true carryover D_q, and runs device counts with binomial shot
noise, the pattern screen, the admission gate, the reader-based carryover screen, the equilibrium bound, the settle
veto with its in-job tau, and the departure, count-rule and mutation verdicts.

- Carryover arms: true D_q on a grid inside the acceptance boundary (D_q = 0.0047 / A_q minus 0, 1 and 2 reader
  standard errors), one sign shared by every qubit in an arm, a positive and a negative arm, each at least 299
  replicates so a zero-fire bound falls below 0.01 per sign.
- Plateau arm: the retained (T1, q) values as truth, q near 0.7; the equilibrium bound and the settle veto must
  withhold its departure verdict.
- Each arm reports the unconditional false-fire rate, the false-fire rate conditional on a verdict being issued, and
  the informative-device rate (a verdict issued); the gamma arms must issue a verdict in at least 80 % of replicates,
  so that withholding cannot manufacture a clean bound.
- The order conditions gate data validity and leave every downstream statistic unevaluated when they fail, so they
  stay out of the null; a member-count simulator has no shot order.

## Cost, size and approval scope

The equilibrium row costs about 8192 x (400 + 20 + 9) us = 3.5 s and the twelve readers about 3.3 s, so attempt 1 at
width 32 expects about 45 s; the dry run's planner sets the ceilings (on the retained dry run: attempt 1 57 s,
fallback 90 s, 147 s for both) and the case quotes the expected charge against attempt 1's ceiling. Storing each
PUB's placed calibration once removes 22.1 MB of the retained run's 42.4 MB `collect.json`, so 13 more rows fit
under the 45 MB limit with room for the wider width tiers; the dry run measures record, collection and raw sizes
before the case. An attempt stays one job, and the change is a constructor and analysis change inside the
`msq-envelope-v1` contract, which binds both by digest.

## Sequence

1. The `collect.json` deduplication pull request merges.
2. Reviews of v3.2: the advisor, then Codex gpt-daybreak-blue in tmux.
3. Implementation: the gamma-rate fit at q = 1 and its shape systematic, the equilibrium row and q_hat, the settle
   veto with in-job tau, the admission gate, the carryover readers and their screen with the vertex sensitivity, the
   order sentinels and the chunk condition, descriptive delay; tests and lanes.
4. A sizing replay over the retained run's counts of every gate it can evaluate (no readers or equilibrium row there),
   then the batched null with all arms at the chosen width.
5. The case on a rehearsal dry run, approval, then `scripts/approved_run.sh`.

Falsifiers: q_hat below 0.86 on most qubits (the departure verdict is withheld and q = 1 is wrong); a pooled settle z
beyond 3; fewer than 8 selected qubits; either order condition failing; a carryover arm's zero-fire bound at or above
0.01 or its informative-device rate below 80 %; a plateau arm whose departure verdict is not withheld.

## Superseded designs

- v1 bounded carryover with two single-circuit history-control jobs; review found an understated allocation bias,
  inter-job drift above the margin and a T2 null that cannot move the settle gap.
- v2 equalized every member's end state with an `sx; measure; reset` coin; Codex found the departure resting on the
  (T1, q) fit and a pooled coin statistic that cannot bound per-class bias, and the device showed carryover near 0.0002.
- v3 averaged every chain over the gamma rate distribution and added a 400 us T1 delay; review found the shape never
  reaches the prediction, the verdict moving with q, and the settle arm demoted although it responds to q.
- v3.1 fixed q = 1 and tested it with the settle gap and an equilibrium row; Codex found the settle gap composite,
  the equilibrium row without an estimator, the 4.1e-4 shape term one run's value, the null planting carryover where
  the screen rejects, alternating signs covering neither, the pattern-row estimator confounded by crosstalk, and the
  order test reading only the job's head.
