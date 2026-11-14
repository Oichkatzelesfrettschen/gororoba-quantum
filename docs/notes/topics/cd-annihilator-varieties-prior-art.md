# Prior art on annihilator varieties and zero-divisor strata of Cayley-Dickson algebras

Question: has any published work identified a variety of annihilators, or of limits of annihilators, of the 16- or 32-dimensional Cayley-Dickson algebra with a homogeneous, quasi-homogeneous, spherical or named projective variety, or computed a fiber cone, Rees algebra or blow-up of a stratum of zero divisors? The question bounds what the A_5 fiber-cone program ([ledger](../../evidence/a5-exceptional-fibers/ledger.tsv), [findings](a5-exceptional-fiber-findings.md)) may call new.

Evidence status. Search of 2026-11-13 through the arXiv API, the zbMATH Open API, the OpenAlex REST API and web search; the query log below records every query. Every work carries an identifier that a tool returned, and titles and authors are copied from that tool's record. Checked a second time: the ten arXiv records math/0511691, math/0702075, 2411.18881, 2512.13002, math/0512517, 2608.08232, math/0610493, 1707.06764, 2608.08442 and 1103.4623 resolve to the titles and authors given, and the quoted phrases of math/0511691 (p. 2, with Theorems 1.2 and 1.3) and math/0512517 (p. 2) were read on the page images of the held copies. The remaining statements about what a work proves rest on one reading of its abstract, review or first pages, as each row says. The answer is a bounded negative: it holds for the queries logged here.

## Answer

No work found under the queries below identifies a variety of annihilators of a 16- or 32-dimensional Cayley-Dickson algebra, or of limits of annihilators, with a homogeneous, quasi-homogeneous, spherical or otherwise named projective variety. No work found computes a fiber cone, special fiber, Rees algebra or blow-up of a zero-divisor stratum. The published identifications are topological or Riemannian, and none of them is algebro-geometric:

- In dimension 16, the normalized zero divisors form a manifold homeomorphic or isometric to the Stiefel manifold V_2(R^7), and the normalized zero-divisor pairs form a manifold isometric to G_2.
- In dimension 32, only the top nullity stratum, ZD_16(A_5), is identified: it is homeomorphic to two disjoint copies of V_2(R^7).

The deeper strata of A_5 are stated to be open by their own authors. The nullity strata are k = 4, 8, 12, 16 (written ZD_k), and Biss, Dugger and Isaksen say these strata are "unknown even in the case of A_5" (math/0511691, p. 2). The identification of the degree-20 fivefold in P^14 with symmetry sp_4 acting on an abelian ideal also found no match. The nearest frameworks are background only:

- Z_2-contractions g_0 ⋉ g_1 of symmetric pairs (Panyushev).
- Euler-symmetric (quasi-homogeneous) projective varieties and their infinitesimal symmetries (Fu-Hwang, Hwang-Li).
- A degeneration of the G_2 adjoint variety (Kapustka).

## Hits by class

"Registered" means the identifier already appears under `docs/notes`, `docs/evidence` or `docs/SOURCES.json` (search: `grep -rlF ID docs/notes docs/SOURCES.json docs/evidence`). "New" means it does not appear there.

### Class (a): annihilator or zero-divisor locus identified with a homogeneous space or named variety

Each identification in this class is a homeomorphism or isometry of a real zero-divisor locus: a set of elements, or a set of normalized pairs. None identifies the image of the annihilator map in a Grassmannian, its closure, or its limits as a complex projective variety.

