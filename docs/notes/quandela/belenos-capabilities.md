# Belenos capability reference

This note collects what a `qpu:belenos` job can be programmed to do, each capability with its limit, its cost and the
retained run that exercised it. It extends [strategy.md](strategy.md) (design guide), the
[credit runbook](../../runbooks/quandela-credit-optimization.md) (billing and job shape),
[platform-specifications.md](platform-specifications.md) (chip figures) and [calibration.md](calibration.md); it repeats a fact
only where the fact has no other home, and links the rest. The procedure that uses it is the `program-quandela-belenos`
skill of gororoba-infrastructure (`agent-config/skills/program-quandela-belenos/`).

Evidence classes. **doc** is a statement of Quandela's captured documentation or platform record. **run** is a value
measured on a retained run, named by its directory under `results/quandela/runs/`. **src** is a line of the Perceval 1.3.1
source read on 2026-11-28 (package `perceval`, `runtime/error_mitigation/`, `runtime/remote_computer.py`). **inf** is an
inference with its discriminating check. Two sources live on branches that have not merged (named in plain text so the link
check holds): `quandela-platform-surface` (PR 1044, the 2026-11-27 platform read) and `qd-belenos-offcone-mechanisms-case`
(the 2026-11-28 off-cone runs and the carried-architecture runner change, commit e75b5bf0c). A row marked **[PR 1044]** or
**[off-cone branch]** is a fact of that branch until it lands. No job was submitted, cancelled or created to write this note.

## 1. Chip

