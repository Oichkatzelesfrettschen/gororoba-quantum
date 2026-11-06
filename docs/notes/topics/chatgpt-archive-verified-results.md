# ChatGPT brainstorm archive: verified results, refuted claims and the reference audit

The owner's ChatGPT export (8,504 conversations, export manifest dated 2026-10-27 UTC) holds raw brainstorms on
moonshine, exceptional algebra, L-infinity algebras, spectral triples and Cayley-Dickson algebras. Four conversations
densest in those topics were checked claim by claim against held primary sources and by computation; every reference
identifier in the whole export was resolved. This note keeps what survived, what failed and why, and the reliability
of the archive's citations. The sibling [persona-corpus report](persona-corpus-verified-results.md) holds the checked
results of an earlier LLM-persona corpus; where the two overlap (L-infinity conventions, Sugawara, Kac determinants)
that note is the home and this one points to it.

Tags: [E] computed (q-series from Eisenstein series, E8 root systems, Cayley-Dickson products through
`gororoba_quantum/cd_core.py`, whose basis and sign convention fix every Cayley-Dickson count and defect below; every
[E] value comes from [scripts/chatgpt_archive_checks.py](../../../scripts/chatgpt_archive_checks.py), which raises when
one fails, and [its test](../../../tests/scripts/test_chatgpt_archive_checks.py) runs in the `tests` check); [T] proved here in a line; [P] a published result, cited by paper and
page; [R] settled by an existing repository note. Each section lists the conversation's checkable claims that
survive and those that fail, and names the claims with no checkable content.

## Reference audit of the whole export

| Identifier | Found | Resolves | Fails |
|---|---|---|---|
| arXiv id | 1,862 distinct | 1,851 exist on arXiv | 11 nonexistent ids |
| DOI | 1,874 distinct | 1,237 through Crossref, 340 more through doi.org (DataCite DOIs, URL suffixes removed) | 219 dead, 20 placeholders (10.12345/..., zenodo.1234567), 58 cut by the extractor at a parenthesis |

An identifier that resolves is not yet a correct citation. In the "Sedenion Research Articles" conversation all 12
arXiv ids exist, yet six carry a wrong title or a false description of the paper's content, and two cited works are
fabricated by attaching a new title and venue to a real paper or a reused DOI. The six: 0804.3416 (a fabricated
subtitle), math/0703745 (a wrong title), 2307.02505 ("and Quarks" added; the paper treats leptons only), 2208.03285
(described as hypercomplex neural networks; it reviews end-to-end deep learning in high-energy physics), 2410.14267
(described as Monster-related; it names the Monster only in a list of examples) and hep-th/9912113 (the same, in one
background sentence). The two fabrications: an "Oberwolfach 2023" title over arXiv 1003.0429, and a "Modular Forms in
Twisted Algebras" title carrying the DOI of a 2018 Burdik-Catto paper. A citation from the archive counts
only after the resolved title and the cited content are checked against the paper itself.

## Monstrous Moonshine and Pulsars (2025-02-18)

Survives:
- The j-function coefficients 744, 196884, 21493760, 864299970 from j = E4^3 / Delta, and McKay's decompositions
  196884 = 1 + 196883 and 21493760 = 1 + 196883 + 21296876, matching Conway and Norton, Monstrous Moonshine, Table 1
  (p. 324) and p. 309. [E][P] They serve as a known-good q-series test vector and carry no research content here.

Fails:
- The j-coefficients are not irreducible degrees of the Monster; McKay-Thompson series begin at q^-1 and their
  coefficients are character values.
- The Monster Lie algebra is graded by the even unimodular Lorentzian lattice II_{1,1}, not by the Leech lattice, and
  the bracket the conversation gives is the Virasoro relation. [P] Borcherds' 1992 paper is "Monstrous moonshine and
  monstrous Lie superalgebras"; the conversation misnames it and invents a co-author.
- The Rademacher sum is ill-formed and the stated asymptotic drops the 4 pi in the exponent.
- Lin, "Topological modularity of Monstrous Moonshine" (arXiv 2207.14076), treats moonshine and topological modular
  forms and contains no black-hole or neutron-star content; the cited Ng paper contains no modular forms; a 2008
  "Smallest Black Hole" paper and its venue resolve nowhere.
- The "sedenionic j-function" has no definition, its "Monster alignment" consists of coefficients entered by hand, and
  pulsar, gravitational-wave and spin-foam moonshine define no observable.

## E7 E8 Algebra Amplification (2025-02-19)

Survives:
- e8(-24) contains e7(-25) + sl(2, R) as a subalgebra and decomposes under it as (133, 1) + (1, 3) + (56, 2),
  248 = 133 + 3 + 112, from Dray, Manogue and Wilson (arXiv 2401.10534, abstract and pp. 1-3). [P] Recomputed: the E8 roots split 126 / 2 / 112 by inner product 0 / plus or minus 2 /
  plus or minus 1 with a fixed root, and 126 + 7 = 133, 2 + 1 = 3. [E]
- E4 / eta^8 = j^(1/3) exactly, as the cube root with leading term q^(-1/3): Delta = eta^24 and j = E4^3 / Delta give
  it, and the coefficients 1, 248, 4124, ... cube to 1, 744, 196884, .... [E]
- The quantum trigonometric Calogero-Sutherland ground-state and excitation formulas: the general formula, eq. (15)
  of Fernandez Nunez, Garcia Fuertes and Perelomov's E7 paper (arXiv math-ph/0507015), evaluated on E8 data,
  reproduces the conversation's E8 coefficient list; their E8 paper is arXiv 0806.1011. [P][E]
