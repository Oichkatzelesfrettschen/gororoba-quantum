# Iso -> N- K2 is prime at p = 32009 and p = 32029, also over the algebraic closure (section and Frobenius-orbit argument)

**Inputs.** K2 = `docs/evidence/a5-exceptional-fibers/working/runs/s3/iso_k2.rel` (sha256 53852d5c...), radical
(`../chart-colon/`), Cohen-Macaulay of dimension 5 and degree 23 (`docs/notes/topics/a5-exceptional-fiber-findings.md`
line 247). Linear forms from ANU QRNG draws (`coefficients.json`, zero-based indices, values >= 32009 rejected):
three per section from `draw-2026-11-05T182851Z.json`, the fourth from `draw-2026-11-05T192653Z.json`.

**Computation** (`build_points.py` writes `points1.sing`, `points2.sing`; Singular 4.4.1, about 1 s each). For each
section: Z = K2 + (four forms) has dimension 1 and degree 23; the chart y_1 = 1 has vdim 23, so every point lies in
y_1 != 0; for every coordinate y_2..y_17 the eliminant (minimal polynomial) has degree 23.

| Section | Eliminant factorization over F_32009 (every coordinate) |
|---|---|
| 1 | 7^1 * 16^1 |
| 2 | 23^1 (irreducible, squarefree) |

**Argument** (orchestrator reasoning; the lifting step is the review's, `concurrency-review/codex-iso-high.md`).
1. The four forms are a regular sequence on the Cohen-Macaulay k[y]/K2, since each drops the dimension (5, 2, 1).
2. Section 2: a squarefree degree-23 eliminant of a coordinate on a length-23 scheme makes the chart k[t]/(e), reduced;
   y_1 is a nonzerodivisor on the one-dimensional Cohen-Macaulay quotient (its associated primes are the 23 points, all
   off y_1 = 0), so that quotient is reduced, and reducedness lifts across the homogeneous nonzerodivisor (fourth form):
   the curve ring R2 = k[y]/(K2 + three forms) is reduced.
3. Every F_32009-component of V(R2) meets the fourth hyperplane in a nonempty Frobenius-stable subset of the 23
   points; the irreducible eliminant makes them one orbit, so R2 has one minimal prime and, being reduced, is a domain.
4. Domainhood lifts across each homogeneous nonzerodivisor of the regular sequence, so k[y]/K2 is a domain: K2 is prime
   over F_32009.
5. The geometric components of the F_32009-irreducible V(K2) form one Frobenius orbit of m components of equal degree,
   so m divides 23. With m = 23 every point of V(K2) would have Frobenius orbit size divisible by 23; section 1 has an
   orbit of size 7. So m = 1: V(K2) is geometrically irreducible, and K2 (radical over a perfect field) stays prime over
   the algebraic closure.

**Cohen-Macaulay check at both primes** (`cm1.sing`, `cm2.sing`): K2 + (four section forms) + (y_1) has dimension 0
and length 23 = deg K2 at p = 32009 (section 2) and p = 32029 (section 10). A linear system of parameters of colength
equal to the multiplicity makes k[y]/K2 Cohen-Macaulay and the five forms a regular sequence, which also gives y_1 a
nonzerodivisor on the one-dimensional quotient in step 2.

**Second prime p = 32029** (`points*-p32029.*`, `p2-section3..18.*`, `build_p2_sections.py`, coefficients in
`coefficients-p32029*.json` from draws `draw-2026-11-05T194911Z.json`, `T194958Z`, `T195001Z`; relations
`working/distribute/out/a5-p2-iso/iso_p2/d2/relations-d2.rel`, degree-certified). Eighteen sections, each 23
distinct points (squarefree degree-23 eliminant of y_2). Section 10: 23^1, one Frobenius orbit, so the argument above
proves K2 prime over F_32029; orbit sizes 1, 5, 7 and others exclude 23 conjugate components, so it is geometrically
prime there too. Orbit partitions of the other sections (for the record): 1+1+1+20, 2+9+12, 1+1+1+3+4+6+7, 2+21,
1+1+2+4+15, 1+2+6+14, 1+6+16, 5+7+11, 3+5+6+9, 5+5+6+7, 1+2+9+11, 4+19, 1+1+2+19, 4+4+6+9, 1+1+3+3+5+10, 1+11+11,
6+6+11. The first six all admitted a degree-2 subset; section 10 and section 11 (5+5+6+7) exclude it.

**Consequence.** The Iso arc certificates need one component, V(K2) itself (degree 23, projective dimension 4).
Not covered: characteristic 0.
