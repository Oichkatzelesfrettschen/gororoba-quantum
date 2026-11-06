# W8 -> N-: the quadric scheme is two geometric primes, of degrees 20 and 30, at p = 32009 and p = 32029

Claim. At p = 32009 and at p = 32029 the W8 -> N- degree-2 kernel K2 is radical and V(K2) = C20 cup C30 with C20 and
C30 geometrically irreducible of projective dimension 5 and degrees 20 and 30. At 32009, with P the ideal of
`check.sing`, V(P) = C20 (so rad P = I(C20)) and K2 : P = I(C30), prime and geometrically prime; at 32029 the two
primes are named I(C20) and I(C30) and are not asserted to be coefficientwise reductions of the 32009 ideals. The
criterion of the findings note (F(I) = k[y]/K2 exactly when Proj F(I) contains every component of V(K2)) therefore
needs arcs into C20 and C30 only.

## Inputs and coordinates

K2 at 32009 is `working/runs/w8_a2/w8_k2.rel` (sha256 31feaac8...), Cohen-Macaulay of degree 50 (`k2-cm.jsonl`);
`same-k2.sing` and `same-k2.log` show that it, the K of `check.sing` and the degree-2 receipt relations
`working/distribute/out/a5-w8-receipt-p1/w8_p1/d2/relations-d2.rel` contain one another in the same coordinates
y(1..24) (the generators G_1..G_24 of the header). K2 at 32029 is
`working/distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel` (sha256 ed601263...), Cohen-Macaulay of degree 50.
`check.log` records that P contains K2 and the nine linear forms Lambda (`P-p32009.txt`, first nine generators), that P
has projective dimension 5 and degree 20, and that K2 = P cap (K2 : P) with K2 : P (`quotient.txt`, sha256
dd18bea7...) of projective dimension 5 and degree 30. No primality of P is used below.

## Sections of the whole V(K2)

`build_k2_sections.py PRIME 8 DRAWS` writes eight sections and the Lambda check per prime from 1,344 ANU QRNG values
(32009: draws `draw-2026-11-06T003103Z.json`, `T003106Z`, `T003108Z`; 32029: `draw-2026-11-05T224545Z.json`,
`T224548Z`, `T224550Z`; the draw file and zero-based index of every coefficient in `coefficients-k2-pP.json`). A section
adds five forms L1..L5, the chart l0 = 1 for a sixth form and t = u for a seventh. Singular 4.4.1 (passagemath,
laptop), about 2 s each; logs `k2-pP-sectionS.log`, `p-pP-check.log`.

| Section | 32009: vdim, factor degrees of the eliminant of t | 32029: vdim, factor degrees |
|---|---|---|
| 1 | 50: 1, 1, 1, 2, 5, 15, 25 | 50: 1, 1, 1, 1, 3, 15, 28 |
| 2 | 50: 2, 11, 17, 20 | 50: 7, 10, 13, 20 |
| 3 | 50: 1, 1, 3, 3, 3, 5, 5, 8, 10, 11 | 50: 1, 2, 8, 9, 12, 18 |
| 4 | 50: 1, 1, 4, 5, 9, 10, 20 | 50: 1, 1, 1, 1, 2, 5, 7, 13, 19 |
| 5 | 50: 1, 1, 2, 4, 7, 7, 28 | 50: 1, 1, 12, 16, 20 |
| 6 | 50: 1, 1, 4, 5, 19, 20 | 50: 1, 3, 3, 6, 14, 23 |
| 7 | 50: 1, 1, 1, 17, 30 | 50: 1, 1, 2, 5, 8, 9, 10, 14 |
| 8 | 50: 1, 1, 1, 1, 2, 2, 3, 3, 7, 7, 8, 14 | 50: 1, 4, 4, 16, 25 |
| K2 + Lambda | projective dimension 5, degree 20; section 1: 20: 1, 1, 1, 2, 15 | 5, 20; section 1: 20: 1, 1, 3, 15 |

All eliminants have degree equal to vdim and every factor has multiplicity 1.

## Proof (at each prime)

