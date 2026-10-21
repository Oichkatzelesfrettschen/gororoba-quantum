# Cayley-Dickson zero-divisor and box-kite claims in the Monographs corpus

Scope: circuit-testable structural claims about Cayley-Dickson (CD) zero divisors,
assessors, box-kites, Theorem 7, XOR indexing and the ladder to 128D, extracted from
the PDFs of the owner's local Monographs collection plus two side files
beside it. Compiled 2026-10-17 by read-only reading of those PDFs; the PDFs stay
outside the repository and the claims below are second-hand unless a row cites
the census.

## 0. Method, conventions, and an important caveat about the sources

The monographs are AI-generated syntheses ("DAS MERGUS" series). They quote de Marrais
(Placeholder Substructures I-III, Presto, Flying Higher, Bricolage, Voyage by
Catamaran), Moreno (q-alg/9710013), Reggiani (arXiv 2411.18881) and Biss-Dugger-Isaksen
second-hand. None of them proves anything itself; "proved" below means "stated as a
theorem of a cited primary paper". The primary papers are on disk
(the owner's local CayleyDickson collection, its cd_tower_structure/
and zero_divisors_geometry/ subdirectories) but were outside the stated scope and were not read.

Independent recomputation. To separate what sources assert from what holds, every
16D claim, and the 32D and 64D census claims, were recomputed in the repository
convention: doubling (a,b)(c,d) = (ac - conj(d) b, da + b conj(c)), basis index =
bit-string, e_p e_q = gamma(p,q) e_{p^q} with gamma = cd_core.cd_sign. "RC" in the
status column means "recomputed". Two authorities carry the recomputations:

- The retained census, [scripts/box_kite_census.py](../../../../scripts/box_kite_census.py)
  with its record [docs/evidence/box_kite_census/census.json](../../../evidence/box_kite_census/census.json)
  (gates core-372 and core-373), built on cd_core alone. Every 16D box-kite fact the
  experiment program uses comes from it; the table "Recomputation authority" below
  names the census field for each row.
- An exploratory scratch recomputation that is not retained. It reimplemented the
  doubling; its 256 sedenion sign and index entries matched the cd_core-identical
  package tables in docs/evidence/algebra_packages/tables.json (0 mismatches), and it
  reproduced (e1+e10)(e2-e13) = e3 + e7 + e8 - e12, (e1+e10)(e4-e15) = 0 and 1848 of
  3375 non-associating imaginary triples. Its 32D and 64D results, the random
  normal-form nullity samples (A11) and the Rule 1 / Rule 2 checks (A10) are not in
  the census and remain second-hand for the program until a retained script
  recomputes them.

RC results hold for this one sign convention; sign-flipped tables can change
lanyard patterns (M2 Thesis G).

### Recomputation authority

| row | census field (census.json) | not retained (scratch only) |
|---|---|---|
| A1 | `two_blades`, `assessors`, `nonkite_planes`, `kites[].assessors` | -- |
| A2 | `kites[].assessors` (U = L ^ (8 ^ S) required), `design_b.all_cross_and_nonkite_ordered_signed_pairs` | -- |
| A3 | `kites[].index_set` | -- |
| A4 | `kites[].struts`, `kites[].edges`, `design_b.within_kite` | -- |
| A5 | `theorem3_zero_sign_choices_over_49_planes` | -- |
| A6, A7 | `kites[].edges[].type`, `kites[].faces`, `edge_totals` | -- |
| A8 | `associator.xor_zero_triples_all_associate`, `associator.kite_triple_classes` (`face-sail-xor0` 0 of 96) | -- |
| A9 | `kites[].struts` (lows xor to S required) | -- |
| A10 | -- | Rule 1, Rule 2, CPO trips |
| A11 | `annihilators` (two-blade diagonals only) | random (a, b) normal-form nullity samples |
| A12 | `annihilators[].nullity_left`, `nullity_right` (dimension 4) | -- |
| A13 | `twist` | -- |
| A14 | `eta_parity` | -- |
| A15 | `kites[].faces` (2 all-opposite faces per kite, 14 of 56) | -- |
| A16 | `frustration_minimum` (16D) | 32D-1024D values |
| A17 | `associator.non_associating_basis_triples` (1848 at 16D), `octonion_non_associating_basis_triples` (168 at 8D) | 15960 of 29791 at 32D |
| B1-B3, B8 | -- | every 32D and 64D count |

