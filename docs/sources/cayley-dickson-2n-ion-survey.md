# Survey of Cayley-Dickson sources at dimension 16 and above

This survey inventories the literature on the Cayley-Dickson (CD) algebras of dimension 16 and up (the sedenions, then the
32-dimensional pathions or trigintaduonions, the 64-dimensional chingons, the 128-dimensional routons, the 256-dimensional voudons
and the general `2^n`-ions) and records the disposition of every candidate against the source registry
[SOURCES.json](../SOURCES.json). The product convention of the repository is `cd_core`'s
`(a,b)(c,d) = (ac - conj(d) b, d a + b conj(c))` over the XOR index
([cd_core.py](../../gororoba_quantum/cd_core.py), `cd_sign`).

Counts: 85 candidates; 31 registered on main; 3 registered on the unmerged branch `sources/sedenion-graph-and-structure-papers`;
20 admitted here (3 published under CC BY 4.0, 17 external with ignored local reading copies); 31 candidates not admitted. The
survey creates no metadata-only registry entry: every admitted source has a readable copy, and the 31 rows without admission appear
only below.

## Method

The inventory merges five searches, all read-only. Each check below names the query and its outcome.

- arXiv API (`export.arxiv.org`): keyword queries over titles and abstracts for Cayley-Dickson, sedenion, pathion, trigintaduonion,
  `2^n`-ion, zero divisor and doubling terms, plus author queries for every author of a registered source. 344 distinct records
  came back; each was triaged by title and abstract, and each admitted note states its own reading scope.
- zbMATH Open: keyword queries for the same terms, triaged together with the Crossref lookups below to find the non-arXiv items.
- Crossref (`api.crossref.org`): title and DOI lookups for every published journal identity, saved as retrieval receipts in the
  registry (12 receipts for the notes admitted here).
- Semantic Scholar, for the five registered sources math/0511691, math/0702075, math/0512517, 0905.2987 and 2608.08232. Reference
  lists were retrieved for all five. Citation lists (later papers that cite the source) were retrieved for math/0702075 and 0905.2987
  and are `not run` for math/0511691, math/0512517 and 2608.08232 (HTTP 429 after four attempts), so a later citer of those three
  sources may be missing here.
- The private bibliography `references.bib` of the author's reading collection, which added only Cawagas 2004 and a sedenion
  physics paper by Chanyal that this survey does not retain.

A candidate qualifies when it states a result about CD algebras at dimension 16 or above (an identity, a classification, a
construction, a sign or loop structure, a zero-divisor or annihilator result, or a polynomial result), or a convention that other
registered sources depend on. Admission is capped at 20 new sources; a qualifying candidate beyond the cap, a source without a
retrievable copy and a source outside the license allowlist of `docs/verify_sources.py` stay in the table as not admitted.

Admission follows [the rights policy](../SOURCES.json): the exact-version arXiv abstract page is captured under
`docs/evidence/source_rights/`; a verified CC BY 4.0 or CC0 grant publishes the unchanged PDF under `docs/pdf/`, and every other
copy stays in the ignored `docs/local_source_cache/`. Each admitted note tags statements `[P]` (paper) and `[I]` (repository
inference), states the paper's multiplication convention, and replays the checkable statements against `cd_core`.

## Candidate table

Dispositions: registered (an existing note), branch (registered on the unmerged sibling branch), new (admitted here), or not
admitted with the reason. A license name is the exact-version license of the registered copy.

### Admitted here

