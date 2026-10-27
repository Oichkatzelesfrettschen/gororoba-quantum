# Audit of the replication peer reviews

Reviews: `report-codex.md` (gpt-daybreak-blue-latest, high), `report-grok.md` (grok-4.7, high), `report-agy.md` (Gemini 3.8 Flash, high; Gemini 4 Argon hit its quota), and the orchestrator's own (`report-claude.md`). Every row below was checked against the source or the retained records; "confirmed" means the orchestrator reproduced it.

## Findings, triaged

| # | Finding | Raised by | Verdict | Evidence checked | Action |
|---|---|---|---|---|---|
| A | The scored predictor includes each test iteration's in-block background, built from its own outside-block counts (`ascella_physical_models.py:210`, `:246`); the prose says "a deterministic function of the returned phases and couplers". Without it R-B reads 0.231 and R-C 0.386. | codex, grok (item 9) | confirmed | source lines 210, 243-246; codex and grok both reproduce 0.231 | disclose in the claim, design and plan; record the background-free r as a sensitivity |
| B | The zero-offset returned circuit does not predict X: r 0.016 without the background term. The orchestrator's 0.149 came from the background term alone. | codex, grok; corrects claude | confirmed | codex 0.01565, grok 0.01565 | drop claude's "returned circuit predicts" reading; state the association lives in the offsets |
| C | Share = r^2/c^2 after optimal affine rescaling; raw within-job R^2 at slope one is -0.83 (R-B) and -0.10 (R-C); slopes 0.20 and 0.44. "Carries X % of the error" and "two thirds outside" overstate. | codex, grok, claude | confirmed | all three compute -0.8349 and -0.0996 | reword every share sentence; print slope and raw R^2 beside it |
| D | Parametric p rests on independence and normality the data do not show (Shapiro-Wilk p 0.0126 and 0.0387 on residuals; centered X p 0.007). Structure-preserving nulls: within-job permutation p 7.5e-4 (R-B), 5.0e-5 (R-C) [grok, 20,000]; circular shifts 1.4e-3, 1.4e-4 [codex, 7,056]. | codex, grok | confirmed in kind | both reports; pairing nulls agree with t for R-B | label t and Fisher bounds model-based; record the permutation p |
| E | Is R-B's fitted direction special among offset directions? Prior-offset null through the full nonlinear predictor: 7 of 2,000 at or above 0.240, p 0.004 [claude]. Linearized Jacobian null without background: p 0.025 (prior), 0.023 (sign flips), 0.010 (within-kind permutation) [grok, 4,000 each]. R-C: 0 of 2,000 and 0 of 4,000 in every null. | claude, grok | confirmed; the two R-B estimates differ by construction (nonlinear with background versus linear without) | diag2000.json; grok recompute.json | state that R-B's direction is at most marginally distinguished from random prior offsets (p 0.004 to 0.025 by construction), while R-C's is not matched by any random draw |
| F | R-C's Pearson share is tail-sensitive: dropping the five most influential meshes gives r 0.291 (share 8.7 %); Spearman 0.305; extreme mesh `theta2-x-arm0-c04`. R-B is stable (drop-five 0.234, Spearman 0.241). | grok, claude | confirmed | grok cite_rows; claude influence block | add Spearman and the drop-five figure beside R-C's share |
| G | "R-C carries more" survives in the plan resolution and PR body; Williams t 2.17 (df 164), Steiger and Meng agree, Zou 95 % interval (0.015, 0.312), r_kh 0.447; job-07, the job nearest the added training calibrations, shows the larger R-C. | codex, grok, advisor | confirmed | grok table; orchestrator's own Williams | fix the plan resolution and PR body; retain the method and r_kh |
| H | "233 perturbed meshes of jobs 02 to 05" miscounts: 30 job-00 configurations + 56 + 147. | codex, grok | confirmed | replication-offsets.json meshes 233; design table | fix the claim sentence |
| I | #799 draft: "within 0.003 of the preceding calibration" misstates (shifts within 0.003, intervals and single iterations not); "fitted on the 56 meshes" omits job-00's 30; "would then follow from crosstalk" is causal language without a causal contrast. | codex, grok | confirmed | anchor table; draft lines 5-13 | rewrite the follow-up |
| J | 258 free offsets on 86 or 233 training configurations are identified by the prior, not the data; effective degrees of freedom not computed. | codex, grok, claude | confirmed (count) | replication-offsets.json free masks | state in the boundary; no individual-offset interpretation |
| K | The anchor gate is a gross additive-shift check, not calibration equivalence. | codex, grok | confirmed | score contract | reword "steady" sentences outside the score |
| L | Program history: the family survived four heater families, eight coupling families and a 28-mesh miss (p 0.050) before its prospective retests; the replication boundary omits it. | grok | confirmed | research_state claims | add pointer to the boundary; no re-adjustment |
| M | "99.5 % bounds" without "one-sided" in the R-C parenthesis, PR table and draft; the pair is a central 99 % interval. | grok | confirmed | score code `norm.ppf(1 - ALPHA_EACH)` | relabel |
| N | Predecessor claim says "against the 0.983 attenuation ceiling" while dividing by c^2 = 0.966. | grok | confirmed | new-seed-score.json squared 0.9661 | reword |
| O | Design sentence names Perceval 1.3.0 where the retained preflights name perceval-quandela 1.3.1. | grok | refuted | preflight `versions` is the local client (exqalibur 1.4.2, perceval-quandela 1.3.1); the platform record's `software_versions` names the worker's perceval-quandela 1.3.0 and exqalibur 1.4.1, which the design quotes | none |
| P | First pair's push-before-draw has no server-side receipt (committed 22 s before its draw). | codex, grok | confirmed, now resolvable | GitHub branch activity still serves branch_creation of 9e92be5 at 2026-10-26T17:42:54Z, 13 s before draw-2026-10-26T174307Z | retain that activity record beside the replication's |