Source keys (PDF page numbers, 1-based, as rendered by pdftotext):
- M1  DAS MERGUS: A Unifying Technical Monograph for XOR-Indexed Cayley-Dickson Zero-Divisors, Box-Kite Skies, ... (18 pp)
- M2  Theorem 7 and the Bitwise Geometry of Box-Kite Zero Divisors (10 pp)
- M3  Reverse engineering the "Sedenion Zero-Divisor Field" ... falsifiable theses (8 pp)
- M4  DAS MERGUS: A Reconstructed Monograph from Split and Negative to 128D CD Algebras ... (15 pp)
- M5  Publication-Grade Synthesis of the CD Zero-Divisor Program in open_gororoba (17 pp)
- M6  Cayley-Dickson Ladder Taxonomy and Nomenclature from 32D to 8192D (11 pp)
- M7  DAS MERGUS: A Derivation-First Synthesis of Bit-String Zero-Divisor Geometry ... (10 pp)
- M8  DAS MERGUS: A Unified Algebra-Lattice-Graph-Dynamics Treatise ...
- M9  Das Mergus: A Full-Corpus Technical Monograph on Algebra-Valued Fractional PDEs ...
- M10 Das Mergus: A Publication-Grade Synthesis of the Chat Corpus and the Open-Gororoba Codebase
- M11 Gororoba Monograph: A Spectral-Topological-Hypercomplex Physics Stack in Rust
- M12 A Unified Algebra-Lattice-Graph-Inference Monograph Reconstructing the Full Chat Corpus
- M13 E10 Billiards, Octonion Locality, and Zero-Divisor Skies
- SOL CAYLEYDICKSON_SOLAR_ANALYSIS.md, a local side file (no structural claims; see section 4)

Observable conventions used in the last two columns. Basis state |k> is e_k with index bit
b on qubit b (little-endian, qubit 0 least significant). "LCU P0" is the fixed-operand
LCU success probability P(s=0) = ||x y||^2 / 2 for normalized x = (e_i + t e_j)/sqrt2 and
normalized y, as in docs/notes/algebra_circuit_rules.md. N(xy) denotes the squared norm of the product xy (a pipe-free spelling for table safety). For x, y both normalized two-blades N(xy) takes only
the values 0, 1, 2 (RC over all 210 x 210 pairs: counts 336, 43428, 336), so P0 is 0,
1/2 or 1. "Hadamard W" is the associator-sign Hadamard-test witness, whose
expectation is +1 for an associating basis triple and -1 for a non-associating one.
"Diagonal" d+ = e_L + e_U and d- = e_L - e_U (the papers write these with a slash and a backslash; the slash is d+).

## 1. Claim table

Status key: PROVED-SRC = stated as a theorem of a cited primary paper; COMP-SRC = source
reports its own computation; CONJ = conjecture or empirical law in the source;
ASSERT = bare assertion; RC-OK / RC-FAIL = recomputed here, holds / fails.

### 1a. Sedenion (16D) box-kite structure

