# Ascella CZ tomography reference across the HOM band: results of 2026-11-09

The band pair of the Ascella CZ process tomography reference
([design](../../design/ascella-cz-tomography-reference-case.md)) ran on 2026-11-09:

| Job | Job id | Submitted (UTC) | Samples |
|---|---|---|---|
| job-00 | `ffb03f3c-67b9-4624-ab90-e79d7ca58e32` | 17:41:45 | 2,033,400 |
| job-01 | `be82ee27-ad26-4f5f-aa3d-85d547ce2131` | 17:52:21 | 1,938,600 |

- **Plan read:** both jobs ran at one plan read: HOM 88.42 %, g2 2.0 %, transmittance 5.62 %.
- **Pooling:** the pool is decided with scale 1 for both jobs; all 144 settings counted; 613,903 eligible events.
- **Retained records:**
  - the two run directories under `results/quandela/runs/2026-11-09T17*`;
  - the preregistered analysis `results/quandela/ascella-cz-tomography-reference-analysis.json`;
  - the post-data decomposition `docs/evidence/ascella-cz-tomography-band/findings.json`, written by `docs/evidence/ascella-cz-tomography-band/analyze.py` (deterministic, about 75 s);
  - the served-mesh record `results/quandela/ascella-cz-tomography-reference-served-mesh.json` (`scripts/ascella_cz_served_mesh.py --pair reference`);
  - the component model of the mesh and its preregistered hold-out, `docs/evidence/ascella-cz-tomography-band/mesh_model.py` and `mesh-model.json`.

The preregistered analysis decides: process fidelity 0.832 (0.824 to 0.839), average gate fidelity 0.865 (0.859 to
0.871). The model check fails, so by the preregistered rule every other verdict is conditional on that failure. The
sections below justify or qualify each verdict against the decomposition and then state what the decomposition
shows beyond them. Every statistic of the decomposition was chosen after the data arrived; each one generates a
hypothesis and decides no preregistered conjecture.

## The preregistered verdicts, each held against the decomposition

The bootstrap interval of F assumes the acquisition law, which the model check rejects. A sensitivity reading
scales the interval half-width by the square root of the Pearson ratio, sqrt(5.73) = 2.39: F lies in 0.814 to
0.850. That widening is not a sound correction for a systematic inside the model space (the design doc's verdict
section), so it serves only to mark which falsifications depend on the interval width.

| Conjecture | Prediction | Measured | Preregistered verdict | Robustness after the decomposition |
|---|---|---|---|---|
| Overlap-only law at M = V | 0.844 | F 0.824 to 0.839 | falsified | Fragile: misses by 0.005 and survives the widened interval. It omits g2, loss and dark counts, which lower F, so its retained survival was a cancellation |
| g2-corrected overlap law | 0.892 | same | falsified | Robust: outside the widened interval by 0.04 |
| Record noise variant at M = V | 0.795 | same | falsified | Robust: below the widened interval by 0.02 |
| g2-corrected noise variant | 0.838 | same | survives | Survives both intervals. The one model that adds g2 to the overlap (Ollivier et al. 2021, priv 1291df4cd86b, Eq. 2) and keeps loss and dark counts |
| Rail overlap equals the HOM read | 0.884 | record-model M_R 0.946 to 0.959 | falsified | The sign stands; the size does not. M_R depends on the readout set: from ZZ readouts alone D gives 0.956, from all nine 0.939 (retained pair: 0.979 and 0.914). Input 10's rate varies 4.2 % across its readouts, against the estimator's premise that a local readout keeps the success probability |
| Overlap-only estimators agree | 0 | M_F - M_R -0.075 to -0.058 | falsified | Robust and expected: both laws omit g2, which moves F and D differently |
| Record-model estimators agree | 0 | -0.045 to -0.027 | falsified | Undecidable with this estimator: the readout-set dependence of M_R is 0.017 to 0.065, as large as the difference |
| Fidelity at or below the record ceiling | 0.934 | lower end 0.824 | survives | Survives trivially; it constrains nothing at this F |
| Balanced rails, r(11)/r(01) = 1 | 1 | 1.045 to 1.074 | falsified | Robust. The ZZ-only ratio is 1.123 and the retained pair's 1.139: a stable control-side imbalance that the nine-readout average dilutes |
| r(11)/r(01) at the record variant's value | 1.040 | same | falsified | Fragile: misses the interval's lower end 1.0446 by 0.005, while the same ratio moves by 0.05 with the readout set; the retained pair's 1.009 survived |
| Model check: scatter matches the acquisition law | Pearson 166,240 | reference up to 40,271 | falsified | Robust, and fixed by the design: the reference omits the per-seed mesh variance, and the retained pair forecasts a ratio of 4.5 (next section) |
| Constant variance factor (1.44) | 1.44 | ratio 5.73 | falsified | Robust |
| Relative systematic per rate (3.67) | 3.67 | ratio 5.73 | falsified | Robust, by the statistic's clip: cells whose expectation it clips to one event grow with the square of the events (next section) |

