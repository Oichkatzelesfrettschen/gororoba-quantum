# Ascella postselected CZ: compilation ensemble with interleaved anchors

Status: built, not sent. [`scripts/ascella_cz_ensemble_case.py`](../../scripts/ascella_cz_ensemble_case.py) freezes
both requests, the platform read, the shot estimate, the plan reads and the forecast under
`results/quandela/cases/ascella_cz_ensemble/` (section "The built case"). Each job waits for the owner's approval of the
written case.

## What the experiment asks

The [process tomography case](ascella-cz-process-tomography-case.md) asked how well qpu:ascella performs a
controlled-Z gate between two photonic qubits and returned an exploratory score of 0.849 (claim
`qd-ascella-postselected-cz-process-fidelity`). The score stays exploratory for three reasons, and this design
measures each one.

| Open question | Why the tomography case leaves it open | What this design measures |
|---|---|---|
| Does the gate depend on which compiled mesh serves it, and by how much? | Each of the 144 settings ran once, on its own mesh, so mesh-to-mesh differences and setting-to-setting differences are one quantity. | Each setting runs under 10 compilation seeds; a homogeneity test across seeds detects mesh variance. |
| Did the device hold still between the two jobs and inside each job? | No setting appears in both jobs. | Four anchor settings repeat at five positions in each job on byte-identical meshes. |
| How does the chance of an eligible event vary between settings? | The fit divides by `nb_shots_used` and assumes one chance of a shot per attempt. | Each setting's eligible events per shot; the rate-weighted score below needs no equality between them. |

## Why one mesh cannot carry the whole measurement

A common mesh for all settings does not exist on this service, by two measured facts in
[strategy.md](../notes/quandela/strategy.md) section 7 ("Per-seed mesh variance of a share"):

- The service compiles every iteration again. The compiled mesh is a function of the iteration's circuit
  parameters and its `compilation_seed`, so two settings with different preparation or readout rotations always
  receive different meshes.
- The same parameters under the same seed return the same `computed_circuit` byte for byte, inside a job and across
  jobs minutes apart, while distinct seeds of one circuit return distinct meshes whose observables differ far beyond
  binomial error.

