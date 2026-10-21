# Published methods for characterizing and controlling a Belenos-class MZI mesh

Retrieved 2026-10-17. Scope: qpu:belenos, a 24-mode thermo-optic Mach-Zehnder
mesh (276 MZIs, 552 Rx beam splitters, 574 phase elements in the compiled
circuit) fed by a quantum-dot source through a 12-input demultiplexer. The
note collects the methods that apply to (a) reconstructing a mesh unitary from
single-photon or coherent-light data, (b) error models of programmable MZI
meshes and their depth scaling, (c) correction, self-configuration and
compilation against mesh errors, and (d) Quandela's own chip, source, detector
and compiler publications.

## Reading rules

- Every arXiv source was downloaded as PDF from arxiv.org and converted with
  `pdftotext`. Numbers and equations come from that text. Where the text dump
  lost a radical or exponent (Laing and O'Brien Eq. 12, Hamerly Eq. 2 and the
  phase-error threshold) the page image was rendered and read instead.
  Search-engine and fetch-tool summaries supplied leads only; one summary
  reported a "77-fold" improvement for Maring et al., and the PDF reads
  "7-fold".
- Depth tags: `full` = read end to end; `sections` = the named sections read
  and the rest skimmed; `abstract only` = abstract (and metadata) read, body
  not used.
- "Derived here" marks arithmetic or reasoning added in this note; it is not a
  claim of the cited paper.
- Author names are transliterated to ASCII. Dates are arXiv submission dates.
- The four uses named in each "Use here" line are:
  - U1: fit a shared static per-heater phase-offset vector across many settings
    whose meshes are known;
  - U2: choose among random transpiler solutions (seeds);
  - U3: detect misrouting of the input photon;
  - U4: estimate dark counts and detector or port efficiency.

## Source index

| # | arXiv or id | Short name | Topic | Depth |
|---|---|---|---|---|
| 1 | 2306.00874v1 | Maring, Ascella platform | d, a, b | full |
| 2 | 2308.14582v1 | Maring, cloud availability | d | sections |
| 3 | 2505.01609v2 | Barzaghi, 24-mode glass chip | d, a, b | full |
| 4 | 2510.07240v2 | Thomas, classical shadows (Belenos hardware) | d | sections |
| 5 | 2609.14153v1 | Karooby, QSP on Belenos | d | sections |
| 6 | 2605.10471v1 | Lopez Carreno, photonic reservoir | d | sections |
| 7 | 2606.18408v2 | Tully, Walsh filters on Belenos | d | sections |
| 8 | 2604.04691v2 | Franco, IFM on Ascella | d, c | sections |
| 9 | 2609.13379v1 | Forster, subcircuit compilation | c, d | sections |
| 10 | 2202.04735v1 | Mezher, photonic quality factor | d | sections |
| 11 | 2204.00602v3 | Heurtel, Perceval | d | sections |
| 12 | vendor page, repo capture | Quandela product page and compile guide | d | full |
| 13 | 1208.2868v1 | Laing, O'Brien | a | sections |
| 14 | 1210.6463v3 | Rahimi-Keshari | a | sections |
| 15 | 1508.00283v2 | Dhand, accurate characterization | a | sections |
| 16 | 2310.15349v2 | Fyrillas, clear-box ML | a, c, d | sections |
| 17 | 2506.05988v1 | Fyrillas, induced phase shifters | a, b, c, d | sections |
| 18 | 2310.19718v1 | Pentangelo, laser-written UPPs | a, b | sections |
| 19 | 2203.01801v5 | Taballione, 20-mode processor | a, b | sections |
| 20 | 1603.08788v2 | Clements | b | sections |
| 21 | 1704.01945v1 | Burgwal | b | sections |
| 22 | 1506.06220v2 | Russell | b | sections |
| 23 | 1910.13001v2 | Fldzhyan | b | sections |
| 24 | 2106.03249v2 | Hamerly, rectangular self-configuration | b, c | sections |
| 25 | 2106.04363v2 | Hamerly, stability | b, c | sections |
| 26 | 2103.04993v1 | Bandyopadhyay, hardware error correction | b, c | sections |
| 27 | 2103.03183v1 | Kumar, port allocation | c | sections |
| 28 | 1912.08789v1 | Dhand, defective components | c | abstract only |
| 29 | peripheral set | thermal crosstalk, drift and calibration, 2022-2026 | a, b, c | mixed |

## Conventions used in this note

- Perceval Rx beam splitter as decoded by `scripts/qd_belenos_mesh.py`:
  B(theta) = [[cos(theta/2), i sin(theta/2)], [i sin(theta/2), cos(theta/2)]].
  The literature splitter S(pi/4 + alpha) of Bandyopadhyay Eq. (1) and Hamerly
  Fig. 1 is the same matrix with theta/2 = pi/4 + alpha. Power reflectivity
  (diagonal element squared) is R = cos^2(theta/2) = (1 - sin(2 alpha))/2 and
  the imbalance is alpha = theta/2 - pi/4.
- Derived here, for the retained calibrated angles 1.557, 1.5867 and 1.662 rad:

  | theta (rad) | R | alpha (rad) | CROSS floor sin^2(2 alpha), both couplers equal |
  |---|---|---|---|
  | 1.557 | 0.5069 | -0.0069 | 0.00019 |
  | 1.5867 | 0.4920 | +0.0080 | 0.00025 |
  | 1.662 | 0.4545 | +0.0456 | 0.00830 |

  With equal couplers the BAR floor is 0.
- Derived here (checked numerically, and consistent with Fldzhyan's
  transmissivity formula and Kumar Eq. 4): an MZI B(theta2) diag(e^{i phi}, 1)
  B(theta1) with imbalances alpha1, alpha2 keeps power in the same waveguide
  in the range [sin^2(alpha1 + alpha2), 1 - sin^2(alpha1 - alpha2)] and moves
  power to the other waveguide in the range [sin^2(alpha1 - alpha2), 1 -
  sin^2(alpha1 + alpha2)]. The CROSS state (light switches waveguide) therefore
  leaks at least sin^2(alpha1 + alpha2) into the same waveguide, and the BAR
  state (light stays) leaks at least sin^2(alpha1 - alpha2) into the other. For
  alpha1 = +0.0456 and alpha2 = -0.0069 the CROSS and BAR floors are 0.0015 and
  0.0028; for two couplers at +0.0456 they are 0.0083 and 0.
- Gauge. With Fock-state inputs and intensity detection, one phase per input
  and one per output is unobservable, 2N - 1 in total after the common phase
  (Rahimi-Keshari; Laing and O'Brien; Fyrillas 2025 Theorem 1). A fitted
  offset vector is defined only modulo these directions.
- Belenos hardware counts disagree across sources and are recorded, not
  reconciled: 552 directional couplers (Barzaghi; Thomas), 576 microheaters
  (Barzaghi), 574 phase elements in the cloud's compiled circuit (repo
  decoder), 676 thermo-optic phase shifters (Thomas). The 676 value differs
  from 576 by one digit; whether it is a typo is not established.

---

## Part I. Quandela, the Belenos chip and its users (topic d)

### 1. Maring et al., Ascella platform

- Citation: N. Maring, A. Fyrillas, M. Pont, E. Ivanov, P. Stepanov, N.
  Margaria, W. Hease, A. Pishchagin, T. H. Au, S. Boissier, E. Bertasi, A.
  Baert, M. Valdivia, M. Billard, O. Acar, A. Brieussel, R. Mezher, S. C. Wein,
  A. Salavrakos, P. Sinnott, D. A. Fioretto, P.-E. Emeriau, N. Belabas, S.
  Mansfield, P. Senellart, J. Senellart, N. Somaschi. arXiv title (v1): "A
  general-purpose single-photon-based quantum computing platform." Published
  as "A versatile single-photon-based quantum computing platform," Nature
  Photonics 18, 603-609 (2024). arXiv:2306.00874v1 (1 Jun 2023, the only
  version). https://arxiv.org/abs/2306.00874. Retrieved 2026-10-17. Depth: full.
- Summary. Ascella is the 12-mode predecessor of Belenos: a quantum-dot source,
  an active demultiplexer, a 12-mode Si3N4 rectangular interferometer with 126
  voltage-controlled thermo-optic phase shifters and 132 directional couplers,
  and SNSPDs. A machine-learned model of the phase-voltage map, coupler
  reflectivities and output losses feeds a two-stage control path: a global
  optimization compiles a target unitary into phases, and a transpilation step
  converts phases to voltages with crosstalk compensation. The system
  recalibrates hourly. The paper benchmarks the path by total variation
  distance (TVD) over 300 random phase configurations.
- Model and procedure (SI S-IV, main text "Chip control"):
  - phi = A V.^2 + b, with phi the 126 implemented phases, V the 126 voltages,
    .^2 element-wise squaring, A a 126 x 126 matrix whose off-diagonal entries
    are thermal crosstalk, b the passive offsets; about 16000 free parameters,
    fitted jointly with coupler reflectivities and relative output losses.
  - The SI states that the apparent long-range structure of A consists of
    artefacts of transformations of A that leave the output state unchanged
    (a gauge freedom).
  - Compile: "a global optimization step fine-tunes the phase shifts to enhance
    matrix fidelity", then voltages are computed "while compensating for
    thermal crosstalk". Photon input ports are fixed, so arbitrary input
    configurations are realized as U x U_perm with a permutation matrix.
  - Benchmark: TVD between measured and simulated 12-output count rates over
    300 random phase configurations.
- Numbers:
  - b entries (0.1 +- 1.2) rad; diagonal of A (0.034 +- 0.001) rad/V^2, so a pi
    shift needs about 10 V.
  - Coupler reflectivity average (56.7 +- 0.6) % in the main text and (56.8 +-
    0.6) % in S-IV, at 928 nm; low and high reflectivity regions follow the
    chip's folding.
  - Mode 10 transmits about 75 % relative to mode 6, confirmed with a power
    meter array and with single-photon detectors.
  - TVD: (21 +- 11) % with interference-fringe characterization at 925 nm,
    (3.0 +- 1.3) % with the ML characterization at 928 nm (a 7-fold
    improvement), repeatability about 3 % relative; compile plus transpile
    fidelity F = 99.7 +- 0.08 % (procedure of Taballione et al.).
  - Phase-scan check on an 8 x 8 unitary: fit slope a = 1.00 +- 0.01, offset b
    = -0.06 +- 0.08 rad.
  - Gate fidelities: one-qubit gate 99.6 +- 0.1 %, CNOT 93.8 +- 0.6 %, Toffoli
    86 +- 1.2 %. The one-qubit error is attributed to state preparation and
    measurement.
  - Loss budget (Table S1): PIC insertion and transmission 45 % (target 70 %),
    demultiplexer 70 %, SNSPD 92 %, total 8.4 +- 0.2 %.
  - SNSPD dark count rate under 20 Hz; coincidence window 1 ns.
  - Source: g2(0) = (7.32 +- 0.07) x 10^-3; HOM visibility 0.9296 +- 0.0003,
    corrected indistinguishability 0.9438 +- 0.0003; 80 MHz excitation.
  - A phenomenological 6-photon boson-sampling simulator that includes
    transpilation error and phase imperfection gives TVD 0.132 against data.