## What the decomposition shows

### The failed model check: a known mesh variance read through a clipped statistic

- **Root cause.** The preregistered reference (`overdispersion` in
  `scripts/ascella_cz_tomography_reference_case.py`) draws synthetic pairs under the linear-inversion fit and the
  acquisition law alone. Every setting ran under its own compilation seed, and the service compiles each seed to its
  own mesh. [strategy.md](../quandela/strategy.md) section 7 ("Per-seed mesh variance of a share") records that
  per-seed error at 50 to 80 times binomial variance on qpu:belenos, and the Ascella signed-coherence anchors record
  a per-mesh error of about 0.011 that persists across jobs on the same seeds. The reference carries no such term.
- **Size of the term here.** Beyond binomial, the eligible-outcome shares scatter about the clipped fit with an RMS
  of 0.013 on the retained pair and 0.016 on the band pair (`implied_share_error`). That is the Ascella per-mesh
  scale and the Belenos extreme-block scale (0.0177).
- **Where the statistic lives.** 153,920 of the band Pearson 166,240 (93 %) sits in 34 cells where the unweighted
  linear-inversion fit predicts fewer than one event, mostly negative. The statistic divides those cells by one
  event, so each contributes (n - E)^2, which grows with the square of the events N. Every other cell contributes
  N delta^2 / p, linear in N. Measured between the pairs: the clipped cells grow 48 times and the rest 5.8 times for
  6.1 times the events per rate. The two-click pattern misfit splits the same way (56 times and 5.7 times for 6.9
  times the events), so the per-event systematic in proper cells held constant between the pairs.
- **Forecast.** Scaling the retained pair's clipped cells by the square of the event ratio and the rest by the ratio
  forecasts the band ratio at 4.5, against 5.73 observed (`model_check_forecast`). A linear forecast gives 1.34. At
  the band's counts, the same mesh variance that passed on 2026-10-31 fails the check.
- **Throughput versus shape.** Split exactly, per-setting throughput carries 2,414 of the band's clipped statistic
  29,411 (8.2 %) and the within-setting outcome shape 26,998 (91.8 %). A scalar per-setting brightness or coupling
  drift is minor; a mode-dependent change is not excluded.
- **Guard.** `qd_platform.scatter_check_gaps`, run over every retained case by
  `tests/scripts/test_quandela_scatter_checks.py`, refuses a preregistered scatter check on qpu:ascella or
  qpu:belenos that names no replicate-seed, anchor or descriptive term. This case is listed as frozen before the rule.

### The Z sector: the source model predicts the bit flips

CZ is diagonal, so for a two-photon event a qubit read out in Z keeps its prepared Z population whatever the overlap.
Multiphoton emission, loss, threshold postselection and dark clicks admit eligible events that are not two-photon
events, and those move Z populations.

- **Bit flips of computational preparations:** mean 1.36 % (retained) and 1.37 % (band). The retained noise
  pipeline at the plan read and the g2-aware overlap predicts a mean of 1.04 % and the per-setting pattern at
  Pearson 0.93 and 0.97 (`source_model_z`).
- **What is left:** the measured flips correlate 0.91 between the pairs, and the residuals after subtracting the
  prediction correlate 0.31. The cross-pair correlation reflects the designed settings through the source model,
  not a static hardware fingerprint; 0 of 144 settings share a compilation seed between the pairs, so no mesh is
  common to both.
