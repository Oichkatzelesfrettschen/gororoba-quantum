# Quandela Belenos strategy guide

A living guide to getting the most science per credit out of Quandela Cloud's
photonic platforms with this repository's tooling. Each section states what
holds, the authority behind it (a retained run, the captured guide, the
Perceval 1.3.1 source or an exact computation), and what it changes in a
case. A new run or a refuted conjecture updates the section it touches and
the run log at the end.

## 1. Cost model (measured)

| Item | Value | Authority |
|---|---|---|
| Per job, any Explorer platform | 1 credit, drawn as `free_credits` from the 200-credit monthly pool | token usage report after jobs e12075f3 (sim) and 7419efb8 (QPU) |
| Per shot, qpu:belenos and qpu:ascella | 1e-06 credits | platform record; job 7419efb8 charged 1.01 for 10000 shots |
| Per shot, every simulator | 0 | platform record; six sim:belenos jobs charged 6.00 |
| Iterated job | 1 credit for 8 iterations (fringe job 685945a8, 83 s on sim:belenos) | usage report after the fringe jobs |
| Seconds charged | `duration_seconds` in the usage report (12 to 18 s per sim job, 13 s for a 10000-shot QPU job, about 10 s per iteration) | usage report |

The job, not the shot, is the cost unit: a 10000-shot QPU job costs 1.01
credits and a 347113-shot two-photon job 1.35. Everything that puts more
configurations into one job (iterations, packing) divides the cost; nothing
that adds shots changes it materially.

## 2. Platform facts that shape a case

- **Job names** are stored in a varchar(50); a longer `job_name` answers
  HTTP 424 "value too long for type character varying(50)". The runner names
  a job `SERIES/job-NN` and refuses longer names.
- **sim:belenos** applies its own default noise model when the payload sends
  none: g2 0.003, indistinguishability 0.92, transmittance 0.06 (result field
  `noise`). It is not the QPU's live figures (g2 1 %, HOM 92.6 % on
  2026-10-17), so a sim prediction of a QPU number sends the QPU's
  NoiseModel or recomputes locally.
- **Rates.** qpu:belenos delivered 10000 one-photon samples in 13 s, about
  770 per second (`physical_perf` 0.0074), not the clock times transmittance
  estimate of about 10^4 per second. The summed detector dark counts (about
  68 per second, 38.2 on mode 5 and 19.6 on mode 0) are then about 9 % of a
  job's samples; an analysis subtracts duration times the per-mode dark
  count before it attributes clicks outside a block to the optics.
- **Compilation.** Both the simulator and the QPU return `computed_input`
  and `computed_circuit`. For a 24-mode circuit the compiled circuit is the
  full chip mesh: 552 beam splitters (Rx convention, calibrated angles such as
  1.5867 against pi/2) and 574 phase shifters, so a photon crosses about 48
  elements whatever the block's size. The sim and the QPU returned
  byte-identical compiled circuits for the same case, so a QPU deviation from
  a sim result is the hardware's realization of that circuit.
- **Input adaptation.** A photon on a mode without a source makes the cloud
  add routing permutations and re-transpile (`guide/user-guide/04-compilation.md`);
  every case puts photons on the connected modes 0, 2, 4, 6, 8, 9, 12, 13,
  16, 18, 20, 22.
- **Iterations.** One Perceval `ComputationIterator` job carries a list of
  iterations, each with any of `circuit_params`, `input_state`,
  `min_detected_photons`, `max_samples`, `max_shots`, `postselect` and
  `compilation_seed` (`perceval/runtime/computation_iterator.py`); the result
  answers `results_list`, one entry per iteration, and a whole parameter scan
  costs one job. Measured on sim:belenos: the server compiles every iteration
  separately (eight distinct `computed_circuit` values in one fringe job, about
  10 s each, so the 300 s job limit admits roughly 25 iterations); each entry
  reports its own `nb_shots_used`, and the answer's top-level `shots` is one
  iteration's `max_shots`, not the job's total. The runner sums
  `nb_shots_used` and bounds every iteration's samples by it.