| Identifier | Title | Authors | Year | Dimensions | License | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| arXiv 0804.3416v2 | Voyage by Catamaran | de Marrais | 2008 | 16 to 256 (box-kite trips N = 4 to 8) | arXiv nonexclusive | new, external: [note](../notes/papers/0804.3416.md) |
| arXiv 0907.2047v3 | The subalgebra structure of the Cayley-Dickson algebra of dimension 32 | Cawagas, Carrascal, Bautista, Sta. Maria, Urrutia, Nobles | 2009 | 32 | arXiv nonexclusive | new, external: [note](../notes/papers/0907.2047.md) |
| arXiv math/0404395v1 | Alternative elements in the Cayley-Dickson algebras | Moreno | 2004 | all `2^n` (checked 16, 32) | arXiv assumed 1991-2003 | new, external: [note](../notes/papers/math-0404395.md) |
| arXiv math/0512516v1 | Monomorphisms between Cayley-Dickson algebras | Moreno | 2005 | all `2^n` (checked 16, 32) | arXiv assumed 1991-2003 | new, external: [note](../notes/papers/math-0512516.md) |
| arXiv math/0405424v1 | The exponential map on the Cayley-Dickson algebras | Moreno | 2004 | all `2^n` | arXiv assumed 1991-2003 | new, external: [note](../notes/papers/math-0405424.md) |
| arXiv math/0404172v1 | Hopf construction map in higher dimensions | Moreno | 2004 | all `2^n` | arXiv assumed 1991-2003 | new, external: [note](../notes/papers/math-0404172.md) |
| arXiv 1102.5151v2 | Automorphism groups of Cayley-Dickson loops | Kirshtein | 2011 | all `2^n` (checked 16, 32) | arXiv nonexclusive | new, external: [note](../notes/papers/1102.5151.md) |
| arXiv 1405.6888v2 | Cayley-Dickson algebras and finite geometry | Saniga, Holweck, Pracna | 2014 | 8 to 64 | arXiv nonexclusive | new, external: [note](../notes/papers/1405.6888.md) |
| arXiv 2606.27798v2 | Involutions in the Cayley-Dickson construction | Aryapoor, Back, Pautrel | 2026 | 8, 16, 32 (general `n` stated) | arXiv nonexclusive | new, external: [note](../notes/papers/2606.27798.md) |
| arXiv 2609.11588v1 | Quasilinear multiplication in the real Cayley-Dickson tower | Lemley | 2026 | 2 to 256 | CC BY 4.0 | new, published: [note](../notes/papers/2609.11588.md) |
| arXiv 2603.20495v3 | Central products of Cayley-Dickson loops | Chapman, Levin | 2026 | all `2^n` (checked to 64) | CC BY 4.0 | new, published: [note](../notes/papers/2603.20495.md) |
| arXiv 2501.00123v1 | Loops with involution and the Cayley-Dickson doubling process | Chapman, Levin, Vishne, Zaninelli | 2024 | all `2^n` (Aut counted at 8, 16) | arXiv nonexclusive | new, external: [note](../notes/papers/2501.00123.md) |
| arXiv 1707.07318v4 | The Cayley-Dickson doubling products | Bales | 2017 | 8 to 64 | arXiv nonexclusive | new, external: [note](../notes/papers/1707.07318.md) |
| arXiv 1107.1301v5 | A catalog of Cayley-Dickson-like products | Bales | 2011 | 8 to 64 | arXiv nonexclusive | new, external: [note](../notes/papers/1107.1301.md) |
| arXiv hep-th/0601033v1 | Alternativity and reciprocity in the Cayley-Dickson algebra | Kuwata, Fujii, Nakashima | 2006 | 16, 32 (general `n` stated) | arXiv assumed 1991-2003 | new, external: [note](../notes/papers/hep-th-0601033.md) |
| arXiv 2505.06011v1 | Construction of exceptional Lie algebra G2 and non-associative algebras using Clifford algebra | Wilmot | 2025 | 8, 15-dimensional imaginary space (16) | CC BY-NC-SA 4.0 | new, external: [note](../notes/papers/2505.06011.md) |
| arXiv 2205.05605v1 | Roots and critical points of polynomials over Cayley-Dickson algebras | Chapman, Guterman, Vishkautsan, Zhilina | 2022 | all `2^n` (replayed at 16) | arXiv nonexclusive | new, external: [note](../notes/papers/2205.05605.md) |
| arXiv 2512.22134v3 | A mnemonic matrix rule for octonionic multiplication and its extension to the Cayley-Dickson tower | Gazeau | 2025 | 8 to 64 | CC BY 4.0 | new, published: [note](../notes/papers/2512.22134.md) |
| Brown, Pacific J. Math. 20 (1967) | On generalized Cayley-Dickson algebras | R. B. Brown | 1967 | 16, 32, 64 | publisher copyright, no open license | new, external: [note](../notes/papers/brown-1967-generalized-cayley-dickson.md) |
| Chan and Dokovic, Canad. Math. Bull. 49 (2006) | Conjugacy classes of subalgebras of the real sedenions | Chan, Dokovic | 2006 | 16 | publisher copyright, no open license | new, external: [note](../notes/papers/chan-dokovic-2006-sedenion-subalgebras.md) |

