# Reconciliation: prospective correction case (job-09)

The [brief](ascella-prospective-correction-review-brief.md) went to the `codex` command-line agent on
gpt-daybreak-blue-latest at high effort, read-only, over commit `044995233`; its
[report](ascella-prospective-correction-review-codex-daybreak-blue.md) found the prospective result sound and raised
three findings. The owner chose codex and the Advisor review for this branch. Each finding was checked against the
files.

| Finding | Verdict | Evidence | Resolution |
|---|---|---|---|
| The 98 % interval has an unstated estimand | holds | `ratios` in `scripts/ascella_correction_score.py` resamples (d, t) mesh pairs with the table and counts fixed | The score record names the population (`interval_population`), and a secondary count resimulation, added after the data and outside the decision, redraws every run's block counts and refits the table: 3.88 to 7.95, no replicate below 2, reproducing codex's independent 3.87 to 7.91. The preregistered rule and its reading stay unchanged. |
| "Almost entirely counting noise" is false | holds | residual 1.1346e-5 = counting 4.649e-6 (41 %) + table noise 6.153e-6 (54 %) + 5.4e-7 | The first-principles note states the split, and the design outcome names both noise sources and calls 10.89 a plug-in benchmark. |
| Power shares are model-conditional | holds | `power_replicate` uses one scalar table and one scalar counting variance | The design text and the docstring call the shares a sensitivity calculation within about 0.025 Monte Carlo error that sized the case and decides nothing; the pre-data power record keeps its bytes. |

Checks that found nothing: the table, rule, thresholds and draw indices were committed at 04:18:25 UTC before job-09's
submission at 04:29:01 UTC; job-09's seeds and order follow job-02's names and the draw rule; its body equals the
frozen body apart from `process_id`; empty `admit_statuses` leaves earlier jobs unchanged; every replay is byte-identical.
