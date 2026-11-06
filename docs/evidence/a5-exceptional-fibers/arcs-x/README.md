# Arc certificate that the reduced exceptional fiber of X+ -> N- and X- -> N+ is P^2

At p = 32009 and p = 32029 the reduced exceptional fiber over the base point is all of P^2 for both opposite-sign
incidences, X+ -> N- (`xp-nm`) and X- -> N+ (`xm-np`). Linear arcs through the origin of the slice V(J) leave it with
order-2 limit vectors F(W, R, S) = (a1 W^2, a2 W (R + S), a3 W (R - S)) whose Jacobian has rank 3 (determinant
-4 a1 a2 a3 W^3, nonzero for W != 0). The image is the open set {y1 != 0} of the affine cone, so the limit points are
dense in P^2, the reduced fiber is P^2, the ideal L of relations of the fiber cone is 0 and
F(I) = k[y1,y2,y3] in every degree. Every statement holds over the fields F_32009 and F_32029 and says nothing about
characteristic 0. The [evidence README](../README.md) places the package among the other records. The package
parallels the arc certificates of E8-bar -> N- and E8-bar -> N+ in `arcs/` (a sibling package of the evidence
directory); module names carry the prefix `xarc_` so both packages import side by side.

## Notation

The slice V(J) of the closure of a nullity-8 orbit is cut out by 12 polynomials J in the seven coordinates
t1, t2, t4, t5, t6, t7, t9 (the emission receipt lists t3 and t8 as eliminated) and carries 3 functions
G1, G2, G3 (the header `ideal G`) whose ideal I defines the blow-up center. The fiber cone is
F(I) = k[y]/L = sum over d of I^d / m I^d, with y1..y3 standing for G1..G3, m the maximal ideal of the origin and
k the algebraic closure of F_p. The two incidences differ by the sign s9 of t9: t9 = s9 * t9xp with s9 = +1 on
X+ -> N- and s9 = -1 on X- -> N+.

## Inputs

The headers `xp-nm.sing` and `xm-np.sing` sit in `../working/build/inputs/pP-rI/` beside the other headers, with the
emission receipt `receipt-x-opposite.json` (the file `receipt.json` of the same directory covers the other
incidences). Line 1 of a header is the ring over F_P, line 2 is `number I=ROOT;` with ROOT a square root of -1 modulo
P, line 3 holds J and line 4 holds G. Every script and record of this package takes P and ROOT from these two lines;
`replay.sh` accepts `--root` and `--header-dir` and raises when either disagrees with the header.

| P | ROOT | `xp-nm.sing` sha256 | `xm-np.sing` sha256 |
|---|---|---|---|
| 32009 | 10754 | `54d3166188cb56a45e2b0d4d0be6da73bbf757de0d6dedc6586d396e201cf280` | `b47b99e772a0878d7d0aba3473d67f46944a46fb91a0189c840ec541f078f500` |
| 32029 | 9115 | `3d383939164ec3d8e4173662ca75a3c2a20b8f654e859c27157eece1947d7e28` | `53306cce7d1063626a85fe9d7cf1696b22b498b3a9b2aa4147c6c571d4d9277c` |

Each digest equals the `header_sha256` of the receipt. Tools: Singular 4.4.1, python-flint 0.9.0, sympy 1.14.0,
Python 3.14.7. Every Singular ring uses the global ordering `dp`.

## Method

**Structure of V(J).** `logs/pP/SLUG_explore.log`: V(J) has dimension 4, J is its own unique minimal prime (global
degree 6), and the Jacobian of J at the origin has rank 3, so the germ at the origin is smooth of dimension 4. The
last generator of J carries the t9 term -8 t9 on X+ -> N- and +8 t9 on X- -> N+. The four generators in t4..t7, t9
are the rank-one relations of the matrix [[m rho, m sigma], [rho, sigma]] used in the E8-bar package of `arcs/`. They
give the parametrization Phi in the four parameters (w, rho, sig, s1) with m = 1 + w:

    t1 = s1,  t4 = (m rho + sig)/2,  t5 = (m rho - sig)/2,  t6 = (m sig + rho)/2,  t7 = (rho - m sig)/2,
    t9 = s9 * t9xp,  t9xp = -w^2/(2m),  t2 = w (2 + w)/(2m) * (s1 - t9xp + 2).

