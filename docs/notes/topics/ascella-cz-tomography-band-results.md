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
  - the post-data decomposition `docs/evidence/ascella-cz-tomography-band/findings.json`, written by `docs/evidence/ascella-cz-tomography-band/analyze.py` (deterministic, 47 s).

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
| r(11)/r(01) at the record variant's value | 1.040 | same | falsified | Robust but small: 2 % beyond the lost-twin multiphoton term; the retained pair's 1.009 survived |
| Model check: scatter matches the acquisition law | Pearson 166,240 | reference up to 40,271 | falsified | Robust, and its content differs from its name (next section) |
| Constant variance factor (1.44) | 1.44 | ratio 5.73 | falsified | Robust |
| Relative systematic per rate (3.67) | 3.67 | ratio 5.73 | falsified | Robust: the excess grows faster than in proportion to events (next section) |

## What the decomposition shows

### The failed model check reads unphysical predictions, and the misfit grows with N squared

- **Where the statistic lives:** 153,920 of the band Pearson 166,240 (93 %) sits in 34 cells where the unweighted
  linear-inversion fit predicts fewer than one event, mostly negative counts near -100, while those cells hold 333
  observed events. The retained pair shows the same structure: 3,181 of 5,288 in 32 cells.
- **Why they carry it:** the statistic divides by max(expected, 1), so a cell predicted at -130 with 5 observed
  contributes about 18,000.
- **What the residual is:** the residual (I - A A+) r is the part of the rates that no linear map, physical or
  not, reproduces. These cells measure inconsistency between settings, not shot noise.
- **Clipped statistic:** with expected counts clipped at one before subtracting, the statistic is 29,411 on the band
  pair and 3,134 on the retained pair.
- **Throughput versus shape:** per-setting throughput carries 2,414 of the band's clipped statistic (8 %) and the
  within-setting outcome shape 25,545 (87 %). So drift of source brightness or coupling across the sequential
  settings does not explain the scatter. The service's samples-per-shot monitor varies 14 to 23 % across settings,
  yet it correlates at most 0.17 with the per-setting rate residual.
- **Misfit scaling:** the two-click pattern fit gives an independent measure. Its misfit grows 49.3 times for 6.90
  times the events, against N squared = 47.7. A fixed relative error per setting adds variance in N squared and
  counting adds variance in N, so the misfit is systematic to within the precision of that ratio.

The acquisition-law model check therefore fails at any event count large enough for the systematic to exceed counting
noise. On the retained pair the systematic was already present and the reference's bias hid it.

### The gate-independent sector: a static bit-flip fingerprint and stable preparation tilts

CZ is diagonal. A qubit read out in Z therefore keeps its prepared Z population whatever the gate, the photon overlap
or the dephasing. The 96 such qubit readouts measure preparation and readout error, free of the gate.

- **Bit flips of computational preparations:** mean 1.37 % in both pairs, largest 5.7 %. The per-setting pattern
  correlates between the pairs at Pearson 0.91 and Spearman 0.93, and at 0.80 without the six largest. This is the
  one static per-setting fingerprint the data show.
- **Not crosstalk from the other qubit:** the flip size does not depend on whether the other qubit is rotated
  (1.0 to 1.6 % in every group on the band pair). Neighbor thermal crosstalk is not supported, with four settings
  per group, so the test is weak.
- **Z-bias of equator preparations, cross-run correlation 0.60:**
  - control |+> sits at -5.7 % in both pairs;
  - target |+> and |i> moved from +2.7 % and +1.7 % to +6.8 % and +5.1 %.

### Rail transmission separates loss from preparation

- **Rail ratios:** inputs 00, 01 and 11 succeed with probability 1/9 at every overlap, so r(00)/r(01) is a
  target-rail transmission ratio and r(01)/r(11) a control-rail one.
- **The target ratio flipped** from 0.905 to 1.108 (ZZ readouts). The two-click pattern fit measures the same change
  independently, as relative detection efficiencies T0/T1 of 0.913 and 1.098: the target rail-1 detection efficiency
  fell about 17 % between the calibrations. The control-rail ratio held at 0.878 and 0.890, while the pattern fit
  finds C1/C0 detection near 1.00, so the control imbalance lies before detection, in the preparation or propagation
  path.
- **Postselected bias:** an equator state p0 then reads eta0/(eta0 + eta1) shifted by its rail loss. Subtracting
  that from the equator Z-biases leaves a preparation tilt near +0.05 on the target and -0.03 on the control in both
  pairs. The target bias that moved between the runs moved with its detection rail, not with its preparation.

### The detector change explains a third of the fidelity drop

- **Corrected F:** dividing each eligible outcome by its fitted detection pair e(C_c) e(T_t) moves F from 0.849 to
  0.846 on the retained pair and from 0.832 to 0.834 on the band pair.
- **What remains:** the efficiency-corrected gap is 0.012, against a raw gap of 0.017. The other 0.012 is gate or
  mesh error.
- **Eligible share:** the eligible share of window two-click events fell from 0.175 to 0.155 at an unchanged pattern
  overlap. More probability leaves the rails, which fits a worse realized mesh and not a worse photon pair.

### Three routes to the photon overlap converge near 0.91 to 0.92; the rail route is the outlier

