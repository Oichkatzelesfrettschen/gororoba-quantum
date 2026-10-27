# Munafo et al. 2017 -- A manifesto for reproducible science (Nature Human Behaviour 1, 0021)

## Source copy and license

The [source PDF](https://www.nature.com/articles/s41562-016-0021.pdf) remains external to the published library. Its
optional reading copy is `docs/local_source_cache/munafo-2017-reproducible-science.pdf`;
[SOURCES.json](../../SOURCES.json) binds the bytes (SHA-256
`607a381bcdaf7d16e5801a570f64c7eb38eeb89bcbf30e343eb00a4ffcfeefd6`, 481779 bytes, 9 pages). The
[article page](https://www.nature.com/articles/s41562-016-0021) carries structured-data license
http://creativecommons.org/licenses/by/4.0/ and the PDF repeats a Creative Commons Attribution notice on PDF p. 9,
so the exact version qualifies for publication. The Nature route of `docs/verify_sources.py` accepts only article
identifiers of the form `s415NN-NNN-NNNNN-C`; `s41562-016-0021` carries a four-digit final group and fails that
pattern, so the PDF stays external until the verifier admits the identifier. The article page bytes are SHA-256
`3f177ff985580d26bb5e65c369567e47dcabd1fa5c472653af93aa05b77995c1`.

Tag convention: [P] marks paper statements with their PDF page; [I] marks repository interpretation. PDF p. N counts
the retained 9-page file; the article body runs on PDF p. 1 to 7, references and the rights notice after.

## Citation and provenance

- Authors: Marcus R. Munafo, Brian A. Nosek, Dorothy V. M. Bishop, Katherine S. Button, Christopher D. Chambers,
  Nathalie Percie du Sert, Uri Simonsohn, Eric-Jan Wagenmakers, Jennifer J. Ware, John P. A. Ioannidis. Perspective,
  Nature Human Behaviour 1, article 0021, published 10 January 2017, DOI 10.1038/s41562-016-0021 (Crossref receipt in
  [SOURCES.json](../../SOURCES.json)).
- Reading scope: PDF p. 1 to 7 in full (text, Table 1, Boxes 1 to 6, Figures 1 and 2 as captions); references not read.

## The problem (PDF p. 1-2)

- [P] Apophenia, confirmation bias and hindsight bias combine to produce false conclusions; over-interpretation of noise
  is facilitated by data analysis that is "rapid, flexible and automated". (PDF p. 1)
- [P] A high-dimensional dataset admits hundreds or thousands of reasonable analysis pipelines; applying almost 7,000
  pipelines to one fMRI dataset left over 90 percent of voxels significant in at least one analysis. (PDF p. 1)
- [P] Hypotheses that emerge to fit the data and are reported without indication of their post hoc origin are
  "not scientific discovery, but self-deception". (PDF p. 2)
- [P] Figure 1 lists the threats along the hypothetico-deductive cycle: low statistical power and poor quality control at
  design, failure to control for bias and P-hacking in conduct and analysis, HARKing (hypothesizing after the results are
  known) at interpretation, and publication bias at the end. (PDF p. 2)

## Methods measures (PDF p. 2-3)

- [P] Blinding mitigates self-deception: a data analyst can be blinded to key parts of the data; "in some physical
  sciences this approach has been extended to include deliberate perturbations in or masking of data to allow data
  preparation (for example, identification of outliers) to proceed without the analyst being able to see the
  corresponding results". (PDF p. 2)
- [P] Pre-registration of the study design, primary outcomes and analysis plan "is a highly effective form of blinding
  because the data do not exist and the outcomes are not yet known". (PDF p. 2)
- [P] Training must cover P value interpretation, limits of null-hypothesis significance testing, statistical power, the
  accuracy of reported effect sizes, and whether a sample that produced significance is large enough to replicate.
  (PDF p. 2)
- [P] Independent methodologists with no stake in the topic mitigate financial and non-financial conflicts of interest
  (Box 1, the CHDI Independent Statistical Standing Committee). (PDF p. 2, 4)
- [P] Studies of statistical power persistently find it below, sometimes well below, 50 percent; low power raises both
  false-positive and false-negative results. (PDF p. 2)

## Reporting and pre-registration (PDF p. 3-5)

- [P] Pre-registration was introduced against publication bias (the file drawer) and analytical flexibility, in
  particular outcome switching: "a researcher may include ten variables that could be considered outcomes ... and, once
  the results are known, select the subset of outcomes that show statistically significant results". Data-contingent
  choices of models, exclusion rules and covariates are P-hacking, and pre-registration can protect against all of them.
  (PDF p. 3)
- [P] The strongest form registers the study with a commitment to publish results and pre-specifies design, primary
  outcome and analysis plan before the study or knowledge of outcomes; it "makes clear the distinction between
  data-independent confirmatory research ... and data-contingent exploratory research". (PDF p. 3-4)
- [P] Pre-registration improves discoverability and does not guarantee usability: only 13 percent of registered trials
  published outcomes completely consistent with their registered commitments (COMPare); in a psychology audit about 40
  percent of reports omitted an experimental condition and about 70 percent omitted an outcome measure, and the omitted
  measures were more likely negative with smaller effect sizes. (PDF p. 4)
- [P] Reporting guidelines are necessary and not sufficient for reporting bias; their effect is assessed best by
  randomized trials (Box 4). (PDF p. 5)
- [P] Registered Reports split review into a stage before and a stage after results; in-principle acceptance is
  conditional on adherence to the approved protocol, pre-specified quality checks and conclusions that are
  "appropriately evidence-bound"; unregistered exploratory analyses are reported if "clearly labelled as post hoc"
  (Box 3). The format also targets CARKing, critiquing after the results are known, by reviewers. (PDF p. 5)

## Reproducibility and disclosure (PDF p. 5-6)

- [P] "Transparency is superior to trust": claims gain credibility through the methodology, data and process of
  analysis being open to review. (PDF p. 5)
- [P] Data sharing in public repositories gives accountability and lets reanalysis detect crucial mistakes (Box 5).
  (PDF p. 6)
- [P] Full disclosure describes the whole design and all data collected. "The probability of a single variable achieving
  P < 0.05 just by chance is 5%, but the probability of one of fifteen variables achieving P < 0.05 is 54%"; readers
  cannot evaluate research when authors do not say whether one or fifteen variables were collected (Box 6). The
  21-word statement reports how sample size was determined, all data exclusions, all manipulations and all measures.
  (PDF p. 6)
- [I] Check: 1 - 0.95^15 = 0.537, matching the printed 54 percent.

## Evaluation and incentives (PDF p. 5-7)

- [P] Pre- and post-publication review and preprints diversify evaluation (arXiv is named for the physical sciences).
  (PDF p. 5-6)
- [P] Journals reward novel, positive and clean results, so incentives raise false positives; replication alone "may not
  suffice to rid us of false results". Proposed solutions need iterative evaluation and some "may be ineffective or even
  harmful". (PDF p. 7)

## Mapping to this repository

Relevance: (a) none, (b) none, (c) none; the source grounds [critical peer review of hardware results](../../runbooks/critical-peer-review.md).

- [I] The Table 1 and Box 6 disclosure demand maps to a run record that lists every registered contrast, every executed
  circuit and every exclusion; a reviewer counts the contrasts against the 54 percent arithmetic.
- [I] The data-masking idea of PDF p. 2 corresponds to freezing the analysis at an experiment digest before the raw
  counts are read, which `collect.json` does in this repository; a second analysis of the same raw files is labeled
  exploratory by its own analysis digest.
- [I] The COMPare and Franco audit numbers (PDF p. 4) justify checking a published result against its registered
  outcome list, outcome by outcome, rather than trusting the summary.
- [I] Nosek et al. 2018 (PNAS 115, 2600) treat preregistration in depth; the publisher blocked automated retrieval, so
  the registry holds a descriptive record only and this note carries the repository's preregistration criteria.
