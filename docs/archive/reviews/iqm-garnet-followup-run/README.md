# Review record: the Grover-depth and sedenion Walsh analyzer and runs (PR 976)

The analyzer was written by a Sonnet implementer from a brief (`docs/local/briefs/garnet-followup-analysis.md`,
ignored), accepted by the parent after rerunning its checks, and given the design document's bit-order check before the
runs entered the tree. Reviewers chosen by the owner (2026-11-21): codex (gpt-daybreak-blue-latest, high), grok and agy
(gemini-4-hydrogen-high) on one brief; agy Flash (gemini-3.8-flash-high) and opencode on the free NVIDIA Nemotron model
(`opencode/nemotron-3.5-super-vl-free`) as red-teamers. All read head c266a43cb. The Advisor reviewed last; its corrections are rows 1, 3 and 12.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, grok, gemini, Flash, Nemotron | "QB12 accounts for the unresolved e_10 row" is refuted as stated: the e_10 mode 1100 and peak 0110 both set QB12 and differ on QB11 and QB17, and the e_10 null arm excites QB11 and QB17 (0.13 to 0.17) where the e_5 null does not | Fixed: the Result refutes a QB12 readout fault as the account. The Advisor refuted the first fix, which inferred a second fault: a QB12 fault before the CZs does not factor. The circuits show why: in e_10, QB11 and QB17 carry Hadamard layers around their CZs with QB12, so an excited QB12 flips them by phase kickback; in e_5 they carry none. One QB12 fault therefore fits all four sedenion arms, and the Result states that as a hypothesis with a local-simulation test |
| 2 | codex, gemini, grok, Flash | The readout-corrected f's delta-method error takes its gradient at the raw lambda | Fixed in 604a8d18d: the gradient is taken at the corrected lambda; the corrected z moves from -2.957587 to -2.95776 and no decision moves |
| 3 | codex, gemini, grok | "Written and self-tested before the counts were read" exceeds git: the jobs completed at 22:04 UTC and the analyzer commits are 22:35 to 22:38 UTC | Fixed: the Result states the commit order, that git does not record when the counts were first read, and (Advisor) that the retained record comes from the analyzer as amended after the counts were read, with no verdict moved |
| 4 | codex, Nemotron | "A second run reproduced it byte for byte" has no retained comparison | Fixed: gate `core-iqm-garnet-followup-replay` reruns the analysis and compares the bytes |
| 5 | codex, Flash | "Every other statistic sits under exploratory" is false: corrected contrasts, per-qubit marginals and the k0 uniformity statistics sit inside `decisions` beside the verdicts | Fixed: the module docstring and the Result say each verdict follows a preregistered rule and the fields beside it decide nothing |
| 6 | Flash | `bit_order` is absent from `prediction.json` `decisions` | Fixed: the Result names its source (this document's decision list) and the commit that added it, before the runs entered the tree |
| 7 | codex, gemini, grok | The calibration comparison names no metric family | Fixed: `metrics.ssro.measure_fidelity.constant` and its herald-conditioned pair |
| 8 | codex, grok, gemini, Nemotron | The packed-job QB12 figures have no retained bytes on this head | Fixed: the Result cites PR 974 and its readout-split record |
| 9 | gemini, grok | The role rule compares a rounded z, and its strict form is attributed to the design document | Fixed: the rule reads the unrounded z (a `resolved` field per D) and the docstring cites `prediction.json` |
| 10 | codex, gemini | The self-test covers four of the refusals | Fixed in part: a run compiled on another calibration set is now refused in the self-test (five refusals). Boundary: a missing circuit or another measurement locus requires other `cases.json` bytes, which the digest check refuses first, so those branches are unreachable while the case bytes are bound |
| 11 | grok, gemini | The model column labels the row-minus-truncation contrast "row" | Fixed: both the model row peak and the contrast are given |
| 12 | Flash, hosted Codex | The 101 depth bend can come from drift, since k = 2 and 3 are single central circuits and k = 1 pools mirrored copies | Fixed: the first fix claimed a linear drift cancels; hosted Codex refuted it: a linear drift perturbs f in proportion to t3 - 2 t2 + t1 = 16 - 30 + 17.5 = 3.5 positions. The Result now says a linear drift enters, and the depth hypothesis's test reads the per-position frequencies first |
| 13 | Flash | The readout-corrected f reads z -2.96 against zero, under 3 | Fixed as a descriptive reading; the registered rule decides the raw f against the model's f |
| 14 | grok | The forward D has the sign opposite to the model's | Fixed as a descriptive reading |
| 15 | Flash, Nemotron | Raw binomial errors omit copy-to-copy drift and the shared readout covariance | Boundary: the design registers binomial and paired per-shot variances; the corrected errors (shared readout included) sit beside each verdict, and no verdict lies near z 3 |
| 16 | Nemotron | Mock refusal keys on the `qc` string | Boundary: `submission.json` names the station that ran the job, written by `iqm_jobs.py submit`; a mock run carries `garnet:mock` |
| 17a | hosted Codex | Every analyzer test carries `audit`, so the hosted lanes run none of the scientific behavior | Fixed in 1636efd03: nine unmarked tests on a synthetic case built in tmp_path (an analytic model device, planted alternatives, the role readings, the sedenion nulls and six refusals), 5.7 s |
| 17b | hosted Codex | The sedenion rows loop serially | Fixed in 2c8f26a62: `sedenion_row` runs through `ordered_map`; the replay gate keeps the record's bytes |
| 17 | codex, gemini | Conjectures: a load-dependent QB12 failure, a row-specific coherent error on e_10, a marked-state-dependent depth bend, a heralding keep fraction that tracks QB12 | They stay in the reports as leads; the e_10 hypothesis's test separates the first two |

Claim 4 (every number and verdict of the Result equals the analysis record) stands; every reviewer confirmed it.
