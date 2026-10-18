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
| Iterated job | 1 credit for 8 iterations (fringe job 685945a8, 83 s on sim:belenos); 1.003 credits for 32 iterations of 1500 samples (job b8e2ec0c, 221 s on qpu:belenos) | usage report after the fringe jobs; run record of b8e2ec0c |
| Seconds charged | `duration_seconds` in the usage report (12 to 18 s per sim job, 13 s for a 10000-shot QPU job, about 10 s per iteration) | usage report |

The job, not the shot, is the cost unit: a 10000-shot QPU job costs 1.01
credits and a 347113-shot two-photon job 1.35. Everything that puts more
configurations into one job (iterations, packing) divides the cost; nothing
that adds shots changes it materially.

## 1a. Job anatomy and names

The cases, the runner and this guide use these names. One POST is one
**job**; everything inside it is free once the job is paid.

| Name | Meaning | Authority |
|---|---|---|
| job | one POST to `/api/jobs`: billed 1 credit plus 1e-06 per billed shot, at most 300 s, one running and one queued per token | usage report, platform record |
| single job (S) | a job whose payload is one Perceval `Computation`: one circuit, one setting, one served mesh. Formerly "one-circuit job" | `job-body.json` starts `pcvlar ... Computation` |
| iterated job (I) | a job whose payload is one `ComputationIterator`: one circuit object plus K iterations, each binding its own setting and sample budget, each re-compiled to its own served mesh. One circuit, many settings; not several circuits | `job-body.json` starts `pcvlar ... ComputationIterator` |
| iteration | one entry of an I job, answered by one `results_list` entry with its own `computed_circuit` and counts | `raw/result.json` |
| setting | what the chip is asked to realize: the circuit's unitary or phases, the input state and the `compilation_seed` (absent: the service's default) | case `cases.json` |
| served mesh | the 574 phases the transpiler returned for a setting, named by the first 8 hex digits of the sha256 of the unzipped `computed_circuit` (29dc6ef8) | `qd_belenos_mesh.mesh_sha` |
| sample | one kept detection event (after `min_detected_photons`); `max_samples` bounds them | Perceval `sample_count` |
| shot | one trigger the service counts for billing; on one-photon cases shots used equal samples kept | `nb_shots_used` in each result |
| dwell | the samples (and seconds) spent consecutively on one setting: 10000 in Q1's S job, 1500 per iteration in every I job so far | case budgets, `duration` |
| packing | several independent blocks side by side in one circuit, so one setting measures several configurations | `box_kite_photonic_packed` |
| cell | one (form, dwell, mesh) combination with its measured in_block | section 7 item 10 |

Billing measured on the retained jobs: S jobs charged 1 + 1e-06 x shots
(1.01 for 10000, 1.0015 for 1500). I jobs charge 1 + 1e-06 x the largest
iteration's `max_shots`: 1.003 for three jobs with 3000 per iteration
(36000 and 48000 shots in all) and 1.12 for job c1eb1cbb, whose largest
iteration named 120000 of its 332000. Samples spread over equal iterations
are nearly free; one long iteration bills its own shots.
Seeds. A `compilation_seed` that explores new meshes comes from the ANU
quantum random number generator: `scripts/anu_qrng.py draw` retains one
1024-value uint16 draw per request under `docs/evidence/anu_qrng/` (raw
response, sha256, UTC time) from the keyed ANU Quantum Numbers service
(100 requests a month, key in `~/.config/anu-qrng/api-key`) or, with
`--source legacy`, the keyless service at one request per minute, and a case names the draw file and the index of every value it
takes, consuming values in index order, so no value seeds two cases. A seed
that reproduces a known served mesh (seed 20 for 29dc6ef8, seed 1 for
e296b6a9) is an identifier and stays fixed. The seeds 0 to 21 of job-09
predate the rule.

Time on qpu:belenos: an S job takes 13 to 15 s whether it collects 1500 or
10000 samples (aa4218f1, a5f0a8a4, Q1), so its duration is overhead. I jobs
fit about 6.3 s per iteration plus 26 us per sample (c2eea262: 24 iterations,
36000 samples, 152 s; c1eb1cbb: 9 iterations, 166000 samples, 61 s); the
setting count, not the samples, fills the 300 s limit, and acquisition runs
near 4 x 10^4 one-photon samples per second.

## 2. Platform facts that shape a case

- **Job names** are stored in a varchar(50); a longer `job_name` answers
  HTTP 424 "value too long for type character varying(50)". The runner names
  a job `SERIES/job-NN` and refuses longer names.
- **sim:belenos** applies its own default noise model when the payload sends
  none: g2 0.003, indistinguishability 0.92, transmittance 0.06 (result field
  `noise`). It is not the QPU's live figures (g2 1 %, HOM 92.6 % on
  2026-10-17), so a sim prediction of a QPU number sends the QPU's
  NoiseModel or recomputes locally.
- **Rates.** A 10000-sample S job lasts 13 s, but that is overhead: the
  166000-sample I job c1eb1cbb places acquisition near 4 x 10^4 one-photon
  samples per second (section 1a), the order of the clock times
  transmittance estimate, not the 770 per second a job's duration suggests.
  Perceval defines a result's `physical_perf` as the share of trials that
  pass the detected-photon filter; reading one trial per source pulse at the
  4.94 MHz catalogue clock, a model no Quandela document confirms, estimates
  the detector read time as samples / (physical_perf x clock): 0.03 to 0.27 s
  per job or iteration over Q1's circuit, against `status.duration` of 13 to
  221 s
  (`docs/evidence/quandela/belenos_light_cone.json`). physical_perf follows
  the requested budget: on 29dc6ef8 at seed 20 within one job it reads
  0.0030, 0.0225, 0.0522 and 0.0528 at 1500, 10000, 40000 and 60000
  samples, and D3's 10000-sample single job read 0.069 against 0.021 for
  its iterated twin. A share of trials fixed by the optics would not move
  with the budget, so physical_perf is no transmission and the time
  estimate is no independent clock. Perceval 1.3.1's DetectorBalancing also
  multiplies physical_perf by a correction factor. The 0.03 to 0.27 s values
  are conditional calculations under an unconfirmed acquisition model: they
  exclude no timing, settling or acquisition mechanism and bound no dark
  count.
- **Mitigation and filtering.** No retained job body carries a
  `mitigations` field, and qpu:belenos's `default_mitigations` decodes to
  `[DetectorBalancing]`, so every retained count passed the service's
  default processing. In Perceval 1.3.1, DetectorBalancing turns the
  subcomputation into `probs`, corrects the distribution by detector and
  output-loss models, and the common mitigation layer converts it back to
  the requested command, which can regenerate counts from corrected
  probabilities (`error_mitigation/detector_balancing.py`,
  `abstract_mitigation.py`, `utils/conversion.py`); the retained artifacts
  do not establish the server-side processing of these acquisitions, so the
  histograms are not assumed to be unmitigated detector records. All 192 retained
  QPU result entries (single jobs and iterator entries) report
  `final_mode_number` 24, which excludes a cutoff to a smaller output
  register; photon-number selection (`min_detected_photons` 1), event
  rejection, correction or resampling that keeps 24 modes stay open. The `apply_emt` flag the bodies carry belongs to
  the command and gates Perceval's client-side mitigations only.