- **Equator preparations:** the source model predicts their Z-bias pattern at Pearson 0.65 and 0.80 but leaves a
  mean absolute residual of 0.04, and the target |+> and |i> biases moved from +2.7 % and +1.7 % to +6.8 % and
  +5.1 % between the pairs.

### Rail transmission separates loss from preparation

- **Rail ratios:** inputs 00, 01 and 11 succeed with probability 1/9 at every overlap, so r(00)/r(01) is a
  target-rail transmission ratio and r(01)/r(11) a control-rail one.
- **The target ratio flipped** from 0.905 to 1.108 (ZZ readouts). The two-click pattern fit, on the same counts,
  gives effective output-mode weights T0/T1 of 0.913 and 1.098, and 0.918 and 1.094 with the four rail outcomes
  excluded: the target rail-1 output weight fell about 17 % between the pairs. Detection efficiency, output
  propagation and realized-unitary error are not separated by these routes. Between the pairs the service changed
  software (mosaiq-arcturus 2.1.5.2.post4 to post11, hardware-core 3.9.3 to 3.9.11) and dark counts on modes 8 to 10
  fell about tenfold. The control-rail ratio held at 0.878 and 0.890 while the pattern weights C1/C0 sit near 1.00.
- **Postselected bias:** an equator state p0 then reads eta0/(eta0 + eta1) shifted by its rail loss. Subtracting
  that from the equator Z-biases leaves a preparation tilt near +0.05 on the target and -0.03 on the control in both
  pairs. The target bias that moved between the runs moved with its detection rail, not with its preparation.

### The output-weight change accounts for a third of the fidelity drop under its own model

- **Corrected F:** dividing each eligible outcome by its fitted output weight pair e(C_c) e(T_t) moves F from 0.849
  to 0.846 on the retained pair and from 0.832 to 0.834 on the band pair.
- **What remains:** the corrected gap is 0.012, against a raw gap of 0.017. Attributing the removed 0.005 to the
  detectors and the remainder to the gate is a hypothesis: source, preparation and readout, and model error are not
  separated.
- **Eligible share:** the eligible share of window two-click events fell from 0.175 to 0.155 at an unchanged pattern
  overlap. More probability leaves the rails, which fits a worse realized mesh and not a worse photon pair.

### The photon overlap sits near 0.93, and the g2 correction carries most of its distance from the HOM read

| Route | Retained pair (HOM read 87.56 %, g2 1.8 %) | Band pair (HOM read 88.42 %, g2 2.0 %) |
|---|---|---|
| HOM read corrected for g2 (Ollivier et al. 2021, priv 1291df4cd86b, Eq. 1 and 2: identical to distinguishable noise photons) | 0.894 to 0.910 | 0.904 to 0.923 |
| All two-click patterns, eligible and off-rail, Perceval source model at the read's g2, transmittance and dark counts (`g2_pattern_overlap`) | 0.931 | 0.933 |
| All two-click patterns with g2 ignored (`two_click_patterns`) | 0.896 (0.893 to 0.899) | 0.893 (0.892 to 0.894) |
| Fidelity inverted through the record noise model (`record_inversion`) | 0.930 (0.912 to 0.946) | 0.917 (0.910 to 0.924) |
| Rail ratio D through the record noise model | 0.923 (0.904 to 0.942) | 0.952 (0.946 to 0.959) |

- **The pattern route:** it uses the 3.4 to 4.0 million window two-click events, 85 % of them off-rail events that
  the tomography discards. It is independent of the tomography estimator.
- **Effect of g2:** adding the multiphoton model and dark counts moves the pattern overlap by 0.035 to 0.040, the
  same size as Ollivier's correction, and lands both pairs at 0.93. That is 4.9 to 5.5 points above the HOM read and
  about 1 point above the g2-corrected HOM range.
- **What remains after g2:** Ollivier's correction alone accounts for up to 3.9 points (band) and 3.4 points
  (retained), leaving 0.8 to 1.9 points that a pair-dependent visibility (Pont et al. 2022, pub 3c845c21a16f,
  Table S1: about 4 points across pairs and delays) covers.
