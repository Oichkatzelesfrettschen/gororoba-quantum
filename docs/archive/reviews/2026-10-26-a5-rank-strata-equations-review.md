# Adversarial review: a5-rank-strata-equations (commit 7aac2ee)

Scope: `docs/evidence/a5-rank-strata-equations/{README.md, rederive_strata_equations.py, result.json}` against the strata
record and `gororoba_quantum/cd_core.py`. Scratch artifacts for every check below are in `docs/local/rev/`.

Verdict: nothing refutes Lemma A, Theorem B or Theorem C. Every Singular check decides what the README says, with one
exception: the "Q and G lie in the Ehat ideal" check holds by construction. The findings are robustness gaps and
wording.

## Issues

1. **Claim (computation 6): "Q and G lie in the Ehat ideal."** The check cannot fail. Q and Delta are generators of
   Ehat, and G = Q^2 - 4 Delta, so `inideal(QG, E)` is 1 by construction and is evidence of nothing. Severity: wording.
   Drop it, or state it as a tautology.
2. **Claim (computation 3, F4): "H acts on L / n0 through traceless matrices of rank 3, which is sl_2."** The script
   subtracts the trace before it takes the rank (`mats.append([m2[0][0] - tr, ...])`). The computation therefore
   shows that the image of H in pgl(L / n0) is all of pgl_2. That is what transitivity on P(L / n0) needs, but it is
   not the statement printed. Severity: wording.
3. **`isotropic_plane_job` ignores Singular errors.** Its `pass` reads only `forms_in_radical == "1"` and never checks
   `singular_error`; slice_job and global_pass do check it. Singular 4.4.1 also keeps running after an error and exits
   with code 0: a test script printed `RESULT after 1` after a `? ... not defined` error, and run_singular captured
   both. Error detection therefore rests only on the `? ` substring, and only in the jobs that consult it. The
   retained run shows no error: the dumped `iso` stdout is clean. Severity: robustness gap. It does not affect
   result.json.
4. **Global "in_radical" for the order 12/10/8 Pfaffians.** When ideal membership holds, the script prints the literal
   `RESULT in_radical_X 1` instead of computing a radical. This is logically valid (ideal membership implies radical
   membership), and every row of result.json has `in_ideal_* = 1`. But the record reports `in_radical_*` values that
   no radical computation produced. Severity: wording.
5. **Claim (Delta redundant): "If u', v' are independent and u' ^ v' lies in their span ... eta(u' ^ v') = 0".** The
   dependent case is omitted. It is trivial (u' ^ v' = 0 and the Gram determinant is 0), but the sentence states
   only half the argument for "Delta is redundant set-theoretically". Severity: wording.