- **Off-cone clicks.** Every mode of the full mesh is reachable from the
  source, so the light cone of a served mesh is defined by amplitude: the
  modes its ideal propagation passes through, joined with every mode the
  exact dephasing channel at 0.5 rad of heater and 0.1 rad of coupler noise
  detects at 1e-3 or more (`scripts/qd_belenos_cone.py`). That noise drops
  in_block to about 0.5 and still puts at most 1.2e-4 of the photon on modes
  0, 1 and 5. One-click samples outside the cone sit mostly on those three
  modes, the three highest receipt dark rates, and come and go: three
  identical 1500-sample iterations of 29dc6ef8 in one job read 0, 0 and 81
  on mode 5, the 40000-sample iterations of 29dc6ef8 and 14a96ca6 read 1671
  and 5541 off-cone clicks, and 15 of 24 bridge iterations read none where
  the receipt rate over the estimated acquisition time predicts 2 to 19.
  Off-cone clicks share no sample with an in-cone click in every cell but
  one, where independent clicks gated to the source pulses would put up to
  329 such pairs; the exception is a 60000-sample iteration with 135 pairs
  of mode 7 and mode 20. No single wrong source mode reproduces the off-cone
  histograms (best TVD 0.55 to 0.78 over all eleven). The origin is open:
  clicks derived from the photon on a fixed set of output channels fit the
  exclusion, and independent noise fits it only if the acquisition is not
  pulse-gated. Neither time base of the receipt's rate predicts these
  clicks; the light-cone reading excludes them without a model.
- **Compilation.** Both the simulator and the QPU return `computed_input`
  and `computed_circuit`. For a 24-mode circuit the compiled circuit is the
  full chip mesh: 552 beam splitters (Rx convention, calibrated angles such as
  1.5867 against pi/2) and 574 phase shifters, so a photon crosses about 48
  elements whatever the block's size. For the one-circuit single/job-04
  body the sim and the QPU returned byte-identical compiled circuits, and the
  QPU returned the same circuit again after a calibration. The iterated
  belenos_mesh/job-02 body returned sixteen different meshes on the QPU than
  on the sim (bodies equal but for platform and process_id, couplers
  unchanged), while the QPU returned all sixteen meshes of job-03 again for
  the repeated body: the QPU is self-consistent, and a sim mesh predicts an
  iterated QPU mesh only through the same target.
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
  `input_state`: every block unitary that fits the 300 s limit costs the
  same one credit. A
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
  clicks, the receipt's per-mode rate times the estimated acquisition
  seconds (`acquisition_seconds`), a few clicks per job. The receipt's rate
  does not describe the off-cone clicks a histogram carries (section 2): in belenos_mesh job-03 on qpu:belenos modes 0 and 1, the two
  highest receipt rates, read zero clicks in every setting whose ideal leaves
  them dark, and elsewhere they come and go. The model-free statistic is
  in_block_cone, in_block over the one-click samples inside the source's
  light cone of the served mesh (`scripts/qd_belenos_cone.py`, gate
  core-546); raw in_block counts the off-cone clicks as leakage. The record
  keeps the one-click account N_B, N_C\B and N_off per cell, so
  in_block = cone_share x in_block_cone, and the label share (the block's
  label roles over every one-click sample): in_block_cone counts the
  block's dilation modes as retained, which a transformation that moves
  light onto them reads as success.
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
  setting's share of the job's wall time, capped by the mode's lowest click
  fraction over the job's settings (the cap, not the rate, sets the term;
  the preregistered fits that consume it keep this definition) (Q1's receipt predicts 277 dark clicks on mode 0, which
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
one-click samples on modes 20 to 23 (0.471 after subtracting the receipt's
dark rates over the estimated 0.27 s acquisition), with the
leaked light on modes 17 (0.178 of the dark-subtracted histogram), 18
(0.094), 19 (0.064) and 16 (0.048), 0.065 on the off-cone mode 5, and 0.38
of the in-block light on the
dilation modes that should be dark. Every conjecture below was tested
offline against the retained raw bytes
(`docs/evidence/quandela/belenos_leakage_rca.json`, efficiency-weighted
total variation distance against a shot-noise floor of 0.013):

| Conjecture | Evidence | Verdict |
|---|---|---|
| Our circuit or encoding is wrong | the decoded compiled mesh gives (0.4999, 0.5001) on modes 20 and 21 and matches Perceval's own BS/PS build to 5e-16; `computed_input` is the photon on mode 20 | refuted |
| Extra photons or entanglement (other sources firing, g2) | 1 event of 10000 has more than one click; with one photon there is no multi-photon state to entangle | refuted |
| Serialization or convention (transpose, mirrored modes, reversed order, negated phases, theta to pi - theta) | best variant TVD 0.414 against 0.880 for the ideal, none near the floor | refuted |
| Coupler (theta) errors | a common shift of 0.1 rad keeps 0.99 of the light in the block; 0.05 rad noise keeps 0.99 | refuted as the main cause |
| Random heater phase noise | the exact dephasing channel reaches TVD 0.273 only at sigma 0.5 rad on every heater and puts the leak on 18 and 19 rather than 17 | not supported at a physical size |
| Heater gain, thermal crosstalk, phase ceiling | best one-parameter fits TVD 0.283 (gain -0.3), 0.379 (crosstalk 0.15), 0.348 (ceiling 4.95 rad), all twenty times the floor | open, none explains the run |
| Wrong photon: the demultiplexer routes the photon into another source mode | the compiled mesh's column 18 fits at TVD 0.331, as well as any physical model | open, tested by the identity settings below |
| Device state: the run preceded a calibration (status `calibration` 40 minutes later) | the exact replay (job 7af74302) ran the identical mesh 29dc6ef8 under the next calibration at HOM 57.6 % and kept 0.504 of one-click samples in the block (Wilson 0.494 to 0.514) against 0.470 (0.460 to 0.480), with the leak on modes 17 to 19 again | refuted: the leak is a fixed pattern of the mesh, stable across the calibration that moved HOM |

The conclusion is that the error is in the chip's realization of a
correct circuit, a single-photon interferometer error of at least 0.5 rad
equivalent per heater or a misrouted photon, and that one run cannot
separate the classes. The discriminating job is `belenos_mesh/job-00`:
sixteen settings whose returned meshes respond differently to each class.

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
   (HOM 92.6 % at the Q1 run, 57.6 % after the next calibration). The HOM
   figure measures the source's indistinguishability, not the mesh: the
   replay of Q1's identical mesh at HOM 57.6 % kept the same leak (in_block
   0.504 against 0.470, raw). Resolved: every plan records
   the live performance figures, two-photon cases wait for HOM to recover,
   and one-photon cases are gated on the live-architecture check alone.
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
   estimates one offset per heater, shared by all settings of a calibration
   session, by MAP under a Gaussian prior, with the exact adjoint Jacobian
   (`jacobians`, equal to a central difference to 4e-10), and
   `static_cross_validation` scores each fold (one run of a campaign) with
   offsets fitted on the others against the dephasing ensemble fitted on the
   same folds. Two traps were found and closed on the way. Scored against the
   nominal mesh, any offset vector "won" by about 1e5 nats on dephasing and
   out-of-family truths, because it only spread light where the nominal mesh
   puts none; the baseline is now the fitted ensemble. And one 16-setting job
   cannot identify 574 offsets: on the S3 block meshes the fit drives
   training TVD below the shot-noise floor while held-out TVD stays at 3 to
   12 floors, even from the true offsets. With uniform-random meshes (the
   transpiler's statistics) on the 12 connected inputs, 48 training settings
   recover 0.1 rad offsets to correlation 0.89 with held-out TVD at 1.2
   floors, and 192 to 0.95 at 1.0. Static offsets therefore need a
   characterization campaign of about 64 random-target settings in one
   calibration session; a single block job reads "not identifiable".
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
  qpu:belenos spent 6.7 to 8.5 s per iteration of 1500 samples over the six
  16-iteration jobs (fit 6.18 s per iteration plus 0.732 ms per sample) and
  ran 32 iterations in 221 s (job b8e2ec0c). The 300 s limit bounds the
  count: at the slowest measured 8.5 s a QPU job plans at most 35
  iterations of 1500 samples, and no service limit on iterations has
  appeared up to 32. A simulator validation of a job longer than 23
  iterations splits into parts that each stay under 300 s.

**The characterization campaign this implies (C1).** Four iterated jobs of
16 one-photon settings each, Haar-random target columns on the 12 connected
inputs in rotation, submitted back to back inside one calibration session
(every plan checks the couplers): about 4.1 credits. Each run is one fold of
`--static`, the class scans run on all 64 returned meshes, and the source
models test the misroute on every input. Its output is a session-keyed
offset vector that predicts the realized column of any mesh the transpiler
returns, which turns seed screening from a heuristic into a computed choice:
compile candidates on sim:belenos, predict each under the fitted offsets,
and send the best. The local transpiler replay converges on 96 % of random
targets (8 of 220 failed), so a campaign plans a few spare settings.

**What C1 measured (qpu:belenos, jobs f945a01d, fa847dfd, 0f0f242b,
445e0482; 4.01 credits).** All 64 settings ran (1500 samples
each: 95,988 one-click and 12 multi-click events in 96000), every mesh was re-transpiled, and
the couplers equaled Q1's throughout.

1. Preregistered verdict: every job reads "no class fits" (median TVD 9.6
   to 15.4 shot-noise floors), and `--static` declares no offsets (held-out
   gain about -79000 nats against fitted dephasing; L-BFGS endpoints of
   this unidentified 574-offset fit move by up to 3 % between BLAS builds).
2. The instrument model behind that verdict is wrong. The receipt's `t_out`
   reads 3 to 6 % on modes 0 to 11 and 194 to 400 % on modes 12 to 23, yet
   modes 0 to 11 collect about twice the clicks of modes 12 to 23; the
   receipt's dark rates predict about 150 clicks per setting on mode 0 where
   the chip reads none. Between Q1 and the replay the clicks of modes 12, 14
   and 16 moved against their `t_out` changes. Integer `sample_count`
   counts do not show that `DetectorBalancing` left them untouched: the
   service default applies it, and Perceval 1.3.1's mitigation layer can
   regenerate counts from corrected probabilities (section 1, Mitigation
   and filtering).
3. Fitted efficiencies (`--efficiency`, committed before it saw the four
   runs; job-03 had been examined in sample): one relative factor per output
   mode, fitted with each class and held out by run. The held-out median TVD
   falls to 4.2 floors (absolute 0.149, range 0.031 to 0.273, floor 0.034),
   every class's best point sits at or next to its null magnitude, and no
   class passes; static offsets with fitted efficiencies lose to fitted
   dephasing held out (about -34000 nats), so the residual is not one offset
   vector shared across runs. The factors put modes 0 to 11 near 1.2 and
   12 to 23 near 0.7; mode 5 reads 6.6 and also collects light the ideal
   places on modes 0 and 4.
4. Sensitivity (exploratory). Per-run independent heater offsets reproduce
   C1's held-out absolute TVD at about 0.08 rad rms, and at that size the
   bright-block mesh 29dc6ef8 keeps a predicted in_block near 0.95 (0.86 to
   0.97 at 0.1 rad); the observed 0.47 to 0.50 needs about 0.4 rad, which
   would triple C1's TVD. Settings whose light lands on modes 16 to 23 show
   about twice the held-out TVD of inputs 0 to 4, so the error is regional,
   but not at the size the bright block's leak needs. The leak is therefore
   specific to that job, its numeric unitary form or its sparse target, and
   not the chip's generic error (inference, moderate confidence: a
   mesh-form job with sparse targets in the same coupler state raises or
   lowers it).
