# Belenos off-cone mechanisms case

Written case for three qpu:belenos jobs that separate the surviving origins of the off-cone packets (pool row
QPU-43). Nothing is submitted; every `--submit` waits for the owner's approval of this case. Builder:
[scripts/belenos_offcone_mechanisms.py](../../scripts/belenos_offcone_mechanisms.py). Cases:
`results/quandela/cases/belenos_offcone_mechanisms/job-00` (cases.json sha256
`3cfea723a031a0ec359c0dbcd38d0c97e873d0c7e25b4b63f806eeaa8e9d86d7`), `job-01` (`b3aaa1bd08aae40346ea989d12d3ff474e29d2b94fe39a60b1e6256552be4383`, mitigations off) and
`job-02` (`d0ec6c4906d1b0b7aceac735e61fa107026b3670563be20f4cb9663f7a937117`); all three carry the circuit of belenos_mesh/job-16 byte for byte (sha256
`69326bf0674a45e8c0005b10e2ac72cee36c122691ec0a5b542dbabb6e1fffb9`). The order is job-00 (default mitigations), job-01
(`mitigations = []`), job-02 (default), and all three run.

## Pre-flight

1. **Hypothesis.** The packets of about 47 off-cone clicks come from one of: photon-triggered episodes on the
   detectors a source lights (`episodes`), noise over an acquisition window proportional to samples (`window_samples`)
   or to samples over physical_perf (`window_time`), or the server's default DetectorBalancing processing amplifying
   rare raw clicks into packets (`balancing`). DetectorBalancing rescales and resamples modes that already carry raw
   clicks and creates none on a zero-count mode (Perceval 1.3.1 `DetectorBalancing._parse_results`), so job-01 tests
   amplification and not fabrication from zero.
2. **Quantity.** A presence is an off-cone mode other than mode 5 whose one-click count is at least 32; the off-cone
   set is the cone of the entry's returned mesh and source (scripts/qd_belenos_cone.py). Mode 5 is a separate
   secondary readout and never enters the primary count. Retained law: an off-cone mode reads 0, 32 to 99 or 100 and
   more, never 1 to 31 (58 iterated cells, packets 47.2 mean, 47.7 variance, n = 35). Contrasts of presence counts:
   job-02 against job-00 (drift), job-01 against the pooled default jobs (mitigation), source 22 against source 20
   (source), 1500 against 60000 recorded samples (level).
3. **Falsifier.** `balancing` fails when job-01 keeps its share of the three jobs near 1/3. `episodes` fails when the
   two sources read equal presences per sample. `window_samples` fails when the 1500-sample level reads presences per
   sample 17.6 times those of the 60000 level (the physical_perf ratio, 0.0528 / 0.0030). `window_time` fails when the
   levels read equal presences per sample. Void rules are in cases.json (`preregistered.void`).
4. **Predicted outcome and budget.** Under the retained primary rate of 1.084e-4 presences per sample (49 in 452,000)
   each job expects 77.5 presences, 38.8 per source, and 49.0 mode-5 presences; 227.16 s per job (8.16 s plus 7.30 s
   per entry, 30 entries; 296.16 s at 9.6 s per entry, inside `max_duration` 300); one credit plus at most 120,000
   shots at 1e-6, so at most 1.12 credits per job and 3.36 for the three. The retained data favor the sample-law share
   over the acquisition-estimate share (deviance 34.8 against 70.9, 57 df), so the prediction is `window_samples` or
   source-independent episodes, and the case reads which family. The prediction stays as recorded; a deviation is the
   finding.
5. **What each result changes.** `balancing` ends the hardware question: packets are processing output and every
   retained off-cone analysis carries that caveat; the mitigation-off arm becomes the Belenos default of cases that
   read counts. `episodes` ties the packets to the photon's detectors and opens a detector-resolved follow-up.
   `window_samples` or `window_time` fixes the noise as chip-side and sets the exposure unit of every dark-count
   correction (samples or samples over physical_perf).

## Design and its departures from the brief

