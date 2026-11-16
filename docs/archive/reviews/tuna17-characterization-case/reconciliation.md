# Reconciliation of the review of pull request 931

One local reviewer ran, `codex` on `gpt-daybreak-blue-latest` at high effort ([codex-report.md](codex-report.md),
on [brief.md](brief.md)), and two red-teamers, `agy` on `gemini-4-hydrogen-high`
([agy-hydrogen-report.md](agy-hydrogen-report.md)) and on `gemini-3.8-flash-high`
([agy-flash-report.md](agy-flash-report.md)), both on [redteam-brief.md](redteam-brief.md); the Advisor reviewed
last. Each finding was checked against the source at the reviewed head. C, H and F name the reports, whose
absolute local paths and link syntax were rewritten to repository-relative code spans; the wording is theirs.

| # | Finding (reports) | Check against the source | Outcome |
|---|---|---|---|
| 1 | `--analyze` never writes `readout_within_tolerance` (C2, H1, F3) | `main()` called `analyze()` without retained rows; the test passed them directly | fixed: `retained_rows()` reads the retained context (`--retained PATH`, default the checkout's file, used when its register has the runs' qubit count); the test runs the command line |
| 2 | `sanity()` checks no outcome in batches 01 to 04 and only a 17-qubit mean in the readout batches (C3, H2, F2) | the outcome check required both readout files | fixed: each circuit with a fixed noiseless outcome (`readout-0`, `readout-1`, `t1-0`, `x90-0`) must read it on all but three qubits; `test_sanity_stops_a_batch_whose_fixed_outcome_is_wrong`. Boundary: batches 02 and 04 hold no such circuit, and no check detects a reversed bit order, since every circuit treats all qubits alike; the case text says both. A single collapsed qubit stops nothing by design: it is the finding the series records |
| 3 | the seeded test breaks the seed ledger (C6, H4, F1) | `random.Random(20261115)` in the test; `ci/seed_provenance.py --check` failed | fixed: the synthetic shots hold exact counts and no random draw; the ledger check passes (440 literals) |
| 4 | a dead qubit divides by zero and a weak one writes `NaN` (H1) | the division preceded the span check | fixed: a pair closer than 0.2 marks the row `readout_unusable` and receives no fit; JSON is written with `allow_nan=False`; tested |
| 5 | the 256-pulse endpoint bounds no coherent error, since P(0) is periodic in it (C4, H3) | cos^2(256 e / 2) returns to 1 at e = pi / 128 | fixed: the verdict requires P(0) of at least 0.5 at 32, 128 and 256 pulses; the docstring, `prediction.json` and the case drop the "upper bound"; the case lists the passing bands of e computed on a grid ([0, 1], [7, 8], [24, 25], [31, 32] in units of pi / 512, period pi / 16), so a pass bounds e only under the assumption e < 7 pi / 512; the decay length is written only when every ladder point keeps a contrast above the floor; an aliased ladder fails in `test_ladder_verdict_needs_the_256_pulse_point_and_every_point_above_the_minimum` |
| 6 | `ladder_clears` is written from the longest collected point when batch 04 is missing (F7) | `max(ladder_raw)` | fixed: written only when the 32, 128 and 256 pulse circuits are all collected; tested for a ladder that lacks the long point and for one that lacks the middle points |
| 7 | the T1 point errors treat the readout pair as exact, and a point at p = 1 receives an unbounded weight (C5, H1) | binomial variance of the point alone, floored at 1e-12 | fixed: the variance holds the binomial terms of the point and of both readout probabilities with a quarter-count term. Boundary: the covariance the shared pair puts between points is left out, stated in the docstring and the case; `test_t1_error_grows_with_the_uncertainty_of_the_readout_pair` fails when the readout terms are zeroed |
| 8 | a flat curve passes the single-exponential verdict (H1) | a slope of rounding size gives a huge length | fixed in part: `t1_beyond_window` marks a fitted T1 above ten times the longest wait; the verdict itself is unchanged, since a constant is a single exponential within the window |
| 9 | drift between the opening and closing readout pair is averaged away (H1, F6) | the mean of the pairs, no comparison | fixed: `readout_drift` and the verdict `readout_stable` per qubit |
| 10 | short-T1 qubits lose the points of batch 02; below about 3.3 us no fit and no notice (H3, F5) | `POPULATION_FLOOR` and three points minimum | fixed in part: the row reads `t1_unfitted`; the case states the three-point fits of qubits 6, 9 and 15. The delay grid is unchanged |
| 11 | "the provider's 500,000" measurements per qubit has no source (C8, H4) | no retained record holds the figure | fixed: removed from the case, the draft and the test; the cited limit is `max_number_of_shots` of the catalogue |
| 12 | the case says the QX run "has been collected" (C1) | the sentence stands under "Admission", a list of conditions | wording fixed: the list now says each condition holds before the first Tuna-17 batch and none holds today |
| 13 | the QX case names no credits and no reason a local run cannot answer it (C7) | absent | fixed |
| 14 | the limit test compares the series estimate with the per-job limit (C9) | `expected_seconds() >= 300` | fixed: `job_seconds()`, largest job 11.28 s |
| 15 | the case says the analysis rows enter `qi_retained_context.py`'s inputs (H4) | that script reads the device-context file only | fixed: the case says the reader does not exist yet |
| 16 | all 17 qubits driven and read at once: crosstalk and neighbor-dependent assignment confound each figure (H3, F4) | retained notes record both | accepted as a limit: the case states that each figure is the value in the all-driven context and that no single-qubit arm separates them |
| 17 | `x90-64` holds 4,352 gate lines, about six times the longest circuit run on Tuna-17, against an unnumbered operation cap; the device may fuse the pulses (H3) | the knowledge-base page names a cap without a number; the client compile record shows no fusion | hypothesis, stated in the case with its consequence (the series ends at batch 04 with the earlier batches retained) |
| 18 | `--check` exempts `CASE.md`, so a number in the case text can drift from the generator (H) | `check()` skips the handwritten file | boundary: the case text is handwritten and reviewed by reading; its counts and seconds were compared with `cases.json` and `prediction.json` in this review |
| 19 | the run layout `sanity()` and `read_run()` read is written by the test itself (Advisor) | compared with a retained Tuna-17 run directory: `results.json` holds `jobs[].file`, `jobs[].job.status`, `jobs[].results[0].shots_done`, `raw/NAME.json` holds a list of shot strings, `cases.json` holds `nqubits`, `shots` and `circuits` | confirmed against the retained layout |

The Advisor confirmed rows 1 to 4, 8 to 11 and 13 to 17 as reconciled and required the changes now recorded in
rows 5, 6, 7 and 12, the pre-flight section of the case, and rows 18 and 19.

Conjecture of the reviewer (C): the ordered shots hold a per-qubit shot-order spectrum near the 0.020 cycles per
shot line the repository already records; `p1()` sums it away. Not added to this analysis; the raw shots are
retained, so a later analysis can read it.
