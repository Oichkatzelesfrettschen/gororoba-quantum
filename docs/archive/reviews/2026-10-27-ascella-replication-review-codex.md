# Referee report: Ascella replication of the element-offset reading

Scratch scripts this report cites under `docs/local/replication-review/` are not retained; [replication-sensitivity.json](../../evidence/ascella-order-coefficients/replication-sensitivity.json) retains the deterministic checks and the [audit](2026-10-27-ascella-replication-review-audit.md) records each finding's disposition.

Document reviewed: pull request 569 and the claim `ascella-signed-coherence-replication-offsets`, checkout head
`cac75978111d594fbfbd8234473d1c1ffb7a84f2`.

Reviewer and ties to the design: `codex`, acting as an independent reanalyst. The reviewer did not design, acquire, or
score the original experiment. The review uses the authors' retained records and repository code, so the review is
independent in execution but not in data provenance.

Registered plans read before the result:
`docs/state/plans/ascella-new-seed-meshes-case.json` and
`docs/state/plans/ascella-replication-meshes-case.json`.

Primary contrast: for each of two frozen predictors, the within-job-centered Pearson correlation between predicted and
observed analyzer statistic X over 168 previously unscored returned meshes. The unchanged predictor, R-B, is the static
heater-and-coupler-offset model fitted on 30 job-00 configurations plus 56 perturbed meshes pooled across jobs 02 and
03. The refitted predictor, R-C, adds 147 meshes from jobs 04 and 05. Each predictor is tested one-sided against
nonpositive correlation at alpha 0.005, the Bonferroni allocation of family alpha 0.01.

## 1. Summary and recommendation

The experiment supports a narrower result than the repository currently claims. Two frozen full predictors have
positive within-job association with X on fresh Ascella meshes: R-B gives r = 0.240 and R-C gives r = 0.404. The
replication plan, predictors, score contract, and seeds have unusually good provenance. The score replays, the seed sets
are disjoint, both jobs point in the same direction, and deterministic post hoc sensitivity checks preserve the
association.

I recommend **accept with revisions**. The decisive revisions concern interpretation, not the existence of a positive
association:

1. The quoted 6.0% and 16.9% are squared-correlation summaries after optimal affine rescaling, not percentages of the
   raw physical error reproduced by the frozen predictors.
2. The score is not a function of the returned circuit and frozen offsets alone. It also uses each test iteration's
   observed outside-block count to construct an in-block background term.
3. The test compares each full predictor with zero correlation. It does not isolate the increment due to offsets over
   the zero-offset returned-circuit predictor.
4. The t tests and Fisher-z bounds are model-based. Two jobs do not establish independent, identically distributed mesh
   residuals, and the residual distributions are detectably nonnormal.
5. The claim mislabels 233 training configurations as 233 perturbed meshes, and the provider-facing follow-up promotes
   a gross anchor check into calibration stability and an unmeasured candidate mechanism into a causal explanation.

The directional association is real enough to report. The physical attribution and percentage language have not earned
the same status.

## 2. Major issues

### 2.1 The held-out predictor uses held-out counts

**Claim and code concerned.** The new-seed plan says a prediction is a deterministic function of returned phases and
couplers (`docs/state/plans/ascella-new-seed-meshes-case.json:18-20`), and the design says the prediction is static light
of the returned mesh under frozen offsets (`docs/design/ascella-signed-coherence-conformance.md:1731-1737`). The actual
data loader reads the test iteration's outside-block count and converts it to an in-block background
(`scripts/ascella_physical_models.py:175-210`). The scoring path mixes that background into the predicted block
probabilities (`scripts/ascella_physical_models.py:242-246`; `scripts/ascella_configuration_holdout.py:57-82`).

**Defect.** The predictor is the returned circuit plus frozen offsets plus an outcome-adjacent quantity measured in the
same test iteration. The score contract was frozen before acquisition, so the defect is not post-outcome model shopping.
It is a claim-versus-delivery error and an undisclosed held-out-data dependency.

