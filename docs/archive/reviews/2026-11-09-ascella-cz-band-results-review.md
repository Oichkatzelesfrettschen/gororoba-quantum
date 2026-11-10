# Review: Ascella CZ tomography reference band results (2026-11-09)

Three adversarial rounds by the `codex` command-line agent on gpt-daybreak-blue at high effort (heads 4cc59bcba,
b7f223c41, a517d7dc5 of `quandela/ascella-cz-tomography-reference-runs`), each checked against the source, then the
Advisor last. The fixes land on `integration/gororoba-quantum-ultrareview`. The subject is
[the band-results note](../../notes/topics/ascella-cz-tomography-band-results.md) and
`docs/evidence/ascella-cz-tomography-band/`.

| Finding | Disposition | Resolution |
|---|---|---|
| N-squared argument reverses Pearson scaling | Survives for proper cells | Cells the statistic clips to one event grow with N squared, the rest with N; on cells in the same class in both pairs, 44 and 5.9 times for 6.1 times the events (`tomography_cell_growth`) |
| Z sector not gate- or source-independent | Survives | `source_model_z`: bit flips predicted at r 0.93 and 0.97; the static-fingerprint claim withdrawn |
| g2-aware overlap contradicts 0.91 to 0.92 convergence | Survives | g2 plus dark counts give 0.931 and 0.933; convergence claim withdrawn |
| "Detector efficiency" is an output-mode weight | Survives | Reworded |
| Throughput/shape split non-additive; then "half is throughput" | Definition point survives, 50 % reading refuted | The signed-E projection reads the clip (per-setting scale 0.17 to 0.35 while totals sit within a median 3.1 %); exact projection on max(E, 0) in the statistic's own weighting: throughput 1.4 % (band), 10.7 % (retained) |
| Forecast scales counting scatter as systematic | Survives | 4.5 withdrawn as a forecast; root cause tested directly instead |
| Root cause of the failed model check | Tested | `mesh_variance_reference.py` (rule at 2efbb1e88): partial; the retained pair passes without the term, so only the band decides. At inputs realizing the recorded per-seed share errors (0.0124, 0.0202) the band stays outside, ratio 3.27 and 2.13 (`calibrated_reference.py`) |
| Sigma is a pre-normalization input | Survives | Realized RMS 0.0098, 0.0155, 0.0292 at inputs 0.011, 0.0177, 0.034; the band's match is 1.65 to 2.65 times the recorded scales and about 3.1 times the retained pair's |
| Implied share error center-dependent | Survives | 0.013 to 0.032 over three centers; no physical scale identified |
| Component model claims localization and calibration/seed separation | Survives as overstatement | Read as a transferable commanded-phase fingerprint; null, draw count and optimizer status stated |
| Guard lexical, test-only, family-wide exemption | Survives | `scatter_check_gaps` walks mappings and lists and reads `statistic`/`test` fields; `UNTYPED_SCATTER_CASES` binds 13 cases.json digests to exact gaps; `scatter_check_refusal` runs in `qd_platform.plan`, through which `submit` passes, on the planned platform |
| Causal "seed change explains it", "not a worse photon pair", additive fidelity gap | Survive | Reworded to consistency statements |
| Control-ratio verdict robust; estimator physicality; job/parity alias | Survive | Relabeled fragile; added as questions |

Bounded residuals: a scatter check whose key and `statistic`/`test` fields avoid the vocabulary passes the guard,
and a decisional Pearson correlation test on a QPU case is refused loudly; a typed preregistration schema is the full
fix. The guard covers Quandela `plan` and `submit`. The band excess beyond the per-seed term is unexplained: proper
cells grow 5.9 times where a 3.1-times share error predicts about 58.

Validation: lint, types and contracts lanes (pinned interpreter) pass; 709 tests touching `qd_platform` or
`fp_host` pass; every Markdown link resolves.
