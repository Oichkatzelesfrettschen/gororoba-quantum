# Referee report: Ascella replication of the element-offset reading

Scratch scripts this report cites under `docs/local/replication-review/` are not retained; [replication-sensitivity.json](../../evidence/ascella-order-coefficients/replication-sensitivity.json) retains the deterministic checks and the [audit](2026-10-27-ascella-replication-review-audit.md) records each finding's disposition.

Document reviewed: pull request #569, branch `quandela/ascella-replication-meshes`, head `cac75978111d594fbfbd8234473d1c1ffb7a84f2` (merge-base with `origin/main` `45865344c9fc139812f50621b7abe836b024813c`). Claim `ascella-signed-coherence-replication-offsets` in `docs/state/research_state.json`, with predecessor `ascella-signed-coherence-new-seed-offsets`. Follow-up draft `docs/local/perceval-799-followup.md`.

Reviewer and ties to the design: grok. No role in the design, the threshold, the fits, or the acquisition. The nominal-circuit check, the raw within-job skill, the pairing permutation, the influence scan, and the mesh-Jacobian nulls below were specified by this review and are absent from the authors' reported analysis.

Registered plan read before the result files were used as evidence: `docs/state/plans/ascella-replication-meshes-case.json` (scope at line 20) and the contract in `scripts/ascella_new_mesh_score.py` lines 25–43. Primary contrast, fixed there: for each of two frozen predictors, within-job-centered Pearson r of predicted with observed block-conditioned X, one-sided t on n − 1 − J degrees of freedom, carried when p < 0.005 (Bonferroni 0.01 over the two predictors). R-B is P-B unchanged. R-C is the same family refitted on the earlier meshes. The null of that test is r ≤ 0 for that frozen predictor. The anchor control gates only the bounded outcome. A comparison of R-C with R-B is absent from the registered outcomes.

## 1. Summary and recommendation

Ascella compiles one logical setting, `theta2-x-arm0`, to a different 12-mode mesh for each compilation seed. The analyzer statistic X on modes 0–3 varies from mesh to mesh by more than counting noise, and a seed-repeat job had already shown that variation to be stable across one recalibration (r 0.885, claim `ascella-signed-coherence-seed-repeat`). This result freezes a 258-parameter map of static heater and coupler offsets on the returned `computed_circuit`, under Gaussian priors N(0, 0.3²) and N(0, 0.1²), and scores it on 168 meshes served on 27 October 2026 by jobs `d54d0e9d` and `f27ad639`.

**Recommendation: accept with revisions.**

The preregistered association is real on these records and reproduces from them. R-B, the offsets fitted earlier and left unchanged, has within-job r 0.240 (t 3.18 on 165 degrees of freedom, one-sided Gaussian p 8.8×10⁻⁴). A within-job permutation of the outcomes gives p 7.5×10⁻⁴. R-C, the refit, has r 0.404, and its permutation p is 5.0×10⁻⁵. Both clear alpha 0.005 on the pooled pairing test the plan named. The returned circuit at zero offsets does not predict X (r 0.016). The arithmetic of r, t, the Fisher bounds, the shares, and the slopes matches `replication-score.json` to the printed precision.

The revisions are about what those numbers are allowed to say. The positive-direction share is r²/c² after an optimal rescaling and a 3.5% ceiling correction. At the offsets' own scale the frozen predictor is less accurate, within job, than the job mean: raw skills −0.835 and −0.100, slopes 0.20 and 0.44. R-C's headline 16.9% falls to 8.7% without five meshes, and its Spearman correlation is 0.305. The Gaussian tail 3.1×10⁻⁸ is not a calibrated probability for this sample. "R-C carries more" is a post hoc comparison at two-sided p 0.031 with a training-size confound the claim boundary already names and the pull-request opening still asserts. The sentence that places all 233 training meshes among the perturbed meshes of jobs 02 to 05 miscounts them. The follow-up's "within 0.003" and "fitted on the 56 meshes" misstate the records.

### Runbook items 1–12

The criteria are those of `docs/runbooks/critical-peer-review.md`. Source notes were used through that runbook and through `docs/notes/papers/diedenhofen-musch-2015-cocor.md`. The PDFs themselves were not re-opened in this session.