| Item | Value | Class and source |
|---|---|---|
| Modes, photons | 24 modes (min 1), 1 to 12 photons, threshold detectors, `support_multi_photon` false | doc; [platform-specifications.md](platform-specifications.md); read again 2026-11-27 **[PR 1044]** |
| Source (input) modes | 0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22 (`connected_input_modes`); a photon on another mode makes the cloud add a routing permutation and re-transpile | doc; strategy.md section 2 "Input adaptation" |
| Mesh | one fixed chip: 552 Rx beam splitters at calibrated angles 1.5573 to 1.6619 rad, 574 symbolic phases `phi0` to `phi573`, 276 MZIs (BS, PS on m+1 and m, BS) in 70 ASAP columns plus 22 edge phases on modes 0 and 23 | run; `docs/evidence/quandela/belenos_leakage_rca.json` (26 retained compiled meshes), decoder `scripts/qd_belenos_mesh.py` `decode` (standard-library protobuf wire reader, cross-checked against exqalibur in `--self-test`) |
| Single-photon figures, 2026-11-27 | clock 4.94 MHz, transmittance 5.37 %, HOM 88.8 %, g2 0.7 % | run (live read) **[PR 1044]** |
| Single-photon figures, 2026-10-17 | HOM 92.6 %, g2 1 % (strategy.md section 2); HOM 94.2 %, transmittance 2.89 % (platform-specifications.md, snapshot `bfcfda2`) | both dated 2026-10-17 and different; the two records are not reconciled here |
| Single-photon figures, 2026-10-20 | transmittance 6.06 %, HOM 88.5 %, g2 0.9 %, maximum dark count 412.7 per s on mode 5 | run; platform-specifications.md |
| Dark counts, per-mode transmission | `perfs.Dark counts` and `t_in`, `t_out` are lists in the live record; `t_out` is in relative units (194 to 399 over modes 12 to 23 on 2026-10-17) | doc; strategy.md section 2 "Detection" |
| Brightness | not in any record; the vendor rate formula Clock x (Transmittance x Brightness)^n has an unknown factor | unsourced |
| Compilation | every circuit is re-transpiled to the full 24-mode mesh; only the occupied column is fixed; the other 23 columns are transpiler draws | run; strategy.md sections 2 and 4 (S3 job 1d7160c1, S4 job e5b74123) |
| Phase budget | a returned mesh drives about 1800 rad of heater phase and spreads the photon over 6 to 8 modes | run; strategy.md section 4 |
| Mesh determinism | the same circuit, input and `compilation_seed` return the same `computed_circuit` within a job and across jobs (teleportation replay 6 of 6; mode-swap 8 of 8 pairs); a sim mesh does not predict a QPU mesh | run; strategy.md section 2 |
| Mesh per source | the server compiled source mode 22 on mesh 500c4fab and source 20 on 29dc6ef8 for one circuit and seed; source and mesh are confounded | run; off-cone case Findings **[off-cone branch]** |
| Light cone | the modes an ideal propagation passes through (peak occupancy above `CONE_FLOOR`) joined with the modes an exact dephasing channel (0.5 rad heater, 0.1 rad coupler) detects at 1e-3 or more; `scripts/qd_belenos_cone.py` | run; `docs/evidence/quandela/belenos_light_cone.json` |
| Off-cone clicks | mostly on modes 0, 1 and 5; law over 58 iterated cells: 0, 32 to 99 or 100 and more, never 1 to 31 (packets mean 47.2, variance 47.7, n = 35) | run; off-cone case **[off-cone branch]** |
| The 2026-11-28 runs | three jobs (90 entries, mesh 29dc6ef8 for source 20, mesh 500c4fab for source 22): the binary presence count (a mode with at least 32 one-click samples) reads 5 per job against 77.5 predicted at the retained rate and 0 on mode 5; the routing-health gate fails all three jobs (next row), so every mechanism verdict is withheld; the earlier readings "DetectorBalancing off reads the same as on", "balancing falsified" and "episodes" are withdrawn, and "the packet law did not reappear" holds only as a statement about the binary count on a routing state the chip never produced before the outage | run; `docs/evidence/quandela/belenos_offcone_mechanisms_analysis.json` **[off-cone branch]** |
| Routing-health gate | a job passes when the median of its valid source-20 entries has `in_block_cone` at or above the minimum and `tvd_cone_from_ideal` at or below the maximum of the 13 mesh-29dc6ef8 entries of belenos_mesh job-16 (retained 2026-10-18; envelope minimum 0.450, maximum 0.819, medians 0.992 and 0.092); a job without such an entry fails. The three 2026-11-28 jobs read medians of 0.158, 0.170 and 0.158 and of 0.887, 0.868 and 0.889, so none passes. The envelope derives from job-16 alone and the gate is post hoc (added after the runs were read), so it is a validity check and no preregistered test; source 22 has no baseline mesh | run; same analysis record, `routing_baseline` and `verdict.routing_gate` **[off-cone branch]** |
| Cone-floor sensitivity | the cone adds a mode whose noisy-channel occupation reaches `NOISY_FLOOR` (1e-3); recounting presences at 0.5, 1 and 2 times the floor gives 0, 5 and 29 to 32 per job, so the presence count is a function of the floor and no count is a law | run; same record, `floor_sensitivity` **[off-cone branch]** |
| Continuous click contrast | the raw primary off-cone clicks (every off-cone mode but mode 5) read 644, 451 and 621 for the two default jobs and the `mitigations = []` job (715,000 samples each): the `mitigations = []` job holds 0.263 of the clicks against the exposure share 1/3 (exact binomial p 2.8e-10, descriptive because packet counts are overdispersed), and the default-over-off click rate is 1.40. In the saturated cell (mode 6, source 20, 60,000 samples, 15 entries) the clicks read 306, 201 and 287 (ratio 1.48) while the binary indicator reads 1 on both arms and cannot see the difference; DetectorBalancing therefore amplified off-cone clicks in that cell, and whether it created packets stays open | run; same record, `click_contrast` **[off-cone branch]** |
| Heater errors | on job 7419efb8 the exact dephasing channel reaches TVD 0.273 only at 0.5 rad on every heater; the best one-parameter fits (gain -0.3, crosstalk 0.15, phase ceiling 4.95 rad) read TVD 0.283, 0.379 and 0.348 against a shot-noise floor of 0.013, so no class explains the run | run; strategy.md section 6 |
| Outage | `qpu:belenos` was unreachable from at least 2026-11-06; daily availability 0 on 2026-11-20 to 25, back 2026-11-26; weekly maintenance Thursday 08:30 to 12:00 Europe/Paris | run **[PR 1044]** |
| Server versions | Perceval `pcvl_version` 1.3.0, `pcvl-worker` 2.1.1, exqalibur 1.4.2, `hardware-core-quandela` 3.9.10, `mosaiq-belenos` 2.9.5; the local client is 1.3.1 | doc **[PR 1044]** |
| `specs.architecture`, `commands`, `default_mitigations`, `known_mitigations`, `type` | absent from the live record on 2026-11-27 (and 2026-10-20, 2026-10-30 to 2026-11-07) | run **[PR 1044]** |

