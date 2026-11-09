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
  - the component model of the mesh and its preregistered hold-out, `docs/evidence/ascella-cz-tomography-band/mesh_model.py` and `mesh-model.json`;
  - the preregistered model-check reference with a per-seed mesh term, `docs/evidence/ascella-cz-tomography-band/mesh_variance_reference.py` and `mesh-variance-reference.json`.

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
| Model check: scatter matches the acquisition law | Pearson 166,240 | reference up to 40,271 | falsified | Robust. The reference omits the per-seed mesh variance; with it at the recorded scale the retained pair is reproduced and the band pair still fails, at 2.3 to 3.4 times its reference (next section) |
| Constant variance factor (1.44) | 1.44 | ratio 5.73 | falsified | Robust |
| Relative systematic per rate (3.67) | 3.67 | ratio 5.73 | falsified | Robust, and carried by the cells whose expectation the statistic clips to one event; the other cells grow with the events (next section) |

## What the decomposition shows

### The failed model check: the per-seed mesh variance accounts for the retained pass and part of the band failure

- **Missing term.** The preregistered reference (`overdispersion` in
  `scripts/ascella_cz_tomography_reference_case.py`) draws synthetic pairs under the linear-inversion fit and the
  acquisition law alone. Every setting ran under its own compilation seed, and the service compiles each seed to its
  own mesh. [strategy.md](../quandela/strategy.md) section 7 ("Per-seed mesh variance of a share") records that
  per-seed error at 50 to 80 times binomial variance on qpu:belenos, and the Ascella signed-coherence anchors record
  a per-mesh error of about 0.011 that persists across jobs on the same seeds. The reference carries no such term.
- **The reference with the term (preregistered test).** `mesh_variance_reference.py` adds independent Gaussian
  share errors per setting and synthetic pair to the case's own reference, at sigma 0.011 (Ascella anchors) and
  0.0177 (Belenos extreme blocks), with its rule fixed before the run (commit 2efbb1e88). Verdict: partial.
  The retained statistic 5,288 sits inside the reference at both values (mean 5,022 at 0.011), and its mean matches
  at sigma 0.0106. The band statistic 166,240 stays outside at both (ratio 3.40 at 0.011, 2.34 at 0.0177), and its
  mean matches only at sigma 0.034, three times the recorded scale. The omitted term explains the retained pass and
  removes half of the band's excess in ratio; it leaves the rest unexplained.
- **Where the rest sits.** 153,920 of the band Pearson (93 %) sits in 34 cells where the unweighted linear-inversion
  fit predicts fewer than one event, mostly negative; the statistic divides those by one event, so each contributes
  (n - E)^2. Only 11 of those cells are below one event in both pairs. On cells in the same class in both pairs, the
  clipped cells grow 44 times and the rest 5.9 times for 6.1 times the events per rate; the two-click pattern misfit,
  whose 795 cells keep their class, splits the same way (56 and 5.7 times for 6.9 times the events). The proper
  cells show no growth of the per-event error, so the excess beyond the recorded per-seed scale sits in the
  near-zero cells, which a larger isotropic share error would not confine there. Hypothesis, low confidence: a
  structured leak into outcomes the gate leaves dark (multiphoton or dark-count events, or a mode-dependent loss)
  that grew between the dates; it falls if a reference with an output weight per mode and job reproduces the band.
- **Scaling the retained statistic.** About 70 % of the retained statistic is acquisition scatter (its reference
  mean, 3,677), and the clip inflates that scatter too: the reference mean grows 7.9 times between the pairs for
  6.1 times the events. Scaling the whole retained statistic gives 4.5 (clipped cells by the square of the event
  ratio) or 4.3 (counts and expectations rescored under the clip), against 5.73 observed; both carry counting
  scatter as if it were systematic, so neither is a forecast (`model_check_forecast`).
- **Size of the share error.** Beyond binomial, the eligible-outcome shares scatter with an RMS of 0.013 (retained)
  and 0.016 (band) about the in-sample fit, 0.028 and 0.029 about the physical projection, and 0.032 and 0.031 about
  leave-one-cell-out predictions (`implied_share_error`). The in-sample value absorbs part of what it measures and no
  center is fully out of sample, so these bracket the per-seed scale at 0.013 to 0.032 and identify none.
