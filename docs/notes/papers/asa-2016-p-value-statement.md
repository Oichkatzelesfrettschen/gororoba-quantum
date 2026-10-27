# ASA 2016 -- Statement on Statistical Significance and P-Values (Wasserstein and Lazar, The American Statistician 70, 129-133)

## Source copy and license

The statement itself is not retained. The retained file is the American Statistical Association's press release of
7 March 2016, which quotes the six principles in full:
[source PDF](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf), optional reading copy
`docs/local_source_cache/asa-2016-p-value-statement-release.pdf`, SHA-256
`5327785901ea402c063458e9d061b131a2f4a81c8a6d46fd9e217238b61f8ca9`, 242050 bytes, 3 pages. The PDF prints no license
or copyright statement, so the registry records the rights as unasserted and the file stays external. The publisher
route to the statement (https://www.tandfonline.com/doi/full/10.1080/00031305.2016.1154108) answered HTTP 403 to
automated retrieval on 2026-10-27 and the statement was not retrieved; the Crossref record identifies the statement
(volume 70, pages 129-133, issued 2 April 2016).

Tag convention: [P] marks release statements with their PDF page; [I] marks repository interpretation.

## Citation and provenance

- Statement: Ronald L. Wasserstein and Nicole A. Lazar, "The ASA's Statement on p-Values: Context, Process, and
  Purpose", The American Statistician 70(2), 129-133, DOI 10.1080/00031305.2016.1154108 (Crossref receipt in
  [SOURCES.json](../../SOURCES.json)). The release is the ASA's announcement of the statement.
- Reading scope: the 3-page release in full. The paragraph that elaborates each principle in the statement, and the
  statement's closing section, are unread.

## Six principles (PDF p. 2)

- [P] 1. P-values can indicate how incompatible the data are with a specified statistical model.
- [P] 2. P-values do not measure the probability that the studied hypothesis is true, or the probability that the data
  were produced by random chance alone.
- [P] 3. Scientific conclusions and business or policy decisions should not be based only on whether a p-value passes
  a specific threshold.
- [P] 4. Proper inference requires full reporting and transparency.
- [P] 5. A p-value, or statistical significance, does not measure the size of an effect or the importance of a result.
- [P] 6. By itself, a p-value does not provide a good measure of evidence regarding a model or hypothesis.

## Further statements of the release (PDF p. 1-2)

- [P] "Good statistical practice ... emphasizes principles of good study design and conduct, a variety of numerical and
  graphical summaries of data, understanding of the phenomenon under study, interpretation of results in context,
  complete reporting and proper logical and quantitative understanding of what data summaries mean." (PDF p. 1)
- [P] "The p-value was never intended to be a substitute for scientific reasoning" (Wasserstein); an editorial reliance on
  the p-value as gatekeeper feeds the file-drawer effect and practices called p-hacking and data dredging (Utts).
  (PDF p. 1)
- [P] Statisticians supplement or replace p-values with methods "that emphasize estimation over testing such as
  confidence, credibility, or prediction intervals; Bayesian methods; alternative measures of evidence such as likelihood
  ratios or Bayes factors; and other approaches such as decision-theoretic modeling and false discovery rates."
  (PDF p. 2)

## Mapping to this repository

Relevance: (a) none, (b) none, (c) none; the source grounds [critical peer review of hardware results](../../runbooks/critical-peer-review.md).

- [I] Principle 2 forbids reading p = 0.01 as a 1 percent chance that the effect is absent; a result document states the
  p-value as a statement about the data under the registered null model only.
- [I] Principles 3 and 5 require every decision statement to carry the effect size and its interval beside the
  threshold outcome; Principle 4 requires the count of registered contrasts and every executed arm.
- [I] The release does not carry the elaborations, so a claim that depends on the statement's wording (for example on
  Principle 6) needs the statement itself first; the reviewer cites the release only for the six sentences above.
