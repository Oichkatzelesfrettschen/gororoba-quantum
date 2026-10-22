# Quaternionic foundations: bibliographic verification and reading boundaries

The source audit separates deposited bibliographic identities, abstract claims and
body readings. [SOURCES.json](../../SOURCES.json) records the response hashes,
retrieval times and reading scopes. Publisher PDFs remain external. [P] marks a
source statement; [I] marks a repository interpretation. Metadata verification
establishes identity rather than a theorem or experimental replication.

## Verified identities

| Source | Citation | Verified scope |
|---|---|---|
| Solèr | M. P. Solèr, "Characterization of hilbert spaces by orthomodular spaces", Communications in Algebra 23(1), 219–243 (1995), DOI 10.1080/00927879508825218 | Crossref identity; theorem body unreviewed |
| Stueckelberg | E. C. G. Stueckelberg, "Quantum Theory in real Hilbert-Space", Helvetica Physica Acta 33 (1960), DOI 10.5169/seals-113093 | DataCite author, title, year and publisher; ETH journal viewer identifies volume and first page 727; last page 752 remains a secondary citation |
| Finkelstein et al. | David Finkelstein, Josef M. Jauch, Samuel Schiminovich and David Speiser, "Foundations of Quaternion Quantum Mechanics", Journal of Mathematical Physics 3(2), 207–220 (1962), DOI 10.1063/1.1703794 | Crossref identity and deposited abstract |
| Adler | Stephen L. Adler, Quaternionic Quantum Mechanics and Quantum Fields, Oxford University Press (1995), ISBN 9780195066432, DOI 10.1093/oso/9780195066432.001.0001 | Crossref book identity, author, publisher and 27 April 1995 print date; deposited title has transcription defects: "Ouaternionic Quantum Mechanics and Ouanturn Fields"; readable title also appears in the reviewed authors' reply reference 4 |
| Peres | Asher Peres, "Proposed Test for Complex versus Quaternion Quantum Theory", Physical Review Letters 42(11), 683–686 (1979), DOI 10.1103/PhysRevLett.42.683 | Crossref identity; proposal body unreviewed |
| Kaiser et al. | H. Kaiser, E. A. George and S. A. Werner, "Neutron interferometric search for quaternions in quantum mechanics", Physical Review A 29(4), 2276–2279 (1984), DOI 10.1103/PhysRevA.29.2276 | Crossref identity; experimental body and numerical bound unreviewed |
| Renou et al. | Marc-Olivier Renou, David Trillo, Mirjam Weilenmann, Thinh P. Le, Armin Tavakoli, Nicolas Gisin, Antonio Acín and Miguel Navascués, "Quantum theory based on real numbers can be experimentally falsified", Nature 600(7890), 625–629 (2021), DOI 10.1038/s41586-021-04160-4 | Crossref identity and deposited abstract |

## Abstract-level consequences

- [P] Finkelstein and colleagues identify composite systems as a principal
  difficulty because the ordinary tensor product fails under noncommutativity.
  Their abstract describes additional degrees of freedom and a generalized
  Stone theorem. [I] The abstract alone fails to verify a precise spectral
  theorem or establish that all composite quaternionic models are undefined.
- [P] Renou and colleagues prove different predictions for real and complex
  formulations in networks comprising independent states and measurements.
  Their abstract proposes a Bell-like experiment whose successful realization
  would disprove the specified real theory. [I] The 2021 article supplies a
  theoretical discrimination result, rather than an experimental execution.
- [I] Solèr's identity leaves theorem hypotheses as a reading obligation.
  A finite hardware encoding cannot establish a universal field-choice result.
- [I] Stueckelberg's bibliographic identity leaves the uncertainty-principle and
  complex-structure argument as a reading obligation. The draft's universal
  dismissal of real theories exceeds the admitted reading.
- [I] Adler's book identity leaves the claimed low-energy averaging or complex
  projection mechanism unreviewed. That mechanism needs a chapter and model
  before the repository can turn a residual coupling into a falsifier.

## Retrieval identities

| Record | Metadata endpoint | SHA-256 of inspected response |
|---|---|---|
| Soler 1995 | https://api.crossref.org/works/10.1080/00927879508825218 | `bbac3fd11e53de3346ef7ff9cf646d73fe94c3e6c8bfcc4b5af3ad39cc638c7b` |
| Peres 1979 | https://api.crossref.org/works/10.1103/PhysRevLett.42.683 | `0bcb25af10554712befda134dc1b500b0e03394cef2f06eb8e8752f155e62870` |
| Finkelstein et al. 1962 | https://api.crossref.org/works/10.1063/1.1703794 | `954b2ddba400d0028c0c2c78c57d678f98d7b946c1a1c11ca5d095c52f4c487a` |
| Kaiser et al. 1984 | https://api.crossref.org/works/10.1103/PhysRevA.29.2276 | `7fc0e4a8a36703ed0fd8e0c3a80b8681a8158648f936f5e06f8236fef2242134` |
| Renou et al. 2021 | https://api.crossref.org/works/10.1038/s41586-021-04160-4 | `e0386a70a8c252211caeb63f01ed8d1ceec5e19b6c02ce40b2be06f57e1988e0` |
| Adler 1995 book | https://api.crossref.org/works/10.1093/oso/9780195066432.001.0001 | `2642ee3d8ab5eacf85e748da26c0d9f2cf183a32be3dc47f3734c0c9b7d3a84a` |
| Stueckelberg 1960 | https://api.datacite.org/dois/10.5169/seals-113093 | `b5d5ea35698c3bfe5817bb6dd0b4fe6109026cddf01ba172f6915b046e6ee5b7` |

The [ETH viewer](https://www.e-periodica.ch/digbib/view?pid=hpa-001:1960:33::735)
identifies Stueckelberg's article title and page 727 in its contents table.
The canonical local historical review cites pages 727–752; that secondary
locator remains separate from DataCite's fields. Automated PDF retrieval from
the archive returned HTML, so the source body remains unreviewed.

## Relevance

[I] Calibration-aware compilation: none. Cayley-Dickson structure: interpretive
boundary. Factoring resource estimates: none. The [optical reading addendum](quaternionic-optical-bound-reading.md)
records the exact-version Procopio/Adler exchange and its narrower bound.
