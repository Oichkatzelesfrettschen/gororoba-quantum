# Measurement-sequence envelope successor: relaxation to the ground state, crosstalk-free carryover readers

Status: design v4.0, the frozen v3.3 with the corrections its implementation forced: a per-qubit shape bound at
the fitted T and a per-qubit settle test against the other qubits' median and MAD (v3.4), a reader statistic
stratified by reader and divided by the squared readout contrast (v3.5), null arms that can each fail (v3.6),
minority q arms with a measured sparse detectable gap (v3.7), a sparse power target bounded over its three widths
as one family (v3.8), a sparse arm that runs to 408 exposed verdicts per width (v3.9), and carryover readers inside their
predecessors' circuits with a posterior-contrast divisor (v4.0). It builds on the deduplicated
`collect.json` (each PUB's placed calibration stored once), which main carries. The
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

The shape enters no chain. Its effect is bounded instead, per qubit: at the qubit's fitted T and its live arm
durations, the analysis takes the largest absolute difference between the rate-averaged and the exponential N = 16
measure prediction over the shapes 0.25 to 64 (`msq_successor_analysis.shape_bounds`); the rate average is a 64-node
generalized Gauss-Laguerre rule in Golub-Welsch form (normalized weights with no Gamma(k), stable for every grid
shape), within 2e-6 to 5e-6 of a 256-node rule where the integrand kinks at T2 = 2 T1. The bound is a function of the
qubit's fit and context alone, so it is fixed before the departure is read, and it covers a shape the series leaves
loosely determined. The analysis adds each kept qubit's bound linearly to its shared systematic, which `pooled_z` sums
across qubits without quadrature. The sign of the difference follows the curvature of the chain's prediction in the
decay rate, not survival alone; on the retained contexts the rate-averaged prediction lies below the exponential one
at every evaluated point, and the bound uses the absolute value either way. On the retained run's 23 selected qubits
the bound has median 0.000485 and maximum 0.00161, against the 0.0188 floor
([successor-replay.json](../evidence/measurement_sequence/successor-replay.json)). A layout-wide domain (T from the
smallest calibrated T1 over 2.5 to the largest times 2.5) gives 0.0074, because it evaluates lifetimes no selected
qubit has; the per-qubit bound replaces it.

## Admission gate

A qubit's T1 series enters the analysis when the gamma-rate fit's chi-square, with dof equal to the delays after the
bracket minus 2, has a p-value at or above 0.01 / W. On the retained run 28 of the exploratory analysis's 30
informative qubits pass, and 29 of the 31 the successor's q = 1 planning error makes informative (q154 joins); the
rejects are q50 and q109, both near p = 1e-6. The gate
rejects shapes no rate mixture produces, such as a fast-decay component; it does not test q.

## Relaxation target

q = 1 is the assumption the departure prediction rests on; a q error of dq moves the N = 16 measure prediction by
about 0.034 dq (median over the retained contexts). q near 0.7 would need an equilibrium excited population near 14 %.
One row estimates q, and the settle arm vetoes inconsistency.

Equilibrium row. A new member idles 400 us from the initialized state and reads. With the ro0/t1-0 bracket
correction, a ground-start row at time t reads the corrected excitation e(t) = (1 - q)(1 - S(t)) / 2, so the analysis
estimates q_hat = 1 - 2 e(400 us) / (1 - S(400 us; T, k)) with the qubit's own fitted gamma survival, and
`propagate_many` carries the shared brackets and the fitted (T, k) into its standard error; q_hat is not clipped at 1.
Each qubit's tolerance comes from its own sensitivity: the analysis evaluates |dP0/dq| of the N = 16 measure
prediction at the qubit's context, and a qubit whose q_hat lower confidence bound (one-sided, Bonferroni over W) lies
below 1 - 0.25 x 0.0188 / |dP0/dq| is withheld. On the retained contexts |dP0/dq| spans 0.021 to 0.065, so the bound
runs from about 0.77 to 0.93; the smallest healthy-q lower confidence bound there is 0.988. The rule needs no power against a 1 to 3 % thermal population, which gives q of at least
0.94 and a departure shift below 0.004 at the largest sensitivity; against q near 0.7 the row reads e near 0.12 at T near 250 us, more than
twenty standard errors from q = 1. The carryover readers (below) bound the excitation any
predecessor leaves at the next shot's start, so a hot predecessor cannot fake a low q beyond the measured carryover.
The analysis reports q_hat as a job-local effective relaxation target, not as a thermal population.

Settle veto. The settle arm differs from the measure arm by sixteen 2 us idles placed after each pinch and before
the next rotation, so its gap at the measure arm's implied loss moves with q and also with the uncharacterized
post-measurement channel the constructor's 2 us gap was built to probe (residual readout photons, detuning during the
next rotation; [heron-r2-readout-resonator.md](../notes/ibm_quantum/heron-r2-readout-resonator.md)). It is a
composite q-consistency veto, not an estimate of q. Over the qubits that pass every gate independent of settle
(eligibility, pattern, admission, carryover, equilibrium), the analysis fits a random-effects model: a common mean gap
mu and a between-qubit scatter tau, with tau estimated about the weighted mean (DerSimonian-Laird moments) and floored
at 0.0019, the retained run's pilot value on the qubits that pass its pattern screen. A common-mean z,
mu / se(mu) with weights 1 / (s^2 + tau^2), beyond 3 in either direction withholds the device-level departure verdict;
because tau is fitted about mu, a common gap cannot hide in the scatter term. Each qubit is tested against the other
qubits alone, by their median and normal-consistent MAD (tau floored at 0.0019, the median's standard error added):
a qubit whose |g - median| / sqrt(s^2 + tau^2 + se^2) exceeds 3 is withheld. A scatter fitted with the tested qubit
inside it lets k equal outliers among n reach at most sqrt(n / k - 1) in z, and a moment fit that leaves only the
tested qubit out still caps two outliers among 8 near 2.4; the median and MAD keep a minority of outliers from
masking a qubit, though a second outlier among few others still moves them. For one outlier the per-qubit test's
detectable gap is (3 + 1.28) times its own denominator, sqrt(s^2 + tau^2 + se^2) with
se^2 = (pi / 2)(s^2 + tau^2) / (n - 1) at n pooled qubits: 0.0145, 0.0143 and 0.0135 at 8, 9 and 24 qubits on the
rehearsal's median s of 0.0024. Two outliers inflate the others' median and MAD, and at that size the null measures
per-qubit power 0.71, 0.75 and 0.85. The detectable gap of two outliers is therefore measured, not derived: a secant
in the planted size over the null's own per-qubit power, on a QRNG seed apart from the null's, puts power 0.9 at
0.0181, 0.0167 and 0.0145 (1.25, 1.17 and 1.07 times the single-outlier size;
[successor-sparse-scale.json](../evidence/measurement_sequence/successor-sparse-scale.json), 500 replicates a point,
binomial standard error about 0.01). A pool size the record does not cover, a width-32 layout's full pool among them,
has no stated detectable gap until the calibration (`scripts/msq_successor_null.py RECORD_DIR --calibrate-sparse`)
runs at that width, and the sparse arm refuses to run without it. On healthy simulated gaps the test withholds a
given qubit about 0.3 % of the time.

## Carryover readers

Twelve reader members carry the carryover measurement inside one circuit. Reader i repeats the signed measure member
it follows in the job (four at N = 2, P1 near 0.47; four at N = 4, P1 near 0.31; four at N = 8, P1 near 0.18), then
the terminal reset, an idle of the Heron r2 rep_delay floor (`qpu_planning.REP_DELAY_FLOOR_SECONDS`, 20 us, rounded
down to the Target's granularity by `qpu_planning.floored_delay`), a measurement into the 1-bit register `reader`,
and a reset. Shot j of the `reader` register reads the excitation the end state of shot j of the same circuit
leaves, so no PUB order enters the estimate, which the executor does not guarantee
([repetition-rate-execution.md](../notes/ibm_quantum/repetition-rate-execution.md)). Between shots the executor
adds at least the same delay and the `init_qubits` reset; every reset or idle maps populations linearly, so a
difference in excitation between predecessor classes after it is the difference before it times r1 - r0, with
|r1 - r0| <= 1, and the in-circuit D bounds the excitation the next shot starts with. Three assumptions remain and the
case states them: the qubit's evolution from the terminal reset to the next shot is Markovian (no memory in a
two-level defect or the resonator outlasts the reset), the executor's rep_delay starts after the terminal reset
completes, so the in-circuit idle is a prefix of the cross-shot sequence, and excitation and leakage do not cancel
between predecessor classes (the reader reads |2> as 1). The idles are phase-covariant, so no assumption on the
coherences after the reset enters.

A qubit's reader P1 after a predecessor final 1, minus after a final 0, estimates D_q times the reader's contrast c
times the predecessor bit's separation of its latent end states. Under discrimination overlap that separation is
c p (1 - p) / (m (1 - m)) at latent excitation p and measured P1 m = e01 + c p, which falls below c away from
p = 0.5 (at e01 0.019, e10 0.005 and p = 0.18 it is 0.94 c); under decay it is about 1. Each stratum therefore
divides by g = (m - e01)(1 - m - e10) / (m (1 - m)), the overlap value and the smaller of the two, with m the
stratum's own predecessor P1 and the errors from the job's ro0 and first t1 members (e10 from the t1 member includes
decay during its idle, an upper bound that lowers g and raises D). A stratum with g below 0.5 drops out. The strata
combine with weights g^2 / (p (1 - p) (1 / n1_k + 1 / n0_k)) at the reader P1 pooled over every stratum and both
classes, so a weight carries no reader outcome and the combination stays unbiased (weights from each stratum's own
variance read D about 8 % low on the null's carryover arm), and a baseline that differs between the N = 2, 4 and 8
blocks cannot enter through pooling. The standard error propagates each conditioning class's own binomial variance
through those fixed weights, so a differing baseline widens it. Every qubit reads ground in both conditioning classes, so readout crosstalk
cannot enter the contrast. Sized from the retained run's ro0 P1 (0.006) at 8192 shots, the twelve readers give a
per-qubit standard error near 0.0006.

Screen: a qubit stays usable when B_q = A_q * U_q lies below 0.25 * 0.0188 = 0.0047, with U_q the one-sided upper
confidence bound of |D_q| (Bonferroni over W) and A_q the qubit's departure shift per unit excitation at the
allocation vertex: the vertex is chosen from the signs of single-class sensitivities, then
`msq_successor_analysis.carryover_allocation` plants U_q at the vertex and its mirror, refits on the run's own counts
at q = 1 and takes the larger absolute shift. The vertex bounds every allocation whose carryover keeps one sign
across predecessor classes, whatever row precedes a member; a carryover whose sign differs between classes can
reach 1.6 to 1.8 times A_q * U_q, and the case states the one-sign assumption, since the readers measure D only
after measure-arm predecessors. At D near 0.0002, B reaches about 0.0029 at the retained run's median allocation
coefficient (1.59) and 0.0043 at its largest (2.31). The carryover screen replaces
`msq_envelope_analysis.reset_screen` as a gate; the reset controls rc1 and rc0 stay as a reported diagnostic.

Cross-check. Consecutive pattern rows read the cross-shot carryover under the submitted order: a qubit's P1 on rows
that prepare 0 after a row that prepared 1, minus after a row that prepared 0 (and the opposite sign on rows that
prepare 1, whose x flips the carried excitation), divided by the readout scale. `pattern_crosscheck` reports it per
qubit with (|D_pattern| - U) / se against the reader bound. A value above the Bonferroni z refutes the bound
direction or the claim that measure-arm predecessors cover every predecessor class; a shuffled order reads zero
here, so this check can fail only toward the falsifier.

Order. No verdict reads the PUB order beyond a cross-shot term the reader bound already covers (the equilibrium
row and the pattern screen see at most U exp(-400 us / T1) from the shot before). The executor's `chunk_timing` (one chunk holding every PUB) and the order
sentinels (two pairs of consecutive delay-arm rows at N = 4 or N = 8 in each third of the job, pooled one-sided z
above 3) are reported, and a run whose frequency noise is too low for the sentinels loses nothing.

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

`msq_successor_null_batch.py`, run through `scripts/msq_successor_null.py`, is the successor's batched null. It reuses the batched primitives of `msq_envelope_null.py`
(#589), which stays the retained envelope family's null with its bytes unchanged, and adds the batched gamma-rate fit
(shape scan, nested Brent profile, golden-section refinement) with scalar bit-identity tests at an interior shape, the 0.25 lower edge and the
exponential edge, and a 400-replicate width-32 benchmark before any cost is quoted. Each replicate draws, per qubit, a
calibration resampled from the retained run's 30 informative qubits (T1, T2, readout errors, sx error), a rate shape
resampled from the retained run's admitted shapes with T equal to that calibration's T1, the sx-error residual as
before (common +0.011, independent SD 0.0105), and a true carryover D_q, and runs device counts with binomial shot
noise, the pattern screen, the admission gate, the reader-based carryover screen (from joint predecessor and reader
outcomes drawn shot by shot from a latent predecessor end state read through the qubit's assignment errors, since
the reader statistic conditions on the predecessor's measured bit and the carryover follows its end state), the equilibrium bound,
the settle veto with its random-effects fit, and the departure, count-rule and mutation verdicts. The calibrations
come from the rehearsal dry run's live layout snapshot, not from the retained run, and shapes are drawn log-uniform
over the admitted grid, so the null covers the qubits the case selects.

- Carryover arms: true D_q three reader standard errors inside the acceptance boundary (D_q = 0.0047 / A_q - 3 SE),
  one sign shared by every qubit in an arm, a positive and a negative arm, each run until it has issued at least 299
  verdicts, so a zero-fire bound conditional on issuing falls below 0.01 per sign; the unconditional bound over every
  replicate run must also fall below 0.01. The negative arm's worst-case allocation loads measure-16 and the T1
  bracket rows but no settle member, so the common settle veto withholds about a quarter of its replicates; the
  unconditional bound, not an issuance floor, shows that this withholding manufactures no clean result. A separate
  boundary arm at 0, 1 and 2 standard errors inside calibrates selection failure and is exempt from the issuance
  requirement.
- q arms: true q where the screen's lower confidence bound at the expected counts sits on the tolerance bound, so
  about half the qubits pass the equilibrium screen. Planted on every qubit (q-tolerance), the deficit moves every
  settle gap together and the common settle veto withholds the device verdict in nearly every replicate, so that arm
  tests the veto: common-veto power at least 0.9 over 300 replicates. Its unconditional false-fire bound below 0.01
  then holds by withholding and only confirms that 300 replicates ran; the minority arm carries the false-fire
  question. Planted on two qubits with the rest at q = 1 (q-minority), the common veto stays quiet and the deficit
  must pass or fail the per-qubit screens on its own; the arm runs until 299 issued verdicts select at least one
  planted qubit (exposed verdicts) and requires the false-fire bound over exposed verdicts and the unconditional
  bound below 0.01. It reports how often the equilibrium screen and the settle veto withheld a planted qubit and how
  often one was selected. A q planted on the bound itself fails the screen in nearly every draw and tests nothing
  downstream.
- Settle arms: a common gap at 8, 9 and the full selected width, sized to the scatter floor times 4, which the
  common-mean veto must catch with power at least 0.9; and a sparse defect on two qubits at the same widths, planted
  as a per-pinch loss in the measure arm alone (the post-measurement tail the settle idles let decay, the
  `eps_settle = 0` device of `msa.device_model`), sized so its noise-free settle gap equals the measured two-outlier
  detectable gap above. Every bound of this arm is one-sided at 1 - 0.05/3 per width (Bonferroni over the three
  widths, a family-wise 95 %). Scored per planted qubit over each width's first 300 replicates, the arm fails when
  the Clopper-Pearson upper bound on the veto's power falls below 0.9, which detects a calibration that overstates
  the power by about 0.03 or more (a width fails at 523 or fewer withheld of 600 planted gaps, which happens half
  the time at true power 0.872). The bound counts the two planted gaps of a replicate as independent trials,
  though they correlate (about 0.43, 0.25 and 0 at 8, 9 and 24 qubits), so a calibration of true power 0.9 fails
  about 6 to 7 % of nulls rather than 5 %: the test errs strict. A missed tail moves the departure only in a verdict
  that selects a planted qubit (an exposed verdict), so each width runs until 408 exposed verdicts, the least
  zero-fire count whose bound falls below 0.01 at the family confidence, and the exposed and unconditional
  false-fire bounds must both stay below 0.01; this measures the departure bias a missed tail leaves. A tail below
  the detectable gap is the veto's stated blind spot.
- Plateau arms: plateau-low draws only the retained (T1, q) pairs with q below every tolerance bound, and the
  equilibrium bound and the settle veto must withhold its departure verdict; plateau-retained draws all 30 retained
  pairs (q from 0.28 to 1.02, the retained device itself) and runs until 299 verdicts are issued with the conditional
  and unconditional false-fire bounds below 0.01. The equilibrium screen, not the common veto, withholds most of its
  qubits (equilibrium screen about 84 %, common veto in about 16 % of replicates at width 24), so it issues about
  one verdict in 50 and needs about 15,000 replicates.
  plateau-minority plants retained pairs on two qubits among healthy ones, with q-minority's exposed-verdict
  targets.
- Each arm reports the unconditional false-fire rate, the false-fire rate conditional on a verdict being issued, and
  the informative-device rate (a verdict issued); the gamma arms must issue a verdict in at least 80 % of replicates,
  so that withholding cannot manufacture a clean bound. A device verdict counts the departure, count-rule and
  mutation results; the settle gap tests appear under `settle_descriptive` and never fire.
- No verdict reads the shot or PUB order (the readers sit in their predecessors' circuits and the order diagnostics
  are reported), so the null, a member-count simulator without shot order, covers the whole verdict path.
- The null's bound is the error guarantee of the whole pipeline; the per-component levels (admission, carryover, q_hat,
  settle) are tuning choices it calibrates.
- Coverage: the null runs on the rehearsal dry run's calibrations. The binding run's mechanical check
  (`scripts/approved_run.sh --check`) refuses the submit when a selected qubit's live T1, T2, readout error or sx error
  differs from the rehearsal snapshot by more than a factor the case states, so the binding run executes inside the
  domain the null covered, and a refusal sends nothing.
- Availability: the null rates hold whatever order the executor runs the PUBs in. The order sentinels read incidental
  phase noise and are reported; a run whose sub-millisecond frequency noise falls below their reach loses no verdict.

Null results at width 24 on the rehearsal dry run `results/live/2026-10-28T163139.827337Z`, every arm with 0
false fires and every target met. [successor-null.json](../evidence/measurement_sequence/successor-null.json) retains
each arm record's statistics without its rows, with the sha256 of the full record (`scripts/msq_successor_null.py
--summarize` writes it and refuses a record whose statistics this code would not compute from its rows). A row
replays byte for byte under the pinned `ci-py3.14.7` interpreter and the numeric environment of
[ci/AGENTS.md](../../ci/AGENTS.md#layout-and-gates) (one Python build and libm; another CPython build flips
individual rows) with `"$PYTHON" scripts/msq_successor_null.py results/live/2026-10-28T163139.827337Z --arm ARM
--replicates CAP` at the cap below, adding `--seed qrng:docs/evidence/anu_qrng/draw-2026-10-27T231303Z.json#3` for
the settle-sparse row (`SPARSE_CONFIRMATION_SEED`); every other row runs at the default `SUCCESSOR_NULL_SEED`. An arm
with a verdict count stops at it, so its replicates fall below its cap. `--arms all --out-dir DIR` writes every row's record through one
process pool at these caps and seeds ([null-shards.md](../runbooks/null-shards.md)). The plateau-retained record merges five
shards of `--shard K --shards 5` (`--merge`), which cuts it at the same replicate as an unsharded run.

| Arm | Cap | Replicates | Result |
|---|---|---|---|
| carryover-positive | 1500 | 369 | 299 issued; bounds 0.00997 issued, 0.0081 overall |
| carryover-negative | 1500 | 416 | 299 issued (common veto 22 %); bounds 0.00997, 0.0072 |
| carryover-boundary | 300 | 300 per offset | issued 0, 0 and 3 at 0, 1 and 2 SE inside (descriptive) |
| q-tolerance | 300 | 300 | common veto 99.7 %; overall bound 0.0099 |
| q-minority | 1500 | 447 | 299 exposed verdicts; bounds 0.00997 exposed, 0.0067 overall |
| settle-common | 300 | 300 per width | common veto 99.7 %, 100 % and 100 % at 8, 9 and 24 qubits |
| settle-sparse | 20000 | 8895, 3207, 2105 at 8, 9, 24 | 408 exposed verdicts per width, family exposed bound 0.00998; power over the first 300 replicates 0.912, 0.924, 0.897 (family bounds 0.936, 0.946, 0.922), over every replicate 0.909, 0.916, 0.895 |
| plateau-low | 300 | 300 | every departure verdict withheld |
| plateau-retained | 20000 | 15710 | 299 issued (1.9 %); bounds 0.00997 issued, 0.0002 overall |
| plateau-minority | 3000 | 1040 | 299 exposed verdicts; bounds 0.00997, 0.0029 |
| gamma | 400 | 400 | 396 informative (99 %); bound 0.0075 |

## What the run can detect

The departure test's sensitivity is set by the per-qubit gate-model systematic (about 0.016 to 0.019), which
`pooled_z` adds as a shared term, so it does not shrink with the qubit count. The eight-qubit planning record
([minimum-detectable-measured-floor.json](../evidence/measurement_sequence/minimum-detectable-measured-floor.json))
gives a minimum detectable pooled departure of -0.052 in N = 16 P0, a per-step loss near 0.0047. The q, shape and
carryover terms this design bounds sit an order of magnitude below that. The expected outcome is `consistent` unless
the measurement-induced loss exceeds about 0.005 per step; the case recomputes the limit at the selected width and
states it as what the run measures.

## Cost, size and approval scope

The equilibrium row costs about 8192 x (400 + 20 + 9) us = 3.5 s, and each in-circuit reader adds its 20 us idle and
a measurement to a measure row's shot. The planner prices the width-24 dry run's 101-PUB job
(`results/live/2026-10-28T163139.827337Z`) at 41.58 s against an attempt-1 ceiling of 57 s; the same job with
standalone reader PUBs priced at 38.15 s. The dry run's planner sets the ceilings and the case quotes the expected
charge against attempt 1's ceiling. Storing each
PUB's placed calibration once removes 22.1 MB of the retained run's 42.4 MB `collect.json`, so the 21 added rows fit
under the 45 MB limit with room for the wider width tiers; the dry run measures record, collection and raw sizes
before the case. An attempt stays one job, and the change is a constructor and analysis change inside the
`msq-envelope-v1` contract, which binds both by digest.

## Sequence

1. The `collect.json` deduplication pull request merges.
2. Reviews of v3.2: the advisor, then Codex gpt-daybreak-blue in tmux.
3. Implementation: the gamma-rate fit at q = 1 and its shape systematic, the equilibrium row and q_hat, the settle
   veto with in-job tau, the admission gate, the carryover readers and their screen with the vertex sensitivity, the
   order sentinels and the chunk condition (reported), descriptive delay; tests and lanes.
4. A sizing replay over the retained run's counts of every gate it can evaluate (no readers or equilibrium row there),
   then the batched null with all arms at the chosen width.
5. The case on a rehearsal dry run, approval, then `scripts/approved_run.sh`.

Falsifiers: q_hat below its per-qubit tolerance on most qubits (the departure verdict is withheld and q = 1 is
wrong); a pooled settle z
beyond 3; fewer than 8 selected qubits; a pattern-row cross-shot carryover above the reader bound at the Bonferroni z
(`pattern_crosscheck`); a carryover or plateau-retained arm's
conditional or unconditional zero-fire bound at or above 0.01; a minority arm with fewer than 299 exposed verdicts or
an exposed or unconditional bound at or above 0.01; a q-tolerance or settle-common arm whose common veto fires in
under 90 % of replicates; a gamma arm's informative-device rate below 80 %; a plateau-low arm whose departure verdict
is not withheld; a sparse settle arm whose per-qubit power upper bound at the family's 95 % falls below 0.9 at any
width, with fewer than 408 exposed verdicts at a width, or whose exposed or unconditional false-fire bound at the
family's 95 % reaches 0.01.

## Superseded designs

- v3.9 ran each carryover reader as its own PUB directly after its predecessor, so a reader read D only under
  column-wise execution, which the executor does not guarantee
  ([repetition-rate-execution.md](../notes/ibm_quantum/repetition-rate-execution.md)); a reordered reader reads
  D = 0, the value the screen passes. Its preregistered fail-closed order rule (one chunk, sentinels in each third)
  tested delay-arm sentinel pairs rather than the reader transitions. v4.0 moves each reader into its predecessor's
  circuit, where shot j's reader follows shot j's predecessor by construction, and reports the order rule as a
  diagnostic, a change to a preregistered rule that the case states. v3.9 also divided the reader difference by
  c^2, which under discrimination overlap reads D s / c with s / c below 1 away from P1 0.5 (0.94 at e01 0.019,
  e10 0.005 and latent excitation 0.18), and added the shape bound to the departure's systematic term without
  recomputing the per-qubit decisions the count rule reads.
- v3.8 scored the sparse arm's departure false-fire bound over all 300 replicates of each width. A missed tail
  moves the departure only in the verdicts that select a planted qubit, of which the confirmation null held 13, 42
  and 38 at 8, 9 and 24 qubits (exposed bounds 0.206, 0.069 and 0.076); the unconditional bound passed because the
  veto and the selection withheld the rest. It also applied the three-width Bonferroni share to the power bound
  alone, where it loosens, and not to the false-fire bound, where 0 fires in 300 replicates gives 0.01356.
- v3.7 bounded each width's sparse power at 95 % on its own. With power exactly 0.9 at every width the arm then
  fails at one width or more in up to 14 % of nulls, and more often within the calibration's one-standard-error
  stopping tolerance. Its null at the preregistered seed failed at 9 qubits: 524 of 599 planted gaps withheld,
  bound 0.8965 (8 and 24 qubits: 539/600 and 549/599). The family bound on the same counts is 0.9022, a verdict
  read after the counts were known, so the v3.8 verdict comes from a settle-sparse null on a fresh seed, ANU QRNG
  `docs/evidence/anu_qrng/draw-2026-10-27T231303Z.json` index 3 (`SPARSE_CONFIRMATION_SEED`, passed as `--seed`). The calibration is
  unchanged.
- v3.6's q arm planted its deficit on every qubit and required 299 issued verdicts; the deficit moves every settle
  gap, the common settle veto withheld 99.7 % of 3000 replicates, and the arm issued none. Its sparse arm planted the
  single-outlier detectable gap, at which two outliers reach per-qubit power 0.72, 0.74 and 0.86 at 8, 9 and 24
  qubits against a point target of 0.9.
- v3.5's null could not fail where it mattered. Its sparse settle arm shifted only the settle arm, so a missed gap
  could never move the departure, and it scored both planted qubits jointly against a per-qubit target with a size
  that left out the median's standard error; its q arm planted q on the tolerance bound, which the screen withholds
  in 97.5 % of draws, so the arm issued no verdict; its plateau arm drew all 30 retained pairs, 8 of them at or above
  the lowest tolerance bound, while its target required that no verdict issue; and its carryover arms carried an 80 %
  issuance floor that the negative arm's settle-veto withholding (27 %) breaks with zero fires in 459 replicates.
- v3.4 pooled the twelve readers into one conditional difference and divided it by the readout contrast once; the
  bit conditioning dilutes D by a second contrast factor (understating D by up to 1 - c), and pooling admits a
  composition bias of about 0.21 times a baseline that differs between reader blocks.
- v3.3 bound the shape term over a layout-wide lifetime domain (0.0074 on the retained run, 40 % of the floor)
  and tested each qubit's settle gap against a scatter fitted with that qubit inside it, which caps two equal
  outliers among 16 below z = 3; it also sized the sparse settle arm below the per-qubit test's detectable gap.
- v1 bounded carryover with two single-circuit history-control jobs; review found an understated allocation bias,
  inter-job drift above the margin and a T2 null that cannot move the settle gap.
- v2 equalized every member's end state with an `sx; measure; reset` coin; Codex found the departure resting on the
  (T1, q) fit and a pooled coin statistic that cannot bound per-class bias, and the device showed carryover near 0.0002.
- v3 averaged every chain over the gamma rate distribution and added a 400 us T1 delay; review found the shape never
  reaches the prediction, the verdict moving with q, and the settle arm demoted although it responds to q.
- v3.2 had the settle scatter fitted about zero (a common gap hid in it at 8 or 9 qubits), one median sensitivity
  for every qubit's q tolerance, carryover null points the screen nearly always rejected, and a min-max calibration
  coverage rule that a device-wide shift would trip.
- v3.1 fixed q = 1 and tested it with the settle gap and an equilibrium row; Codex found the settle gap composite,
  the equilibrium row without an estimator, the 4.1e-4 shape term one run's value, the null planting carryover where
  the screen rejects, alternating signs covering neither, the pattern-row estimator confounded by crosstalk, and the
  order test reading only the job's head.