| id | source | page | claim | math content | status | falsifying observable | predicted value |
|---|---|---|---|---|---|---|---|
| A1 | M1, M2, M11, M9 | M1 p5, p15 (C-ZD-1); M2 p3, p9; M11 p7, p10 | Primitive sedenion zero divisors form 7 box-kites partitioning 42 assessors (84 diagonal line elements). | Assessor = plane span(e_L, e_U), L in 1..7, U in 9..15 (L < G=8 < U). 49 such planes; 42 lie in box-kites, 7 (U = L^8) do not. 6 assessors per kite, one kite per S in 1..7. | PROVED-SRC (de Marrais); RC-OK: 42 assessors, 7 components of 12 diagonal nodes, every assessor in exactly 1 kite | Enumerate all 210 x 210 signed two-blade pairs by LCU P0; count assessor planes with any P0 = 0 partner | Exactly 84 diagonals (42 planes) have a P0 = 0 partner among two-blades; 168 undirected (x,y) pairs with P0 = 0; planes (l, l^8) never |
| A2 | M2 | p3 (Thm 7.1), p8 (Thesis A) | U-index law: with X = G^S = 8^S, every assessor in kite S has U = L ^ X. | L in {1..7} minus {S}; U = L xor (8 xor S). S=7: (1,14),(4,11),(5,10),(2,13),(3,12),(6,9). | PROVED-SRC; RC-OK for S=1..7 (all six assessors per kite) | LCU P0 for x=(e_L+s e_U), y=(e_L'+s' e_U') over all (L,L',s,s'): zero only when L^U = L'^U' | P0 = 0 requires L^U = L'^U' = 8^S; every cross-kite pair has P0 = 1/2 (RC: all 43260 cross-kite and non-assessor ordered pairs have N(xy) = 1) |
| A3 | M2, M1 | M2 p3, p9; M1 p5 | Strut constant S is the octonion index absent from the six low indices of the kite ("signature"). | S in 1..7; lows = {1..7} minus {S}. | PROVED-SRC; RC-OK | Same as A2 | Six lows per kite omit exactly S |
| A4 | M2, M11 | M2 p3, p5; M11 p7 | Three struts per kite; strut-opposite assessors never make zero; the other 12 vertex pairs (edges) each do. | Struts (S=7): (1,14)-(6,9), (2,13)-(5,10), (3,12)-(4,11); low indices of a strut pair xor to S. Octahedral graph K2,2,2: 6 vertices, 12 edges, degree 4. | PROVED-SRC (DMZ); RC-OK: S=7 struts match M2 exactly; all 7 kites have 3 struts and 12 edges | LCU P0 on all 4 diagonal combos of a strut pair | Strut pair: P0 = 1/2 for all four combos (RC: N(xy) = 1 each). Edge pair: P0 = 0 for 2 combos and P0 = 1 for the other 2 (RC: N(xy) = 2, norm doubling) |
| A5 | M2 | p8 (Thesis B), p3 (Thm 3) | For every non-strut pair of assessors exactly two of four diagonal products vanish, and they are either the same-sign pair or the opposite-sign pair, never mixed. | (P,Q) edge: zero set is {(+,+),(-,-)} (same) or {(+,-),(-,+)} (opp). Theorem 3: (a+A)(b+B)=0 implies (a+A)(b-B) != 0. | PROVED-SRC (Thm 3); RC-OK: across all 861 assessor pairs, #zero in {0,2} only (0: 777; 2: 84 -- 42 same, 42 opp) | As A4 | Four-combo P0 vector is (0,0,1,1) in some order; never one or three zeros |
| A6 | M2 | p3-4 (Thm 7.2-7.4), p5, p8 (Thms C, D) | Edge-sign law: the 3 edges of the zigzag sail are opposite-sign DMZ; in each trefoil sail the two edges incident to the vertex shared with the zigzag are same-sign and the third is opposite-sign. | S=7 zigzag = {(1,14),(4,11),(5,10)}: (1,14)-(4,11), (1,14)-(5,10), (4,11)-(5,10) opposite. Zero set of an opp edge: d+ d- = 0 and d- d+ = 0. | PROVED-SRC (Thm 7, via PSL(2,7) argument); RC-OK for convention (ac - d*b, da + bc*): the 8 faces of every kite split 1 zigzag (3 opp, lows xor to 0), 3 trefoils (lows xor to 0; 1 opp, 2 same), 1 vent (3 opp, lows not a trip), 3 other (1 opp, 2 same) | see predicted | Zigzag edge: P0(d+,d-) = P0(d-,d+) = 0 and P0(d+,d+) = P0(d-,d-) = 1. Trefoil incident edge: P0(d+,d+) = P0(d-,d-) = 0 and P0(d+,d-) = 1 |
| A7 | M2 | p5 (audit), p8 (Thesis E) | Exactly 6 of the 12 edges per kite are opposite-sign and 6 same-sign; the opposite face (vent) also has three opposite edges. | Lanyard coloring: red = opposite = zigzag (3) + vent (3); blue = 6 cross edges. | COMP-SRC; RC-OK in all 7 kites (6/6) | Sum LCU P0 pattern over the 12 edges | 6 edges with P0(d+,d-)=0, 6 with P0(d+,d+)=0 per kite; S=7 vent = {(2,13),(3,12),(6,9)} |
| A8 | M2 | p4 (Corollary), p8 (Thesis F) | Each sail has four associative triplets (one L-trip, three U-trips) and so "forms a quaternion copy with the real unit". | S=7 zigzag: trips (1,4,5), (1,11,10), (14,4,10), (14,11,5), each xor = 0. | PROVED-SRC (corollary); RC partly: each of 28 sails has 4 trips and each trip {0,a,b,a^b} is an associative quaternion subalgebra, but the 6 indices of a sail are not closed under xor (e.g. 1^14 = 15), so the phrase "a quaternion copy" is an ambiguous paraphrase: it holds per trip, not for the union | Hadamard W on every triple from {0,a,b,a^b}. Weak discriminator: all 35 xor-zero triples of the sedenions associate (RC), so this predicts W = +1 everywhere | W = +1 (associating) on every triple within one trip; e_1 e_14 = +-e_15 lies outside the sail index set |
| A9 | M1, M8 | M1 p5; M8 p7 | Strut-opposite XOR identities (Presto "strut logic", Vizier lemma): for opposite assessors (v,V),(z,Z): V^Z = v^z = S, Z^v = V^z = G, Z^z = v^V = X = G^S; {0,S,G,G^S} is a Klein four-group. | Pure xor identities; M1 writes them as products "VZ = vz = S, Zv = Vz = G, Zz = vV = X" (index values). | PROVED-SRC (M8 gives proof); RC-OK (follows from A2) | Not an algebra observable; check on index registers: xor of two bit-registers | S=7 strut (1,14)-(6,9): v^z = 1^6 = 7 = S, V^Z = 14^9 = 7, Z^v = 9^1 = 8 = G, V^z = 14^6 = 8, Z^z = 9^6 = 15 = v^V = G^S |
| A10 | M1, M2, M7 | M1 p3; M2 p1-2; M7 (Rules cited) | Rule 1 (e_L e_G = +e_{G+L}, L<G), Rule 2 ((a,b,c) -> (a, c^G, b^G)), CPO. | In the repository convention all 7 octonion CPO trips hold, Rule 1 holds at G=8 and G=16, Rule 2 sends the 7 octonion trips to 7 sedenion CPO trips. | PROVED-SRC (convention); RC-OK (sign table of cd_core-compatible gamma) | Hadamard-test relative-phase of e_L e_8 vs e_{L+8}; sign of controlled left-multiplication block | e_L e_8 = +e_{L+8}; products around each CPO trip all +1 |
| A11 | M3, M9, M4 | M3 p3 (Lemma, Prop 2.1), p6 (Thesis Z1); M9 p3; M4 p4 | Normal form: x=(a,b) in O x O is a zero divisor iff a, b are imaginary octonions of equal norm and orthogonal. | a,b in Im O (7-dim), norm(a)=norm(b), <a,b>=0. e_L + e_U is (e_L, e_{U-8}) with U-8 in 1..7, which is why planes (l, l^8) (b real) carry no zero divisor. | PROVED-SRC (Moreno; Reggiani Prop 2.1); RC-OK: nullity of L_x is 4 for 200 random such x; violate any one condition (not orthogonal / unequal norm / real part in a) and nullity is 0 for 100 samples each | LCU P0 with x = (a,b)/norm over random orthonormal imaginary pairs, y = a basis of the annihilator | P0 = 0 exactly on the 4-dim annihilator; elsewhere P0 > 0. Annihilator of e_1+e_10 contains the diagonals e_4-e_15, e_5+e_14, e_6-e_13, e_7+e_12 (RC) |
| A12 | M3, M4 | M3 p3-4, p6 (Thesis Z2); M4 p4 | Normalized zero divisors ZD(S) ~ Stiefel manifold V2(R7), dimension 11; the manifold of normalized annihilating pairs Z(S) ~ G2 (dimension 14) with transitive G2 action and SU(2) isotropy. | 14 = 11 + dim S^3; annihilator is a 4-dim real subspace (RC: nullity 4). | PROVED-SRC (Reggiani); dimension consistent with RC nullity 4 | Not a short-circuit observable; annihilator dimension via rank of the 16x16 left-multiplication matrix of x, i.e. 4 LCU kernel dimensions | Kernel dimension 4 for every zero divisor, 0 otherwise |
| A13 | M7 | p3 (Catamaran slide, Thesis C p9) | Twist: (B+b)(D+d) = 0 iff (B+d)(D-b) = 0 (vertex language to edge language). | b,d low; B,D high; sign pattern as written. | ASSERT (slide material; "groupoid" closure claim is conjectural) | LCU P0 on both factorizations of the same zero product | RC-OK: 28224 sign/index quadruples (b!=d, B!=D) tested, 0 mismatches, 1344 of them zero products. Predicted: P0(x1,y1)=0 iff P0(x2,y2)=0 |
| A14 | M5, M10 | M5 p4-5 (eta, fiber F, quarter rule), p9 (claim matrix); M10 p3, p10 | Anti-diagonal parity: the edge type of assessors a=(la,ha), b=(lb,hb) is eta = psi(la,hb) xor psi(ha,lb), psi(i,j)=0 iff e_i e_j = +e_{i^j}. Diagonal formula psi(la,lb) xor psi(ha,hb) is claimed wrong. | eta = 0 / 1 labels "Same" / "Opposite" (mapping not fixed in M5). | COMP-SRC (Rust exhaustive enumeration, not retained); RC: at 16D eta = 1 - [opposite] on all 84 edges and the diagonal formula gives the SAME value on all 84, so 16D cannot discriminate the two formulas; under this gamma eta=1 marks same-sign DMZ | Edge sign from LCU P0 on d+ x d+ (P0=0 means same) compared with eta from the sign table | Same-sign edge: eta=1, P0(d+,d+)=0. Opposite edge: eta=0, P0(d+,d-)=0 |
| A15 | M5, M10 | M5 p5 (Quarter Rule, Double 3:1), M10 p9 | Triangles of the signed assessor graph: exactly 1/4 are "pure" (all three eta equal); 3:1 ratios between mixed patterns. | At 16D: 56 triangles = 8 faces x 7 kites; 14 have 3 opposite edges (eta all 0), 42 have 1 opposite and 2 same; no all-same triangle. | CONJ in M5 (F uniform over F_2^2 stated, mechanism "unexplained"); RC-OK at 16D: 14/56 = 1/4, 42 = 3 x 14 | LCU P0 pattern on each face's three edges | 14 faces with pattern (0,0,0) in eta, 42 with eta sum 2 |
| A16 | M5, M10 | M5 p10 (sequence), M10 p5 | Frustration ratio of the Cayley-Dickson signed graph is 0.000 at 16D (balanced) and approaches 3/8 for large dimension (values 0.307, 0.377, 0.388, 0.385, 0.381, 0.378 at 32..1024). | Balance iff every cycle has positive sign product. | COMP-SRC for table; limit 3/8 is CONJ ("not proved", M10 says needs 2048). RC-OK at 16D: with sign -1 on same-sign (eta=1) edges every kite is balanced (frustration 0 of 12); with sign -1 on opposite edges frustration is 4 of 12 | Cycle sign product of LCU edge types around each 4-cycle or triangle | Every cycle in a kite has an even number of same-sign edges (eta-parity 0) |
| A17 | M4 | p3, p9 | Associator-defect density mu_n = Pr[phi(p,q,r) = -1] over nonzero p,q,r: d=8: 0.4898 (168/343), d=16: 0.5476 (1848/3375), d=32: 0.5357; d=64: 0.5234, d=128: 0.5102 (sampled). Claimed limit 1/2. | phi = gamma(p,q) gamma(p^q,r) / (gamma(q,r) gamma(p,q^r)); XOR associative so only a sign 3-cocycle obstructs associativity. | COMP-SRC; RC-OK: 168/343, 1848/3375, 15960/29791 = 0.53573 exact; 64D and 128D not recomputed. The 168 at d=8 is the 28 non-line index triples times 6 orderings (octonion non-associativity) | Hadamard W averaged over uniform imaginary triples | <W> = 1 - 2 mu: 16D: 1 - 2(1848/3375) = -0.0951; with zero index included (repository convention over 4096 triples) 25/256 |

### 1b. 32D and higher (pathions, chingons, routons)

| id | source | page | claim | math content | status | falsifying observable | predicted value |
|---|---|---|---|---|---|---|---|
| B1 | M1 | p6-7, p15 (C-ET-1, C-ET-2) | At 32D non-midden zero divisors fall in 15 emanation tables (14 x 14, 14 assessors each), 168 fillable cells each; 7 of them (inner xor > 24) are sparse with 72 of 168 cells filled and fold 1-1 onto the 7 sedenion box-kites. | Slugs X = i^j in 17..31 give the 15 tables. | ASSERT (de Marrais Flying Higher abstract); RC-OK for counts: slugs 17..24 have 14 assessors, 84 DMZ assessor pairs = 168 ordered cells, 12-regular; slugs 25..31 have 14 assessors, 36 pairs = 72 ordered cells, mixed degree 4 and 12. Fold-down map not checked | LCU P0 on 5-qubit (32D) register over all signed two-blades with i^j = X | Per slug 17..24: every one of the 14 assessors has 12 DMZ neighbors; slugs 25..31: degrees 4 or 12, 72 cells total |
| B2 | M4 | p5, p10 (Thesis 2) | Signed two-blade census: 32D #B=930, 2520 edges, 22 components; 64D 3906 / 26040 / 53; 128D 16002 / 234360 / 116; "every nontrivial component has v = d-4 vertices and degree d+2-4" (so 28 / 12 at 32D). | Graph on e_i + s e_j (1<=i<j<d), edge iff xy=0. | COMP-SRC. RC-FAIL on the law: edge totals 168 / 2520 / 26040 and component counts 7 / 22 / 53 reproduce exactly, but sizes do not. 32D has 7 components of 24 nodes (8-regular, slugs 9..15) and 15 of 28 nodes (8 are 12-regular, 7 have degrees 4 and 12). 64D: 7x48, 15x56, 31x60. Also the paper's own numbers contradict the law: 22 x 28 x 12/2 = 3696 != 2520. | LCU P0 sweep over 5-qubit pairs; component sizes by slug | 32D total ZD nodes 588 (not 616); sizes {24:7, 28:15}; per-slug component |
| B3 | M4 | p10 (Thesis 3) | Slug exclusion: no ZD edge for slugs {1..8} union {2^k: 4<=k<=n-1}. | i^j=k^l must be a non-power-of-two above 8. | CONJ ("established for 16-128D" empirically); RC-OK at 16, 32, 64D (slugs without edges: 1..8; plus 16 at 32D; 16 and 32 at 64D) | LCU P0 for pairs with slug in 1..8 or equal 16 | No zero product with those slugs |
| B4 | M1 | p7-9 (C-HF-1, T4), p15 | Hide/fill involution: prepending a high bit to S turns a kite's DMZ edges off; doing it twice turns them on; spandrels (hidden box-kites) contain exactly one octonion copy. | Bricolage "Fano node update under g insertion". | ASSERT (de Marrais Bricolage); not recomputed (needs 64D+ / 6+ qubits and the paper's S-to-ET map, which M1 and M7 admit is not stated algorithmically) | None defined without the primary definition of S above 7 | n/a |
| B5 | M1, M13, M7 | M1 p2, p7, p15; M13 p3; M7 p4 | Any integer S > 8 not a power of 2 generates a Sky (meta-fractal). | Strut constant beyond the sedenion window. | ASSERT; all three note the journal abstract page says "less than 8" (transcription error, PDF says "> 8") | none at 16D | n/a |
| B6 | M8 | p6-9 | Mandala theorem (power-of-two strut fills all addressable cells; DMZ growth ratio tends to 4), Sky conjecture (densification toward 1), regime address = (N-4)-bit expansion of floor(S/8), "Theorem 11" two-copy ET embedding. | A(K)=K(K-2), K=G-2. | M8 labels "theorem" the mandala claim and "conjecture" the sky claim; empirical, from a Rust tool | LCU sweeps at N=6,7,8 | n/a at 16D |
| B7 | M8, M12 | M8 p6; M12 p10 | "Zero-divisor adjacency" at 32D is K16 u K16 (parity cliques, degree 15), at 64D K32 u K32; "pathion adjacency" at 64D/128D is the perfect matching i -> i^4, i -> i^8 (partner i xor dim/16). | Adjacency matrices from CSV files of the codebase, predicate not defined in the monographs. | COMP-SRC about CSV files; NOT product-zero graphs: there is no pair of basis elements with e_i e_j = 0, and RC shows the real two-blade ZD graph at 32D is 588 nodes with 2520 edges, not 32 nodes with 240 edges. Treat as a different predicate | none (no algebraic definition) | n/a |
| B8 | M2, M1 | M2 p6-7 (Lacunae) | Scale-free / fractal network claims for ZD ensembles. | N to infinity, power-law degree. | CONJ; M2 states it is a research-program claim, not a theorem | Degree distribution of per-slug graphs | RC: per-slug graphs are regular or two-valued (degrees {8}, {12}, {4,12}, {16}, {24}, {28}, ...), not power-law at 16..64D |
| B9 | M6 | p2-9 | Naming ladder (pathion 32D, chingon 64D, routon 128D, voudon 256D) and generalized gamma (Brown) classification. | Metadata only. | ASSERT; no structural content | none | n/a |