- Use here: (U1) the model phi = A V.^2 + b is the template for a per-heater
  offset vector; b has a spread of order one radian before calibration, so the
  offsets are large and wrap, and the SI gauge remark says to fix gauge before
  quoting offsets; (U2) the compile is a gradient-based global optimization
  with an initialization, so start dependence is expected (source 8 documents
  it); (U3) a calibrated 12-mode chip reaches
  TVD of a few percent, so a retained fraction of 0.47 is far outside the
  calibrated-chip scale; (U4) SNSPD efficiency 92 % and dark counts below 20 Hz
  anchor the order of magnitude, and a 25 % transmission deficit on one output
  mode shows that per-output efficiency must be fitted.

### 2. Maring et al., cloud availability

- Citation: N. Maring, A. Fyrillas, M. Pont, E. Ivanov, E. Bertasi, M.
  Valdivia, J. Senellart. "One nine availability of a Photonic Quantum
  Computer on the Cloud toward HPC integration." arXiv:2308.14582v1 (28 Aug
  2023). https://arxiv.org/abs/2308.14582. Retrieved 2026-10-17. Depth:
  sections (operation and calibration passages).
- Summary. Six months of Ascella cloud operation at 92 % availability. The
  system runs a few minutes of automated calibration every hour that measures
  92 parameters (optical transmissions, purity, indistinguishability, module
  temperatures); the calibration time counts as downtime.
- Procedure: the chip imperfections (passive phases, thermal crosstalk,
  asymmetric directional couplers, inhomogeneous input and output losses) are
  measured by the ML method of Fyrillas et al. (source 16), compensated by the
  compile and transpile steps, and the characterization "can take up to 24
  hours for the Ascella UPIC and must be executed every time a new
  single-photon source is installed", with on-the-fly updates from usage data
  in preparation. Weekly maintenance lasts 4 hours.
- Use here: (U1) the offset model is refreshed from usage data, so the
  residual a user sees is calibration-state dependent; (U2) n/a; (U3) the
  hourly metric set is the reference for logging calibration state per job;
  (U4) the transmissions and purity published per request are the available
  efficiency priors.

### 3. Barzaghi et al., the 24-mode glass chip

- Citation: A. Barzaghi, M. Benefice, F. Ceccarelli, G. Corrielli, V. Galli,
  M. Gardina, V. Grimaldi, J. Kaczorowski, F. Malaspina, R. Osellame, C.
  Pentangelo, A. Rocchetto, A. Rudi. "A low-loss, 24-mode laser-written
  universal photonic processor in a glass-based platform." arXiv:2505.01609v2
  (2 May 2025, v2 30 Jul 2025; Ephos and CNR-IFN). Thomas et al. (source 4,
  ref. 88) cite this work as Proc. SPIE, Quantum Computing, Communication, and
  Simulation V (2025), under the title "A 24-mode laser-written universal
  photonic processor in a glass-based platform." https://arxiv.org/abs/2505.01609.
  Retrieved 2026-10-17. Depth: full.
- Summary. This is the chip class behind Belenos. The paper never names
  Quandela or Belenos; the link rests on Thomas et al. ref. 88 (24-mode silica
  glass interferometer, 552 beam splitters) and Karooby et al. ref. 8 (15 x 134
  mm^2 footprint), which match this device. It describes a femtosecond-laser-
  written 24-mode mesh in Corning EAGLE XG alumino-borosilicate glass for 925
  nm, 552 directional couplers, 576 chromium microheaters (each MZI has two
  thermal shifters), isolation trenches 60 um deep and 1 mm long that leave
  the MZI arms suspended, and a machine-learned calibration.
- Procedure: calibration starts by optimizing the route from the first input to
  the last output with interference fringes, then measures 30000 unitaries with
  every heater set to a uniformly random dissipated power between 0 and 45 mW.
  A machine-learning model trained on these fits the 576 static phase
  contributions, the 552 coupler splitting ratios and 13824 thermal crosstalk
  coefficients (13824 = 576 x 24; the paper does not state the neighborhood
  structure, so "24 coefficients per heater" is an inference).
- Numbers:
  - Optimized 1-to-24 routing: 2 pi shift at 46 mW on that route; extinction
    ratio 24 dB.
  - 2000 Haar-random unitaries after calibration: average amplitude fidelity
    99.7 %; one example at 99.57 %.
  - Average fiber-to-fiber insertion loss 4.35 dB (about 4.1 dB before
    pigtailing); coupler arms 1 mm, minimum bend radius 15 mm, footprint 15 x
    134 mm^2, waveguide pitch 82 um at the ports.
  - A heater held at 57 mW (2.5 pi) for 12 hours drifts upward by under 0.005
    %/h; total electrical power under 10 W for all tested unitaries.
- Use here: (U1) the calibrated parameter set (576 static phases, 552 splitting
  ratios, 13824 crosstalk coefficients, trained on 30000 random settings) is the
  upper bound on what a shared offset vector can be asked to resolve, and a
  random-power training design is the data recipe; (U2) the calibration route
  optimization is closed-loop and fringe based, so its quality differs from a
  model-only compile; (U3) a closed-loop-optimized 23-crossing route reaches 24
  dB extinction relative to the target output on this chip, which bounds the
  total leak of a healthy mesh to about 9 % (23 x 10^-2.4, an upper-bound
  reading of a figure that is not tabulated); (U4) per-input insertion loss is measured per port, so port
  efficiencies differ by design of the fiber array.

### 4. Thomas, Chabaud and Emeriau, classical shadows (Belenos hardware paragraph)

- Citation: H. Thomas, U. Chabaud, P.-E. Emeriau. "Shedding light on classical
  shadows: learning photonic quantum states." arXiv:2510.07240v2 (8 Oct 2025,
  v2 27 Mar 2026). https://arxiv.org/abs/2510.07240. Retrieved 2026-10-17.
  Depth: sections (Methods, hardware paragraphs "Hardware" for Ascella and
  Belenos).
- Summary. A classical-shadow protocol run on Ascella (12 modes) and Belenos
  (24 modes). Its Methods give the most specific published description of
  Belenos.
- Facts (Methods, paragraph g):
  - Temporal-to-spatial multiplexing by a resonantly driven Pockels-cell
    demultiplexer, "overall transmission exceeding 85%"; custom polarization
    control modules.
  - A 24-mode silica glass interferometer with 552 beam splitters integrated as
    directional couplers and 676 reconfigurable thermo-optic phase shifters,
    driven by custom low-noise current electronics.
  - "The circuit is calibrated using machine learning [Fyrillas et al.]. The
    processor implements a self-calibration strategy, which automatically
    recalibrates the photonic integrated circuit using periodically acquired
    data samples."
  - Detection: 16 polarization-resolved photon-number-resolving detectors, each
    with 28 interleaved pixels (two simultaneous photons per spatial mode
    resolvable by multi-trigger events), and 8 SNSPDs. Single-photon detection
    probability 90 to 92 %; two-photon detection probability about 78 %.
  - The demultiplexer citation is only "Quandela cloud (2025)"; no
    demultiplexer paper was found.
- Use here: (U1) current-driven heaters avoid the order-3 electric-crosstalk
  tensor of Fyrillas 2023 App. B, so a matrix phase model suffices; (U2)
  self-calibration from periodic data implies the effective mesh changes
  between calibrations; (U3) n/a; (U4) the detector banks differ (modes 0 to 15
  photon-number-resolving, modes 16 to 23 SNSPD), so efficiency and dark counts
  must be fitted per bank and per mode, not as one scalar.

### 5. Karooby et al., QSP on Belenos

- Citation: E. Karooby, M. Hakimi Heris, Y. Liu, Q. Gu. "Programmable
  nonlinear function synthesis on a photonic processor with quantum signal
  processing." arXiv:2609.14153v1 (12 Sep 2026). https://arxiv.org/abs/2609.14153.
  Retrieved 2026-10-17. Depth: sections (hardware error, Methods "Experimental
  platform").
- Summary. Dual-rail single-photon QSP sequences up to depth L = 11 on the
  24-mode Belenos, programmed on a Clements-style rectangular mesh. Hardware
  error is compared with the finite-depth approximation error.
- Facts: the circuit is fabricated in alumino-borosilicate glass with a 15 x 134
  mm^2 footprint (ref. 8 is Barzaghi); the directional couplers are fixed at a
  nominal 50:50; platform specifications give g2(0) = 0.013, indistinguishability
  0.902, overall system transmittance 0.058; phase-to-voltage conversion is
  handled by Quandela's transpilation (ref. 45 is Fyrillas et al.).
- Numbers: at L = 11 the hardware-induced mean squared error (experiment versus
  analytic QSP prediction) is 0.006 (STEP), 0.003 (ReLU), 0.003 (SELU); over
  accessible depths it lies between 1e-3 and 1e-2.
- Use here: (U1) a two-mode circuit on 24 modes keeps a 1e-3 to 1e-2 mean
  squared error against theory, a reference scale for a well-routed single
  photon; (U2) n/a; (U3) the paper reports the extra modes "left inactive" and
  does not quantify their leakage, so it gives no leakage figure to compare
  with; (U4) per-job platform metadata (g2, indistinguishability,
  transmittance) differ between papers (0.013, 0.902, 0.058 here; 0.019, 4.84 %
  in source 7; 0.019, 0.923 in source 6), so these values drift and must be
  read per job.

### 6. Lopez Carreno et al., photonic quantum reservoir processing

- Citation: J. C. Lopez Carreno, S. Swierczewski, A. Opala, A. Salavrakos, B.
  Pietka, M. Matuszewski. "Quantum and classical processing with photonic
  quantum machine learning." arXiv:2605.10471v1 (11 May 2026).
  https://arxiv.org/abs/2605.10471. Retrieved 2026-10-17. Depth: sections
  (Methods "Belenos architecture", "Mitigation of experimental errors").
- Facts: Belenos is described as a single-photon source, a 12-mode active
  demultiplexer with fiber delays, a 24-mode silica-glass chip, and detectors;
  "the architecture of the chip is a universal Bell-Walmsley interferometer
  [Bell and Walmsley]"; "the first 16 detectors corresponding to the first 16
  modes of the chip have polarization-resolved photon-number-resolving
  capabilities"; compilation is "an algorithm that is integrated into Perceval,
  and which employs machine learning techniques". Source figures at the time
  of the experiment: g2(0) = 0.019 +- 0.001, indistinguishability 0.923 +-
  0.007. An m-mode experiment on the 24-mode chip is run by injecting photons
  into the first modes and blocking transmission into the last modes by
  controlling the phases.
- Number: in-silico training with random perturbations of each unitary element
  drawn from a normal distribution of variance epsilon^2 gave best hardware
  accuracy at epsilon = 0.075, "consistent with the measured transpilation
  error in the Ascella QPU" (the perturbation definition is in the main text;
  the measurement is in the SI, not read).
- Conflict recorded: Karooby calls the mesh Clements-style rectangular, this
  source says Bell-Walmsley, and Barzaghi describes MZIs with two thermal
  shifters each (Clements-like). The repo decoder counts 276 MZIs, equal to
  24 x 23 / 2.
- Use here: (U1) an element-level transpilation error of about 0.075 per
  matrix element on Ascella sets an upper scale for the residual that a fitted
  offset vector has to explain; (U2) hardware-aware training with perturbations
  shows that a design robust to element perturbations beats seed picking when
  the unitary is free to choose; (U3) blocking by phases is the same "mirror"
  mechanism the repo uses, and its leakage is not quantified here; (U4) the
  first 16 modes are photon-number-resolving, so threshold-detector models are
  wrong for them.

### 7. Tully, Washburn and Simons, Walsh filters on Belenos (third party)