5. The preregistered follow-up (`followup-preregistration.json`, committed
   before submission; readout `followup.json`). belenos_mesh job-02 on
   qpu:belenos (job 4e208d22) kept a median in_block of 0.952 over its
   sixteen block configurations, above the 0.924 job-specific threshold
   recomputed on the meshes it returned: **Q1's leak belongs to its
   one-circuit numeric-unitary job, not to sparse targets.** Q1's own target
   (bright-04) kept in_block 0.987 and a = 0.988 in the iterated form, against
   0.470 and 0.256 as a single unitary.
6. The exact repeat of C1 job-03 (job f9e13312, 36 minutes after the
   original) returned the same sixteen meshes and different histograms:
   summed G^2 2564 on 226 degrees of freedom, median TVD 0.128 between the
   runs. **The chip drifts between jobs** by about as much as C1's whole
   held-out residual against the ideal (0.149), which is why no offset vector
   fitted on three runs predicts the fourth. Q1 and its replay, whose
   one-circuit failure repeated within 0.034 across a calibration, are the
   exception that this drift does not explain.
7. The form test (`pair-preregistration.json`, readout `pair.json`):
   Q1's exact case as one circuit at compilation_seed 1 (job 8d28f121)
   compiled to a new mesh (e296b6a9) and kept in_block 0.886 (Wilson 0.879
   to 0.892, a = 0.931), against 0.470 and 0.504 on Q1's mesh 29dc6ef8.
   The preregistered rule reads **intermediate** (0.65 < 0.886 < 0.90): it
   rejects the one-circuit-form reading (at most 0.65) and withholds the
   Q1-mesh reading (at least 0.90). At seed 0 the one-circuit form returned
   29dc6ef8 both times, so form and mesh stay confounded, and one seed on
   one new mesh does not split the remaining 0.114 between a form effect
   and mesh-to-mesh scatter, which the iterated bright configurations put
   at 0.75 to 0.997 in_block. One-circuit jobs at several more seeds split
   them.
8. The seed ensemble (job b8e2ec0c, belenos_mesh job-07): every
   configuration returned three distinct meshes at seeds 0, 1 and 2, so
   **compilation_seed selects the served mesh**, and a configuration's a moves
   by a median of 0.043 between seeds (at most 0.185, bright-10). Thirty-two
   iterations of 1500 samples ran in 221 s, inside the preregistered 200 to
   290 s window: a job carries twice the settings the first campaigns sent.