- **The rail route:** it agrees on the retained pair and stands 2 points high on the band pair, inside its
  readout-set dependence of 0.017 to 0.065.
- **Fidelity route:** on the band pair the fidelity route stands 1.4 points low, matching a gate fidelity lowered by
  something other than the overlap.

Consequence: the dashboard HOM understates the photon-pair overlap at the CZ coupler by about 5 points in both
pairs, and the known multiphoton correction explains most of it. The pattern law is misspecified (Pearson per degree
of freedom 3.7 retained and 17 band with g2 and dark counts), so the quoted intervals are curvature intervals of that
law and not uncertainties of the physical overlap. Confidence is moderate: it falls if a realized-mesh model moves the
overlap by more than 0.01, and the component model below reports the overlap it fits beside each hold-out.

### Per-setting error: not reproduced across fresh seeds, and its source is the realized mesh

- **The map:** the pattern fit gives an effective overlap per setting, a coordinate that absorbs mesh, loss and
  source mismatch. 111 of 144 settings identify it; on those it spreads with standard deviation 0.035 to 0.043 and
  correlates between the pairs at 0.11 (0.11 to 0.24 under other identifiability thresholds). Counting all 144 gives
  0.98, an artifact of settings pinned at 0 or 1.
- **The seed change explains it.** 0 of 144 settings share a compilation seed between the pairs, so every setting
  ran on a different mesh, and the median largest phase difference between a setting's two meshes is 3.1 rad. A low
  correlation is what per-mesh error predicts whether or not the chip recalibrated. Whether the error is fixed
  inside one calibration was not measured: each setting ran once.
- **The transpiler is faithful.** The served meshes reproduce the designed gates to a nominal total variation of at
  most 9.1e-4 (band) and 7.6e-4 (retained), so the error enters between the commanded phases and the photons.
- **Precedent:** Tully, Washburn and Simons 2026 (priv 724460b24428, Sec. V) report repeats inside one calibration
  agreeing within counting and separately compiled circuits scattering beyond it. Fyrillas et al. 2025 (pub
  623fee140d48, Sec. II and V) attribute setting-specific phase errors to heat in bare waveguides.

### A static component model of the 12-mode mesh carries the per-setting error across meshes and dates

Every served mesh of the four jobs decodes to one fixed topology: 132 couplers at calibrated angles, identical in all
288 meshes and on both dates, and 126 heaters whose phases the transpiler sets per iteration. A component error is
therefore shared by every setting, and the per-setting count of 36 free parameters against 14 constraints does not
apply: 132 coupler errors, 126 heater offsets, a heater gain and a crosstalk coefficient stand against 66 two-click
patterns in each of 288 settings. `mesh_model.py` fits them with a ridge penalty, refits the overlap and twelve
output weights on each held-out set, and fixed its pass rule before the fit to measured counts (commit a67b761ee):
Gain = (baseline - transfer) / (baseline - in-sample ceiling) of held-out deviance at least 0.3, and transfer below
every one of 20 null draws of permuted, sign-flipped component errors.

| Hold-out | Gain | Deviance: baseline, transfer, ceiling | Null deviance: min, median | Preregistered rule |
|---|---|---|---|---|
| retained job-00 to job-01 | 0.80 | 37,711; 12,380; 6,179 | 15,355; 18,912 | passes |
| band job-00 to job-01 | 0.84 | 245,543; 57,854; 21,425 | 64,499; 80,973 | passes |
| retained pair to band pair | 0.90 | 477,466; 102,430; 62,685 | 191,406; 385,758 | passes |
| band pair to retained pair | 0.88 | 69,859; 21,291; 14,855 | 22,905; 24,694 | passes |

- **Preregistered reading:** within passes and across passes, so static component errors carry the per-setting
  misfit from 2026-10-31 to 2026-11-09, across a fresh compilation seed for every setting and a service software
  update. The redrawn per-setting pattern follows the commanded phases through fixed components.