- **Compiled width.** A 4-mode circuit compiles to the same full 24-mode mesh
  (552 beam splitters, 574 phase shifters) as a 24-mode one; only the photon's
  entry mode moves (to mode 0). A circuit sent as native BS.H / PS / PERM gates
  and the same unitary sent as one `Unitary` compile to different phase
  settings, while an identical circuit compiles to an identical mesh on the
  simulator and the QPU. Width therefore cannot shorten a photon's path; a
  compact job tests placement at the chip's edge.
- **Calibration windows.** qpu:belenos reports status `calibration` outside
  its weekly maintenance (observed 2026-10-17 about 22:15 UTC); `plan` refuses
  any status but `available`, so a job waits rather than queues.
- **Compilation seeds** are an iteration key, and `CompilationAveraging` is a
  known mitigation of both Belenos platforms, so the spread over compilations
  is measurable inside one job.
- **Weekly maintenance** blocks qpu:belenos (2026-10-22 07:30 to 11:00 UTC
  in the platform record); the runner refuses any status other than
  `available`.
- **The chip is one fixed mesh.** The processor record's `specs.architecture`
  is an Experiment of 552 Rx beam splitters at calibrated angles (1.557 to
  1.662 rad against pi/2) and 574 symbolic phases `phi0..phi573`: 276 MZIs
  (BS(m), PS on m+1 and m, BS(m)) in 70 ASAP columns plus 22 edge phases on
  modes 0 and 23. All 26 retained compiled meshes (sim and QPU, single and
  iterated) carry exactly that topology and those angles
  (`docs/evidence/quandela/belenos_leakage_rca.json`), so a job is fully
  described by 574 numbers and the transpiler only chooses them.
- **The transpiler fixes only the occupied columns.** The compiled mesh of
  the bright block reproduces |U[:,20]|^2 = (0.4999, 0.5001) on modes 20 and
  21, but its other 23 columns are arbitrary (input 0 spreads over modes 0 to
  9): the captured guide's promise that unused modes act as "complete
  mirror" does not describe what the service returned. Internally the
  photon's amplitude fans out over modes 16 to 23 (peak occupancy 0.32 on
  mode 17, 0.38 on 18, 0.61 on 19) and must re-converge by interference.
- **Detection.** `default_mitigations` is DetectorBalancing; the per-mode
  output transmission `t_out` spans 194 to 399 (relative units) across modes
  12 to 23, mode 20 lowest, so a model comparison weights each mode's
  probability by `t_out` before it compares histograms.

## 3. Client safety

`perceval.serialization.deserialize` evaluates parameter expressions through
sympy, and the deprecated result-mapping branch of
`RPCBasedCommunicationLayer.get_results` calls `__import__` on a module name
taken from the service's answer. The runner never calls either: it parses
counts from the BSCount string itself, reads architectures and compiled
circuits through a standard-library protobuf wire decoder
(`scripts/qd_belenos_mesh.py`, cross-checked against
`exqalibur.serialization.circuit_pb2` in its self-test), posts through a
no-redirect opener and keeps the token out of every file it writes.

## 4. Circuits from first principles

- **Encoding.** A photon carries the Design B product x y. V = L_x on
  span{e_L', e_U'} divided by sqrt2 is M / 2 for the sign block
  M = [[g(L,L'), s g(U,U')], [s g(U,L'), g(L,U')]], and the circuit is the
  Halmos dilation [[V, sqrt(I - V V^T)], [sqrt(I - V^T V), -V^T]], exact over
  Q(sqrt2) (`scripts/qd_box_kite_cases.py`).