The two incidences are the same variety under t9 -> -t9: `logs/pP/flip_check.log` finds that the sign change of t9
maps the 12 generators of J of `xp-nm` onto those of `xm-np` up to sign and each G_j onto G_j (three more sign
changes of the coordinates relate the pair the same way). The `xm-np` Phi is verified directly, not inferred from that
map.

**Phi lies on V(J) and is a local isomorphism.** `sing/pP/SLUG_phi.sing` substitutes Phi into J, clears the
denominators (u = 1/m) and finds 0 nonzero numerators of 12 generators for both incidences at both primes. The control
that reverses the sign of the t9 term of the last generator of J leaves 1 nonzero numerator (`logs/pP/SLUG_ctl.log`;
the script reads the coefficient from the header). `xarc_certify.py` repeats the identity on 36 exact parameter
points (0 nonvanishing evaluations) and computes the 7 x 4 Jacobian of Phi by dual numbers: rank 4 at the origin and
at (w, rho, sig, s1) = (3, 5, 7, 11). Phi is an isomorphism of formal germs onto the smooth germ of V(J), so every
formal arc of V(J) through the origin is an arc of Phi.

**Limit map.** For x(s) = Phi(w = W s, rho = R s, sig = S s, s1 = K s) the script `sing/pP/SLUG_limit.sing` expands
G_j(x(s)) modulo s^4 with W, R, S, K symbolic. The coefficients of s^0 and s^1 vanish and the coefficient of s^2 is
the limit vector; K does not enter it. The coefficients below come from `records/pP/SLUG/result.json`
(`limit_map`).

| P | Incidence | F1 | F2 | F3 | determinant in W, R, S |
|---|---|---|---|---|---|
| 32009 | X+ -> N- | 19990 W^2 | 32001 W (R + S) | 32001 W (R - S) | 3076864 W^3 |
| 32009 | X- -> N+ | 19990 W^2 | 8 W (R + S) | 8 W (R - S) | 3076864 W^3 |
| 32029 | X+ -> N- | 14305 W^2 | 32021 W (R + S) | 32021 W (R - S) | -3662080 W^3 |
| 32029 | X- -> N+ | 14305 W^2 | 8 W (R + S) | 8 W (R - S) | -3662080 W^3 |

The coefficient 32001 is -8 modulo 32009 and 32021 is -8 modulo 32029. The Jacobian of F = (a1 W^2, a2 W (R + S),
a3 W (R - S)) with respect to (W, R, S) has determinant -4 a1 a2 a3 W^3, which is 4000 W^3 modulo 32009 and
21255 W^3 modulo 32029 and vanishes only at W = 0 because a1, a2, a3 are nonzero. The rank of the limit map is 3
wherever W != 0.

**Density.** A limit vector F of an arc with G(x(s)) not identically 0 gives a point of P^2. F is dominant onto A^3,
so its projectivization is dense in P^2, and the set of limit points of the blow-up fiber is closed and equal to the
reduced fiber (curve selection: every point of the fiber is an arc limit). For a relation f of degree d in L,
f(G) lies in m I^d and forces f(F) = 0 at every limit vector; with density f = 0, so L = 0. The map inverts
explicitly: the projective point (1 : a : b) is the limit of the arc with W = 1, R + S = a1 a/a2, R - S = a1 b/a3, so
every F_p-point of P^2 with y1 != 0 is the limit of an F_p-rational arc.

