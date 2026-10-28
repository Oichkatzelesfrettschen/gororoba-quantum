# Provider-counter audit

This audit names what every provider counter in the retained runs counts. It traces each counter to the analyses
that divide, subtract or benchmark with it, and records which registered claims depend on it. Each output lists
the runs it covers as its `inventory`, taken from main at `d333878` (2026-10-27), and `--check` recomputes exactly
that inventory, so a run retained later leaves the check valid and enters a later audit. The Perceval definitions
are those of 1.3.1, the system package that [python-stack.md](../../notes/quandela/python-stack.md) describes. Every retained raw record, manifest and analysis
keeps its path and bytes. The replays below write only their own outputs. On every run, the audit-marked test
`tests/gororoba_quantum/test_provider_counters.py::test_audit_replays_reproduce_their_retained_output_without_touching_inputs`
replays each one with `--check` and requires `git status` over `results/` and `docs/evidence/` to stay unchanged.

| Replay | Output | Establishes |
|---|---|---|
| [quandela_counter_table.py](quandela_counter_table.py) | [quandela_counter_table.json](quandela_counter_table.json) | Top-level, per-iteration and requested counters of all 81 retained Quandela runs |
| [gate_model_counter_census.py](gate_model_counter_census.py) | [gate_model_counter_census.json](gate_model_counter_census.json) | Requested, reported and returned shots of every retained Quantum Inspire, IQM and IBM run |
| [simulator_counter_census.py](simulator_counter_census.py) | [simulator_counter_census.json](simulator_counter_census.json) | Every retained simulator count histogram against the shots its record declares |
| [exposure_sensitivity.py](exposure_sensitivity.py) | [exposure_sensitivity.json](exposure_sensitivity.json) | Every retained dark subtraction recomputed under three detector exposures |

```sh
export PYTHON="${PYTHON:-python3}" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" docs/evidence/provider-counter-audit/quandela_counter_table.py --check
"$PYTHON" docs/evidence/provider-counter-audit/gate_model_counter_census.py --check
"$PYTHON" docs/evidence/provider-counter-audit/simulator_counter_census.py --check
"$PYTHON" docs/evidence/provider-counter-audit/exposure_sensitivity.py --check
```

[provider_counters.py](../../../gororoba_quantum/provider_counters.py) carries the contract as code. A `Counter`
names its population, scope, status (observed, requested, modeled, unavailable) and source. `ratio` divides only
an inner population by one that contains it, and `total` sums only one population and status over disjoint
scopes. A requested cap or billing quantity never becomes the denominator of a trial ratio, a missing counter
stays unavailable, and a modeled exposure carries its assumptions.

## Quandela counter contract

| Field | Population | Status | Authority |
|---|---|---|---|
| per-iteration `nb_shots_used` | detection events, each a trigger with at least one detected photon | observed, censored at the iteration's `max_shots` | Perceval `runtime/simulated_computer.py` (`max_shots`: "A shot is any event with at least 1 photon"); counter table |
| returned BSCount total | photon-filtered samples (detection events passing `min_detected_photons`) | observed | counter table |
| iterated job's top-level `shots` | the job-level `max_shots` request, one iteration's cap, where it equals that request; otherwise unidentified | requested, else unavailable | counter table; [strategy.md](../../notes/quandela/strategy.md) Iterations |
| single job's top-level `shots` | detection events | observed | counter table (sim:belenos pairs: 162604 shots for 5000 two-photon samples) |
| `physical_perf` | the share of simulated events passing the photon filter (Perceval `simulators/noisy_sampling_simulator.py`); undocumented on QPU | provider diagnostic | strategy.md |
| `duration` | job wall time, compilation included | observed time, not exposure | counter table |
| source triggers, incident photons | none reported | unavailable | no result field |
| billed shots | 1 + 1e-6 x shots for a single job; 1 + 1e-6 x the largest iteration's `max_shots` for an iterated job | billing | strategy.md, measured billing |

The table supports four findings:

- **QPU detections.** 1374 of the 1380 QPU iterations that report `nb_shots_used` report exactly their returned
  samples. Every one of them ran under `min_detected_photons` 1, the only filter their runs' cases state, so every
  detection event became a sample. The 360 iterations of Ascella signed-coherence jobs 04 to 07 request equal
  `max_shots` and `max_samples` of 32768 and reach both, so neither budget is identified as the one that stopped
  them (`terminated_by` "both").