1. Preregistration. **Pass** for the replication contract. `docs/evidence/ascella-order-coefficients/replication-push-order.json` records GitHub `branch_creation` of `bc1567336ac3c51d6e74c8da856a4eba2ebbb5e7` at `2026-10-27T00:37:09Z`; the draw file records `retrieved_utc` `2026-10-27T003715Z`. Author date of `bc15673` is `2026-10-26T17:37:08-07:00`. `git diff --stat bc15673 HEAD` on the five score and offset scripts is empty. This review did not re-query GitHub. The predecessor's public-push receipt is **not run**: the tree holds no activity record for `9e92be5` (author date `2026-10-26T10:42:45-07:00`, 22 s before draw `2026-10-26T174307Z`).
2. Multiplicity. **Pass** for the replication's own denominator. The plan fixes two predictors at alpha 0.005 each, and the score reports both. The earlier rejected families are a selection history the replication boundary still has to cite (major issue 8); they are not a license to re-adjust this p over families the earlier plans already scored as misses.
3. Effect size beside significance. **Fail.** `docs/state/research_state.json:2502` pairs each p with a share and then reads the share as the fraction of compilation-induced variance the offsets carry. The unrescaled within-job skill is negative (major issue 1).
4. Confidence bounds. **Pass** for the interval the plan names. One-sided 99.5% Fisher-z bounds in `replication-score.json` match a recomputation with standard error 1/√(n − J − 2). The follow-up's bare "99.5% bounds" drops "one-sided" (minor issue 1).
5. Dependent correlations. **Fail** on the public comparison, **pass** on the claim boundary's arithmetic. The boundary reports Williams t 2.17 on 164 degrees of freedom, two-sided p 0.031, and withholds a decision. The pull-request opening and the plan resolution say R-C carries more. The published sentence omits r_kh (major issue 4).
6. Calibration drift. **Pass** for the preregistered anchor gate, which both jobs meet (`replication-score.json` shifts −0.002028 and −0.000849, half-widths 0.002394 and 0.002395, margin 0.011881, reading steady). The gate detects a gross additive shift of the seed-0 mesh. It is silent on mesh-dependent stationarity. Lag-1 of within-job-centered X is −0.180 and −0.125.
7. Provenance and replay. **Pass.** The primary recomputed from the retained score rows matches the record to printed precision, and `static_light` on the two run directories reproduces every scored X with maximum absolute gap 0. The submitted manifest names the previous plan; the run README states the binding (minor issue 4). The pull request's "1268 passed" and "13 of 13" gates were **not run** here.
8. Simulation versus hardware. **Pass.** The scored X values are device counts. Predictions are a classical function of the returned circuit. Zero-offset light does not predict the hardware X (section 4).
9. Mitigation and exclusion. **Pass.** Anchors are excluded by the registered rule. `previously_served` is 0 and `empty_logical_block` is 0 in both jobs. The in-block background inside `setting_probabilities` moves R-B's r from 0.231 (pure light) to 0.240 (the registered score).
10. Strength of the certified statement. **Fail.** One share is asked to stand for how much of the error the offsets carry. Slope, raw skill, Spearman correlation, and the per-job split are computed by the contract or by this review and stay out of the claim sentence (major issues 1 and 2). The boundary's refusal to name a mechanism is the right strength for the association itself.
11. Claim wording. **Fail.** Issues 1, 4, 5, and 6, and the follow-up sentences in section 5.
12. Independence. **Pass.** No design tie. The checks in section 4 that the authors did not report are the independence check this item asks for.

## 2. Major issues

### 1. The share is a rescaled correlation, and the frozen predictor loses to the job mean

Claim and code. `docs/state/research_state.json:2502` ("a positive-direction share of 6.0 %", "a share of 16.9 %"). Boundary at line 2506 ("At least two thirds of the compilation-induced variance stays outside both predictors at their upper bounds"). Design outcome at `docs/design/ascella-signed-coherence-conformance.md:2042`. Plan resolution at `docs/state/plans/ascella-replication-meshes-case.json:178` and `next_action` at line 22. Contract at `scripts/ascella_new_mesh_score.py:31` and `:273`: share = r²/c², with c² = s_c² / (s_c² + mean counting variance).

Defect. The registered share divides the squared within-job correlation by the plug-in ceiling. That is the fraction of within-job variance linearly associated with the predictor after the predictor is multiplied by the least-squares slope, then inflated by 1/c². The sentences above call that fraction the part of the compilation-induced variance the offsets carry. The frozen predictor, used at its own scale on within-job-centered X, has a larger sum of squares than the job mean.

Evidence. Command: `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3 docs/local/replication-review/scratch-grok/recompute.py`. From `docs/local/replication-review/scratch-grok/recompute.json`, on the 168 score rows, ceiling squared 0.9661859899344794 as in `replication-score.json`:

| Predictor | r | r² | slope | raw centered skill | mean predicted | mean observed |
|---|---:|---:|---:|---:|---:|---:|
| R-B | 0.24034 | 0.05776 | 0.20279 | −0.83491 | 0.90026 | 0.88587 |
| R-C | 0.40394 | 0.16316 | 0.44073 | −0.09957 | 0.90377 | 0.88587 |

Raw centered skill is 1 − Σ(y − x)²/Σy² after within-job centering of both series (`recompute.py` lines 45–56). The design table already prints the slopes (`ascella-signed-coherence-conformance.md:2028`) and the claim sentence does not use them. Zero-offset light has mean 0.904511, so the observed mean sits 0.01864 below the nominal circuit, against a compilation standard deviation √1.4114993759659365×10⁻⁴ = 0.01188. Centering deletes that deficit before the correlation is formed. The replication within-job variance of centered X is 1.367209×10⁻⁴, a ratio 0.9686 to the retained compilation variance. The ceiling correction is about 3.5% relative (1/0.96619 − 1). It is a small part of the gap between r² and the wording.