### Registered on main

| Identifier | Title | Authors | Year | Dimensions | Disposition |
| --- | --- | --- | --- | --- | --- |
| arXiv math/0011260 | The 42 assessors and the box-kites they fly | de Marrais | 2000 | 16 | registered: [note](../notes/papers/math-0011260.md) |
| arXiv math/0207003 | Flying higher than a box-kite | de Marrais | 2002 | 16, 32, higher | registered: [note](../notes/papers/math-0207003.md) |
| arXiv math/0403113 | Box-kites III | de Marrais | 2004 | 16 to `2^N` | registered: [note](../notes/math-0403113.md) |
| arXiv math/0603281 | Presto! Digitization, part I | de Marrais | 2006 | zero-divisor ensembles | registered: [note](../notes/papers/math-0603281.md) |
| arXiv math/0703745 | Placeholder substructures I | de Marrais | 2007 | 32 and higher | registered: [note](../notes/papers/math-0703745.md) |
| arXiv 0704.0026 | Placeholder substructures II | de Marrais | 2007 | 32 and higher | registered: [note](../notes/papers/0704-0026.md) |
| arXiv 0704.0112 | Placeholder substructures III | de Marrais | 2007 | 32 and higher | registered: [note](../notes/papers/0704-0112.md) |
| arXiv math/0511691 | Large annihilators in Cayley-Dickson algebras | Biss, Dugger, Isaksen | 2005 | 16 and all `n >= 4` | registered: [note](../notes/math-0511691.md) |
| arXiv math/0512517 | Constructing zero divisors in the higher dimensional Cayley-Dickson algebras | Moreno | 2005 | all `n >= 4` | registered: [note](../notes/math-0512517.md) |
| arXiv math/0702075 | Large annihilators in Cayley-Dickson algebras II | Biss, Christensen, Dugger, Isaksen | 2007 | `n >= 3` | registered: [note](../notes/math-0702075.md) |
| arXiv 0905.2987 | Eigentheory of Cayley-Dickson algebras | Biss, Christensen, Dugger, Isaksen | 2009 | all `n` | registered: [note](../notes/0905.2987.md) |
| arXiv q-alg/9710013 | The zero divisors of the Cayley-Dickson algebras | Moreno | 1997 | all `n >= 4` | registered: [note](../notes/papers/q-alg-9710013.md) |
| arXiv 2505.11747 | Structure of the Cayley-Dickson algebras | Wilmot | 2025 | 16 and higher | registered: [note](../notes/papers/2505.11747.md) |
| arXiv 2512.07210 | Automorphisms of sedenions | Wilmot | 2026 | 16 | registered: [note](../notes/papers/2512.07210.md) |
| arXiv 2512.13002 | Determinant factorization for left multiplication in the sedenions | Koebisu | 2026 | 16 | registered: [note](../notes/papers/2512.13002.md) |
| arXiv 2411.18881 | The geometry of sedenion zero divisors | Reggiani | 2024 | 16 | registered: [note](../notes/papers/2411.18881.md) |
| arXiv 2608.08232 | Determinant factorization in dimension 32 | Koebisu | 2026 | 32, `n >= 2` | registered: [note](../notes/2608.08232.md) |
| arXiv 2608.26893 | Doubly alternative zero divisors and anisotropic annihilators | Zhilina | 2026 | 16, 32 | registered: [note](../notes/2608.26893.md) |
| arXiv 2608.26903 | Relation graphs of the sedenion algebra | Guterman, Zhilina | 2021 | 16 | registered: [note](../notes/papers/2608-26903.md) |
| arXiv 2608.28163 | Orthogonality graphs, part II | Zhilina | 2026 | 16 and higher | registered: [note](../notes/papers/2608.28163.md) |
| arXiv 2608.28176 | Orthogonality graphs, part I | Zhilina | 2026 | 16 and higher | registered: [note](../notes/papers/2608.28176.md) |
| arXiv 2609.10569 | Sedenions, Clifford algebras and three fermion generations | Gresnigt | 2026 | 16 | registered: [note](../notes/papers/2609.10569.md) |
| arXiv 1207.4230 | Multiplication groups and inner mapping groups of Cayley-Dickson loops | Kirshtein | 2012 | all `n` (128 mentioned) | registered: [note](../notes/1207.4230.md) |
| arXiv 1107.1375 | Cayley-Dickson and Clifford algebras as twisted group algebras | Bales | 2011 | all `n` | registered: [note](../notes/papers/1107.1375.md) |
| arXiv 1602.02317 | An alternate Cayley-Dickson product | Bales | 2016 | all `n` | registered: [note](../notes/papers/1602.02317.md) |
| arXiv 1602.02843 | Periodicity of the Cayley-Dickson twists | Bales | 2016 | all `n` | registered: [note](../notes/1602.02843.md) |
| arXiv 2103.12805 | A twisted group algebra structure for an algebra obtained by the Cayley-Dickson process | Flaut, Boboescu | 2021 | all `n` | registered: [note](../notes/papers/2103.12805.md) |
| arXiv 2205.07986 | The explicit twisted group algebra structure of the Cayley-Dickson algebra | Ren, Zhao | 2023 | all `n` | registered: [note](../notes/papers/2205.07986.md) |
| Kivunge conference slides 2013 | Sign matrices for frames of `2^n`-ons | Kivunge | 2013 | 16 to 64 and higher | registered: [note](../notes/papers/kivunge-2013-sign-matrices-2n-ons.md) |
| Schafer, Amer. J. Math. 76 (1954) | On the algebras formed by the Cayley-Dickson process | Schafer | 1954 | all `2^n` | registered: [note](../notes/papers/schafer-1954-cayley-dickson-flexible.md) |
| Brown dissertation 1972 | Zero divisors in higher dimensional real Cayley-Dickson algebras | H. C. Brown | 1972 | 16 and higher | registered: [note](../notes/papers/brown-1972-dissertation.md) |