- **Throughput versus shape.** The case's statistic has no exact throughput/shape split, because its clip leaves the
  negative-expectation cells at weight E^2 in any projection. Per-setting event totals deviate from the fit's
  totals by a median of 3.1 % (band) and 5.3 % (retained), a Pearson of 2,434 and 565 across 144 settings, small
  beside the full statistics; the clipped-center statistic splits the same way (2,414 throughput, 26,998 shape). A
  scalar per-setting brightness drift is minor by both measures; a mode-dependent change is not excluded.
- **Guard.** `qd_platform.scatter_check_gaps`, run over every retained case by
  `tests/scripts/test_quandela_scatter_checks.py`, refuses a preregistered scatter statistic (overdispersion,
  homogeneity, goodness of fit, Pearson, deviance and kin, at any depth) on qpu:ascella or qpu:belenos unless a typed
  `mesh_variance` term names replicate seeds with their degrees of freedom, same-seed anchors with their repeats, or
  a non-decisional check that gates no verdict. Three earlier cases are listed with the place their text carries
  the term, this one with none.

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
  overlap. More probability leaves the rails. A worse realized mesh fits that; the conditional pattern law is
  misspecified and blind to absolute success, so a source change is not excluded.

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

### Per-setting error: not reproduced across fresh seeds, its source not identified

- **The map:** the pattern fit gives an effective overlap per setting, a coordinate that absorbs mesh, loss and
  source mismatch. 111 of 144 settings identify it; on those it spreads with standard deviation 0.035 to 0.043 and
  correlates between the pairs at 0.11 (0.11 to 0.24 under other identifiability thresholds). Counting all 144 gives
  0.98, an artifact of settings pinned at 0 or 1.
- **The seed change explains it.** 0 of 144 settings share a compilation seed between the pairs, so every setting
  ran on a different mesh, and the median largest phase difference between a setting's two meshes is 3.1 rad. A low
  correlation is what per-mesh error predicts whether or not the chip recalibrated. Whether the error is fixed
  inside one calibration was not measured: each setting ran once.
- **The transpiler is faithful.** The served meshes reproduce the designed gates to a nominal total variation of at
  most 9.1e-4 (band) and 7.6e-4 (retained), so the error enters after compilation: in the realized mesh, the
  source, or detection.
- **Precedent:** Tully, Washburn and Simons 2026 (priv 724460b24428, Sec. V) report repeats inside one calibration
  agreeing within counting and separately compiled circuits scattering beyond it. Fyrillas et al. 2025 (pub
  623fee140d48, Sec. II and V) attribute setting-specific phase errors to heat in bare waveguides.

### A static model of the commanded phases predicts part of the per-setting error on held-out meshes and dates

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

- **Preregistered reading:** within passes and across passes. A static model of the commanded phases through fixed
  components predicts part of the held-out pattern error, from 2026-10-31 to 2026-11-09, across a fresh compilation
  seed for every setting and a service software update. The pass shows a transferable phase-command fingerprint; it
  does not locate the error in components, and it does not separate the calibration from the seed, which changed
  together.
- **Qualification (post-data):** random component errors of the fitted size also beat the ideal mesh by a wide
  margin, since any perturbation leaks probability into patterns the ideal mesh puts at zero. Measured from the
  null median instead of the baseline, the fitted components close 0.51 and 0.39 of the remaining span within the
  pairs and 0.88 and 0.35 across them; the band-to-retained transfer clears the best null by 7 %. The predicted
  per-cell shifts correlate with the observed ones at 0.07 to 0.22, the range that element-offset fits reached on
  unseen meshes in the Ascella pathion persistence runs (0.16 to 0.32). The null permutes only the coupler and heater
  vectors (gain and crosstalk, both near zero, are copied), it holds 20 draws, and `fit` records no optimizer status
  or restarts, so the margin over the null is measured, its false-positive rate is not.