Effect. A reader of "16.9% of the compilation-induced variance" and "two thirds lies outside" is entitled to think the refit removes a sixth of the mesh-to-mesh error and that the upper bound still leaves two thirds. The squared correlations are 5.8% and 16.3%. The shares 6.0% and 16.9% are those figures divided by 0.96619. The remainder "at least two thirds" is 1 − 0.3219 = 0.678 of the share estimand at R-C's upper bound. The frozen R-C predictor increases within-job squared error by about a tenth relative to predicting each job's mean.

Required revision. Beside every share, in the claim, the design outcome, the plan resolution, the pull-request table, and the follow-up, print the slope and the unrescaled within-job skill. Define the share in the sentence as r²/c² of the within-job correlation. Keep the mean deficit in the same paragraph: the offsets leave a shift of about 0.014 (R-B) and 0.018 (R-C) that the centering removes.

### 2. R-C's 16.9% is a Pearson figure carried by a few meshes

Claim. `docs/state/research_state.json:2502`, the share 16.9% (5.2% to 32.2%) attached to r 0.404.

Defect. The Pearson correlation that enters the share moves when a handful of meshes are set aside. Rank correlation and a 5/95 winsorization move it in the same direction. No single point has Cook's distance above 1, so this is a heavy tail of the association rather than one broken row.

Evidence. The same `recompute.py` run, influence on the within-job-centered R-C series: Spearman 0.30501, winsorized r 0.33713, r after dropping the five largest |Δr| points 0.29054, maximum |Δr| 0.06169 at row index 3, maximum Cook 0.332, excess kurtosis of residuals 0.431, Shapiro–Wilk residual p 0.0387. Command: `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3 docs/local/replication-review/scratch-grok/cite_rows.py`. The five rows, in |Δr| order:

| Index | Job | Mesh | Observed X | R-C prediction | Δr |
|---:|---|---|---:|---:|---:|
| 3 | job-06 | theta2-x-arm0-c04 | 0.93107 | 0.94808 | +0.0617 |
| 24 | job-06 | theta2-x-arm0-c28 | 0.89519 | 0.87267 | −0.0230 |
| 159 | job-07-i96 | theta2-x-arm0-c86 | 0.91464 | 0.92758 | +0.0208 |
| 126 | job-07-i96 | theta2-x-arm0-c49 | 0.85691 | 0.88071 | +0.0191 |
| 111 | job-07-i96 | theta2-x-arm0-c31 | 0.85609 | 0.88309 | +0.0174 |

`theta2-x-arm0-c04` is a concordant high extreme, 3.77 within-job standard deviations in centered X. Dropping those five leaves r 0.29054. Dividing its square by the same ceiling gives share 0.08737. R-B is stable under the same scan: drop-five r 0.23420, winsorized r 0.22880, Spearman 0.24101, maximum Cook 0.153.

Effect. The carried decision at alpha 0.005 still holds at r 0.291 (the one-sided t remains far below 0.005). The headline 16.9%, and the upper bound 32.2% that feeds "two thirds outside", describe the Pearson point and its Gaussian interval. They do not describe the rank association or the sample without those five meshes. Inference, labeled as such: the point share is sensitive to tails; the sign and the threshold decision are not.

Required revision. In the claim and the follow-up, put Spearman 0.305, the drop-five r 0.291 (share 8.7%), and the mesh `theta2-x-arm0-c04` next to 16.9%. Let 16.9% remain the preregistered Pearson share, identified as that estimand.

### 3. The quoted tail probability of R-C is a Gaussian calculation on a non-Gaussian sample

Claim. `docs/state/research_state.json:2502`, "p 3.1e-8". Code: `scripts/ascella_new_mesh_score.py:255`, `stats.t.sf` on n − 1 − J = 165 degrees of freedom.

Defect. The t tail treats the within-job-centered pairs as independent Gaussian draws. Shapiro–Wilk rejects the centered outcomes (p 0.00706) and the R-C residuals (p 0.0387). The pairing permutation, which keeps each job's outcome multiset and the mesh order of the predictor, lands in a much heavier tail than 3.1×10⁻⁸.

Evidence. `recompute.json`, generator `numpy.default_rng(20261026)`, 20,000 within-job permutations, add-one p = (1 + count)/(1 + 20000). This integer seeds only the review Monte Carlo. It is not an experiment seed.

| Predictor | Gaussian one-sided p | Permutations with r at least as large | Add-one p |
|---|---:|---:|---:|
| R-B | 8.78×10⁻⁴ | 14 | 7.50×10⁻⁴ |
| R-C | 3.09×10⁻⁸ | 0 | 5.00×10⁻⁵ |