### Registered on the unmerged branch

These three sources are admitted by the branch `sources/sedenion-graph-and-structure-papers` and are not admitted again here.

| Identifier | Title | Disposition |
| --- | --- | --- |
| arXiv 2608.26890 | Zhilina, commutativity diameter of the sedenion zero-divisor graphs | branch: registered on `sources/sedenion-graph-and-structure-papers` |
| Guterman and Zhilina 2023, Comm. Algebra 51(4) | Cayley-Dickson split algebras: doubly alternative zero divisors and relation graphs | branch: registered on `sources/sedenion-graph-and-structure-papers` |
| Cawagas, Discuss. Math. Gen. Algebra Appl. 24 (2004), DOI 10.7151/dmgaa.1088 | On the structure and zero divisors of the Cayley-Dickson sedenion algebra | branch: registered on `sources/sedenion-graph-and-structure-papers` |

### Candidates not admitted

| Identifier | Title | Authors | Year | Reason |
| --- | --- | --- | --- | --- |
| arXiv 2607.23613v3 | General polynomials and eigenvalues over Cayley-Dickson algebras | Chapman, Levin, Vishkautsan | 2026 | CC BY-SA 4.0 lies outside the license allowlist of `docs/verify_sources.py`; admission needs a verifier change that the survey leaves to a separate change |
| arXiv 2306.15889v4 | Alternating roots of polynomials over Cayley-Dickson algebras | Chapman, Levin | 2023 | beyond the cap; polynomial roots, the tower facts it uses are in [2205.05605](../notes/papers/2205.05605.md) |
| arXiv 2311.16704v4 | Roots and right factors of polynomials and left eigenvalues of matrices over Cayley-Dickson algebras | Chapman, Vishkautsan | 2023 | beyond the cap; same polynomial theme |
| Hentzel and Peresi, J. Algebra (1997), DOI 10.1006/jabr.1996.6814 | Identities of Cayley-Dickson algebras | Hentzel, Peresi | 1997 | found by the Crossref lookup; identities of the algebra family, publisher copy only, no open copy retrieved |
| Bremner and Hentzel, Comm. Algebra 29(8) (2001) | Identities for algebras obtained from the Cayley-Dickson process | Bremner, Hentzel | 2001 | cited by [2205.05605](../notes/papers/2205.05605.md); no open copy retrieved |
| Khalil and Yiu (1997) | named in the literature search | Khalil, Yiu | 1997 | bibliographic record not re-verified; no open copy found |
| Carmody (1988, 1997) | named in the literature search | Carmody | 1988, 1997 | bibliographic record not re-verified; no open copy found |
| Kivunge and Smith, CMUC (2004) | named in the literature search | Kivunge, Smith | 2004 | bibliographic record not re-verified; no open copy found |
| Cawagas and Gutierrez (2005) | named in the literature search | Cawagas, Gutierrez | 2005 | bibliographic record not re-verified; no open copy found |
| Cariow and Cariowa, JTACS (2014) | named in the literature search | Cariow, Cariowa | 2014 | bibliographic record not re-verified |
| Gresnigt, Tang and Weng physics papers on sedenions | named in the literature search | Gresnigt, Tang, Weng | not recorded | physics applications of the 16-dimensional algebra; the registered review [2609.10569](../notes/papers/2609.10569.md) covers the Gresnigt line |
| Park and Kang, Zenodo deposit | named in the literature search | Park, Kang | not recorded | deposit record not re-verified |
| arXiv 2403.03763v3 | Flipped non-associative polynomial rings and the Cayley-Dickson construction | Aryapoor, Back | 2024 | beyond the cap; abstract reviewed, ring-theoretic framework |
| arXiv 1505.01670v1 | On the radius in Cayley-Dickson algebras | Goldberg, Laffey | 2015 | abstract reviewed; a metric question without sign or zero-divisor content |
| arXiv math-ph/0003031v1 | Similarity and consimilarity of elements in real Cayley-Dickson algebras | Tian | 2000 | abstract reviewed; the treatment concerns Clifford-type matrix algebras |
| arXiv 1205.5057v1 | Some graded identities of the Cayley-Dickson algebra | Henry | 2012 | abstract reviewed; octonion identities only |
| arXiv 2406.16312v1 | Rota-Baxter operators of weight zero on Cayley-Dickson algebra | Panasenko | 2024 | abstract reviewed; split octonions only |
| arXiv 2512.00600v1 | Convergence domains of sedenionic star-power series | Dou, Jin, Ren, Sabadini | 2025 | CC BY; analysis on slice-regular functions, no algebraic structure result |
| arXiv 2401.01166v1 | Sixteen-dimensional sedenion-like associative algebra | Jitender, Kumar | 2024 | an associative algebra, not a Cayley-Dickson algebra |
| arXiv hep-th/0306271v1 | Born-Infeld Lagrangian using Cayley-Dickson algebras | Kuwata | 2003 | physics application; the algebra content is in [hep-th/0601033](../notes/papers/hep-th-0601033.md) |
| arXiv hep-th/9906065v1 | Matrix representation of octonions and generalizations | Daboul, Delbourgo | 1999 | abstract reviewed; matrix representations without a dimension 16 result retrieved |
| arXiv 0807.0343v2 | Cayley-Dicksonia revisited | Merkel | 2008 | abstract reviewed; hypercomplex unit conventions without theorems |
| arXiv 2512.14007v1 | Perplex analysis and geometry of singularities | Menegon | 2025 | analysis on perplex numbers, not the CD tower |
| arXiv math/0412390v1 | C-loops: extensions and constructions | Kinyon, Phillips, Vojtechovsky | 2004 | no Cayley-Dickson-specific content verified |
| Eakin and Sathaye, J. Algebra 129 (1990), DOI 10.1016/0021-8693(90)90221-9 | On automorphisms and derivations of Cayley-Dickson algebras | Eakin, Sathaye | 1990 | Elsevier; no open copy retrieved |
| Imaeda and Imaeda, Appl. Math. Comput. (2000), DOI 10.1016/s0096-3003(99)00140-x | Sedenions: algebra and analysis | Imaeda, Imaeda | 2000 | publisher copy only; no open copy retrieved |
| Culbert, J. Gen. Lie Theory Appl. (2007), DOI 10.4303/jglta/s060101 | Cayley-Dickson algebras and loops | Culbert | 2007 | no PDF retrieved from the journal host |
| de Lourdes Merlini-Giuliani, Plaumann, Sabinina, UNIPA Springer Series (2017), DOI 10.1007/978-3-319-62181-4_6 | Half-automorphisms of Cayley-Dickson loops | Merlini-Giuliani, Plaumann, Sabinina | 2017 | Springer chapter; no open copy retrieved |
| Kivunge dissertation, Iowa State (DOI 10.31274/rtd-180813-11037) | Sedenion extension loops and frames of hypercomplex `2^n`-ons | Kivunge | 2013 | repository returned HTTP 500; the slides are registered as the Kivunge row above |
| Winters-Hilt, Adv. Stud. Theor. Phys. (2022), DOI 10.12988/astp.2022.91846 | Chiral trigintaduonion emanation leads to the standard model of particle physics | Winters-Hilt | 2022 | physics claim built on the 32-dimensional algebra; not retrieved |
| Goecen and Soykan, preprint (2019), DOI 10.20944/preprints201906.0303.v1 | Horadam `2^k`-ions | Goecen, Soykan | 2019 | number-sequence algebras, not the doubling construction |