The second fact gives the two tools of this design. Replicate seeds of one setting sample the ensemble of meshes that
can serve it, which is rule 1 of that section ("run replicate seeds of the identical circuit in the same job, and
pool their spread"). A repeat of one setting under one seed returns the identical mesh, so any change in its counts
is drift or shot noise, which is rule 2 ("keep repeats of one seed as the drift reference").

## Observable: two complementary truth tables

Full tomography under ten seeds would need 1440 iterations. The design measures the gate through two truth tables
instead (H. F. Hofmann, "Complementary Classical Fidelities as an Efficient Criterion for the Evaluation of
Experimentally Realized Quantum Operations", Physical Review Letters 94, 160504 (2005),
[doi:10.1103/PhysRevLett.94.160504](https://doi.org/10.1103/PhysRevLett.94.160504)).

- **ZX table.** Control in the Z basis, target in the X basis. The ideal CZ maps |0,+> to |0,+>, |0,-> to |0,->,
  |1,+> to |1,-> and |1,-> to |1,+>. Four inputs, each read in the ZX basis.
- **XZ table.** Control in the X basis, target in the Z basis, the same four maps with the roles exchanged. Four
  inputs, each read in the XZ basis.

Each of the eight settings is one 6 x 6 unitary on chip modes 0 to 5, built as in the tomography case (readout
rotations after the CZ after the preparations), with the photons on chip modes 0 and 2 and the same eligibility rule:
exactly two threshold clicks, one on each rail pair.

For one setting, the eligible rate is its eligible events divided by its iterations' summed `nb_shots_used`, and the
correct rate is the same quotient for the eligible events on the ideal output. Two scores follow for each table:

- **Rate-weighted score** F_ZX, F_XZ: the sum of the four correct rates over the sum of the four eligible rates. The
  four inputs of a table form an orthonormal basis, so for one trace-non-increasing CP map the sum of their success
  probabilities is the trace of the map's Choi matrix, the same normalization for both tables. Hofmann's bound

      F_ZX + F_XZ - 1 <= F <= min(F_ZX, F_XZ)

  then holds for the trace-normalized process fidelity F of that map whatever its success depends on. Checked
  numerically: no violation over 20 000 and, independently, 200 000 random trace-non-increasing CP maps, and on both
  counterexamples below. Hofmann proves the bound for one map's raw output probabilities (Eqs. (15) and (16)); the normalization to
  the trace-normalized fidelity of a postselected map is this design's linearity argument, which the paper does not
  contain ([source note](../notes/papers/quant-ph-0409083.md), "Relation to the ascella CZ ensemble case").
- **Per-input score** F'_ZX, F'_XZ: the mean over the four inputs of each setting's correct over eligible events. It
  equals the rate-weighted score when success is equal within a table and violates the bound otherwise. The Kraus
  operator (CZ / 3) diag(1, 0.1, 0.1, 0.1) gives F' = 0.7995 on both tables, a claimed lower bound of 0.599 above its
  process fidelity 0.410, while its rate-weighted scores give the interval [0.214, 0.607] around 0.410. The case
  reports F' as a descriptive companion only.

The case's result is the two rate-weighted scores. Hofmann's interval on them rests on two hypotheses that this design
cannot test, so the case reports it beside the scores as a statement conditional on both, and no reading of the case
rests on it:

- **One process for every setting.** Each setting compiles its own mesh, so the ZX and XZ settings can be served by
  different processes. A device that serves CZ·Z_control to every ZX setting and CZ·Z_target to every XZ setting
  scores 1 on both tables and stays stable at every anchor, while both processes and their mixture have process
  fidelity 0 to CZ. The decoded mesh shows only the compiler's nominal law, which that example passes, and
  strategy.md section 7 records observables that differ between seeds of one circuit at 50 to 80 times the
  binomial variance, so individual meshes do differ physically; whether their mean process is the same across
  settings stays open.
- **One chance of a shot per attempt.** The eligible rate divides by `nb_shots_used`, a detection of at least one
  photon; a setting whose chance of any click differs rescales its rates. The tomography fit rests on the same
  hypothesis, so the comparison of estimate 5 below sets quantities of one kind side by side.

## Schedule

Two jobs of 60 template iterations each, about 180 s at the measured 3.0 s per iteration on qpu:ascella
([quandela-credit-optimization.md](../runbooks/quandela-credit-optimization.md), "What bounds packing"), inside the
300 s `max_duration`; both retained 72-iteration tomography jobs took 221 s, which scales to 184 s for 60.

| Block | Per job | Content |
|---|---|---|
| Ensemble | 40 iterations | the 8 settings, each under 5 compilation seeds; job-01 uses 5 further seeds, so each setting has 10 |
| Anchors | 20 iterations | 4 anchor settings (|0,+> and |1,-> of the ZX table, |+,0> and |-,1> of the XZ table), each under one fixed seed, repeated at 5 positions |

- The anchors use the same four seeds in both jobs, so all ten repeats of an anchor request one mesh.
- The five anchor positions divide a job into four equal ensemble segments; the anchor block sits at iterations
  0 to 3, 14 to 17, 28 to 31, 42 to 45 and 56 to 59.
- Inside each segment the ensemble order is a draw from the case's ANU QRNG record, balanced so every setting
  appears in every pair of adjacent segments.
- All 84 compilation seeds (80 ensemble, 4 anchor) and the order draw come from one ANU QRNG draw that the case owns
  whole in the seed ledger.
- Each iteration takes 4000 samples, as in the tomography case; the builder sets `max_shots` from Perceval's
  estimate with the same 1.25 margin. Each job is billed 1 credit plus one millionth of a credit per billed shot, and an
  iterated job bills at most its largest iteration's `max_shots` (`qd_platform.job_billing`), so a job of 60
  iterations of 150 000 to 250 000 shots each is billed like one iteration. The
  tomography's `qd_platform.py plan` ceilings were 1.4 and 2.6 credits; the 2.6 came from the 1 600 000-shot cap
  that its setting in-10-ZZ required (estimate 1 201 113 shots), which this design does not run. Its settings that
  match this design's inputs were estimated at 133 457 to 240 223 shots, which the 1.25 margin and the 100 000-shot
  quantum round to 400 000, about 1.4 credits per job. The case states a ceiling of 6 credits for both jobs, and the
  plan re-reads the price and prints each job's ceiling from the frozen `max_shots`.

## Preregistered analysis

Preconditions, each a refusal when it fails:

- Each run's `cases.json` matches the retained manifest digest, its `job_id` matches its submission, and its raw
  result matches `result_sha256`.
- Every iteration echoes its `compilation_seed` and `circuit_params`.
- Every one of the 120 iterations returns counts, and each carries at least 200 eligible events; an iteration
  short of either makes the case undecided rather than leaving the analysis, since its eligible count depends on the
  mesh under study. The retained tomography settings carried 423 to 3873 eligible events each.

Estimates, the anchor iterations entering estimate 1 alone:

1. **Drift and job effect.** For each anchor, three Monte Carlo homogeneity tests of its outcome tables, each with
   100 000 tables drawn uniformly over the arrangements with the observed row and column totals (sequential
   hypergeometric draws, the exact conditional null): positions inside job-00,
   positions inside job-01, and job-00 against job-01. A fourth test per anchor compares its eligible rate between
   the jobs (the conditional binomial comparison of per-shot rates, the Poisson-rate form; because each iteration
   stops at its samples and its shots are random, its variance ratio is 1 - p_eligible / p_any_click, about 0.996 at
   the forecast, so it is slightly conservative rather than exact). The two jobs pool only when all 16 tests pass at
   the 0.01 level after a Bonferroni factor of 16. When an anchor returns more than one `computed_circuit` digest,
   different digests in the two jobs, or a missing or empty one, a recalibration or a missing identity leaves the jobs unpooled, and
   they are reported separately.
2. **Mesh variance.** For each ensemble setting, a Monte Carlo multinomial homogeneity test of its ten seed outcome
   tables as in estimate 1, at the 0.01 level after a Bonferroni factor of 8; when estimate 1 leaves the jobs
   unpooled, each job's five seed tables are tested instead, with a factor of 16, so a shift between the jobs never
   reads as mesh variance. The excess of the between-seed variance of its correct fraction over the binomial variance
   is reported beside it as a magnitude, and seeds that return one `computed_circuit` count as one mesh in the
   reported mesh count.
3. **Scores.** The seed index s of a setting is the position of its seed in the case's pre-data draw order, 1 to 5
   in job-00 and 6 to 10 in job-01. For each s, the rate-weighted scores F_ZX(s) and F_XZ(s) of the four settings at
   that index; a pooled interval follows estimate 1. Each
   table's score is the mean over s with a Student-t interval on 9 degrees of freedom, which carries mesh variance and
   shot noise together. The per-input scores F' are reported with the same construction. The index s pairs the four
   settings of a table arbitrarily: each setting's replicates sit in segments drawn by their own order keys, so over
   the draw of schedules drift in time between values of s enters as variance the interval carries, not as a bias.
   The frozen schedule is one draw and leaves some values of s uneven in time (section "Limits").
4. **Bound.** L is the one-sided 97.5 % lower limit of the mean over s of F_ZX(s) + F_XZ(s) - 1, and U is the
   smaller of the one-sided 98.75 % upper limits of F_ZX and F_XZ, so [L, U] covers the bound at a joint level of at
   least 95 % by Bonferroni. The case reports [L, U] as the conditional statement above, never as the result.
5. **Comparison with the tomography.** The build recomputes the retained unprojected tomography fit from the two
   retained runs and predicts from it the eligible and correct rates of the eight ensemble settings, hence its own
   rate-weighted scores F_ZX^tomo and F_XZ^tomo. A parametric bootstrap of the two tomography runs (500 replicates,
   the resampling of the tomography's own interval) gives each prediction a standard deviation; it carries the shot
   noise of the 144 tomography tables only, and leaves out the spread among the tomography's own meshes on purpose,
   since that spread is what this comparison exists to expose. Each ensemble score
   is compared with its prediction by the difference and an interval at estimate 3's Student-t quantile on the
   combined standard error of the two; the predicted rates are linear images of the unprojected fit and can be
   negative, and the 0.849 process fidelity of the fit, a non-positive Choi matrix, enters no comparison.

Readings fixed before the data:

| Outcome | Reading |
|---|---|
| Both difference intervals of estimate 5 contain 0 | The single-compilation tomography fit predicts the ensemble's truth tables; mesh selection did not bias it on these settings. |
| A difference interval lies above 0 | The ensemble reads that table better than the tomography fit predicts: the 144-mesh fit understated it. |
| A difference interval lies below 0 | The tomography fit overstated that table, by mesh selection or by its estimator. |
| A mesh-variance test rejects for at least one setting | The tomography interval, which covers shot noise only, is too narrow for the mesh ensemble, whatever the bound reads. |
| A drift or job-effect test fails, or the anchor digests differ between jobs | The jobs are reported separately and no pooled bound is claimed. |
| The plan's HOM differs from the tomography's 87.56 % by more than one point | Estimate 5 states the HOM difference beside each comparison; hypothesis: under a partial-distinguishability model of the Ralph CZ the process fidelity moves about 0.013 per point of HOM. |

## What the retained tomography runs already show

`scripts/ascella_cz_served_mesh.py` decodes the `computed_circuit` of all 144 retained iterations and retains
[ascella-cz-served-mesh.json](../../results/quandela/ascella-cz-served-mesh.json); its `--check` runs in
`tests/test_cli_record_checks.py`, and `tests/scripts/test_ascella_cz_served_mesh.py` holds the decoder against
Perceval's deserializer on all 144 meshes.

- **The transpiler serves the designed law.** Over the 144 meshes the served and designed eligible-outcome
  distributions differ by a total variation distance of at most 7.6e-4 (median 1.7e-4), and the served eligible
  probability lies within 0.9990 to 1.0015 of the designed one; the law of distinguishable photons agrees as closely.
  Compilation error therefore explains neither the non-positive Choi matrix of the tomography fit nor its distance
  from the ideal gate; that distance is physical (source, loss, phase error), and the seed count stays at ten, since
  the ensemble measures physical mesh variance.
- **The chance of an eligible event varies between inputs.** Eligible events per shot range from 0.79 to 1.31 times
  their mean over the 144 settings, against a binomial spread of about 4 % at the 423 to 3873 eligible events per
  setting. The single settings that match this design's inputs read 0.829 (in-0+-ZX), 1.147 (in-1+-ZX), 0.955
  (in-+0-XZ) and 0.886 (in-+1-XZ); the minus-basis inputs have no retained analog. A per-rail transmission model,
  in which the rate factorizes into a control and a target rail factor, fails: it requires the ratios |1,0>/|0,0> and
  |1,1>/|0,1> of the input means to agree, and they read 1.357 and 1.009. hypothesis: the variation follows partial
  photon distinguishability in the Ralph CZ, whose success depends on the input; mixing the indistinguishable and
  distinguishable two-photon laws of the designed unitaries with weight V fits the 16 input means at V = 0.922
  (correlation 0.953, rms residual 0.026). The rate-weighted score makes this variation harmless to the bound, and
  the per-input score F' violates the bound under it.

## Limits

- The bound holds for one process and one chance of a shot per attempt; the design tests neither, and a reported
  [L, U] says so.
- The served-mesh check covers the compiler's nominal law only. Physical phase error, loss and source imperfection
  do not appear in a decoded mesh.
- Ten seeds sample the mesh ensemble thinly; the Student-t interval states that honestly and a wide interval is a
  valid outcome. Its coverage rests on near-normal seed scores; a skewed or bimodal mesh distribution can undercover,
  and the forecast's false-alarm study covers estimates 1 and 2 only, not the intervals of estimates 3 to 5.
- The truth tables bound the process fidelity and give no Choi matrix. A full reconstruction under an ensemble needs
  the 1440 iterations this design declines.
- The anchors test drift over about 180 s and across one gap between jobs, the time scales of this case only.
- Each setting's seed tables sit at different positions in the frozen schedule, so drift below the power of
  estimate 1's tests inflates estimate 2's between-seed spread as if it were mesh variance. A rejection of estimate 2
  is therefore attributed to the mesh only when estimate 1's drift family passes, and a pass bounds drift only to the
  power of those tests.
- hypothesis: preparation and readout rotations contribute comparable mesh error to the gate itself; each compiled
  mesh carries all three, and no setting of this design separates them.

## Before a submission

1. The no-hardware served-mesh calculation is retained (section "What the retained tomography runs already show").
2. Build the case script with `--build`, `--check`, `--forecast` and `--analyze`, its tests, and the frozen
   requests; draw the seeds; forecast both scores of both tables under Perceval's noise model at the live HOM and
   g2, and simulate the false-alarm rate of estimates 1 and 2 at that forecast.
3. Register Hofmann 2005 as a retrieval receipt in the source registry.
4. Review the built case adversarially, then ask the owner for approval of the two jobs.

## The built case

`scripts/ascella_cz_ensemble_case.py --check` rebuilds both requests byte for byte, binds every iteration through
`qd_platform.template_experiment`, and holds the schedule above: the anchors at iterations 0-3, 14-17, 28-31, 42-45
and 56-59 under one seed each, the same four in both jobs, and every ensemble setting once in every segment plus one
replicate in a second segment, so each appears in every pair of adjacent segments. `--forecast` recomputes
`forecast.json` within 1e-12 (gate `core-ascella-cz-ensemble-forecast`); `--check` runs in gate
`core-record-check-07`. The shared readout, eligibility rule and noise model are those of
[`ascella_cz_tomography_case.py`](../../scripts/ascella_cz_tomography_case.py); the iterated-job charge is stated by
`billing_rule_v2.RULE`.

- **Seeds and order.** One ANU QRNG draw,
  [draw-2026-11-07T164259Z.json](../evidence/anu_qrng/draw-2026-11-07T164259Z.json) (320 uint16 values, no zero and
  no repeat), seeds everything in index order: indices 0 to 3 the anchors, 4 to 83 the ensemble (ten per setting in
  table order, seed index s = 1 to 10, s <= 5 in job-00), 84 the analysis Monte Carlo stream, 85 the forecast's
  false-alarm study, 86 to 261 the order keys (88 per job), 262 the bootstrap of the tomography prediction, 263 the
  random-map check of the bound and 264 the test fixtures; indices 265 to 319 are owned and unused. The manifests
  name the draw without an index, so the case owns it whole.
- **Platform read** (2026-11-07, read-only): HOM 88.88 %, g2 2.0 %, transmittance 5.57 %, clock 13.33 MHz. The
  photon inputs sit on chip modes 0 and 2, both connected sources; the window stays at chip modes 0 to 5 for
  comparison with the tomography fit, although the read's darkest connected window starts at mode 2 (623 against 681
  dark counts per second, about 4e-6 dark clicks per attempt).
- **Shots.** Perceval's estimate for 4000 samples reaches 251 328 shots at most (`shot-estimate.json`); times 1.25,
  rounded up to the 100 000-shot quantum, each iteration's `max_shots` is 400 000, so each job's credit ceiling is
  1.4 and both jobs' 2.8, inside the 6-credit ceiling of this design.
- **Plan reads** (`plan-read.json`, `ascella_cz_ensemble_case.py --preflight JOB`, read-only): each retains the
  fresh plan of its job without the body and the submission policy's verdict under `admission`. The reads of
  2026-11-08 give a ceiling of 1.4 credits and 11 793 960 estimated shots per job, and HOM 88.64 %, which the policy
  refuses; the modeled job takes 188 s expected and 197 s with every iteration at its cap. `--check` holds each
  plan's request fields (case, circuit digest, budgets, ceiling) to the request and prints its verdict; the live
  fields are a read.
- **Submission policy** (`submission_policy` in each `cases.json`, enforced by `--submit` as the verify step of
  `qd_platform.submit`, which refuses a manifest naming a `submit_wrapper` without one): HOM strictly above 90 %
  (strategy.md design rule 1) and within one point of the reference tomography's HOM, so estimate 5 compares the
  ensemble with a fit taken at the same source quality; Explorer row and processor `available`, or `running` while
  the token counts no running and no queued job; the plan's ceiling, per-job price and expected seconds equal to the
  case's; and for job-01 a collected job-00 run that completed with 60 bound iterations, none uncounted, each with at
  least 200 eligible events (`--after RUN`). `--submit` also requires the retained preflight to be admitted and the
  fresh plan to equal it in case digest and in body digest without `process_id`, so the request sent is the one the
  owner reviewed. Against the reference of 87.56 % the HOM band is empty, so neither job
  submits until a fresh tomography reference taken above 90 % replaces it; the owner set both rules on 2026-11-08.
- **Forecast** under Perceval's NoiseModel at the read, with loss and dark counts: F_ZX = F_XZ = 0.8635, F' = 0.8766,
  Hofmann interval [0.727, 0.864]; indistinguishability alone gives 0.900. The thinnest settings expect 447 eligible
  events per iteration, above the floor of 200.
- **Tomography prediction** (estimate 5): the unprojected fit recomputed from the two retained runs reproduces the
  retained process fidelity 0.849328 within 1e-12 and predicts F_ZX = 0.888 and F_XZ = 0.882, above the noise
  forecast; over 500 bootstrap replicates of the tomography runs each prediction has a standard deviation of 0.012
  (95 % percentile intervals [0.866, 0.911] and [0.859, 0.908]), comparable to the ensemble's expected interval.
  The prediction is solved in arb ball arithmetic at 128 bits, and each retained float64 is the certified correct
  rounding of its enclosure, so its bytes do not depend on the BLAS or its thread count; the record carries the
  digests of its float64 inputs ([least-squares precision](../evidence/least-squares-precision/README.md)).
- **False alarms.** Over 1000 synthetic datasets at the forecast law, with each iteration stopping at its samples and
  its shots drawn as the samples plus a negative binomial count, the drift family rejects in 0.007 of datasets (95 %
  Clopper-Pearson interval [0.003, 0.014]) and the mesh-variance family in 0.007 ([0.003, 0.014]), at the 0.01 level;
  `--check` requires each interval to reach down to 0.01 and stay below 0.02. Seven datasets unpooled and took the
  per-job mesh test. With the Monte Carlo tables drawn exactly conditional on both margins, the mesh tests'
  unadjusted per-test rate reads 0.0108 against 0.01, and the sixteen drift tests read 0.003 to 0.017.
- **Bound check.** 20 000 random trace-non-increasing maps (`forecast.json` `bound_check`), half Ginibre maps and half
  CZ times a random input filter plus a weak random term, show no violation of the normalized bound; the least
  margins are 2.2e-5 below F and 1.4e-5 above it.
- **Binding.** The two retained tomography runs echo `circuit_params` equal to their manifests in all 144 iterations,
  the property the binding rule requires.
- **HOM reading.** Both tomography jobs were submitted at 87.56 %. The platform read behind the forecast gave
  88.88 %, and the plan reads of 2026-11-08 read 88.64 %, 1.08 points above it and outside the one-point threshold; the
  analysis states each submission plan's difference and sets `hom_moved` beyond one point (`hom` of the analysis
  record). Under the design's hypothesis of about 0.013 process fidelity per point of HOM, a submission at 90 %
  would shift estimate 5 by about 0.03, about 2.5 times the prediction's standard deviation; the submission policy
  therefore admits no HOM more than one point from the reference.