R-B's two tails agree. R-C's permutation test never hit the observed correlation in 20,000 draws, so 5.0×10⁻⁵ is an upper bound of that Monte Carlo, and it is three orders above the t probability. Lag-1 of centered X is −0.180 in job-06 and −0.125 in job-07 (n = 84). Under an independent-mesh standard error 1/√84 ≈ 0.109 that is a mild negative serial correlation, about 1.6 standard errors, so the dependence that would inflate r is not a positive drift along the file order. Inference: the Gaussian p is anti-conservative for R-C; the threshold comparison with 0.005 is unchanged.

Required revision. Quote the permutation p beside 3.1×10⁻⁸, and call 3.1×10⁻⁸ the t-distribution tail under the registered formula. Keep "carried" on the registered comparison, which the permutation also meets.

### 4. "Carries more" asserts a contrast the registration tested and then set aside

Claim boundary. `docs/state/research_state.json:2506`: the higher r is descriptive, Williams t 2.17 on 164 degrees of freedom, two-sided p 0.031, and jobs 04 and 05 are the calibrations nearest jobs 06 and 07. Design `ascella-signed-coherence-conformance.md:2034`. The contradictory sentences are the pull-request #569 opening ("A refit on all 233 retained meshes carries more, r 0.404") and `docs/state/plans/ascella-replication-meshes-case.json:178` ("carries more at r 0.404").

Defect. R-C and R-B are dependent overlapping correlations on the same 168 meshes. One clearing 0.005 and the other also clearing it does not, by itself, establish a difference. The plan's outcome list has no branch for that difference. The boundary then reports a Williams test and, correctly, withholds a decision. The opening and the resolution do not.

Evidence. The cocor unit check inside `recompute.py` reproduced Williams t −2.77432, Steiger z −2.75135, Meng z −2.74325, and the Zou interval (−0.36894, −0.06297) for the published example r_jk = 0.1038, r_jh = 0.3213, r_kh = 0.0257, n = 291. On the replication, r_RC = 0.403935, r_RB = 0.240340, r_kh = 0.447062 (correlation of the two within-job-centered predictors):

| Effective n | Williams t (df) | two-sided p | Steiger z (p) | Meng z (p) | Zou 95% interval for the difference |
|---:|---|---:|---|---|---|
| 168 | 2.176 (165) | 0.0310 | 2.153 (0.0313) | 2.148 (0.0317) | (0.0150, 0.3113) |
| 167 = n − (J − 1) | 2.170 (164) | 0.0315 | 2.147 (0.0318) | 2.141 (0.0322) | (0.0146, 0.3118) |

The authors' t 2.17 on 164 degrees of freedom is the second row. The three tests agree. The 95% interval for the difference excludes 0 and a 99% reading of the same p does not. Per job, R-C is 0.3659 on job-06 (one-sided p 3.10×10⁻⁴) and 0.4368 on job-07 (p 1.63×10⁻⁵). Job-07 is the stronger of the two, which is the direction the calibration-proximity confound predicts. Inference: that pattern is consistent with the confound and does not separate it from a genuine training-size gain. R-B alone is 0.2606 (p 0.00833) and 0.2228 (p 0.0208). Neither replication job meets 0.005 by itself. The carried reading of R-B is the pooled one the plan specified, and the plan should say so where it says carried.

Effect. "Carries more" is the sentence a reader remembers, and it is stronger than a descriptive p of 0.031 on a confounded contrast.

Required revision. Make the pull-request opening, the plan resolution, and the follow-up match the boundary: descriptive Williams result, n = 167, r_kh = 0.447, two-sided p 0.031, Steiger and Meng in agreement, training size confounded with calibration proximity. State that R-B's per-job one-sided p-values are 0.0083 and 0.021.

### 5. The 233-mesh sentence counts job-00 twice in the grammar and relocates it onto later jobs

Claim. `docs/state/research_state.json:2502`: "refitted on job-00 and the 233 perturbed meshes of jobs 02 to 05".

Defect. The record field `meshes` on the R-C predictor is 233 (`docs/evidence/ascella-order-coefficients/replication-offsets.json`, predictor `all-served`). The design table defines that 233 as job-00 plus the 56 meshes of jobs 02 and 03 plus the 147 of jobs 04 and 05 (`ascella-signed-coherence-conformance.md:1965`). The plan scope uses the same definition (`ascella-replication-meshes-case.json:20`). Job-00 contributes its 30 configurations (`ascella-signed-coherence-conformance.md:1641`), and 30 + 56 + 147 = 233. Jobs 02 through 05, with job-03's repeat of job-02 pooled by setting name, contribute 203 perturbed meshes.

Evidence. The three texts just cited. The follow-up at `docs/local/perceval-799-followup.md:6` says "refitted on all 233 meshes", which matches the training-unit count and avoids the claim's misplacement.