## Convention map and mismatches found

Each admitted note states its paper's multiplication convention and the replay result under `cd_core`. The conventions group as
follows.

| Convention relative to `cd_core` | Sources |
| --- | --- |
| equal to `cd_core` | Brown 1967 (`gamma = -1`), the four Moreno papers, Chapman et al. 2205.05605, Chapman and Levin 2603.20495, Lemley 2609.11588, Bales 1707.07318 `P3T` and 1107.1301 `P31`, Kuwata et al., Aryapoor et al. 2606.27798, Kirshtein 1102.5151, de Marrais 0804.3416 and Cawagas et al. 0907.2047 (both print XOR-indexed facts rather than a formula) |
| equal to `cd_core` on the opposite loop | Chapman et al. 2501.00123 (its scheme places `j` on the right; Remark 4.1) |
| opposite algebra (factors exchanged on the basis) | Saniga et al. 1405.6888 (Bales `P3`, the transpose of `P3T`) and Gazeau 2512.22134 |
| oriented-line algebras, not a doubling | Wilmot 2505.06011 |

Mismatches the notes record, none of which the survey corrects silently:

- Kirshtein 1102.5151, Lemma 36, third claim: the lift generated by `(x,1)`, `(y,1)`, `(z,1)` is not the octonion loop; it is non-Moufang at
  dimension 16 (1 of 1 tested) and 32 (8 of 8). The claim is not used later in the paper, and Chapman et al. 2501.00123 (Remark 15.3) records the same error.