1. Reduced section. A squarefree eliminant of degree vdim makes the point scheme k[t]/(e): vdim distinct points in
   the chart l0 != 0, on which Frobenius acts with orbits the factor degrees.
2. K2 radical. A = k[y]/K2 is Cohen-Macaulay of dimension 6, so the general forms L1..L5 are a regular sequence and
   B = A/(L1..L5) is Cohen-Macaulay of dimension 1; l0 avoids its minimal primes (the section is finite and of full
   length 50 = deg K2, so no point lies at l0 = 0), so l0 is a nonzerodivisor on B and B embeds in
   B[1/l0] = (B/(l0 - 1))[l0, 1/l0], which is reduced by step 1. Reducedness lifts from A/(L1..L_k) to A/(L1..L_(k-1))
   along the homogeneous nonzerodivisor L_k (a nilpotent a lies in L_k A, a = L_k b with b nilpotent of lower degree),
   so A is reduced.
3. Each component contributes exactly its degree, disjointly. Over the algebraic closure V(K2) = V_1 cup ... cup V_m
   is equidimensional of degree 50 (K2 radical, A Cohen-Macaulay, F_p perfect). A linear space of complementary
   dimension meets V_i in at most deg V_i points when the intersection is finite, so 50 distinct points force each V_i
   to contribute exactly deg V_i points, disjoint from the others; an F_p-component of degree d owns a
   Frobenius-stable set of d section points, so d is a subset sum of orbit sizes in every section.
4. Possible degrees. The proper subset sums common to the eight sections are 2, 19, 20, 30, 31, 48 at 32009 and
   17, 20, 30, 33 at 32029.
5. The degree-20 component. The 5-dimensional part of V(K2 + Lambda) is the union of the components of V(K2) inside
   V(Lambda). Section 1 cuts K2 + Lambda (degree 20) in 20 distinct points, a subset of the section-1 points of K2, so
   that union has degree exactly 20 (the 20 distinct points exclude a doubled component of degree 10) and owns the
   section-1 orbits 1, 1, 1, 2, 15 (32009) or 1, 1, 3, 15 (32029). Splitting 20 into allowed degrees with those orbits
   is impossible, so it is one F_p-component C20. The remaining orbits, 1, 1, 5, 25 (32009) or 1, 1, 28 (32029), sum to
   30, which has no split into allowed degrees, so the rest is one F_p-component C30.
6. Geometric irreducibility. If an F_p-component split over the algebraic closure into r > 1 conjugate components,
   Frobenius would permute them cyclically and, by step 3, every orbit on it would have size divisible by r. Each of
   C20 and C30 owns an orbit of size 1 in section 1.
7. The ideals of check.sing at 32009. P contains K2 and Lambda, so V(P) lies in V(K2 + Lambda); V(P) has projective
   dimension 5 and degree at most 20, so its reduced 5-dimensional part is C20 and V(P) = C20, rad P = I(C20). Since K2
   is radical, K2 = I(C20) cap I(C30), and K2 : P = (I(C20) : P) cap (I(C30) : P) = (1) cap I(C30) = I(C30), because P
   lies in I(C20) and not in the prime I(C30). This needs no primality of P.

## Corroboration: sections of K2 : P at 32009

`build.py` cuts V(K2 : P) itself (`quotient.txt`) with 1,344 further QRNG values (draws
`draw-2026-11-05T223710Z.json`, `T223713Z`, `T223715Z`; the draw file and index of every coefficient in
`coefficients.json`); logs `section1.log` .. `section8.log`.

| Section | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| factor degrees (degree 30 = vdim, squarefree) | 3, 3, 24 | 1, 7, 8, 14 | 1, 2, 7, 7, 13 | 1, 3, 5, 21 | 1, 3, 5, 21 | 1, 3, 3, 23 | 8, 22 | 1, 4, 12, 13 |

Sections 1 and 7 share no proper subset sum (3, 6, 24, 27 against 8, 22) and six sections have an orbit of size 1, so
V(K2 : P) is geometrically irreducible of degree 30, which agrees with K2 : P = I(C30).

Scope. Finite fields F_32009 and F_32029; characteristic 0 is not addressed.
