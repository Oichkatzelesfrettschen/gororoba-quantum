# Review record: retention of the Emerald idle-schedule successor run (PR 973)

Reviewers chosen by the owner (2026-11-21): grok as reviewer and opencode on the free NVIDIA Nemotron model
(`opencode/nemotron-3.5-super-vl-free`, first attempt accepted) as red-teamer, on two briefs that share their claims. Both
read head d3b8a3327. The Advisor reviewed last.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | grok, Nemotron | "falsifies the stationary gap model" uses the decision verb of the preregistered stationarity test, which `gap_test` never reaches (it returns at the QB44 exclusion) | Fixed: the note calls the 7.8-standard-error comparison descriptive and inconsistent with one shared gap, and names the stationarity test as not computed |
| 2 | grok | The measurement-alignment hypothesis cites iqm-pulla's multiplexed-probe merge pass, which postpones sequential measurements; these circuits end in one joint `measure`, so the pass has nothing to merge | Fixed: the hypothesis now concerns a joint-measure overhead and states that the pass does not explain the term; its test (alone against joint measurement) is unchanged |
| 3 | grok | The layout split is headed "eleven gated qubits" but `layout_split.py` keeps every qubit with a positive delay rate, QB44 among the eight | Fixed: the item names QB44 and the script's selection |
| 4 | Nemotron | The +- on each mean gap is a standard error under a common gap the record rejects, so it understates the spread | Fixed: the note states what the +- is and gives the per-qubit ranges (23.5 to 36.8 ns at 1000 pulses, 26.1 to 58.6 ns at 500) |
| 5 | Nemotron | `unidentifiable` may read as a settled negative | Fixed: the note states non-identification, neither support nor refutation |
| 6 | Nemotron | a and b of g(N) = a + b / N may be copied as measured constants | Fixed: the note calls them fitted values that two points determine exactly |
| 7 | Nemotron | QB44's calibrated-uncertainty sentence may read as the exclusion ground | Fixed: the delay fit is named the sole ground and the uncertainty context |
| 8 | Nemotron | "wall clock equal to the billed execution" is loose: 2.641 s of runtime billed as 3 s | Fixed: the cost line gives runtime and whole-second billing |
| 9 | grok | "T1 reads near or above the calibration copy" smooths QB42 (0.79) and QB34 (0.87) | Fixed: both named; the hypothesis cites the median |
| 10 | grok | The unit-scale hypothesis has no falsifier; QB30 sits 4 and 8 standard errors above the means; the QB44 test cannot separate a stable defect from a static channel | Fixed: a delay-against-identity-train falsifier, a QB30 hypothesis with its falsifier, and the QB44 limit are stated |
| 11 | grok | The first commit-body line runs 97 columns against the 72-column rule | Boundary: the pushed commit keeps its body, since rewriting it needs a force-push, which the workspace forbids; later commits wrap at 72 |
| 12 | grok | `docs/evidence/iqm/account/credit.json` still reads 30.00 expiring 2026-11-01 | Boundary: the account snapshot is outside this retention; the run's own `results.json` carries the balance before and after |
| 13 | Nemotron | Raw digests not recomputed on the read-only host | Refuted: grok recomputed all four `raw/*.json` sha256 values and the sixteen circuit hashes and found them equal to `results.json` and `cases.json` |

Claims 1, 2, 3, 5 and 6 of the brief stand as stated; grok verified identities, the verdict fields, the exclusion
arithmetic (QB44 survival 4.26e-8; next-largest chi-square QB5 11.98 under the 13.82 threshold) and the cost
arithmetic from the retained files.