6. **Title and statement 3: "covering over Q" and "Pfaffians of C_z ... over Q".** The ideals live in split
   coordinates. Pfaffians of C_z in original coordinates have Gaussian-integer coefficients and equal unit multiples
   of the Pfaffians of M(z'). The covering is a statement over C. Severity: wording.
7. **No self-test control exercises `R_in_union` failing.** All eight mutations target `piece_in_R`, saturation,
   isotropy or lifts. I added the missing control: see Confirmed, item 4. It discriminates. Severity: gap in the
   self-test, now closed by this review and not by the record.

No refuting defect was found.

## Confirmed, and how

1. **Replay.** `--out docs/local/rev/rerun.json` passes every part in 31 s. It is identical to result.json once
   `seconds`, `timings_s`, `total_s` and `workers` are removed. The script sha256 matches the record (67d6aba0...).
   `--self-test` passes 8 of 8 in normal mode and 8 of 8 under `-O`.
2. **Generated Singular text** (dumped by instrumenting run_singular: `docs/local/rev/ehat_1.sing`, `slice_1.sing`,
   `iso_1.*`).
   - `sat(E, f)` returns type `ideal` in Singular 4.4.1, checked on a toy ideal: sat((x^2 y, x y^2), x) = (y). It is
     not the older list return.
   - The direction is right: S reduced mod std(E) is 0, so S lies in E.
   - `inrad` is `reduce(f, std(radical(I)))`, which decides f in rad I.
   - `R_in_union` is intersect(A0, A1) inside rad P, which decides V(P) inside V(A0) u V(A1).
   - An empty ideal becomes `0` and does not pass vacuously: rad(0) = 0, so a nonzero P fails.
   - stdout and stderr were clean in all dumped runs.
3. **Split coordinates and M(z').**
   - By hand: u.u = eta(u'), v.v = -eta(v'), u.v = i eta(u', v'), z_8 = i mu', and N_+ is v' = u' in split
     coordinates. So every piece is defined by eta, the cross product and mu', and is G_2-stable.
   - Q on P3a is d^2 - b^2 - m^2, as recorded.
   - M = D C_(Dz') D is skew, and its rank equals rank C_z.
   - Pfaffians: at a random integer z' I computed my own recursive Pfaffians of M over all index sets of orders 8
     and 10. As sets of absolute values they equal the values of the script's 6435 and 3003 Pfaffians
     (`pfcmp.py`), and Pf^2 = det at orders 8, 10 and 12.
4. **Covering discriminates.** I replaced `intersect(A0, A1)` with a single piece (`ctl.py`).
   - P2 at order 12: W8 alone gives 0 and Ehat alone gives 0. Both components (dimensions 2 and 3) are needed.
   - P4s at order 8: N_+ alone and N_- alone both give 0.
   - P3a at order 12 passes with Ehat alone, and P4g at order 12 passes with W8 alone. Both are consistent with the
     strata record's slice table.
5. **Independent points (`indep.py`, 6 seeds, 36 points).** The points are built in original coordinates from
   cd_core.cd_multiply_exact over Gaussian rationals and use none of the script's functions.
   - Construction: e = i r with r a random rational unit vector, so e.e = -1. Then n = w +- e ^ w for random w
     perpendicular to e, u = a n + b e, v = c n + d e, and mu^2 = b^2 + d^2 for Q = 0.
   - E8 points (eigenvalue +1 and -1): Q = Delta = 0, rank [u; v; u ^ v] = 2, and rank C_z = 10 over Q(i) (by
     realifying to 30 x 30). The nullity of the 32 x 32 L_y from cd_core is 8. None of the points is in W8.
   - All 37 generators of the generated Singular text (E.txt), evaluated at z' = D^-1 z, vanish at every E8 point.
   - Negative controls:
     - the same points with Q != 0 give rank C_z = 14 and nullity 0, and the generators do not vanish;
     - Gram-rank-1 planes with a mixed (P3c-type) null radical and Q = 0 give rank [u; v; u ^ v] = 3, rank C_z = 12
       and nullity 4, so they lie in V(Q, Delta) but outside Ehat and outside R_8.
   - These controls show that the minors condition is necessary and that Ehat is strictly smaller than V(Q, G).
   - nullity L_y = 28 - 2 rank C_z held at all 36 points, which spot-checks the imported Theorem 2.
6. **Degree 24, by a separate route.** E plus 10 random homogeneous linear forms plus one random affine form (`lin_p`,
   char 32003) gives a zero-dimensional ideal with vdim 24 and vdim of its radical 24. The section is therefore 24
   reduced points, which corroborates deg P(E8-bar) = 24 and generic reducedness. In char 32003, std(E) also has dimension 11 and
   multiplicity 24. Over Q (`lin_q`), vdim J = 24. The radical of the section over Q was not run to completion: I
   killed it after about 15 minutes to stay within the shared-host limit, and the result in char 32003 stands in for
   it.
7. **Saturation without `sat`** (`quot_q`, over Q). quotient(E, f) and quotient(E, z8) both reduce to 0 mod std(E).
   So f is a nonzerodivisor mod E, which implies E : f^infinity = E by a second code path.
8. **Proof steps read and accepted.**
   - Lemma A's case split is exhaustive: P has dimension 0, 1 or 2, and each case is taken at every Gram rank.
   - F1: tangent e-perp at a point with eta(e) != 0.
   - F2: SL_3 is transitive on {xi(x) = c}, c != 0, and on {xi(x) = 0, x != 0, xi != 0} for n = 3.
   - F3: the null cone minus 0 is irreducible of dimension 6.
   - F4: the tangent of the plane orbit is rank [h x, n0, x] - 2, because H fixes n0. Rank >= 5 off L gives an
     open orbit in the smooth quadric threefold minus a line.
   - Theorem C step 2:
     - Gram rank 0 is excluded by Q = -mu'^2 != 0;
     - beta = 0 from eta(n ^ e, e) = 0;
     - n ^ e != 0 and alpha^2 = 1 from e ^ (e ^ n) = n;
     - the reflection g e'_1 = -e'_1 swaps V_+ and V_-;
     - the identity signs match the script output (alpha, beta) = (1, -1) and Lagrange sign +1.
   - Steps 3 to 5: V(I : f^inf) = closure(V(I) minus V(f)), and V(E) is irreducible of dimension 11. A Jacobian
     rank of 4 at a point of V(E) then makes the local ring regular, so E is reduced at the generic point, and
     mult(SE) = 24 is the degree.

## Not run

- **Radicality of the full Ehat ideal, and minAssGTZ(E) over 15 variables.** Not run. The README declares radicality
  out of scope, and both computations are expensive on the shared host.
- **Global covering by sampling random points of R_8.** Not run: no sampler for R_8 exists independent of the
  covering argument. Lemma A carries that direction, and I accepted it on reading.
- **Irreducibility of W8, V, B9 and N_+-.** Not run. The record inherits it from the strata record.

## Disposition

The scratch files under `docs/local/rev/` were not retained. The commit after 7aac2ee answers each issue:

1. The `inideal(QG, E)` check and its README line are removed.
2. F4 now reads: the trace-free parts span dimension 3, so the image of H in pgl(L / n0) is all of pgl_2.
3. `isotropic_plane_job` fails on `singular_error`.
4. The global jobs print `in_radical_*` only where they computed a radical; the pass reads ideal membership or a
   computed radical.
5. The Delta-redundancy argument covers the dependent case.
6. The title no longer says "over Q", and statement 3 names the split coordinates and the extension to C.
7. A ninth self-test control drops Ehat from the P2 order-12 union, and `R_in_union` must then be 0.

The section-degree corroboration (24 reduced points modulo 32003) is cited in Theorem C.