## agy's report

| # | Finding | Verdict | Evidence checked | Action |
|---|---|---|---|---|
| Q | Between R-B and R-C the 126 heater offsets correlate 0.82 and the 132 coupler offsets 0.15: the coupler offsets are not identified. | confirmed | replication-offsets.json; now in replication-sensitivity.json `offset_stability` | add to the boundary and design |
| R | A refit on jobs 04 and 05 alone reads r 0.445 on the replication meshes, above R-C. | plausible, unretained | agy scratch script; not rerun under the memory limit | cite as unretained exploratory support for the proximity confound |
| S | "R-B does not beat the zero-offset circuit (Williams p 0.31)." | refuted as stated | the comparator is the background-only prediction, not the circuit (zero-offset r without background 0.016), and a difference of correlations is not the incremental test; the offset component reads r 0.231 and the partial r given the zero-offset prediction 0.207, one-sided p 0.0037 (replication-sensitivity.json) | record the partial test; no wording that R-B fails |
| T | Prior-offset Monte Carlo: random offsets reach R-B's r with probability 0.018 (50,000 linear draws). | consistent with E | agy scratch | the boundary cites the 0.004 to 0.025 range as unretained |
| U | Job-07's twelve anchors drift (slope r -0.61, p 0.034) within the gross-shift margin. | plausible, single post hoc test | not rerun | noted here only; the anchor gate is already worded as a gross-shift check |
| V | Mesh c04 is the most influential row (Cook D 0.19 and 0.36); without it R-B reads 0.205, p 0.004. | confirmed | leave-one-out minimum 0.2045 in replication-sensitivity.json | covered by the leave-one-out range in the record |

## Disposition

Every confirmed action of rows A to N, P and Q is implemented on PR #569 in the commit that archives this audit; R and T enter the boundary as unretained exploratory results; S is refuted; O is refuted; U and V need no further change.
