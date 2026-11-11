# Reconciliation of the local review of the offline hardware-residual analyses (2026-11-11)

One local reviewer ran on [brief.md](brief.md): the `codex` command-line agent, read-only
([review-codex.md](review-codex.md)). Each of its ten findings was checked against the scripts and the retained
records, and none is refuted. The numbers below are read from the regenerated files of
`docs/evidence/hardware-residuals/`.

| # | Finding | Disposition | What changed |
|---|---|---|---|
| 1 | The IBM report calls Poisson tails exact | fixed | `ibm/exact_laws.py` holds the conditional laws (run counts, runs of length at least L, hypergeometric same-shot pairs convolved over PUBs) and checks each against enumeration of every arrangement at small sizes (`ibm/exact_laws_run.log`, reproduced byte for byte on a second run). Global Bonferroni survivors: coupler-distance pairs 51 to 54, lag-1 diagonal 409 to 415, run lengths 879 to 894. The lag-1 pairs of distinct columns and the burst tails keep a Poisson tail and are labeled approximations; the pooled state-preparation run length 2 uses a Chernoff upper bound. |
| 2 | The coupler-distance trend treats PUBs of one calibration epoch as replicates | bounded | The 12 state-preparation PUBs sit under four calibration stamps on three dates, not three epochs. Across the four stamps the slope reads 10^-3.3 against 10^-7.1 at PUB level and the near-minus-far contrast 10^-3.6 against 10^-6.9; the sign agrees in all four. The pilot is one epoch and has no epoch-level test. |
| 3 | Periodogram tails ignore drift and memory | bounded | A bin-enumeration null over each job's own spectrum replaces the white-noise tail for the 60 Hz window (prior from the mains frequency) and the 29.70 Hz window (found in these records, post hoc). 60 Hz: 8 of 67 jobs at rank 0.01 or better against 0.60 expected. A single bit column reaches no calibrated p below about 1/330, the enumeration floor. |
| 4 | Stacked-column p-values are anti-conservative | fixed | The stack's Gamma and F p-values are marked anti-conservative, the shared-shift null is added, and the ledger is reported with the stacks (3,042 Bonferroni survivors of 627,453 tests) and without them (2,994). |
| 5 | "Memory" and "leakage proxy" name mechanisms the tests do not identify | fixed | The text reads "temporal dependence". An exact block-local null on 512-shot blocks keeps 400 of 409 significant qubits: dependence inside a block, with no mechanism claimed. |
| 6 | The burst dispersion law omits temporal autocorrelation | fixed | The dispersion statistic is referred to all N-1 column-wise circular shifts. Global survivors go from 5 to 0, since the shift p-value cannot fall below about 10^-4; eight PUBs sit at that floor. |
| 7 | Tuna-17 and Quandela tests keep dependence and model approximations | fixed in four parts, bounded in one | `tuna-quandela/loglinear.py` and `common.py` add the log-linear tests and the Benjamini-Yekutieli line; the dependence-safe family has 87 tests with 54 Bonferroni, 64 Benjamini-Hochberg and 58 Benjamini-Yekutieli survivors (before: 90 tests, 58 and 65). The series-level heterogeneity test across families is bounded, and the calibration of the log-linear tests on sparse tables is not verified. |
| 8 | The Belenos implementation contradicts its falsifier | fixed | `a3_belenos_mode_efficiency.py` and its JSON. |
| 9 | Serial CPU-bound loops | fixed | `ibm/verify_60hz.py` and the per-column loop of `ibm/a5_run_length.py` run through `parallel.ordered_map`. |
| 10 | Broad exception handling and a dead assignment | fixed | `tuna-quandela/readout_data.py` catches the specific exceptions and reports problem rows; the dead `b_mem` assignment leaves `ibm/a4_lag1_memory.py`. |

Not run: phase-preserving or moving-block surrogates for single-column periodograms, the exact joint law of the
lag-1 pairs of distinct columns, a nonstationary-Markov null for the run lengths, and reruns of `ibm/a1_line_scan.py`,
`ibm/a6_calibration_age.py` and `ibm/a0_catalog.py`, whose retained files come from their original run.
