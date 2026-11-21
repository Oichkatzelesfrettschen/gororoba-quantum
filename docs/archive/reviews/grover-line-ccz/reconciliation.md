# Reconciliation: review of gororoba-quantum #966 (iqm_grover_line)

Both reviewers read head 5417bc0df6bc8d41067507de1be83d6822f582d2. Fixes
landed in 5f44c44195ba8e0bcb70aacf90b77e1e9e4b0a93; the Garnet run
(e31ba697d94092c6367770d5dff44058552b188f) used the fixed case.

| # | Reviewer | Finding | Disposition | Check |
|---|---|---|---|---|
| C1 | codex | The line and generic copies always run line first, so position drift aliases the compile effect. | Fixed: four copy pairs in ABBA order (`arms()`), equal summed positions. | Garnet copies: line chi-squared 0.67 on 3 degrees of freedom, slope +0.0002 per position (`results/iqm/grover_line_ccz_analysis.json`). |
| C2 | codex | The prediction schedules ALAP and reads unheralded readout, while Garnet runs ASAP and the job heralds; path choice needs recomputation. | Fixed: ASAP with every qubit idle until the joint measure, herald-conditioned readout; all 136 paths re-ranked, QB20-QB16-QB17 chosen. The ASAP switch exposed a defect: a measure left mid-circuit made Aer's density-matrix probabilities a sampled average (one circuit read 0.666 to 0.696 across runs); measures now leave before scheduling and the builder refuses a remaining one. | Identical copies predict identically; `check` replays byte for byte. |
| C3 | codex | The generic copies measure in another physical order, so one assignment matrix cannot correct them. | Fixed: prediction.json and the design record the permutation; `analyze` permutes the matrix per circuit. | `analysis_selftest` relabel check; corrected values in the analysis record. |
| C4 | codex | The stated P(resolve) 0.90 used unpooled denominators while the rule pools copies. | Fixed: pooling stated per decision; the power table recomputed with pooled arms. | Design "Pre-flight" table. |
| O1 | opencode | Same as C4. | Fixed with C4. | As C4. |
| O2 | opencode | A fresh generic compile gives 18 CZ / 68 prx where the retained bytes held 25 CZ / 71 prx at the same pins. | Root cause: the case had been built under qiskit 2.1.2, off `requirements.txt` (qiskit 2.6.2); rebuilt under the pins, generic now 18 CZ, ledger text corrected. | core-773 replay under the pinned stack. |
| O3 | opencode | The design attributed the 37.5 us shot time to `iqm_jobs.py`, which holds 8.7 us. | Fixed: attributed to `ACTIVE_SHOT_SECONDS` in `scripts/iqm_signed_probe.py`. | Design "Seconds and credits". |
| O4 | opencode | The prediction used unheralded readout while the job heralds. | Fixed with C2. | As C2. |

## Hosted Codex round

Hosted Codex reviewed 6f6f7f1e589174f33f60a23bc104e549a753b045 (review
6001333060); each thread was answered and resolved.

| # | Finding | Disposition | Check |
|---|---|---|---|
| H1 | The run reader and analyzer sit in the case script, against the root `AGENTS.md` rule that reusable readers and analyzers live in `gororoba_quantum/` with explicit inputs. | Fixed in e25376ed5e93d6fc923a7a31b0ec5c0d7c4179ec: `gororoba_quantum/grover_line_analysis.py`, validating through `iqm_records.read_run` and reusing `walsh_counts.parity_numerators`; it imports no qiskit. | core-774 replay; self-test checks the parity numerators against the parity matrix. |
| H2 | The k0 uniformity statistic divided by binomial variances, inflating Pearson's statistic by 8/7. | Fixed: Pearson's multinomial statistic, 11.54 on 7 degrees of freedom. | Analysis record `k0.pearson_chi2_uniform_raw`. |
| H3 | Corrected Walsh ratios were set beside a model spectrum that still includes readout. | Fixed: the model's herald-conditioned product readout is inverted before its spectrum is compared with the corrected one; the raw spectrum is compared with the model with readout. The pre-readout model is nearly flat in weight, which changed the design record's reading. | Design "Analysis" table. |

Claims both reviewers confirmed independently: the 8 and 7 CNOT minima
(independent breadth-first searches; codex added that the seven parities'
coefficients cannot vanish modulo 2 pi, so the search covers every
CNOT-plus-phase circuit), the native-against-logical unitary equivalence
(residual 5.9e-11 in codex's pure-NumPy check), the PRX frame convention,
the request digests, the credit arithmetic, and the seed provenance.

Advisor: not run (tool unavailable in the session).