**Evidence obtained.** I ran:

```text
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=1 \
  python3 -B -W error \
  docs/local/replication-review/scratch-codex/statistical-audit.py
```

The script is at `docs/local/replication-review/scratch-codex/statistical-audit.py:95-170`. With the retained observed
background, it reproduced R-B r = 0.24034 and R-C r = 0.40394. Setting every per-iteration background term to zero gave
R-B r = 0.23133 and R-C r = 0.38642. The positive result survives, but the numerical predictor is not the predictor the
prose names.

**Effect.** The omission prevents attribution of the retained correlations solely to `computed_circuit` and frozen
offsets. The sensitivity shows that the omission does not explain the full association.

**Required revision.** State the observed-background conditioning in the claim, design, plan resolution, and score
description. Add the zero-background result to durable evidence. A future confirmatory score should freeze its
background treatment from training data or preregister a background-free predictor.

### 2.2 The “share of error carried” is not raw predictive accuracy

**Claim and code concerned.** The claim reports shares of 6.0% and 16.9%
(`docs/state/research_state.json:2501-2506`; `docs/design/ascella-signed-coherence-conformance.md:2026-2044`). The score
defines share as r squared divided by a plug-in attenuation ceiling, while recording the affine slope separately
(`scripts/ascella_new_mesh_score.py:240-277`).

**Defect.** Correlation is invariant under affine rescaling. A predictor can have a positive correlation while getting
the response amplitude badly wrong. Calling r squared divided by the ceiling a fraction of physical error “carried”
silently grants the model an optimal rescaling that the frozen physical prediction did not contain.

**Evidence obtained.** The retained record gives slopes 0.20279 for R-B and 0.44073 for R-C beside shares 0.05978 and
0.16887 (`docs/evidence/ascella-order-coefficients/replication-score.json:64-98`). Direct calculation from its 168 rows
gave:

```text
predictor   raw unrescaled R^2   optimally rescaled R^2   slope
R-B         -0.8349              0.0578                    0.2028
R-C         -0.0996              0.1632                    0.4407
```

The computation is `raw_metrics` in
`docs/local/replication-review/scratch-codex/statistical-audit.py:44-60`. The negative raw coefficients of
determination mean both frozen numerical predictions perform worse than predicting the within-job mean when used at
face value.

**Effect.** The numbers support directional mesh-by-mesh association after affine calibration. They do not show that the
frozen model reproduces 6.0% or 16.9% of the absolute error.

**Required revision.** Replace “carries X% of the error” with “accounts for X% of the centered across-mesh variance
after optimal affine rescaling, conditional on the retained attenuation estimate.” Report the slope and raw unrescaled
R-squared beside every correlation-derived share. Remove “remaining nine tenths” and “remaining two thirds” language,
because those complements inherit the same estimand mismatch.

### 2.3 The primary test does not isolate offsets from the returned-circuit baseline

**Claim and code concerned.** The claim assigns the full-model association to static element offsets on the returned
circuit (`docs/state/research_state.json:2502-2506`). `static_light` always evaluates the returned phases and couplers,
then adds the fitted offsets (`scripts/ascella_physical_models.py:460-502`).

**Defect.** Testing the full predictor against zero correlation does not test whether offsets add information beyond the
nominal returned circuit. That nested comparison was absent from the preregistration.

**Evidence obtained.** On the same 168 rows, a zero-offset returned-circuit predictor gave r = 0.14906, one-sided
p = 0.0273, slope 1.231, and raw R-squared 0.0214 when the retained observed-background term remained. Post hoc partial
correlations controlling that nominal predictor were 0.20717 for R-B and 0.39463 for R-C, with model-based one-sided
p = 0.00370 and 7.16e-8. With the background term set to zero, the nominal predictor became nearly constant
(r = 0.01565), while R-B and R-C remained at r = 0.23133 and 0.38642. The commands and implementation are the same
scratch replay, at `docs/local/replication-review/scratch-codex/statistical-audit.py:95-170`.

