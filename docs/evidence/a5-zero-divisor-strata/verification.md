# Independent verification of the A_5 zero-divisor strata claims

The object under test is commit 326da18 ("geometry/a5: exact rank-locus strata of the pathion zero-divisor set"),
with these sha256 digests:
- `scripts/a5_zero_divisor_strata.py`: b1bc9bfb7d9bdd2087a321b3e8d4f92d60bcf0028b2be003a33374114648493c;
- `docs/evidence/a5-zero-divisor-strata/README.md`: 898a9c37ae7ace9e3535744788b422651684da6892704ecf485ba16e9fe60b46;
- `docs/evidence/a5-zero-divisor-strata/result.json`: 5813f0d814cff8c819ebb94f3e5a37555e62e92b63fcd3fa3b5c7c5794b31d6c.

The retained `verification.json` comes from a rerun after review edits that pooled the author's equivariance and
anticommutation loops, fixed a docstring, and corrected the README's Theorem 4 multiplicity, its P3b covering argument,
scope and literature lines. `result.json` is byte-identical, and the rerun changed no verdict: only the double-cross
entry (now a symbolic identity) and the recorded verifier digest differ from the first run. Rerun digests:
- `scripts/a5_zero_divisor_strata.py`: 09fd6941e7945638d37e53d24f6d4cd7e49c45b724e313394091b2bee9f1b0d4;
- `docs/evidence/a5-zero-divisor-strata/README.md`: 07844db54b186b1194b7ef465dd8be1072993bc74958e6ac760132d960527adf;
- `docs/evidence/a5-zero-divisor-strata/result.json`: 5813f0d814cff8c819ebb94f3e5a37555e62e92b63fcd3fa3b5c7c5794b31d6c;
- `docs/evidence/a5-zero-divisor-strata/verify_strata_independent.py`: 19832b9d75f270d69eb6e6c44e04727f9567da2fbf34a591e139044a404c15d3 (also `verifier_sha256` in the JSON);
- `docs/evidence/a5-zero-divisor-strata/verification.json`: 4868225961525cd737368e7a1c04f06c9eb9bcccb400014127eee5e139a3d388.

[`verify_strata_independent.py`](verify_strata_independent.py) re-derives the claims of
[`scripts/a5_zero_divisor_strata.py`](../../../scripts/a5_zero_divisor_strata.py) and its [README](README.md) from
`gororoba_quantum/cd_core.py` alone and writes [`verification.json`](verification.json). It imports nothing from the
author's script. Every multiplication table comes from `left_mult_matrix_exact` and is checked against
`cd_multiply_exact`. Every nullity is the exact rank of the 32 x 32 rational matrix L_y. rank_C C_z is half the rank
of the realification [[A, -B], [B, A]], so the identity nullity = 28 - 2 rank C_z compares two independent
computations at every point. Tangent spaces are Zariski tangent spaces of the rank scheme R_k at a point with
rank C_z = r: {w : x^T C_w x' = 0 for x, x' in ker C_z}, the pull-back of the tangent space of the skew matrices of
rank at most r, which form a variety smooth at rank exactly r. Lower bounds on dimension are exact Jacobian ranks,
by forward-mode differentiation over Q(i), of explicit rational parametrizations. An image has dimension at least the
rank of the differential at any point. Piece membership uses the equations of the README table in original
coordinates (W8: mu = 0, U = V, W = 0; V: rank [u; v] <= 1, Q = 0; B9: mu = 0, U = V = W = 0, Im(u v) = 0;
N+-: mu = 0, v = +-i u, U = 0).

E8-bar has no equations in the README. The verifier uses the closed set Ehat = {Q = 0, Delta = 0,
rank [u; v; Im(u v)] <= 2}. Ehat contains every E8 point: the plane span(n, e) has Gram rank 1, and n x e is a
multiple of n when n lies in an eigenspace of e x -. So Ehat contains E8-bar. A nullity-8 point outside W8 u Ehat
refutes R_8 = W8 u E8-bar. E8i, Ehat restricted to 2-planes of Gram rank exactly 1, is the intrinsic E8 family. It
equals the README's E8 under the standard transitivity of G_2 on {e.e = -1} and of SL_3 on an eigenspace minus 0.