| Identifier | Title | Authors | Year | Dimension | What it proves | Status |
|---|---|---|---|---|---|---|
| arXiv:math/0511691; DOI 10.1080/00927870701724094; Zbl 1137.17007 | Large annihilators in Cayley-Dickson algebras | Daniel K. Biss, Daniel Dugger, Daniel C. Isaksen | 2005 (arXiv); 2008 (Commun. Algebra 36) | 2^n for n ≥ 4, so 16 and 32 | Theorem 1.2: dim Ann x ≤ 2^n − 4n + 4, and every multiple of 4 in that range occurs. Theorem 1.3: ZD_{2^n−4n+4}(A_n) is homeomorphic to 2^{n−4} disjoint copies of V_2(R^7). For n = 4, ZD_4(A_4) = V_2(R^7). For n = 5, ZD_16(A_5) is two copies, the only dimension-32 stratum identified in the literature found here. Pages 1-3 were read. | Registered |
| arXiv:2411.18881 | The geometry of sedenion zero divisors | Silvio Reggiani | 2024 | 16 | The set of normalized pairs with product zero, Z(S) ⊂ S × S, is isometric to G_2 with a naturally reductive left-invariant metric. It is a Riemannian submersion over the symmetric space G_2/SO(4) of quaternion subalgebras of O. The set of normalized elements with nonzero annihilator, ZD(S), is isometric to V_2(R^7) with a G_2-invariant metric. Abstract read. | Registered |
| arXiv:2512.13002 | Determinant Factorization for Left Multiplication in the Sedenions | Shoot Koebisu | 2025 (v2 2026) | 16 | det L_a factors as a norm power times the square of a quartic polynomial. After normalization, the left-zero-divisor locus is identified with V_2(R^7). On a 3-dimensional purely imaginary slice, the locus is a quadratic cone. Abstract read. | Registered |
| arXiv:math/0512517 | Constructing zero divisors in the higher dimensional Cayley-Dickson algebras | Guillermo Moreno | 2005 | 16; relation only for 2^{n+1} with n > 3 | The introduction (p. 2) states two facts for A_4, citing the author's earlier papers [M1], [M2] and Khalil-Yiu [K-Y]: zero divisors of fixed norm are identified with V_{7,2}, and the singular set of pairs (x, y) with xy = 0 and \|x\| = \|y\| = 1 is homeomorphic to G_2, via the fibration G_2 → V_{7,2} with fiber S^3. For n ≥ 5 it states that "there is NO analogous description". Section 5 relates zero divisors in A_{n+1} to V_{2^n−1,2}, but notes they "are not equal" and that the singular set has an "(unknown) complicated description". Pages 1-3 were read. | Registered |

Attribution for Moreno 1997 (arXiv:q-alg/9710013; Zbl 1006.17005; *The zero divisors of the Cayley-Dickson algebras over the real numbers*; R. Guillermo Moreno; Bol. Soc. Mat. Mex. 4, 1998):

- Pages 1-4 were read. In them, Theorem I.15 gives the decomposition by which dim Ker L_a ≡ 0 mod 4 and dim Ker L_a ≤ 2^n − 4. Chapter II constructs "special" zero divisors and states that in A_4 these are all of them.
- The paper defers the topological description, "relate this with suitable Stiefel manifolds", to a second paper (p. 3-4).
- The G_2 and V_{7,2} statements above are therefore attributed to math/0512517, which cites [M1], [M2] and [K-Y] for them. They are not credited here to the 1997 paper.
- The 1997 paper is registered (`docs/notes/papers/q-alg-9710013.md`). Its class is (c), pending a read of the Chapter II theorem statements.

### Class (b): strata or limits in dimension 32 or higher

| Identifier | Title | Authors | Year | What it proves | Status |
|---|---|---|---|---|---|
| arXiv:math/0511691 (also class a) | Large annihilators in Cayley-Dickson algebras | Biss, Dugger, Isaksen | 2005/2008 | Defines the strata ZD_k(A_n) = {x : \|\|x\|\| = 1, dim Ann x = k} (p. 2). It solves only the top stratum (Theorem 1.3). It states that "these strata are also complicated, and unknown even in the case of A_5", and that describing ZD_k for smaller k is "an intriguing open problem". | Registered |
| arXiv:math/0702075; Zbl 1228.17006 | Large annihilators in Cayley-Dickson algebras II | Daniel K. Biss, J. Daniel Christensen, Daniel Dugger, Daniel C. Isaksen | 2007 (Bol. Soc. Mat. Mex. 13) | Theorems 1.3 and 1.5 cover elements {a, b} of A_{n+1}, with a, b in the orthogonal complement of C_n: dim Ann{a, b} equals dim Ann a + dim Ann b, plus 4 exactly on the "D-locus" (Definition 1.4). Section 7, Theorem 7.5, makes this explicit for A_5 on a codimension-4 subspace. Theorem 1.7 is a stability statement: for n ≥ c/4 + 4, the near-maximal locus T^c_{n+1} is two copies of T^c_n. The text after Theorem 1.7 (p. 4) leaves open the explicit geometry of a connected component of T^c_n. No limits, closures or projective varieties appear. Pages 1-4 were read. | Registered |

