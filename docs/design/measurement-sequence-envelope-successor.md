# Measurement-sequence envelope successor: relaxation to the ground state, crosstalk-free carryover readers

Status: design v3.6, the frozen v3.3 with the corrections its implementation forced: a per-qubit shape bound at
the fitted T and a per-qubit settle test against the other qubits' median and MAD (v3.4), a reader statistic
stratified by reader and divided by the squared readout contrast (v3.5), and null arms that can each fail (v3.6). It builds on the deduplicated
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
twenty standard errors from q = 1. The row runs directly after a carryover reader (below), whose predecessor-
conditioned excitation the readers measure, so a hot predecessor cannot fake a low q beyond the measured carryover.
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
masking a qubit, though a second outlier among few others still moves them. The per-qubit test's detectable gap is
(3 + 1.28) times its own denominator, sqrt(s^2 + tau^2 + se^2) with se^2 = (pi / 2)(s^2 + tau^2) / (n - 1) at n
pooled qubits: 0.0145, 0.0143 and 0.0135 at 8, 9 and 24 qubits on the rehearsal's median s of 0.0024. One outlier
alone reaches per-qubit power 0.84 to 0.93 near that size on synthetic gaps; a second outlier among 7 others lowers
it to about 0.72 at 8 qubits, which the sparse null arm measures. On healthy simulated gaps the test withholds a
given qubit about 0.3 % of the time.

## Carryover readers

Twelve new members read ground only: measure, then the terminal reset. Each runs directly after a measure-arm row
that ends near 50/50 (four after the N = 2 rows, P1 near 0.47; four after N = 4, P1 near 0.31; four after N = 8, P1
near 0.18). Under column-wise execution a reader's shot j follows the predecessor's shot j, so a qubit's reader P1
after a predecessor final 1, minus after a final 0, estimates D_q, the excitation an |1> end state leaves at the next
shot's start, diluted twice: the reader reads it through its own contrast c, and the predecessor's measured bit
separates the predecessor's end states by at most c (exactly c under discrimination overlap, nearly 1 when the
readout error is decay). Each reader gives its own conditional difference, and the twelve combine with weights set by
their class sizes at the pooled reader P1, var_k = p (1 - p) (1 / n1_k + 1 / n0_k), so the weights carry no outcome
and the combination stays unbiased at P1 near 0.006 (weights from each stratum's own variance read D about 8 % low on
the null's carryover arm) (a baseline that differs between the N = 2, 4 and 8 blocks, whose predecessors end at different P1, cannot enter
through pooling), and the combination divided by c^2 bounds |D_q| from above. Every qubit reads ground in both
conditioning classes, so readout crosstalk cannot enter the contrast. Sized from the retained run's ro0 P1 (0.006) at
8192 shots, the twelve readers give a per-qubit standard error near 0.0006.

Screen: a qubit stays usable when B_q = A_q * U_q lies below 0.25 * 0.0188 = 0.0047, with U_q the one-sided upper
confidence bound of |D_q| (Bonferroni over W) and A_q the qubit's departure shift per unit excitation at the
allocation vertex: the vertex is chosen from the signs of single-class sensitivities, then
`msq_successor_analysis.carryover_allocation` plants U_q at the vertex and its mirror, refits on the run's own counts
at q = 1 and takes the larger absolute shift. The vertex bounds every allocation whose carryover keeps one sign
across predecessor classes; a carryover whose sign differs between classes can reach 1.6 to 1.8 times A_q * U_q, and
the case states the one-sign assumption, since the readers measure D only after measure-arm predecessors. At D near 0.0002, B reaches about 0.0029 at the
retained run's median allocation coefficient (1.59) and 0.0043 at its largest (2.31). The pattern-row estimator stays
a reported cross-check. The carryover screen replaces `msq_envelope_analysis.reset_screen` as a gate; the reset
controls rc1 and rc0 stay as a reported diagnostic.

Order. The readers read about zero under any order but column-wise, so two preregistered conditions establish the
order and fail closed, withholding every qubit when either fails: the executor's `chunk_timing` reports one chunk
holding every PUB (no repository source documents the order of `chunk_timing`'s parts as execution order, so the
chunk condition rules out a reported split and no more), and order sentinels pass in each third of the job. The
constructor places two pairs of consecutive delay-arm rows at N = 4 or N = 8 at the head, between the reader blocks
and among the pattern rows at the tail; each segment's same-shot conditional differences, minus the mean of the
one-column-misaligned ones, must reach pooled one-sided z above 3. On the retained run a single N = 4 or N = 8 pair
gives z 10 to 21, so two pairs per segment pass with a wide margin, while the N = 1 pairs give -0.7 to 2.0 and are
not used; a run whose frequency noise falls far enough to fail this withholds every qubit, which the case states as
the run's remaining all-withheld risk.

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
- q arm: true q where the screen's lower confidence bound at the expected counts sits on the tolerance bound, so
  about half the qubits pass; run until 299 verdicts are issued, with the conditional and unconditional false-fire
  bounds below 0.01. A q planted on the bound itself fails the screen in nearly every draw and tests nothing
  downstream.
