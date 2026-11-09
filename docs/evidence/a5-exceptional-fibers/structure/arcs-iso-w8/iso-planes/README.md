# Iso -> N-: linear planes over the base locus of the point blowup

Result. At p = 32009 and p = 32029 the point-blowup plane family of Iso -> N- sweeps a cone of dimension 5 inside
V(K2), and every plane lies in V(K2). The cone is the whole of V(K2) because V(K2) is irreducible of dimension 5, so
E0 = Proj F(I) contains V_+(K2); with K2 in L, E0 = V_+(K2), and with K2 radical and saturated, L = K2 and F(I) =
k[y]/K2 in every degree at both primes (steps 1 to 7 below). The route follows the W8 certificate
([../../c30-bounded/README.md](../../c30-bounded/README.md), ledger rows A5-066 and A5-236) and replaces its
two-generator slice by a one-generator slice. Marks: proved (a deduction from the stated inputs), computed (a script
result in `logs/`), measured (a retained log of an earlier run), hypothesis. The deduction of steps 1 to 7 is the
W8 deduction carried to Iso; the two W8 reviews do not cover this adaptation, and no reviewer has read the Iso steps
yet (hypothesis: they hold). The ledger rows A5-007 and A5-067 are not edited by this directory; the statement
"E0 = V(K2) at p = 32009 and p = 32029" is the ledger change that these records support once the steps are reviewed.

## Reduction: why the planes lie in E0

Notation. t2, ..., t7 are the coordinates of the Iso header `iso-nm.sing`; J = t2^2 + t4^2 - t5^2 - t6^2 + t7^2 is
free of t3, so V(J) is a quadric cone times the t3-axis and singular along that axis; G_1, ..., G_17 generate I (14 of
them have a nonzero degree-2 part, none a term of degree below 2: `logs/iso-control-emq-p*.result`); every one
vanishes on L0 = {t2 = 0, t4 = t6, t5 = t7}.

1. Point blowup [proved]. B = Bl_0 V(J) has the chart t3 = s, t_k = s u_k (k = 2, 4, 5, 6, 7). There J = s^2 J'(u)
   with J' = u2^2 + u4^2 - u5^2 - u6^2 + u7^2 and G_j = s^2 G'_j(s, u) (exact division, checked by every plane script:
   `not divisible by s^2 ... 0`), so I O_B = s^2 I'. B = {J' = 0} is smooth where dJ' is nonzero, which holds at
   p = (s, u) = (0, [0 : b : c : b : c]) for (b, c) different from (0, 0): dJ' = 2 (b v4 - c v5 - b v6 + c v7) in the
   local coordinates v2 = u2, v4 = u4 - b, v5 = u5 - c, v6 = u6 - b, v7 = u7 - c. B is singular along u = 0, which
   the points used avoid. The divisor {s = 0} is Cartier at p.