- Citation: E. Tully, J. Washburn, M. Simons. "Characterization of nested
  Walsh parity-check filters in a single-photon eight-mode register on a cloud
  photonic processor." arXiv:2606.18408v2 (16 Jun 2026).
  https://arxiv.org/abs/2606.18408. Retrieved 2026-10-17. Depth: sections
  (hardware, Table II, Table IX, systematics). Provenance caveat: an
  unrefereed preprint by authors outside Quandela; its numbers are recorded as
  reported and unreplicated.
- Summary. Eight logical modes of the 24-mode Belenos, circuits submitted
  through the default Perceval cloud compiler with no manual remapping.
  Readouts are normalized to postselected single-photon detections, so
  mode-independent loss divides out; discarded events include zero-photon,
  multi-photon and dark-count-flagged events.
- Facts and numbers:
  - Backend metadata: clock 4.94 MHz, g2(0) = 0.019, transmittance 4.84 %,
    HOM visibility above 90 %; software stack mosaiq-belenos 2.7.12,
    hardware-core 3.7.4, pcvl-worker 1.4.0, perceval-quandela 1.1.0,
    universalchipworker 1.7.0, exqalibur 1.1.1; campaign April 2026.
  - The compiler, not the user, assigns logical to physical modes; "run-to-run
    reassignment" is possible.
  - An 8-mode separator whose ideal dump-port probability is 0.125 measured
    0.188 +- 0.030 averaged over eight inputs (range 0.140 to 0.237); rms
    deviation from ideal 0.070, mean upward bias 50 %. This fixed-pattern bias
    is the dominant systematic.
  - Residuals of a soft-error calibration fit at the +-0.02 level; chi^2/dof
    about 24 against counting statistics; "compilation scatter" near 1e-3
    leakage and an order of magnitude across separately compiled circuits.
  - Neutral inputs leak 0.02 % to 1.1 % (mean 0.6 %) into the dump port.
  - HOM control across a recalibration window: visibility 90.7 % (dump
    probability 0.0073), 21.2 % (0.481, a factor of about 66 higher), restored
    about 91 % (0.0058).
  - Multi-photon postselection retains 99.9 % of detected events; discarded
    detected pairs 0.049 %.
- Use here: (U1) per-compile scatter and a fixed-pattern bias of about 0.07 rms
  on an 8-mode unitary are the Belenos-side residual to explain with an offset
  fit; (U2) separately compiled circuits scatter by an order of magnitude in
  leakage, which supports seed ensembles; (U3) a leakage that jumps 66-fold
  across a calibration episode shows that calibration state can by itself move
  a block's leakage from percent to tens of percent; (U4) the normalization
  that divides out mode-independent loss, and the dark-count flag, are the
  platform's own treatment.

### 8. Franco, Camillini and Galvao, interaction-free measurement on Ascella

- Citation: S. Franco, A. Camillini, E. F. Galvao. "Interaction-free
  measurement of multiple objects using a universal integrated photonic
  processor." arXiv:2604.04691v2 (6 Apr 2026); DOI 10.1088/2058-9565/ae8df9 as
  listed on arXiv. https://arxiv.org/abs/2604.04691. Retrieved 2026-10-17.
  Depth: sections (Sec. IV A, App. A 1 and A 2).
- Summary. One-photon experiments on the Ascella cloud. The paper reports that
  compilation or transpilation artefacts biased some circuits, with a bias that
  changed from one on-site calibration routine to the next, and mitigates it by
  ensemble averaging over equivalent circuits.
- Procedure (App. A 2): for each reflectivity setting, M = 40 equivalent
  circuits are submitted. Each carries a random phase drawn uniformly from [0,
  2 pi) on every mode just before detection. These phases leave the output
  probabilities unchanged but "randomize the initial parameters input to the
  compilation procedure", which helps the algorithm converge to a higher
  fidelity unitary. About 10^6 samples per circuit are taken, one estimate per
  circuit, then the mean over M = 40 with its standard error.
- Numbers: without mitigation some data points deviate "as large as 40 %
  relative error" from theory; the cause is attributed to poor convergence of
  the calibration routine, "for some circuits, the machine-learning iteration
  was converging to a set of phase shifter values that resulted in a lower
  fidelity unitary". The paper states the average coupler reflectivity as 56.7
  % (from source 1) and notes that dark counts could not be characterized on
  the cloud. Poisson noise at about 10^6 samples was insignificant against the
  other errors.
- Use here: (U1) the bias depends on the calibration session, so an offset fit
  must be keyed to a session; (U2) this is the direct precedent for seed
  ensembles: random output phases change the compile start and not the ideal
  distribution, and ensemble averaging removed a 40 % bias; (U3) systematic
  deviations of tens of percent on a one-photon, few-mode experiment trace to
  compile convergence, a candidate cause for a block that loses half its light;
  (U4) dark counts were not separable from the cloud, so they must be bounded
  from dedicated no-signal jobs.

### 9. Forster et al., subcircuit compilation

- Citation: T. Forster, Y. Stade, A. Fyrillas, J. Senellart, L. Burgholzer, R.
  Wille. "Handling Imperfections in Subcircuit Compilation for Linear Optical
  Quantum Computing." arXiv:2609.13379v1 (11 Sep 2026; TU Munich and Quandela).
  https://arxiv.org/abs/2609.13379. Retrieved 2026-10-17. Depth: sections
  (motivation, method, evaluation, Table I).
- Summary. Current compilers embed a small target unitary U_sub into a
  circuit-sized unitary, which spreads the computation across the whole mesh
  and connects the same input and output ports. The proposed compiler places a
  compact computation zone, routes photons to it through BAR and CROSS MZI
  states, and weights input and output port transmissions against routing
  loss, optimizing the coincidence rate.
- Procedure: the mesh becomes a directed acyclic graph with edge weights equal
  to routing loss and logarithmic port-transmission costs; a shortest-path
  search picks the route; routing fixes only the internal phase difference of
  each MZI, so the common phase sum stays free for the optimizer; phases are
  then compiled by gradient descent on the overlap. The paper states that BAR
  is typically realized more accurately than CROSS because fabrication errors
  are spatially correlated and the two couplers of an MZI have similar
  reflectivities.
