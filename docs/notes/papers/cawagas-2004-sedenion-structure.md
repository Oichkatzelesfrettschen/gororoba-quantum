# Cawagas: structure and zero divisors of the Cayley-Dickson sedenion algebra

## Source copy and license

The source PDF remains external to the published library. Its optional
personal reading copy is `docs/local_source_cache/cawagas-2004-dmgaa-1088.pdf`,
fetched from the
[Wayback Machine snapshot of the journal PDF route](https://web.archive.org/web/20240718205948id_/https://www.dmgaa.uz.zgora.pl/publish/pdf.php?doi=1088)
(2024-07-18) because the journal host `dmgaa.uz.zgora.pl` refused or timed
out every connection on 2026-10-25.
Original PDF SHA-256:
`4bddb6c90e401928e0705a7102bb48afd98b45acc08b65a9d1fa24efc29d5991`
(408865 bytes, 15 pages).

The [archived article page](https://web.archive.org/web/20250726081148id_/https://www.dmgaa.uz.zgora.pl/publish/article.php?doi=1088)
(2025-07-26, retained decompressed as
[dmgaa-1088-article.html](../../evidence/source_rights/dmgaa-1088-article.html))
carries a site navigation item "Open Access License" linking CC BY 4.0. That
link is journal-wide; it names neither this 2004 article nor its PDF, and the
PDF carries no license or copyright notice of its own. The registry's
`source_rights_policy` requires a source-specific grant covering the exact
retained version, so the entry records `NOASSERTION` and `external_only`.
[SOURCES.json](../../SOURCES.json) binds the PDF bytes, the evidence hash and
the reading scope.

[P] identifies a source statement. [I] identifies a repository deduction or
proposed use. [C] identifies a statement recomputed against
`gororoba_quantum/cd_core.py` by
[check.py](../../evidence/cawagas-2004-checks/check.py), whose output is
[check.txt](../../evidence/cawagas-2004-checks/check.txt).

## Citation and provenance

- Author: Raoul E. Cawagas, SciTech R and D Center, OVPRD, Polytechnic
  University of the Philippines, Manila.
- Title: On the structure and zero divisors of the Cayley-Dickson sedenion
  algebra.
- Journal: Discussiones Mathematicae - General Algebra and Applications
  24(2), 251-265 (2004), DOI
  [10.7151/dmgaa.1088](https://doi.org/10.7151/dmgaa.1088). Received 19 May
  2004, revised 25 July 2004 and 30 December 2004. MSC 2000: 20N05, 17A45.
- Crossref record: https://api.crossref.org/works/10.7151/dmgaa.1088,
  receipt registered for the
  [Casimir and dark-sector web sources](casimir-dark-sector-web-sources.md)
  (SHA-256
  `1371435eb38b42f4bd276219a73237945f0b1e6574af236bcbcf7381711ac9a1`).
- Reading scope: the full text, pp251-265, every section, table,
  proposition, remark and footnote; the page image of Table 2 (p258) was
  inspected to separate a printed misprint from a text-extraction artifact.
  Table 1 (p254) and Tables 4(A), 4(B) (pp259-260) are images without
  extractable entries; the 35 triplets of p254 determine Table 1, and
  check.py rebuilds it from them.
- Sibling source: the dimension-32 sequel by Cawagas et al.
  ([0907.2047](0907.2047.md)) applies the same FINITAS loop analysis to the
  32-dimensional algebra.

## Section 2: the sedenions (pp252-255)

- [P] p253: the canonical basis is `E16 = {e_0, ..., e_15}`, `e_0` the unit,
  `e_1..e_15` imaginaries; indices 0-7 span the octonions and 8-15 the "pure
  sedenion" elements. Multiplication is bilinear with structure constants
  `gamma^k_ij` (Table 1).
- [P] p254: the rule is 35 associative triplets, seven octonion triplets
  `(1,2,3), (1,4,5), (1,7,6), (2,4,6), (2,5,7), (3,4,7), (3,6,5)` and 28
  sedenion triplets, four for each `i = 1..7`:
  `(1,8,9), (1,11,10), (1,13,12), (1,14,15)`, `(2,8,10), (2,9,11),
  (2,14,12), (2,15,13)`, `(3,8,11), (3,10,9), (3,15,12), (3,13,14)`,
  `(4,8,12), (4,9,13), (4,10,14), (4,11,15)`, `(5,8,13), (5,12,9),
  (5,10,15), (5,14,11)`, `(6,8,14), (6,15,9), (6,12,10), (6,11,13)`,
  `(7,8,15), (7,9,14), (7,13,10), (7,12,11)`.
- [P] p255: for a triplet `(a,b,c)`, `ab = c`, `ba = -c`, the same for cyclic
  shifts, and `(ab)c = a(bc)`: triplet elements associate and anticommute.
- [C] Every triplet obeys `a XOR b = c`; with `e_i^2 = -1` the 35 triplets
  fix all 256 basis products, and all 256 signs equal `cd_core.cd_sign(16,
  a, b)` with no basis change. The paper's convention is the repository's
  convention. Sixteen diagonal sign maps `e_i -> s_i e_i` preserve the table.
- [P] Remark 1, p255: Conway-Smith sedenions and J.D.H. Smith's sedenions are
  16-dimensional semi-algebras with multiplicative norms, distinct from the
  Cayley-Dickson sedenions.

## Section 3: subalgebras (pp255-261)

- [P] p255: `SL = {+-e_i}`, order 32, is a non-commutative loop under
  sedenion multiplication (the Cayley-Dickson sedenion loop); its subloops
  determine the basis-generated subalgebras. The analysis uses the program
  FINITAS, reference [2]; the text cites it as [9], a numbering slip.
- [P] p256, result I: `SL` is a non-associative finite invertible loop
  (NAFIL) with PAP, IP, WIP, AAIP, SAIP, AP, FL, RIF, CL and NSLP (LN, MN,
  RN), hence diassociative; every element other than `+-e_0` has order 4;
  the center is `{+-e_0}` and holds every square.
- [P] p256, result II: `SL` has exactly 67 subloops, 66 non-trivial and
  normal: 15 of order 16 (8 octonion loops `O_L`, 7 quasi-octonion loops
  `~O_L`, the maximal subloops), 35 of order 8 (quaternion groups), 15 of
  order 4 (cyclic `C4`), one of order 2 (the center) and the trivial one;
  1 + 15 + 35 + 15 + 1 = 67.
- [C] The subloops containing `+-e_0` correspond to linear subspaces of
  `F_2^4` under XOR: 15 of dimension 3, 35 of dimension 2, 15 of dimension 1,
  matching the counts.
- [P] Proposition 1, p257: every non-trivial subloop of `SL` is isomorphic to
  one of `O_L`, `~O_L`, `Q`, `C4`, `C2`.
- [P] p257: the class of `~O_L` is the seven subloops numbered 4, 7, 10, 18,
  21, 29, 32 in Table 3. In each octonion and quasi-octonion copy, three of
  the seven imaginaries form an octonion triplet and four are pure sedenion
  elements (the `O_L` copy on indices 0-7 excepted).
- [P] Table 2, p258: IP, FL, AP, CL, LC, RC, PAP, WIP, AAIP, RIF, NSLP, LN,
  MN, RN hold in `SL`, `O_L` and `~O_L`; MP holds in `O_L` only. The defining
  identity printed for MP is `(xy)(zx) = (x(yx))z`.
- [C] The printed MP identity is a misprint: it fails on all 15 order-16
  subloops, including the octonion loop on indices 0-7, which is Moufang. The
  standard Moufang identity `(xy)(zx) = (x(yz))x` splits the 15 subloops into
  8 Moufang and 7 non-Moufang, under the paper's rule and under `cd_core`.
- [P] Table 3, p259: octonion-loop copies are FINITAS subloops 2, 3, 6, 9, 17,
  20, 28, 31 (positive index sets `{0..7}`, `{0,1,2,3,8,9,10,11}`,
  `{0,1,4,5,8,9,12,13}`, `{0,1,6,7,8,9,14,15}`, `{0,2,4,6,8,10,12,14}`,
  `{0,2,5,7,8,10,13,15}`, `{0,3,4,7,8,11,12,15}`, `{0,3,5,6,8,11,13,14}`);
  quasi-octonion copies are subloops 4, 7, 10, 18, 21, 29, 32
  (`{0,1,2,3,12,13,14,15}`, `{0,1,4,5,10,11,14,15}`,
  `{0,1,6,7,10,11,12,13}`, `{0,2,4,6,9,11,13,15}`,
  `{0,2,5,7,9,11,12,14}`, `{0,3,4,7,9,10,13,14}`,
  `{0,3,5,6,9,10,12,15}`).
- [C] The Moufang subloops computed from `cd_core` equal Table 3's octonion
  column and the non-Moufang ones equal its quasi-octonion column. The
  octonion copies are the octonions and the seven 3-dimensional subspaces
  of `F_2^4` containing index 8; the quasi-octonion copies are the remaining
  seven, which contain neither.
- [P] Remark 2, p260: the quasi-octonion loop was not previously identified;
  it and its copies give natural models of the Bol-Moufang (Fenyves)
  identities CL, RC, LC, LN, MN, RN.
- [P] pp260-261: the positive elements of the `~O_L` copies span an
  8-dimensional quasi-octonion algebra `~O`; `S` contains subalgebras
  isomorphic to `O`, `~O`, `H`, `C`. Whether these are all subalgebras of `S`
  up to isomorphism is stated open. `~O` is non-commutative, non-associative,
  non-alternative, power-associative, has a quadratic form and zero divisors,
  and has every known octonion property except the Moufang identity.

## Section 4: zero divisors (pp261-264)

- [P] p261, footnote: Moreno's example pair `x = e_1 + e_10`,
  `y = e_15 - e_4`, `xy = 0`.
- [C] `(e_1 + e_10)(e_15 - e_4) = 0` in `cd_core` with the indices as
  printed.
- [P] p262: de Marrais's 84 zero-divisor pairs (Table 5, from
  [math/0011260](https://arxiv.org/abs/math/0011260)) come in seven "GoTo"
  lists, one per octonion triplet, each with an "automorpheme" of seven
  imaginaries. Footnote † calls them the pairs "in Table 3", a slip for
  Table 5.
- [P] Proposition 2, p262: the known zero divisors of `S` all lie in copies of
  `~O`. Argument: the `O_L`, `Q`, `C4`, `C2` copies span division algebras;
  `~O` has zero divisors; each automorpheme is the positive imaginary set of
  a `~O_L` copy, and each Table 5 pair's four indices lie in its list's
  automorpheme.
- [C] All 84 Table 5 pairs multiply to zero under the paper's rule and in
  `cd_core` with the indices as printed, and each pair's four indices lie in
  one quasi-octonion copy.
- [P] p264: worked product `(e_2 - e_14)(e_3 + e_15) = e_1 + e_13 - e_13 -
  e_1 = 0`.
- [C] The worked product is zero in the paper's rule and in `cd_core`.
- [C] Proposition 2 holds for the listed pairs and says nothing about all
  zero divisors: among the 13440 four-term elements with `+-1` coefficients (every sign pattern)
  whose index support spans `F_2^4`, 1344 are zero divisors in `cd_core`
  (first: `e_1 + e_2 + e_11 + e_12`, nullity 4). A spanning support lies in
  no order-16 subloop, so these zero divisors lie in no quasi-octonion copy.
  [I] The unit zero divisors of the sedenions form an 11-dimensional set
  (Moreno, `V_2(R^7)`), which the seven 7-dimensional unit spheres of the
  8-dimensional copies cannot cover.

## Repository bearing

[I] The convention match makes this paper's triplet list a third
independent statement of the `cd_core` sedenion table, beside
[Wilmot](2512.07210.md)'s graded table and the 35-term calibration.

[I] The quasi-octonion term reaches the repository's census through
[Wilmot](2505.11747.md) Table 5, which the
[Casimir note](casimir-dark-sector-web-sources.md) records; this note binds it
to its source and to the computed Moufang split.

[I] Zero divisors of dimension 32 or higher: none; the paper concerns the
sedenions. Moreno's Stiefel question (`math/0512517` Section 5): none.