| Route | Overlap |
|---|---|
| HOM read corrected for g2 = 2 % (Ollivier Eq. 1 and 2: identical to distinguishable noise photons) | 0.904 to 0.923 |
| Fidelity inverted through the record noise model at the plan read (`record_inversion`) | 0.917 (0.910 to 0.924) |
| All two-click patterns, eligible and off-rail, one overlap and six detection efficiencies, g2 ignored | 0.893 (0.892 to 0.894) |
| Rail ratio D through the record model | 0.952 (readout-set dependent: 0.939 to 0.956 overlap-only) |

- **The pattern fit:** it uses the 3.36 million two-click events that the tomography discards as off-rail. It
  ignores g2, whose noise photons lower apparent visibility, so it reads low by about the g2 correction.
- **Consequence:** the platform's HOM read understates the photon-pair overlap by 2 to 4 points once g2 is
  restored, not by the 5 to 7 points that the rail estimator reports.
- **What would raise or lower this:** confidence is moderate. It rises if a g2-aware pattern fit lands at 0.91 to
  0.92. It falls if per-setting mesh error, which the pattern fit absorbs into the overlap, shifts that fit by more
  than 0.01.

### Per-setting error is fixed inside a calibration and redrawn by recalibration

- **The map:** the pattern fit gives an overlap per setting. Settings where the photons never meet leave it
  unidentified (pinned at 0 or 1); 111 of 144 are identified.
- **Spread and correlation:** on the identified settings the per-setting overlap spreads with standard deviation
  0.035 to 0.043 around a median of 0.893 to 0.895, and correlates between the pairs at only 0.11. Counting all 144
  settings gives 0.98, an artifact of the pinned settings.
- **Reading:** the setting-to-setting variation is systematic within a run (the N squared misfit) and not
  reproduced nine days and at least one recalibration later.
- **Precedent:** Tully, Washburn and Simons 2026 (priv 724460b24428, Sec. V) report the same split on Belenos.
  Repeats of one circuit inside one calibration agree within counting; separately compiled circuits scatter beyond
  it.
- **Mechanism:** Fyrillas et al. 2025 (pub 623fee140d48, Sec. II and V) give one: heat in bare waveguides makes
  setting-specific phase errors that a crosstalk model of controlled shifters leaves at 7.5 % total variation on
  random patterns.
- **The confound:** the band pair used fresh compilation seeds (QRNG indices 0 to 143 of the 2026-11-09 draw), so
  "redrawn by recalibration" and "redrawn by recompilation" are not separated.

## Questions the measurement raises that the preregistration did not ask

- **Which error does the 0.832 measure?** Linear inversion of absolute rates mixes each setting's own preparation
  and readout error into the process. The gate-independent sector shows that error at 1 to 7 %, which is the size of
  the gap to Maring et al. 2024 (pub 0ee7b47bd723, Table 1): average gate fidelity 0.865 against their 0.938 for the
  same 1/9 gate class.
- **What do the off-rail events know?** 85 % of window two-click events are off-rail. They carry 11 constraints per
  setting beyond the 4 eligible outcomes, enough to fit each setting's realized mesh error.
- **Does the per-setting error follow the calibration or the compilation seed?** The band pair changed both.
- **Is the per-setting error stable inside one run?** Each setting was measured once, so within-run drift and static
  compile error remain inseparable from counts. Proctor et al. 2020 (priv 24b8e9e8f9c6) need chunk order; the
  service returns per-setting totals.
- **What does the dashboard HOM describe?** It is a once-per-calibration source figure (Maring et al. 2023, pub
  8d34bd0f8e4e, Sec. III.A). Pont et al. 2022 (pub 3c845c21a16f, Table S1) record pair-dependent visibility over
  about 4 points, so the pair on modes 0 and 2 can differ from it.

## Measurements that decide them

| Test | Decides | Cost | Falsifier |
|---|---|---|---|
| Off-rail self-calibration: fit per-setting phase errors of the realized mesh from the 15-pair distributions, then reconstruct the process with the calibrated unitaries | Whether the per-setting systematic is mesh error, and the process fidelity free of it | none (retained counts) | The calibrated fit leaves a misfit that still grows with N squared |
| g2-aware pattern fit (Perceval `photon_distribution` at g2 = 2 %) | The overlap the off-rail data give with noise photons modeled | none | The fit stays below 0.90 |
| Constrained process fit with a per-setting preparation-and-readout nuisance (gate-set style, van Enk and Blume-Kohout 2013, priv 01508c79f85b, Sec. IV) | F with SPAM separated | none | The nuisance-free and nuisance fits agree within 0.005 |
| job-00 twice back to back with its retained seeds | Within-calibration reproducibility of the per-setting pattern | 2 x 2.567 credits | Per-setting outcome differences between repeats exceed counting (Rudinger et al. 2019, priv 8c2599bc077d, Eq. 11 to 13, with Hochberg control) |
| job-00 at the retained 2026-10-31 compilation seeds, beside a fresh-seed repeat, in one calibration | Seed versus calibration as the source of the redrawn pattern | 2 x 2.567 credits | The per-setting pattern follows neither the seed nor the calibration |

The first three tests run on retained data. The last two need new provider jobs and an approved written case each.