- Chapman et al. 2501.00123, abstract (formula for `n > 3`) and p. 2 (`Aut(Q_3)`): `Aut(Q_3) = GL_3(F_2)` and `Aut(Q_n) = GL_3(F_2) x {+-1}^(n-3)`. Exact
  counts give `|Aut(Q_3)| = 1344 = 8 x 168` and `|Aut(Q_4)| = 2688`, short by the `(Z_2)^3` sign changes; Corollary 15.7 is consistent with the counts.
- Bales 1107.1301, Table 7 is titled the octonion table of all eight quaternion-property products, but four of the eight have zero divisors at dimension 8
  (`(e2 + e5)(e3 + e4) = 0`); 1707.07318 states this.
- Wilmot 2505.06011: the claim that the 15-dimensional `Phi` with `e48C` negated is isomorphic to the sedenions fails a monomial isomorphism test over
  all 20,160 index maps of `GL(4,2)`, and the printed series of non-associative triple counts at dimensions 32 to 256 differs from the counts of `cd_core`.
- Brown 1967: the formula of the order-3 automorphism `psi` is unreadable in the retained text layer; the note reconstructs it and verifies the reconstruction.

## Bearing on Moreno's Stiefel question and on dimensions 64 and above

[I] Moreno's question (math/0512517, Section 5) asks whether every element of the Stiefel set of pure, orthogonal, equal-norm pairs
`(a, b)` in `A_n`, viewed in `A_(n+1)`, is a zero divisor. The repository answers it at `A_5` affirmatively (`a5-stiefel-universal`) and at
`A_6` negatively (`a6-stiefel-witness`). Of the admitted sources, only math/0404172 touches the Stiefel set: it places the
zero-divisor pairs `X_n` (equal halves with `ab = 0`) inside the Stiefel set `V_(2^n - 1, 2)` and gives that inclusion only. math/0512516
realizes doubly pure pairs with `ad = 0` as octonion subalgebras and treats no Stiefel set. No admitted source settles the question or
compares the dimension of `X_n` with that of the zero-divisor set.