No work found under the queries below studies limits of annihilators, closures of strata in a Grassmannian, or a blow-up or fiber cone of a stratum, in any dimension.

### Class (c): background

Cayley-Dickson works:

| Identifier | Title | Authors | Year | Relevance | Status |
|---|---|---|---|---|---|
| arXiv:2608.08232 | Determinant Factorization of Left Multiplication in the 32 Dimensional Cayley Dickson Algebra | Shoot Koebisu | 2026 | Dimension 32, but the whole zero-divisor locus and no strata: det L_x = N(x)^2 D_14(x)^2, x is a left zero divisor iff D_14(x) = 0, and N does not divide D_14 after complexification (abstract, pp. 1-3). D_14 cuts out the nullity ≥ 4 locus as a degree-14 hypersurface. It does not separate the nullity 4, 8, 12, 16 strata. | Registered |
| arXiv:0905.2987; DOI 10.1515/FORUM.2009.041 | Eigentheory of Cayley-Dickson algebras | Biss, Christensen, Dugger, Isaksen | 2009 | Eigenspaces of L_{x*}L_x have dimension divisible by 4, and 1 is always an eigenvalue. These are the spectral inputs to the nullity stratification. Not titled as part III of the series. | Registered |
| arXiv:math/0404172; Zbl 1139.17301 | Hopf construction map in higher dimensions | Guillermo Moreno | 2004 | The zbMATH review gives the inclusions X_n ⊂ W_{2^{n−1}−1,2} ⊂ V_{2^n−2,2} ⊂ V_{2^n−1,2} for the normalized zero-divisor pairs of A_n, n ≥ 4. This is containment only, not an identification. | Registered |
| arXiv:2608.26893; DOI 10.1007/s10958-023-06444-8 | On doubly alternative zero divisors in Cayley-Dickson algebras | Svetlana Zhilina | 2026 (arXiv), 2023 (J. Math. Sci.) | Gives explicit annihilators of doubly alternative zero divisors over a general field and considers possible annihilator dimensions. Combinatorial and linear, with no varieties. | Registered |
| arXiv:math/0207003 | Flying Higher Than a Box-Kite: Kite-Chain Middens, Sand Mandalas, and Zero-Divisor Patterns in the 2n-ions Beyond the Sedenions | Robert P. C. de Marrais | 2002 | Combinatorial patterns of basis-diagonal zero divisors in the 32-dimensional algebra. No nullity strata. | Registered |
| Zbl 1480.17009; DOI 10.1007/s10958-020-04930-x | Relation graphs of the split-sedenion algebra | S. A. Zhilina | 2020 | Classifies split-sedenion zero divisors by annihilator and orthogonalizer dimension (zbMATH review). Concerns the split algebra and graph invariants, not varieties. | Not checked |
| arXiv:2505.11747 | Structure of the Cayley-Dickson algebras | G. P. Wilmot | 2025 | Counts and organizes zero divisors (84 in the sedenions) through a graded construction. Combinatorial. | Registered |

Works relevant to identifying the degree-20 fivefold in P^14, independent of Cayley-Dickson algebras:

| Identifier | Title | Authors | Year | Why it is background rather than a hit | Status |
|---|---|---|---|---|---|
| arXiv:math/0610493; Zbl 1177.17010; DOI 10.1016/j.aim.2006.12.011 | On the coadjoint representation of Z_2-contractions of reductive Lie algebras | Dmitri I. Panyushev | 2007 (Adv. Math. 213) | Studies the Lie algebra g_0 ⋉ g_1 obtained by contracting a symmetric decomposition g = g_0 ⊕ g_1. The pair (sl_4, sp_4) gives sp_4 ⋉ C^5, the symmetry algebra that issue 863 of this repository reports for the component. The paper treats coadjoint invariants and contains no projective variety of degree 20. | New |
| Zbl 1317.17022; arXiv:1104.5472; DOI 10.1007/s00031-013-9224-y | Commuting involutions and degenerations of isotropy representations | Dmitri I. Panyushev | 2013 (Transform. Groups 18) | Degenerations attached to Z_2-gradings, at the representation-theory level. | New |
| Zbl 1405.17020; DOI 10.1093/imrn/rnv381 | Symmetric invariants of Z_2-contractions and other semi-direct products | Oksana Yakimova | 2017 (IMRN) | Invariants of Z_2-contractions. No projective geometry. | New |
| arXiv:1707.06764 | Euler-symmetric projective varieties | Baohua Fu, Jun-Muk Hwang | 2017 | Euler-symmetric varieties are quasi-homogeneous, are classified by symbol systems, and are related to equivariant compactifications of G_a^n. A 5-dimensional variety whose symmetry algebra contains an abelian 5-dimensional ideal acting with an open orbit would fall in this framework. The paper does not list the component. | New |
| arXiv:2608.08442 | Fundamental forms and infinitesimal symmetries of projective varieties | Jun-Muk Hwang, Qifeng Li | 2026 | Bounds the dimension of the linear automorphism group of a projective variety by its fundamental forms, with equality exactly for Euler-symmetric varieties. Determines their infinitesimal automorphism algebra. Proves rigidity for specializations that preserve the fundamental forms. This gives a test for whether the component is Euler-symmetric. | New |
| arXiv:1103.4623 | Some degenerations of G_2 and Calabi-Yau varieties | Michal Kapustka | 2011 | Constructs a degeneration of the G_2 adjoint variety from a degenerate four-form. That variety is a fivefold in P^13, not P^14, and has a different group. | New |
| arXiv:math/0608471 | The adjoint variety of SL_{m+1}(C) is rigid to order three | Colleen Robles | 2006 | Third-order extrinsic rigidity of the SL_{m+1} adjoint variety. Relevant to how far a degeneration can depart from it to that order. | New |
| arXiv:0707.3410 | Fubini-Griffiths-Harris rigidity and Lie algebra cohomology | J. M. Landsberg, C. Robles | 2007 | Shows that adjoint varieties are extrinsically rigid to third order. | New |
| Zbl 1261.17003; arXiv:1010.2156; DOI 10.1016/j.jalgebra.2010.11.003 | On locally complex algebras and low-dimensional Cayley-Dickson algebras | Matej Brešar, Peter Šemrl, Špela Špenko | 2011 (J. Algebra 327) | Characterizes the sedenions among locally complex super-alternative algebras. No zero-divisor geometry. | New |

## Unresolved recollections

- **Khalil-Yiu.** A Khalil-Yiu paper on Cayley-Dickson algebras and Hurwitz's theorem is cited as [K-Y] in math/0512517 for the A_4 G_2 statement. zbMATH `au:Khalil au:Yiu Cayley-Dickson` returned 0, and no other tool was queried for it. Label: unresolved recollection.
- **"Large annihilators in Cayley-Dickson algebras III".** Earlier repository text names a part III. No record carrying that title was found on arXiv, zbMATH or OpenAlex. The third paper of the series that tools resolve is *Eigentheory of Cayley-Dickson algebras* (0905.2987), which is not titled part III. Label: unresolved.
- **Classification of smooth horospherical varieties of Picard number one.** This is a candidate frame for quasi-homogeneous Sp_4-varieties with a non-reductive automorphism group. The arXiv query for it failed with HTTP 429, and the work is not resolved. Label: unresolved recollection.

## Query log

"Opened" lists the records whose abstract or review was read. "PDF" marks the works whose PDF pages were read.