Effect. A reader who adds "job-00 and the 233" overshoots the fit by job-00's 30 configurations, and a reader who looks for 233 perturbed meshes in jobs 02 to 05 will not find them.

Required revision. Replace the claim sentence with the design table's definition: job-00 (30 configurations) + 56 + 147 = 233 training meshes.

### 6. The follow-up's anchor sentence and its training count contradict the records

Text. `docs/local/perceval-799-followup.md:5` ("fitted on the 56 meshes of the earlier jobs") and line 7 ("the seed-0 anchor iterations stayed within 0.003 of the preceding calibration").

Defect. P-B's training count in the offset record is 86, which the predecessor claim states as job-00 plus the 56 (`research_state.json:2454`; design `ascella-signed-coherence-conformance.md:1742`). The design outcome prose repeats the shorter count (`ascella-signed-coherence-conformance.md:1927`, "fitted on all 56 served meshes of jobs 02 and 03"). The anchor sentence is false as a statement about iterations and as a statement about the preregistered intervals. The preregistered gate is ±0.0119 (`scripts/ascella_new_mesh_score.py:37` and `:94`, `ANCHOR_LEVEL = 0.99`), and it gates only the bounded outcome (lines 41–43). Both replication jobs, and both new-seed jobs, read steady on that gate.

Evidence. Recorded anchor controls:

| Job | Shift of the inverse-variance mean | 99% half-width | Margin | Reading |
|---|---:|---:|---:|---|
| job-04 vs job-03 | −0.002779 | 0.003362 | 0.011881 | steady |
| job-05-i88 vs job-03 | −0.001838 | 0.003312 | 0.011881 | steady |
| job-06 vs job-05-i88 | −0.002028 | 0.002394 | 0.011881 | steady |
| job-07-i96 vs job-05-i88 | −0.000849 | 0.002395 | 0.011881 | steady |

The job-04 half-width alone is wider than 0.003, so that job's 99% interval does not lie inside ±0.003. `recompute.json` gives the twelve seed-0 iterations of the replication jobs. Against the job-05 mean 0.883952, job-06's anchor minimum 0.879328 sits 0.004624 below and job-07's minimum 0.879677 sits 0.004275 below. Job-07's maximum absolute deviation from its own anchor mean is 0.003426.

Effect. "Within 0.003" reads as a precision claim the intervals and the iterations both miss. The means' shifts do sit inside 0.003. That weaker sentence is true and is not what line 7 says. "56 meshes" drops the 30 job-00 configurations that were in the fit.

Required revision. Replace line 7 with the four shifts, their half-widths, and the margin ±0.0119. Replace "56 meshes" with 86 training meshes (job-00 plus the 56). Apply the same repair to the design sentence at line 1927.

### 7. R-B's direction is ordinary for this Jacobian; R-C's is not. Those are different hypotheses from "carried"

Code. The registered null is independence of the frozen predictor and X after within-job centering (`ascella_new_mesh_score.py:248`). This review added a null that keeps the mesh Jacobian of block-conditioned X at zero offsets.

Defect. "Element offsets carry the error" can be read as "this frozen vector is associated with X" or as "the fitted direction is special among offset directions". The registration tests the first. On the linear map, the second is true for R-C and false at alpha 0.005 for R-B.

Evidence. `recompute.json`, `circuit_without_offsets`. The Jacobian is the derivative of pure block light, mode 0 minus mode 3, at zero offsets; heater count 126 from `data["phases"].shape[1]`, and the offset vector has length 258, so the remaining 132 components are the couplers. Linear R-B correlation after within-job centering is 0.23394, against the score-definition r 0.24034; the maximum absolute gap between the centered linear predictor and the centered (prediction minus nominal) series is 0.00742. The null correlates the same centered outcomes with Gθ for random θ, globally centering Gθ. Because the two jobs have equal size, the outcomes' grand mean is already zero. Generators `default_rng(20261027)` for R-B and `default_rng(20261028)` for R-C, 4,000 draws each. Correlation is invariant to a common scale factor. The Gaussian draws use the family prior, standard deviations 0.3 on heaters and 0.1 on couplers, so that null is a prior on directions.

| Null | R-B linear r 0.2384, add-one p | R-B 99.5% quantile of the null | R-C linear r 0.3911, add-one p |
|---|---|---|---|
| Prior Gaussian | 0.0252 | 0.312 | 0.000250 (0 of 4,000) |
| Sign flips of the fitted vector | 0.0227 | 0.289 | 0.000250 (0 of 4,000) |
| Permute within heaters and within couplers | 0.00975 | 0.254 | 0.000250 (0 of 4,000) |