- **One circuit, two sources.** The four-mode block on modes 20 to 23 of job-16 with compilation seed 20, which served
  mesh 29dc6ef8, plays through source modes 20 and 22. Measured by exact propagation on the retained mesh with the cone
  definition of scripts/qd_belenos_cone.py: of the twelve connected source modes only 20 (cone modes 8 to 23) and 22
  (modes 6 to 23) keep the hot channels 0, 1 and 5 off-cone; every other source covers them and would hide packets
  inside ordinary counts. The brief's modes 2 and 4 fail that test, so the second source is 22.
- **Source separation has a bound.** Source 20 lights detectors 20 and 21 only. Source 22 puts 59.83 percent of its
  ideal photons on detectors 20 and 21, 21.23 percent on modes 10 to 19 and 4.5 percent on mode 22 and 14.5 percent on mode 23, so
  the source-20 over source-22 rate ratio that photon-triggered packets on detectors 20 and 21 can produce is at most
  1 / 0.5983 = 1.671. No pair of connected sources on 29dc6ef8 has disjoint lit detector sets and keeps modes 0, 1 and
  5 off-cone. The power table therefore spans ratio 1 to 1.671, and ratios 2 and 3 are the reach of a second mesh,
  whose returned cone and ideal shares the live plan read states before submission. Source-independent
  photon-triggered episodes (a packet per photon burst on any detector) read equal presences per sample at both
  sources and every level, the `window_samples` signature; the design separates detector-resolved episodes only, and
  the case reads `window_samples` and source-independent episodes as one reading.
- **Source 22 may return its own mesh.** A source-22 entry is legal under whichever mesh the server returns when that
  mesh and source keep modes 0, 1 and 5 off its cone (`preregistered.void`); the cone and the ideal shares of that
  mesh replace those of 29dc6ef8 for the entry, and the returned mesh sha256 of every entry is reported. A source-20
  entry still reads void unless it returns 29dc6ef8, the identifier the compilation seed reproduces. The live plan
  read (`qd_platform.py plan`, below) names the returned mesh of a source-22 entry before the owner approves.
- **30 entries.** Job duration follows 8.16 s plus 6.00 s per entry in the ten-run fit (at most 24 entries and
  36,000 samples) and 6.9 to 9.6 s per iteration at large sample counts over the 136 completed runs of
  [quandela-credit-optimization](../runbooks/quandela-credit-optimization.md). The case plans at 7.3 s, which gives
  227.16 s, and checks 9.6 s against `max_duration` (296.16 s). The levels are 1500, 10000 and 60000 samples at 5
  repeats per source each (levels from belenos_mesh job-12, 60000 the largest retained entry), 715,000 samples per
  job. Entries come in adjacent source pairs by repeat block, so a cut at `max_duration` keeps completed pairs and
  the contrasts read the observed exposures instead of voiding the job.
- **Power.** Exact power with Poisson counts at the primary rate; the source and level contrasts pool the default jobs
  job-00 and job-02, the mitigation contrast sets job-01 against both. The retained cells show cross-mode
  co-occurrence, so each entry is an upper bound. Source rows hold the pooled total of 155.0 presences at the
  retained rate (`fixed_total`) or scale source 22 to 1 / ratio of it (`source_22_scaled`, a lower total):

  | Contrast | Truth | Power |
  |---|---|---|
  | source, 22 against 20 | ratio 1.0 (size) | 0.041 |
  | source, fixed total | ratio 1.25, 1.5, 1.671 (bound), 2, 3 | 0.256, 0.677, 0.867, 0.985, 1.000 |
  | source, source 22 scaled | ratio 1.25, 1.5, 1.671 (bound), 2, 3 | 0.233, 0.593, 0.778, 0.944, 0.999 |
  | level, 1500 against 60000 | `window_time` holds, sample-law share tested | 1.000 |
  | level | `window_samples` holds, time-law share tested | 1.000 |
  | level | sample law holds, sample-law share tested (size) | 0.033 |
  | mitigation, job-01 against both default jobs | job-01 rate ratio 0, 0.25, 0.5, 1.0 | 1.000, 1.000, 0.986, 0.046 |
  | drift, job-02 against job-00 | rate ratio 1.0 (size), 1.5, 2.0 | 0.041, 0.778, 0.999 |

  `"$PYTHON" scripts/belenos_offcone_mechanisms.py --power` prints the table; it uses no random draw.