2. The fibers [proved]. The universal-property argument of W8 step 2 uses only that (s^2) is an invertible ideal
   sheaf near p: Bl_{I'} B = Bl_{I O_B} B factors through Bl_I V(J), the factor map is proper, birational and
   preserves the projective coordinate [G] = [G'], so the fiber of Bl_{I'} B over p maps into E0.
3. The slice [proved from the computed inputs]. Let B_3 = B cap {v6 = v7 = 0}, smooth of dimension 3 and transversal
   to P(L0) at p. F(I'_{B,p}) maps onto F(I'|B_3), so Proj F(I'|B_3) embeds in the fiber over p. The equations
   J' = G'_ia = 0 have an invertible Jacobian in (v4, v5) at p (the 2x2 Newton block, determinant nonzero: computed),
   so the formal implicit function theorem gives a unique solution (v4, v5) = x(s, v2) in k[[s, v2]]^2: the smooth
   surface S = {J' = G'_ia = 0} in B_3. Divisibility by v2 is exact: J and all 17 G_j vanish identically on L0
   (`logs/iso-l0-p*.result`, a polynomial identity in s, b, c: computed), the chart curve (s, v2 = v4 = v5 = 0) lies in
   {J' = G'_j = 0} for every (b, c) and solves the two Newton equations at v2 = 0, so x(s, 0) = 0 by uniqueness and
   G'_j|_S (s, 0) = 0. Newton iteration to order 10 computes the 2-jets of G'_j|_S exactly (computed), hence the exact
   1-jets of H_j = G'_j|_S / v2; their constant terms vanish and their linear parts have rank 2 in (s, v2) (computed:
   `I3 ... rank 2`), so by Nakayama (H_1, ..., H_17) = (s, v2). The linear parts of all G'_j on the tangent space of
   {J' = 0, v6 = v7 = 0} at p are multiples c_j1 of that of G'_ia (computed: `linear-part consistency
   failures 0`; this is the statement that dG' has rank 1 there, where W8 had rank 2). Writing x = G'_ia,
   G'_j = c_j1 x + x (Q_j - c_j1) + v2 H_j with Q_j - c_j1 in m, so G'_j = c_j1 x + v2 (alpha_j s + beta_j v2) modulo
   m I', and I'|B_3 = (x, v2 s, v2^2) in the coordinates (x, s, v2). The exponents (1,0,0), (0,1,1), (0,0,2) are
   affinely independent, so the products x^a (v2 s)^c (v2^2)^e with a + c + e = n are distinct monomials and a
   basis of I^n / m I^n, and the fiber cone is the polynomial ring k[Z1, Z2, Z3]. A recomputation of the minimal
   generators of (x, v2 s, v2^2)^n gives 3, 6, 10, 15, 21, 28 for n = 1 to 6 at both primes (computed:
   `logs/iso-k2-p*.result`).
4. The plane [proved]. The 17 x 3 matrix M(p) with rows (c_j1, alpha_j, beta_j) (row ia is the unit vector
   (1, 0, 0)) maps Proj k[Z] to a plane Pi_p = column space of M(p) in P^16, and Pi_p lies in E0. The column space is
   independent of the generator chosen as x: M(p) built on G'_9 and on G'_13 span the same 3-space (computed:
   `cross-check ... 3`; the check reads the `.M` file of the G'_9 run).
5. The family [proved from the computed rank]. M(p) is a rational function of (b, c) on the open set U of P(L0)
   where the Newton determinant and the linear coefficient of G'_ia are nonzero and the linear parts of the H_j have
   rank 2. Step 3 holds on all of U: the divisibility by v2 holds wherever the Newton determinant is nonzero, and the
   remaining inputs are closed conditions that hold identically in (b, c). The 18 x 3 matrix of linear coefficients
   of (dJ', dG'_1, ..., dG'_17) in (dv2, dv4, dv5) on the slice, with b and c as variables, has every one of its 816
   3 x 3 minors identically zero and 99 nonzero 2 x 2 minors (computed: `logs/iso-linear-p*.result`), so dG' has
   rank 1 on the tangent space of {J' = 0, v6 = v7 = 0} at every point of P(L0) with dJ' nonzero, and the constant
   terms of the H_j vanish at every point of U. The rank-2 condition on the linear parts of the H_j is open, and it
   holds at the points computed. The set T = closure of the union of
   the Pi_p over U is irreducible and lies in E0. Dual-number arithmetic over F_p[eps]/eps^2 gives dM/db and dM/dc;
   the matrix [M(p) | dM/db Y0 | dM/dc Y0] for a vector Y0 has rank 5 (computed, below). The map f(p, Z) = M(p) Z has
   differential of rank at most the dimension of the cone over T at a general point, and the rank is lower
   semicontinuous, so the affine cone over T has dimension at least 5.
6. The cone is V(K2) [proved from computed and recorded inputs]. T lies in V(K2) because E0 lies there (K2 lies in L,
   degree-2 receipts); the vanishing of the 68 quadrics of K2 on each computed plane is a control of the pipeline, not
   a premise. K2 is prime with affine dimension 5 and degree 23 (ledger rows A5-058 to A5-060; dimension and degree
   recomputed: `logs/iso-k2-p*.result`), so a closed irreducible cone of dimension at least 5 inside V(K2) is V(K2), and
   V_+(K2) lies in E0. E0 lies in V_+(K2), so E0 = V_+(K2) set-theoretically.
7. The ideal [proved]. K2 is radical (A5-058) and, k[y]/K2 being Cohen-Macaulay of positive dimension (A5-059),
   saturated; F_p is perfect, so K2 = I(V_+(K2)) over an algebraic closure, contracted back. E0 = V_+(L) contains
   V_+(K2), so L lies in I(V_+(K2)) = K2; with K2 in L, L = K2 and F(I) = k[y]/K2 in every degree, the analytic
   spread of I is 5 and e(F(I)) = 23. L need not be assumed radical.

## Computation

`iso_planes_gen.py` writes `points.json` and `sing/*.sing` from the Singular templates in `templates/`
(`--check` regenerates in memory and requires every file to match). `run.sh CASE [LIMIT_S]` runs one script under
`timeout`, an 8 GiB cap (a cgroup scope where a user bus answers, else `prlimit --as`; this host has no user bus, so
the cap was the address-space limit), keeps `logs/CASE.log`, `.result`, `.err`, `.time` (`/usr/bin/time -v`) and
`.rss`, and fails a run whose log carries a Singular error line. Singular 4.4.1 (44105; passagemath-singular 10.8.13 wheel) on the build host,
one process at a time, stdin from /dev/null, global ordering `dp` throughout; the dual-number truncation uses the
weight vectors of the C30 template. The header is `working/build/inputs/p<P>-r<I>/iso-nm.sing` (sha256 in each
script), K2 is `working/runs/s3/iso_k2.rel` at 32009 and `working/distribute/out/a5-p2-iso/iso_p2/d2/relations-d2.rel`
at 32029 (68 quadrics each), and the K2 files use the generator order of the run that wrote them, which differs
from the header by the signs of G_6..G_15 (`signs of the run generators`), applied as eps in every K2 evaluation.

| Case (`sing/CASE.sing`) | Question |
|---|---|
| `iso-l0-pP` | G and J vanish on the points (0, s, s b, s c, s b, s c) of L0, symbolically in s, b, c |
| `iso-linear-pP` | the 18 x 3 matrix of linear parts of J' and G' along P(L0) with b, c symbolic: 3 x 3 minors, 2 x 2 minors |
| `iso-k2-pP` | K2: 68 generators, affine dimension 5, degree 23; minimal generators of (x, v2 s, v2^2)^n |
| `iso-plane-pP-pt1` | plane over a QRNG point, smooth generator G'_9: all pipeline checks, K2 on Pi_p, rank 5 |
| `iso-plane-pP-pt1-ia13` | the same point with G'_13 as the smooth generator; reads `logs/iso-plane-pP-pt1.M`, so `pt1` runs first; column space equal to that of pt1 |
| `iso-plane-pP-pt2` | the same over the fixed point (b, c) = (17, 29), Y0 = (3, 5, 7) |
| `iso-control-emq-pP` | on control: the limits [G_2(u)] over the exceptional divisor J' = 0 |
| `iso-control-base-pP` | off control: the first-order fiber over a point of L0 away from the origin |

Randomness. The point of `pt1` and its vector Y0 take their values from `docs/evidence/anu_qrng/draw-2026-11-09T060635Z.json`,
the uint16 values in [1, 32008] at zero-based index 5 or above, in index order: b = 28176 (index 5), c = 1840
(index 7), Y0 = (11447, 3841, 7421) (indices 9, 10, 11); the off control takes s0 = 29214, b = 507, c = 9044 (indices 13,
14, 15). Indices 0 to 4 belong to `docs/evidence/quandela/permanent-estimators/permanent_probe.py`, and indices 6, 8
and 12 exceed 32008. The same integers serve both primes. `points.json` lists [index, value]; eight `reserved` rows
of `docs/evidence/qrng_seeds/allocations.json` register them. `ci/seed_provenance.py --check` reads each reserved row's path from the tracked tree; run against a copy of the
index that holds `points.json` it prints `439 seed literals accounted` and exits 0 (measured on the uncommitted
tree), and against the real index it reports only that `points.json` is not a tracked file. The fixed point (17, 29) and the on-control point
(a, c, d, t) = (3, 5, 7, 11) in the split coordinates a = u2 + i u4, c = u5 + i u6, d = u5 - i u6, t = u7 are hand
chosen: a rank at any point bounds the generic rank from below, so a hand-chosen point needs no draw.

## Results

Every plane script reports at all three points (`logs/*.result`), at both primes: J and G divisible by s^2 (0
failures); Newton residual 0; every G'_j|_S divisible by v2; no s term in a linear part of G'; linear-part
consistency failures 0; Newton block and the G'_ia linear coefficient nonzero; I3 = (s, v2) (constant terms 0, linear
rank 2); M(p) equal between the two dual directions.

| Prime | Case | Newton block, G'_ia coefficient | K2 nonzero on Pi_p | K2 nonzero on mutated plane | rank M | K2 Jacobian rank, tangent entries nonzero | rank [M, dM/db Y0, dM/dc Y0] | time, peak RSS |
|---|---|---|---|---|---|---|---|---|
| 32009 | pt1 (G'_9) | 2569, 8 | 0 of 68 | 31 | 3 | 12, 0 | 5 | 1.36 s, 18.6 MB |
| 32009 | pt1-ia13 | -2690, 7916 | 0 of 68 | 31 | 3 | 12, 0 | 5 | 0.70 s, 18.6 MB |
| 32009 | pt2 (17, 29) | -464, 8 | 0 of 68 | 31 | 3 | 12, 0 | 5 | 1.29 s, 18.7 MB |
| 32029 | pt1 (G'_9) | 2589, 8 | 0 of 68 | 32 | 3 | 12, 0 | 5 | 1.30 s, 18.7 MB |
| 32029 | pt1-ia13 | -2410, 10706 | 0 of 68 | 32 | 3 | 12, 0 | 5 | 0.72 s, 17.5 MB |
| 32029 | pt2 (17, 29) | -464, 8 | 0 of 68 | 32 | 3 | 12, 0 | 5 | 1.38 s, 18.7 MB |

Cross-check of the smooth generator, both primes: rank 3 from G'_9, rank 3 from G'_13, rank 3 side by side. The
point y0 = M(p) Y0 has 0 of 68 K2 generators nonzero, and the Jacobian of K2 at y0 has rank 12 = 17 - 5, a smooth
point of the 5-dimensional cone, against the five tangent vectors with zero entries: the tangent space of V(K2) at
y0 is the span of the five columns, an independent check of dM/db and dM/dc. Cost of the remaining cases: `iso-l0`
0.03 s, `iso-linear` 0.03 to 0.04 s, `iso-k2` 0.04 s, the controls 0.05 s each, all at 12.6 to 15.3 MB (`logs/*.time`).

Controls (both primes):

| Control | Expectation | Reading |
|---|---|---|
| on: the limits [G_2(u)] over J' = 0 at the point (3, 5, 7, 11) (`iso-control-emq-pP`) | rank 4 (the generic-direction arcs reach rank 4 of 5, [`../README.md`](../README.md)), in V(K2) | rank 4; K2 0 of 68 nonzero |
| off: the first-order fiber over the point (s0, 0, b, c, b, c) of L0 off the origin (`iso-control-base-pP`) | K2 does not vanish away from the origin | gradient rank 2; K2 nonzero 11 of 68 at 32009 and 8 of 68 at 32029 |
| mutation: one coordinate of M(p) shifted by one | K2 stops vanishing | 31 of 68 at 32009, 32 of 68 at 32029 |

The on control reproduces the rank-4 arc value with this code path's Jacobian method; the rank-5 plane family
therefore reaches beyond everything the arc scans reached. The off control and the mutation show that K2 vanishing
on Pi_p is specific to the fiber over the origin and to the computed M(p).

## Scope and falsifiers

- Fields. Exact over F_32009 and F_32029; the statements say nothing about characteristic 0. The characteristic-0
  transfer stays with the transfer tasks recorded in [`iso-saturation-trace.md`](../../../../../archive/reviews/a5-vb7-w8-char0/iso-saturation-trace.md).
- Points. One QRNG point and one fixed point per prime, rank 5 at each. The rank at one point bounds the generic
  rank from below, so T has affine dimension at least 5 as soon as one point reads 5; equality comes from T lying in
  V(K2). A further point of lower rank would lie on the rank-drop locus and falsifies nothing.
- Hypothesis. No reviewer has checked steps 3 to 7 for Iso. The W8 reviews found two insufficient sentences (the unit
  claim of step 2 and the truncation argument of step 4 there); this README carries the corrected forms.
- Falsifiers. (a) A plane that fails any K2 generator at a point where the pipeline reports success. (b) A rank of
  the swept family below 5 at every point of a larger sample: the route then stays silent, a statement that
  dim E0 >= 4 is not reached by these planes, not a refutation. (c) A fiber cone that is not a polynomial ring in
  three variables (a nonzero constant term or a linear-part rank below 2 in I3, a nonzero consistency count, or
  minimal-generator counts of (x, v2 s, v2^2)^n other than binomial(n + 2, 2)) refutes the model of step 3. (d) A J
  or G_j that fails to vanish on the chart curve of L0, or a vanishing Newton determinant at every point of P(L0).
  (e) A relation of L outside K2 in some degree (a membership failure in a degree-7 receipt) contradicts step 7.
- Not claimed. The ledger rows are unchanged; no characteristic-0 statement; no multiplicity computation beyond the
  degree 23 of K2 recomputed in `iso-k2-pP`.
- Records. The global gitignore excludes `*.log`; stage this directory with `git add -f` after
  `git ls-files --others --ignored --exclude-standard DIR` lists what was held back.