**Effect.** The full-model associations survive reasonable post hoc baselines, but the preregistered test does not earn
the statement that the offsets themselves supply the entire recorded association. The strong dependence of the nominal
baseline on observed-background treatment reinforces major issue 2.1.

**Required revision.** State that the preregistered result concerns the full returned-circuit-plus-offset predictor. Mark
the nominal and partial results post hoc. Register a nested nominal-versus-offset contrast before making a confirmatory
incremental-offset claim.

### 2.4 The parametric p-values and Fisher bounds rest on unverified independence and distribution assumptions

**Claim and code concerned.** The score treats 168 mesh rows as independent after subtracting two job means and applies
a Student t reference plus Fisher-z bounds (`scripts/ascella_new_mesh_score.py:233-277`). The two jobs and their 84
meshes each are recorded in `docs/evidence/ascella-order-coefficients/replication-score.json:10-62`.

**Defect.** Within-job centering removes a job intercept. It does not establish independent residuals within one
sequential calibration block, and two jobs cannot support cluster-robust inference. The affine residuals also depart
from normality: Shapiro-Wilk p = 0.0126 for R-B and 0.0387 for R-C, with excess kurtosis 1.06 and 0.43.

**Evidence obtained.** The scratch replay enumerated every pair of circular shifts of the two 84-row outcome sequences,
7,056 combinations. This post hoc null preserves the predictor values, outcome values, and serial structure within each
job while breaking their alignment. Ten shifts reached R-B's observed correlation (p = 0.001417), and one reached R-C's
(p = 0.0001417). Leave-one-mesh-out r ranges were 0.2045 to 0.2633 and 0.3414 to 0.4272. The record's Spearman values are
also positive, 0.241 and 0.305 (`docs/evidence/ascella-order-coefficients/replication-score.json:64-102`).

**Effect.** The positive association survives a structure-preserving falsifier and influence checks. The retained t
p-values and Fisher intervals remain conditional on stronger assumptions than the hardware record establishes.

**Required revision.** Label the t p-values and Fisher bounds “model-based.” Add the circular-shift and rank checks as
post hoc sensitivity analyses, with the cyclic-stationarity assumption stated. A future plan should preregister a
structure-preserving randomization or repeated-block design. Do not describe 168 meshes as statistically independent;
“distinct, previously unscored meshes in two jobs” is supported.

### 2.5 The training count is wrong, and the offsets are not physically identified

**Claim and code concerned.** The claim says R-C was fitted on “job-00 and the 233 perturbed meshes of jobs 02 to 05”
(`docs/state/research_state.json:2502`). The design correctly lists R-B at 86 training inputs and R-C at 233
(`docs/design/ascella-signed-coherence-conformance.md:1962-1965`), and the fitting code constructs R-C from job-00,
56 pooled meshes from jobs 02 and 03, and 147 new-seed meshes (`scripts/ascella_replication_offsets.py:60-83`).

**Defect.** Jobs 02 through 05 provide 56 + 147 = 203 perturbed meshes. The reported 233 includes 30 job-00
configurations. The model also has 258 fitted offsets in both cases
(`docs/evidence/ascella-order-coefficients/replication-offsets.json:267-268,791-792`). Gaussian priors make these
maximum-a-posteriori fits mathematically defined, but neither the parameter count nor fresh-set correlation identifies
258 physical element errors.

**Evidence obtained.** `jq` over the offset record returned `meshes: 86` and `meshes: 233`, each with 258 true entries
in the free mask. The first 147-mesh test and the present 168-mesh replication are genuine out-of-sample safeguards,
and R-B's unchanged replication is particularly useful. No retained record reports effective degrees of freedom,
prior-width sensitivity, or parameter recovery.