The prior-null standard deviation is 0.129 for R-B. Inference, and only as a scale read off that width: a Gaussian width 0.129 corresponds to a rough dimension 1/0.129² ≈ 60 equally contributing directions. A hat-matrix trace of the 258-parameter posterior was not computed. Separately, identification: R-B's record has 258 free parameters, every entry of `free` true, and 86 training meshes (`replication-offsets.json`, predictor `all-meshes`, rms 0.0437, maximum absolute offset 0.386). With p > n the Gaussian prior is what identifies the fit. R-C has the same 258 free parameters on 233 meshes (rms 0.0379, maximum 0.248). The slopes 0.20 and 0.44 are the out-of-sample scale of that shrinkage. Inference: out-of-sample correlation shows that the prior did not erase the association; it does not show that 233 meshes identified 258 physical offsets.

Effect. R-B can be "carried" on the pairing test and still be a typical direction through this Jacobian. Reporting only the pairing p presents an ordinary linear image of a random offset as a distinguished element-offset mechanism. R-C's direction is rare in these 4,000 draws, which supports a real refit signal on the linear map and still leaves the tail sensitivity and the calibration confound in place.

Required revision. Keep the registered pairing test as the decision. In the boundary, state the geometry-null results as a sensitivity analysis with the three p-values above, state that R-B's direction would miss alpha 0.005 on that null, and state that 258 parameters on 86 meshes are identified through the prior. Say that the effective degrees of freedom were not computed.

### 8. The replication claim is silent on the families that selected this one

Claims. `ascella-signed-coherence-compilation-dependence` (`research_state.json:2589`): four heater families fitted on job-00 miss the 56 meshes, joint quadratic forms 1150, 649, 771, and 201 against a chi-square 0.999 quantile 94.5. `ascella-signed-coherence-heater-coupling` (line 2635): eight families miss, predicted-observed correlations from −0.04 to 0.19. `ascella-signed-coherence-fixed-mesh-offsets` (line 2543): this family on 28 held-out meshes reads r 0.318, one-sided p 0.050, below alpha 0.01, not carried; the exploration leave-one-out correlation 0.59 is labeled exploratory in that boundary.

Defect. The replication claim reports a confirmatory success of the family that survived that sequence. Its own boundary states the two-predictor registration and omits the sequence. A reader of line 2502 sees one family and two significant correlations.

Evidence. The three claim sentences just cited, plus the new-seed claim at line 2454, which is the first prospective clearance (P-B carried, P-A not carried).

Effect. Ioannidis and Munafo, as the runbook states them, put the positive predictive value of a selected significant result below the nominal alpha. The replication's alpha stays 0.005 because the plan fixed that bar for these two predictors before these shots. Adjusting this p again over the killed families would mix two registered studies. Leaving the history out of the replication boundary lets the success be read as the first time the question was asked.

Required revision. Add to the replication boundary a pointer to those three claims: four heater families and eight coupling families missed, this family missed its 28-mesh gate at p 0.050, and the new-seed and replication jobs are the prospective retests. Do not replace 8.8×10⁻⁴ or the permutation p with a program-wide Bonferroni adjustment.

## 3. Minor issues

### 1. "99.5% bounds" on a pair of one-sided 99.5% limits is a central 99% interval

Code. `scripts/ascella_new_mesh_score.py:30` and `:257`: `norm.ppf(1 − alpha_each)` with `alpha_each` 0.005, standard error 1/√(n − J − 2). The design at line 1773 says "one-sided 99.5% Fisher-z bounds". The claim's R-B clause repeats "one-sided". The R-C parenthesis "(5.2 % to 32.2 %)", the pull-request table header "99.5% bounds", and the follow-up at line 6 do not.

Evidence. `cite_rows.py`. The recorded R-C interval of r, (0.2234, 0.5577), matches `norm.ppf(0.995)`. A central 99.5% interval uses `norm.ppf(0.9975)` and is (0.2062, 0.5700), share (4.40%, 33.63%). R-B moves from (0.0440, 0.4188) to (0.0259, 0.4336), share (0.070%, 19.46%).

Effect. The numerical change is small next to major issue 2. The label still overstates the coverage by half a percent in the tail and invites a reader to treat the pair as the interval the plan did not compute.

Required revision. Write "one-sided 99.5% bounds (together, a central 99% interval)" in the R-C parenthesis, the table header, and the follow-up.

### 2. The predecessor calls the ceiling 0.983 while the share divides by c²

Claim. `research_state.json:2454`, "against the 0.983 attenuation ceiling", share 10.5%.

Evidence. `new-seed-score.json` ceiling squared 0.9661139559510469. √0.966114 = 0.983. The recomputed P-B share is r²/c² = 0.101701/0.966114 = 0.10527, which matches the record. Dividing r² by 0.983 would have given 0.1035.

Effect. The share is reproducible. The word "against the 0.983" can be read as the divisor. The relative difference is about two percent of the share.

Required revision. Say the ceiling factor is c² = 0.966 (c = 0.983) and that the share divides by c².

### 3. The new-seed planning sentence names Perceval 1.3.0; the retained preflights name 1.3.1