### 1c. Claims in the corpus that no qubit circuit can test (listed so nothing is silently dropped)

| id | source | page | claim | status | why untestable |
|---|---|---|---|---|---|
| C1 | M3 | p4-7 | "SEDENION ZERO-DIVISOR FIELD" figure is a soft-min (power-mean, D -> -infinity) distance field over 6 major and 28 minor sites | CONJ | refers to a raster; the 2-plane projection is unidentifiable (M3 p6) |
| C2 | M1, M13, M8 | M1 p11-12, p15 | E10 billiard wall transitions are enriched on E8 Dynkin-adjacent nodes; Fano-triple enrichment; r_E8 baseline 14/56 = 0.25 | ASSERT/CONJ | dynamics claim, no algebra observable |
| C3 | M7 | p7-9 | Euclid Q1 / cosmic-web comparison with ZD graphs | CONJ | astronomy data |
| C4 | M5 | p6, p11 | Lambda lattice sizes 2187/2048/1024/512/256; two singleton exclusions patch | ASSERT | codebook-specific, not an algebra identity |
| C5 | M10 | p15 | "Validate sedenion contains R/C/H subalgebras claim (should be false)" | ASSERT | the sedenions do contain C and H, so the expectation is wrong: {e_0,e_1} spans C, {0,a,b,a^b} spans H (A8 recomputation: all 105 pairs give associative 4-element subalgebras); the sedenions also contain O |
| C6 | M9 | p3 | Normalized sedenion zero divisors ~ V2(R8) | see disagreement D1 | contradicts A11/A12 |

