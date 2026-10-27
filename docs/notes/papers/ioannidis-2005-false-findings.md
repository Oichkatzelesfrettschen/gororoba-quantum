# Ioannidis 2005 -- Why Most Published Research Findings Are False (PLoS Medicine 2(8): e124)

## Source copy and license

The [source PDF](https://journals.plos.org/plosmedicine/article/file?id=10.1371/journal.pmed.0020124&type=printable)
remains external to the published library. Its optional reading copy is
`docs/local_source_cache/ioannidis-2005-false-findings.pdf`; [SOURCES.json](../../SOURCES.json) binds the bytes
(SHA-256 `ffc1005680cb620eec4c913437dfabbf311b535cfe16cbaeb2faec1f92afc362`, 255629 bytes, 6 pages). The article
page ([rights evidence](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.0020124)) and the PDF
(PDF p. 1) state that the article is "distributed under the terms of the Creative Commons Attribution License"
without a version number; Crossref labels the record CC BY 4.0. The exact-version grant therefore rests on Crossref
alone, and the verifier in `docs/verify_sources.py` has no publication route for a PLoS host, so the PDF stays external
until both gaps close.

Tag convention: [P] marks paper statements with their PDF page; [I] marks repository interpretation. PDF p. N counts
the retained file (journal pages e696 to e701).

## Citation and provenance

- Author: John P. A. Ioannidis. Essay, PLoS Medicine 2(8): e124, August 2005, DOI 10.1371/journal.pmed.0020124
  (Crossref receipt in [SOURCES.json](../../SOURCES.json)).
- Reading scope: all six PDF pages, main text, Tables 1 to 4, Box 1 and the reference list titles. Figures 1 and 2 were
  read as captions only.

## The model

- [P] A research finding is any relationship that reaches formal statistical significance. R is the ratio of true to
  non-true relationships among those tested in the field; the pre-study probability is R/(R+1). Power is 1-beta;
  alpha is the Type I error rate. (PDF p. 1)
- [P] Without bias, the post-study probability that a claimed finding is true is
  PPV = (1-beta) R / (R - beta R + alpha); the finding is more likely true than false only if (1-beta) R > alpha.
  (PDF p. 1-2, Table 1)
- [P] Bias u is the proportion of probed analyses that would not have been findings but are reported as findings through
  design, data, analysis or presentation choices, assumed independent of whether a true relationship exists:
  PPV = ((1-beta) R + u beta R) / (R + alpha - beta R + u - u alpha + u beta R); PPV falls with u unless 1-beta <= alpha.
  (PDF p. 2, Table 2)
- [P] For n independent teams of equal power on one question:
  PPV = R (1 - beta^n) / (R + 1 - (1-alpha)^n - R beta^n). PPV falls with n unless 1-beta < alpha. For unequal power,
  beta^n becomes the product of the beta_i. (PDF p. 2, Table 3)
- [I] Check of the transcription: the nine rows of Table 4 (PDF p. 5) reproduce from the bias formula at alpha = 0.05,
  for example power 0.80, R = 1:1, u = 0.10 gives 0.850, and power 0.20, R = 1:1000, u = 0.20 gives 0.0015. The Box 1
  figures reproduce for the 12-fold rise (11.99) and the biased value 4.4e-4, and the ten-team no-bias value computed
  from the Table 3 formula with R = 1e-4 and power 0.6 is 2.5e-4 where the text prints 1.5e-4 (PDF p. 4); the printed
  value deviates from the paper's own formula.

## Corollaries (PDF p. 2-4)

- [P] Corollary 1: smaller studies give less probable findings, because power falls toward alpha.
- [P] Corollary 2: smaller effect sizes give less probable findings; fields with true effects below a relative risk of
  1.05 are plagued by almost ubiquitous false positive claims.
- [P] Corollary 3: the greater the number and the lesser the preselection of tested relationships, the lower the PPV;
  confirmatory designs beat hypothesis-generating ones.
- [P] Corollary 4: flexibility in designs, definitions, outcomes and analytical modes raises u; common standards and
  unequivocal outcomes raise the proportion of true findings; selective outcome reporting persists even in randomized
  trials, so abolishing selective publication alone leaves the bias in place.
- [P] Corollary 5: financial and non-financial interests and prejudice (belief in a theory, commitment to one's own
  findings) raise u.
- [P] Corollary 6: the more teams in a field, the lower the PPV of an isolated finding, and the faster extreme claims
  alternate with extreme refutations (the Proteus phenomenon).

## Simulation and null-field reading (PDF p. 4-5)

- [P] PPV above 50 percent is difficult to reach: a well-powered randomized trial at 1:1 pre-study odds reaches about
  0.85; an adequately powered exploratory study at 1:10 reaches 0.20; discovery-oriented work with a 1:1000 ratio of
  true to tested relationships reaches 0.001 to 0.0015. (Table 4)
- [P] In a null field every claimed effect size measures net bias, and "too large and too highly significant effects may
  actually be more likely to be signs of large bias in most fields of modern research" and "should lead investigators to
  careful critical thinking about what might have gone wrong with their data, analyses, and results." (PDF p. 5)

## Recommendations (PDF p. 5-6)

- [P] Put large studies where pre-study probability is already considerable, and test major concepts rather than
  narrow claims; extremely large studies find significance for trivial effects.
- [P] Emphasize the totality of evidence over the significant findings of any single team.
- [P] Register studies upfront where feasible; otherwise borrow the principles of developing and adhering to a protocol
  from randomized trials.
- [P] Estimate the range of R before an experiment and ask what the chances are that a true relationship is tested; a
  single report cannot reveal how much testing happened outside it, and multiple-testing corrections cannot recover
  that count.

## Mapping to this repository

Relevance: (a) none, (b) none, (c) none; the source grounds [critical peer review of hardware results](../../runbooks/critical-peer-review.md).

- [I] A reviewer states the number of hypotheses, analyses and parameter values probed (the denominator c and the
  forking paths u) before reading a p-value; the runbook items on preregistration, multiplicity and claim wording cite
  Corollaries 3 and 4 and the n-team formula.
- [I] An observed correlation far above the instrument's characterized scale prompts a search for bias before
  celebration (PDF p. 5); the runbook applies this to a hardware correlation that exceeds its simulated ceiling.
- [I] The pre-study odds R have no value in this repository; a reviewer names the assumed range instead of leaving the
  implicit R at 1:1 (PDF p. 6).