## 2. Job surface

| Setting | What it does | Limit and evidence |
|---|---|---|
| Commands | `probs`, `samples`, `sample_count`, `entropy` (`available_commands`); all 78 retained `qpu:belenos` runs (platform read from each `submission.json`, commit dd460ea88) name `sample_count` in `cases.json` | doc; platform-specifications.md |
| `input_state` | the photons' source modes; one photon per source mode (`support_multi_photon` false) | doc; checked on the client by `ConstraintChecker` (`perceval/runtime/contraint_checker.py`) |
| `input_mode` (per iteration) | a seeded setting moves its one photon to a named source mode on the job's fixed circuit | src of the runner **[off-cone branch]**: `qd_records.iteration_form`, `qd_platform.source_state`; main accepts `input_mode` only in mesh settings |
| `min_detected_photons` | keeps only samples with at least that many clicks; at 1 a sample is one detection event | doc; credit runbook "Coincidences cost shots" |
| `postselect`, heralds | logical selection on the detected pattern; coincidence samples cost shots (about 1 for one photon, 74 for two, 1,800 for three) | run; credit runbook; teleportation rehearsal jobs f918c870, e7f527ce, 137c771c |
| Iterations | one `ComputationIterator` job holds a list; each iteration sets any of `circuit_params`, `input_state`, `min_detected_photons`, `max_samples`, `max_shots`, `postselect`, `compilation_seed`; circuit structure, photon filter and mitigation list are shared by the job | doc and run; `perceval/runtime/computation_iterator.py`; credit runbook "What bounds packing" |
| Seeded, template, mesh forms | seeded: fixed circuit, iterations set `compilation_seed` and budgets; template: iterations bind a state's angles and phases; mesh: iterations bind all 574 phases and an input mode | src `qd_records.iteration_form`; `qd_platform.payload` |
| `compilation_seed` | selects the served mesh; a new seed comes from a QRNG draw, a reproduced mesh keeps its identifier (AGENTS.md "Seeds") | run; strategy.md section 1a |
| `max_samples`, `max_shots` | per iteration; the job's top-level `shots` is one iteration's `max_shots`; the platform record has `max_sample_count` null | run; strategy.md section 2 "Iterations" |
| `max_duration` | 300 s counted from `start_time`; queue time never counts; a cut returns the completed iterations and bills the largest-shot ceiling | run; credit runbook "The clock" and "A cut" (708bb40d, dc348230) |
| Concurrency | `max_concurrent_jobs` 1, `max_jobs_in_queue` 1, 10 Quantum Toolbox jobs; queue depth and position need a dashboard session | doc **[PR 1044]** |
| Job name | at most 50 characters (HTTP 424 otherwise); the runner names `SERIES/job-NN` | run; strategy.md section 2 |
| Status | `plan` admits `available`, plus statuses a written case names (`running`); it refuses `calibration`, `unreachable`, `maintenance` | src `qd_platform.plan` |

### Mitigations (Perceval 1.3.1 source)

`known_mitigations` of both Belenos platforms is DetectorBalancing, CompilationAveraging, DistinguishablePhoton and
PhotonRecycling (the tags of the classes `DetectorBalancing`, `CompilationAveraging`, `DistinguishablePhotonMitigation` and `PhotonRecycling`) (snapshot 2026-10-20, platform-specifications.md). A request without a `mitigations` key selects the server
default (DetectorBalancing on `qpu:belenos` before the field vanished); only an explicit empty list fixes the policy. With
`known_mitigations` absent from the record, `RemoteComputer._use_mitigations_remotely` finds a requested mitigation unknown
and runs it on the client, which splits the job into sub-computations (src `remote_computer.py`). Every result of a
mitigation passes through `AMitigation.parse_results`: the mitigation's own `_parse_results`, then `apply_min_photons` and
`apply_post_select` (when the class flags allow), then `ConversionHelper.convert_to` back to the requested command, then
`global_perf` and `physical_perf` are multiplied by the filter yields (src `abstract_mitigation.py`).

