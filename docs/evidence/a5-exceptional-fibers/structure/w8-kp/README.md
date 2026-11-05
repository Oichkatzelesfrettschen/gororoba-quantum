# W8 -> N-: K2 : P is geometrically prime at p = 32009

Claim. Over F_32009 the W8 -> N- degree-2 kernel K2 equals P cap Q with P prime (projective dimension 5, degree 20)
and Q = K2 : P prime and geometrically prime (projective dimension 5, degree 30). So V(K2) has exactly two components,
V(P) and V(Q), and the criterion of the findings note (F(I) = k[y]/K2 exactly when Proj F(I) contains V(P) and every
component of V(K2 : P)) needs arcs into V(P) and into V(Q) only.

Inputs. Q is `quotient.txt` (sha256 dd18bea7..., written by
`check.sing`, whose log `check.log` records K2 = P cap (K2 : P), P prime of degree 20, K2 : P of projective dimension 5
and degree 30). Premises from `docs/notes/topics/a5-exceptional-fiber-findings.md`: K2 radical (W8 row of the
structure table), k[y]/K2 Cohen-Macaulay at 32009 (section "The quadric ring k[y]/K2 is Cohen-Macaulay"), so every
minimal prime of K2 has projective dimension 5 and none is embedded; Q, the intersection of the minimal primes of K2
other than P, is radical and equidimensional of degree 30.

Sections. `build.py` takes 1,344 ANU QRNG values (draws `docs/evidence/anu_qrng/draw-2026-11-05T223710Z.json`,
`T223713Z`, `T223715Z`; uint16 values below 32009 in draw order then index order, each used once; first and last index
of each section in `coefficients.json`). Section s adds five forms L1..L5, the chart l0 = 1 for a sixth form and
t = u for a seventh. Singular 4.4.1 (passagemath, laptop), under 1 s each; logs `section1.log` .. `section8.log`,
script digests `sha256.txt`.

| Section | dim, vdim | eliminant of t: degree, factor degrees (all multiplicity 1) |
|---|---|---|
| 1 | 0, 30 | 30: 3, 3, 24 |
| 2 | 0, 30 | 30: 1, 7, 8, 14 |
| 3 | 0, 30 | 30: 1, 2, 7, 7, 13 |
| 4 | 0, 30 | 30: 1, 3, 5, 21 |
| 5 | 0, 30 | 30: 1, 3, 5, 21 |
| 6 | 0, 30 | 30: 1, 3, 3, 23 |
| 7 | 0, 30 | 30: 8, 22 |
| 8 | 0, 30 | 30: 1, 4, 12, 13 |

Proof.

1. Reduced section. A squarefree eliminant of degree 30 = vdim makes A = k[y, t]/(Q + L + (l0 - 1) + (t - u)) equal
   to k[t]/(e): 30 distinct points of V(Q) in the chart l0 != 0, all cut by L, and Frobenius acts on them with orbits
   the factor degrees of e.
2. Each component contributes exactly its degree, disjointly. Let V(Q) = V_1 cup ... cup V_m over the algebraic closure
   (Q stays radical and equidimensional there, F_p being perfect). A linear space of complementary dimension meets
   V_i in at most deg V_i points when the intersection is finite, so the 30 points are at most sum deg V_i = 30, and
   equality forces each V_i to meet it in deg V_i points, disjoint from the other V_j.
3. F_p-irreducible. An F_p-component of degree d then owns a Frobenius-stable set of d section points, so d is a subset
   sum of orbit sizes in every section. Section 1 allows proper d in {3, 6, 24, 27}, section 7 allows {8, 22}; the sets
   are disjoint, so V(Q) is F_p-irreducible and, Q being radical, Q is prime over F_32009.
4. Geometrically prime. If Q split over the algebraic closure into r > 1 conjugate components, Frobenius would permute
   them cyclically and, by step 2, move each section point off its own component, so every orbit size would be a
   multiple of r. Sections 2, 3, 4, 5, 6 and 8 each have an orbit of size 1, so r = 1.

Scope. The section below carries the decomposition to p = 32029. It rests on
the two premises above, both recorded in the findings note at 32009. Characteristic 0 is not addressed.

## The same decomposition at p = 32029

`build_k2_p32029.py` cuts the whole V(K2) at p = 32029 (`working/distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel`,
sha256 ed601263..., Cohen-Macaulay of degree 50 by `k2-cm.jsonl`) with 1,344 further QRNG values (draws
`draw-2026-11-05T224545Z.json`, `T224548Z`, `T224550Z`; indices in `coefficients-k2-p32029.json`). Logs
`k2-p32029-section1.log` .. `k2-p32029-section8.log`, about 2 s each:

| Section | vdim | eliminant of t: degree, factor degrees |
|---|---|---|
| 1 | 50 | 50: 1, 1, 1, 1, 3, 15, 28 |
| 2 | 50 | 50: 7, 10, 13, 20 |
| 3 | 50 | 50: 1, 2, 8, 9, 12, 18 |
| 4 | 50 | 50: 1, 1, 1, 1, 2, 5, 7, 13, 19 |
| 5 | 50 | 50: 1, 1, 12, 16, 20 |
| 6 | 50 | 50: 1, 3, 3, 6, 14, 23 |
| 7 | 50 | 50: 1, 1, 2, 5, 8, 9, 10, 14 |
| 8 | 50 | 50: 1, 4, 4, 16, 25 |

Every section is 50 distinct points, so K2 is radical at 32029 (a reduced Artinian reduction of a Cohen-Macaulay
graded ring lifts reducedness along the regular sequence). The proper subset sums common to all eight partitions are
17, 20, 30 and 33. `p-p32029-check.sing` adds the nine linear generators of P at 32009 with i = 10754 replaced by the
32029 root 9115: K2 + Lambda has projective dimension 5 and degree 20, and section 1 cuts it to 20 distinct points
with orbits 1, 1, 3, 15 (`p-p32029-check.log`). The 5-dimensional part of V(K2 + Lambda) is the union of the
components of V(K2) inside V(Lambda), of total degree 20; with component degrees in {17, 20, 30, 33} that is one
component of degree 20, and the rest, of degree 30, is one component. In section 1 the degree-20 component holds the
orbits 1, 1, 3, 15 and the degree-30 component 1, 1, 28, so each has a size-1 orbit and is geometrically irreducible.
So at p = 32029 as at p = 32009, K2 = P cap Q with P and Q geometrically prime of degrees 20 and 30.