- **Three jobs.** Perceval sets the mitigation policy once per body (`RemoteComputer.mitigations`, qd_platform
  `MITIGATION_POLICIES`), so the DetectorBalancing arm is job-01 with `mitigations = []`. It runs unconditionally
  between two default jobs: a single default job beforehand could not separate the arm from drift between jobs, and a
  presence threshold on job-00 would select on a noisy count (a null mean of 15 presences passes a threshold of 25
  in 1.1 percent of runs, and 32 percent of those read a false balancing effect). A body without the key selects the
  server default, DetectorBalancing for qpu:belenos (strategy.md, "Mitigation and filtering"); the retained
  demarrais_tower jobs already send an empty list.
- **Order.** Each repeat block lists the levels still owed, ascending; the two sources of a level alternate their
  order. The job opens with the 1500-sample entry because belenos_mesh job-12 passed its 1500-sample opening while five
  10000-sample openings failed.
- **Runner change.** A seeded setting may name `input_mode`, and the payload gives that iteration a one-photon
  `input_state` on that mode (`qd_records.iteration_form`, `qd_platform.source_state`); budgets keep their own
  rule. The shot estimate of the plan reads the base input (source 20), so a source-22 entry's shot need is unchecked:
  the cap is the retained twice the samples, and an entry that records fewer samples than its budget reads void.

## Seeds, costs, retention

- No new random seed: compilation seed 20 is the identifier of mesh 29dc6ef8 (`qd_belenos_mesh.DWELL_Q1_SEED`) and the
  power table is closed form. The ANU draw of 2026-11-27 stays unconsumed here.
- Backend qpu:belenos, command sample_count, shots 1,430,000 per job (largest entry 120,000), expected seconds 227.16,
  credit ceiling 1.12 per job (3.36 for three), `max_duration` 300 (0.9 margin 270 s).
- `"$PYTHON" scripts/qd_platform.py plan` for each job takes `--max-credits 1.12 --expected-seconds 227.16
  --per-job-credits 1`; the plan carries the catalogue architecture of 2026-10-17 (`architecture_source` "carried") and
  reads no live coupler, so each run records `couplers_checked` "unread" at plan and at collect. The live plan read of
  the returned mesh of a source-22 entry was not run when this case was written (no job token in the session). The offline payload of the three jobs, built from the catalogue
  record of qpu:belenos with a stand-in token, carries the 30 entries with each setting's input state, budgets and
  seed, and job-01's empty mitigation list (tests/scripts/test_belenos_offcone_mechanisms.py).
- Retention: `collect` writes `results/quandela/runs/<stamp>-qpu_belenos-belenos_offcone_mechanisms-job-NN`
  with the raw result untouched. The readout is [scripts/belenos_offcone_mechanisms_analyze.py](../../scripts/belenos_offcone_mechanisms_analyze.py)
  (the shared reader `qd_records.validate_run` and the cone reading `qd_belenos_cone.run_cells`, with the per-entry source
  from `computed_input`, the primary and mode-5 counts and the pair-completion rule); its record is
  [belenos_offcone_mechanisms_analysis.json](../evidence/quandela/belenos_offcone_mechanisms_analysis.json). The run enters
  docs/state/research_state.json in the change that retains it.

## Findings

Measured on the three retained runs (job-00, job-01 with mitigations off, job-02; each completed, 715,000 samples,
`couplers_checked` "unread"). `"$PYTHON" scripts/belenos_offcone_mechanisms_analyze.py --write OUT RUN RUN RUN`
validates every run with `qd_records.validate_run` and refuses on failure; `--check` recomputes the record (gate
`core-belenos-offcone-mechanisms-analysis-replay`). The test, alpha and rejection rule are the case's: the builder's
exact two-sided binomial rule (`rejection_region`), alpha 0.05. The analyst choices the case leaves open are the null
shares from the observed sample exposures, the time-law share from the case's physical_perf ratio 17.6 (the observed
physical_perf share is recorded beside it and never decides), the episodes bound on the returned mesh, and the void-job
and cut-run handling; the script docstring lists them.