- **What the fitted classes say:** the global heater gain and crosstalk fit near zero (|g| at most 0.0044, |k| at
  most 0.0014); the fit places its content in per-coupler errors (RMS 0.022 to 0.040 rad) and per-heater offsets
  (RMS 0.022 to 0.067 rad). Two photons on modes 0 and 2 leave gauge directions, and the self-test recovers planted
  components only in part (correlation 0.77) from data drawn under the same model, so neither the split between the
  classes nor any single value reads a physical component. The neighborhood of the crosstalk term follows the ASAP
  column order, whose match to the chip's thermal layout is a hypothesis.
- **Overlap under the realized mesh:** the component model fits overlaps of 0.889 to 0.899 without g2, within 0.007
  of the ideal-mesh pattern fit, so the realized-mesh error does not move the overlap reading.
- **Falsifier of the reading:** the compilation ensemble case's same-seed anchors differing beyond counting inside
  one calibration, or a component model fitted on one date failing to predict a third date's meshes.

## Questions the measurement raises that the preregistration did not ask

- **Which error does the 0.832 measure?** Linear inversion of absolute rates mixes each setting's own preparation
  and readout error, its mesh error and the source's multiphoton events into the process. The Z sector puts the
  source part at about 1 % per readout and the per-seed share error at 0.013 to 0.032; neither has a demonstrated
  map to process fidelity, so their sum does not measure the gap to Maring et al. 2024 (pub 0ee7b47bd723, Table 1):
  average gate fidelity 0.865 against their 0.938 for the same 1/9 gate class, a figure measured with hourly
  recalibration. The constrained fit below separates them.
- **Which physical-channel estimator is intended?** Raw linear inversion gives 0.832, the conditional estimate
  0.811 and the projection onto physical maps 0.790. A comparison with published gate fidelities needs one of them
  named before the data.
- **Can a job difference read drift?** `schedule` assigns inputs to jobs by pair, so job identity is aliased with
  input parity, and a job-00 to job-01 difference does not identify time drift.
- **Does the per-setting error follow the calibration or the compilation seed?** The band pair changed both, and so
  does every cross-date hold-out of the component model. The ensemble case's same-seed anchors separate them.
- **Is the per-setting error stable inside one run?** Each setting was measured once, so within-run drift and static
  compile error remain inseparable from counts. Proctor et al. 2020 (priv 24b8e9e8f9c6) need chunk order; the
  service returns per-setting totals.
- **What does the dashboard HOM describe?** It is a once-per-calibration source figure (Maring et al. 2023, pub
  8d34bd0f8e4e, Sec. III.A). Pont et al. 2022 (pub 3c845c21a16f, Table S1) record pair-dependent visibility over
  about 4 points, so the pair on modes 0 and 2 can differ from it.

## Measurements that decide them

| Test | Decides | Cost | Falsifier |
|---|---|---|---|
| Component model with output weights per job, then g2 in the pattern law (`mesh_model.py` extended), with nulls that also permute gain and crosstalk and record optimizer status | Whether the transferable content survives per-job output weights (job identity is aliased with input parity), and how much the source carries | none | Held-out Gain over the null median falls below 0.3 with per-job weights |
| Model-check reference with a per-seed term and an output weight per mode and job | Whether a mode-dependent leak carries the band excess beyond the recorded per-seed scale | none | The band statistic stays outside the reference's central 95 % |
| Constrained process fit with a per-setting preparation-and-readout nuisance (gate-set style, van Enk and Blume-Kohout 2013, priv 01508c79f85b, Sec. IV), with the realized-mesh model as the readout | F with SPAM and mesh error separated | none | The nuisance-free and nuisance fits agree within 0.005 |
| The CZ compilation ensemble case ([design](../../design/ascella-cz-compilation-ensemble-case.md), built, not sent): ten seeds per setting and same-seed anchors in each job | Per-seed mesh variance of the gate and within-calibration repeatability, the two quantities this pair confounds | per its written case | Its homogeneity and anchor tests, as preregistered there |

The first three run on retained counts. The ensemble case already holds the replicate-seed and same-seed-repeat design
that a seed-swap or back-to-back repeat of job-00 would duplicate, and it needs the owner's approval of its written
case.