## 1d. Tallies (one primary source status per row, 32 rows)

Source status (what the monograph itself claims): PROVED-SRC 11 (A1-A6, A8-A12); COMP-SRC 6 (A7,
A14, A16, A17, B2, B7); CONJ 7 (A15, B3, B6, B8, C1, C2, C3); ASSERT 8 (A13, B1, B4, B5, B9, C4, C5, C6).
Total 32. Rows with a second component are labeled by their weaker part (A16: computed table, conjectured limit,
counted COMP-SRC; B6: counted CONJ).

Recomputation outcome (separate tally, this inventory's own check): holds, 17 (A1-A7, A9-A13, A15, A16 at 16D,
A17 at 8-32D exact, B1 counts, B3 at 16-64D); holds but cannot discriminate, 2 (A8: every sedenion xor-zero
triple associates; A14: both parity formulas agree at 16D); fails, 2 (B2 size/degree law; C5 expectation);
not recomputed, 11 (B4, B5, B6, B7 different predicate, B8 partly, B9, C1-C4, C6 settled by argument).

## 2. Complete sedenion box-kite inventory as the sources give it

Sources give: 7 box-kites (M1 p5, p15; M2 p5; M11 p7); 42 assessors, 6 per kite (M1 p5 "7 octahedral
lattices ... partition the 42 Assessors"; automorphism group of order 84, M1 p5, ASSERT);
84 diagonal line elements (two per assessor plane, M1 p5); 12 edges and 3 struts per kite
(M2 p3; M11 p7). Strut constant S = the octonion index absent from the six lows, S in 1..7,
one kite per S (M2 p5 "one per strut constant"); U = L xor (8 xor S) (M2 p3). Only one
explicit instance is listed in the sources: S = 7, assessors (1,14), (4,11), (5,10),
(2,13), (3,12), (6,9) with struts (1,14)<->(6,9), (4,11)<->(3,12), (5,10)<->(2,13) and
zigzag sail on the first three listed vertices (M2 p5). No source lists the other six kites
or the zero-divisor diagonals as explicit index pairs of the form (e_i +- e_j)(e_k +- e_l) = 0
beyond the S=7 edge-sign pattern. (The repository's own docs/notes/algebra_circuit_rules.md names S=3: (e1+e10)(e4-e15)=0.)

Recomputed inventory (RC, convention above). Each row: kite S, X = 8^S, assessors
(L,U), struts (pairs of strut-opposite assessors):

| S | X | assessors (L,U) | struts |
|---|---|---|---|
| 1 | 9 | (2,11) (3,10) (4,13) (5,12) (6,15) (7,14) | (2,11)-(3,10); (4,13)-(5,12); (6,15)-(7,14) |
| 2 | 10 | (1,11) (3,9) (4,14) (5,15) (6,12) (7,13) | (1,11)-(3,9); (4,14)-(6,12); (5,15)-(7,13) |
| 3 | 11 | (1,10) (2,9) (4,15) (5,14) (6,13) (7,12) | (1,10)-(2,9); (4,15)-(7,12); (5,14)-(6,13) |
| 4 | 12 | (1,13) (2,14) (3,15) (5,9) (6,10) (7,11) | (1,13)-(5,9); (2,14)-(6,10); (3,15)-(7,11) |
| 5 | 13 | (1,12) (2,15) (3,14) (4,9) (6,11) (7,10) | (1,12)-(4,9); (2,15)-(7,10); (3,14)-(6,11) |
| 6 | 14 | (1,15) (2,12) (3,13) (4,10) (5,11) (7,9) | (1,15)-(7,9); (2,12)-(4,10); (3,13)-(5,11) |
| 7 | 15 | (1,14) (2,13) (3,12) (4,11) (5,10) (6,9) | (1,14)-(6,9); (2,13)-(5,10); (3,12)-(4,11) |

Strut rule: strut-opposite assessors have lows that xor to S (RC, all 21 struts).
Planes (l, l^8) = (1,9)..(7,15) are in no kite and carry no zero divisor. Every DMZ pair
lies inside one kite (zero products exist only for same-X assessor pairs; cross-kite
and non-kite pairs have N(xy) = 1 for every sign choice).

Within one kite (sign convention (ac - d*b, da + bc*)): the octahedron has 8 faces; per
kite 4 are sails (lows xor to 0: 1 zigzag with 3 opposite edges and 3 trefoils each with
1 opposite and 2 same edges, the opposite edge being the one not incident to the shared
vertex) and 4 are vents (lows do not xor to 0: 1 with 3 opposite edges, 3 with 1 opposite
edge). Totals per kite: 6 opposite-sign and 6 same-sign edges; 24 undirected diagonal
adjacencies (12-node, 4-regular graph); every assessor has exactly 4 DMZ neighbor
assessors and 1 strut partner.

Example, S=7 diagonals (RC, all zero): d+(1,14)*d-(4,11), d-(1,14)*d+(4,11),
d+(1,14)*d-(5,10), d-(1,14)*d+(5,10), d+(4,11)*d-(5,10), d-(4,11)*d+(5,10) (zigzag, opp);
d+(2,13)*d-(3,12) and mirror, d+(2,13)*d-(6,9) and mirror, d+(3,12)*d-(6,9) and mirror (vent, opp);
the 6 cross edges (1,14)-(2,13), (1,14)-(3,12), (2,13)-(4,11), (3,12)-(5,10), (4,11)-(6,9),
(5,10)-(6,9) with d+*d+ = 0 and d-*d- = 0 (same).

## 3. Disagreements between sources (and with recomputation)

D1. Stiefel manifold. M3 p3-6 and M4 p4 give V2(R7), dimension 11, which matches the
normal form in A11 (imaginary a,b in R^7). M9 p3 writes V2(R8). By the normal form the
imaginary parts live in R^7, so V2(R7) is right and V2(R8) is a typo (dimension 13 would
fail the 14 = 11 + 3 fibre count).

D2. G2 versus V2(R7). M3 Thesis Z2 (p6) states ZD(S) is diffeomorphic to G2 and, in the
same sentence, to V2(R7); it also says "transitive G2 action with isotropy SU(2)", which
would make the space G2/SU(2) of dimension 11, not G2 (dimension 14). M4 p4 has it right:
the pair manifold Z(S) is isometric to G2, the single-element locus ZD(S) to V2(R7).
M3's earlier text on p3 ("corrects the 14-dimensional claim to 11") fits M4.

D3. Component law at 32D and above (B2). M4 asserts size d-4 and degree d+2-4 for every
component; RC finds the edge totals and component counts it reports but sizes {24, 28}
at 32D and {48, 56, 60} at 64D with several degree profiles. M4's own totals are
arithmetically inconsistent with the law (22 x 28 x 12/2 = 3696, but it reports 2520).
M4's component counts 22, 53, 116 equal 7+15, 7+15+31 and 7+15+31+63, i.e. one component
per admissible slug (RC: 22 slugs have edges at 32D, 53 at 64D); the size law fits the
16D case only.

D4. Kite versus 12-node component. M4 p5 says the 12-vertex, 4-regular components are a
"cuboctahedral-type" graph and "42 assessors correspond to an edge census in an unsigned
quotient"; M1 and M2 describe the octahedral K2,2,2 on 6 assessors. RC: both are the
same kite; 6 assessors x 2 diagonals = 12 nodes, 12 octahedron edges x 2 = 24 edges
(168 = 7 x 24). The 168 is the edge count of the signed model (M4) and also the order of
PSL(2,7) (M1 p6); the sources read the two as related, but 7 x 24 = 168 follows from the
count alone. The "168 fillable cells per
emanation table" at 32D (B1) is a third, unrelated 168 (14 x 12).

D5. Hurwitz date and "G2 as automorphisms of E8". M2 p2, p6 notes de Marrais gives 1896 for
the Hurwitz obstruction (usual attribution 1898/1923) and calls G2 the automorphism group
of E8 (it is the automorphism group of the octonions). Neither affects any circuit claim.

D6. "Any integer less than 8" versus "greater than 8" for Sky strut constants: M1 p2,
M2 p7, M7 p4 and M13 p3 all treat "< 8" (Complex Systems abstract page) as a transcription
error; the PDF and Part III say "> 8".

D7. M8 erratum: M8 p7 corrects an earlier claim that {S, G, G^S} is a subgroup; the Klein
four-group is {0, S, G, G^S}. M1 p5 still writes X = G + S (ordinary sum) in the strut
formulas. For S in 1..7, G = 8, G + S = G ^ S, so no numeric conflict at 16D; at G = 16 and
S >= 16 the two differ.

D8. Edge-sign naming. M5 does not fix whether eta = 0 means "same" or "opposite"; RC
under (ac - d*b, da + bc*) gives eta = 1 for same-sign DMZ edges. M5/M10's "diagonal versus
anti-diagonal" correction cannot be validated at 16D: both formulas agree on all 84
sedenion edges.

D9. Hurwitz/zero-divisor mechanism: M3 p2 says zero divisors arise either from indefinite
norm (split composition algebras) or from loss of the composition law (CD n>=4); M6 p4
notes split versus non-split is a signature distinction at n>=4. No quantitative conflict.

D10. Fold-down and middens: M1 states the 7 sparse 32D tables (inner xor > 24) fold onto the
7 sedenion box-kites; RC shows the 32D slugs 9..15 (X < 16) give 7 further components of 24
nodes each (12 assessors), which the monographs call "middens" without listing them. Whether
those are the images of the sedenion kites under a doubling is not checked.

## 4. Sources skipped, and why

Read in full (all 7 named monographs): M1 through M7.
Also scanned by keyword with the relevant sections read: M8, M9, M10, M11, M12, M13, and
"Warp Ring Visualization Analysis Synthesis" (M14, uses box-kite/strut language as an analogy only, no
algebraic claim).

Skipped, with reason (zero or incidental hits for "box-kite", "assessor", "zero divisor",
"sedenion", "strut"):
- A Deep Synthesis of STAR's Lambda-Lambda-bar ... Cayley-Dickson Triad; Condensate Spin Correlations ...
  Algebraic Triads; Coupler-Manifold Synthesis; DAS MERGUS AD ASTRA; DAS MERGUS (Wavelet-Gated
  Dynamics); Das Mergus.pdf; Directus Maximalus Audit; Genesis 2.0; Lambda, Randomness and Integrated
  Computation; Provenance map for the Wow Signal; Retrocausality and the Time Rondeau Crystal;
  Single-minus gluon amplitudes; TOP-Lambda Unification Audit; Towards a Unified Computation-Quantum-
  Cognition Architecture; Warp Evidence-Contract Monograph; Drude Metals; theme and desktop PDFs.
  Keyword counts were 0 (Drude: 2, incidental). The two physics ones with "Cayley-Dickson" in the title
  (STAR and Condensate) contain no zero-divisor or box-kite text.
- CAYLEYDICKSON_SOLAR_ANALYSIS.md: read headings and every zero-divisor hit.
  Its only use is as a null control: the CD associator observable is reported "not a zero-divisor
  artifact" (lines 139, 156, 239), i.e. a zero-divisor proximity audit that stayed flat. No structural
  box-kite claim. Not tabulated.
- The top level of the local CayleyDickson collection (PDFs): titles are a Statistics and
  Probability Letters paper, "Spacetime Quasicrystals", "Perturbative unitarity of fractional field
  theories", two Nature/Nature Physics silicon-qubit papers, an MPEG-2 and rate-control set, and the
  Nature Scientific Reports paper; none concerns Cayley-Dickson algebras, zero divisors or sedenions,
  so none was opened beyond page 1. The CD primary literature lives in subdirectories
  (tier1_core_cd_algebra/cd_tower_structure with de Marrais papers math/0011260, math/0207003,
  math/0403113, math/0603281, 0704.0026, 0704.0112, 0804.3416, Pathions1-3, wilmot_2025; and
  zero_divisors_geometry with Moreno, Reggiani, Guterman-Zhilina). Out of the stated scope; a
  follow-up should read de Marrais' Theorem 3 and Theorem 7 statements, the Placeholder Substructures III
  S-to-ET definition (needed for B4 and B5), and the Guterman-Zhilina relation-graph papers
  (cross-check of the 84-vertex 4-regular graph) before citing a primary page.
- Source images, GitHub files and CSVs that the monographs reference (open_gororoba data/csv,
  boxkites.rs tests, the retained Rust census CSV) were not opened and are not available as primary
  evidence here; claims resting on them (A14 enumeration, A16 table, A17 for 64D and 128D, B2, B7) are
  taken as reported or marked as recomputed only where this inventory says RC.
