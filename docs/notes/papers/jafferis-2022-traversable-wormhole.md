# Jafferis et al. 2022 -- Traversable wormhole dynamics on a quantum processor (Nature 612, 51)

## Source copy and license

The article is closed. The Nature [article page](https://www.nature.com/articles/s41586-022-05424-3)
carries the rights line "2022 The Author(s), under exclusive licence to Springer Nature Limited" and
no Creative Commons license, and the Crossref record lists no license. No PDF of the article was
retrieved, and none is registered. An arXiv title search returned the two comment papers
([Kobrin et al.](2302.07897.md) and the [authors' reply](2303.15423.md)) and no preprint of the
article itself; no repository search beyond arXiv was run, so an open copy may exist elsewhere. The
two comment papers restate the protocol and the Hamiltonian in their own words and are the open
sources for the statements marked secondary below. [SOURCES.json](../../SOURCES.json) records two
retrieval receipts, the Crossref record and the article page, and no PDF identity.

Tag convention: [P] marks paper statements; [S] marks statements about the paper made by a comment
paper; [I] marks repository interpretation.

## Citation and provenance

- Authors: Daniel Jafferis; Alexander Zlokapa; Joseph D. Lykken; David K. Kolchmeyer; Samantha I.
  Davis; Nikolai Lauk; Hartmut Neven; Maria Spiropulu (the Crossref record lists these eight).
- Journal reference: Nature 612(7938), 51-55 (2022), published online 30 November 2022, DOI
  10.1038/s41586-022-05424-3 (Crossref receipt below).
- Reading scope: the article page's abstract (the `description` metadata, identical to the abstract),
  title, DOI, dates and rights line. The article body, Methods, the Supplementary Information and the
  figures unread.

| Source | URL | SHA-256 of retrieved bytes | Read for |
|---|---|---|---|
| Crossref record of the version of record | https://api.crossref.org/works/10.1038/s41586-022-05424-3 | `14ba970da173b4eedd7dfe15a24306fdc191f7926ec41e8ed353cfd116ebfe3f` | Bibliographic identity |
| Nature article page | https://www.nature.com/articles/s41586-022-05424-3 | `393f5c17f1b1ee7bc07d3c237be2bdf6567a025545f14cb7d0a1424d51cb68d6` | Abstract, rights line |

## Transcribed statements

- [P] Abstract (article page): the paper uses "the holographic correspondence of the SYK many-body
  system and gravity to probe the conjectured ER=EPR relation between entanglement and spacetime
  geometry through the traversable wormhole mechanism as implemented in the SYK model"; "a qubit can
  be used to probe the SYK traversable wormhole dynamics through the corresponding teleportation
  protocol", realized "as a quantum circuit, equivalent to the gravitational picture in the
  semiclassical limit of an infinite number of qubits".
- [P] Abstract: "we use learning techniques to construct a sparsified SYK model that we experimentally
  realize with 164 two-qubit gates on a nine-qubit circuit and observe the corresponding traversable
  wormhole dynamics"; the experiment ran "on the Google Sycamore processor".
- [P] Abstract: "despite its approximate nature, the sparsified SYK model preserves key properties of
  the traversable wormhole physics: perfect size winding, coupling on either side of the wormhole that
  is consistent with a negative energy shockwave, a Shapiro time delay, causal time-order of signals
  emerging from the wormhole, and scrambling and thermalization dynamics".
- [S] The comment of Kobrin, Schuster and Yao (p. 1 of [2302.07897](2302.07897.md)) gives the
  learned Hamiltonian of seven Majorana fermions as a sum of five four-fermion terms with
  coefficients -0.36, 0.19, -0.71, 0.22 and 0.49, states that the machine-learning procedure fits the
  teleportation behavior of the N = 10 SYK model, and reads the observable of the protocol as the
  mutual information I(P:T) between a reference qubit P and a readout qubit T (Fig. 2 caption).
  These values are the comment authors' transcription and are not checked against the article.

## Mapping to this repository

- [I] Vacuum and quantum-energy-teleportation notes
  ([vacuum_field_run_opportunities.md](../vacuum_field_run_opportunities.md)). The dispute recorded in
  the [comment](2302.07897.md) and the [reply](2303.15423.md) is a worked case of what an
  emulated-dynamics claim has to show: properties at the time of the protocol, controls on
  operators outside the training set and a null ensemble of equally structured models. The
  repository's quantum energy teleportation rows price their controls on the same footing; this
  article's own text was not read for them.
- [I] The claim reads through a learned, sparsified Hamiltonian, so the evidence that the experiment
  observed gravitational dynamics is the match of the learned model to the dense model, which the
  comment disputes; neither paper concerns a measurement of spacetime geometry.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] Everything attributed to the article above comes from its abstract or from the comment papers; no
equation, figure or Methods statement of the article was read. The repository takes no position on
whether the experiment observed traversable wormhole dynamics.