- **Shot-budget termination.** The other 6 are the teleportation rehearsal (job `55479252`). Each reported its
  whole `max_shots` of 1,200,000 and returned no three-click sample, so the shot budget ended it.
- **Simulator offset.** On sim:belenos, 25 of 72 iterations report one shot more than their samples.
- **Top-level shots.** In an iterated job, the top-level `shots` equals the job body's job-level `max_shots` in 54
  of 55 completed jobs. The exception is mesh job-14, a one-iteration list whose top-level `shots` equals that
  iteration's `nb_shots_used`.

Six iterations carry a Perceval `RuntimeError` string instead of a BSCount: the single iterations of six Ascella
jobs (input readiness checks, order pilots and the BDSC control job) that returned an error and no samples. Their sample counts stay unavailable, while an empty BSCount (`{}`) reads
zero. No retained QPU run ends by its sample budget under a filter above one photon. What `nb_shots_used` counts in that
regime therefore rests on the Perceval definition alone.

Accepted samples per detection event is an acceptance fraction. A per-trial rate or a transmittance needs a
trigger count that no result reports. Ten accepted samples of twenty detections fit twenty incident trials or two
thousand, which gives the same acceptance and different no-detection rates
(`test_equal_acceptance_leaves_the_trial_population_unidentified`).

## Gate-model census

A gate-model shot is one circuit execution that writes one classical record. All 392 retained Quantum Inspire
results report equal `number_of_shots`, `shots_requested` and `shots_done`, and that count matches their raw shot
lists. All 59 retained IBM jobs return, summed over PUBs, the `submitted_pub_shots` their collection records. Of
the 776 retained IQM circuits, 547 run without heralding and return exactly their requested shots. The other 229
run under all-zeros heralding and return a nonempty subset of them, at retention 0.2345 to 0.98925.
`iqm_jobs.shots_ok` admits that subset, and `iqm_cancellation_probe` weights each heralded circuit equally rather
than by its kept shots. Every gate-model counter is supported as recorded.

## Simulator census

