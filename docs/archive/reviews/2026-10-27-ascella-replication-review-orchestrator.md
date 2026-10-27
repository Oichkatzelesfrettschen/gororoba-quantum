# Referee report (orchestrator): Ascella replication of the element-offset reading

Correction, from the audit (row B): major issue 2's zero-offset r 0.149 comes from the in-block background term read from the test counts, not from the returned circuit; without that term the zero-offset circuit reads r 0.016. The diagnostics scripts named below ran from the session scratchpad and are not retained; `replication-sensitivity.json` retains the deterministic checks.

Diagnostics: `diag.py` and `partial.py` (copied beside this report), run on the retained records at head e09250c; null-calibration seed `draw-2026-10-27T012346Z.json` index 0.

## Summary and recommendation

Both preregistered predictors read "carried" on 168 unseen meshes, the anchors are steady, the push preceded the draw (00:37:09 against 00:37:15 UTC), and no scored mesh is a near duplicate of a training mesh (nearest wrapped phase distance 16.6 rad, the same as between two new meshes). The confirmatory reading stands. The wording around it overstates what it shows in four ways; accept with revisions.

## Major issues

1. **The parametric p-value assumes exchangeable mesh noise that the data do not show.** Offsets drawn at random from the family's prior (heater N(0, 0.3^2), coupler N(0, 0.1^2)) give centered correlations with standard deviation 0.091 over 2,000 draws (99th percentile 0.223, maximum 0.309), against the 1/sqrt(165) = 0.078 the t test implies for a fixed predictor; 7 of 2,000 random draws reached R-B's 0.240, a randomization p of (7 + 1) / 2,001 = 0.004. The meshes share a structure that any offset vector partly projects onto, so "p 8.8e-4" is the probability under a null the program does not face. Revision: report the prior-offset randomization p beside the t-test p, and state R-B's evidence as p 0.004 against random offsets, inside alpha 0.005 by a small margin. R-C (0 of 2,000 at or above 0.404, p below 5e-4) is unaffected in kind.

2. **The returned circuit without offsets already predicts X.** The zero-offset prediction reads r 0.149 (one-sided p 0.027), with a spread of 0.0014, a tenth of the observed 0.0116. R-B correlates 0.302 with it. Controlling for it, R-B keeps partial r 0.207 (p 0.0037) and R-C 0.395 (p 7e-8), and the offset component alone (prediction less the zero-offset prediction) reads 0.231 and 0.386. Revision: attribute the share to the offsets only through these partial figures; "element offsets carry 6 %" counts the returned circuit's own 2 % (0.149^2 / 0.966).

3. **"Carries X % of the error" describes a rescaled predictor, and the frozen predictors as frozen predict worse than the mean.** The affine slopes are 0.20 (R-B) and 0.44 (R-C); the R-B prediction spread exceeds the observed spread (ratio 1.19). Raw out-of-sample R^2 at slope one is -0.83 for R-B and -0.10 for R-C. The positive-direction share r^2 / c^2 is a correlation share after an optimal affine map fitted on the test meshes. Revision: say "the frozen offsets' predictions correlate with ..., a share of the variance that an affine rescaling of them would explain", and record the raw R^2 and the slope beside the share. The slope well below one is the expected signature of 258 free offsets fitted on 86 meshes: the offsets are overfit in amplitude while partly right in direction.

4. **The R-C over R-B margin** is descriptive; the revision in e09250c already states this, with the confound of calibration proximity. Add the second confound that R-C's training set is a superset that includes the first new-seed meshes, whose own readings shaped no choice, so no leakage arises; keep it descriptive.

## Minor issues

5. Heavy tails: the five meshes with the largest centered products carry 52 % (R-B) and 53 % (R-C) of the covariance sum; removing the five largest predictions moves r to 0.205 and 0.358, and leave-one-out r spans 0.205 to 0.263 (R-B) and 0.341 to 0.427 (R-C). The reading survives, but the Spearman correlation (0.241, 0.305) belongs beside Pearson in the claim.
6. Per job, R-B reads 0.261 and 0.223 and R-C 0.366 and 0.437: consistent.
7. Scaling R-B's offsets by 0.5 or 2 leaves r at 0.248 and 0.231; negating them gives -0.225. The signal sits in the offsets' direction, not their size, consistent with issue 3.

## Sound

Preregistration ordering, seed disjointness (`compilation_seeds`, test `test_replication_jobs_skip_every_earlier_seed`), mesh novelty, anchor control (shifts -0.0020 and -0.0008, half-width 0.0024), duration rule, score replay, and the old score's byte-identical replay after the Design refactor.

## Statement the evidence supports

On 168 unseen meshes, static heater and coupler offsets fitted on earlier meshes predict the direction of each mesh's fixed error beyond what the returned circuit alone predicts (partial r 0.21 for the carried offsets, 0.39 for the refit on all 233 meshes), though their amplitudes are overfit (slopes 0.20 and 0.44) and the carried offsets' margin over random prior offsets is modest. The #799 follow-up may say that offsets on the returned phases predict a reproducible, minor component of the per-mesh error and that most of the error lies outside them; it should not quote "16.9 % of the variance" as a property of a frozen model without the rescaling caveat, nor imply that more training meshes caused the larger reading.
