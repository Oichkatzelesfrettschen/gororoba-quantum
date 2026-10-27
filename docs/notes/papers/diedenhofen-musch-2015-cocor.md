# Diedenhofen and Musch 2015 -- cocor: A Comprehensive Solution for the Statistical Comparison of Correlations (PLOS ONE 10(4): e0121945)

## Source copy and license

The [source PDF](https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0121945&type=printable)
remains external to the published library. Its optional reading copy is
`docs/local_source_cache/diedenhofen-musch-2015-cocor.pdf`; [SOURCES.json](../../SOURCES.json) binds the bytes
(SHA-256 `a21fcdad41b5a9e04b765949e02d7c8bec8229faf5f2059e10758a8ee85d933d`, 537051 bytes, 12 pages). The
[article page](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0121945) links
http://creativecommons.org/licenses/by/4.0/ in its copyright line and the PDF names the Creative Commons Attribution
License (PDF p. 1), so a CC BY 4.0 grant exists. The verifier in `docs/verify_sources.py` has no publication route for a
PLOS host, so the PDF stays external until that route exists. The S1 Appendix, a separate 14-page PDF the formulas live
in, is registered as a retrieval receipt (SHA-256 `00f7462329ce42279bb7b76fd88a89e67e57be090ef041976b9d5a7c497279b3`,
139505 bytes) from https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0121945.s001&type=supplementary
and is cited here as S1.

Tag convention: [P] marks paper statements with their PDF page or S1 equation; [I] marks repository interpretation.

## Citation and provenance

- Authors: Birk Diedenhofen and Jochen Musch (University of Duesseldorf). PLOS ONE 10(4): e0121945, 2 April 2015, DOI
  10.1371/journal.pone.0121945 (Crossref receipt in [SOURCES.json](../../SOURCES.json)). Software: R package cocor
  1.1-0, web interface http://comparingcorrelations.org.
- Reading scope: all 12 PDF pages of the article and all 14 pages of S1 for the independent-group and the
  dependent-overlapping tests; the dependent-nonoverlapping formulas of S1 were skimmed to Eq. 39.
- Steiger 1980 (Psychological Bulletin 87, 245-251, DOI 10.1037/0033-2909.87.2.245) is not retrieved; the registry
  holds a descriptive record, and Steiger's formulas enter this note only through S1 Eq. 19 to 21.

## When a direct comparison is required (PDF p. 1-2)

- [P] A valid comparison of two correlations needs a direct test of their difference. Researchers who find one
  significant and one nonsignificant correlation and conclude the two differ commit a statistical fallacy; the authors
  cite Rousselet and Pernet, Nieuwenhuis et al., and Rosnow and Rosenthal: "God loves the .06 nearly as much as the
  .05". (PDF p. 1-2)
- [P] Three cases need three families of test: independent groups; dependent groups with overlapping variables (two
  correlations share one variable, rho_A12 versus rho_A23); dependent groups with nonoverlapping variables (rho_A12
  versus rho_A34, including the same correlation before and after a treatment in one group). (PDF p. 2)
- [P] May and Hittner found no test uniformly preferable for dependent overlapping correlations; the best choice depends
  on sample size, predictor intercorrelation, effect size and predictor-criterion correlation. The package therefore
  reports every test. (PDF p. 2)
- [P] Zou's method returns a confidence interval for the difference, which shows magnitude and precision together;
  an interval can test the difference against a nonzero threshold (the `null.value` argument). (PDF p. 3, 5)
- [P] Limits: two correlations only; no structural-equation approaches. (PDF p. 5)

## Formulas of S1 for the dependent overlapping case

Notation: r_jk and r_jh are the compared correlations, r_kh the related correlation, n the group size, Z the Fisher
transform atanh(r) (S1 Eq. 1), rbar = (r_jk + r_jh)/2, |R| = 1 + 2 r_jk r_jh r_kh - r_jk^2 - r_jh^2 - r_kh^2.

- [P] Williams t (S1 Eq. 12 to 14), df = n - 3:
  t = (r_jk - r_jh) sqrt( (n-1)(1+r_kh) / ( 2 ((n-1)/(n-3)) |R| + rbar^2 (1-r_kh)^3 ) ). S1 notes typographical
  errors in the cited literature for this formula: the cube on (1-r_kh) is dropped in one source, and another divides
  by the square root term and adds parentheses that multiply the denominator by 2.