9. The form-mesh bridge (`bridge-preregistration.json`, readout
   `bridge.json`, job c2eea262, belenos_mesh job-09): Q1's exact case
   iterated 24 times at compilation seeds 0 to 21, 0 and 1. Q1's
   one-circuit mesh 29dc6ef8 recurred at seed 20 and kept in_block 0.949
   (Wilson 0.936 to 0.959) against 0.470 and 0.504 as one circuit; the
   repeated seeds 0 and 1 returned their meshes again within 0.005, so the
   preregistered rule reads **form or dwell**: the leak belongs to the
   one-circuit job form or its 10000-sample dwell per setting, not to the
   programmed mesh. The effect is mesh specific: job-08's mesh e296b6a9
   recurred at seed 1 and kept 0.907 iterated against 0.886 as one circuit.
   Over the 22 distinct meshes the median in_block is 0.943 and the lowest
   0.748 (family verdict iteration). Seed 0 returned 54aef849, so the
   service's unseeded default is not seed 0. The job ran 152 s, under the
   preregistered 161 to 204 s, and was charged 1.003 credits.

10. **Next: form versus dwell (design, not run).** Four cells exist for
    Q1's circuit:

    | | dwell 1500 | dwell 10000 |
    |---|---|---|
    | S, mesh 29dc6ef8 | missing | 0.470, 0.504 (Q1, replay; unseeded) |
    | I, mesh 29dc6ef8 | 0.949 (c2eea262, seed 20) | missing |
    | S, mesh e296b6a9 | - | 0.886 (8d28f121, seed 1) |
    | I, mesh e296b6a9 | 0.907 (c2eea262, seed 1) | - |

    The leak is a property of S with dwell 10000 on 29dc6ef8 and absent on
    e296b6a9 in either form. Four designs fill the missing cells: D1 and D2
    split form from dwell on 29dc6ef8, D3 and D4 ask the same of a fresh
    mesh drawn from the ANU QRNG, so the reading is not tied to one mesh.

    - **D1, S at dwell 1500 on 29dc6ef8.** Q1's body unchanged (unseeded,
      so the service serves 29dc6ef8 as it did twice) with `max_samples`
      1500 and `max_shots` 3000: the only change against Q1 is the dwell.
      About 7 s and 1.0015 credits. Reading: at most 0.65 says the S form
      leaks at any dwell (form); at least 0.90 says the leak needs the long
      dwell (dwell); between says both. A served mesh other than 29dc6ef8
      leaves the cell missing.
    - **D2, I over a dwell ladder on 29dc6ef8.** Iterations of Q1's circuit
      at seed 20 (29dc6ef8 in c2eea262) of 1500, 10000, 1500, 40000, 1500
      and 60000 samples. The long iterations read in_block against dwell
      inside the I form; the 1500-sample iterations between them bound
      drift and any after-effect of a long dwell. A leak that grows with
      dwell here reads dwell whatever D1 reads.
    - **D3, S at dwell 10000 on a fresh mesh.** Q1's body at
      `compilation_seed` 46667, value 0 of
      `docs/evidence/anu_qrng/draw-2026-10-18T083548Z.json`: Q1's own
      condition on a mesh nobody has measured. 13 to 15 s, 1.01 credits.
      Reading: at most 0.65 says the S-form leak is generic to long S jobs;
      at least 0.90 says it needs a susceptible mesh, as e296b6a9 already
      suggests.
    - **D4, I over a dwell ladder on the same fresh mesh.** Iterations at
      seed 46667 of 1500, 10000 and 40000 samples, D3's I partner. They ride
      in D2's job, because iterations are free: nine iterations, 166000
      samples, about 47 s of overhead plus 125 s of sampling, about 170 s
      against 300 s, 1.003 credits if the billing rule holds. D3 and D4 pair
      only if seed 46667 serves one mesh in both forms, as seed 1 did for
      e296b6a9; each iteration's mesh sha256 decides it, and an unpaired D3
      still reads its S cell while D4 reads its own mesh's ladder.

    Order and stop rule: D1, then D3, then the combined D2 + D4 job, one at
    a time per the token's limit and back to back, so the cross-job drift
    stays near the 0.034 scale. D1 and D3 both reading 'needs the long
    dwell or a susceptible mesh' still leave the I ladder as the test of
    dwell inside one form, so the third job runs unless the user stops
    after the two S jobs. A fifth job, S at dwell 1500 on D3's mesh, is
    worth its credit only if D3 leaks. The three jobs cost about 3.015
    credits, about 3.13 if an I job bills its largest iteration's
    `max_shots` instead. A `samples` command in place of `sample_count`
    would return the individual events of one long S job and could resolve
    in_block over time within it, but nothing retained shows the events
    come back in acquisition order, and a shuffled list would hide a dwell
    trend and read form, so it stays unused until a job proves the order.
    The runner needs one extension for D2 + D4: a seeded iteration that names
    its own `max_samples` and `max_shots`. D3's seed is the first ANU value
    a case consumes; the next case takes value 1 of the same draw.

11. **Form versus dwell, run** (`dwell-preregistration.json`, readout
    `dwell.json`, [form-dwell-decomposition.md](form-dwell-decomposition.md)).
    D1 (aa4218f1): Q1's single job at 1500 samples served 29dc6ef8 again
    and kept in_block 0.918 (Wilson 0.903 to 0.931), against 0.470 and
    0.504 at 10000; the rule reads intermediate, 0.016 short of 'dwell'
    after its 0.034 margin. D2 (c1eb1cbb, seed 20, 29dc6ef8 in all six
    iterations): 0.993, 0.896, 0.995, 0.949, 0.940 and 0.945 at 1500, 10000,
    1500, 40000, 1500 and 60000 samples, flat (drop 0.029 within the 0.055
    short-iteration spread). D3 (a5f0a8a4): ANU seed 46667 served the fresh
    mesh 14a96ca6, which held 0.937 at Q1's 10000 samples, mesh
    susceptible. D4 (same job as D2): seed 46667 served 14a96ca6 again
    (paired) and read 0.990, 0.961 and 0.852 at 1500, 10000 and 40000,
    intermediate (drop 0.138). Read raw, 29dc6ef8 lost half its light only
    in the 10000-sample single jobs and held at 1500 samples or in any
    iterated job; the D1 endpoint is intermediate, so the cells do not
    establish what the single-job leak needs. Because an S job's 13 s is overhead and
    10000 samples take about 0.3 s of acquisition, the sample count, not
    seconds of heater dwell, is what separates Q1 from D1, which points at
    how a single job acquires a large budget (several acquisition chunks,
    re-settling between them) rather than at heater heating; that reading
    is inferred and untested. The fresh mesh shows the opposite trend, a
    loss that grows with samples inside an iterated job, at the end of a
    job that had already run 114500 samples, so position in the job and
    dwell are confounded for D4.

    **Light-cone reading** (`docs/evidence/quandela/belenos_light_cone.json`,
    gate core-546, a second analysis; the preregistered verdicts above stand
    as recorded). Inside source 20's cone every seeded iterated cell and D3
    read 0.982 to 0.995 on 29dc6ef8 and 14a96ca6: D2 0.993, 0.993, 0.995,
    0.991, 0.994 and 0.990; D4 0.990, 0.992 and 0.989; D3 0.985; the
    bridge's seed 20 0.982. D2's dip and D4's decline are off-cone clicks on
    mode 5 (977 and 5541 off-cone in all), not a mesh or dwell effect. The
    cells that lose light inside the cone are the single jobs on 29dc6ef8:
    Q1 0.507 and 0.518 at 10000 samples, D1 0.918 at 1500 and job-13
    (seeded, item 12) 0.370 at 10000, with in-cone total variation from the
    served mesh's ideal of 0.870, 0.857, 0.137 and 0.829 against 0.058 to
    0.083 for every iterated cell on the same mesh. D1 ran two minutes
    before D2 under one calibration, so the deficit follows the job form,
    not the chip's state; the single jobs on e296b6a9 (job-08, seed 1) and
    14a96ca6 (D3) equal their iterated partners, so the effect is specific to
    29dc6ef8. The bridge's 22 meshes read 0.852 to 0.998 inside the ideal
    cone, repeating within the job (seed 0: 0.991, 0.993; seed 1: 0.910,
    0.905); exact heater dephasing on each served mesh lowers every mesh
    together and fits worse than none (chi-square 1012 at sigma 0, 14305 at
    0.1), so the compile-dependent deficit lies outside the isotropic
    dephasing class. Seeded cells sit 1 to 23 shot floors from their mesh's
    ideal inside the cone (TVD 0.012 to 0.228).