[I] Sources that reach dimension 64 or beyond with checkable content: Lemley 2609.11588 (algorithm and multiplication-count bound
replayed to dimension 256), de Marrais 0804.3416 (box-kite trip counts to dimension 256), Brown 1967 (the order-3 map `psi` as an
automorphism at dimensions 32 and 64), Chapman and Levin 2603.20495 (associativity degree to dimension 64), Bales 1707.07318 (tables to
64) and Saniga et al. 1405.6888 (finite geometry to 64). Moreno's theorems in math/0404172 and math/0512516 hold for every `n >= 4`
and `n >= 3`, and apply to the 64-ions and beyond without counts or nullities. Each note states which of its general-`n`
statements were replayed and which were read only.

## Merge note for the registry counts

The count lines of [INDEX.md](../INDEX.md) and [README.md](README.md) change in this survey (3 published and 17 external additions) and in the unmerged
branch `sources/sedenion-graph-and-structure-papers` (new external entries), so the two branches edit the same lines. The
merge keeps the sum of both additions.

## Later admissions

Three sources at dimension 16 and above entered the registry after the candidate table above and are absent from its counts, and
a fourth entry records a newer version of a registered source. Each note states its reading scope and the checks it ran against
`cd_core`.

| Source | Dimension | Disposition |
| --- | --- | --- |
| Skiouris, Algebraic hiddenness in the sedenion algebra (Zenodo 10.5281/zenodo.22016333, CC BY 4.0) | 16 | registered and hosted: [note](../notes/papers/skiouris-2026-algebraic-hiddenness.md) |
| Skiouris, Aphanics at the pathion level (Zenodo 10.5281/zenodo.22082732, CC BY 4.0) | 32 | registered and hosted: [note](../notes/papers/skiouris-2026-aphanics-pathion.md) |
| Levratti, Sign-parity classification of zero divisors in Cayley-Dickson algebras (Zenodo 10.5281/zenodo.20315751, CC BY 4.0) | 16 and higher | registered and hosted: [note](../notes/papers/levratti-2026-sign-parity-zero-divisors.md); a later Zenodo version (record 21296777) is not retained |
| Wilmot, arXiv 2505.11747v4 (CC BY-NC-SA 4.0) | 16 and higher | version 4 registered external beside version 3: [note](../notes/papers/2505.11747.md) |
