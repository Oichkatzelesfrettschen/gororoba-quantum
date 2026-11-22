# Review record: retention of the interleaved Tuna-17 series (PR 975)

Reviewers chosen by the owner (2026-11-21): agy (gemini-4-hydrogen-high), codex (gpt-daybreak-blue-latest, high) and grok
on one brief; agy Flash (gemini-3.8-flash-high) and opencode on the free NVIDIA Nemotron model
(`opencode/nemotron-3.5-super-vl-free`, first attempt accepted) as red-teamers. All read head f6d6d824e. The opencode
run wrote an untracked report file into the worktree against its read-only brief; that file went to the trash and its
report is the run's retained output. The Advisor reviewed last; its corrections are rows 4 and 5.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, gemini, grok, Flash, Nemotron | "T1 changes on a scale of minutes" reads the round split's scaled between-round test as T1 drift, though T is the parameter of mostly rejected fits, the scale comes from 5 degrees of freedom and the threshold is unadjusted; the scaling hides swings on badly fitted qubits (q2, q7) | Fixed: the note states that neither count measures T1 drift and gives the scaling's limits; the commit body's "T1 drift" stays in history (Boundary: no force-push) |
| 2 | Flash | The first open hypothesis's test (refit with variance from the replicate scatter) passes by construction | Fixed: replaced by a test that separates a moving T1 from an additive level shift (replicate variance by multiplier against the two profiles), from gemini's conjecture |
| 3 | codex, gemini | The staggered comparison's 0.36 is a mean of row z-scores, not a standard error of the mean, over correlated rows; large cancelling rows are hidden | Fixed: the note gives the mean and the mean z separately, says no schedule effect is resolved, and names the largest rows, the 5 us extrapolation and the 80 us sign pattern |
| 4a | owner, Advisor | The deferral of row 4 ("would mislead the dashboard") does not survive: the retained context already labels fitted T1 figures by their adequacy | Fixed: `interleaved_t1` per qubit with verdict and probabilities, the analysis bound in sources, an unmarked test; the dashboard keys stay unchanged |
| 4b | owner | Elucidate and test what the series supports | Fixed: `hypothesis_tests.py` (prediction, falsifier and threshold first; synthetic self-test) falsifies an additive level shift and a batch-common disturbance, keeps a moving T1, and finds the ladder over-rotation not decidable |
| 4 | gemini, grok | CASE.md's "Record" asks the retaining change to extend `scripts/qi_retained_context.py` to read the analysis rows and to put the seed indices of `schedule.json` on its ledger row; the script's `--check` fails once the new runs land | Fixed in part: the retained-context file is regenerated and `--check` passes (it was already stale on main, missing the QX twin's 2026-11-19 jobs). Boundary, put to the owner with the merge: the extension waits because the interleaved fits are rejected on 16 of 17 qubits and their T values would mislead the dashboard (removal condition: a fit that passes); the acquisition rows carry five fixed keys, so the seed indices stay in `schedule.json` (lines 4 to 20), which the rows' run directories reach |
| 5 | gemini, Flash | The q12 timeline is wrong (one batch on 2026-11-20, not several), and the submit-gate note claims a comparison of the two `w0` batches that the analyzer does not make | Fixed: the timeline gives each batch's time from its `results.json` and the 20.6 h gap. The Advisor refuted the first fix, which called the comparison impossible: three angles 120 degrees apart fix a phase with its binomial error. `q12_batches.py` now compares the batches of each wait (w0 difference -0.019 +- 0.017 rad, z -1.1; w25 -0.002 +- 0.020), and the submit-gate note keeps its promise |
| 6 | gemini, Nemotron | Both gates (replicate and tail-fit lack of fit) zero the sixteen qubits; "not_confirmed" may read as no tail | Fixed: the note names both gates and says the test had no power against a tail there |
| 7 | Flash, Nemotron | The q12 `null` hides a 3.2-standard-error offset and its error carries binomial variance only across 20.6 h | Fixed: the note says `null` is the band's verdict, not zero rotation, and states the error's basis |
| 8 | Nemotron | 29/98 reads as familywise-controlled though contrasts share an all-17 job | Fixed: the note states the correlation and that the familywise rate is not exact |
| 9 | Nemotron | The q1/q2 headline compares circuits that differ (retained 40 X pulses against this 128-pulse X90 ladder) | Fixed: the note says the series do not compare like for like |
| 10 | Nemotron | The 643.2 s figure is unattested because `execution_time_in_seconds` reads 0.0 | Refuted: the job-level field reads 0.0, while each job's result row carries the execution time; grok and Flash summed the 90 result rows to 643.234605 s; the note names the field |
| 11 | codex | The byte replay has no retained comparison | Fixed: gate `core-qi-tuna17-interleaved-replay` reruns `--analyze` and the round split and compares both with the retained files |
| 12 | gemini | `round_fits.py` is outside the lint and type lists | Fixed: added to `checked_files` and `typed_files` in `ci/pr_checks.sh` |
| 13 | Flash | The case's follow-up budget assumed six of eight flagged qubits; 15 distinct qubits flag | Fixed: the note's Open list says the follow-up budget needs recomputing |
| 14 | Flash | Execution seconds understate the series' wall clock (about 21 h) | Fixed: the note states the wall-clock span |
| 15 | gemini, grok | "13 to 32 us" rounds 32.52 us down | Fixed: 13.1 to 32.5 us |
| 16 | codex, gemini, grok | Conjectures: a batch-common disturbance, an over-rotation reading of the ladder contrasts, a calibration-epoch q1/q2 response, a processor-wide Ramsey frame offset, an 80 us excess | The first two enter the note as open hypotheses with tests; the others stay in the reports as leads |

Claims 1, 3 and 5 of the brief stand as stated; reviewers confirmed the 30 batches, 90 jobs, 688,128 shots, the ledger's
90 retained and 84 declared ids, every preregistered field and the 30 acquisition rows.
