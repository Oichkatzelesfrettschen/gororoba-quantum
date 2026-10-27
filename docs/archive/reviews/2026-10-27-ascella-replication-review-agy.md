# Critical Peer Review: Ascella Replication of the Element-Offset Reading

Ran on Gemini 3.8 Flash (high) after Gemini 4 Argon reached its quota. Scratch scripts this report cites under `docs/local/replication-review/` are not retained; [replication-sensitivity.json](../../evidence/ascella-order-coefficients/replication-sensitivity.json) retains the deterministic checks and the [audit](2026-10-27-ascella-replication-review-audit.md) records each finding's disposition, including the refuted claim that R-B fails against the zero-offset circuit.

```text
Document reviewed: Pull Request #569 (branch quandela/ascella-replication-meshes), HEAD commit cac75978111d594fbfbd8234473d1c1ffb7a84f2
Reviewer and ties to the design: REVIEWER=agy; independent referee. Zero ties to the study design, experimental execution, data collection, or authoring.
Registered plan read before the result: docs/state/plans/ascella-replication-meshes-case.json (pre-draw revision bc1567336ac3c51d6e74c8da856a4eba2ebbb5e7, scope digest 0fafa7eb28111246cac50a83d5f6d40e38e98fce87ee7f695b4ddcfa78647618)
Primary contrast: R-B (P-B unchanged, 86 training meshes) and R-C (refit on 233 meshes); null arm: within-job-centered Pearson r <= 0; decision threshold: alpha = 0.005 each (Bonferroni alpha = 0.01 over two predictors).
Items 1-12:
  Item 1 (Preregistration and forking paths): pass docs/state/plans/ascella-replication-meshes-case.json; defect noted on submitted cases.json metadata
  Item 2 (Multiplicity): pass alpha = 0.005 Bonferroni on primary; fail on historic multi-family model search without family-level penalization
  Item 3 (Effect size versus significance): fail claim wording cites r^2/c^2 as variance "carried" while native unscaled predictions have R^2 = -0.835
  Item 4 (Confidence bounds): pass docs/evidence/ascella-order-coefficients/replication-score.json
  Item 5 (Dependent-correlation comparisons): pass post hoc Williams t, Steiger z, Meng z evaluated in boundary and replication-sensitivity.json
  Item 6 (Calibration drift and confounds): fail R-C vs R-B gain is confounded with calibration proximity of jobs 04/05 to jobs 06/07
  Item 7 (Provenance and replay): pass full bit-exact recomputation of replication-score.json and new-seed-score.json
  Item 8 (Simulation versus hardware boundary): pass all counts are from qpu:ascella physical executions
  Item 9 (Error mitigation and post-processing): fail test-iteration background leakage via outside-block counts in setting_probabilities
  Item 10 (Strength of the certified statement): fail claims assert static offsets "carry" error, but model at native scale increases MSE
  Item 11 (Claim wording): fail claim and perceval-799-followup.md overstate physical explanatory power and omit critical qualifications
  Item 12 (Independence and conflicts): pass review conducted independently without reading peer reviewer outputs
Recomputed numbers: All primary numbers in replication-score.json and new-seed-score.json verified to machine precision (see Section 4).
Not rerun: Physical hardware execution on qpu:ascella (governed by read-only review protocol and credit preservation).
Decision: Accept with major revisions. Decisive findings ordered by consequence: (1) native-scale predictive failure and misleading "share" estimand, (2) test-iteration data leakage via outside-block counts and lack of significant gain over the nominal circuit, (3) calibration proximity confounding in R-C, and (4) submitted cases.json manifest metadata discrepancy.
```

---

## 1. Summary of Claim and Overall Recommendation

### Summary of Claim
The author team investigates compilation-dependent errors in Quandela's 12-mode photonic quantum processor (`qpu:ascella`). A single logical setting (`theta2-x-arm0`) was compiled into different physical meshes using pseudo-random compilation seeds. Across 168 previously unseen meshes served in two jobs (`d54d0e9d` [job-06] and `f27ad639` [job-07-i96], 84 meshes each), the authors evaluate whether a physical model incorporating static heater and coupler offsets on the returned circuit predicts the observed analyzer statistic $X$.