- Settle arms: a common gap at 8, 9 and the full selected width, sized to the scatter floor times 4, which the
  common-mean veto must catch with power at least 0.9; and a sparse defect on two qubits at the same widths, planted
  as a per-pinch loss in the measure arm alone (the post-measurement tail the settle idles let decay, the
  `eps_settle = 0` device of `msa.device_model`), sized so its noise-free settle gap equals the detectable gap above.
  The per-qubit veto must withhold each planted qubit with power at least 0.9, scored per qubit, and the departure
  false-fire bound over all replicates must stay below 0.01, which measures the departure bias a missed tail leaves.
  A tail below that size is the veto's stated blind spot.
- Plateau arms: plateau-low draws only the retained (T1, q) pairs with q below every tolerance bound, and the
  equilibrium bound and the settle veto must withhold its departure verdict; plateau-retained draws all 30 retained
  pairs (q from 0.28 to 1.02, the retained device itself) and runs until 299 verdicts are issued with the conditional
  and unconditional false-fire bounds below 0.01.
- Each arm reports the unconditional false-fire rate, the false-fire rate conditional on a verdict being issued, and
  the informative-device rate (a verdict issued); the gamma arms must issue a verdict in at least 80 % of replicates,
  so that withholding cannot manufacture a clean bound. A device verdict counts the departure, count-rule and
  mutation results; the settle gap tests appear under `settle_descriptive` and never fire.
- The order conditions gate data validity and leave every downstream statistic unevaluated when they fail, so they
  stay out of the null; a member-count simulator has no shot order.
- The null's bound is the error guarantee of the whole pipeline; the per-component levels (admission, carryover, q_hat,
  settle) are tuning choices it calibrates.
- Coverage: the null runs on the rehearsal dry run's calibrations. The binding run's mechanical check
  (`scripts/approved_run.sh --check`) refuses the submit when a selected qubit's live T1, T2, readout error or sx error
  differs from the rehearsal snapshot by more than a factor the case states, so the binding run executes inside the
  domain the null covered, and a refusal sends nothing.
- Availability: every null rate is conditional on the order conditions passing, since a member-count simulator has no
  shot order. The order sentinels read incidental phase noise, not a marker the circuit creates; no deterministic
  cross-shot marker exists under `init_qubits`. The retained run's head segment reaches pooled z 24.7 against the
  threshold 3, so the case states plainly that a run whose sub-millisecond frequency noise falls about eight-fold
  below the retained level fails the sentinels and withholds every qubit.

## What the run can detect

The departure test's sensitivity is set by the per-qubit gate-model systematic (about 0.016 to 0.019), which
`pooled_z` adds as a shared term, so it does not shrink with the qubit count. The eight-qubit planning record
([minimum-detectable-measured-floor.json](../evidence/measurement_sequence/minimum-detectable-measured-floor.json))
gives a minimum detectable pooled departure of -0.052 in N = 16 P0, a per-step loss near 0.0047. The q, shape and
carryover terms this design bounds sit an order of magnitude below that. The expected outcome is `consistent` unless
the measurement-induced loss exceeds about 0.005 per step; the case recomputes the limit at the selected width and
states it as what the run measures.

## Cost, size and approval scope

The equilibrium row costs about 8192 x (400 + 20 + 9) us = 3.5 s, the twelve readers about 3.3 s and the eight
sentinel rows added in the middle and tail thirds about 3 to 4 s, so attempt 1 at width 32 expects about 49 s against
the retained run's 38 s bill; the planner prices the 109-PUB job at 39.88 s against its 31.18 s for the retained
88 PUBs. The dry run's planner sets the ceilings (on the retained dry run: attempt 1 57 s,
fallback 90 s, 147 s for both) and the case quotes the expected charge against attempt 1's ceiling. Storing each
PUB's placed calibration once removes 22.1 MB of the retained run's 42.4 MB `collect.json`, so the 21 added rows fit
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

Falsifiers: q_hat below its per-qubit tolerance on most qubits (the departure verdict is withheld and q = 1 is
wrong); a pooled settle z
beyond 3; fewer than 8 selected qubits; either order condition failing; a carryover, q or plateau-retained arm's
conditional or unconditional zero-fire bound at or above 0.01; a gamma arm's informative-device rate below 80 %; a
plateau-low arm whose departure verdict is not withheld; a sparse settle arm with a departure false-fire bound at or
above 0.01.

## Superseded designs

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