- **Native gates.** Every sign matrix is M = D1 K D2 with +-1 diagonals and
  K the edge core [[1, 1], [1, 1]] or the strut core [[1, 1], [1, -1]], and
  dil(D1 K D2) = diag(D1, D2) dil(K / 2) diag(D2, D1). So every block is a
  pi-phase layer, a core and a pi-phase layer of Perceval's BS.H (balanced),
  PS(pi) and PERM:
  - edge core (BS.H_01 BS.H_23) PS_2 SWAP_13 (BS.H_01 BS.H_23): the core
    routes, it does not mix label and dilation space;
  - strut core BS.H_01 BS.H_02 BS.H_13 BS.H_23: balanced mixing of label and
    dilation modes, the beam splitters of a Hong-Ou-Mandel suppression.
  The box-kite signs enter only as pi phases; edge against strut is a
  routing core against a mixing core. Perceval places beam splitters on
  adjacent modes only, so the non-adjacent pair is
  SWAP_12 (BS.H_01 BS.H_23) SWAP_12. Every native list is checked against its
  unitary in exact arithmetic, and the runner checks Perceval's unitary of
  the circuit it sends against the case to 1e-12.
- **What one photon can show.** Only column 0 of U is observable, and an
  output phase changes no click probability, so a one-photon block tests
  that the chip implements a known distribution: classical-wave
  interference, never a nonclassical effect.
- **What two photons show.** One photon on each input port of the dilation
  is the bipartite case: the label coincidence is |perm(V)|^2 =
  (perm M / 4)^2, and perm M = g(L,L') g(L,U') (1 + p0 p1), det M =
  g(L,L') g(L,U') (1 - p0 p1) for the kite phase products. An edge
  (p0 = p1) bunches at 1/4 and a strut (p0 != p1) suppresses to 0 against
  1/8 for distinguishable photons. The box-kite octahedron is K_{2,2,2}:
  struts pair assessors within one of its three parts, edges join parts, and
  the permanent vanishes exactly on the within-part pairs.