Design. `ascella-signed-coherence-conformance.md:1866`, "Perceval 1.3.0 on the worker" at 17:42 UTC on 26 October, with HOM 87.46% and g2 2.1%.

Evidence. `preflight.json` line 91 in the job-04, job-05-i88, job-06, and job-07-i96 run directories: `"perceval-quandela": "1.3.1"`. Job-06's preflight also has HOM 87.16%, g2 2.0%, clock 13.33 MHz, exqalibur 1.4.2 (lines 27, 42, 43, 90). Those platform figures can move between 17:42 and the jobs. The version string on the retained preflights is 1.3.1 for every scored job of both cases.

Required revision. Point the design sentence at the preflight version of the runs it introduces, or confine "1.3.0" to a snapshot that the design identifies by path.

### 4. The submitted manifest still names the previous plan

File. `results/quandela/cases/ascella_signed_coherence/job-06/cases.json:42753`, `"plan": "docs/state/plans/ascella-new-seed-meshes-case.json"`, and line 42847, seed rule text that names job-02's seeds alone. The design at lines 2003–2006 and the job-06 run README at lines 33–43 state that the bytes were kept because the cases digest binds the submission, and that the analysis contract is `ascella-replication-meshes-case`, `replication-offsets.json`, and `ascella_replication_score.py`. The score record's `previously_served` is 0 for both jobs. This review did not re-compare compilation-seed integers across case files.

Effect. A reader who opens the submitted manifest and stops there loads the new-seed plan and a skip set the code does not use. The authors' reply on pull request #569, commit `969297f`, documents the choice and leaves the bytes in place. That is a coherent digest policy. The claim's evidence list points at `results.json` and the score, and it does not point at the README caveat.

Required revision. One sentence in the replication boundary: the submitted `cases.json` names the new-seed plan, the bytes are unchanged, and the contract is the replication plan named in the run README.

### 5. The predecessor's outcomes are heavy-tailed, and its carried decision survives the same permutation

This is context for the family the replication retests, not a defect in the replication arithmetic.

Evidence. `recompute.json` on `new-seed-score.json`: P-B r 0.31891, slope 0.31948, raw skill −0.35975, Spearman 0.31917, one-sided t p 4.37×10⁻⁵. `cite_rows.py` permutation, same generator and 20,000 within-job shuffles: 1 draw at least as large, add-one p 1.00×10⁻⁴. Centered outcomes have skew −1.61, excess kurtosis 7.24, Shapiro–Wilk p 3.85×10⁻⁸. The extreme row is job-04 `theta2-x-arm0-c62`, observed 0.80775, centered −5.79 standard deviations. Dropping the five largest |Δr| points leaves P-B at r 0.32282. P-A falls from 0.15664 to 0.08776 under the same drop, and its raw skill is −1.18157.

Effect. The predecessor's carried call on P-B is stable. Its sample is a poor Gaussian specimen, which is further reason to quote a permutation p in both claims (major issue 3).

Required revision. Mention the excess kurtosis and the permutation p in the new-seed boundary when that claim is next touched. No change to its carried reading.

## 4. Checks that came out sound