**Effect.** The numerical miscount does not alter the score. It overstates the perturbed training sample and encourages
a physical-parameter interpretation that the regularized predictive exercise cannot support.

**Required revision.** Say “233 training configurations: 30 job-00 configurations, 56 distinct perturbed meshes pooled
across jobs 02 and 03, and 147 meshes from jobs 04 and 05.” Keep the current statement that the result identifies no
physical mechanism. Add effective-degrees-of-freedom and prior-sensitivity analyses before interpreting individual
heater or coupler offsets.

### 2.6 The anchor control does not establish calibration stability

**Claim and code concerned.** The design defines the anchor as a gross additive-shift gate on the seed-0 mean, with a
margin equal to 0.0119 in X units (`docs/design/ascella-signed-coherence-conformance.md:1778-1787`). The provider-facing
follow-up says every job stayed within 0.003 “of the preceding calibration”
(`docs/local/perceval-799-followup.md:7`).

**Defect.** A stable seed-0 mean cannot test mesh-dependent phase-voltage changes, coupler changes, loss, detector
response, or a changed relationship between predicted and observed X. The comparison is against a named prior-run anchor
mean, not against a calibration record. The repository itself acknowledges that R-C's added training meshes are closest
in calibration time to the test jobs, confounding training size with calibration proximity
(`docs/design/ascella-signed-coherence-conformance.md:2034-2041`).

**Evidence obtained.** The retained score records shifts -0.002028 and -0.000849 with 99% half-widths 0.002394 and
0.002395, against margin 0.011881. The earlier seed-repeat experiment supplies strong but bounded evidence: 56 identical
returned meshes reproduced at r = 0.8847 across an intervening calibration (`docs/design/ascella-signed-coherence-conformance.md:1607-1623`).

**Effect.** The anchor excludes a large additive event. It does not establish common calibration state across jobs, and
it cannot deconfound the R-C versus R-B difference.

**Required revision.** Say “the seed-0 anchor mean shifted by at most 0.0028 from the named prior-run baseline and passed
a gross additive-shift gate.” State that mesh-dependent calibration equivalence remains unmeasured. Treat R-C's apparent
gain over R-B as descriptive unless a design separates training size from calibration proximity.

### 2.7 The proposed Perceval explanation is causal language without a causal contrast

**Claim concerned.** The provider-facing follow-up says the unexplained remainder “would then follow from” off-diagonal
crosstalk and the voltage solution (`docs/local/perceval-799-followup.md:13`).

**Defect.** The experiment observes neither the voltage vector nor the calibration matrix. The copied provider request
also names coupler reflectivities, port losses, detector efficiencies, dark counts, and unresolved `computed_circuit`
semantics (`docs/local/replication-review/perceval-799.txt:10-14,27-32,42-47`). The retained contrasts therefore do not
allocate the remainder among those mechanisms.

**Evidence obtained.** Earlier screens cover specific simplified families, not the provider's full phase-voltage model
(`docs/design/ascella-signed-coherence-conformance.md:1342-1528`). Major issues 2.1 to 2.3 additionally show that the
reported share is not a causal decomposition.

**Effect.** The sentence turns a request for discriminating data into a conclusion supposedly obtained without those
data.

**Required revision.** Replace the causal sentence with: “The unexplained mesh-dependent variation could include
voltage- and calibration-dependent error, coupler and loss variation, detector response, or other omitted quantities.
Per-iteration voltages and a calibration identifier would permit direct tests.”

## 3. Minor issues

### 3.1 The first pair's historical public-push time is not retained