Randomness comes from two fresh ANU QRNG draws of 1024 uint16 values each,
`docs/evidence/anu_qrng/draw-2026-10-26T012526Z.json` (A) and `draw-2026-10-26T012529Z.json` (B). The script header
gives every index range, and each index is used once: A 0..119 for the Schwartz-Zippel points, A 120..139 for one
PCG64 seed per point family, A 240..254 for the self-test point, B 0 for the B9 curves, B 1..4 for the F_p samples and
B 5 for the float search.

Replay:

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHON=...   # the ci-py3.14.7 interpreter
"$PYTHON" -B -W error docs/evidence/a5-zero-divisor-strata/verify_strata_independent.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-zero-divisor-strata/verify_strata_independent.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-zero-divisor-strata/verify_strata_independent.py \
    --out docs/evidence/a5-zero-divisor-strata/verification.json
```

The first full run took 234 s wall clock on 12 workers (user 7 min 42 s) and the rerun 153 s, with Python 3.14.7, python-flint 0.9.0 and
numpy 2.5.4; `verification.json` records these versions under `versions`. Per stage:

| Stage | Seconds |
| --- | --- |
| F_p slices | 62 |
| float search | 57 |
| exhaustive integer search | 53 |
| F_p samples | 33 |
| point families | 20 |
| every other stage | under 4 each |

The stage times vary with machine load, which other sessions shared during these runs; earlier runs took 181 s and
221 s. Every CPU-bound loop runs through `parallel.ordered_map`. `ruff format --target-version py313`, `ruff check`
and `mypy` pass on the script.

The author's gates were re-run unchanged on commit 326da18:
- `--check docs/evidence/a5-zero-divisor-strata/result.json` exits 0 in 3.6 s;
- `--self-test` reports "13 mutations and corruptions rejected", both in normal mode and under `-O`.

`--self-test` of the verifier runs four mutation controls, and reports "4 of 4 mutation controls rejected" in normal
mode and under `-O`:
- a quartic Q^2 - 3 Delta in place of G fails the characteristic polynomial check;
- a W8 test with U = -V produces violations on the first 200 two-coordinate supports of the exhaustive search;
- an E8 family whose radical lies in neither eigenspace fails its family expectations;
- `rank_mod_p` returns wrong ranks on 2 x 2 controls.

The F_p stages rest on `rank_mod_p`. The `rank_crosscheck` stage compares it with `flint.nmod_mat` on the first 3000
F_11 points of P3a and of P4s with a = 1: 6000 matrices covering ranks 6, 8, 10 and 14. They agree on every matrix.

## Claim 1: the zero divisors are the doubly pure points with Q G = 0; nullity = 28 - 2 rank C_z; the relation C (C^2 + Q)(C^4 + 2 Q C^2 + G) = 0

**Verdict: confirmed.**

*Falsification criteria, stated before the runs.* Any one of these refutes the claim:
- J = L_(e_16) with J^2 != -I;
- an L_(e_k), k != 0, that is not skew;
- a k not in {0, 16} with J L_(e_k) + L_(e_k) J != 0;
- a QRNG point where the characteristic polynomial of C_z differs from l (l^2 + Q)^3 (l^4 + 2 Q l^2 + G)^2, where the
  degree-7 relation is a nonzero matrix, or where det of a 14 x 14 principal minor is not +-(Q G z_j)^2 with a sign
  fixed per j;
- any point whose nullity differs from 28 - 2 rank C_z;
- a point with nullity >= 4 and Q G != 0, or the reverse.

*Computation and output.*
- `tables`: all three operator identities hold. The octonion and sedenion tables equal `cd_multiply_exact` on every
  basis pair, and distinct octonion imaginary units anticommute. With L_y = y_0 + y_16 J + L_d, these give L_y^T L_y = (y_0^2 + y_16^2) I + L_d^T L_d, which is
  positive definite when (y_0, y_16) != 0. The README proof of Theorem 1 is therefore reproduced from the table.
- `identities`: at 8 integer points z in [0, 65535]^15 (QRNG A 0..119) the characteristic polynomial and the
  degree-7 relation hold exactly. All 15 cofactor identities hold with sign +1 at every point: det(C_z without row
  and column j) = (Q G z_j)^2. Each identity is a polynomial identity over Z of degree at most 15. By Schwartz-Zippel
  a false one survives 8 independent uniform points with probability at most (15/65536)^8, about 8e-30. The
  cofactor identity gives rank C_z <= 12 exactly when Q G = 0 for z != 0.
- The nullity identity held at every point the verifier touched: 472,760 exhaustive integer points (all four
  nullities 4, 8, 12, 16 occur), 126 random family points and the 29 registry witnesses. Nullity 4 occurred exactly
  where Q G = 0. These points also include 1.6 M F_p points under the equivalent criterion rank <= 12 iff Q G = 0.
  None violated either criterion.
- No z != 0 has rank C_z <= 4, so nullity 20 and above never occurs. No exhaustive point had nullity >= 20, no F_p
  point had rank below 6, and none of 150 float starts converged to rank 4.

The nullity identity itself is checked pointwise. Its general proof is the README lemma together with the imported
transport rank_R L_y = 2 rank_C A(z, conj z) of gate core-690. I read the lemma and found it sound; I did not
re-derive the transport.

## Claim 2: Q and G are absolutely irreducible, complex dimension 14, unit dimension 27

**Verdict: confirmed.**

*Falsification criteria.* Any one refutes the claim:
- a Hessian of Q with rank below 3;
- G reducible over Q;
- no smooth rational zero of G in coordinates with rational coefficients;
- a random point of V(Q) or V(G) where the tangent dimension of R_4 is not 14.

*Computation and output (`g_irreducibility`, `split_consistency`, families).*
- The substitution z_k = i^popcount(k) z'_k is computed from cd_core, not taken from the README. It makes
  D C_z D = M(z') a skew integer matrix, with D = diag(i^popcount). Under it, Q, Delta and Im(u v) agree with the
  README's split forms.
- G in split coordinates has rational coefficients and 141 terms, and `fmpq_mpoly.factor` returns it irreducible
  over Q.
- G has the smooth rational zero u' = e'_1, mu' = 4, v' = 5 e'_1 + 2 e'_3, where G = 0 with nonzero gradient. This
  point is not the README's (whose v' is 5 e'_1 + 3 e'_3 with mu' = 3).
- The README's Galois argument then gives absolute irreducibility, and I checked that argument. A Q-irreducible
  polynomial with a smooth Q-point has exactly one geometric factor through that point; that factor is
  Galois-stable, so it is G.
- Q = sum z_k^2 has Hessian 2 I of rank 15.
- At 6 + 6 random points of V(Q) and V(G) the tangent dimension is 14, equal to the parametrization rank 14. Both
  are hypersurfaces of C^15, so the unit dimension is 2 x 14 - 1 = 27.

## Claim 3: nullity 16 = N+ u N- (6, 11 each); nullity 12 = V (8, 15) u B9 (9, 17) meeting in (7, 13); nullity 8 = W8 (12, 23) u E8-bar (11, 21)

**Verdict: confirmed, with one part resting on the author's certificates.** The dimensions and the non-redundancy of
the pieces are proved here at exact points. The covering, that R_k lies in the union of the pieces, survived four
independent exact searches and one float search. Its proof remains the author's: the slice Groebner certificate,
which re-runs green, together with the G_2 orbit facts F1 to F4. I checked the slice tables by exhaustive enumeration
over F_11 and F_13 and did not re-derive them over Q.

*Falsification criteria for dimension and non-redundancy.* Any one refutes the claim:
- at a random point of a piece, the tangent dimension of R_k differs from the claimed dimension;
- the parametrization rank (a lower bound) differs from the claimed dimension;
- a piece's random point has a nullity other than the claimed one, or lies in another piece of the same stratum.

Equal tangent dimension and lower bound at a point p prove two things: the piece has that dimension, and it is the
only irreducible component of R_k through p. The second fact excludes containment in any other piece.

| Piece (QRNG seed index) | points | nullity | tangent dim of R_k | parametrization rank | outcome |
| --- | --- | --- | --- | --- | --- |
| N+ (A 133), N- (A 134) | 6 + 6 | 16 | 6 | 6 | dim 6, unit 11 |
| V, mu != 0 (A 128) | 8 | 12 | 8 | 8 | dim 8, unit 15; outside B9 |
| B9 (A 129) | 8 | 12 | 9 | 9 | dim 9, unit 17; outside V |
| V n B9 (A 130) | 6 | 12 | 11 (singular: two components) | 7 | dim 7, unit 13 |
| W8 hyperbolic (A 125) | 12 | 8 | 12 | 12 | dim 12, unit 23 |
| W8 generic isotropic (A 126) | 12 | 8 | 12 | | regular point of R_8 |
| E8, mu != 0 (A 127) | 8 | 8 | 11 | 11 | dim 11, unit 21; outside W8 |

The parametrization rank is the maximum over the family's points. One of the 12 W8 hyperbolic points sits at a
degenerate parameter value with rank 8; the other 11 have rank 12.

The upper bound dim (V n B9) <= 7 comes from counting. A point of V n B9 has mu = 0, a dependent pair u, v in span(w)
and U = V = 0, so w is null. The intersection is therefore the image of (null cone, dimension 6) x C^2 under
(w, alpha, beta) -> (alpha w, 0, beta w), whose fibers have dimension 1, so its dimension is 6 + 2 - 1 = 7.

*Falsification criteria for the covering.* A point of nullity >= 8 outside W8 u Ehat, of nullity >= 12 outside
V u B9, or of nullity >= 16 outside N+ u N- refutes the claim. So does the reverse failure: a point of W8, E8i, V,
B9 or N+- below the claimed nullity.

- **Exhaustive integer search** (`exhaustive`): all 472,760 doubly pure y in {-1, 0, 1}^30 with support at most 4
  gave 0 violations. Counts by nullity: 274,520 have nullity 0, 129,360 nullity 4, 52,080 nullity 8, 16,464 nullity
  12 and 336 nullity 16.
  - Of the nullity-8 points, 46,704 lie in W8, and every one of the other 5,376 lies in E8i.
  - Of the nullity-12 points, 7,392 lie in V only, 1,344 in B9 only and 7,728 in both.
  - The nullity-16 points split 168 in N+ and 168 in N-.
- **Registry witnesses** (`witnesses`): all 29 rational witnesses of `docs/evidence/rank_locus_local_dimension`
  reproduce their recorded nullity and fall in the claimed pieces, with 0 violations. The zd-zd-generic witnesses
  lie in W8 with tangent dimension 12, the zd-nonzd-locus witnesses in E8i with 11, and the zd-zd-locus witnesses in
  B9 with 9. The nonzd-axis and Proposition 8.2 witnesses lie in V with 8, and the zd-axis witnesses in N+ with 6.
- **Exhaustive F_p slices** (`fp_slices`): every F_p point of the six README slices P2, P3a, P3b, P3c, P4s and P4g
  (p^5 - 1 nonzero points each, for p = 11 and p = 13; 3.19 M points) was ranked mod p and classified.
  - The README slice table holds exactly. Rank <= 10, <= 8 and <= 6 coincide with the claimed varieties at every
    point, with 0 mismatches at each order.
  - The global criteria above also hold, with 0 violations.
  - Using 11 (3 mod 4) and 13 (1 mod 4) covers components defined over Q(i). P2 has no N+- points over F_11, where
    -1 is not a square, and 48 over F_13. Both agree with the table.
- **Full-space F_p samples** (`fp_samples`): 800,000 uniform points of F_7^15 and 800,000 of F_13^15 gave 0
  violations.
  - Over F_7: 2,734 points of rank <= 10, of which 309 lie in E8i, and 7 of rank <= 8.
  - Over F_13: 394 points of rank <= 10, of which 19 lie in E8i.
  - Every rank-<=10 point lies in W8, E8i, V or B9. No point of Ehat has rank above 10.
- **Float search** (`float_search`, corroboration only): alternating projections onto rank <= r inside {C_z}, from
  150 QRNG-seeded starts per target, all in general position. Every converged point lies in the claimed pieces.
  - Rank <= 10: 140 starts converged, 74 into W8 and 66 into Ehat outside W8.
  - Rank <= 8: 121 converged, 101 into B9 and 20 into V.
  - Rank <= 6: 149 converged, all into N+-.
  - Rank <= 4: none converged.

## Claim 4: incidences

**Verdict: confirmed.**

*Falsification criteria.* Any one refutes the claim:
- a B9 or N point that fails the W8, V or B9 equations it should satisfy;
- a V point that is not an E8 point;
- a random B9 point that is not a limit of E8 points;
- a W8 point with G != 0;
- a hyperbolic W8 point with Q = 0;
- an E8, V or B9 point with Q != 0 or G != 0.

*Computation and output.*
- **B9 < W8 and N+- < V n B9.** The equations imply each other algebraically. The family rows confirm it at random
  points: every B9 point is also in W8, and every N+- point is in V, B9 and W8.
- **V < E8-bar.** A V point (alpha w, mu, beta w) with w.w != 0 is the E8 point with a = c = 0 and
  e = w / sqrt(-w.w), directly from the family's definition. All 8 V points lie in Ehat.
- **B9 < E8-bar.** The verifier builds its own curves (`b9_curves`, seed B 0), not the README's. It takes a random
  special plane span(n, k), with n null and k = n x y, y perp n, so n x k = 0. It solves the linear system e0 perp
  n, k with Im(e0 n) = n. It chooses beta^2 + delta^2 = -e0.e0 through beta + i delta = A and m = e0.e0, which
  makes Q vanish identically.
  - The curve is z(s) = (alpha n + beta (k + s e0), m s, gamma n + delta (k + s e0)).
  - For s = 1..8 the point has rank C <= 10 and lies in E8i outside W8. Since C is linear in s, every order-12
    Pfaffian has degree at most 6 in s, so 8 values make the rank bound hold identically.
  - At s = 0 the point is a B9 point outside V, with nullity 12 and tangent dimension 9. B9 is smooth of dimension 9
    there.
  - All 8 random endpoints pass. The endpoints come from a Zariski-dense family in B9, and E8-bar is closed, so B9
    lies in E8-bar.
- **Memberships.**
  - At mu = 0, G = (U - V)^2 + 4 W^2 holds identically, so W8 lies in V(G). Q = 2U = x.w is nonzero at all 12
    hyperbolic points, so W8 does not lie in V(Q).
  - E8, V and B9 points have Q = G = 0 at every random point and every witness.
  - Algebraically, Q = 0 by definition on these pieces, and Delta vanishes on planes of Gram rank at most 1, so
    G = Q^2 - 4 Delta = 0.

## Claim 5: connected components: nullity 4 connected, 8 two, 12 connected, 16 two

**Verdict: confirmed, given claim 3.** The counts follow from the decomposition through the standard facts the
README uses: an irreducible complex cone minus a proper closed subset is connected, and S_k and D_(5,k) have the
same components.

*Falsification criteria.* Any one refutes the claim:
- no nullity-4 point on V(Q) n V(G);
- a point of W8 minus R_12 inside E8-bar;
- no nullity-12 point on V n B9;
- a nonzero point of N+ n N-, or a nonzero point of rank <= 4.

*Computation and output.*
- **k = 4.** The family "V(Q) n V(G), Gram rank 1 unaligned" (A 123) is u = X f_1, v = Y f_1 + c n, mu = i M, with
  X^2 + Y^2 = M^2 and n null, perpendicular to f_1 and not in an eigenspace of f_1 x -. All 6 of its points have
  Q = G = 0 and nullity exactly 4, and they lie outside Ehat and W8. V(Q) minus R_8 and V(G) minus R_8 therefore
  meet.
- **k = 8.** Here the verifier gives an argument that needs no orbit classification and so is stronger than the
  README's. Write x = u - i v and w = u + i v. W8 is {mu = 0, x and w null}. A point of W8 minus R_12 has one of
  two forms:
  - x.w != 0. Then Q = x.w != 0, so the point is outside V(Q), which contains Ehat, which contains E8-bar.
  - x.w = 0, with x and w spanning an isotropic plane where x x w != 0. Dependent pairs lie in V n B9 and N+-, and
    x x w = 0 is B9; all of these are in R_12.

  The cd_core identity x x (x x w) = (x.w) x - (x.x) w (`double_cross`, a symbolic expansion over Z[x_1..x_7, w_1..w_7]) and the
  anticommutativity of the cross product (`tables`) show that on an isotropic plane x x w lies in span(x, w) only
  when x x w = 0. Since u x v = -(i/2) x x w, generic isotropic pairs
  lie outside Ehat. So W8 minus R_12 misses E8-bar, and the two parts of S_8 are disjoint.

  As a second route, the 12 random generic isotropic W8 points (A 126) all have tangent dimension 12, the regularity
  that the README's argument uses. They also lie outside Ehat.
- **k = 12.** All 6 V n B9 points (A 130) have nullity exactly 12, so V minus R_16 and B9 minus R_16 meet.
- **k = 16.** v = i u and v = -i u force u = v = 0, so N+ and N- meet only at 0. Rank <= 4 occurs at no nonzero
  point: the exhaustive search, the F_p samples and the float search all found none.

## Claim 6: the "+2" of the two-dimension gap is the complex coordinate mu = (y_8, y_24)

**Verdict: confirmed.**

*Falsification criteria.* Any one refutes the claim:
- mu != y_8 + i y_24 in the code's coordinates;
- a point of V, E8-bar, V(G) or V(Q) on {mu = 0} where the mu-direction is outside the tangent space of R_k, or
  where dim (T n {mu = 0}) != dim T - 1;
- a family of piece n {mu = 0} whose dimension is not dim P - 1;
- a registry witness that does not fit.

*Computation and output.* mu = z_8 = y_8 + i y_24 by the coordinate map. The table gives complex dimensions; unit =
2 x complex - 1.

| Points on {mu = 0} | tangent T of R_k | mu-direction in T | dim T n {mu = 0} | family rank | unit dim of P n {mu = 0} |
| --- | --- | --- | --- | --- | --- |
| {a,0} axis of V (A 131, 132) | 8 | yes | 7 | 7 | 13 |
| E8 n {mu = 0} (A 137) | 11 | yes | 10 | 10 | 19 |
| V(G) n {mu = 0} (A 138) | 14 | yes | 13 | 13 | 25 |
| V(Q) n {mu = 0} (A 139) | 14 | yes | 13 | 13 | 25 |

At the registry witnesses the same holds for the four gap families:
- nonzd-axis (1, 8, 15): T = 8, T n {mu = 0} = 7;
- zd-nonzd-locus (4, 11, 18): T = 11, 10;
- zd-nonzd-generic (5, 12, 19): T = 14, 13;
- nonzd-nonzd-locus (6, 13, 20): T = 14, 13.

These give unit tangent bounds 15, 21, 27, 27 and family dimensions 13, 19, 25, 25. Those are the
`dimension_upper_bound` and `dimension` fields of `rank_locus_local_dimension/result.json`, and the cone dimensions
16, 22, 28, 28 of the gap record. The three families without a gap fit the same explanation:
- zd-axis: N+, inside {mu = 0}, T = 6, family dimension 11;
- zd-zd-locus: B9, inside {mu = 0}, T = 9, family dimension 17;
- zd-zd-generic: W8, inside {mu = 0}, T = 12, family dimension 23.

Their pieces lie inside {mu = 0}, the mu-direction is not in T, and the unit dimension equals the family dimension.

## Defects and gaps in the author's script and README

No mathematical claim was refuted. These are places where the record asserts rather than computes, or where the
proof leans on more than the code certifies:

1. `topology()` in `scripts/a5_zero_divisor_strata.py` sets `intersection_V_B9["complex"]` to the literal 7. It
   records the representative's orbit-family rank as `lower_bound_rank` but never requires it to equal 7. The upper
   bound ("the same upper bound from the parametrization", README Theorem 6) has no code. The counting argument
   above supplies it.
2. `PIECE_DIMENSIONS` is a table of literals. Representative checks guard it: lower == upper == literal for W8, E8,
   B9, V and N. VQ and VG get only a tangent-dimension-14 check.
3. Every `connected_components` value (1, 2, 1, 2) and its `why` field is a literal. The code checks the supporting
   facts (the meeting points, the W8 regularity at two representatives, the `plane_table` numbers) but computes no
   component count.
4. README Theorem 8 rests k = 8 disjointness on F4 and the full gl_2 action: W8 minus R_12 being two orbit types,
   with regularity checked at one representative of each. A simpler argument exists that needs no orbit claim. The
   hyperbolic type has Q != 0, so it misses E8-bar, which lies in V(Q). The isotropic type misses Ehat, which
   contains E8-bar, by the double-cross identity. The README could state that.
5. The README defines E8-bar only as a closure and gives no equations. The verifier's Ehat contained every
   nullity-8 point outside W8 that any search found. No Ehat point had nullity below 8 in 3.19 M slice points and
   1.6 M sample points over F_p. This suggests R_8 = W8 u Ehat, a closed-form description the record could adopt
   after its own proof; that statement is an observation, not checked over Q.
6. Theorem 2's nullity identity imports the transport of gate core-690. The record verifies it at 14
   representatives, and this verifier at about 473,000 points, but neither re-proves it.

## Scope

- Not run: a re-derivation of the slice Pfaffian varieties over Q. The F_p enumeration replaces it as an exhaustive
  check at two good primes.
- Not checked: the G_2 orbit facts F1 to F4, which this verifier uses only to identify E8i with the README's E8 and
  to cite Lemma 5. Each fact is standard; the author's certificates cover them and re-ran green.
- The two QRNG draw files are `owned` rows of `docs/evidence/qrng_seeds/allocations.json`: the script holds no seed
  literals and reads its values from the draw files by runtime index, so no other row may take one of their indices.