**Divisorial part.** `sing/pP/SLUG_phi.sing` also computes the gcd h of the three cleared numerators of G_j(Phi) in
k[w, rho, sig, s1]: h = -w (w+2) (s1+1) Q with Q(0) = 4 at both primes, so locally h = unit * w, which matches the
height 1 of I (the divisor w = 0 is t2 = 0, t9 = 0). The quotients G''_j = G_j(Phi)/h divide exactly (remainder 0)
and have the linear initial forms below. Three independent linear forms make (G'') the ideal of a smooth curve germ,
part of a regular system of parameters, so I = w * (G'') has analytic spread 3 and I^d/m I^d is the degree-d part of
k[y1,y2,y3]. This is a second proof of F(I) = k[y1,y2,y3] that needs Phi to be a local isomorphism (rank 4 above) and
no arcs.

| P | Incidence | initial forms of G''_1, G''_2, G''_3 |
|---|---|---|
| 32009 | X+ -> N- | -10501 w, rho + sig, rho - sig |
| 32009 | X- -> N+ | -10501 w, -rho - sig, -rho + sig |
| 32029 | X+ -> N- | -13799 w, rho + sig, rho - sig |
| 32029 | X- -> N+ | -13799 w, -rho - sig, -rho + sig |

**Ideal-level check without arcs.** `sing/pP/SLUG_quot.sing` (global ordering) computes I' = (J + G) : t2 with
111 generators; f = t2 equals w times a unit at the origin. The colength of I' + m^n is 1, 2, ..., 8 for
n = 1..8, the ladder of a smooth curve germ, so I' has height 3 at the origin and O/I' is regular of dimension 1. The
colengths of (J + t2) + m^n are 1, 4, 10, 20, 35, 56 (a smooth 3-fold germ, C(n+2, 3)) and equal those of
(J + t2 + G) + m^n for n = 1..8, so G lies in (t2) modulo J at the origin. Hence I = t2 * I' locally with I' a smooth
height-3 curve germ in the smooth 4-fold germ, I^d/m I^d is isomorphic to I'^d/m I'^d, and F(I) = k[y1,y2,y3] in
every degree. The containment is local: globally 3 of the remainders of G modulo J + t2 are nonzero, because t2 = 0
also holds on the branch w = -2 away from the origin. The colength tests bound the containment to n <= 8; the exact
containment is the gcd statement above. The same logs hold at both primes and both incidences.

**Hilbert-Samuel ladder.** The colength of x1 (x1, x2, x3) + m^n in k[x1..x4] is 5, 23, 61, 127, 229, 375, 573 for
n = 2, 4, ..., 14 (`logs/pP/model_colength.log`, equal to C(n+2, 3) + n - 1), the prediction of I = t2 * I' for the
colength of J + G + m^n. At p = 32009 the measured values of J + G + m^n equal these at every n
([../x-opposite-ladder/hs-xp-nm.log](../x-opposite-ladder/hs-xp-nm.log) and `hs-xm-np.log` there). The truncated
ranks of the degree-d fiber cone for d = 5 to 9 in [../x-opposite-ladder/](../x-opposite-ladder/README.md) are the
full monomial counts C(d+2, 2) of k[y1,y2,y3].

## Checks and results

The checks hold for each of the four (prime, incidence) pairs.

| Check | Result |
|---|---|
| dim V(J), primality, Jacobian rank at 0 | 4, one minimal prime, rank 3 |
| J(Phi) = 0 as a rational identity (Singular) | 0 nonzero numerators of 12 |
| J(Phi) = 0 at 36 parameter points (flint) | 0 failures |
| rank dPhi (dual numbers) | 4 at the origin, 4 at (3, 5, 7, 11) |
| Jacobian rank of the limit map at 5 points, symbolic | 3, 3, 3, 3, 3 |
| Same rank from exact replays (central differences, exact because F has degree 2) | 3, 3, 3, 3, 3 |
| 100-point grid W in {1,3,7,11,19}, R in {2,5,13,21,34}, S in {1,6}, K in {0,4} | 0 failures: x(0) = 0, all 12 J generators vanish mod s^12, order of G(x(s)) is 2, the coefficients of s^0..s^3 of the three G_j equal the Singular symbolic ones |
| 100 prescribed projective targets (1 : a : b), a, b in 0..9 | 100 of 100 hit exactly by their arcs |
| Control: sign of the t9 term of J[12] reversed | symbolic numerators nonzero (1); J(x(s)) != 0 at 100 of 100 points |
| Control: G_2 replaced by G_2 + t2^2 | series differ from the symbolic ones at 100 of 100 points |
| Control: G_3 replaced by a copy of G_2 | Jacobian rank of the limit map is 2 at all 5 points |