- **Qualification (post-data):** random component errors of the fitted size also beat the ideal mesh by a wide
  margin, since any perturbation leaks probability into patterns the ideal mesh puts at zero. Measured from the
  null median instead of the baseline, the fitted components close 0.51 and 0.39 of the remaining span within the
  pairs and 0.88 and 0.35 across them; the band-to-retained transfer clears the best null by 7 %. The predicted
  per-cell shifts correlate with the observed ones at 0.07 to 0.22, the range that element-offset fits reached on
  unseen meshes in the Ascella pathion persistence runs (0.16 to 0.32). The component-specific content is real and
  partial.
- **What the classes say:** the global heater gain and crosstalk fit near zero (|g| at most 0.0044, |k| at most
  0.0014); the transferable content sits in per-coupler errors (RMS 0.022 to 0.040 rad) and per-heater offsets (RMS
  0.022 to 0.067 rad). The self-test shows that two photons on modes 0 and 2 identify those components only in part
  (planted-to-fitted correlation 0.77), so individual values are not readings of single components.
- **Overlap under the realized mesh:** the component model fits overlaps of 0.889 to 0.899 without g2, within 0.007
  of the ideal-mesh pattern fit, so the realized-mesh error does not move the overlap reading.
- **Falsifier of the reading:** the compilation ensemble case's same-seed anchors differing beyond counting inside
  one calibration, or a component model fitted on one date failing to predict a third date's meshes.

## Questions the measurement raises that the preregistration did not ask

- **Which error does the 0.832 measure?** Linear inversion of absolute rates mixes each setting's own preparation
  and readout error, its mesh error and the source's multiphoton events into the process. The Z sector puts the
  source part at about 1 % per readout and the per-mesh share error at 0.013 to 0.016, together of the size of the
  gap to Maring et al. 2024 (pub 0ee7b47bd723, Table 1): average gate fidelity 0.865 against their 0.938 for the same
  1/9 gate class, a figure measured with hourly recalibration.
- **Which physical-channel estimator is intended?** Raw linear inversion gives 0.832, the conditional estimate
  0.811 and the projection onto physical maps 0.790. A comparison with published gate fidelities needs one of them
  named before the data.
- **Can a job difference read drift?** `schedule` assigns inputs to jobs by pair, so job identity is aliased with
  input parity, and a job-00 to job-01 difference does not identify time drift.
- **Does the per-setting error follow the calibration or the compilation seed?** The band pair changed both; the
  component model's hold-out within each pair and across them separates the two through the commanded phases.
- **Is the per-setting error stable inside one run?** Each setting was measured once, so within-run drift and static
  compile error remain inseparable from counts. Proctor et al. 2020 (priv 24b8e9e8f9c6) need chunk order; the
  service returns per-setting totals.
- **What does the dashboard HOM describe?** It is a once-per-calibration source figure (Maring et al. 2023, pub
  8d34bd0f8e4e, Sec. III.A). Pont et al. 2022 (pub 3c845c21a16f, Table S1) record pair-dependent visibility over
  about 4 points, so the pair on modes 0 and 2 can differ from it.

## Measurements that decide them

| Test | Decides | Cost | Falsifier |
|---|---|---|---|
| Component model with g2 in the pattern law and output weights per job (`mesh_model.py` extended) | How much of the remaining held-out deviance the source and per-job weights carry | none | Held-out Gain over the null median stays below 0.5 |
| Constrained process fit with a per-setting preparation-and-readout nuisance (gate-set style, van Enk and Blume-Kohout 2013, priv 01508c79f85b, Sec. IV), with the realized-mesh model as the readout | F with SPAM and mesh error separated | none | The nuisance-free and nuisance fits agree within 0.005 |
| The CZ compilation ensemble case ([design](../../design/ascella-cz-compilation-ensemble-case.md), built, not sent): ten seeds per setting and same-seed anchors in each job | Per-seed mesh variance of the gate and within-calibration repeatability, the two quantities this pair confounds | per its written case | Its homogeneity and anchor tests, as preregistered there |

The first two run on retained counts. The ensemble case already holds the replicate-seed and same-seed-repeat design
that a seed-swap or back-to-back repeat of job-00 would duplicate, and it needs the owner's approval of its written
case.