| Mitigation | What it does to the request and the counts | Flags and limits |
|---|---|---|
| DetectorBalancing | replaces the command by `probs`, drops ports and postselection, divides each state's probability by its detection probability under the detector models (largest photon number first, subtracting the detected sub-states), normalizes, and multiplies `global_perf` and `physical_perf` by the recovered mass; the requested `sample_count` is regenerated by `probs_to_sample_count` (src `utils/conversion.py`): each state's probability gets independent Gaussian noise of standard deviation sqrt(p (1 - p) / count) from the unseeded numpy global generator, the vector is renormalized, scaled by the count and rounded, and the rounding residue goes to a random state; the counts are neither detector records nor multinomial draws, and a state of probability 0 stays 0 | `APPLY_MIN_PHOTONS` false, `APPLY_LOGICAL_SELECTION` true; assumes loss-only detectors and independent states |
| CompilationAveraging(repetitions, starting_seed) | splits samples and shots over `repetitions` sub-computations with seeds `starting_seed + i`, command `probs`, and sums the distributions; a command without `compilation_seed` is left alone; **without `starting_seed` the seed is `random.randint(0, 1_000_000)`**, which breaks the QRNG-seed rule | needs shots and samples of at least `repetitions` |
| DistinguishablePhotonMitigation(order), tag DistinguishablePhoton | for a Fock input, adds sub-computations with fewer photons (the orthogonal-bad-bits model) split by transmittance times brightness, filters outputs with more than the input photon count, requires g2 at most 0.5 | returns the input unchanged when g2 is 0 and indistinguishability is 1; overhead `overhead(input_state)` |
| PhotonRecycling | fits a decay law to the n-1 and n-2 photon events (arXiv 2405.02278); the input must hold events of both | unitary experiments with at least 3 photons; a one-photon case disables it (credit runbook) |
| Presets | `MitigationLevel` low = DetectorBalancing; medium adds DistinguishablePhotonMitigation(1) and CompilationAveraging(3); high adds DistinguishablePhotonMitigation(3) and CompilationAveraging(5) | src `mitigation_factory.py` |