The grid replay is independent of Singular: it builds Phi as truncated series in python-flint `nmod_poly` (1/m by
series inversion), evaluates the original J and G from the headers (not G''), and compares with the symbolic
coefficients parsed from the Singular log. The perturbation in the second control is a monomial of t-degree 2; a
term of t-degree 3 or more is invisible at order s^2.

## Records per prime

| Path | Content |
|---|---|
| `records/pP/SLUG/result.json` | `incidence`, `certified_P2`, `family`, `jacobian_rank`, `points`, `grid_failures`, the three controls, `prime`, `root_of_minus_one`, the limit map and its determinant, the dPhi ranks, the target hits, `input_sha256` of the header |
| `records/pP/SLUG/details.json` | the first grid failures (none), every grid limit vector, the 100 target hits, the rank points, the replay Jacobians, the symbolic Jacobian |
| `logs/pP/` | every Singular log (`SLUG_phi`, `SLUG_limit`, `SLUG_ctl`, `SLUG_explore`, `SLUG_quot`, `model_colength`), `flip_check.log` and `certify_SLUG.log` (one line: `SLUG certified_P2 True rank 3 failures 0 hits 100`) |
| `sing/pP/` | the generated Singular scripts (`xarc_gen.py`) |
| `work/pP/` | the cleared numerators `gn_SLUG.txt` and the gcd `h_SLUG.txt` that the phi script writes |

`logs/` holds `.log` files that a global ignore pattern hides; `git add -f` records them.

## Commands

    PYTHON=python3 sh docs/evidence/a5-exceptional-fibers/arcs-x/replay.sh 32009
    PYTHON=python3 sh docs/evidence/a5-exceptional-fibers/arcs-x/replay.sh 32029

`replay.sh PRIME` finds the one directory `pPRIME-r*` of `../working/build/inputs/` that holds both headers and runs
`xarc_run.py`: it generates `sing/pPRIME/` (`xarc_gen.py`), runs the 11 Singular scripts through
`parallel.ordered_map` into `logs/pPRIME/`, writes `flip_check.log` (`xarc_flip.py`) and replays the series
certificate of each incidence (`xarc_certify.py`), which maps its Jacobian rank points, parameter points, grid and
target loops through `parallel.ordered_map` as well. A Singular step raises on a nonzero exit status, a timeout or a
`?` error line (Singular exits 0 after a failed statement). The wrapper sets `ulimit -v 8388608`,
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` and `GOROROBA_WORKERS=3`; the replay of one prime takes under
15 seconds. A rerun reproduces every log of `logs/pP/`, `sing/pP/` and `work/pP/` and every record of `records/pP/`.
The tests in `tests/test_a5_x_arc_certificates.py` replay the series certificate on grid points and the controls
from the retained logs without Singular.

## Limits and falsifiers

- A nonzero numerator of J(Phi) at either prime, a limit-map Jacobian of rank below 3 at a point with W != 0, a grid
  or target failure, or a control that passes would each refute the certificate for that pair.
- A relation f in L of degree d, that is a nonzero polynomial f with f(G) in m I^d, would refute F(I) = k[y1,y2,y3]
  in degree d; the truncated ranks of `../x-opposite-ladder/` are lower bounds of the Hilbert function and at their
  full value C(d+2, 2) for d = 5 to 9 allow no such f in those degrees.
- Two primes give evidence for characteristic 0 only; a specialization argument across primes would be needed.
- The global primary decomposition of I is not computed; the ideal-level check is local at the origin.
- The result concerns the fiber over the origin. Its relation to the 21-generator E8-bar fibers of `arcs/` is not
  addressed here.
