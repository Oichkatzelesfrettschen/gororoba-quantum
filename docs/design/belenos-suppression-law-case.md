# Belenos three-photon suppression-law case

This is the written case for two qpu:belenos jobs that test three-photon indistinguishability through a Fourier
suppression law. The test asks whether multi-photon interference on the chip suppresses the outputs that the
zero-transmission law of Tichy et al. ([source 33](../notes/quandela/literature.md#33-tichy-et-al-zero-transmission-law-for-multiport-beam-splitters),
generalized by Dittel et al., [source 35](../notes/quandela/literature.md#35-dittel-et-al-totally-destructive-many-particle-interference))
forbids for genuine indistinguishable photons, at the level a Perceval source model with the live HOM visibility and g2
predicts, and where a distinguishable-particle model and the random-phase mean-field model of Tichy et al.
([source 34](../notes/quandela/literature.md#34-tichy-et-al-stringent-assessment-of-boson-sampling-devices)) predict
none. The test is standalone. It bounds nothing for the teleportation rehearsal, whose lack of a classical bound comes
from service-contract facts that this case leaves untouched.

[scripts/belenos_suppression_case.py](../../scripts/belenos_suppression_case.py) builds the frozen request in
[results/quandela/cases/belenos_suppression_law](../../results/quandela/cases/belenos_suppression_law/), checks it
and analyzes the collected runs. [tests/scripts/test_belenos_suppression_case.py](../../tests/scripts/test_belenos_suppression_case.py)
rebuilds it and asserts the exact suppressed set. Nothing has been sent to a provider: the case rests on local
Perceval simulation, one ANU QRNG draw and read-only platform reads (`qd_platform.py snapshot` and `plan`).

## Interferometer and suppressed set

Three photons enter a six-mode window of the 24-mode chip. The window programs the six-mode Fourier matrix
F[j, k] = exp(2 pi i j k / 6) / sqrt6. The probability of the collision-free output set O for identical photons on
input ports P is |perm F[O, P]|^2.

- **Periodic setting.** Ports P = {0, 2, 4}, a cyclic input of period m/n = 2. Exactly 12 of the 20 collision-free
  outputs have a zero permanent; the other 8 each carry probability 1/24. The zero set is the set of outputs whose
  mode labels (0 to 5) do not sum to a multiple of three. The permanents establish the set; the label-sum rule
  agrees with them numerically. The case attributes no statement of the periodic m/n form to Tichy et al., whose
  abstract (the only part read) treats n photons on n ports. The case computes both independently, and the test
  requires them to agree on this set: 013, 014, 023, 025, 034, 035, 124, 125, 134, 145, 245, 235.
- **Control setting.** Ports {0, 1, 2}. Every one of the 20 collision-free outputs has a nonzero permanent (the
  smallest probability is 0.0046), so the suppressed set is empty.
- **Shared law of distinguishable photons.** Every entry of F has modulus 1/sqrt6, so distinguishable photons leave
  each collision-free output with probability 6/216 in both settings. Detector inhomogeneity therefore moves the
  periodic and control fractions of a distinguishable source together.

Smaller choices fail. For every input triple, the Fourier matrices of 3, 4 and 5 modes have no collision-free output
with a zero permanent (three modes have one collision-free output and it is allowed), and the test enumerates them. Six
modes is the smallest Fourier size with a suppressed collision-free output. Nine modes (54 of 84 outputs) and twelve
modes (144 of 220) raise the suppressed share from 0.60 to 0.64 and 0.65 only, for a larger mesh. The n = 2 and
Sylvester variants are not needed because n = 3 works.

### Threshold detectors

Belenos detectors are threshold detectors, so a bunched pair merges into one click. The analysis keeps only events with
three clicks on three distinct window modes. The SLOS backend of Perceval on the compiled 24-mode unitary of each
setting (run by `--check`) establishes the facts the analysis rests on:

- all probability stays inside the window (outside mass below 1e-9);
- the probability of each collision-free output equals its permanent to 1e-9, and each of the 12 suppressed outputs
  has probability below 1e-12 in the periodic setting;
- collision-free outputs carry exactly 1/3 of the probability in both settings, so 2/3 of three-photon events bunch
  and fall outside the analysis, which costs yield and no bias, since the retained and the suppressed sets are both
  collision-free.

Photon loss and g2 add non-collision-free emissions that still yield three clicks on distinct modes. The forecasts
below include them through the click model; they are why the indistinguishable forecast is 0.21 and not zero.

## Request

`job-00` `cases.json` sha256 `5920ca4126b26f1384804e529dc5bb568d4c184e6681b2c51c10022b5ea68a18`, `job-01`
`cases.json` sha256 `a3cfbf0288091a9af63d59ace955a328a09cc925458f6a4474ddee8f743c683b`; both `circuit.json` files have
sha256 `68946fe4bcbd44c7b6887d1d4c465cff5d30a786e11dd9c1234328c53d13f1d0`.

**Layout.** `choose_window` reads the case's platform read
([platform-read/catalogue.json](../../results/quandela/cases/belenos_suppression_law/platform-read/catalogue.json),
retrieved 2026-10-31T03:39:42Z, sha256 `795503e1...ad1a`). A window of six consecutive chip modes qualifies when it holds
three connected input modes, every window mode has at most 100 dark counts per second and the ratio of the largest to
the smallest t_out is at most 2. The score is the product of the three source t_in values times the modeled
three-click probability per pulse. The winner is the window of chip modes 16 to 21 with the photons on connected modes
16, 18 and 20 (window slots 0, 2, 4):

| Quantity | Value |
|---|---|
| Source t_in (modes 16, 18, 20) | 3.53 %, 3.19 %, 3.01 % |
| t_out of modes 16 to 21 | 113.3, 153.3, 148.1, 144.0, 151.8, 178.2 (ratio 1.57) |
| Detection probability per mode (Transmittance 5.37 % times t_out over the largest t_out) | 0.0341, 0.0462, 0.0446, 0.0434, 0.0457, 0.0537 |
| Dark counts, modes 16 to 21 | 0.2, 0.3, 0.1, 12.5, 0.2, 0.2 per second |

Dark clicks complete a three-click event only from a two-click real event: that probability is about 5.5e-3 per pulse
times the window's 2.7e-6 dark clicks per pulse, below 5e-4 of the 3.35e-5 accepted events per pulse, so the models
leave dark counts out. The window of modes 0 to 5 passes the balance limit and scores lower, the window of modes 6 to 11 exceeds the
balance limit, and the region of modes 16 to 23 also carried the teleportation rehearsal.

**Circuit.** Both jobs bind the same 81-parameter triangular Rx/phase template (`photonic_template`) on modes 16 to
21, the identity elsewhere, with the input state on modes 16, 18 and 20. The photons sit on the same three chip modes in
every iteration of both settings. The control permutes the columns of the programmed matrix (Fourier ports 0, 1, 2 take
the source slots), which keeps t_in, the source modes and the detectors fixed. A phase scramble at the inputs or
outputs alone would not serve as a control: it multiplies each permanent by a unit phase and leaves the suppressed set
unchanged.

**Jobs and order.** Four template iterations per job, 400 samples each:
- `job-00`: periodic, control, control, periodic (ABBA);
- `job-01`: control, periodic, periodic, control (the arm-swapped block).

Each setting is listed below by compilation seed; the server draws its compilation randomness from it, so the four
periodic iterations compile four different meshes. `min_detected_photons` is 3, mitigations are the empty list,
`max_duration` is 300 s and the job returns all 24 modes.

**Compilation seeds.** Values 0 to 7, in index order and each used once, of the ANU QRNG draw
`docs/evidence/anu_qrng/draw-2026-10-31T034820Z.json` (uint16, retrieved 2026-10-31T03:48:20Z), registered in
`docs/evidence/qrng_seeds/allocations.json`: 63889, 65328, 18934, 51115 (job-00 iterations in submission order) and
51480, 31486, 50307, 51095 (job-01).

**Eligibility.** A sample is accepted when exactly three modes click, all inside modes 16 to 21, one count per mode.
Samples with a click outside the window, a count above one in a mode, more than three clicks or fewer than three
in-window clicks are tallied by cause and excluded.

## Models and forecast

The statistic is the suppressed fraction s, the share of accepted events that lie in the 12-output suppressed set of the
periodic setting; both arms are scored against that set. Each model passes its photon-number distribution through the
per-mode threshold-click model of `detected_clicks` with the detection probabilities above.

- **Indistinguishable.** Perceval `NoiseModel(indistinguishability = HOM, g2)` on the window unitary. The model reads
  the HOM visibility as the photon indistinguishability, which is the repository convention (`photon_distribution` in
  the teleportation rehearsal); for three photons the mapping from two-photon visibility to the three-photon overlap
  is the source model's, and the case tests it.
- **Distinguishable.** The same source with indistinguishability 0 and the same g2.
- **Mean-field.** The random-phase sampler of Tichy et al.: for an emission pattern with n_j photons on input slot j,
  each photon independently occupies output k with probability |sum_j F[k, j] sqrt(n_j) e^{i phi_j}|^2 / N, averaged
  over the phases. The emission patterns come from the g2 source with no interference. The average runs exactly on a
  7-point uniform grid per free phase (the integrand has degree at most 6 in each phase), and the test compares it with
  a 10-point grid.

Forecast at the platform read (HOM 87.9 %, g2 1.4 %, Transmittance 5.37 %), retained in
[noise-model.json](../../results/quandela/cases/belenos_suppression_law/noise-model.json):

| Model | s, periodic setting | s, control setting | Three-click probability per pulse (periodic) |
|---|---|---|---|
| Ideal indistinguishable (no loss, g2 = 0) | 0 | 0.667 | |
| Indistinguishable at HOM and g2 | 0.208 | 0.644 | 3.35e-5 |
| Distinguishable | 0.602 | 0.602 | 5.18e-5 |
| Mean-field | 0.727 | 0.588 | 3.35e-5 |

The indistinguishable periodic forecast moves with g2 (0.188 at half g2, 0.246 at double) and with HOM:
0.38, 0.34, 0.29, 0.24, 0.18, 0.12 and 0.06 at HOM 0.70, 0.75, 0.80, 0.85, 0.90, 0.95 and 1.00. At g2 1.4 % and HOM 1.00
the fraction is still 0.058, so the g2 tail alone leaks 0.058. The slope is about -1.2 per unit HOM. Three effects move
s by the same order and are not separable in this case: the HOM visibility, the g2 tail (about +-0.03) and compilation
error. Compilation error is a one-sided bias, because the ideal fraction is 0 and a perturbed Fourier matrix can only
add weight to the suppressed set; an independent review's Monte Carlo perturbation of the unitary by exp(i eps H) with random Hermitian H
(not retained or reproduced here) raised the mean s from 0.001 to 0.114 as the single-photon column error grew from 0.010 to 0.102 (total variation
distance), with a spread of about half the shift. An observed s above the forecast therefore does not show partial
distinguishability. The paired contrast s(control) - s(periodic) is +0.436 for indistinguishable photons, exactly 0 for
distinguishable photons at any detection efficiencies and g2, and -0.138 for the mean-field sampler.

## Decision rule

The decision uses the per-iteration fractions of each arm, pooled over both jobs (four periodic and four control
iterations), so every compilation seed counts once and the interval carries the variation between compiled meshes. The
interval is one-sided Student t with alpha = 0.01 and 3 degrees of freedom. The forecasts are recomputed at the
`perfs_at_plan` of each job's submission record, and the arm forecast is their mean. An iteration counts only with at
least 200 accepted events (half of its 400 samples); a smaller one is reported apart and does not count.

- **Suppression observed.** Two rules, both required:
  - the upper 99 % bound of s_periodic lies at least 0.10 below the smaller of the distinguishable and mean-field
    forecasts (about 0.50 at the read above);
  - the lower 99 % bound of the paired contrast s_control - s_periodic is at least 0.10. The contrast is exactly 0
    for distinguishable photons whatever the detection efficiencies, so this rule rejects the distinguishable and the
    mean-field alternatives without the t_out detection model. Its forecast under the indistinguishable model is
    +0.436 and its expected lower bound is about 0.37.

  If either fails, the verdict is no suppression beyond the distinguishable and mean-field forecasts.
- **Null arm and instrument check.** The control setting has an empty suppressed set. Its fraction must lie within 0.10
  of the indistinguishable control forecast (0.644); all three models lie within 0.06 of each other there. A
  departure means the detectors or the selection deplete or inflate the suppressed set, and the verdict is invalid
  control whatever the periodic arm shows.
- **Level.** The periodic mean lies within max(0.05, 3 se) of the indistinguishable forecast: suppression at the
  predicted level. Below it is suppression stronger than predicted. Above it is suppression weaker than predicted,
  and the case cannot attribute the excess to partial distinguishability: compilation error and the g2 tail raise s
  too. The analysis reports the HOM at which the forecast curve reaches the observed mean as a lower bound on the
  effective HOM (compilation error only raises s), under the Perceval source model and the forecast g2. Each counted
  iteration returns its served mesh in `result_fields.computed_circuit`, which `photonic_compilation_audit._elements`
  decodes; a forecast per served mesh would remove the compilation confound and is a follow-up, not part of this
  rule.
- **Undecided.** Fewer than four counted iterations in either arm, including a cut-short job whose lost iterations
  come back as `missing`, `malformed` or `error` entries; the analysis tallies and skips those.

The analysis binds each result iteration to its setting by `compilation_seed` (unique across the eight settings) and
checks `circuit_params`; an iteration that binds to no setting or to two raises, so a dropped or reordered iteration
leaves every count in its own arm. It reads one run per job name and every compilation seed once, and refuses a second
run of the same job. A repeat of a failed job supersedes the failed run, is never pooled with it, and takes fresh QRNG
compilation seeds.

**Job order.** `job-01` is submitted only after `job-00` is collected with at least 800 accepted events (half of the
1,600 samples). A chip that degrades without a record update then costs one job's credits, not two.

The analysis also reports, without deciding on them, the pooled binomial counts, the chi-square homogeneity of each
arm's iterations, the paired contrast with its standard error against the three model contrasts, the forecast
sensitivity to g2, and the excluded events by cause, per arm and per iteration.

**Falsifiers.** The case predicts s_periodic about 0.21 with a between-iteration standard error near 0.010 (1600
accepted events per arm at the modeled yield, binomial error 0.010). It is wrong about genuine three-photon
indistinguishability if the upper bound of s_periodic exceeds about 0.50 or the lower bound of the paired contrast falls
below 0.10; the distinguishable and mean-field models then describe the chip. The expected upper bound under the
forecast is 0.25, so the sample size leaves the first rule a margin of 0.25. The level rule is a consistency check, not
a falsifier of the Perceval overlap mapping: compilation error and g2 move s by the same order as the HOM mapping.

**What the bound certifies.** One fully distinguishable photon with two identical ones gives s_periodic = 0.75, above the
fully distinguishable 0.60. Pairwise interference alone therefore raises the suppressed fraction, and an upper bound at
or below 0.50 needs a substantial fully indistinguishable three-photon component. The rule certifies genuine
three-photon interference against distinguishable, partially distinguishable and mean-field alternatives.

## Written case

**What it measures.** The suppressed-outcome fraction of collision-free three-click events of the six-mode Fourier
matrix with a cyclic three-photon input, against the same fraction with a non-periodic input on the same chip modes and
detectors. A fraction near 0.2 against 0.6 to 0.7 for the distinguishable and mean-field models shows three-photon
interference at about the visibility the chip reports. The result bounds the effective three-photon
indistinguishability from below only, since compilation error raises s.

**Why local simulation cannot answer it.** Perceval reproduces the models, and the case computes them. The question is
the fraction the chip produces: the physical indistinguishability of three photons from the demultiplexed source, the
compiled phase error of a 24-mode thermo-optic mesh, the loss and the threshold detection. No local computation
contains those, and the forecasts above are the predictions the data tests.

**Backend and jobs.** `qpu:belenos`, two jobs (`job-00`, `job-01`), submitted one after the other because the account
runs one job at a time and queues one; `job-01` waits for the `job-00` yield gate above.

**Iterations and shots.** Four template iterations per job, 400 samples and a 1,500,000-shot cap per iteration (aggregate
1,600 samples and 6,000,000 shots per job). The `qd_platform.py plan` estimate (read-only, retained in
[shot-estimate.json](../../results/quandela/cases/belenos_suppression_law/shot-estimate.json)) is 1,182,561 shots per
iteration and 4,730,244 per job; the cap is the largest estimate times 1.25, rounded up to 50,000.

**Expected seconds.** 180 per job. The model is a fixed part per iteration plus the shots times a per-shot cost,
fitted over retained qpu:belenos runs (the BDSC stationarity and qualification cases fix the 6.6 to 6.9 s fixed part;
the teleportation rehearsal gives 9 to 12.8 microseconds per shot on a healthy chip and about 35 microseconds on a
degraded one). At the 1,500,000-shot cap, an iteration takes 6.9 + 19.2 = 26.1 s and a job 104.4 s; scaled by 1.25 and
rounded up to 60 s this is 180. Acquisition does not stay small: at the 1,182,561-shot estimate it is about 15 s per
iteration. On a degraded chip (35 microseconds per shot) a job takes about 238 s, above 180 and below the 300 s
`max_duration`, which is the worst case measured. The earlier clock model (3.35e-5 events per pulse at 4.94 MHz) is not
used: it predicted 240 s for the teleportation rehearsal's job-01, which was cut at 300 s with 11 of 12 iterations.

**Credits.** Quandela bills each job its full ceiling, 1 credit plus 1e-6 per shot of its largest iteration's
`max_shots`: 2.5 per job and 5.0 for the case. A repeat of one job brings the total to 7.5, under the 8 credits the case
allows. `plan` for both jobs (2026-10-31, status running) returned `credit_ceiling` 2.5 and `estimated_credits` 2.5.

**Commands.** Per job, with the written case's arguments:

```sh
"$PYTHON" scripts/qd_platform.py plan results/quandela/cases/belenos_suppression_law/job-00 \
  --platform qpu:belenos --max-credits 2.5 --expected-seconds 180 --per-job-credits 1 --admit-status running
```

`submit` takes the same arguments plus `--approval` with the owner's quoted approval; `collect` follows each job.
`"$PYTHON" scripts/belenos_suppression_case.py --analyze RUN_00 RUN_01` writes `analysis.json` beside both runs.

**Owner decision: HOM.** `plan` warns that Belenos reads HOM 87.9 %, not above 90 %, and
[strategy.md](../notes/quandela/strategy.md) asks a block of two or more photons to wait until HOM exceeds 90 %. The
case decides at either value because the forecast and its null gap are computed at the HOM of the plan (0.18 at 90 %,
0.21 at 87.9 %), so waiting changes the expected fraction by 0.03 and not the verdict. Nothing is approved. The owner chooses
between running both jobs at the live HOM and waiting for HOM above 90 %, and approves each job from this case.

## Limits

- The click model uses the per-mode detection of the t_out read, the convention of the teleportation rehearsal. The
  t_in values select the sources and enter no forecast. The paired design removes a common detector factor but not a
  setting-dependent one, which the control check bounds.
- The Perceval source model fixes how a two-photon HOM visibility becomes a three-photon distinguishability. The
  analysis reports the HOM lower bound beside the plan's HOM and reaches no conclusion about the source model.
- The server re-transpiles every circuit, so each iteration realizes the Fourier matrix with a compilation phase error
  that the case does not model. The error raises s (one-sided, since the ideal is 0), so it biases the level rule and
  the HOM lower bound and enters the between-iteration spread the interval carries. The primary rules have a margin of
  about 0.25 against it.
- The control is setting-independent only for fully distinguishable or symmetric partial distinguishability. If one
  source's demultiplexed photons differ in overlap from the others, the control forecast shifts (with one photon
  distinguishable, s_control is 0.50 or 0.75 by port), while the periodic forecast stays 0.75. At HOM 0.879 the
  shift is likely inside the 0.10 control tolerance.
- The mean-field definition rests on a machine-generated summary of the ar5iv rendering of Tichy et al. (2014); read the
  paper's section on the sampler before the owner cites the mean-field row. At the figures above the null in force is
  the smaller of the two forecasts, the distinguishable 0.602, so the mean-field definition does not change the primary
  decision.
- Two-thirds of the three-photon events bunch (collisions) and drop out, and four-photon emissions that lose one photon
  enter the accepted set; both are in the forecast yield and fraction.