The server runs Perceval 1.3.0 and the client 1.3.1, so server-side behavior is **inf**. The one measured contrast is the
2026-11-28 off-cone case, whose binary presence count (5 of 15 against 1/3, p = 1.0) hid a saturated cell: on the raw clicks of
mode 6 the `mitigations = []` job read 201 against 306 and 287 for the two default jobs (ratio 1.48, descriptive p 1.1e-6), and
all three jobs failed the routing-health gate **[off-cone branch]**. DetectorBalancing is neither shown to create nor shown to
spare the off-cone packets; a contrast between mitigation arms needs a job that passes the gate (section 1, "Routing-health
gate").

## 3. Timing and price laws

Billing. A completed job costs 1 credit plus 1e-6 times the smaller of the shots it used and its largest iteration's
`max_shots`; `plan`'s `credit_ceiling` prices the largest `max_shots` in full, so it bounds the charge and predicts it only when the
job uses its whole cap. The rule reproduces 136 completed charges to 5e-6 (credit runbook "The billing rule"; 1 + 1e-6 x largest cap is
the ceiling). Examples: 1.003 for 16 iterations of 1,500 samples (cap 3,000); 1.12 for job
c1eb1cbb (cap 120,000 per iteration; bdsc_stationarity retains 24 iterations with `max_shots` 2,880,000 in all, 120,000 per iteration); 1.06 for a 60,000-sample packed job; 4.0 for a 3-photon postselected job; 2.5 for a suppression-law job.

Seconds. Measured on the completed `qpu:belenos` runs under `results/quandela/runs/` (71 of 78 completed at commit dd460ea88,
7 canceled; the rows below cover the named series and omit the five `belenos-*-repeat-block` runs; `status.duration` over the
iteration count, recomputed 2026-11-28):

| Shape | Runs | Iterations by samples | Duration | Per iteration |
|---|---|---|---|---|
| one photon, mesh settings | belenos_mesh job-02 to job-06 | 16 by 1,500 | 107 to 136 s | 6.7 to 8.5 s |
| one photon, long | belenos_mesh job-07, job-09, job-12, job-16 | 32 by 1,500; 24 by 1,500; 9 by up to 60,000; 24 by 10,000 | 221, 152, 61, 149 s | 6.2 to 6.9 s |
| one photon, qualification | bdsc_qualification (five jobs) | 12 by 300,000 | 87 to 115 s | 7.3 to 9.6 s |
| one photon, series | bdsc_diagnostic, bdsc_stationarity, bdsc_drift_series (16 jobs) | 24 by 40,000 to 100,000 | 164 to 176 s | 6.8 to 7.3 s |
| one photon, single job | single-iteration runs | 1 by 1,500 to 10,000 | 13 to 15 s | the whole job is overhead |
| two photons, `min_detected_photons` 2 | belenos_associator_visibility job-00, job-01 | 8 by 2,048 | 101, 117 s | 12.6, 14.6 s |
| suppression law | belenos_suppression_law job-00, job-01 | 4 by 400 | 133, 68 s | 33, 17 s |
| three photons, postselected | teleportation_rehearsal job-02, job-03, job-02-replay | 6 by 1,200 | 125 to 186 s | 21 to 31 s |
| six photons in separate blocks | box_kite_photonic_packed (10 jobs) | 1 by 60,000 | 52 to 55 s | 52 to 55 s |
| six photons, five iterations | belenos_mode_swap_interleaved (8 jobs) | 5 by 30,000 | 213 to 245 s | 42.6 to 49 s |

Three fits coexist and are not reconciled: 6.3 s plus 26 microseconds per sample (strategy.md section 1a, from c2eea262
and c1eb1cbb), 8.16 s plus 6.00 s per iteration with no sample slope (ten-run fit with R^2 1.000 **[off-cone branch]**), and
the table's 6.2 to 9.6 s range. Use the table for a shape a retained job ran, the fit with margin 0.9 for planning, and the first
job of any new shape as the measurement. Planning arithmetic is the credit runbook's: credits J (1 + 1e-6 h n) and
seconds J k t(n), with J = ceil(N / k) and k = floor(0.9 x 300 / t).

The retained-rate comparison is the owner's pre-flight rule (2026-11-15) applied to a job: before approval write five lines
(hypothesis; the quantity with its primary-source definition; falsifier; predicted outcome with the budget that makes it
informative, in shots, seconds, credits and power; what each result changes) and compare the prediction with every retained
measurement of the same shape in the tables above; a deviation is the finding. The off-cone mechanisms case
**[off-cone branch]** is the worked example: it predicted 77.5 presences per job at the retained rate and read 5.

## 4. The runner and its checks

`scripts/qd_platform.py` (commands `snapshot`, `observe`, `check`, `facts`, `plan`, `review`, `submit`, `recover`, `collect`,
`runs`). Run it with the Perceval interpreter of [PYTHON.md](../../PYTHON.md) and the token file named by
`QUANDELA_TOKEN_FILE` ([providers.md](../providers.md)); the compute workstation's system `python3` lacks Perceval, and a
submit there uses the isolated Quandela environment. The runner pins Perceval 1.3.1 (`RUNNER_PERCEVAL`).

| Stage | Fail-closed checks (each raises `PlatformError`) |
|---|---|
| `plan` (read-only) | finite non-negative `--max-credits`, `--expected-seconds`, `--per-job-credits`; `--max-credits` at most the case's `max_credits`; platform named in `cases.json`; scatter-check refusal; Explorer and processor status in {available} plus admitted statuses; `max_duration` at most the platform's; expected seconds at most `max_duration`; credit ceiling (largest `max_shots` times the live price plus the per-job price) at most `--max-credits`; `hom_warning` prints, and holds nothing, for two photons in one block below HOM 90 % (88.8 % today); `live_mesh` for mesh cases; `live_architecture` for seeded cases; token capacity (idle token, or one free queue slot for a successor case); Perceval's shot estimate at most `max_shots`; `payload_version_basis` restores the command set from a frozen record of the same worker when `specs.commands` is absent |
| `architecture_blob` | returns the live record's `specs.architecture` or raises "the live record has no specs.architecture, so its couplers cannot be checked"; `live_mesh` calls it, so no mesh case plans while the field is absent **[PR 1044]** |
| `live_mesh` | refuses a mesh case whose couplers, symbols or operation order differ from the live architecture; with `specs.architecture` absent it raises, so no mesh case plans today **[PR 1044]** |
| `live_architecture` | main: a seeded case on `qpu:belenos` refuses when the live record has no architecture. **[off-cone branch, e75b5bf0c, PR 1038]**: it admits on the retained catalogue's architecture, recorded as `architecture_source` "carried" with the catalogue sha256 and stamp, refuses a present `specs.architecture` that is no non-empty string, and refuses when a present architecture's couplers differ (`couplers_differ` compares the whole sequence of coupler and phase-shifter kind, mode and parameter, in order). Carried admission exists only once PR 1038 lands; a carried run fixes the server's compile model and leaves the physical routing unchecked |
| `submit` | nonempty `--approval`; `submit_wrapper` match; no `draft`; `acquisition_admission` ready; Ascella target-slot cases need an externally anchored reviewed packet; refuses a directory holding `submission.json`, `submission-state.json` or `job-body.json`; takes an `flock` beside the token file; repeats `plan`; writes the body and a `post_outcome_unknown` checkpoint before the POST, then the job id; `recover` writes a lost receipt |
| `collect` | cases sha256 equal to the receipt; retains `raw/result.json` before parsing; treats only HTTP 404 as an absent result; a recollection must equal the retained record; **[off-cone branch]** `couplers_checked` reads "live-match", "live-differ" (refuses after the raw bytes are kept) or "unread" (field omitted or retained blob digest changed), a recollection keeps the more severe state, and `compiled_couplers_checked` compares the `computed_circuit` couplers of every entry with the planned architecture ("match", "differ" refuses, "unread"); `validate_run` requires the collection's `architecture_source` to equal the plan's |
| `charged` | usage delta, or the billing rule with the largest `max_shots` in full when no delta isolates the charge |
| records | `qd_records.validate_run` checks one retained run offline: the receipt schema and the cases sha256, a nonempty approval, the body sha256 against `job-body.json`, the platform inside `cases.json`, the `results.json` schema and job id, forbidden keys, `check_couplers`, the returned payload against the sent body, the raw result sha256 and its summary against `results.json`, the mode count of every counted state, samples at most `max_samples`, and a terminal status; `check_couplers` **[off-cone branch]** refuses a carried-architecture run whose collect state is not live-match or unread |
| gates | `core-546` (light-cone reading), `core-502` (facts table against platform-specifications.md), `core-belenos-suppression-law-case-check`; `core-belenos-offcone-mechanisms-analysis-replay` **[off-cone branch]**; each case family names its own gate in its design document |
| matched mesh | not a runner check: `matched_mesh` is an Ascella transition analysis (`scripts/ascella_transition_context.py`, `ascella_transition_ci_check.py`) that compares repeats served the same mesh; a Belenos case that needs it compares returned mesh digests itself |
| approval | every `--submit` waits for the owner's approval of a written case (AGENTS.md "Hardware services"); a simulator job is a provider job and needs it too |

`scripts/qd_surface.py diff` **[PR 1044, 700714fc4]** compares the live surface (schema qd-surface-v2: value classes, sha256 digests of long strings such as `specs.architecture` and `specs.commands`, the short policy lists `available_commands`, `connected_input_modes`, `default_mitigations` and `known_mitigations`, and the Explorer price, `max_duration`, `locked`, `bookable` and status fields) with the 2026-11-27 baseline and exits 1 on a field-class or policy change; a performance-figure change alone exits 0, and a v1 baseline reads every policy item as new until it is re-read with `read --out`. Run it after each maintenance window and before a mesh case.

## 5. What we can program

Each row names the primitive, its limit, its cost, and the retained run. The circuit-size limit for every row is 24 modes
with photons only on the 12 source modes.

| Primitive | Limit | Shots and seconds | Charge | Retained run |
|---|---|---|---|---|
| Single-photon unitary sampling on the mesh (the column U[:,source]) | a unitary on up to 24 modes realized through the full mesh; one observable column per iteration, so a one-photon job sees classical-wave interference only; error in a share is dominated by the compiled mesh (std 0.0515 against binomial 0.007 per 30,000 samples) | 24 iterations by 100,000 samples, 165 to 176 s; samples cost about 2e-6 credits each and almost no time | 1 + 1e-6 x largest cap, 1.003 to 1.12 (1.12 for bdsc_stationarity and bdsc_drift_series, 1.08 for bdsc_diagnostic, 1.003 for belenos_mesh job-03) | bdsc_stationarity (five jobs), bdsc_drift_series (seven), belenos_mesh job-03 |
| Replicate compilation seeds of one circuit | each seed returns its own mesh; the spread over seeds is the measurement | five 30,000-sample iterations per layout, 213 to 245 s | 1.09 | belenos_mode_swap_interleaved job-03 to job-10 |
| Packed independent blocks (several blocks side by side, one photon each, one click per sample) | six photons in separate blocks read one click per sample | 52 to 55 s per 60,000-sample iteration | 1.06 | box_kite_photonic_packed job-00 to job-04 |
| Two-photon HOM and two-photon associator (`min_detected_photons` 2) | HOM 88.8 % is below the 90 % floor of `hom_warning`; about 74 shots per sample | 12.6 to 14.6 s per iteration of 2,048 samples | 1.262 | belenos_associator_visibility job-00, job-01 |
| Suppression law (multi-photon) | 5.5 to 5.6 million shots over four iterations | 68 to 133 s | 2.5 | belenos_suppression_law job-00, job-01 |
| Heralded and postselected three-photon gates (teleportation rehearsal) | about 1,800 shots per sample; a four-photon coincidence extrapolates to about 43,000 and six to about 25 million (inf, medium confidence) | 21 to 31 s per iteration of 1,200 samples | 4.0 | teleportation_rehearsal job-02, job-03, job-02-replay |
| Boson-sampling-like multi-photon occupations | cost per sample grows about 24 times per added photon at transmittance near 5 %, so six photons all detected do not fit one sample in a job; the platform record permits 12 photons | not run beyond three photons | not run | none |
| Iterated settings (`circuit_params`, `input_state`, `input_mode`, budgets, seeds in one job) | k = floor(0.9 x 300 / t) iterations; one circuit structure, one photon filter and one mitigation list per job | 6.2 to 9.6 s per one-photon iteration | one job per set | every iterated run above |
| Dark-subspace certificate (24-mode measurement U24 and a 160-setting preparation bank) | compression of a 24-mode unitary equal to E0 = L_x^T L_x / 2 on 16 dimensions; qualification stops at native compilation | 12 iterations by 300,000 samples, 87 to 115 s | 1.6 | bdsc_qualification (five jobs); [bdsc.md](bdsc.md) |

A Halmos dilation [[V, sqrt(I - V V^T)], [sqrt(I - V^T V), -V^T]] of an n-dimensional contraction whose Gram matrix has a full
defect needs 2n modes, so a block of at most 12 dimensions fits 24 modes as a single-photon unitary and a 16-dimensional block
does not; the dark-subspace certificate measures only the compression of a 24-mode unitary and avoids the dilation. A real matrix needs this
unitary dilation, a complex block with the same spectrum needs the same size.

## 6. Unsourced facts

- Brightness, the factor in the vendor rate formula (no record carries it).
- Queue depth and position of a job (dashboard session only).
- Server-side behavior of each mitigation (the server runs Perceval 1.3.0, the source read here is 1.3.1).
- The mode limits of `sim:slos` and `sim:sampling` (the record carries `max_photon_count` only; platform-specifications.md gives photons 2 to 12 and no mode count).
- The cause of the intermittent omission of the five QPU fields, and whether the packet law returns after the outage (open items of PR 1044 and the off-cone case).
