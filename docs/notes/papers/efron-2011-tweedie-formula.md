# Efron: Tweedie's formula and selection bias

## Source copy and license

The retained reading copy is Bradley Efron's author manuscript from his
[Stanford paper page](https://efron.ckirby.su.domains/papers/2011TweediesFormula.pdf) (22 pages, TeX build of 4 August
2011). It carries no license notice. The same manuscript is deposited in PubMed Central as PMC3325056 (NIHMS316433),
whose article record carries only the PMC copyright notice; [PMC's notice](https://pmc.ncbi.nlm.nih.gov/about/copyright/)
(SHA-256 of the inspected bytes in the registry) states that without an explicit statement standard copyright
protection applies. The copy therefore stays out of the published library: it is the
ignored `docs/local_source_cache/efron-2011-tweedie-formula.pdf`, with a second copy in the owner's private documents
repository. [SOURCES.json](../../SOURCES.json) binds the SHA-256, the evidence hashes and the reading scope.
Attribution to Bradley Efron applies to every statement below.

Tag convention: [P] marks a statement of the paper; [I] marks repository interpretation. Page numbers are PDF page
indices of the retained manuscript; the PMC deposit numbers the same equations identically.

## Citation and provenance

- Bradley Efron, "Tweedie's Formula and Selection Bias", Journal of the American Statistical Association 106(496),
  1602-1614 (2011), DOI 10.1198/jasa.2011.tm11181; the Crossref record is a registered retrieval receipt. The version
  of record was not retrieved.
- Retained PDF: 22 pages, 440275 bytes, SHA-256 `af27a444711d8d8c775ff8e6e3a19f7af32efe003fdb6ea9014af9782f2754c9`,
  retrieved 2026-11-01 01:58 UTC.
- Reading scope: Sections 1 to 4 in full, Section 7 Remark I; Sections 5 (relevance) and 6 (false discovery rates)
  read for their statements only.

## Statements

- [P] Model (1.1), p. 1: `z_i ~ N(mu_i, sigma^2)`, i = 1..N, possibly correlated. Selection bias: the largest few
  `z_i` overestimate their `mu_i` (abstract).
- [P] Bayes model (1.2), p. 2: `mu ~ g(.)` and `z | mu ~ N(mu, sigma^2)`, with marginal density
  `f(z) = integral phi_sigma(z - mu) g(mu) dmu` (1.3).
- [P] Tweedie's formula (1.4), p. 2: `E{mu | z} = z + sigma^2 l'(z)` with `l'(z) = d/dz log f(z)`. The correction
  depends on the marginal density alone, so it can be estimated from the observed `z_i` without modeling `g`.
- [P] Posterior to second order (2.8), p. 4: `mu | z ~ (z + sigma^2 l'(z), sigma^2 (1 + sigma^2 l''(z)))`.
- [P] Normal prior (3.7), p. 8: `mu ~ N(0, A)`, `z | mu ~ N(mu, 1)`. Then `z ~ N(0, V)` with `V = A + 1`,
  `l'(z) = -z / V`, and Tweedie's formula becomes `E{mu | z} = (1 - 1/V) z` (3.8).
- [P] James-Stein (3.9), p. 8: substituting the unbiased estimate `(N - 2) / sum z_j^2` for `1/V` gives
  `mu_hat_i = (1 - (N - 2) / sum z_j^2) z_i`.
- [P] Regret and empirical Bayes information, Section 4, p. 9: the regret of the James-Stein rule at `z_0` grows like
  `c(z_0) / N` with `c(z_0) = 2 (z_0 / V)^2` under (4.10), and the empirical Bayes information is
  `I(z_0) = (V / z_0)^2 / 2` (4.11): an estimate at a large `|z_0|` borrows less strength from the other cases.
- [P] Remark I, pp. 20-21: in the James-Stein situation the posterior is `mu_0 | z_0 ~ N(C z_0, C)`, `C = 1 - 1/V`
  (7.24); with `C` estimated, `N(C_hat z_0, C_hat)` (7.25) understates the uncertainty, and (7.26) adds the variance
  `2 z_0^2 / (V^2 (N - 4))` for the estimation of `V`. That added variance is the James-Stein regret (4.8); Morris
  (1983) derives (7.26) with `N - 2` in place of `N - 4` from a hierarchical Bayes formulation.

## Use in this repository

- [I] [belenos-best-mesh-design-investigation.md](../../design/belenos-best-mesh-design-investigation.md) applies
  (3.7)-(3.8) to the six block-A minus block-B correctness differences of the Belenos teleportation meshes, scaled by
  each difference's binomial standard error. With six inputs the plug-in `C` of (3.9) is unstable, so the analysis
  carries the between-mesh standard deviation `tau` as uncertain under a uniform prior on [0, 0.25], which is the
  concern (7.26) addresses with an added variance term
  (`scripts/belenos_best_mesh_first_principles.py`, function `shrinkage`).