The design says the first pair's offsets were pushed before its draw
(`docs/design/ascella-signed-coherence-conformance.md:1731-1737`), and the provider follow-up says both pairs were pushed
publicly before their seeds were drawn (`docs/local/perceval-799-followup.md:3`). Commit `9e92be5` contains the frozen
predictors and plan at 17:42:45 UTC; the draw record says 17:43:07 UTC. Current remote ancestry proves present
publication, but a local commit timestamp does not prove historical public-push time. The replication has the missing
server-side receipt: branch activity records `bc15673` at 00:37:09 UTC and the draw at 00:37:15 UTC
(`docs/evidence/ascella-order-coefficients/replication-push-order.json:6-10`;
`docs/evidence/anu_qrng/draw-2026-10-27T003715Z.json:2-4`). Retain a server-side receipt for the first pair or say
“committed 22 seconds before the draw; historical public-push time was not retained.” This issue affects provenance
wording, not independence from outcome data, because the final score code preceded hardware submission and the outcome.

### 3.2 The R-C versus R-B comparison needs a reproducible method

The durable design correctly labels the comparison post hoc and calibration-confounded
(`docs/design/ascella-signed-coherence-conformance.md:2034-2041`), but the plan resolution still says R-C “carries more”
without that qualifier (`docs/state/plans/ascella-replication-meshes-case.json:178`). The text names a Williams test but
does not retain its implementation, predictor correlation, or formula. I reproduced predictor correlation 0.4471 and an
ordinary Williams calculation near t = 2.17 and two-sided p = 0.031; the precise degrees of freedom depend on how the
within-job centering is treated. Retain the formula and the job-adjusted effective sample size. The provider-facing text
should either include the post hoc/confounding caveat or omit the comparison.

### 3.3 The pull-request body could not be inspected under the review boundary

An unauthenticated public API read failed because DNS was unavailable (`curl: (6) Could not resolve host:
api.github.com`). I did not invoke `gh`, because doing so would touch the prohibited credential path. The local commit
message for the retained replication reports the same headline values as the record. The authors should compare the
actual pull-request body with the corrections in this report before merge.

## 4. Checks that came out sound

1. **Preregistration and push-before-draw: pass for the replication.** Commit `bc15673` contains the plan, both frozen
   predictors, and the scoring contract. `git diff --exit-code bc15673..HEAD` over the predictor and score artifacts
   returned zero. The server-side branch activity precedes the draw by six seconds. The first pair's analysis also
   preceded hardware outcomes; only its historical public-push wording lacks a server-side receipt.
2. **Multiplicity: pass within the frozen fresh-mesh test.** The two primary predictors use Bonferroni alpha 0.005 each
   (`scripts/ascella_new_mesh_score.py:83-87,263-275`). Earlier family exploration remains disclosed and limits the
   mechanism claim, but a genuinely fresh test prevents those earlier searches from mechanically inflating these two
   p-values.
3. **Effect size versus significance: fail as worded.** Correlations and slopes are present, but the claim gives the
   correlation-derived share a raw physical-error interpretation. Major issue 2.2 decides this item.
4. **Confidence bounds: fail as interpreted.** The Fisher-z share bounds replay, but they bound an affine-rescaled,
   model-based estimand and omit raw predictive accuracy.
5. **Dependent-correlation comparison: revision required.** The R-C versus R-B difference is correctly labeled post hoc
   and confounded, but its method is not retained sufficiently for exact replay.
6. **Calibration drift and confounds: fail.** The anchor is a useful gross additive-shift check; calibration-state
   equivalence remains unmeasured.
7. **Provenance and replay: pass.** Both score replays and the offset-fit replay exited zero. SHA-256 values for
   `replication-score.json` (`ae5a109a...`) and `replication-offsets.json` (`b541d774...`) match the claim ledger. Raw
   results, manifests, processor snapshots, draw provenance, and submission records are retained.
8. **Simulation versus hardware boundary: pass.** The headline X values come from retained Ascella results, and the
   design states why local simulation cannot supply the device response.
9. **Compilation and post-processing: fail pending disclosure.** Major issue 2.1 identifies the observed-background
   term omitted from the predictor description.