| # | Tool | Query | Results | Opened |
|---|---|---|---|---|
| A1 | arXiv search | `abs:sedenion AND abs:"zero divisors"` | 12 | all 12: 2505.11747, math/0011260, 2608.26903, 2512.13002, 2608.26890, 2512.00600, math/0207003, 2411.18881, 2608.08232, math/0403113, math/0603281, 2610.28921 |
| A2 | arXiv search | `abs:"Cayley-Dickson" AND abs:annihilator` | 3 | 2608.26893, math/0511691, 2411.18881 |
| A3 | arXiv search | `abs:"Cayley-Dickson" AND abs:"zero divisors"` | 16 | all 16, including math/0702075, 2608.28176, 2608.28163, 2606.27798, math/0512516, math/0703745, 0704.0112, 0704.0026 |
| A4 | arXiv search | `abs:"large annihilators" OR ti:"large annihilators"` | 67 (25 returned) | math/0511691, math/0702075; the rest are physics and Lie-module uses of the phrase |
| A5 | arXiv search | `(abs:sedenion OR abs:"Cayley-Dickson") AND (abs:Stiefel OR abs:Grassmannian OR abs:"flag variety" OR abs:"homogeneous space")` | 4 | 2411.18881, 1409.5691, 1405.6888, 2512.13002 |
| A6 | arXiv search | `(abs:"zero divisors" OR abs:"zero-divisors") AND (abs:sedenions OR abs:"Cayley-Dickson algebras") AND abs:G_2` | 3 | 2512.13002, 2411.18881, 2610.28921 |
| A7 | arXiv search | `ti:"Cayley-Dickson" AND (au:Isaksen OR au:Dugger OR au:Biss)` | 3 | math/0511691, math/0702075, 0905.2987 |
| A8 | arXiv search | `(abs:pathion OR abs:pathions OR abs:trigintaduonion OR abs:trigintaduonions OR abs:"32-dimensional Cayley-Dickson")` | 6 | 2407.18265, 0704.0136, math/0207003, 0907.2047, 2608.08232, math/0603281 |
| A9 | arXiv search | `(abs:sedenion OR abs:sedenions OR abs:"Cayley-Dickson") AND (abs:variety OR abs:varieties OR abs:"orbit closure" OR abs:degeneration OR abs:"singular locus" OR abs:stratification)` | 3 | 2501.00123, 1704.02240, 2410.17634 (none on zero-divisor geometry) |
| A10 | arXiv search | `abs:"annihilator variety" AND (abs:nonassociative OR abs:"non-associative" OR abs:algebra)` | 4 | 2304.03475, 2509.24346, 2606.11790, 2001.11746 (Lie-module annihilator varieties, unrelated) |
| A11 | arXiv search | `abs:"zero divisor variety" OR abs:"variety of zero divisors" OR abs:"zero-divisor variety"` | 0 | none |
| A12 | arXiv search | `(abs:"fiber cone" OR abs:"special fiber" OR abs:"Rees algebra" OR abs:"blow-up" OR abs:blowup) AND (abs:sedenion OR abs:octonion OR abs:"Cayley-Dickson" OR abs:"zero divisors of")` | 6 | 2409.05146, 2508.05809, math/9809116, math/0601734, 2611.07992, 2412.13285 (none relevant) |
| A13 | arXiv search | `abs:"adjoint variety" AND (abs:degeneration OR abs:contraction OR abs:"quasi-homogeneous" OR abs:horospherical)` | 1 | 1103.4623 |
| A14 | arXiv search | `(abs:"Inonu-Wigner" OR abs:"Inönü-Wigner" OR abs:contraction) AND abs:sl_4 AND abs:sp_4` | 0 | none (probable tokenization failure; A24 and Z12 rerun the family) |
| A15 | arXiv search | `(abs:"nilpotent orbit" OR abs:"orbit closure") AND abs:"Rees algebra" AND (abs:"fiber cone" OR abs:"special fiber")` | 0 | none |
| A16 | arXiv search | `(abs:"adjoint varieties" OR abs:"adjoint variety") AND (abs:degenerations OR abs:deformation OR abs:rigidity OR abs:"Euler-symmetric")` | 3 | math/0608471, 0707.3410, 1103.4623 |
| A17 | arXiv search | `(abs:"quasi-homogeneous" OR abs:horospherical OR abs:"equivariant compactification") AND (abs:"Sp_4" OR abs:"Sp(4)" OR abs:"sp_4" OR abs:"Sp_{4}") AND abs:fivefold` | 0 | none |
| A18 | arXiv search | `abs:"hyperplane section" AND (abs:"P^3 x P^3" OR abs:"P^3\\times P^3" OR abs:"Segre") AND abs:"flag variety" AND abs:degenerat*` | 0 | none |
| A19 | arXiv search | `abs:"Euler-symmetric" OR (abs:"equivariant compactifications of vector groups" AND abs:"Picard number one")` | 6 | 1707.06764, 2111.09231, 2608.08442, 2203.16068, 2403.10812, 2606.14236 |
| A20 | arXiv search | `abs:"Inonu-Wigner contraction" AND (abs:"projective variety" OR abs:"orbit closure" OR abs:"nilpotent orbit" OR abs:"adjoint")` | 2 | 2504.17036, alg-geom/9508006 |
| A21 | arXiv search | `(abs:"zero divisors" OR abs:"zero-divisors") AND (abs:nonassociative OR abs:"non-associative") AND (abs:variety OR abs:"algebraic set" OR abs:locus)` | 0 | none |
| A22 | arXiv search | `(abs:"fiber cone" OR abs:"special fiber ring") AND (abs:Pfaffian OR abs:Pfaffians OR abs:"orbit closure")` | 0 | none |
| A23 | arXiv search | `(abs:sedenion OR abs:"Cayley-Dickson") AND (abs:"adjoint variety" OR abs:limit OR abs:limits)` | 1 | 1505.03089 (random matrices, unrelated) |
| A24 | arXiv search | `(abs:"Z_2-contraction" OR abs:"Z_2-contractions" OR abs:"symmetric pair") AND abs:contraction AND (abs:"sl_4" OR abs:"sl(4)" OR abs:"SL_4" OR abs:"so_5" OR abs:"sp_4")` | 0 | none |
| A25 | arXiv search | `abs:horospherical AND abs:"Picard number one" AND (abs:smooth OR abs:"odd symplectic")` | failed (HTTP 429) | not run |
| G1 | arXiv get | `q-alg/9710013, math/0512517, math/0404172, 0905.2987` | 4 | all 4 |
| G2 | arXiv get | `math/0610493, 1010.2156` | failed (HTTP 429) | resolved instead through Z12 and Z10 |
| P1 | arXiv PDF | q-alg/9710013 | 1 | PDF pp. 1-4 |
| P2 | arXiv PDF | math/0511691 | 1 | PDF pp. 1-3 |
| P3 | arXiv PDF | math/0702075 | 1 | PDF pp. 1-4 |
| P4 | arXiv PDF | 2608.08232 | 1 | PDF pp. 1-3 |
| P5 | arXiv PDF | math/0512517 | 1 | PDF pp. 1-3 |
| Z1 | zbMATH search | `ti:sedenion* zero divisor*` | 4 | Zbl 1102.17001 (Cawagas 2004); arXiv mirrors of math/0403113, math/0207003, 2411.18881 |
| Z2 | zbMATH search | `Cayley-Dickson annihilator*` | 7 | Zbl 1137.17007, Zbl 1228.17006, Zbl 1508.05105, Zbl 1480.17009, Zbl 0824.00029; arXiv mirrors of 2608.26893, 2411.18881 |
| Z3 | zbMATH search | `ci:1006.17005` (citers of Moreno 1998) | 2 | Zbl 1137.17007, Zbl 1139.17301 |
| Z4 | zbMATH search | `ci:1137.17007` (citers of BDI I) | 1 | Zbl 1228.17006 |
| Z5 | zbMATH search | `ci:1228.17006` (citers of BDI II) | 0 | none |
| Z6 | zbMATH search | `(trigintaduonion* \| pathion* \| "32-dimensional Cayley-Dickson")` | 6 | Zbl 1496.11043; Weng 2025 (DOI 10.1002/mma.10345); arXiv mirrors of 2608.08232, 0907.2047, math/0603281, math/0207003 |
| Z7 | zbMATH search | `zero divisor* Cayley-Dickson (variety \| Stiefel \| homogeneous \| Grassmann*)` | 4 | arXiv mirrors of 2608.08232, math/0512517, 2411.18881; Zbl 1071.17024 (unrelated) |
| Z8 | zbMATH search | `ti:"fiber cone" (Pfaffian* \| "orbit closure*" \| nilpotent)` | 0 | none |
| Z9 | zbMATH search | `au:Khalil au:Yiu Cayley-Dickson` | 0 | none |
| Z10 | zbMATH search | `sedenion* (G_2 \| G2 \| Stiefel \| homogeneous)` | 9 | Zbl 1261.17003, Zbl 1331.51004, Wilmot 2026 (DOI 10.1007/s00006-025-01423-5); arXiv mirrors of 2512.13002, 2610.28921, 2411.18881, 2512.07210, 2608.08232, 1202.0941 |
| Z11 | zbMATH search | `("annihilator variety" \| "zero divisor variety" \| "variety of zero divisors") nonassociative` | 0 | none |
| Z12 | zbMATH search | `Z_2-contraction* reductive Lie algebra*` | 3 | Zbl 1317.17022, Zbl 1177.17010, Zbl 1405.17020 |
| O1 | OpenAlex REST | `works/doi:10.1080/00927870701724094` | 1 | W2964257931 (BDI I, 33 citers) |
| O2 | OpenAlex REST | `works?search=Large annihilators in Cayley-Dickson algebras` | 154 (25 returned) | titles only; BDI II, Eigentheory, Moreno 2005 IDs taken |
| O3 | OpenAlex REST | `works?search=zero divisors of the Cayley-Dickson algebras over the real numbers` | 383 (25 returned) | titles only; Moreno 1997 W1504695943 (67 citers) |
| O4 | OpenAlex REST | `works?filter=cites:W2964257931` (citers of BDI I) | 33 | all titles read; candidates checked: 0905.2987, 2608.08232, Zhilina series, 1010.2156 |
| O5 | OpenAlex REST | `works?filter=cites:W1504695943` (citers of Moreno 1997) | 67 | the first run stopped at a null title after 48 rows; a rerun printed rows 49-67; all titles read |
| O6 | OpenAlex REST | `works?filter=cites:W2008773379` (citers of BDI II) | 4 | all titles read |
| O7 | OpenAlex REST | `works?filter=cites:W2058229666` (citers of Eigentheory) | 5 | all titles read |
| O8 | OpenAlex REST | `works?filter=cites:W1666677827` (citers of Moreno 2005) | 11 | all titles read |
| O9 | OpenAlex REST | `works?search=annihilators Cayley-Dickson algebras III` | 10 returned | no part III |
| O10 | OpenAlex REST | `works?filter=cites:W4405029806` (citers of 2411.18881) | 0 | none |
| O11 | OpenAlex REST | `works?filter=cites:W4417453536` (citers of 2512.13002) | 1 | 2608.08232 |
| W1 | web search | `sedenion zero divisors variety orbit closure stratification annihilator dimension 32 Cayley-Dickson algebraic geometry` | 10 links | link list only; every cited work was re-resolved through arXiv or zbMATH |
| W2 | web search | `"Cayley-Dickson" zero divisors "limits" annihilators blow-up OR "fiber cone" OR "Rees algebra"` | 10 links | link list only; no Cayley-Dickson blow-up or fiber-cone work |
| W3 | web search | `degeneration of the adjoint variety of SL_4 sp_4 contraction quasi-homogeneous fivefold degree 20 P^14` | 10 links | math/0608471 (re-resolved by A16), math/0610493 (re-resolved by Z12) |
| W4 | web search | `pathion OR trigintaduonion zero divisors annihilator dimension 4 8 12 16 strata geometry` | 10 links | link list only |

