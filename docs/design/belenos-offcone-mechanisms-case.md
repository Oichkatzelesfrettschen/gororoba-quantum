# Belenos off-cone mechanisms case

Written case for two qpu:belenos jobs that separate the three surviving origins of the off-cone packets (pool row
QPU-43). Nothing is submitted; every `--submit` waits for the owner's approval of this case. Builder:
[scripts/belenos_offcone_mechanisms.py](../../scripts/belenos_offcone_mechanisms.py). Cases:
`results/quandela/cases/belenos_offcone_mechanisms/job-00` (cases.json sha256
`f57695a779de511dad72fc4045481396ece27e25a579de94f99d96de5963b7e3`) and `job-01` (`565e78dee1b8fda46e23b1afe43f27b5e8e4f102a0615dac9b1f2c16cc93765d`); both carry
the circuit of belenos_mesh/job-16 byte for byte (sha256 `69326bf0674a45e8c0005b10e2ac72cee36c122691ec0a5b542dbabb6e1fffb9`).

## Pre-flight

1. **Hypothesis.** The packets of about 47 off-cone clicks come from one of: photon-triggered episodes (`episodes`),
   noise over an acquisition window proportional to samples (`window_samples`) or to samples over physical_perf
   (`window_time`), or the server's default DetectorBalancing processing (`balancing`).
2. **Quantity.** A presence is an off-cone mode whose one-click count is at least 32; the off-cone set is the cone of
   the entry's returned mesh and source (scripts/qd_belenos_cone.py). Retained law: an off-cone mode reads 0, 32 to 99
   or 100 and more, never 1 to 31 (58 iterated cells, packets 47.2 mean, 47.7 variance, n = 35). Three contrasts of
   presence counts: job-01 against job-00 (mitigation), source 22 against source 20 (source), 1500 against 60000
   recorded samples (level).
3. **Falsifier.** `balancing` fails when job-01 keeps its share of the pair near 1/2. `episodes` fails when the two
   sources read equal presences per sample. `window_samples` fails when the 1500-sample level reads presences per
   sample 17.6 times those of the 60000 level (the physical_perf ratio, 0.0528 / 0.0030). `window_time` fails when the
   levels read equal presences per sample. Void rules in cases.json (`preregistered.void`): served mesh other than
   29dc6ef8, input other than one photon on the entry's source, recorded samples below the budget, or fewer than 25
   presences in job-00.
4. **Predicted outcome and budget.** Under the retained rate of 1.084e-4 presences per sample (49 in 451,500) each job
   expects 78.6 presences, 39.3 per source; 224.16 s (8.16 s plus 6.00 s per entry, 36 entries); one credit plus at
   most 120,000 shots at 1e-6, so at most 1.12 credits per job and 2.24 for both. The retained data favor the
   sample-law share over the acquisition-estimate share (deviance 34.8 against 70.9, 57 df), so the prediction is
   `window_samples` or `episodes`, and the case reads which. The prediction stays as recorded; a deviation is the
   finding.
5. **What each result changes.** `balancing` ends the hardware question: packets are processing output and every
   retained off-cone analysis carries that caveat; the mitigation-off arm becomes the Belenos default of cases that
   read counts. `episodes` ties the packets to the photon's detectors and opens a detector-resolved follow-up.
   `window_samples` or `window_time` fixes the noise as chip-side and sets the exposure unit of every dark-count
   correction (samples or samples over physical_perf).

## Design and its departures from the brief

- **One circuit, two sources.** The four-mode block on modes 20 to 23 of job-16 with compilation seed 20, which served
  mesh 29dc6ef8, plays through source modes 20 (ideal output on modes 20, 21) and 22 (modes 20 to 23). Measured on the
  retained mesh with the cone definition of scripts/qd_belenos_cone.py: of the twelve connected source modes only 20
  (cone modes 8 to 23) and 22 (modes 6 to 23) keep the hot channels 0, 1 and 5 off-cone; every other source covers them
  and would hide packets inside ordinary counts. The brief's modes 2 and 4 fail that test, so the second source is 22.
- **36 entries, not six.** At the brief's 1000, 5000 and 20000 samples per source the job holds 5.6 presences and the
  exact two-sided test rejects a source rate ratio of 2 with power 0.083 (ratio 1.5: 0.031; ratio 3: 0.284). Job
  duration follows 8.16 s plus 6.00 s per entry with no positive sample slope, so entries are the cheap lever. The case
  runs 8, 5 and 5 repeats per source at 1500, 10000 and 60000 samples (levels from belenos_mesh job-12, 60000 the
  largest retained entry), 724,000 samples. Exact power per job (Poisson counts, retained rate; the retained cells show
  cross-mode co-occurrence, so each entry is an upper bound):

  | Contrast | Truth | Power |
  |---|---|---|
  | source, 22 against 20 | ratio 1.0 (size) | 0.038 |
  | source | ratio 1.5, 2, 3 | 0.471, 0.947, 1.000 |
  | level, 1500 against 60000 | `window_time` holds, sample-law share tested | 1.000 |
  | level | `window_samples` holds, time-law share tested | 1.000 |
  | level | sample law holds, sample-law share tested (size) | 0.031 |
  | mitigation, job-01 against job-00 | job-01 rate ratio 0, 0.25, 0.5, 1.0 | 1.000, 1.000, 0.947, 0.041 |

  `"$PYTHON" scripts/belenos_offcone_mechanisms.py --power` prints the table; it uses no random draw.
- **Two jobs.** Perceval sets the mitigation policy once per body (`RemoteComputer.mitigations`, qd_platform
  `MITIGATION_POLICIES`), so the DetectorBalancing arm is a twin job, job-01 with `mitigations = []`, run only after
  job-00 reads at least 25 presences. A body without the key selects the server default, DetectorBalancing for
  qpu:belenos (strategy.md, "Mitigation and filtering"); the retained demarrais_tower jobs already send an empty list.
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
- Backend qpu:belenos, command sample_count, shots 1,448,000 per job (largest entry 120,000), expected seconds 224.16,
  credit ceiling 1.12 per job, `max_duration` 300 (0.9 margin 270 s).
- `"$PYTHON" scripts/qd_platform.py plan` for each job takes `--max-credits 1.12 --expected-seconds 224.16
  --per-job-credits 1`; its estimate step also checks the live couplers against the catalogue. The live plan was not
  run when this case was written (no job token in the session). The offline payload of both jobs, built from the
  catalogue record of qpu:belenos with a stand-in token, carries the 36 entries with each setting's input state,
  budgets and seed, and job-01's empty mitigation list (tests/scripts/test_belenos_offcone_mechanisms.py).
- Retention: `collect` writes `results/quandela/runs/<stamp>-qpu_belenos-belenos_offcone_mechanisms-job-NN`
  with the raw result untouched. The readout extends scripts/qd_belenos_offcone_packets.py (pull request 1036) with the
  per-entry source from `computed_input`; the run enters docs/state/research_state.json in the change that retains it.

## Open items

- hypothesis: the server compiles source 22 on the same mesh as source 20 (the compile reads the unitary and seed);
  the void rule on the returned mesh sha256 tests it per entry.
- hypothesis: Perceval 1.3.1 `ComputationIterator.add_iteration(input_state=...)` accepts the per-iteration state on
  a seeded circuit; the offline plan exercises it and was not run.