10. **Strength of certified statement: fail as stated.** Positive association is supported; percentage-of-error and
    physical-offset attribution are not.
11. **Claim wording: fail.** Major issues 2.1, 2.2, 2.5, 2.6, and 2.7 require bounded replacement language.
12. **Independence and conflicts: pass with declared limitation.** This review was independently executed, but all
    retained inputs originate from the authors' repository. The circular-shift falsifier was not part of the authors'
    plan.

Additional deterministic checks:

- `python3 -B -W error scripts/ascella_replication_score.py ... --check` exited 0 and reproduced the retained score.
- `python3 -B -W error scripts/ascella_new_mesh_score.py ... --check` exited 0 and reproduced the predecessor score.
- `python3 -B -W error scripts/ascella_replication_offsets.py ... --check` exited 0 after refitting R-C.
- `python3 -B -W error scripts/ascella_coherence_request.py --check`, with Perceval persistent data and Matplotlib cache
  directed to `/tmp`, validated all job-00 through job-07 manifests and rejection mutations.
- Pinned Ruff and mypy passed all eight named Python files. Ruff also passes the scratch audit.
- The 168 replication seeds are distinct, nonzero, and disjoint from jobs 02, 04, and 05. Every scored returned mesh is
  new relative to the reference runs.
- Individual-job correlations point in the same direction: R-B gives approximately 0.261 and 0.223; R-C gives 0.366
  and 0.437. Leave-one-mesh-out deletion never changes either sign or removes the broad association.
- All headline score values, anchor shifts, durations, credits, and the count of 315 fresh meshes over jobs 04 through
  07 reproduce from the retained JSON records.

Not rerun: provider execution, live calibration queries, and any network-backed provider or GitHub operation. The public
pull-request body was unavailable under the credential and network boundary described in minor issue 3.3.

## 5. Honest result statement and Perceval follow-up boundary

An honest one-paragraph result would say:

> On 168 distinct, previously unscored meshes served sequentially in two `qpu:ascella` jobs, two frozen full predictors
> showed positive within-job association with the observed analyzer statistic X. The predictor trained on 30 job-00
> configurations and 56 earlier perturbed meshes gave r = 0.240; the predictor refitted on 233 total training
> configurations gave r = 0.404. The preregistered model-based one-sided tests crossed the Bonferroni threshold, and
> post hoc circular-shift, rank, zero-background, per-job, and leave-one-out checks preserved a positive association.
> Each retained predictor combines the returned circuit, frozen static offsets, and an observed per-iteration background
> term. Its correlation-derived share is an affine-rescaled centered-variance summary, not raw predictive accuracy or a
> percentage of absolute physical error; the raw unrescaled R-squared values are -0.835 and -0.100. The experiment does
> not identify physical heater or coupler offsets, does not establish calibration-state equivalence, and does not locate
> the cause of the remaining mesh-dependent variation.

The follow-up to Perceval issue 799 may claim the following observations:

- 315 distinct fresh-seed meshes were scored across four later Ascella jobs.
- The unchanged full R-B predictor showed positive association on the 147-mesh first pair and again on the 168-mesh
  replication pair.
- The seed-0 anchor means passed a named gross additive-shift gate, and the earlier repeated-seed experiment reproduced
  56 returned meshes at r = 0.885 across an intervening calibration event.
- Per-iteration voltages, calibration identity, coupler and loss data, and detector records would enable direct tests
  that the present result cannot perform.

The follow-up may not claim that static offsets reproduce 6.0% or 16.9% of absolute physical error, that 233 perturbed
meshes trained R-C, that the anchor proves calibration stability, that R-C's larger correlation establishes a training-
size effect, that `computed_circuit` is known to be the applied physical configuration, or that the unexplained variation
comes from off-diagonal crosstalk or the voltage solution. Those are precisely the questions for which issue 799 asks the
missing records.

DONE