A simulated gate-model shot is one sampled execution, so a supported histogram sums to its declared shots.
[simulator_counter_census.json](simulator_counter_census.json) covers 705 JSON and gzipped JSON files under
`results/kaggle/`, `results/local_compute/` and `results/local-simulation/`. Of their histograms, 1,063 on Kaggle,
5 in local compute and 336 in local simulation sum to the `shots` or `shots_per_pub` of their record, with no
mismatch. Eight Kaggle files, the GPU smoke, configuration and environment probes, declare no shots in the record;
their totals equal the shots their producers pass (`TOY_SHOTS = 200000` in `scripts/aer_gpu_probe.py`,
`shots=256` in `kaggle_kernel/gpu_env_report.py`, `shots=1024` in the smoke kernel's `run.py`), and
`aer_gpu_probe` scores its readout law against the histogram total itself. No simulator output under these trees
carries a photonic count, `nb_shots_used` or `physical_perf`; the cloud simulator `sim:belenos` is in the Quandela
counter table. Every simulator counter is supported as recorded.

## Counter-arithmetic sweeps

[sweeps/collect.py](sweeps/collect.py) runs two rules over every tracked Python file of `scripts/`,
`gororoba_quantum/` and `docs/evidence/` and writes [sweeps/findings.json](sweeps/findings.json).
[counter-arithmetic.semgrep.yml](sweeps/counter-arithmetic.semgrep.yml) is an intraprocedural taint rule (semgrep
1.164.0) from a provider counter field to a division, product, difference or sum; two full runs at its default settings
returned different finding sets, and with no per-rule timeout and one worker three full runs matched byte for
byte, so it runs with those flags (a taint fixpoint cut short by load is the likely cause).
[counter-reads.ast-grep.yml](sweeps/counter-reads.ast-grep.yml) (ast-grep 0.42.3) lists every subscript or `.get`
read of those fields. The collector names each finding by file, line and enclosing function and assigns it the class of
its function or else of its file; a finding in an unclassified file exits 1. A new finding in an already
classified file takes that file's class, and any line shift in a scanned file changes findings.json, so a replay
on a later commit runs `--write` and reviews the diff of findings.json, classes included.

The 171 findings (65 taint, 106 reads) fall into these classes: the audit's own replays and contract; Target and
circuit instruction durations, which name no provider result field; gate-model shots compared or summed within
one population (Quantum Inspire `shots_done`, QX simulator counts); `nb_shots_used` summed over disjoint
iterations as detection events (`qd_platform.result_summary`, `evidence_closure.quandela`); Quandela job
`duration` read as wall time (the job-05 iteration rule of `ascella_new_mesh_score`, the bridge and dwell
duration windows of `qd_belenos_mesh`, `bdsc_stationarity` seconds per sample, `qd_schedule`); counters echoed
without arithmetic; a local Perceval simulator's documented filter share; the inventoried sinks below; three
consumers the sink table adds below (the stray-mode ungated bound, the rehearsal delivery share and the
five-experiment acceptance fraction); and one false positive, where taint reaches statevector probabilities in
`local_photonic_compiler_crosscheck.qi_case` through a mapping that also holds `shots_done`. Semgrep cannot parse
`scripts/gl52_split_conjugators.py`; its counter words name transpiled schedule durations in dt and seeded
samples of a coset graph, both outside counter scope. Neither tool is in the CI environment, so the collector is
an operator replay at the commit it last ran on:

```sh
SEMGREP=/usr/bin/semgrep AST_GREP=ast-grep "$PYTHON" docs/evidence/provider-counter-audit/sweeps/collect.py
```

## Scientific sinks

| Consumer | Quantity | Classification | Retained effect |
|---|---|---|---|
| `qd_belenos_mesh.analyze_run` (ten mesh analyses) | dark rate x duration x `nb_shots_used` share | model-dependent, inert | `capped_dark` caps each mode's dark expectation at its lowest click fraction over the job's settings, which is zero on every mode of all ten analyses, so every retained `dark_expected` entry is 0.0 and each fit ran without dark subtraction |
| `qd_belenos_mesh.rca_record` ([belenos_leakage_rca.json](../quandela/belenos_leakage_rca.json)) | dark rate x samples / (`physical_perf` x clock) | model-dependent, robust | exposures of 0, 0.274 and 13 s keep every decisive comparison: ideal-mesh TVD 0.871 to 0.880 against a floor of 0.0124 to 0.0129, best single-parameter TVD 0.252 to 0.273, and the same convention order |
| `qd_box_kite_analysis.one_photon` `dark_corrected` (six blocks) | the same timing model | model-dependent | the algebra share `a` moves at most 2.06e-4 across exposures; the dark-corrected in-block share moves up to 0.042 |
| `qd_teleportation_rehearsal.analyze` | `attempts_benchmark` at `nb_shots_used` and at modeled attempts | model-dependent | detection events stand in for attempts, and the larger of two benchmarks covers two candidate profiles, not every profile; the one retained run reads `inconclusive` with zero samples, and `DECISION_CASES` confines the rule to that case, so a new case takes the descriptive rule with its assumption-labeled comparisons |
| `qd_belenos_cone`, `qd_box_kite_analysis.acquisition_seconds` | acquisition-time estimates; the cone's per-iteration wall share of job `duration` and its pulse-gated expectation off cone x `physical_perf` / (1 - `physical_perf`) | model-dependent, labeled | claim boundaries name the timing model as unconfirmed and gating as unknown |
| `bdsc_stray_mode_veto`, `bdsc_diagnostic`, `bdsc_stationarity` | `physical_perf` as a covariate or ordering | supported as an uninterpreted diagnostic | ranks against dark rate / `physical_perf` are reported as conditional and drive no reading |
| `iqm_jobs`, `iqm_cancellation_probe`, `iqm_signed_probe` | heralded shot counts | supported | heralding retention reported; conditional estimators use returned shots |
| `bdsc_stray_mode_veto.stray_report` `ungated_stray_share_bound` | stray dark rate x job `duration` / samples | model-dependent, labeled | wall time, which includes compilation, is an upper exposure, so the bound only rules out a stray detector live for the whole job; the retained shares lie far below it |
| `qd_rehearsal_secondary.record_state` | returned samples / requested `max_samples` (the job total, `job.samples x count`) | outside the trial contract, labeled | a budget-delivery share, not a trial ratio: it sorts the record into a preregistered state and enters no verdict of `qd_teleportation_rehearsal` |
| `experiment_analysis.analyze_qd` `accepted_vs_detected_fraction` | accepted samples / `nb_shots_used` | supported, contract-checked | an acceptance fraction of logical samples among detection events; the record's `denominator_boundary` states that incident pulses stay unknown. `test_experiment_analysis_acceptance_agrees_with_the_contract_ratio` builds collector-format runs and proves the fraction equals `provider_counters.ratio` of logical-accepted over detection-event counters on each iteration of a template job. A single answer carries no `nb_shots_used` in its result fields, so `analyze_qd` leaves that fraction unavailable while `quandela_record` reads the top-level `shots` as the detection count: an omission, never a wrong value. No retained run reaches the fraction, because teleportation job-00 returned no samples and the five other `qd-hypercomplex-cases-v1` runs `analyze_qd` accepts ended in provider errors |
| `experiment_analysis.analyze_qi` `incident_shots` | returned shots, `len(shots)` | supported, misnamed | the value counts circuit executions, the right gate-model population, and every returned shot decodes, so `unreturned_events` is 0; only the field name says incident. The name stays because the conformance records bind `experiment_analysis.py` |
| `photonic_repeat_readout.observation`, which `photonic_compilation_audit` imports | per-mode one-click counts / the one-click total | supported | each frequency conditions on reported total occupation one, the claim's boundary, and the one-click, vacuum and multiple-click counts must sum to the returned samples; `nb_shots_used`, `physical_perf`, `logical_perf` and `global_perf` are copied as `reported_*` without arithmetic, and neither pooled script reads them |

The root-cause run itself also contradicts the timing model. Under that model, 7 of its 24 modes expect more dark
clicks than they recorded; mode 0, for one, expects 5.85 and recorded 0 (Poisson probability 0.0029). Dark counts
at the catalogue rate over that exposure therefore do not reach the one-click samples. That agrees with the
registry's refutation of the receipt dark rates by the C1 runs
(`qd-belenos-bright-block-leak-survives-recalibration`). The mechanism is an inference with medium confidence: a
dark click beside the photon makes a two-click event, and gated acquisition would shorten the exposure. A provider
statement on gating would settle it.

## Claim reconciliation

| Claim | Dependency | Classification |
|---|---|---|
| `qd-belenos-bright-block-routing-deficit` | root-cause record | unchanged; exposure-robust |
| `qd-belenos-bright-block-leak-survives-recalibration` | raw in-block shares | unchanged |
| `qd-belenos-random-meshes-no-class-fits-under-receipt-model` | mesh analyses with receipt dark rates | unchanged result; the boundary now states that the cap sets every dark expectation to zero |
| `qd-belenos-q1-one-circuit-new-mesh-intermediate` | raw in-block share, mesh job-08 | unchanged |
| `qd-belenos-q1-leak-needs-single-job-and-large-budget` | raw in-block shares; 4 x 10^4 samples per second | shares unchanged; the rate is the per-sample term of a two-job linear duration fit ([strategy.md](../../notes/quandela/strategy.md) section 1) that the two jobs determine exactly, so it is conditional on that fit; the boundary now says so |
| `qd-belenos-fresh-anu-mesh-holds-single-job` | raw in-block share | unchanged |
| `qd-belenos-q1-leak-single-job-form-whatever-seed` | acquisition times 0.10 and 0.25 s | conditional on the `physical_perf` timing model, which the boundary now names |
| `qd-belenos-light-cone-reading` | acquisition-time estimates | unchanged; the boundary names the timing model |
| `qd-belenos-single-job-failure-is-a-transformation` | raw distributions | unchanged |
| `qd-belenos-teleportation-rehearsal-job-00` | `nb_shots_used` at its cap | unchanged; the boundary states that a shot is no optical trial |
| `qd-belenos-bdsc-stray-mode-veto`, `qd-belenos-bdsc-diagnostic-readout`, `ascella-signed-coherence-device-diagnostics` | `physical_perf`, plan-time dark rates | unchanged; already conditional |

## Providers without executed results

The research registry holds acquisitions from four providers: Quantum Inspire (144), Quandela (81), IBM (57) and
IQM (49), all covered above. Open Quantum holds two unsubmitted proposals,
`results/open_quantum/proposals/packed-pauli-response-ionq/` (`ionq:forte-1`) and
`.../packed-pauli-response-rigetti/` (`rigetti:cepheus-1-108q`), each with circuits and a budget and without a job
identity or result. IonQ, BlueQubit, Quafu and Origin Quantum have no tracked path under `results/`. These
providers carry no executed counter to audit; their first retained run enters a later census.

## Open provider questions

The audit leaves these as named limitations rather than measurements:

- what `nb_shots_used` counts in a sample-limited iteration under a filter above one photon on a QPU;
- what `physical_perf` measures on a QPU;
- whether acquisition is pulse-gated, and the exposure a catalogue dark rate multiplies;
- the source-trigger count of an iteration.

[Perceval issue 798](https://github.com/Quandela/Perceval/issues/798) carries the result-contract questions of the
teleportation plan.