- Numbers (simulation only, Perceval 1.1.0, 5 Haar-random targets per cell,
  coupler reflectivities taken from "an actual Quandela device for the
  24-waveguide circuit", port transmissions drawn uniformly from 0.7 to 1.0):
  - Phase noise 0, 15, 30 mrad. For a 4-dimensional subcircuit on a 24-mode
    circuit the baseline TVD is 7.9e-6, 2.7e-2, 5.2e-2 and the proposed method
    gives 2.7e-3, 2.3e-2, 3.5e-2.
  - Coincidence rate at zero phase noise 0.562 to 0.844 (4 of 24) and 0.265 to
    0.425 (8 of 24); the largest absolute gain in the table is +0.332 and the
    abstract states "up to plus 33.2%".
  - Compilation time 0.38 to 3.41 min.
- Use here: (U1) the baseline TVD scales roughly as 1.7 to 1.8 per radian of
  per-heater phase noise on a 4-of-24 embedding (derived here from 2.7e-2 at
  15 mrad and 5.2e-2 at 30 mrad), a direct sensitivity for a shared-offset
  residual; (U2) route and zone choice move the coincidence rate by tens of
  percent, so a placement search beats picking among equivalent embeddings;
  (U3) CROSS routing leaks more than BAR in current hardware, so a photon
  routed through many CROSS states is the first suspect; (U4) the optimizer
  already weights input and output port transmissions, which the cloud
  compiler is not documented to do.

### 10. Mezher and Mansfield, photonic quality factor

- Citation: R. Mezher, S. Mansfield. "Assessing the quality of near-term
  photonic quantum devices." arXiv:2202.04735v1 (9 Feb 2022; Quandela).
  https://arxiv.org/abs/2202.04735. Retrieved 2026-10-17. Depth: sections
  (noise model, loss test).
- Summary. A boson-sampling-based certification with a single-number metric
  (Photonic Quality Factor, the largest number of input photons that passes all
  tests) built on photon loss and pairwise distinguishability.
- Model: uniform loss lambda per mode, commuted to the input (assumptions A1,
  A2); distinguishability D_ij = x + (1 - x) delta_ij, fidelity F = x^2 (A3,
  A4); loss test: estimate lambda from the distribution of lost photons, P(l) =
  C(n, l) (1 - lambda)^(n - l) lambda^l, lambda_est = sum_l l P(l) / n, and
  require lambda <= o(1) in n. The authors state they "will not consider errors
  due to imperfect calibration of optical components such as beam splitters",
  dark counts or cross-talk. Sufficient scaling: loss per mode o(1) and
  fidelity (1 - o(1/n^6))^2.
- Use here: (U1) n/a, calibration errors are excluded; (U2) n/a; (U3) the
  binomial lost-photon model is the baseline against which a photon that
  leaves the block (not lost) is distinguished; (U4) the loss test estimates a
  mode-uniform lambda and says nothing about dark counts.

### 11. Heurtel et al., Perceval

- Citation: N. Heurtel, A. Fyrillas, G. de Gliniasty, R. Le Bihan, S. Malherbe,
  M. Pailhas, E. Bertasi, B. Bourdoncle, P.-E. Emeriau, R. Mezher, L. Music, N.
  Belabas, B. Valiron, P. Senellart, S. Mansfield, J. Senellart. "Perceval: A
  Software Platform for Discrete Variable Photonic Quantum Computing."
  Quantum 7, 931 (2023). arXiv:2204.00602v3. https://arxiv.org/abs/2204.00602.
  Retrieved 2026-10-17. Depth: sections (Processor and Circuit classes).
- Facts: the Circuit class composes components, computes the unitary of a
  circuit and decomposes a unitary into user-defined components; the Processor
  source model tunes transmittance, multiple-photon emission probability and
  indistinguishability; detectors can be number-resolving or threshold; the
  circuit can include non-unitary (lossy) components. The paper contains no
  description of exqalibur's CircuitOptimizer or of the cloud compile
  internals.
- Use here: (U1) the Circuit class is the forward model for the offset fit;
  (U2) n/a; (U3) lossy components model leakage as loss when needed; (U4) the
  source and detector parameters (transmittance, g2, indistinguishability,
  detector type) are the place to put efficiency and dark-count nuisance
  terms.

### 12. Quandela product page and compile guide (non-arXiv)

- Citation: Quandela, "Belenos" product page, https://www.quandela.com/qpus/belenos/,
  retrieved 2026-10-17 (HTML read directly). Quandela Cloud user guide,
  "Compilation", captured in this repository as
  `docs/notes/quandela/guide/user-guide/04-compilation.md` (retrieved
  2026-10-17 from cloud.quandela.com). Depth: full.
- Product page facts (vendor figures, no method stated): product line
  MOSAIQ-12; 24 modes; QOPS 576; universal chip design; 1-qubit gate fidelity
  (99.6 +- 0.1) %; 2-qubit gate fidelity (99.0 +- 0.8) %; read-out fidelity 99
  %; 12 fully entangled qubits; 8 kW; air-cooled.
- Compile guide facts: the compile has three phases (input state adaptation by
  routing permutations to the connected source modes; circuit transpilation;
  detection configuration). Transpilation converts the circuit to its unitary
  and "will attempt to find a sub-circuit able to encode the unitary as
  accurately as possible, while the unused modes parameters will be configured
  to act as complete mirror to avoid any transmission between the modes of
  interest and the extraneous modes." The guide adds that fidelity "improves on
  a larger size than the one of the unitary (due to redundancy of parameters
  that can compensate for potential manufacturing defects)" at the price of
  lower total transmission. The exqalibur CircuitOptimizer is not documented
  in these pages.
- Use here: (U1) the mirror parameters are part of the 574 phases, so their
  offsets enter the same fit; (U2) the guide itself says redundancy changes
  fidelity, so block placement and seeds are legitimate degrees of freedom;
  (U3) "complete mirror" is a bar-state chain whose leakage floor is
  sin^2(alpha1 - alpha2) per MZI plus a phase-error term; (U4) vendor
  read-out fidelity 99 % has no stated method and no per-mode breakdown.

---

## Part II. Characterization from counts (topic a)

### 13. Laing and O'Brien, super-stable tomography

- Citation: A. Laing, J. L. O'Brien. "Super-stable tomography of any linear
  optical device." arXiv:1208.2868v1 (14 Aug 2012).
  https://arxiv.org/abs/1208.2868. Retrieved 2026-10-17. Depth: sections
  (method, noise analysis; Eq. 12 read from the page image).
- Summary. A constructive reconstruction of the m x m unitary from one-photon
  count rates and two-photon (HOM-type) visibilities. It is independent of
  input and output port efficiencies and insensitive to fluctuating phases
  between inputs and between outputs. Amplitudes come from one-photon data;
  phases from specific two-photon ensembles. The matrix is real-bordered
  (first row and column real and positive) and Im(M_22) >= 0 fixes the
  conjugation ambiguity. The two-photon count is about 2 m^2 of about m^4
  possible.
- Equations (plain text):
  - R_jk = S_k s_k T_jk r_j (rate = source x input coupling x transition
    probability x detection efficiency).
  - X_ghjk = R_jk R_gh / (R_jh R_gk) = tau_jk tau_gh / (tau_jh tau_gk) (Eq. 5,
    with x = sqrt(X) and tau = sqrt(T)); input and output efficiencies cancel.
  - V_ghjk = (C - Q) / C = -2 cos(a_jk - a_jh - a_gk + a_gh) tau_jk tau_jh tau_gk
    tau_gh / (tau_jk^2 tau_gh^2 + tau_gk^2 tau_jh^2); with y = x + 1/x,
    cos(a_jk - a_jh - a_gk + a_gh) = -V y / 2 (Eq. 6); the signs follow Eq. 7.
  - Unitary completion: orthonormality of the first column and row.
- Noise result (Eq. 12, from the page image): average reconstruction fidelity F
  ~ exp(-lambda sqrt(delta)) with lambda ~ (m - 3)/5, where counts and
  visibilities are multiplied by (1 + epsilon), delta = 3 sigma of epsilon,
  1000 Haar unitaries per point; valid down to F ~ 85 %; m = 4 tested to delta =
  5 % and m = 20 to delta = 0.25 %.
- Derived here, an extrapolation beyond the tested m <= 20: at m = 24, lambda =
  4.2, so F = 0.99 needs delta ~ 6e-6 (relative count error 2e-6, about 3e11
  counts per rate) and F = 0.9 needs delta ~ 6e-4 (about 2e7 counts per rate).
- Use here: (U1) the border-plus-completion estimator is not suited to a
  574-parameter offset fit at one-photon count budgets; use a model-based fit
  and keep Laing's gauge (real border) for reporting; (U2) n/a; (U3) the ratio
  X is a leak test free of port efficiency; (U4) X cancels input coupling and
  detector efficiency but needs at least two inputs, so efficiency separation
  comes from varying the input mode across one-photon jobs.

### 14. Rahimi-Keshari et al., direct characterization

- Citation: S. Rahimi-Keshari, M. A. Broome, R. Fickler, A. Fedrizzi, T. C.
  Ralph, A. G. White. "Direct characterization of linear-optical networks."
  Optics Express 21(11), 13450-13458 (2013). arXiv:1210.6463v3 (24 Oct 2012, v3
  31 May 2013). https://arxiv.org/abs/1210.6463. Retrieved 2026-10-17. Depth:
  sections (method, experiment, start of the lossy-network section).
- Summary. A laser and photodetectors suffice. Moduli come from single-input
  intensities and phases from a two-input coherent state with a swept relative
  phase, with the first row and column as a phase reference; 2N - 1
  configurations give all nontrivial parameters; a 6 x 6 fused-fiber network
  was characterized and verified by two-photon interference.
- Equations: a_j^dagger = sum_k M_jk b_k^dagger; r_jk = sqrt(I_k / I) (Eq. 3);
  for input pair (1, j) with relative phase phi, I_k = I [r_1k^2 + r_jk^2 + 2
  r_1k r_jk cos(phi + theta_jk)] for k != 1 (Eq. 6), I_1 = I [r_11^2 + r_j1^2 +
  2 r_11 r_j1 cos(phi)] (Eq. 5); the phase is read at the intensity maximum,
  theta_jk = 2 pi - phi (Eq. 7). Parameter count (N - 1)^2 + N^2 after absorbing
  the 2N - 1 unobservable phases into D(mu) M' D(nu); moduli alone do not fix
  the phases for N > 3. Two-photon check: Q = |M_ik M_jl + M_il M_jk|^2 /
  (1 + delta_ij) (indistinguishable), C = |M_ik M_jl|^2 + |M_il M_jk|^2
  (distinguishable), visibility V = (C - Q)/C.
- Use here: (U1) the count of observable parameters and the gauge (2N - 1)
  carry over to the offset fit; (U2) n/a; (U3) one-input intensities give
  moduli only, so a photon prepared in a superposition of two inputs by an
  on-chip splitter plays the role of the two-input coherent probe and exposes
  phase errors that single-input counts miss; (U4) intensity ratios between
  outputs cancel a common efficiency, absolute efficiencies do not.

### 15. Dhand, Khalid, Lu and Sanders, accurate and precise characterization

- Citation: I. Dhand, A. Khalid, H. Lu, B. C. Sanders. "Accurate and precise
  characterization of linear optical interferometers." J. Opt. 18, 035204
  (2016). arXiv:1508.00283v2 (2 Aug 2015, v2 2 Mar 2016).
  https://arxiv.org/abs/1508.00283. Retrieved 2026-10-17. Depth: sections
  (abstract, introduction, scaling and comparison passages; derivations not
  read in full). Numerical simulation only.
- Summary. An extension of the Laing and O'Brien procedure that corrects
  systematic error from spatiotemporal and polarization mode mismatch with a
  calibration step, fits coincidence data to curves computed from measured
  source spectra (not Gaussians), puts error bars on the matrix elements by
  bootstrapping, and cuts experimental time with a scattershot source.
- Numbers: holding the standard deviation of the amplitude and phase estimates
  fixed requires O(m) and O(m^2) photons respectively, so the time scales as
  O(m^4); scattershot collection of (m - 1)^2 data sets in parallel reduces it
  to O(m^2). The procedure averages the ratio of single-photon detections over
  runs, not the ratio of averages, which tolerates fluctuating source
  brightness.
- Use here: (U1) the O(m^4) time and the bootstrap error bar bound what a count
  budget can resolve at m = 24; (U2) n/a; (U3) n/a; (U4) the averaged-ratio
  estimator tolerates fluctuating source and coupling, which is the cloud
  situation.

### 16. Fyrillas et al., clear-box machine-learning characterization

- Citation: A. Fyrillas, O. Faure, N. Maring, J. Senellart, N. Belabas.
  "Scalable machine learning-assisted clear-box characterization for
  optimally controlled photonic circuits." Optica 11(3), 427-436 (2024).
  arXiv:2310.15349v2 (23 Oct 2023, v2 22 Feb 2024).
  https://arxiv.org/abs/2310.15349. Retrieved 2026-10-17. Depth: sections
  (Secs. I-V, Apps. B, D, E, F read; Apps. A, C, G, H skimmed).
- Summary. A virtual replica of the chip is trained by gradient descent so that
  its predicted output intensity distributions match measured ones. The
  replica holds a phase-voltage matrix and passive phases, coupler
  reflectivities and port transmissions. Data are (voltages, input port,
  normalized 12-vector of output intensities). A laser and power meters suffice
  and a single-photon source with single-photon detectors is equivalent, with
  more noise; the paper's hardware test used single photons. The same model
  drives a compile step with detector relabeling and a crosstalk-compensating
  phase-to-voltage solver. This is the method behind Ascella and, by the
  citations in sources 4 and 5, behind Belenos.
- Model and estimator (plain text):
  - Coupler: [[sqrt(R), i sqrt(1-R)], [i sqrt(1-R), sqrt(R)]] (Eq. 1). Input
    port i with transmission T: column i of U multiplied by sqrt(T); output
    transmissions scale rows; max of T_out normalized to 1.
  - Phase-voltage: phi = sum_{k>=1} C_k V.^k + c0 (Eq. 2); thermo-optic heaters
    need only k = 2, an optional k = 4 term accounts for heater resistance
    changing with temperature; the paper uses phi = C2 V.^2 + c0.
  - Prediction: p-hat(V, i) from U(phi-hat, R-hat, T-in, T-out), normalized to
    sum 1. Loss: mean squared error between measured p and p-hat, optimized by
    Adam (PyTorch), one learning rate per parameter type, 80/20 train/test.
  - Initialization: C2 = 0, c0 = 0, couplers at target reflectivity, all
    transmissions 1. Stage order: V-IFM (per-heater voltage fringe sweeps for
    initial diagonal of C2 and c0) -> ML -> phi-IFM (phase sweeps through the
    learned relation that update c0 from the offset between measured and
    expected fringes) -> repeat until the minimum test MSE stops improving ->
    ITM (input transmission measurement).
  - c0 stays fixed during the ML stage "because the model usually converges to
    a local minimum for the passive phases"; phi-IFM updates it.
  - Metrics: TVD(p, q) = (1/2) sum_i |p_i - q_i|; fidelity F(U, V) =
    |Tr(U^dagger V)| / m, with F = 1 iff U = e^{i theta} V; amplitude fidelity
    Fa(P, Q) = Tr(P^T Q) / m for P = |U|, Q = |V|, and F <= Fa(|U|, |V|)
    (Eq. D9). Empirically Fa ~ 1 - TVD_test^2.
  - Compile: "Clements decomposition" assumes R = 0.5; "corrected Clements"
    and "local correction" (Bandyopadhyay, source 26) use the learned R; "global
    optimization" minimizes C = 1 - F^2 by gradient descent. Prior detector
    relabeling samples 32 random permutations out of m! and keeps the best,
    which raises the fidelity of every compile method; a bar state with R !=
    0.5 yields a perfect cross after relabeling the two outputs.
  - Electric crosstalk (App. B): a shared ground makes the phase a quadratic
    form in all voltages (order-3 tensor), growing the data need from n_PS^2 to
    n_PS^3; current-controlled heaters avoid it.
- Numbers:
  - 12-mode Si3N4 Clements chip, 126 thermo-optic phase shifters, 132
    couplers, characterization about 18 hours.
  - Training samples of the order of the parameter count (data-to-parameter
    ratio 1; n_PS^2 + #couplers + #modes).
  - Model-versus-data TVD_test about 2.9 % (train 2.2 %), against about 0.1 %
    expected from photon-counting noise, which signals unmodeled imperfections;
    circuit amplitude fidelity 99.92 +- 0.02 %.
  - 100 Haar-random 12 x 12 unitaries: Fa = 99.77 +- 0.04 %, 99.85 +- 0.04 %
    with estimated output losses compensated; solver precision 0.1 mrad.
  - Average coupler reflectivity far from 0.5 because source and fabrication
    wavelengths are 11 nm apart; a systematic error of -250 mrad on the measured
    passive phase of an external shifter at that reflectivity (App. C).
  - 24-mode simulation: coupler reflectivities 0.52 +- 0.01, crosstalk 0.5 %,
    about 300000 training samples, 1500 epochs per ML stage, TVD_test = 1e-3
    after 6 iterations.
  - Prior work in the paper's Table I: black-box NN 3 modes 2 phase shifters
    (2400 samples); gray-box NN 3 modes 4 phase shifters; Haar unitary
    infidelity 9.6 % (12-mode, passive phases ignored), 1.3 % (6-mode), 2.6 %
    (20-mode, 380 shifters); this work 0.23 % raw.
- Use here: (U1) the estimator, its stage order, the c0 local-minimum warning
  and the one-sample-per-parameter data rule are the published template for
  fitting a shared offset vector; because meshes are known the fit reduces to
  c0 (and R, T_out as nuisance), and the V-IFM or phi-IFM initialization has an
  analogue in a one-photon fringe sweep over a single phase; (U2) 32-permutation
  best-of selection on a known objective is the published precedent for
  choosing among equivalent compilations; (U3) the replica predicts the full
  output distribution, so a leak map is a residual against the replica; (U4)
  T_in and T_out are fitted nuisance parameters and p / T_out compensates
  output loss, but dark counts are not modeled and must be added.

### 17. Fyrillas et al., induced phase shifters and crosstalk mitigation

- Citation: A. Fyrillas, N. Heurtel, S. Piacentini, N. Maring, J. Senellart,
  N. Belabas. "Resource-efficient crosstalk mitigation for the high-fidelity
  operation of photonic integrated circuits with induced phase shifters."
  arXiv:2506.05988v1 (6 Jun 2025). https://arxiv.org/abs/2506.05988. Retrieved
  2026-10-17. Depth: sections (Secs. II-V, Methods; appendices skimmed).
- Summary. The ML characterization of source 16 recovered unphysical long-range
  crosstalk. The paper models crosstalk on bare waveguide sections as
  "induced" phase shifters, builds an extended rectangular crosstalk matrix,
  proves when induced shifters can be eliminated, and gives a graph criterion
  for crosstalk-robust meshes.
- Equations: restricted model phi = C2(res) V.^2 + c0(res), C2 of size n_CPS x
  n_CPS (controlled shifters); extended model phi(ext) = C2(ext) V.^2 + c0(ext)
  with C2(ext) of size n_PS x n_CPS, nonnegative entries, induced-shifter
  passive phases set to 0 by convention. Theorem 1 (row deletion): if for an
  induced shifter k there is an invariant transformation phi_i -> phi_i +
  alpha_i phi_k (i != k), phi_k -> 0, then R_i -> R_i + alpha_i R_k and row k
  is deleted. Theorem 2: a mesh is crosstalk-robust iff its pruned graph is
  acyclic; Reck, Clements and Bell-Walmsley meshes are robust. Phase-invariant
  input and output ports (Fock inputs, intensity detectors) allow shifters
  there to be discarded.
- Numbers:
  - Simulation, 6-mode SiN chip with trenches: a heater at 14 V (2 pi on its own
    waveguide) induces measurable phase on neighboring bare waveguides;
    ignoring induced shifters limits amplitude fidelity to 99.3 %.
  - Simulation, 12-mode Clements, pseudo-inverse voltage solution of the
    extended matrix: 6 mrad error on controlled phases, 140 mrad residual on
    induced shifters, Fa = 97.7 +- 0.6 %.
  - Simulated crosstalk law used: off-diagonal coefficient f(d) = 0.5/d^2 for d
    != 0 and 0.02 for d = 0, in layout units (10 units between waveguides);
    diagonal 0.034 rad/V^2; crosstalk strength is coefficient divided by the
    average diagonal coefficient (Fig. 7 caption), so nearest neighbors sit near
    2 % of the self-heating coefficient.
  - Hardware, 12-mode chip with an attenuated laser: TVD_test 7.5 % (restricted
    model) against 2.9 % with a true single-photon source in source 16; Fa 98.7
    +- 0.2 % (restricted) and 98.6 +- 0.2 % (extended, reduced), so the
    extended model does not improve hardware control here.
  - Training: about 16000 samples and 4000 test samples; parameters about
    16000 (restricted) and about 32000 (extended); the extended model needs no
    more samples. A 12-mode model trains in 235 ms (restricted) and 302 ms
    (extended) per epoch on a GPU.
- Use here: (U1) gauge directions are explicit here: phase-invariant input and
  output ports can be dropped, so fix those offsets and fit the rest; induced
  shifters mean "per-heater offset" can absorb crosstalk from unmodeled
  neighbors; (U2) n/a; (U3) a crosstalk-robust mesh (acyclic pruned graph) is
  the condition under which a phase error can be traced to a controlled heater;
  (U4) n/a.

### 18. Pentangelo et al., laser-written universal photonic processors

- Citation: C. Pentangelo, N. Di Giano, S. Piacentini, R. Arpe, F. Ceccarelli,
  A. Crespi, R. Osellame. "High-fidelity and polarization insensitive
  universal photonic processors fabricated by femtosecond laser writing."
  Nanophotonics 13(12), 2259-2270 (2024); DOI 10.1515/nanoph-2023-0636.
  arXiv:2310.19718v1 (30 Oct 2023). https://arxiv.org/abs/2310.19718.
  Retrieved 2026-10-17. Depth: sections (Secs. II-V; supplement not read).
- Summary. The closest published platform analog to Belenos: 6-mode
  femtosecond-laser-written mesh in glass with trenches and chromium
  microheaters, current-driven, calibrated with a node-isolation procedure
  and a crosstalk model restricted to vertically adjacent MZIs.
- Model (Eqs. 2-4): P_out = (1 + cos(theta)) / 2 at the cross port;
  theta = theta0 + alpha_I I^2 (1 + beta I^2) per shifter, where theta0 is the
  offset from fabrication tolerance and beta accounts for heater resistance
  changing with temperature; with crosstalk theta_i = theta_0,i + sum_j alpha_ij
  I_j^2 (1 + beta_j I_j^2). Horizontal neighbors are millimeters apart and
  vertical neighbors 160 um apart, so alpha_ij is kept only for vertically
  adjacent MZIs. Calibration uses coherent light and a node-isolation
  algorithm: already calibrated MZIs are set to straight, crossing or balanced
  states so that the MZI under test is surrounded by fully reflective or
  transmissive paths.
- Numbers: average Haar amplitude fidelity 0.9979 (785 nm UPP A, 1000
  unitaries) and 0.9970 (1550 nm UPP B); 30 random switching matrices 0.9963
  +- 0.0009 (A) and 0.9956 +- 0.0016 (B); 2 pi power 39 mW (A) and 63 mW (B); loss under 3 dB (2.5 dB);
  Nelder-Mead on the amplitude infidelity of a single unitary raised 0.9936 to
  0.9997 (repeat measurements of one unitary agree to about 0.9998, the
  reproducibility limit). Monte Carlo with phase noise uniform on epsilon_max x [-pi, pi]:
  epsilon_max = 0.034 reproduces the measured Fa = 0.9978 +- 0.0008,
  with true Frobenius fidelity F = 0.9921 +- 0.0029; the paper concludes the
  calibration errors are below +-0.1 rad. Amplitude fidelity is biased: E[Fa]
  ~ pi/4 for unrelated Haar unitaries as N grows, and F = 1 - (tau_ampl^2 +
  tau_angle^2)/(2N) <= Fa.
- Use here: (U1) the model theta_i = theta_0,i + sum_j alpha_ij I_j^2(1 + beta_j
  I_j^2) with sparse alpha is the closest published form for Belenos heaters
  and says which crosstalk terms to keep; a calibration residual under 0.1 rad
  is the benchmark for a fitted offset vector; (U2) per-unitary optimization
  of currents against measured counts is a closed-loop alternative to seed
  picking; (U3) amplitude fidelity is a ceiling on true fidelity (0.9978
  against 0.9921), so a one-photon test cannot certify unitary conformance;
  (U4) n/a.

### 19. Taballione et al., 20-mode processor

- Citation: C. Taballione, M. Correa Anguita, M. de Goede, P. Venderbosch, B.
  Kassenberg, H. Snijders, N. Kannan, W. L. Vleeshouwers, D. Smith, J. P.
  Epping, R. van der Meer, P. W. H. Pinkse, H. van den Vlekkert, J. J. Renema.
  "20-Mode Universal Quantum Photonic Processor." Quantum 7, 1071 (2023).
  arXiv:2203.01801v5 (3 Mar 2022, v5 26 Jul 2023).
  https://arxiv.org/abs/2203.01801. Retrieved 2026-10-17. Depth: sections
  (Sec. 3.1, Table 1).
- Summary and numbers: a Si3N4 20-mode mesh with 380 tunable elements, cooled by
  a Peltier element. Phase-voltage relations are characterized with coherent
  light through a fiber switch; the control software compensates crosstalk. 1000
  Haar-random matrices reach amplitude fidelity (97.4 +- 0.5) %; 190
  permutation matrices (99.5 +- 0.2) %; insertion loss (2.9 +- 0.2) dB; HOM
  visibility 98 %; performance stable for at least 6 months without
  recalibration; amplitude fidelity defined as F = Tr(|U^dagger| |U_exp|) / N.
- Use here: (U1) 20-mode Si3N4 residuals are an order of magnitude larger than
  the 24-mode glass chip's, which shows that fidelity at m ~ 20 depends on
  calibration quality, not on mode count alone; (U2) n/a; (U3) permutation
  targets (all MZIs at bar or cross) score 99.5 % against 97.4 % for Haar, so
  bar and cross routing is the easier case for a calibrated mesh; (U4) n/a.

---

## Part III. Error models and depth scaling (topic b)

### 20. Clements et al., rectangular mesh

- Citation: W. R. Clements, P. C. Humphreys, B. J. Metcalf, W. S. Kolthammer,
  I. A. Walmsley. "An Optimal Design for Universal Multiport Interferometers."
  Optica 3(12), 1460-1465 (2016). arXiv:1603.08788v2 (29 Mar 2016).
  https://arxiv.org/abs/1603.08788. Retrieved 2026-10-17. Depth: sections
  (decomposition, loss tolerance).
- Summary. The rectangular mesh of N(N - 1)/2 MZIs has optical depth N against
  2N - 3 for the triangular mesh and, for equal loss per beam splitter, higher
  fidelity because path lengths are balanced. The paper treats loss only; it
  gives no model of coupler imbalance or phase error.
- Equations: T_mn(theta, phi) = [[e^{i phi} cos theta, -sin theta], [e^{i phi}
  sin theta, cos theta]] on modes m, n, a lossless splitter of reflectivity cos
  theta with an input phase, realized by an MZI of two 50:50 couplers; U =
  D prod T, nulled diagonal by diagonal; fidelity F = | tr(U^dagger U_exp) /
  sqrt(N tr(U_exp^dagger U_exp)) |^2 (Eq. 6, squared, read from the page
  image) removes balanced loss. The loss study uses 500 random unitaries per
  point. Figure 3 (read approximately from the plot, not from text): at 0.2 dB
  per beam splitter the rectangular mesh stays above about 0.998 fidelity up
  to size 50 while the triangular mesh falls to about 0.82; for 20 x 20 at 1.0
  dB per beam splitter the rectangular mesh keeps about 0.975 and the
  triangular about 0.54.
- Use here: (U1) n/a; (U2) n/a; (U3) a photon crossing a column of the
  rectangular mesh meets depth N = 24 MZIs, which sets the number of leakage
  opportunities (derived below); (U4) balanced loss does not change the
  fidelity metric, unbalanced loss does, which supports fitting output
  transmissions separately.

### 21. Burgwal et al., imperfect network and random unitaries

- Citation: R. Burgwal, W. R. Clements, D. H. Smith, J. C. Gates, W. S.
  Kolthammer, J. J. Renema, I. A. Walmsley. "Using an imperfect photonic
  network to implement random unitaries." Opt. Express 25(23), 28236-28245
  (2017); arXiv title "Implementing random unitaries in an imperfect photonic
  network," arXiv:1704.01945v1 (6 Apr 2017).
  https://arxiv.org/abs/1704.01945. Retrieved 2026-10-17. Depth: sections
  (results and optimization).
- Summary. A numerical study with static couplers drawn from N(0.5, sigma). An
  MZI with unbalanced couplers cannot reach full reflection or transmission;
  Haar-random targets need most MZIs near low reflectivity, so a fixed sigma
  limits the fidelity of large meshes.
- Numbers: the average required reflectivity of a 20-mode Haar mesh is 0.18, the
  mesh center has no values above 0.4 in the sample, and the effect sharpens as
  size grows; at state-of-the-art tolerance sigma = 0.025 a 50-mode mesh is
  limited to fidelity 0.999, equivalent to single-photon probabilities off by
  2 % on average and by up to 25 % at maximum; the number of at-risk MZIs
  scales as N^2 for Haar targets and as N for the Fourier transform; numerical
  optimization with one extra layer of couplers raises fidelity to the 1e-4
  infidelity level for small networks.
- Use here: (U1) n/a; (U2) n/a; (U3) block-plus-mirror jobs place most MZIs at
  extreme states, the regime where coupler imbalance sets a hard floor, so Haar
  scaling understates or misplaces the error; (U4) n/a.

### 22. Russell et al., direct dialling of Haar random unitaries

- Citation: N. J. Russell, L. Chakhmakhchyan, J. L. O'Brien, A. Laing. "Direct
  dialling of Haar random unitary matrices." New J. Phys. 19, 033007 (2017);
  DOI 10.1088/1367-2630/aa60ed. arXiv:1506.06220v2 (20 Jun 2015, v2 6 Mar
  2017). https://arxiv.org/abs/1506.06220. Retrieved 2026-10-17. Depth:
  sections (pdfs and error-coverage passages).
- Summary. The independent probability densities of the MZI phases that
  generate a Haar-random unitary: the density of the internal phase at
  position index (n - i) is proportional to cos(theta/2) sin(theta/2)^(2(n - i) -
  1) (Eq. 24; sin and cos swap for a directional-coupler convention, Eq. 25),
  with external phases uniform. Components at the center of the rectangular
  scheme are the most error-sensitive. Coverage of unitary space falls with
  size when reflectivities are restricted to [|e|, 1 - |e|]; the figure uses
  sigma of e from 1e-4 to 20e-4.
- Use here: (U1) n/a; (U2) n/a; (U3) the position-dependent densities say which
  MZIs sit near bar or cross for a given target, hence where imbalance bites;
  (U4) n/a.

### 23. Fldzhyan, Saygin and Kulik, error-tolerant design

- Citation: S. A. Fldzhyan, M. Yu. Saygin, S. P. Kulik. "Optimal design of
  error-tolerant reprogrammable multiport interferometers." Opt. Lett. 45(9),
  2632-2635 (2020). arXiv:1910.13001v2 (28 Oct 2019, v2 30 May 2020).
  https://arxiv.org/abs/1910.13001. Retrieved 2026-10-17. Depth: sections
  (MZI error formula and design description).
- Summary. The MZI mesh needs balanced static couplers for universality, and the
  harm grows with size. The paper proposes a mesh of single static couplers and
  one phase shifter per block, tolerant to coupler transmissivity from about
  1/2 to about 4/5; the fraction of unimplementable matrices falls rapidly with
  size. A MZI mesh has N^2 - 1 phase shifts, the number of independent
  parameters of a unitary.
- Equation: MZI power transmissivity tau = |b|^2 = cos^2(phi1) cos^2(alpha1 +
  alpha2) + sin^2(phi1) sin^2(alpha1 - alpha2), with alpha_i the coupler
  imbalances. Rerouting port 1 to port N needs all diagonal MZIs in the cross
  state; the paper states that unit transmissivity needs alpha1 = alpha2 = 0.
  Derived here: at phi1 = 0 the formula gives 1 when alpha1 + alpha2 = 0, so
  opposite-sign imbalances also reach full transmission; with same-sign
  imbalance the floor is sin^2(alpha1 + alpha2), matching the conventions block.
- Use here: (U1) n/a; (U2) n/a; (U3) the formula gives the per-MZI leak of a
  routed photon from the retained coupler angles; (U4) n/a. The design cannot
  be applied to the fabricated MZI mesh.

### 24. Hamerly, Bandyopadhyay and Englund, rectangular self-configuration

- Citation: R. Hamerly, S. Bandyopadhyay, D. Englund. "Accurate
  Self-Configuration of Rectangular Multiport Interferometers." Phys. Rev.
  Applied 18, 024019 (2022). arXiv:2106.03249v2 (6 Jun 2021, v2 1 Dec 2022).
  https://arxiv.org/abs/2106.03249. Retrieved 2026-10-17. Depth: sections
  (algorithm summary, results, Discussion, Appendix D; Eq. 2 and the threshold
  read from page images).
- Summary. A configuration algorithm for the Clements mesh that needs only
  external sources and coherent detectors: it zeroes elements of V^dagger U
  W^dagger diagonal by diagonal from physical measurements and initializes all
  MZIs near cross. The corrected matrix error scales quadratically below the
  uncorrected error.
- Error model and equations (plain text): MZI with splitter errors alpha, beta
  and arm phase errors psi_i: T -> S(pi/4 + beta) diag(e^{i(theta + psi1)},
  e^{i psi2}) S(pi/4 + alpha) diag(e^{i(phi + psi3)}, e^{i psi4}), with S(x) =
  [[cos x, i sin x], [i sin x, cos x]] (Eq. 8). Metric E = <||Delta U||>_rms /
  sqrt(N), the average relative error per element. Uncorrected: each MZI adds
  sqrt(2) sigma, so E0 = sqrt(2N) sigma (errors add in quadrature across O(N)
  depth); with phase errors E0 = sqrt(2N (sigma_ph^2 + sigma_bs^2)). Corrected:
  Ec = sqrt(2/3) N sigma^2 = E0^2 / sqrt(6) (Eq. 2, page image). Exact
  correction holds while the coverage of unitary space is near 1, roughly N^3
  sigma^2 < 3. Phase errors are exactly correctable by a one-time calibration;
  without it self-configuration works while sqrt(N) sigma_ph is of order 1,
  with a sharp threshold sigma_ph ~ 3/sqrt(N) and a practical condition N
  sigma_ph^2 <~ 2; the amplitude of a chain of N imperfect crossings falls as
  exp(-N sigma_ph^2) in the paper's estimate. Loss imbalance and DAC
  precision are not correctable: Ec = sqrt(N) sigma_l and sqrt(N) sigma_dac / 2.
- Numbers: Fig. 6 parameters sigma_bs = 2 %, sigma_ph = 0.2 rad, sigma_l = 5e-4,
  12-bit DAC; silicon couplers typically sigma ~ 2 %; sigma_l = 5e-4 for a 200
  um shifter at 2 dB/cm waveguide loss, which the paper says is close to
  wafer-scale loss variations; a 32 x 32 switch network showed trimming power
  variability 1.52 mW against 18.1 mW for a pi shift, giving sigma_ph ~ 0.2
  rad.
- Use here: (U1) per-arm phase error sigma_ph enters E0 as sqrt(2N) sigma_ph and
  is the term a calibrated offset fit removes; the N sigma_ph^2 <~ 2 condition
  is the budget for an uncalibrated start; (U2) n/a; (U3) the exp(-N
  sigma_ph^2) law describes the coherent nulling signal of the algorithm, which
  also responds to external phases; the intensity retained by a routed photon
  follows a law with a 4-times smaller exponent, checked by simulation in the
  Synthesis; (U4) n/a.

### 25. Hamerly, Bandyopadhyay and Englund, stability of self-configuration

- Citation: R. Hamerly, S. Bandyopadhyay, D. Englund. "Stability of
  Self-Configuring Large Multiport Interferometers." Phys. Rev. Applied 18,
  024018 (2022). arXiv:2106.04363v2 (6 Jun 2021, v2 1 Dec 2022).
  https://arxiv.org/abs/2106.04363. Retrieved 2026-10-17. Depth: sections
  (abstract, Sec. 2 error statistics, the coverage passage; Secs. 3 to 5 not
  read in detail).
- Summary. Sequential element-setting self-configuration is unstable for large
  meshes; power-ratio methods are stable even for large errors. To first order
  Delta U = sum_n [dU/d alpha_n alpha_n + dU/d beta_n beta_n] and ||dU/d alpha||
  = ||dU/d beta|| = sqrt(2), so the mesh is equally sensitive to every coupler
  irrespective of geometry. The coverage of a mesh with errors falls as
  cov(N) ~ exp(-N^3 sigma^2 / 3) for Haar targets, and a splitter that cannot
  reach the required angle contributes an error ~ 2^(-1/2) |theta - theta_hat|.
- Use here: (U1) the equal first-order sensitivity to every coupler justifies
  one scalar sigma_bs in a first fit; (U2) n/a; (U3) the stability finding
  warns that a compile that sets elements sequentially can fail on a large
  mesh, a candidate mechanism for non-convergence; (U4) n/a.

### 26. Bandyopadhyay, Hamerly and Englund, hardware error correction

- Citation: S. Bandyopadhyay, R. Hamerly, D. Englund. "Hardware error
  correction for programmable photonics." Optica 8(10), 1247-1255 (2021); DOI
  10.1364/OPTICA.424052. arXiv:2103.04993v1 (8 Mar 2021).
  https://arxiv.org/abs/2103.04993. Retrieved 2026-10-17. Depth: sections
  (Secs. 2 and 3, Supplementary-derived scaling passages).
- Summary. A deterministic per-MZI correction that needs a one-time
  characterization of each coupler pair (alpha, beta) and no feedback.
- Equations (plain text; theta' is the corrected internal phase):
  - Splitter S(alpha) = [[cos(pi/4 + alpha), i sin(pi/4 + alpha)], [i sin(pi/4 +
    alpha), cos(pi/4 + alpha)]] (Eq. 1); ideal MZI T(theta, phi) = i e^{i
    theta/2} [[e^{i phi} sin(theta/2), cos(theta/2)], [e^{i phi} cos(theta/2),
    -sin(theta/2)]] (Eq. 3).
  - theta' = 2 arcsin sqrt((sin^2(theta/2) - sin^2(alpha + beta)) /
    (cos^2(alpha - beta) - sin^2(alpha + beta))) (Eq. 8); realizable only for
    2|alpha + beta| < theta < pi - 2|alpha - beta| (Eq. 9); outside it set theta'
    = 0 or pi.
  - phi' = phi + arctan(sin(alpha - beta)/cos(alpha + beta) tan(theta'/2)) -
    arctan(sin(alpha + beta)/cos(alpha - beta) cot(theta'/2)) (Eq. 12);
    psi1 = -arctan(sin(alpha - beta)/cos(alpha + beta) tan(theta'/2)) + (theta
    - theta')/2 (Eq. 13); psi2 = arctan(sin(alpha + beta)/cos(alpha - beta)
    cot(theta'/2)) + (theta - theta')/2 (Eq. 14). The output phases psi1, psi2
    propagate forward to the output phase screen.
  - Uncorrected matrix error <e> ~ sigma_BS sqrt(2(N - 1)) (Eq. 17);
    P(theta < xi) ~ (N + 1) xi^2 / 12 (Eq. 19) for Haar targets; corrected
    error about e^2 / sqrt(6); improvement <e> / <e_corrected> ~ sqrt(3) /
    (sigma_BS sqrt(N + 1)) (Eq. 22).
- Numbers: two couplers at 52:48 (alpha = beta = 0.02) need theta corrections of
  about 0.1 rad and phi, psi2 corrections that exceed 1 rad near theta ~ 0; wafer
  variance 2 % cited as typical; for sigma_BS up to 4 % error correction yields
  at least a factor of 2 for circuits up to N = 500; classification accuracy
  stays within 1 % up to sigma_BS ~ 4 %.
- Use here: (U1) Eqs. 12-14 show that a given coupler imbalance maps into large
  required phase offsets (above 1 rad) for MZIs near theta ~ 0, so per-heater
  offsets are not small corrections for mirror-state MZIs; (U2) the correction
  fixes the compile for known (alpha, beta), which is the deterministic
  alternative to a stochastic global search; (U3) Eq. 9 gives the exact set of
  MZI settings that cannot be realized (theta < 2|alpha + beta|), which is where
  a bar or cross state leaks; (U4) n/a.

---

## Part IV. Mitigation by allocation and compilation (topic c)

### 27. Kumar et al., port allocation and tailored compilation

- Citation: S. P. Kumar, L. Neuhaus, L. G. Helt, H. Qi, B. Morrison, D. H.
  Mahler, I. Dhand. "Mitigating linear optics imperfections via port
  allocation and compilation." arXiv:2103.03183v1 (4 Mar 2021).
  https://arxiv.org/abs/2103.03183. Retrieved 2026-10-17. Depth: sections
  (Secs. II-V and Apps. D-F).
- Summary. Relabeling input and output ports changes nothing for an ideal chip
  and a lot for an imperfect one; the unitary becomes Q U P for permutations
  P, Q, with the input light and detector assignments permuted accordingly.
  Port allocation reduces mean power and power range and, with a compile that
  uses the real splitting ratio, improves fidelity.
- Equations: phase-voltage phi_l = alpha_l + beta_l V_l^2 (offset and slope per
  shifter, "vastly different for each phase shifter", crosstalk assumed
  negligible); an imperfect MZI with couplers of reflectivity cos^2 theta has
  reflectivity 1 - sin^2(2 theta) cos^2(phi_i / 2), which ranges from cos^2(2
  theta) to 1, so perfect reflection is possible and perfect transmission is
  not; calibration method 1 sets each MZI to phi_i = 0 while the rest sit at pi
  and reads theta from intensities; method 2 assumes a uniform theta,
  implements a fixed unitary with the tailored decomposition at a trial theta
  and minimizes the norm of the intensity difference (Brent optimization;
  recovered 0.469 against a true mean 0.47); the tailored decomposition nulls
  with the imperfect MZI matrix and sets phi_i to 0 or 2 pi when a null is
  unreachable.
- Numbers: tailored decomposition cuts the mean distance by a factor of 550 for
  a 49:51 splitting ratio on a 6-mode chip; calibration plus port allocation
  plus tailored compile gives 5 orders of magnitude on a 4-mode chip with
  reflectivity 0.47 (5000 Haar unitaries), and a factor 11.5 when the true
  ratios vary across the chip but a single value is assumed; port allocation
  (Sweep Search, k about 2) cuts mean power by over 25 % (unrestricted search
  over 40 %) and the standard deviation of the power by a factor of 139.3.
- Use here: (U1) alpha_l, beta_l per shifter is the offset-and-gain model the
  repo fits; (U2) port allocation and relabeling are published ways to choose
  among equivalent solutions with a known objective; (U3) the bound cos^2(2
  theta) on an imperfect MZI is the exact floor of a "mirror" state; (U4) n/a.

### 28. Dhand, circumventing defective components (abstract only)

- Citation: I. Dhand. "Circumventing defective components in linear optical
  interferometers." arXiv:1912.08789v1 (18 Dec 2019).
  https://arxiv.org/abs/1912.08789. Retrieved 2026-10-17. Depth: abstract only.
- Abstract content: a method that circumvents lossy modes and unresponsive
  phase shifters or beam splitters by using a universal interferometer with
  defects as a smaller universal interferometer, tolerating high defect rates.
- Use here: (U1) to (U4) n/a beyond the idea that a defective region can be
  excluded by block placement; the paper was not read.

### 29. Peripheral set (2022-2026)

- Teofilovic, Cem, Sanchez-Jacome, Perez-Lopez, Da Ros. "Thermal Crosstalk
  Modelling and Compensation Methods for Programmable Photonic Integrated
  Circuits." arXiv:2404.10589v1 (19 Mar 2024). Depth: sections (models and
  results skimmed). Three models of crosstalk-induced resonance shift on a
  silicon hexagonal mesh: total phase model (one scale s, about 0.23 to 0.26
  pm/rad), thermal decay model (exponential decay with distance, four
  parameters), and a linear regressor; modeling error below 0.5 pm, and below
  2.0 pm on parts of the chip not used for training. Use here: (U1) an
  exponential decay with distance is the published sparsity prior for crosstalk
  coefficients.
- Gurses, Fatemi, Khachaturian, Hajimiri. "Large-Scale Crosstalk-Corrected
  Thermo-Optic Phase Shifter Arrays in Silicon Photonics." arXiv:2206.04525v2
  (5 Jun 2022). Depth: abstract only. A 288-element thermo-optic array with a
  thermal excitation model, finite-difference simulation and a crosstalk
  correction algorithm.
- Rausell-Campo, Perez-Lopez, Capmany. "Programming universal unitary
  transformations on a general-purpose silicon photonics platform."
  arXiv:2407.03235v1 (3 Jul 2024). Depth: abstract only. Hexagonal-mesh
  programming of 3 x 3 and 4 x 4 unitaries with fidelity above 98 %, with a
  recalibration for passive phase deviations.
- Elmas, Litvin, Kohl, Notzel. "Modeling and Analysis of Phase Instability in
  Photonic Processor." arXiv:2606.25196v1 (23 Jun 2026; DOI
  10.1364/AO.560370 as listed). Depth: sections (model definition skimmed).
  Phase instability from active cooling and temperature drift is modeled as a
  Brownian random walk with variance sigma^2 t, tested on 300 s traces over 35
  trials, plus a harmonic reconstruction; feedback control at 38 Hz suppresses
  it. Use here: (U1) a drift model for how long a fitted offset stays valid.
- Elmas, Litvin, Notzel. "Local Variance-Based Calibration of Programmable
  Photonic Interferometer Meshes." arXiv:2607.14759v1 (16 Jul 2026). Depth:
  abstract only. Intensity-only calibration from the variance of output power
  under phase perturbations; |sin(theta)| for MZIs, |cos(phi)| for shifters;
  validated on an 8 x 8 SiN processor.
- Valdez, Sun, Kroo, Miller, Solgaard. "High Contrast Nulling in Photonic Meshes
  Through Architectural Redundancy." arXiv:2502.07997v2 (11 Feb 2025). Depth:
  abstract only. Double MZIs reach extinction above 80 dB on silicon by
  compensating fabrication imperfections.
- Screened and not used: arXiv:2002.01371 (a different paper than the
  Fldzhyan search hit), 2601.09423 (ring-resonator lattices), 2607.06488
  (a different chip, no Quandela authorship), 2603.20085 (measurement
  tomography with a coherent laser), 2507.08570 (a classical-light processor
  benchmark whose thermal-noise conclusion concerns its own device).

---

## Not found

- A Quandela publication on the Belenos chip itself (fidelity metrics, passive
  phases, calibration residuals). The chip is described only through Barzaghi
  et al. (maker's paper) and the hardware paragraphs of Thomas et al. The
  vendor product page gives gate and read-out fidelities without a method.
- A demultiplexer paper behind "overall transmission exceeding 85 %". Thomas et
  al. cite only "Quandela cloud (2025)". Maring et al. give 70 % for Ascella.
- A published description of the exqalibur CircuitOptimizer. The compile
  description available is the one in Maring et al. (global optimization of
  phases, then transpilation with crosstalk compensation), Perceval's
  Circuit.decomposition, the cloud compile guide, and the user-side reports in
  sources 7 and 8. The statement that the cloud compiler "ignores photon-free
  input modes" has no published source here.
- A peer-reviewed in-situ calibration method that uses single-photon counts
  alone and fits a shared offset vector across compiled settings. The nearest
  methods are source 16 (photon or laser counts, needs voltage control) and
  source 29's intensity-only variance calibration (classical light).

---

## Synthesis for Belenos

### Error model the literature supports for a 24-mode thermo-optic MZI mesh

The unitary is a product of MZIs, each B(theta2) diag(e^{i(phi + psi)}, 1)
B(theta1) with fixed couplers, a phase-voltage map per heater, and port
transmissions: phi = A p + c0 with p the heater drive power (or V.^2), A a sparse
matrix whose diagonal is the self-heating coefficient, c0 the passive offsets,
R_j per coupler, T_in and T_out per port (sources 1, 16, 17, 18). Ranking by
magnitude, with the source of each number:

| Rank | Term | Magnitude | Source |
|---|---|---|---|
| 1 | Raw passive phase offsets c0 of the bare chip; a cloud user never fits these, because Quandela's calibrated phase map already removes them, and sees them only if that calibration fails | (0.1 +- 1.2) rad as printed, read as mean and spread over heaters | 1 |
| 2 | Residual phase error after calibration, the quantity a cloud user fits on top of the calibrated map (initialize the fit at zero) | hardware-backed bound: below 0.1 rad on a 6-mode glass mesh (source 18). Simulation inputs only: 15 and 30 mrad (source 9); 6 mrad controlled and 140 mrad induced-shifter residual (source 17); 0.2 rad as an uncalibrated example (source 24) | 18, 9, 17, 24 |
| 3 | Coupler imbalance | R = 0.567 on Ascella (Si3N4, off design wavelength); alpha up to 0.0456 (R = 0.4545) on the Belenos angles; silicon sigma_bs about 2 % | 1, 24, 26 and conventions block |
| 4 | Compile non-convergence and calibration state | up to 40 % relative bias in an observable; leakage scatter by an order of magnitude; HOM 90.7 % to 21.2 % and 66-fold leakage across one recalibration | 8, 7 |
| 5 | Thermal crosstalk residual | off-diagonal about 2 % of self-heating at the nearest heater, falling as 1/d^2 (simulation); vertical-neighbor-only model on glass | 17, 18 |
| 6 | Non-uniform port loss and detector banks | mode 10 at 75 % of mode 6 on Ascella; 4.35 dB average insertion loss on the 24-mode glass chip; modes 0 to 15 photon-number-resolving, 16 to 23 SNSPD | 1, 3, 4 |
| 7 | Detector dark counts | Ascella SNSPD under 20 Hz per detector is not a Belenos prior; repo records for Belenos are in the cross-check below | 1 |
| 8 | Drift | heater resistance drift under 0.005 %/h; hourly recalibration cadence | 3, 2 |

Calibrated meshes reach Haar amplitude fidelity of 99.85 % (12 modes, Si3N4,
loss compensated), 99.79 % (6 modes, glass), 99.7 % (24 modes, glass) and 97.4
% (20 modes, Si3N4) (sources 16, 18, 3, 19). Source 16 observes empirically
that the amplitude fidelity of a circuit satisfies Fa ~ 1 - TVD^2 for the
model-versus-data TVD.

Depth scaling. For uncorrelated per-component errors the matrix error grows as
sqrt(N): E0 = sqrt(2N (sigma_ph^2 + sigma_bs^2)); local correction leaves Ec =
sqrt(2/3) N sigma_bs^2 = E0^2/sqrt(6); a phase-error threshold N sigma_ph^2 <~ 2
governs uncalibrated self-configuration (sources 24 to 26). These are
Haar-average statements. They do not transfer to a one-photon block on a
mirror background, where most MZIs sit at bar or cross, the coupler-imbalance
floors sin^2(alpha1 +- alpha2) per MZI apply (conventions block; sources 23, 26,
27), and CROSS is the harder state (source 9).

Derived here, retained power versus phase error. An MZI nominally in bar or
cross, with 50:50 couplers and an arm-phase difference error D, leaks power
sin^2(D/2) ~ D^2/4. With independent per-arm errors of rms sigma_psi, Var(D) =
2 sigma_psi^2, so the mean leak is sigma_psi^2 / 2 per MZI and the retained
power is about exp(-N_c sigma_psi^2 / 2), with N_c the number of MZIs on the
photon's path. The constant was checked by simulation (24-mode rectangular
mesh, 50:50 couplers, random N(0, sigma) phase on both arms of every MZI,
400 draws per point, probability of leaving in the mode the nominal setting
sends the photon to):

| sigma (rad) | all-bar chain, interior mode 11 | all-cross diagonal 0 -> 23 | all-bar chain, edge mode 0 | exp(-24 sigma^2 / 2) |
|---|---|---|---|---|
| 0.05 | 0.969 | 0.972 | 0.984 | 0.970 |
| 0.10 | 0.886 | 0.893 | 0.938 | 0.887 |
| 0.15 | 0.770 | 0.776 | 0.870 | 0.763 |
| 0.20 | 0.647 | 0.638 | 0.791 | 0.619 |
| 0.25 | 0.535 | 0.497 | 0.711 | 0.472 |
| 0.30 | 0.439 | 0.361 | 0.675 | 0.340 |

The formula holds to a few percent through sigma = 0.15 and underestimates
retention beyond that, because leaked light partly returns. Hamerly's exp(-N
sigma_ph^2) is an amplitude law for the coherent nulling signal of a
self-configuration algorithm, which also responds to external phases; read as
an intensity law it would give exp(-2 N sigma^2) = 0.05 at sigma = 0.25, which
the simulation contradicts. N_c is 24 only for interior modes: an edge mode
meets an MZI every other column (12 MZIs for mode 0), and the 0 -> 23 diagonal
route meets 23, so N_c depends on block geometry. A retained fraction of 0.47
needs sigma of about 0.25 (diagonal cross route) to 0.28 (interior bar chain)
rad rms per arm, and about 0.4 or more for an edge mode.

Phase scales for comparison: the only hardware-backed residual bound is below
0.1 rad on a 6-mode glass mesh (source 18). The other numbers in the error table
are simulation inputs. The needed sigma is therefore about 2.5 to 3 times the
bound, not far outside every published scale, and the gap would close if
the Belenos residual were larger than that of a 6-mode device.

The 24 dB figure of source 3 is an extinction ratio relative to the target
output of a closed-loop-optimized route. If every one of the other 23 outputs
sat at that level, the total leak would be at most 23 x 10^-2.4, about 9 %
(an upper-bound reading; the full distribution is in a figure that was not
tabulated). A closed-loop route therefore loses at most about 9 %, while the
model-compiled job lost about half, which points at the compile and calibration
path and not at the physical mesh.

Repo cross-check (values read from the repo records, not from the literature):
`docs/evidence/quandela/belenos_leakage_rca.json` (run
2026-10-17T213646Z-qpu_belenos-box_kite_photonic_single-job-04, one photon on
mode 20) records the TVD of the observed distribution against the ideal
compiled-mesh prediction as 0.880; an isotropic phase-noise hypothesis reaches
its best stored TVD, 0.273, at sigma = 0.5 rad (the largest of the stored
values 0.2, 0.3, 0.4, 0.5); the gain, crosstalk, wrong-source, ceiling and
convention hypotheses each leave TVD at or above 0.283; the shot-noise floor is 0.0129; and the expected dark
counts over the job's estimated 0.27 s acquisition are 5.8 on mode 0 and 13.5 on mode 5,
against 664 single clicks on mode 5. Those 664 clicks lie outside the photon's
light cone and come and go in a way the receipt's rate does not predict
(`docs/notes/quandela/strategy.md` section 2), so a retained fraction is read
over the in-cone samples, where an off-cone mode cannot mimic a leak.

Inference, uncertainty moderate to low. A static residual of the published
hardware-backed scale (0.1 rad) predicts retention of about 0.89 on an interior
path; 0.47 needs a residual about 2.5 to 3 times larger, or a non-static cause.
The documented Quandela-side causes of order-one deviations are compile
non-convergence (source 8) and calibration-state episodes (source 7), and the
repo's own phase-noise fit favors a scale of 0.5 rad or more. What would
raise confidence in a compile or calibration cause: a retained fraction that
changes with the compile seed or across calibration sessions for an identical
circuit. What would raise confidence in a static residual: log retention linear
in the number of MZIs crossed with slope sigma^2 / 2 and a leak map that is
reproducible across seeds. What would point to coupler imbalance: leakage
concentrated on the waveguides adjacent to the route in proportion to the
CROSS floor sin^2(alpha1 + alpha2) of the MZIs on it.

### Best-supported characterization from one-photon counts only

1. Fit a model-based replica, not a ratio reconstruction. The Laing and O'Brien
   fidelity law gives F ~ exp(-((m - 3)/5) sqrt(delta)); extrapolated to m = 24
   it needs about 3e11 counts per rate for F = 0.99. The model-based fit of
   source 16 needs about one training sample per parameter and reached TVD
   2.9 % on hardware with a single-photon source.
2. Parameterize by the known compiled phases plus unknowns. A cloud user fits
   the residual on top of Quandela's calibrated phase map, so the offset vector
   delta (574 entries, minus gauge) starts at zero with a prior scale of about
   0.1 rad (source 18), not at the O(1) rad raw offsets of source 1. Source 16
   addressed only 6 of 12 inputs (the even ports) and still identified its
   model, which supports a fit that uses the 12 connected Belenos inputs.
   Add a global or per-heater gain, a sparse crosstalk term with
   vertical-neighbor structure (source 18) or an exponential-decay prior
   (source 29), per-coupler R seeded from the retained angles, and per-port
   T_in, T_out (and per-bank detector efficiency). Fix the gauge before
   quoting offsets: one input and one output phase per mode are unobservable
   with Fock inputs and intensity detection (sources 14, 13, 17).
3. Freeze c0 while the gain, coupler and transmission terms converge, then
   update c0 from one-photon fringes (an on-chip splitter prepares a
   superposition of two inputs; the intensity pattern is the two-input
   interference of source 14). Source 16 reports that joint descent on passive
   phases stalls in local minima.
4. Estimate with a multinomial likelihood on counts and put dark counts and an
   efficiency vector in as nuisance parameters; source 16 uses mean squared
   error and has no dark-count term. Subtract duration x per-mode dark rate
   before computing any retained fraction, and take the dark rates from
   Belenos records (see the repo cross-check above), not from the Ascella
   figure of under 20 Hz. Select models on held-out settings in
   the 80/20 split of source 16 and compare the held-out TVD with the
   counting-noise floor.
5. Key each fit to a calibration session and the backend metadata. Source 8
   shows biases that change between calibrations, and source 7 shows
   a recalibration window that moves leakage 66-fold.
6. Keep amplitude fidelity and TVD as ceilings, not conformance claims: single
   photons from one input measure |U| only, and Fa overstates F (0.9978
   against 0.9921 in source 18).

### Ranked design rules for the jobs

1. Run every one-photon configuration as an ensemble of at least 8 equivalent
   compiles (source 8 used 40), each carrying random output phases or a
   distinct compile seed, and report the mean and the between-seed spread. The
   spread is the compile-bias estimate. Evidence: source 8 (40 % to mitigated);
   source 7 (leakage scatter by an order of magnitude); repo per-iteration
   compile.
2. Select among seeds by held-out leakage, never by the leakage of the shots
   that are then reported. Split shots in two, choose on one half, report on
   the other. Evidence: source 16 keeps the best of 32 relabelings against a
   known objective; sources 7 and 8 show that raw compile scatter is large.
3. Place the block to minimize the number of MZIs crossed and the number of
   CROSS states, and to use the best ports. Evidence: source 9 (compact zone,
   BAR more accurate than CROSS, coincidence rate up to +33.2 %); source 24
   (error grows as sqrt(N)); source 27 (port allocation).
4. Use relabeling as a free degree of freedom. Choose among output-permutation
   equivalents so that the required bar and cross MZIs sit on couplers whose
   retained angles satisfy the realizability condition 2|alpha1 + alpha2| <
   theta (source 26 Eq. 9). Evidence: sources 16, 27.
5. Log calibration state with every job (backend metadata, HOM and g2 if
   reported, compile session) and repeat a fixed extinction control per session.
   Evidence: source 7 (HOM 90.7 % to 21.2 %, leakage 0.0073 to 0.481); source
   2 (hourly calibration).
6. Treat the mirror MZIs as part of the error budget and map leakage by
   distance from the block, then fit log retained fraction against the number
   of MZIs crossed (interior modes meet one MZI per column, edge modes one per
   two columns). Evidence: simulated retention law above; sources 12, 23.
7. Separate instrument terms from routing before reading any retained
   fraction as optical: subtract duration x per-mode dark rate (the repo
   records tens of dark counts per second on single modes and about 9 % of a
   job's samples), fit T_in and T_out per port and per detector bank (modes 0
   to 15 photon-number-resolving, 16 to 23 SNSPD), use the efficiency-free
   ratio of source 13 across at least two input modes, and bound dark counts
   from jobs with no signal on the output modes of interest (the cloud blocks
   direct access, source 8). Anchors from the literature: SNSPD efficiency 90
   to 92 % (source 4); Ascella dark counts below 20 Hz per detector (source 1)
   do not transfer to Belenos.
8. Do not claim unitary-level conformance from one-photon counts. Add a
   two-input on-chip interference test before quoting phase accuracy (sources
   14, 18).
9. Do not use ratio-based reconstruction at m = 24 with finite counts (sources
   13, 15).
10. Size counts so that the statistical floor sits below the systematic target:
    source 8 used about 10^6 samples per circuit, source 16 reports a
    counting-noise TVD floor near 0.1 % at its rate, and source 18 reports a
    reproducibility floor of 0.9998 amplitude fidelity between repeats of one
    unitary.