12. **Seeded single job on Q1's mesh, run** (case job-13, readout
    `docs/evidence/quandela/belenos_seeded_single.json`, gate core-547).
    Q1's case byte for byte as a single job at compilation_seed 20 and
    10000 samples, preregistered on in_block over source 20's ideal cone of
    the served mesh: void unless the job serves 29dc6ef8; at least 0.95
    reads "the leak follows the unseeded single-job path"; at most 0.65
    reads "the leak needs the single-job form at Q1's budget on 29dc6ef8
    whatever the seed"; between reads intermediate. Job c0db42f6 served
    29dc6ef8 and kept 0.389 inside the ideal cone (Wilson 0.379 to 0.400;
    0.370 inside the noise-bounded cone, raw in_block 0.335), reading **the
    single-job form at Q1's budget, whatever the seed**. The same mesh keeps
    0.982 to 0.995 in every iterated cell up to 60000 samples and 0.918 in
    the 1500-sample single job, so what leaks is a 10000-sample single job
    on 29dc6ef8; seeding plays no part. Its estimated acquisition lasted
    0.10 s (physical_perf 0.020) against 0.27 s and 0.11 s for Q1 and 0.25 s
    for D1, so acquisition time does not order the cells. Its 424 clicks on
    mode 12 (Q1: 98) lie outside the ideal cone and inside the noise-bounded
    one, the signature of a realized setting far from the served phases.

    The requested experiment and its reported mesh fail to predict the
    returned distribution of these single jobs. Every single job on
    29dc6ef8 at 10000 samples puts most of its block on the dilation modes
    the ideal leaves dark: Q1 (206, 996, 1772, 1724) and (260, 1130, 1770,
    1878), job-13 (425, 1123, 849, 951) on modes 20 to 23 against the ideal
    (1/2, 1/2, 0, 0). The label modes hold 0.12, 0.14 and 0.15 of every
    one-click sample and 0.26, 0.28 and 0.46 of the block, against 0.81 to
    0.96 of every one-click sample in the passing Q1-circuit cells on
    29dc6ef8 and 14a96ca6 (other meshes include passing cells above 0.20).
    A uniform survival factor leaves the normalized distribution unchanged
    and cannot populate a dark output; loss inside the interferometer can
    alter interference, so loss as such stays open. The record does not
    separate the optical transformation from input preparation, applied
    settings, detector assignment, acquisition, mitigation or result
    assembly. The redistribution is not reproducible across single jobs:
    Q1's two runs, five hours apart, agree (modes 17, 18, 22 and 23), while
    job-13 puts 0.31 of its clicks on mode 16; the experiment bytes of the
    three bodies are identical and job-13's differs from Q1's only by its
    compilation_seed parameter, so the reported mesh identifier does not
    determine the observed behavior. The mesh hash verifies the returned
    circuit description, not the applied phases. Offline tests against
    job-13 narrow three mechanisms, each within its tested family: the RCA's
    implemented classes over their searched ranges (wrong source, U^T,
    mirrored modes, gain, crosstalk, ceiling, dephasing) fit no better than
    TVD 0.39 against a shot floor of 0.012, and the fitted gains of Q1
    (-0.30) and job-13 (+0.41) show that one gain correction describes
    neither, not that a physical gain changed sign; the ideal output of each
    of the 135 complete meshes served to this account fits no better than
    0.20 (Q1) and 0.29 (job-13), which leaves partial, foreign, mixed or
    stale-plus-error configurations open; and reweighting the passing
    10000-sample iteration by powers of the receipt's t_out leaves it 0.77
    to 0.79 from job-13, which excludes that receipt-derived family only,
    since free weights w_j = q_j / p_j fit any histogram.