- [P] Hotelling t (Eq. 10), Pearson and Filon z (Eq. 8, 9), Olkin z (Eq. 15), Dunn and Clark z (Eq. 16, 17),
  Hendrickson et al. modification of Williams t (Eq. 18) and Hittner et al. backtransformed-average variant (Eq. 27 to
  30) are the other implemented tests.
- [P] Steiger z (Eq. 19 to 21): z = (Z_jk - Z_jh) sqrt(n-3) / sqrt(2 - 2c) with
  c = [ r_kh (1 - 2 rbar^2) - (1/2) rbar^2 (1 - 2 rbar^2 - r_kh^2) ] / (1 - rbar^2)^2, which replaces r_jk and r_jh by
  their mean inside c.
- [P] Meng, Rosenthal and Rubin z (Eq. 22 to 26): z = (Z_jk - Z_jh) sqrt( (n-3) / (2 (1-r_kh) h) ), h = (1 - f r2) /
  (1 - r2), f = (1-r_kh) / (2 (1-r2)) with f <= 1, r2 = (r_jk^2 + r_jh^2)/2; the interval is (Z_jk - Z_jh) +- z_(alpha/2)
  sqrt(2 (1-r_kh) h / (n-3)) on the Z scale.
- [P] Zou interval (Eq. 31 to 36): with Fisher-scale limits l', u' = Z +- z_(alpha/2) / sqrt(n-3) mapped back by tanh to
  (l_1, u_1) and (l_2, u_2), and
  c = [ (r_kh - r_jk r_jh / 2)(1 - r_jk^2 - r_jh^2 - r_kh^2) + r_kh^3 ] / ((1 - r_jk^2)(1 - r_jh^2)),
  L = (r_jk - r_jh) - sqrt( (r_jk - l_1)^2 + (u_2 - r_jh)^2 - 2c (r_jk - l_1)(u_2 - r_jh) ) and
  U = (r_jk - r_jh) + sqrt( (u_1 - r_jk)^2 + (r_jh - l_2)^2 - 2c (u_1 - r_jk)(r_jh - l_2) ). The rendered pages of S1 (p. 2 and
  p. 7, checked as images, not only the text layer) print a minus sign before the square root of U in Eq. 4 and Eq. 32;
  the plus sign reproduces the PDF p. 9 interval, so the printed sign is a typographical error. (S1 p. 2, 7)
- [P] Independent groups: Fisher z = (Z_1 - Z_2) / sqrt(1/(n_1-3) + 1/(n_2-3)) (Eq. 2). (S1 p. 1)

## Worked example and reproduction check (PDF p. 8-9)

- [P] For r_jk = 0.1038, r_jh = 0.3213, r_kh = 0.0257, n = 291 the article prints Williams t = -2.7743 (df 288), Steiger
  z = -2.7513, Meng z = -2.7432, Dunn and Clark z = -2.7595, Pearson and Filon z = -2.7914, and the Zou 95 percent
  interval [-0.3689, -0.0630] for r_jk - r_jh = -0.2175.
- [I] A direct transcription of Eq. 12 to 14, 19 to 21, 22 to 25 and 31 to 36 reproduces the Williams, Steiger and Meng
  statistics and the Zou interval to four decimals (-2.7743, -2.7513, -2.7432, [-0.3689, -0.0630]); a repository implementation of the Williams, Steiger
  and Meng tests passes only when it reproduces these figures from the same inputs.
- [P] Independent-group example: r = 0.3213 versus 0.2024, n_1 = 291, n_2 = 334 gives Fisher z = 1.5869, p = 0.1125 and a
  Zou interval [-0.0281, 0.2637] that includes zero. (PDF p. 6-7)

## Mapping to this repository

Relevance: (a) none, (b) none, (c) none; the source grounds [critical peer review of hardware results](../../runbooks/critical-peer-review.md).

- [I] Two correlations that share one variable are dependent and overlapping: a measured response vector correlated with
  predictor A and with predictor B, over the same meshes, is the case r_jk versus r_jh. The Williams, Steiger or Meng
  test needs r_kh, the correlation between the two predictors, and the independent-group Fisher z is the wrong test.
  Correlations computed over disjoint mesh sets use the independent form.
- [I] A reviewer demands the interval of the difference (Zou or Meng) beside the p-value, and the tested threshold when
  the claim is "exceeds by at least delta". Deviations of the Fisher-scale approximations from small-n or
  strongly nonnormal data are outside this source; a bootstrap or permutation check on the same statistic covers them.