The authors report that:
1. Predictor **R-B** (258 heater and coupler offsets fitted on 86 earlier configurations and frozen before the replication draw) is associated with the centered $X$ statistic at Pearson $r = 0.240$ ($t = 3.18, df = 165$, one-sided $p = 8.8 \times 10^{-4}$), declared "carried" at $\alpha = 0.005$, and assigned an explained "positive-direction share" of $6.0\%$ ($99.5\%$ Fisher-$z$ one-sided bounds: $0.2\%$ to $18.2\%$).
2. Predictor **R-C** (the same family refitted on 233 retained meshes) reads $r = 0.404$ ($t = 5.67$, one-sided $p = 3.1 \times 10^{-8}$), declared "carried", with a share of $16.9\%$ ($5.2\%$ to $32.2\%$).
3. The authors claim that static element offsets on the returned circuit carry a reproducible, minor part of the per-mesh error, with the remaining five-sixths unexplained.

### Overall Recommendation: Accept with Major Revisions
The replication demonstrates a statistically detectable directional correlation between the fitted offset vectors and the centered hardware observations across unseen meshes. Furthermore, the git provenance rigorously establishes push-before-draw ordering for the frozen predictor weights.

However, acceptance is conditional on **major revisions** addressing five critical defects:
1. **Misleading Estimand and Native-Scale Failure**: The reported "share of error carried" ($6.0\%$ and $16.9\%$) is an affine regression coefficient of determination ($r^2/c^2$) that requires shrinking the model's physical predictions by factors of $0.20$ (R-B) and $0.44$ (R-C) and recentering per job. Evaluated at their native physical scale ($\beta = 1$), the raw model predictions have within-job $R^2 = -0.835$ (R-B) and $-0.100$ (R-C); that is, using the uncalibrated physical model *increases* squared prediction error by $83.5\%$ relative to predicting the job mean. Calling this "carrying 6% of the error" is scientifically unacceptable without prominent disclaimers.
2. **Test-Iteration Measurement Leakage and Nominal Circuit Baseline**: The prediction pipeline (`ascella_physical_models.setting_probabilities`) uses the test iteration's own measured outside-block detector counts to estimate an in-block additive background. When this term is present, the nominal returned circuit with zero offsets achieves $r = 0.1491$ ($p = 0.027$), and a Williams $t$-test reveals that R-B does *not* significantly improve upon the zero-offset circuit ($t = 1.0223, p = 0.3081$, Zou $95\%$ CI spans zero: $[-0.0837, 0.2644]$).
3. **Severe Confounding in R-C vs R-B**: The increase from $r = 0.240$ (R-B) to $r = 0.404$ (R-C) is confounded with calibration proximity. Jobs 04 and 05 (comprising 147 of R-C's 233 training meshes) were acquired within 2 hours of jobs 06 and 07. An independent refit conducted during this review on jobs 04 and 05 alone yields $r = 0.4447$ on the replication set ($df = 165, p = 8.68 \times 10^{-10}$), demonstrating that adding earlier training data actually diluted predictive accuracy. The gain is an artifact of temporal calibration drift, not purely sample size scaling.
4. **Extreme Overfitting of Coupler Offsets**: 258 parameters are fitted on 86 meshes (R-B) and 233 meshes (R-C). While heater offsets correlate at $r = 0.8218$ between the two fits, the 132 coupler offsets correlate at only $r = 0.1507$ (essentially unconstrained noise). In addition, Monte Carlo draws from the prior show that random offset vectors achieve $r \ge 0.2403$ with probability $1.84\%$ (~1 in 54) purely by linear chance in 258 dimensions.
5. **Submitted Manifest Metadata Defect**: The submitted `cases.json` manifests for jobs 06 and 07 embedded preregistration metadata pointing to the predecessor plan (`ascella-new-seed-meshes-case.json`) and predecessor offset file (`new-mesh-offsets.json`). This harness defect must be formally cited in the documentation.

---

## 2. Major Issues

### Major Issue 1: Physical Model Fails at Native Scale; "Share Carried" is an Affine Artifact
- **Concern**: `docs/state/research_state.json:2502`, `docs/design/ascella-signed-coherence-conformance.md:2026-2030`, `docs/local/perceval-799-followup.md:5-6,11`.
- **Defect**: The text claims that static offsets "carry 6.0 %" (R-B) and "16.9 %" (R-C) of the compilation-induced error. In ordinary scientific language, this implies that adopting the physical offset model reduces experimental error by $6\%$ to $17\%$. In reality, the estimand is $r^2 / c^2$ from a within-job centered Pearson correlation. This metric permits an arbitrary post hoc linear scaling ($Y = \alpha + \beta \hat{Y}$). The fitted slope $\beta$ is $0.2028$ for R-B and $0.4407$ for R-C.
- **Evidence**:
  Evaluating the raw, unrescaled physical predictions on the 168 replication meshes (`docs/local/replication-review/scratch-agy/predictive_accuracy.py`):
  ```text
  Observed within-job std:      0.011658
  R-B prediction std:           0.013816 (std ratio: 1.19)
  Baseline MSE (predicting mean): 0.00013509 (RMSE = 0.011623)
  R-B affine slope:             0.2028
  R-B raw unscaled MSE:         0.00024788 (RMSE = 0.015744) -> MSE / Baseline = 1.8349 (+83.5% error)
  R-B within-job R^2 (beta=1):  -0.8349
  R-C affine slope:             0.4407
  R-C raw unscaled MSE:         0.00014854 (RMSE = 0.012188) -> MSE / Baseline = 1.0996 (+10.0% error)
  R-C within-job R^2 (beta=1):  -0.0996
  Without centering (absolute): R-B MSE / Baseline = 3.33; R-C MSE / Baseline = 3.45
  ```
- **Effect on Numbers and Wording**: The physical model's predicted swings are 5 times too large for R-B and 2.3 times too large for R-C. If an experimenter applies the uncalibrated physical model directly, prediction variance increases by $83.5\%$. The variance reduction ($5.8\%$ for R-B and $16.3\%$ for R-C) is achieved only *after* shrinking the model predictions by $80\%$ and subtracting job-specific anchor shifts.
- **Required Revision**:
  1. Revise the claim statement, design document, and PR summary to explicitly state:
     "The reported share represents the variance accounted for by an optimal post hoc affine rescaling and job recentering ($\beta = 0.20$ for R-B, $\beta = 0.44$ for R-C). At its native physical scale ($\beta = 1$), the model overpredicts variance and increases mean squared error relative to the job mean ($R^2 = -0.83$ for R-B, $-0.10$ for R-C)."
  2. Remove unqualified phrasing such as "offsets carry 6% of the error" from `perceval-799-followup.md`.

---

### Major Issue 2: Test-Iteration Background Leakage and Lack of Significant Gain over the Nominal Circuit
- **Concern**: `scripts/ascella_physical_models.py:210,242-246`, `docs/evidence/ascella-order-coefficients/replication-sensitivity.json:80-83`.
- **Defect**: To generate the predicted $X$ statistic for a test mesh, `setting_probabilities` uses `data["background"]`, defined at line 210 as:
  `counts[:, LOGICAL:].sum(axis=1)[:, None] * share[None, :]`
  where `counts[:, LOGICAL:]` represents counts in detector modes 4 through 11 *on that specific test iteration*. This constitutes data leakage: the predictor consumes measured photon loss from the test iteration itself to predict that iteration's in-block contrast.
- **Evidence**:
  1. When this background term is included in the evaluation, the nominal returned circuit with **zero offsets** achieves a statistically significant correlation with observed $X$:
     ```text
     r(Y, Nominal) = 0.149057 (t = 1.9363, df = 165, one-sided p = 0.02727)
     ```
  2. A direct test comparing R-B ($r = 0.2403$) against the zero-offset nominal circuit ($r = 0.1491$, intercorrelation $r = 0.3024$) via Williams $t$, Steiger $z$, and Meng $z$ (`docs/local/replication-review/scratch-agy/nominal_analysis.py`):
     ```text
     Williams t = 1.0223, df = 165, two-sided p = 0.3081 (difference = 0.0913)
     Steiger z  = 1.0116, p = 0.3117
     Meng z     = 1.0090, p = 0.3130
     Zou 95% CI on (R-B - Nominal): [-0.0837, 0.2644]
     ```
     The difference between R-B and the zero-offset circuit is *not statistically significant* ($p = 0.31$).
  3. When test-iteration background counts are excluded (`r_without_background` in `replication-sensitivity.json`):
     Nominal circuit correlation drops to $r = 0.0156$, R-B drops to $r = 0.2313$, and R-C drops to $r = 0.3864$.
- **Effect on Numbers and Wording**: The claim that R-B confirms that static element offsets explain the fixed error assumes a null of $r \le 0$. But against a proper null arm representing the nominal returned circuit without offsets, R-B fails to achieve significance ($p = 0.31$).
- **Required Revision**:
  1. The report must state that R-B does not statistically significantly outperform the nominal circuit under the primary protocol ($p = 0.31$).
  2. The methodological reliance on test-iteration outside-block counts must be explicitly disclosed as an exploratory covariate adjustment, not a pure circuit prediction.

---

### Major Issue 3: R-C's Apparent Superiority is Confounded with Calibration Proximity
- **Concern**: `docs/state/research_state.json:2502,2506`, `docs/design/ascella-signed-coherence-conformance.md:2034-2042`, `docs/local/perceval-799-followup.md:6`.
- **Defect**: The presentation contrasts R-C ($r = 0.404$, trained on 233 meshes) with R-B ($r = 0.240$, trained on 86 meshes) to imply that increasing the training set size improves predictive power. However, 147 of R-C's 233 training meshes originate from jobs 04 and 05, which executed on October 26 at 22:30 UTC, approximately 2 hours before jobs 06 and 07 (October 27 at 00:43 UTC). In contrast, R-B's training data came from jobs 00, 02, and 03, run 24 to 72 hours earlier.
- **Evidence**:
  Refitting the model during this review on jobs 04 and 05 *alone* (147 meshes, omitting jobs 00, 02, 03; `docs/local/replication-review/scratch-agy/calibration_proximity_test.py`):
  ```text
  Fit on jobs 04+05 alone (147 meshes) scored on replication (168 meshes):
    Pearson r = 0.444702 (t = 6.3776, df = 165, one-sided p = 8.68e-10)
    Affine slope = 0.4239
    Compare to R-B (86 meshes from jobs 00,02,03): r = 0.240340
    Compare to R-C (all 233 meshes pooled):        r = 0.403935
  ```
  Training on 147 temporally proximate meshes achieves $r = 0.445$, whereas adding 86 older meshes *reduces* the correlation to $r = 0.404$.
- **Effect on Numbers and Wording**: The performance delta between R-C and R-B is primarily a reflection of non-Markovian calibration drift on Ascella over days, rather than an asymptotic sample-size effect.
- **Required Revision**:
  In `research_state.json` and `docs/design/ascella-signed-coherence-conformance.md`, elevate this finding from a secondary boundary note to an explicit finding:
  "The margin of R-C over R-B is driven by calibration drift: a fit on the 147 meshes of jobs 04 and 05 alone yields r = 0.445 on the replication meshes, exceeding the full 233-mesh fit (r = 0.404). Older training meshes act as out-of-date calibration noise."

---

### Major Issue 4: High Dimensionality, Coupler Instability, and Prior-Draw Chance Alignment
- **Concern**: `docs/evidence/ascella-order-coefficients/replication-offsets.json`, `scripts/ascella_replication_offsets.py`.
- **Defect**: The offset model optimizes 258 free parameters (126 phase shifters, 132 directional couplers) with $n = 86$ (R-B) and $n = 233$ (R-C). Although ridge priors ($\tau_h = 0.3, \tau_c = 0.1$) ensure numerical stability, the effective parameter identification is weak.
- **Evidence**:
  1. Parameter correlation between R-B and R-C across the 258 parameters:
     ```text
     Overall parameter correlation: r = 0.5390
     Heater offsets (126 parameters): r = 0.8218
     Coupler offsets (132 parameters): r = 0.1507
     ```
     The 132 coupler offsets are unstable, exhibiting virtually no persistence between 86 and 233 training meshes ($r = 0.15$). This matches the exploratory leave-one-out failure of couplers in `fixed-mesh-error.json` ($\chi^2$ sum 1133 vs threshold 56.9).
  2. Monte Carlo simulation drawing 50,000 random vectors from the prior $N(0, 0.3^2) \times N(0, 0.1^2)$ (`docs/local/replication-review/scratch-agy/prior_draw_mc.py`):
     ```text
     Max r achieved by a random prior draw: 0.3858
     95th percentile:                       0.1970
     99th percentile:                       0.2619
     Probability of reaching R-B's r (0.2403): 0.01842 (~1 in 54 draws)
     Probability of reaching R-C's r (0.4039): 0.00000
     ```
- **Effect on Numbers and Wording**: R-B's correlation of $0.240$ is not a uniquely identified physical state; approximately $1.8\%$ of random prior draws produce equal or higher correlation on these 168 meshes. Only R-C ($r = 0.404$) firmly separates from the prior draw distribution.
- **Required Revision**:
  The report and claim boundary must document that the coupler parameters are underdetermined noise ($r = 0.15$ inter-fit stability) and that R-B's correlation is achieved by ~1 in 54 random directions drawn from the parameter prior.

---

### Major Issue 5: Provenance Discrepancy in Submitted Hardware Manifests
- **Concern**: `results/quandela/runs/2026-10-27T004134Z-qpu_ascella-ascella_signed_coherence-job-06/cases.json`, `job-07-i96/cases.json`, `scripts/ascella_coherence_request.py:448-454`.
- **Defect**: The `cases.json` manifests submitted to Quandela for jobs 06 and 07 carry preregistration metadata pointing to the predecessor plan and predecessor offsets:
  ```json
  "preregistered": {
    "plan": "docs/state/plans/ascella-new-seed-meshes-case.json",
    "frozen_offsets": "docs/evidence/ascella-order-coefficients/new-mesh-offsets.json",
    "family_alpha": 0.01,
    "interpretation": "prediction of unseen served meshes' analyzer response by frozen element offsets"
  }
  ```
  This occurred because `scripts/ascella_coherence_request.py` had hardcoded `NEW_SEED_PLAN` and `NEW_SEED_OFFSETS` for all non-job-02 draws.
- **Evidence**:
  Commit `969297f` acknowledged this defect post hoc:
  `quandela: name the replication runs' analysis contract beside their submitted manifests ... The request builder writes the new-seed preregistered block and seed-rule text for every job seeded from a draw other than job-02's, so the submitted job-06 and job-07 manifests name ascella-new-seed-meshes-case and new-mesh-offsets.json.`
- **Effect on Numbers and Wording**: Under strict audit protocols (`docs/runbooks/critical-peer-review.md`, Item 1), a mismatch between submitted hardware manifest metadata and the analysis contract constitutes a defect. Fortunately, GitHub remote branch activity (`replication-push-order.json`) confirms that `replication-offsets.json` and `ascella-replication-meshes-case.json` existed in commit `bc15673` on the remote at `00:37:09 UTC`, 6 seconds prior to the ANU QRNG draw at `00:37:15 UTC`.
- **Required Revision**:
  Explicitly classify this manifest metadata mismatch as an identified harness defect in the review and claim documentation, noting that cryptographic commit timestamps prevent post-draw forking.

---

## 3. Minor Issues

### Minor Issue 1: High Influence of Outlier Mesh `job-06:theta2-x-arm0-c04`
- **Concern**: `docs/evidence/ascella-order-coefficients/replication-score.json:rows[3]`.
- **Defect**: Mesh `c04` in job-06 exhibits extreme influence on both regression models.
- **Evidence**:
  In R-B, Cook's $D = 0.1902$, studentized residual = $3.4018$, leverage = $0.0318$ ($Y = +0.0438, X = +0.0287$).
  In R-C, Cook's $D = 0.3558$, studentized residual = $2.3917$, leverage = $0.1106$ ($Y = +0.0438, X = +0.0447$).
  Removing `c04` drops R-B's correlation from $r = 0.2403$ to $r = 0.2045$ ($t = 2.6758, p = 0.00411$). Since the preregistered threshold is $\alpha = 0.0050$, the exclusion of this single point pushes R-B close to the significance boundary. For R-C, removing `c04` drops $r$ from $0.4039$ to $0.3414$.
- **Required Revision**: Document the sensitivity of R-B and R-C to mesh `c04` in the sensitivity section.

### Minor Issue 2: Violation of Bivariate Normality Assumption in Student's t-test
- **Concern**: `scripts/ascella_new_mesh_score.py:255-256`.
- **Defect**: The reported $p$-values ($p = 8.8 \times 10^{-4}$ and $p = 3.1 \times 10^{-8}$) rely on Student's $t$-distribution, which assumes bivariate normality.
- **Evidence**:
  Shapiro-Wilk test on observed centered $Y$: $W = 0.978, p = 0.0071$ (rejects normality at $p < 0.01$; skewness = $-0.233$, excess kurtosis = $+1.175$).
  Shapiro-Wilk test on R-B residuals: $W = 0.980, p = 0.0126$ (excess kurtosis = $+1.062$).
  Shapiro-Wilk test on R-C residuals: $W = 0.984, p = 0.0387$ (skewness = $-0.461$).
  However, non-parametric tests confirm robustness:
  - Exact within-job permutation test (50,000 permutations): R-B $p = 0.00080$ (vs parametric $0.00088$); R-C $p < 0.00002$.
  - Exact circular shift null (7,056 alignments): R-B $p = 0.00142$; R-C $p = 0.000142$.
  - Spearman rank correlation: R-B $\rho = 0.2410$ ($p = 8.25 \times 10^{-4}$); R-C $\rho = 0.3050$ ($p = 2.91 \times 10^{-5}$).
- **Required Revision**: Note that the parametric $t$-test is non-Gaussian but validated by non-parametric permutation and rank tests.

### Minor Issue 3: Statistically Significant Temporal Anchor Drift in Job-07-i96
- **Concern**: `results/quandela/runs/2026-10-27T004828Z-qpu_ascella-ascella_signed_coherence-job-07-i96`.
- **Defect**: The anchor control assumes stationarity across the run. In job-07-i96, anchor $X$ exhibits a statistically significant negative drift over its 12 anchor iterations ($r = -0.612, p = 0.034$).
- **Evidence**:
  Linear regression of anchor values against iteration index: slope = $-3.08 \times 10^{-5}$ per iteration ($p = 0.034$).
  Across the ~4.8 minutes of execution, anchor values dropped by approximately $0.0029$.
  Because this shift remains within the preregistered $\pm s_c = \pm 0.0119$ gross margin, the job passed the gate.
- **Required Revision**: Acknowledge within-job drift in job-07-i96 as an indicator of minor thermal relaxation.

### Minor Issue 4: Incomplete Disclosure in Perceval Issue #799 Follow-Up Draft
- **Concern**: `docs/local/perceval-799-followup.md:5-7`.
- **Defect**: The draft states that refitted offsets achieve $r = 0.404$ ($16.9\%$ share) without mentioning:
  1. That R-C vs R-B is a descriptive, non-preregistered comparison.
  2. That R-C's gain is confounded with calibration proximity.
  3. That R-B does not achieve statistical significance over the nominal circuit ($p = 0.31$).
  4. That the model at native scale has negative $R^2$.
- **Required Revision**: Revise `perceval-799-followup.md` in accordance with Section 5.

---

## 4. Checks That Came Out Sound

The following checks were recomputed and verified independently from raw bytes:

1. **Replication Score Reproduction**:
   - Every entry of `docs/evidence/ascella-order-coefficients/replication-score.json` reproduced bit-for-bit:
     - R-B: Pearson $r = 0.24033965$, $t = 3.18044101$, $df = 165$, one-sided $p = 0.00087841$, $99.5\%$ Fisher bounds $[0.043968, 0.418831]$, share $0.05978471$ ($5.98\%$), share bounds $[0.002001, 0.181558]$, Spearman $\rho = 0.24100911$, slope $0.20279171$, intercept $6.03 \times 10^{-17}$.
     - R-C: Pearson $r = 0.40393507$, $t = 5.67196101$, $df = 165$, one-sided $p = 3.0945 \times 10^{-8}$, $99.5\%$ Fisher bounds $[0.223373, 0.557695]$, share $0.16887384$ ($16.89\%$), share bounds $[0.051642, 0.321908]$, Spearman $\rho = 0.30500706$, slope $0.44073290$, intercept $-4.28 \times 10^{-17}$.
     - Anchor control: Job-06 mean $0.88192380$, shift $-0.00202787$, half-width $0.00239366$; Job-07-i96 mean $0.88310296$, shift $-0.00084870$, half-width $0.00239486$. Both pass margin $0.01188065$.
2. **New-Seed Score Reproduction**:
   - Every entry of `docs/evidence/ascella-order-coefficients/new-seed-score.json` reproduced bit-for-bit:
     - P-A: $r = 0.156641$, $t = 1.903187$, $p = 0.029506$, share $2.54\%$, bounds $[0\%, 13.19\%]$ (not carried).
     - P-B: $r = 0.318906$, $t = 4.037692$, $p = 4.3696 \times 10^{-5}$, share $10.53\%$, bounds $[1.36\%, 25.61\%]$ (carried).
3. **Push-Before-Draw Ordering**:
   - Git commit `bc1567336ac3c51d6e74c8da856a4eba2ebbb5e7` author date: `2026-10-26T17:37:08-07:00` (`2026-10-27 00:37:08 UTC`).
   - GitHub branch creation event timestamp in `replication-push-order.json`: `2026-10-27T00:37:09Z`.
   - ANU QRNG draw timestamp in `draw-2026-10-27T003715Z.json`: `2026-10-27T00:37:15Z`.
   - The frozen predictor commit was undeniably public on the remote repository 6 seconds before the random seeds were drawn.
4. **Execution Integrity**:
   - Job-06 (`d54d0e9d`): 96 iterations returned, duration 288 s, credit debit 1.032768.
   - Job-07-i96 (`f27ad639`): 96 iterations returned, duration 289 s, credit debit 1.032768.
   - All 168 seeds are distinct, non-zero, and disjoint from all prior job seeds.
5. **Dependent-Correlation Tests**:
   - Post hoc Williams $t = 2.1696$ on $df = 164$ ($p = 0.0315$), Steiger $z = 2.1468$ ($p = 0.0318$), Meng $z = 2.1413$ ($p = 0.0322$), and Zou $95\%$ CI $[0.0146, 0.3118]$ verified.

---

## 5. Required Statements for Publication and Issue #799

### Honest One-Paragraph Statement of the Result
> "Across 168 novel meshes served on `qpu:ascella` at QRNG-drawn seeds, a pre-frozen model of 258 static heater and coupler offsets (R-B) exhibits a statistically significant directional correlation with the within-job centered analyzer statistic ($r = 0.240$, $p = 8.8 \times 10^{-4}$), confirming directional persistence across independent compilation seeds. However, the model severely overpredicts variance at its native physical scale (affine slope $\beta = 0.20$, native $R^2 = -0.835$), meaning that it accounts for a positive-direction variance share ($6.0\%$, $99.5\%$ bounds $0.2\%$ to $18.2\%$) only after empirical shrinkage. Against a zero-offset nominal circuit baseline, R-B's improvement is not statistically distinguishable from zero ($p = 0.31$), and the 132 coupler parameters show near-zero inter-fit stability ($r = 0.15$). Refitting on 233 meshes increases the correlation to $r = 0.404$ ($p = 3.1 \times 10^{-8}$), but this gain is heavily confounded by calibration proximity: fitting on the 147 temporally adjacent meshes alone yields $r = 0.445$. At least two-thirds of the compilation-induced variance remains entirely outside the static offset model."

### What the Follow-Up to Perceval Issue #799 May and May Not Claim

**Permitted Claims**:
- May state that static element offsets on the returned circuit show a reproducible directional correlation ($r = 0.240$ and $r = 0.404$) with per-mesh variations on unseen seeds.
- May state that the static offset model leaves the vast majority (at least two-thirds to five-sixths) of the compilation-induced variance unexplained.
- May cite this shortfall as quantitative evidence supporting the request for applied voltage vectors and calibration matrices ($A$ and $b$ from Maring et al.), because returned phase representations cannot express dynamic thermal crosstalk or voltage-solution errors.

**Prohibited Claims**:
- Must **not** claim that static offsets "carry" 6% or 17% of the physical error without explicitly stating that this requires empirical affine rescaling and that native-scale predictions increase squared error.
- Must **not** claim that R-C proves larger sample sizes improve offset recovery, as the effect is confounded with temporal calibration proximity.
- Must **not** imply that R-B conclusively rules out a zero-offset model, given that R-B does not significantly exceed the nominal circuit under the primary protocol ($p = 0.31$).

DONE