- McKay's question relating E8, E7, E6 to the Monster, the Baby Monster and the Fischer group Fi24 is a real open
  problem, listed as problem (10) in Borcherds' "Problems in moonshine" (zbMATH 1077.11503), which names Fi24 and
  Fi24.2. [P]

Fails:
- The magic-square rows are shifted: e6 sits at C (x) O, e7 at H (x) O, e8 at O (x) O, and Dray-Manogue-Wilson build e8
  over O' (x) O. H3(O) is the Albert algebra, whose derivation algebra is f4, not e6.
- E7 has 126 roots, not 133; j(i) = 1728, not 1; the E8 level-1 character is j^(1/3), not j - 744.
- The stated E7 Calogero-Sutherland Hamiltonian, ground state and spectrum, the Freudenthal product and the cubic norm
  of the triple system are wrong, and the theorems and numerical outputs the conversation generated fail where
  checked (j(i) = 1 against 1728 [E]). Its L-functions, entropies and machine-learning outputs carry no checkable definition.

## L-infinity Algebras and Spectral Triples (2026-07-07 and 2026-07-10)

Survives: the L-infinity conventions once corrected (skew-symmetric l_n of degree 2 - n, Lada and Stasheff, arXiv
hep-th/9209099), Kontsevich formality for every Poisson manifold, the Connes distance formula, the Sugawara central
charge and the Kac determinants. These are recorded in the
[persona-corpus report](persona-corpus-verified-results.md) [R]; two values that report does not list are the
level-2 singular-vector coefficients a = -3/(2(2h + 1)) of (L_-2 + a L_-1^2)|h>, -3/4 at h = 1/2 and -4/3 at
h = 1/16 for c = 1/2, and the Ising embedding levels. [E]

Fails: the Sugawara contraction f^{abc} f^{acd} = +2h delta^{bd} for real antisymmetric structure constants, whose
contraction is negative (-2 delta^{bd} for su(2) with f = epsilon, -4 delta^{bd} = -2h delta^{bd} with long roots of
squared length 2), the value +2h holding only in the i-convention, as the persona-corpus report records; Poincare duality presented as a hypothesis of Connes'
reconstruction theorem (arXiv 0810.2088, Theorem 1.1 does not assume it); global formality called open; the
finite-eigenspace hypothesis of the conformal-net and vertex-algebra correspondence placed on the net rather than on
its representations (the conversation attributes it to Henriques and Tener without a theorem; the attribution is
unverified here).

Survives but nearly empty: the later conversation's chain from a spectral triple through its differential forms to a
strict L-infinity algebra, since every differential graded algebra gives one.

## Sedenion Research Articles (2024-12-08)

Survives: the real papers, nine of them already held and six carrying notes under [papers](../papers/) (Reggiani
2411.18881, de Marrais math/0207003, 0704.0112, math/0703745, 0804.3416, Morier-Genoud and Ovsienko 1003.0429).

Fails: the doubling formula the conversation states breaks octonion norm multiplicativity (x = e1 + e4,
y = e2 + e7 give N(xy) = 8 against N(x)N(y) = 4), its "Prather" variant fails at dimension 4 (x = e0 + e2,
y = e1 + e3 give N(xy) = 0 against 4), and N(xy) = N(x)N(y) across the hierarchy fails at the sedenion zero divisor
(e3 + e10)(e6 - e15) = 0 [E]; "fractal doping" adds to x the multiples phi^-k x, k >= 1, which sum to phi x, so the doped
element is (1 + phi) x = phi^2 x, a scalar rescaling. The de Marrais names agree through dimension 256; "reston" and "dudon" appear in no held source.

## Results that bear on the repository

- The commutator of a Cayley-Dickson algebra of dimension at least 8 carries no L-infinity structure with l_1 = 0,
  since l_1 = 0 forces the strict Jacobi identity, which fails. On imaginary basis triples the Jacobiator vanishes
  exactly on the XOR lines {e_i, e_j, e_(i xor j)}, in every dimension: on a line each bracket term is a multiple of
  [e_k, e_k] = 0, and off a line each of the three cyclic terms is plus or minus 4 e_m with the same
  m = i xor j xor k, so their sum is an odd multiple of 4 e_m. Counts: 7 of 35 triples at dimension 8, 35 of 455 at
  16, 155 of 4,495 at 32. [E][T] These are the lines of PG(n - 1, 2), the known associative-triple structure in
  [the open_gororoba survey](../open_gororoba_survey.md) and the notes on [1405.6888](../papers/1405.6888.md) and
  [2505.06011](../papers/2505.06011.md); the Jacobiator characterization adds the link to Wilmot's Malcev lemma in
  [2505.11747](../papers/2505.11747.md). The statement is elementary and claims no novelty.
- No Cayley-Dickson algebra of dimension at least 8 is a finite tolerance algebra. D'Andrea, Landi and Lizzi state
  this themselves (arXiv 2112.09698, p. 7, the paragraph after Proposition 7, which shows a tolerance algebra
  associative exactly when power-associative); it is their result, not a repository one, and it bears on the
  intrinsic non-associativity recorded in [the math/9802116 note](../math-9802116.md). [P]
- A question with low prior: whether the G2 found on the Iso core of the A_5 nullity-8 kernel bundle
  ([verification](../../evidence/a5-kernel-bundles-nullity8/verification.md)) is the octonion derivation algebra that
  Dray-Manogue-Wilson's e8(-24) contains as g2 + g2(2). Falsifier: that stabilizer is not conjugate to Der(O) under
  the `cd_core` convention.

Every paper cited above as read has a reading copy in the owner's documents repositories.