13. **Single computation versus iterator payload, design** (cases job-14
    to job-16, preregistration `WRAPPER_PREREGISTERED` in
    `scripts/qd_belenos_mesh.py`, readout `qd_belenos_cone.py
    --readout-series`). The single-path failure has run three times out of
    three on 29dc6ef8 and the two reference meshes hold as single jobs
    (job-08, D3), so the remaining split is the payload class at fixed seed,
    budget and mesh. Each entry reads tvd_cone_from_ideal, which separates
    every retained cell (passing 0.058 to 0.158, failing 0.829 to 0.870):
    at most 0.20 passes, at least 0.50 fails, and an entry is void off
    29dc6ef8 or when the result's `results_list` length differs from the
    payload sent (one for job-14, none for job-15, and for job-16 its two
    attribution entries plus the 22 extension entries, 24 in all), which
    catches a service that normalizes a one-entry iterator. job-14, Q1's
    case as a ComputationIterator holding one entry (manifest
    `"iterator": true`), runs first; a pass is followed by job-15 (job-13
    again, the time control) and a fail by job-16 (two identical 10000-sample
    entries, separating the first entry's position from the entry count,
    since D2's 10000-sample entry passed second). Two jobs at most, 2.06
    credits at the shot-cap ceiling. The mitigation-off arm
    (`mitigations = []`) and the native `samples` command change the
    execution path and stay out until the payload class is read; a list
    returned under `samples` is no chronological detector stream without
    provenance, since Perceval's conversion can generate or shuffle one.

    The readout validates before it scores: a run whose `results_list`
    length differs from the payload sent reads void before any cell is
    built, and an entry reads void when its `computed_input` is not one
    photon on mode 20, its retained samples (multi-click included) differ
    from 10000, its mesh is not 29dc6ef8 or its score is undefined. job-14
    always precedes its follower, so each reading describes the ordered
    block: job-14 pass then job-15 fail tracks request form in this block,
    not a subsystem; job-16 fail then pass implicates entry position or
    preceding execution, both arms being iterators; a pair failing twice
    says two-entry repetition did not recover the iterated behavior, and a
    second entry passing shows that a 1500-sample predecessor is
    unnecessary. The case manifests' `readings` strings predate this
    wording and stay as sent; thresholds and the branch rule are unchanged.

    **job-14 ran and failed** (job 3d95587b, run
    `2026-10-18T190504Z-qpu_belenos-belenos_mesh-job-14`, readout
    `docs/evidence/quandela/belenos_payload_series.json`, gate core-563).
    The one-entry iterator returned one entry, one photon on mode 20 and
    10000 samples on 29dc6ef8 in 14 s, and read tvd_cone_from_ideal 0.823
    against a 0.004 shot floor. Its block reads (1683, 13, 1433, 1218) on
    modes 20 to 23, a label share of 0.17 of every one-click sample, with
    2058 clicks on mode 19 and 1050 and 882 on modes 14 and 15: a fourth
    wrong histogram under the same reported mesh, unlike Q1's and job-13's.
    The singleton iterator payload alone does not restore the iterated
    behavior, so the branch rule prescribes job-16.

    **job-16 extended before sending** (preregistration
    `PAIR_EXTENSION_PREREGISTERED`, readout `extension` field). Every
    failing cell on 29dc6ef8 is the first and only entry of its job at 10000
    samples; every passing large cell on it sits at position 2 or later
    (D2), and a 1500-sample first entry passes (D1). Entry duration is about
    7 s whatever the budget (job-07, job-09, job-12), so an entry, not a
    sample, is the unit of cost. job-16 keeps its two preregistered seed-20
    entries first and appends 11 blocks of (seed 46667, which serves
    14a96ca6, then seed 20), all at 10000 samples: 24 entries, about 170 s,
    a 480000-shot cap and a 1.48-credit ceiling inside the 1.49 the user set,
    which priced the series at up to 2.5 credits. The usage ledger charged
    job-16 1.02 credits (qpu:belenos free_credits 16.2055 before, 17.2255
    after) against the 1.24 the per-shot rate gives for 240000 samples, and
    job-14 1.01, so the series cost 2.03; one iterated job is the evidence
    that the charge does not scale with summed entry shots. No earlier job ran a large
    29dc6ef8 entry right after a mesh switch: job-09 switched meshes at 1500
    samples and D2 ran large entries without a switch. The readings:
    - any 14a96ca6 entry failing: the fault reaches beyond 29dc6ef8 in this
      job, and mesh specificity is not supported;
    - of the post-load seed-20 entries that read pass or fail (at least 9,
      else inconclusive), a share of 0.8 or more failing reads that a large
      29dc6ef8 acquisition fails after a mesh load, none failing that
      post-load acquisitions hold, and anything between is intermittent,
      reported as a share with its Wilson interval;
    - each is read beside the pair: a passing first entry implicates the
      job's entry count or path, a passing second entry with failing
      post-load entries implicates the load, and a failing second entry with
      holding post-load entries implicates repetition of the first mesh.

    The readout adds one validity rule after the preregistration: fewer
    than 9 readable 14a96ca6 entries read inconclusive, since void
    references show no load of the reference mesh; job-16's 11 readable
    references leave its reading unchanged.

    The extension cannot ask the first-entry question again; a 1500-sample
    first entry today (D1's order) needs its own job. No result entry
    carries a timestamp, so every position reading assumes in-order
    execution. Offline, 29dc6ef8 is unremarkable among the 135 meshes
    served to this account in mean heater phase (3rd lowest) and sits in
    the upper sixth for phases within 0.3 rad of the wrap, a weak feature
    that changes no design.

    **job-16 ran: the failure persists until another mesh loads** (job
    46b810ae, run `2026-10-18T193509Z-qpu_belenos-belenos_mesh-job-16`, 24
    entries in 149 s, readout `docs/evidence/quandela/belenos_payload_series.json`,
    gate core-563). Series verdict: the singleton and both pair entries
    failed (0.819 and 0.814), and two-entry repetition did not recover the
    iterated behavior. Their blocks, (1708, 7, 1378, 1175) and (1788, 25,
    1427, 1215), reproduce job-14's within TVD 0.04 to 0.05: one wrong state,
    stable across three acquisitions 30 minutes apart, unlike Q1's and
    job-13's. Extension: all 11 14a96ca6 entries passed (0.080 to 0.103) and
    all 11 29dc6ef8 entries that each followed a 14a96ca6 entry passed (0.078
    to 0.104; post-load failure share 0 of 11, Wilson 95 % 0 to 0.26). The
    preregistered reading: 29dc6ef8 recovers after a load of another mesh,
    while repeating the job's first mesh kept the failure. So the wrong
    state set when a job opens on 29dc6ef8 at 10000 samples persists while
    the job keeps that mesh and clears on one load of another mesh, which
    fits a service that skips re-applying the configuration between entries
    that share a mesh (inferred; no result field shows a reload). Offline,
    the stable failing histogram matches no ideal output of the 135 meshes
    served to this account (best 0.20, e3f757ed, a characterization mesh)
    and no other source mode of 29dc6ef8 (best 0.41).

    Operational procedure, nominated: an entry on another mesh before each
    29dc6ef8 entry returned 11 of 11 passing entries. It is one job on one
    target mesh, a procedure candidate rather than a causal resolution.
    The retained runs already hold that discriminator: D2 (job-12,
    c1eb1cbb) opened on 29dc6ef8 at 1500 samples and then passed at 10000,
    40000 and 60000 with no switch. Over all ten jobs carrying Q1's case,
    each of the five 10000-sample openings on 29dc6ef8 failed and each of
    the two 1500-sample openings passed (one-sided Fisher p 0.048), in
    both job forms, interleaved in time with the failures
    (docs/notes/quandela/belenos-first-load-hypothesis-2026-10-18.md).
    Open: the time-of-day control (no 10000-sample opening ran inside
    D1's and D2's two-minute window), the threshold between 1500 and
    10000, and whether either opening repairs other meshes.

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

1. Gate a QPU job on calibration state: plan records HOM and g2 and checks
   the live couplers. A two-photon case waits until HOM is back above 90 %,
   the settled state of the cited episode; a one-photon case runs on the
   coupler check alone, because the identical-mesh replay showed the
   bright block's leak unchanged across a fall of HOM from 92.6 % to 57.6 %.
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

On qpu:belenos (job 4e208d22, 1.003 credits, compilation seed 0) the program
reads algebra share a = 0.048 averaged over the 8 dark configurations (0.000
to 0.184; dark-11 the highest) and a = 0.979 over the 8 bright ones (0.936 to
0.991): a bright-minus-dark contrast of 0.931 for all 168 zero products and
168 controls of the 84 edges in one job. The values are one job's snapshot of
a chip that drifts between jobs (section 7, item 6); the seed ensemble with
split-half selection that the "no class fits" branch preregisters measures
their spread.

At seeds 1 and 2 in one 32-iteration job (b8e2ec0c) the program reads dark
a = 0.028 and bright a = 0.938 (contrast 0.910). Across seeds 0, 1 and 2 a
configuration's a moves by a median of 0.043; bright-10 (0.989, 0.994, 0.808),
bright-18 (0.988, 0.888, 0.815) and dark-11 (0.184, 0.061, 0.017) move most, so
a production readout takes the median of several seeds and jobs.
`sample_count` returns counts without shot order, so split-half seed
selection needs repeated jobs rather than a split of one.

**Sixteen-mode annihilator energy (design input, nothing sent).** For
a = e1 + e10, `cd_core.left_mult_matrix(16, a)` gives H_a = L_a^T L_a with
tr H_a = 32, tr H_a^2 = 96 and H_a (H_a - 2) (H_a - 4) = 0 in integer
arithmetic, so its spectrum is 0 (four times, the annihilator, holding
e4 - e15), 2 (eight) and 4 (four). One photon over sixteen modes measures it
through V^T (H_a = V diag V^T) and reads <H_a> = 2 p_2 + 4 p_4; K = L_a / 2
has singular values 1, 1/sqrt2 and 0 with multiplicities 4, 8 and 4, so
splitting the eight 1/sqrt2 channels on balanced couplers gives a 24-mode
dilation with twelve success outputs whose success probability is
<H_a> / 4 and whose success branch carries K's output in its twelve-mode
range. Both read every acceptance and every excluded event alongside the
conditional result, and both wait until a payload procedure qualifies
(section 7 item 13), because the compiler constrains only the occupied input
columns.

## 9. Open conjectures and their falsifiers

| Conjecture | Test | Falsifier |
|---|---|---|
| The QPU leakage comes from fitting a 24-mode unitary | belenos_diagnostics job-01 against single/job-04 | settled: a 4-mode circuit compiles to the same 24-mode random-start mesh |
| The transpiler re-fits native gates as a unitary | diagnostics job-01/02/03 on sim:belenos | settled: every form compiles to the full mesh, with form-dependent phases |
| The server runs iterations in one job on one compiled mesh | belenos_fringe on sim:belenos | settled: one job and one credit, one compiled mesh per iteration |
| The chip implements U, not its transpose | the RCA's convention variants | settled offline: U^T fits at TVD 0.567 |
| The server runs an architecture-form circuit without re-transpiling | belenos_mesh job-00 (S3) and job-01 (S4) on sim:belenos | settled: refuted, all 574 phases change in both forms |
| The transpiler is exqalibur's CircuitOptimizer with photon-free modes ignored | local replay against the S3 meshes | settled statistically; bitwise replay open (server seed mapping) |
| The photon is misrouted into another source mode | source models on the returned meshes of C1 | settled: refuted on random meshes, every misroute fraction's best point is 0 under fitted efficiencies |
| The chip's error class is random heater noise | class scans over C1 | open: under fitted efficiencies sigma 0.05 is the best point of a family that fails the fit (4.2 floors held out) |
| The chip carries static heater offsets that user jobs can measure | `--static` and `--efficiency` over the four runs of C1 | settled for this session: refuted, held-out gain about -79000 nats (receipt model) and -34000 nats (fitted efficiencies) |
| The bright-block leak is a property of its job (numeric unitary form or sparse target), not the chip's generic error | belenos_mesh job-02 on qpu:belenos scored against the C1 efficiencies, same couplers | settled: job specific, median in_block 0.952 against the 0.924 threshold; Q1's target kept 0.987 in the iterated form |
| The one-circuit job form, not the bright block's own mesh, causes the leak | Q1's case as one circuit at compilation_seed 1 (belenos_mesh job-08), then Q1's case iterated over 24 seeds (job-09), which served 29dc6ef8 at seed 20 | supported: 29dc6ef8 kept 0.949 iterated against 0.470 and 0.504 as one circuit, in-job drift 0.005; preregistered verdict form or dwell, mesh specific (e296b6a9 0.886 one-circuit, 0.907 iterated); D1 to D4 (section 7 item 11): at 1500 samples the single job keeps 0.918 on 29dc6ef8, iterations up to 60000 samples keep about 0.945, a fresh ANU-seeded mesh keeps 0.937 at 10000 in a single job; read raw, the leak appears only in the 10000-sample single jobs on 29dc6ef8 (D1 intermediate); the light-cone reading moves the in-cone deficit to the unseeded single jobs and the D4 decline to off-cone clicks (section 7 item 11) |
| Off-cone clicks are a stationary dark rate the receipt measures | light-cone reading over every Q1-circuit run | settled: refuted, 0 to 5541 clicks per cell on modes 0, 1 and 5 that come and go within a job (0, 0, 81 on identical iterations) |
| Off-cone clicks are independent of the photon | pairs of an off-cone and an in-cone click against the pulse-gated independent expectation | open: none observed in every cell but one where up to 329 are expected, which favors clicks derived from the photon unless the acquisition is not pulse-gated; no single wrong source fits (TVD 0.55 to 0.78); routing error within 0.5 rad puts at most 1.2e-4 of the photon on modes 0, 1 and 5 |
| The in-cone deficit on 29dc6ef8 follows the unseeded single-job path | case job-13 (seeded single job at Q1's budget), section 7 item 12 | settled: refuted, the seeded single job c0db42f6 kept 0.389 inside the ideal cone on 29dc6ef8 (preregistered: single-job form at Q1's budget, whatever the seed) |
| The single-job failure on 29dc6ef8 is one fixed response of the reported mesh, independent of execution context | identical bodies on one reported mesh (Q1 twice, job-13) and the one-entry iterator job-14 against its iterated cells | settled: refuted, Q1, job-13 and job-14 returned three different wrong histograms (job-13 0.31 on mode 16, job-14 0.21 on mode 19) under one reported mesh, and the iterated cells hold; a defect that depends on preparation or execution history stays open |
| The single-job failure is a stale load of an earlier complete mesh served to this account | ideal output of the 135 meshes served to this account against Q1 and job-13 | settled for those meshes: refuted, best TVD 0.20 and 0.29 against a 0.012 shot floor; partial, foreign, mixed or stale-plus-error configurations stay open |
| The single-job failure is the receipt-derived per-detector reweighting applied to one path | the passing 10000-sample iteration reweighted by powers of t_out against job-13 | settled for that family: refuted, TVD 0.77 to 0.79 under every power; arbitrary correction, mode assignment or format-dependent processing stays open |
| A one-entry iterator restores the iterated behavior on 29dc6ef8 | case job-14, section 7 item 13 | settled: refuted, job-14 (3d95587b) read tvd_cone_from_ideal 0.823 |
| A second 10000-sample entry on the same mesh restores it | case job-16, section 7 item 13 | settled: refuted, job-16's two leading 29dc6ef8 entries failed at 0.819 and 0.814 |
| The failure is a property of 29dc6ef8 in any execution context | job-16 extension: 11 29dc6ef8 entries, each after a 14a96ca6 entry | settled: refuted, 11 of 11 passed (0.078 to 0.104) |
| The chip's state fails every mesh in a job that opens badly | job-16 extension: 11 14a96ca6 entries | settled: refuted, 11 of 11 passed (0.080 to 0.103) |
| The bad opening state needs a 10000-sample opening entry (D1's and D2's 1500-sample openings passed) | a job opening on 29dc6ef8 at 1500 samples, then 10000 samples with no switch | supported by retained data: D2 (job-12) did exactly this and passed at 10000, 40000 and 60000; 5 of 5 10000-sample openings failed and 2 of 2 1500-sample openings passed (Fisher p 0.048); open: time-of-day control and the threshold |
| The compiled phases alone determine the photon's output on a seeded mesh | in-cone TVD of seeded cells against the served mesh's ideal, raw and weighted by C1's fitted efficiencies | refuted at the 0.01 to 0.23 level: seeded cells sit 1 to 23 shot floors from the ideal (29dc6ef8 a stable 0.058 to 0.083 across six iterations and every budget), C1's efficiencies do not close the gap, and per-mesh in-cone deficits up to 0.15 (seeds 1, 10, 12) repeat within a job outside exact heater dephasing |
| The same body returns the same meshes on sim:belenos and qpu:belenos | job-02 on both | settled: refuted for iterated jobs (16 of 16 meshes differ); holds for the one-circuit single/job-04 |
| C1's residual is a fixed property of each mesh within a session | exact repeat of C1 job-03 | settled: refuted, same meshes and G^2 2564 on 226 degrees of freedom (drift) |
| compilation_seed selects the served mesh | job-02 at seeds 1 and 2 (belenos_mesh job-07) on qpu:belenos | settled: 16 of 16 configurations return three distinct meshes at seeds 0, 1 and 2 |
| The bright-block leak is a calibration episode that the HOM figure indexes | exact replay of Q1's mesh after the calibration that moved HOM from 92.6 % to 57.6 % | settled: refuted, the identical mesh 29dc6ef8 kept in_block 0.504 (0.470 at Q1) with the leak on modes 17 to 19 |
| The fringe visibility separates edge from strut on hardware | the fringe settings of belenos_mesh job-00 on qpu:belenos | edge visibility within 4.5 standard errors of the strut's |

## 10. Tricks

Used:

- One architecture, many settings: an iterated job of the architecture
  circuit binds all 574 phases and the input mode per iteration, so every
  unitary that fits the 300 s limit (32 measured) costs one credit.
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
| 2026-10-18 02:55 | 7af74302 | qpu:belenos | single/job-04 bright, exact replay of 7419efb8 at HOM 57.6 % | 1.01 | same compiled circuit (sha256 9bbbaf63); in_block 0.504 (Wilson 0.494 to 0.514) against 0.470; a = 0.276; leak on modes 17, 18, 19 (1720, 1110, 769 clicks against 1773, 940, 637) |
| 2026-10-18 03:01 | f945a01d | qpu:belenos | belenos_mesh job-03, C1 run 1 | 1.003 | no class fits (median 15.4 floors); all 16 re-transpiled |
| 2026-10-18 03:04 | fa847dfd | qpu:belenos | belenos_mesh job-04, C1 run 2 | 1.003 | no class fits (14.6 floors) |
| 2026-10-18 03:07 | 0f0f242b | qpu:belenos | belenos_mesh job-05, C1 run 3 | 1.003 | no class fits (9.6 floors) |
| 2026-10-18 03:10 | 445e0482 | qpu:belenos | belenos_mesh job-06, C1 run 4 | 1.003 | no class fits (14.4 floors); `--static` declares nothing; fitted efficiencies reach 4.2 floors held out |
| 2026-10-18 03:34 | 4e208d22 | qpu:belenos | belenos_mesh job-02, the 84/84 program | 1.003 | dark a = 0.048, bright a = 0.979; median in_block 0.952, preregistered verdict job specific; 16 meshes differ from the sim's |
| 2026-10-18 03:37 | f9e13312 | qpu:belenos | belenos_mesh job-03, exact repeat of f945a01d | 1.003 | same 16 meshes; G^2 2564 on 226 dof, median TVD 0.128: drift |
| 2026-10-18 04:24 | 8d28f121 | qpu:belenos | belenos_mesh job-08, Q1's case as one circuit at seed 1 | 1.01 | new mesh e296b6a9; in_block 0.886, a = 0.931; preregistered verdict intermediate |
| 2026-10-18 04:25 | b8e2ec0c | qpu:belenos | belenos_mesh job-07, 84/84 at seeds 1 and 2, 32 iterations | 1.003 | 221 s; seed selects the mesh (16 of 16); dark a = 0.028, bright a = 0.938 |
| 2026-10-18 07:45 | c2eea262 | qpu:belenos | belenos_mesh job-09, Q1's case iterated at seeds 0 to 21, 0, 1 | 1.003 | 152 s; 29dc6ef8 at seed 20, in_block 0.949 against 0.470 and 0.504 one-circuit; verdict form or dwell; 22 meshes, median 0.943 |
| 2026-10-18 09:03 | aa4218f1 | qpu:belenos | belenos_mesh job-10 (D1), Q1's single job at 1500 samples | 1.0015 | 29dc6ef8; in_block 0.918; 14 s; verdict intermediate |
| 2026-10-18 09:04 | a5f0a8a4 | qpu:belenos | belenos_mesh job-11 (D3), Q1's single job at ANU seed 46667 | 1.01 | fresh mesh 14a96ca6; in_block 0.937; 14 s; mesh susceptible |
| 2026-10-18 09:05 | c1eb1cbb | qpu:belenos | belenos_mesh job-12 (D2 + D4), 9 iterations, dwell ladders at seeds 20 and 46667 | 1.12 | 61 s for 166000 samples; D2 flat on 29dc6ef8 (0.90 to 0.99); D4 0.990, 0.961, 0.852 on 14a96ca6; billed the largest iteration's 120000 max_shots |
| 2026-10-18 15:53 | c0db42f6 | qpu:belenos | belenos_mesh job-13, Q1's single job at seed 20 | 1.01 | served 29dc6ef8; in_block_cone 0.389 (raw 0.335); 14 s; preregistered: single-job form at Q1's budget, whatever the seed |
| 2026-10-18 19:05 | 3d95587b | qpu:belenos | belenos_mesh job-14, Q1's circuit as a one-entry iterator at seed 20 | 1.01 | served 29dc6ef8; one results_list entry, 10000 samples; tvd_cone_from_ideal 0.823; 14 s; preregistered: fail, follower job-16 |
| 2026-10-18 19:35 | 46b810ae | qpu:belenos | belenos_mesh job-16, pair at seed 20 plus 11 blocks of seeds 46667 and 20, 10000 samples each | 1.02 | 24 entries in 149 s; pair fail (0.819, 0.814); 14a96ca6 11/11 pass; post-load 29dc6ef8 11/11 pass; preregistered: recovers after a mesh load |

A QPU approval quotes the expected credits, the expected seconds and why a
local Perceval simulation cannot answer the question. Job 4e208d22's quotes
its credits and seconds; the approvals of jobs 8d28f121 and b8e2ec0c quote
the dialog's question without its option text, and `pair-approval.json` in
the session directory holds that dialog verbatim ("~2 credits" and both job
descriptions) and names the terms it lacks.