Coverage notes:

- **Citers come from OpenAlex.** zbMATH `ci:` returns only the citations it has parsed: 2 citers of Moreno 1998, against 67 citers of the arXiv record of Moreno 1997 on OpenAlex. The citing-works sweep therefore rests on OpenAlex.
- **zbMATH arXiv mirrors are counted once.** zbMATH rows tagged `database: arXiv` mirror the arXiv record. They are counted once and are not treated as independent confirmation.
- **Web-search summaries are excluded.** The prose summaries attached to the web-search results contained errors, including a retitled 2512.13002, a wrong dimension for the SL_4 adjoint variety, and an unresolved arXiv number. No statement here rests on them.

## Sources not reached

- **MathSciNet:** requires a subscription; not queried.
- **Google Scholar citation counts:** not queried. OpenAlex supplied citation data.
- **Full text of the published (journal) versions:** not read. The arXiv versions were read instead.
- **arXiv API:** rate-limited (HTTP 429) for query A25 and get call G2. G2 was recovered through zbMATH; A25 was not.
- **Moreno 1997, Chapter II:** the theorem statements were not read. Its class stays provisional, as noted under class (a).
- **Biss, Christensen, Dugger, Isaksen 2007, Section 7:** read only through the statements on pp. 1-4. Theorem 7.5 itself was not read.
