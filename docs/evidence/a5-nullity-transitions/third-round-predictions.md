Written 2026-11-28 before any level-7 or level-8 run.
At y = e_1 + e_10 in A_n (dimension 2^n), n = 7 and 8:
- kernel dimension 2^(n-2): 32 and 64; it meets the lower and upper halves in 2^(n-3) each (16+16, 32+32).
- pencil dimension 2^(n-2) - 1: 31 and 63.
- commutant a quaternion algebra (dimension 4, noncommutative, traceless trace form negative definite).
- Lie closure sp(2^(n-4)) of dimension k(2k+1), k = 2^(n-4): 136 and 528.
Calibration: levels 4, 5, 6 reproduce 3/7/15 pencil, 4 commutant, 3/10/36 closure; the type-R point
e_1+e_10+e_3+e_20 in A_5 reads commutant 1, closure 28.

Written 2026-11-28 before any N+- Pfaffian run (A5-657 at N+-):
- at N- = e3+e20+e12-e27 and N+ = e3+e20-e12+e27 the pencil has 19 coordinate units, 18 of them doubly pure.
- restricted to the doubly pure coordinates, Pf of the 16x16 pencil (degree 8) equals a nonzero constant times
  |lead Q|^2 |lead G|^2 on the lines along those units, with 2 (ord Q + ord G) = 8.

Written 2026-11-28 before the common-kernel search (MATH-225):
- for sedenion zero divisors p, q, dim (ker L_p n ker L_q) lies in {0, 2, 4} and never 1 or 3 (hypothesis: a
  complex structure on the common kernel); on every W8 point (p, q) found, the pencil type follows that dimension.

Written 2026-11-28 after the first record run and before the determinant route was coded (P26):
- an implementation sharing no code with cd_core or the polynomial-ring expansion (products by the doubling
  formula, Q and G as Gaussian-integer polynomials in s) finds, at N- and N+ over all 30 doubly pure imaginary
  units and 60 integer points, det of the pencil equal to a constant times (|lead Q|^2 |lead G|^2)^2, with the
  normalized constant 4 of the 18-unit identity.