The recomputation is `docs/local/replication-review/scratch-grok/recompute.py`, output `recompute.json`, plus `cite_rows.py` for row names, the central 99.5% intervals, offset norms, and the P-B permutation. Python was `python3` with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`.

- Registered primary, from the score rows. R-B r 0.240339645541003, t 3.180441, df 165, one-sided p 8.784×10⁻⁴, r bounds 0.043968 to 0.418831, share 0.059785 (0.002001 to 0.181558), slope 0.202792, Spearman 0.241009, n 168, J 2. R-C r 0.403935070457843, t 5.671961, p 3.095×10⁻⁸, r bounds 0.223373 to 0.557695, share 0.168874 (0.051642 to 0.321908), slope 0.440733, Spearman 0.305007. The record's printed p-values differ in the last stored digit only (R-B record p 0.0008784096056259957 against recomputed 0.0008784096056259938). Ceiling squared 0.9661859899344794, counting variance 4.939882652368512×10⁻⁶, matches `replication-score.json`.
- Score-definition reconstruction. `static_light` under both frozen offset vectors, scored with the project's `job_data` and `geometry.statistic` on the job-06 and job-07-i96 run directories, matches every retained row: maximum absolute gap 0 on observed X, R-B, and R-C.
- Push-before-draw of the replication executable contract. Author date, activity receipt, and empty script diff, as in item 1. Draw committed in `dfedf1a` at author date `2026-10-26T17:41:10-07:00`. The six-second gap was not re-queried against GitHub.
- Nominal circuit and mesh distance, a check the authors did not report. Zero-offset X on the 168 meshes spans 0.904167 to 0.904724 (standard deviation 8.018×10⁻⁵) and correlates with observed X at r 0.01565 (one-sided p 0.420). Circular phase RMS against the anchor configuration has mean 1.818 rad, coefficient of variation 0.0418, and r 0.00689 with observed X (one-sided p 0.465). The association lives in the offsets, not in the ideal of the returned phases and not in distance from the seed-0 mesh.
- Pairing permutation. R-B agrees with the t test (7.50×10⁻⁴ against 8.78×10⁻⁴). R-C remains carried at add-one p 5.0×10⁻⁵. P-B remains carried at add-one p 1.0×10⁻⁴.
- R-B influence. Drop-five r 0.234, winsorized r 0.229, Spearman 0.241, no Cook distance above 1. The pooled signal is not one mesh.
- Both replication jobs have positive R-B correlations of similar size (0.261 and 0.223). R-C is positive in both and would meet 0.005 in each (0.366 and 0.437).
- Linearization. The zero-offset Jacobian reproduces the centered R-B score to a correlation 0.234 against 0.240.
- Anchors on the registered margin. All four shifts in minor issue 2's table read steady at ±0.011881. Durations 288 s and 289 s, dispersion ratios 64.32 and 69.34, match the score record.
- Cocor implementation. The published numerical example reproduces to the digits quoted in the runbook.
- Predecessor primary. P-A r 0.15664, p 0.02951, share 0.02540, slope 0.12483, not carried. P-B r 0.31891, p 4.37×10⁻⁵, share 0.10527, slope 0.31948, carried. Both match `new-seed-score.json` to the printed precision, including anchor shifts −0.002779 and −0.001838.
- Seed-repeat, compilation-family, and coupling-family claims were read as the selection history and were not re-fit in this review.
- Hardware identity of the replication jobs. Job-06 preflight: perceval-quandela 1.3.1, exqalibur 1.4.2, HOM 87.16%, g2 2.0%, clock 13.33 MHz. No per-job matrix A or voltage vector is in the run directory. That absence is the subject of Perceval #799, and it is consistent with what the files contain.

Not rerun, besides the items already marked: the pull request's lint, type, test, and gate commands; a hat-matrix trace of either fit; individual anchor ranges for jobs 03, 04, and 05 beyond the recorded means and half-widths; a fresh compilation-seed intersection across case files; any provider job; the ANU QRNG; a second query of the GitHub activity API.

## 5. What the result can say

On 168 meshes of one logical setting that the fit had not seen, served by `qpu:ascella` on 27 October 2026 in two jobs of 96 iterations, static heater and coupler offsets on the returned phases, frozen before the compilation seeds were drawn, are associated with the within-job variation of the analyzer statistic X. Left unchanged, the earlier fit gives within-job Pearson r 0.240 (pooled one-sided t p 8.8×10⁻⁴; within-job permutation p 7.5×10⁻⁴). Refitted on 233 earlier training meshes, the same family gives r 0.404 on those 168 (permutation p 5.0×10⁻⁵; t tail 3.1×10⁻⁸ under a Gaussian formula the residuals do not support). Both clear the preregistered alpha of 0.005 on the pooled test. The squared correlations are 5.8% and 16.3% of the within-job variance, and the reported shares 6.0% and 16.9% are those figures divided by the plug-in ceiling 0.966. The affine slopes are 0.20 and 0.44, and the frozen predictors' within-job skills are −0.83 and −0.10, so at the offsets' own scale the job mean is the more accurate predictor. R-C's Pearson share falls to 8.7% without its five most influential meshes, and its Spearman correlation is 0.305. The difference between the two correlations is a post hoc Williams test, t 2.17 on 164 degrees of freedom, two-sided p 0.031, with training size confounded with calibration proximity. The seed-0 anchor means moved by −0.0020 and −0.0008 relative to the preceding calibration, inside the preregistered margin of ±0.0119. The mean of X sits about 0.018 below the nominal circuit, a deficit the centered correlation removes and the offsets leave in place. The zero-offset circuit, scored in this review, correlates with observed X at r 0.016.

The follow-up to Perceval #799 may say that static offsets on the returned phases associate with a minor, replicated part of the mesh-to-mesh variation of X; that the shares above are rescaled squared correlations with the slopes and skills just stated; that a post hoc comparison of the refit with the frozen fit is descriptive at p 0.031 and confounded; that the anchor means passed ±0.0119; and that the applied voltage vector and an identifier of the calibration snapshot (A, b, coupler reflectivities, per-port transmissions), together with per-mode detector efficiencies and dark counts, are what items 1–3 of that issue ask for and what would let the remainder be tested. It may cite r 0.016 for the zero-offset circuit only as a result of this review.

It has to refrain from saying that the model removes 16.9% of the error, that the frozen predictor beats the within-job mean, that the anchors stayed within 0.003, that the fit used 56 training meshes or 233 perturbed meshes of jobs 02 to 05, that R-C is established as the better predictor, that 3.1×10⁻⁸ is a calibrated tail probability, or that the remainder has been shown to be crosstalk. Crosstalk through A in the Maring control model is a hypothesis the returned circuit cannot test, which is the reason the voltage vector matters.

DONE
