# Review record: Emerald third train length (written case)

Reviewers (owner's selection for pull request 986, 2026-11-22): codex on gpt-daybreak-blue at high and grok as reviewers, agy on gemini-4-neon-high as red-teamer; the Advisor last. grok's second and later rounds did not run (its usage balance is exhausted). Raw reports stay outside the tree. Nothing has been submitted.

| # | Round, reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | 1: codex, agy | The case pinned the predecessor's calibration set ecec1d0a, while a live-built IQM case is rebuilt on the current default set | Fixed in 04af781d8: built from set 7d7ebe74 retained in the case; CASE.md requires a live rebuild immediately before submission |
| 2 | 1: codex, agy, grok | The line test treated the retained 500- and 1000-pulse anchors as independent although they share each qubit's T1 rate and baseline, widening the band 1.3 times (a 5 ns deviation read on-line) | Fixed in 04af781d8: the decision is the within-job deviation of 250 and 2000 from the line through the same job's 500 and 1000, with a delta-method error over the shared counts |
| 3 | 1: agy | One borderline qubit turned the verdict unidentifiable with probability about 0.81; QB24 was judged on the cohort's anchors | Fixed in 04af781d8: per-subject gates, a cohort minimum of 7 of 11 |
| 4 | 1: agy | power.json planted the cohort gap on QB24 and used calibration T1s; an a + b/N form also arises from a population drop between N = 0 and N > 0 | Fixed in 04af781d8: subject-specific planting, retained T1s and readout; CASE.md limits on-line to the a + b/N form |
| 5 | 1: agy | CASE.md said a cancelled job bills nothing | Fixed in 04af781d8 |
| 6 | 2: codex | The false-alarm rate covered the cohort's two deviations while QB24's two also reject (0.0100 over four) | Fixed in b090afa24 |
| 7 | 2: codex | CASE.md stated on-line as an established linear law | Fixed in b090afa24: consistency with linearity within the errors |
| 8 | 3: agy | The retained delay decays are non-exponential (chi2 66.9 on 22 dof); with linear timing the curvature alone makes a spurious off-line at z -4.86 | Fixed in 06ce8a300: a 96 us delay circuit and a quadratic delay correction with its covariance; spurious off-line 0.998 before, 0.0105 after |
| 9 | 3: agy | A non-decaying qubit, a broken readout pair and disjoint cohorts at 250 and 2000 passed every gate; anchors-moved was outside the false-alarm rate; an explicit null describes_id bypassed the calibration-key check | Fixed in 06ce8a300: decay, contrast and intersection gates; six-statistic rate 0.0153; the key fix with a test |
| 10 | 4: codex | The power model injected the timing shift as an exponential factor instead of evaluating the decay at the shifted time | Fixed in 89c41c404: physical-alternative resolvable deviations (cohort 4.0 and 2.4 ns, QB24 12.0 and 5.9 ns at 250 and 2000) beside the population figures; the self-test checks the physical alternative |
| 11 | 4: codex | 0.0153 was called the rate of any verdict but on-line | Fixed in 89c41c404: the six-statistic rejection rate given the modeled membership, with the unidentifiable bound beside it (union at most 0.051) |