- **The phase fringe.** With the input phase as a parameter, a block's
  algebra probability is P(phi) = [4 + 2 cos phi (m00 m01 + m10 m11)] / 8:
  an edge follows (1 + cos phi) / 2 (bright at 0, dark at pi) and a strut is
  flat at 1/2. One iterated job over phi = k pi/4 measures visibility (the
  chip's zero-divisor contrast) and phase offset (its phase error) on one
  compiled mesh, where common-mode errors cancel (`belenos_fringe`).
- **Coverage.** Census Design B rows reach 14 of the 16 sign matrices;
  cd_core witness pairs supply the other two, and every two-label two-blade
  product at D = 16, 32 and 64 maps to one of the 32 (M, t) circuits
  (`docs/evidence/box_kite_census/two_blade_blocks.json`).
- **Many unitaries in one job.** `scripts/qd_belenos_mesh.py` sends the
  architecture circuit with one Perceval parameter per phase, so every
  experiment of a job is one iteration's 574 `circuit_params` plus its
  `input_state`: sixteen different block unitaries cost one credit. A
  block's phases come from placing it on the first six (or eight) MZIs
  inside its four modes, fitted to D_out U D_in with free diagonal frames,
  with every other MZI in bar (hot) or idle at phase 0 outside a two-mode
  margin (cold); those phases fix the unitary the server receives, and the
  photon's designed path stays on modes 19 to 22.
- **The server re-transpiles every circuit (measured).** S3 (job 1d7160c1,
  16 parameterized settings) and S4 (job e5b74123, one numeric setting, the
  guide's pre-compiled form) both came back with all 574 phases changed: the
  occupied column survived (|U|^2 within 2e-4, every setting's histogram
  within shot noise of its ideal), the other 23 columns did not, and every
  returned mesh drives about 1800 rad of heater phase and spreads the photon
  over 6 to 8 modes whatever was sent. The designed path never reaches the
  chip; the designed column does. Section 7 holds the transpiler model.

## 5. Analysis rules

- One-photon block: in_block (one-click samples on the block's modes over
  all one-click samples, ideal 1) separates routing loss from the algebra
  share a; the per-mode total variation distance uses every sample. The
  analysis also reports both after subtracting each mode's expected dark
  clicks (the receipt's per-mode rate times the job's duration): the QPU
  bright block's in_block rises from 0.470 to 0.505 once about 692 expected
  dark clicks outside the block are removed, and a stays at 0.256.
- Two-photon block: threshold detectors with min_detected_photons 2 keep
  only two-click samples, so the observable is the conditional label
  fraction f(V) = (V L_ind + (1 - V) L_dist) / (V T_ind + (1 - V) T_dist),
  fitted under the g2 read at submission; a two-mode HOM job reads only (0, 1)
  coincidences under that filter and carries no V.
- Fringe: a(phi) per iteration and the closed-form fit A + B cos phi +
  C sin phi over the eight phases (`scripts/qd_box_kite_analysis.py`).
- Mesh job: per iteration, the returned mesh (its sha256, heater sum and
  largest phase change against the sent phases), the one-click histogram, the
  dark-corrected block share and the algebra share a against the case's ideal.
  Every model is computed on the mesh the iteration returned, on that run's
  own couplers (`run_architecture`), so a refreshed catalogue never changes a
  retained analysis. Dark clicks are the receipt's per-mode rate times the
  setting's share of the job, capped by the mode's lowest click fraction over
  the job's settings (Q1's receipt predicts 277 dark clicks on mode 0, which
  read none). Each class is scanned over its magnitude (exact dephasing
  channel sigma 0 to 0.8, heater gain -0.6 to 0.6, crosstalk -0.2 to 0.2,
  misroute fraction 0 to 1 with noise), and a class fits when the chi-square
  p-value of G^2 at its degrees of freedom is at least 0.001 and the median
  ratio of setting TVD to the shot-noise floor is at most 3; otherwise the
  job reads "no class fits", and a best point at every class's null
  magnitude reads "ideal". The static class (section 6) wins when its
  held-out gain exceeds 10 nats (`qd_belenos_mesh.analyze_run`). On
  sim:belenos, whose truth is the ideal mesh, both mesh runs read "ideal"
  (p = 0.033 and 0.094) and the static offsets lose 28 nats on held-out
  settings.

## 6. Leakage root cause (qpu:belenos job 7419efb8)

The bright block sent one photon into mode 20 and kept 0.470 of the
one-click samples on modes 20 to 23 (0.505 after dark subtraction), with the
leaked light on modes 17 (0.190 of the dark-subtracted histogram), 18
(0.101), 19 (0.068) and 16 (0.052), and 0.38 of the in-block light on the
dilation modes that should be dark. Every conjecture below was tested
offline against the retained raw bytes
(`docs/evidence/quandela/belenos_leakage_rca.json`, efficiency-weighted
total variation distance against a shot-noise floor of 0.012):

| Conjecture | Evidence | Verdict |
|---|---|---|
| Our circuit or encoding is wrong | the decoded compiled mesh gives (0.4999, 0.5001) on modes 20 and 21 and matches Perceval's own BS/PS build to 5e-16; `computed_input` is the photon on mode 20 | refuted |
| Extra photons or entanglement (other sources firing, g2) | 1 event of 10000 has more than one click; with one photon there is no multi-photon state to entangle | refuted |
| Serialization or convention (transpose, mirrored modes, reversed order, negated phases, theta to pi - theta) | best variant TVD 0.378 against 0.871 for the ideal, none near the floor | refuted |
| Coupler (theta) errors | a common shift of 0.1 rad keeps 0.99 of the light in the block; 0.05 rad noise keeps 0.99 | refuted as the main cause |
| Random heater phase noise | the exact dephasing channel reaches TVD 0.252 only at sigma 0.5 rad on every heater and puts the leak on 18 and 19 rather than 17 | not supported at a physical size |
| Heater gain, thermal crosstalk, phase ceiling | best one-parameter fits TVD 0.256 (gain -0.3), 0.364 (crosstalk 0.155), 0.315 (ceiling 4.95 rad), all twenty times the floor | open, none explains the run |
| Wrong photon: the demultiplexer routes the photon into another source mode | the compiled mesh's column 18 fits at TVD 0.298, as well as any physical model | open, tested by the identity settings below |
| Device state: the run preceded a calibration (status `calibration` 40 minutes later) | Belenos read 0 % availability 2026-10-10 to 13 and returned on 10-14 | open, tested by the diagnostic job's class likelihood on fresh calibration |

The conclusion is that the error is in the chip's realization of a
correct circuit, a single-photon interferometer error of at least 0.5 rad
equivalent per heater or a misrouted photon, and that one run cannot
separate the classes. The discriminating job is `belenos_mesh/job-00`:
sixteen settings whose returned meshes (identical on the simulator and the
QPU for the same body) respond differently to each class.

**Lessons learned and how each is resolved.**

1. A compiled circuit can be checked: decode `computed_circuit`, rebuild its
   unitary and compare with the case before blaming the hardware. Resolved in
   `qd_belenos_mesh.decode` and the RCA record.
2. The transpiler owns the photon's path, and the path it picks is a random
   one: a mesh that fans the photon over eight modes exposes it to every
   heater error on them. Neither a parameterized nor a numeric architecture
   circuit reaches the chip unchanged (S3, S4). Resolved by the seed lever of
   section 7: screen `compilation_seed` on the simulator, score each returned
   mesh under the identified error class and send the QPU the most robust
   seed.
3. Hardware errors are classes with opposite remedies: across 48 transpiler
   starts of the same bright block, in_block under 0.4 rad heater noise
   ranges 0.46 to 0.76 and under a -0.3 heater gain 0.16 to 0.86, and the
   best seed for one class is not the best for another. Resolved by
   computing every class's prediction on the mesh each iteration returns and
   letting a likelihood over one job decide the class first.
4. A misrouted photon looks like optical leakage in a block test. The
   returned meshes' unused columns are transpiler draws, so a misrouted
   photon lands wherever its column sends it, not on its own mode. Resolved
   by the source models, whose likelihood on the returned meshes separates a
   misroute from every other class by at least 8993 nats in one job.
5. A calibration window can follow a run, and the source changes with it
   (HOM 92.6 % at the Q1 run, 57.8 % after the next calibration). Resolved:
   every plan records the live performance figures, and two-photon cases wait
   for HOM to recover.
6. Coupler angles change with recalibration, and the transpiler's output for
   a seed depends on them. Resolved: `plan` decodes the live architecture and
   refuses a mesh case whose couplers or symbols differ, and the analysis
   records each returned mesh's sha256, so a QPU mesh that departs from the
   screened one is visible.
7. The server applies its default mitigations when the body names none
   (`RemoteComputer.prepare_payload` sends `None`); DetectorBalancing
   rewrites probabilities, while `sample_count` histograms return as integer
   counts. A case states its mitigations explicitly.

**Fitting the chip's error: what failed and how each failure is resolved.**

1. Direct mesh control was assumed from the captured guide's promise that
   a compatible circuit skips transpilation. S3 and S4 refuted it for both
   the parameterized and the numeric form. Resolved: predictions use the
   returned mesh, and the seed is the planning lever (section 7).
2. Averaged-noise predictions were Monte Carlo means over 200 replicates.
   Their estimator error (about 0.02 per mode at sigma 0.6) exceeds the shot
   noise of 1500 samples, so an in-family truth drawn on independent
   replicates failed the fit (G^2 / dof 2.11 against 1.31 on the scan's own
   replicates). Resolved: `channel` propagates the photon's 24 x 24 density
   matrix with each noisy shifter damping its coherences by e^{-sigma^2/2}
   and each noisy coupler mixing by its exact moments, the exact ensemble in
   18 ms, equal to `propagate` at sigma 0 to 3e-16 and to a 20000-replicate
   Monte Carlo within its own error.
3. An ensemble is the wrong object for a miscalibrated chip, which is one
   static realization shared by every job on it. Resolved: `StaticFit`
   estimates one offset per heater, shared by all settings of a job, by MAP
   under a Gaussian prior, with the exact adjoint Jacobian (`jacobians`,
   equal to a central difference to 4e-10), and `static_cross_validation`
   scores each fold of settings with offsets fitted on the others. The
   photons of the 16 S3 meshes touch 83 % of the 574 heaters, so one job
   constrains most of the chip. On the simulator the held-out gain is -28
   nats (no offsets), and on a synthetic static truth of 0.3 rad it is about
   1.1e5 nats.
4. The first decision rule crowned the best of twelve fixed models, so a
   data set no model explains still named a class. Resolved: magnitude
   scans, an absolute fit criterion and the preregistered "no class fits"
   outcome, held by core-512 on three synthetic truths (phase noise 0.6 off
   the fixed grid, misroute 0.3 plus noise 0.3, and an out-of-family
   distribution) and by core-513 on the static class.

## 7. Transpiler model and planning around it

- **Engine.** Perceval's `CircuitOptimizer` wraps
  `exqalibur.CircuitOptimizer(target, template, empty_mode_list, seed)`:
  a fidelity optimization of the template's free phases against the target
  unitary, from random starting phases, that ignores every mode in
  `empty_mode_list` ("modes without input photon ... ignored during
  optimisation"), stopping at 1 - fidelity below 1e-6 (4 trials, 200000
  evaluations each by default). The platform runs exqalibur 1.4.2, the
  version installed here.
- **Evidence it is this engine.** Run locally on the Belenos architecture
  with the photon-free modes as `empty_mode_list`, it returns meshes
  indistinguishable from the served ones: summed heater phase 1793 +- 35 rad
  locally against 1807 +- 22 served (uniform phases give 574 pi = 1803),
  phase standard deviation 1.813 against 1.803 (uniform 2 pi / sqrt12 =
  1.814), photon spread 8.4 against 7.7 modes, 2.4 % of MZIs in bar in both.
  It converges in about 0.9 s for a one-photon target. Local runs are
  deterministic per seed, and the same submitted unitary compiled to the same
  mesh on sim:belenos and qpu:belenos (S1 and Q1). The server's seed mapping
  and options are not published, and no local seed from 0 to 63 reproduced a
  served phase, so the model is statistical, not bitwise.
- **Consequences.** Only the occupied input columns are constrained; every
  other degree of freedom keeps its random start, so the photon's path is a
  random draw from the solutions, and what we send for unused columns,
  frames or mesh phases changes the draw but not its distribution.
- **Planning.** `compilation_seed` is an iteration key, and Perceval's
  `CompilationAveraging` mitigation exists because a single compilation
  carries mesh-specific error: it splits the shots over consecutive seeds
  and averages. Selection beats averaging once the error class is known:
  1. run the diagnostic job on the QPU and read the class from the summed
     likelihood;
  2. screen seeds on sim:belenos, one iteration per seed (about 25 per
     credit), keeping each returned mesh;
  3. score every returned mesh offline under the identified class and keep
     the best seed per target (the 48-seed spread above is the expected
     gain);
  4. send the QPU job with those seeds and confirm each returned mesh's
     sha256 equals the screened one; a mismatch (recalibration) voids the
     selection, not the data.
- **Budget per credit.** A job costs 1 credit plus 1e-06 per QPU shot, and
  any number of iterations ride on it within 300 s. sim:belenos spent about
  13 s per iteration of 1500 samples (212 s for sixteen); the local
  optimizer needs about 1 s, so most of that is the simulator's sampling.
  qpu:belenos returned 10000 one-photon samples in 13 s. The diagnostic job
  measures the QPU's per-iteration overhead; until then a QPU job plans
  sixteen settings of 1500 samples, and a simulator validation of a larger
  job splits into halves that each stay under 300 s.

## 7a. What the literature adds (docs/notes/quandela/literature.md)

The literature note transcribes 30 sources with their arXiv ids and the
equations used here. Five findings set the plan:

1. The Belenos chip class (Barzaghi et al., arXiv:2505.01609) is a
   laser-written glass mesh whose calibration fits static phases, every
   coupler's splitting ratio and a thermal crosstalk matrix from 30000 random
   settings, reaching 99.7 % Haar amplitude fidelity; a closed-loop route
   reaches 24 dB extinction, so a healthy mesh loses at most about 9 % on a
   one-photon route. Q1's loss of about half therefore points at the compile
   and calibration path, not at the glass.
2. Calibration episodes move leakage by more than an order of magnitude: a
   Belenos study (Tully et al., arXiv:2606.18408) saw HOM visibility fall from
   90.7 % to 21.2 % and a dump-port leak rise 66-fold across one
   recalibration, then recover. qpu:belenos read HOM 92.6 % at Q1 and 57.8 %
   after the next calibration.
3. Compile non-convergence biased one-photon observables on Ascella by up to
   40 % and changed between calibrations; an ensemble of 40 equivalent
   circuits with random output phases removed it (Franco et al.,
   arXiv:2604.04691).
4. Retained power on a bar or cross route of N_c MZIs under per-arm phase
   error sigma is about exp(-N_c sigma^2 / 2), so Q1's 0.47 on an interior
   route needs sigma near 0.25 to 0.28 rad, 2.5 to 3 times the only
   hardware-backed residual bound (0.1 rad, 6-mode glass).
5. Model-based fits with about one sample per parameter work on hardware;
   ratio reconstruction at 24 modes needs about 3e11 counts.

Design rules taken from it, in order:

1. Gate a QPU job on calibration state: plan records HOM and g2, and a
   one-photon diagnostic waits until HOM is back above 90 %, the settled
   state of the cited episode.
2. Run every production configuration as an ensemble of equivalent compiles
   (distinct `compilation_seed` values), report the mean and the
   between-seed spread, and select seeds on one half of the shots while
   reporting the other.
3. Key every offset fit to one calibration session; the static class is
   valid only within the session that produced its data.
4. Place blocks to minimize MZIs crossed and cross states, and subtract
   instrument terms (dark clicks, per-port efficiency) before reading any
   retained fraction as optical.

## 8. The 84/84 box-kite program

The census's seven box-kites hold 84 edges, each a pair of assessors whose
diagonals multiply to zero for two sign choices (`zero_signs`). For every
edge and sign choice, `qd_belenos_mesh.edge_coverage` builds x = e_i + s e_j
and y = e_k + t e_l, certifies |x y|^2 = 0 through `cd_core.cd_multiply`,
flips t for the bright control (|x y|^2 = 8), computes the sign block
M = [[g(i,k), s g(j,l)], [s g(j,k), g(i,l)]] and looks up the single-series
configuration whose retained block carries the same (M, t). The 168 zero
products use 8 dark configurations (single jobs 05, 06, 08, 11, 16, 19, 21,
22; 18 or 24 uses each) and the 168 controls 8 bright ones (04, 07, 09, 10,
17, 18, 20, 23), so `belenos_mesh/job-02` carries all of them as sixteen
iterations of one job, and `--check` recomputes the coverage from the
census. The same collapse holds at every dimension the two-blade census
covers: the 32 one-photon configurations carry all 336, 5040 and 52080
signed two-label zero products at D = 16, 32 and 64
(`docs/evidence/box_kite_census/two_blade_blocks.json`), so the full
32-configuration job is the D = 64 program as well. A one-hot D = 32
encoding needs 34 modes, beyond the chip's 24.

## 9. Open conjectures and their falsifiers

| Conjecture | Test | Falsifier |
|---|---|---|
| The QPU leakage comes from fitting a 24-mode unitary | belenos_diagnostics job-01 against single/job-04 | settled: a 4-mode circuit compiles to the same 24-mode random-start mesh |
| The transpiler re-fits native gates as a unitary | diagnostics job-01/02/03 on sim:belenos | settled: every form compiles to the full mesh, with form-dependent phases |
| The server runs iterations in one job on one compiled mesh | belenos_fringe on sim:belenos | settled: one job and one credit, one compiled mesh per iteration |
| The chip implements U, not its transpose | the RCA's convention variants | settled offline: U^T fits at TVD 0.546 |
| The server runs an architecture-form circuit without re-transpiling | belenos_mesh job-00 (S3) and job-01 (S4) on sim:belenos | settled: refuted, all 574 phases change in both forms |
| The transpiler is exqalibur's CircuitOptimizer with photon-free modes ignored | local replay against the S3 meshes | settled statistically; bitwise replay open (server seed mapping) |
| The photon is misrouted into another source mode | source models on the returned meshes of belenos_mesh job-00 on qpu:belenos | the misroute class fits and outscores every other class |
| The chip's error class is random heater noise | class scans over belenos_mesh job-00 on qpu:belenos | another class fits better, the static offsets gain over 10 nats held out, or no class fits |
| The chip carries static heater offsets that a user job can measure | static cross-validation over belenos_mesh job-00 on qpu:belenos | held-out gain at or below 10 nats |
| compilation_seed selects the served mesh | a seed screen on sim:belenos | two seeds return the same mesh for the same target |
| The fringe visibility separates edge from strut on hardware | the fringe settings of belenos_mesh job-00 on qpu:belenos | edge visibility within 4.5 standard errors of the strut's |

## 10. Tricks

Used:

- One architecture, many settings: an iterated job of the architecture
  circuit binds all 574 phases and the input mode per iteration, so sixteen
  different unitaries cost one credit.
- Per-iteration predictions on the returned mesh, so a re-transpiled mesh
  is still a known mesh.
- Offline transpiler replay with exqalibur to price a strategy before any
  credit is spent.

Not yet used:

- Seed screening and selection (section 7).
- `CompilationAveraging` as the model-free alternative when no error class
  stands out.
- Packing six one-photon blocks per setting (the packed series) to carry all
  32 configurations in six iterations, once the QPU's per-iteration overhead
  and multi-photon rate are measured.
- A likelihood fit of all six two-click mode pairs with V and g2, and the
  quasi photon-number-resolving detectors to recover bunched events.

## 11. Run log

| Date (UTC) | Job | Platform | Case | Credits | Result |
|---|---|---|---|---|---|
| 2026-10-17 21:35 | refused | sim:belenos | single/job-04 | 0 | HTTP 424, job name over 50 characters |
| 2026-10-17 21:36 | e12075f3 | sim:belenos | single/job-04 bright | 1.00 | a = 1 (5003/4996/0/0) |
| 2026-10-17 21:37 | 7419efb8 | qpu:belenos | single/job-04 bright | 1.01 | in_block 0.470, a = 0.256 |
| 2026-10-17 | five jobs | sim:belenos | dark, strut, one-hot, pair edge, pair strut | 5.00 | every exact ideal; strut V = 0.918 |
| 2026-10-17 22:10 | three jobs | sim:belenos | diagnostics job-01/02/03 | 3.00 | a = 1 each; every form compiles to the 24-mode mesh |
| 2026-10-17 22:12 | 685945a8 | sim:belenos | fringe edge, 8 iterations | 1.00 | visibility 0.996, offset -0.008 rad, 8 meshes |
| 2026-10-17 22:16 | one job | sim:belenos | fringe strut, 8 iterations | 1.00 | flat: visibility 0.023 (2500 samples per point) |
| 2026-10-17 23:27 | 1d7160c1 | sim:belenos | belenos_mesh job-00, 16 settings | 1.00 | every setting at its ideal (TVD 0.0002 to 0.038); all 574 phases re-transpiled; class likelihood names ideal by 352 nats |
| 2026-10-17 23:36 | e5b74123 | sim:belenos | belenos_mesh job-01, numeric form | 1.00 | 721/779 on modes 20/21; re-transpiled, max phase change pi |
| 2026-10-18 00:29 | 32b28fe8 | sim:belenos | belenos_mesh job-02, the 84/84 program | 1.00 | 8 dark configurations a = 0 (0/1500 each, Wilson upper 0.0026), 8 bright a = 1; verdict ideal (p = 0.136) |