- **Presences per job, source and level.** Each job reads 5 presences, all on mode 6 at source 20 and 60,000 samples
  (one per entry); every other (job, source, level) cell reads 0, so source 20 reads 15 and source 22 reads 0, level
  60,000 reads 15 and the levels 1500 and 10,000 read 0. Mode 5 reads 0 presences in every job (at most 10 clicks in
  one entry). No entry is void. The server returned mesh 29dc6ef8 (cone modes 8 to 23) for source 20 and mesh
  500c4fab (cone modes 10 to 23) for source 22, so the source-22 hypothesis of the open items is refuted: the server
  compiles source 22 on its own mesh, and the void rule admitted it. Source is therefore confounded with mesh. The
  off-cone one-click counts of 1 to 31 that the retained law excludes appear 73, 88 and 71 times (job-00, job-01,
  job-02).
- **Contrasts.** Drift, job-02 against job-00: 5 of 10, p = 1.0, does not reject. Mitigation, job-01 against the
  three: 5 of 15 against 1/3, p = 1.0, does not reject. Source, pooled over the three jobs: source 22 holds 0 of 15
  against the exposure share 1/2, p = 6.1e-5, rejects with source 22 below. Level, 1500 against 60,000 (pooled over the
  three jobs): 0 of 15 against the sample-law share 0.0244, p = 1.0, holds; against the time-law share 0.3056, p =
  8.5e-3, rejects (observed-physical_perf share 0.4125, p = 3.8e-4, also rejects). The sample-law test has little
  power at this count (about 0.37 presence expected at the 1500 level).
- **Episodes bound on the returned mesh.** Source 22 puts 0.49997 of its ideal photon on detectors 20 and 21 of mesh
  500c4fab (source 20 puts 0.999999 on them of 29dc6ef8), so detector-resolved episodes give source 22 at most the
  presence share 0.3333. Observed 0 of 15 rejects that share (p = 4.1e-3): the source split exceeds what episodes on
  detectors 20 and 21 can produce on equal samples.
- **Falsifier layer (Pre-flight 3).** `balancing` falsified (job-01 reads the same 5 presences as each default job).
  `episodes` survives its falsifier (the two sources do not read equal presences per sample). `window_samples`
  survives its falsifier (the sample-law share is not rejected). `window_time` falsified (time-law share rejected).
- **Case reading (cases.json `readings`).** `episodes`: the mitigation contrast does not reject and the source
  contrast rejects with source 22 below. `window_samples` is excluded by the same source contrast. The reading is
  `episodes` as written; the bound above and the next item qualify it.
- **Prediction as recorded against outcome.** The case predicted 77.5 presences per job (38.8 per source) and 49.0
  mode-5 presences per job at the retained rate of 1.084e-4 per sample, and the family `window_samples` or
  source-independent episodes. Observed: 5 per job (0.065 of the predicted rate; Poisson p 9e-27) and 0 mode-5
  presences (Poisson p 1e-21). The deviation is the finding: the packets of about 47 clicks on modes 0, 1 and 5 that the
  retained cells read (belenos_mesh job-16, 10,000 samples: a mode among 0, 1 and 5 reads 36 to 1154 clicks in 23 of 24
  entries) do not reappear in the 90 entries here, so the contrasts read another phenomenon, and the retained zero
  or packet law does not hold on this circuit, seed and server mode. The 15 presences are one channel: mode 6 at source
  20 reads tens of clicks at 60,000 samples (job-00: 49 to 80) and 0 to 9 below, and the source-20 cone begins at mode
  8. In job-16 mode 6 read no click at source 20 and 10,000 samples in 12 of 12 entries, against 4 of 5 entries here.
  hypothesis: mode 6 is photon-linked leakage just outside the cone threshold of source 20, a different channel from
  the retained packets; the cheapest discriminating check is the mode-6 count against samples at source 20 on mesh
  29dc6ef8 with the cone floor lowered until mode 6 joins the cone.
- **Caveat.** Couplers were unread at plan and at collect; only the 2026-10-17 catalogue stamp backs the carried
  architecture. A cut run is refused by the analyzer (the shared cone reader zips settings and entries strictly), and
  the pair-completion rule is applied to a run that reads whole; no run was cut.

## Open items

- measured: the server compiled source 22 on mesh 500c4fab, not 29dc6ef8 (Findings); the void rule accepted it.
- measured: the per-iteration input state ran on all 90 entries (each `computed_input` is one photon on its
  setting's input_mode).
- hypothesis: a cut at `max_duration` returns the completed entries of `results_list`; no run was cut, and the analyzer
  refuses one that holds fewer entries than settings.
