# Arc-family support certificate: E8bar -> VB over F_32009

Scope: step 2 of section 10 of `docs/local/a5-failed-runs/decision-record.md`. All files are in `build/arc/`. Software: Singular 4.4.1, Sage 10.10 (series arithmetic and exact linear algebra over F_p, F_p(u); python-flint not used). Every job ran in `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` with `timeout -k 10 1800` and `MALLOC_ARENA_MAX=2`, one at a time. No seeds were drawn; all test points are fixed small integers.

## Verdicts

| Prime of sqrt(K2) | Dimension, degree | Verdict over F_32009 |
| --- | --- | --- |
| P2 (`primeP2.txt`, 9 minimal generators) | 3, 4 | support-certified: both Hensel branches land exactly in V(P2) (all 9 generators vanish identically in u1,u2,k), exact generic Jacobian rank 3 over F_p(u1,u2,k), so the family is dominant onto V(P2) |
| P1 (`primeP1.txt`, 7 minimal generators) | 3, 3 | not certified. Falsifier fired: every arc family built (both branches, charts t1=1 and t3=1, 24 numeric points plus the exact family) has all 7 generators nonvanishing on the leading vector F(u); the family lies in V(P2) only. A failed ansatz does not show P1 is absent from the fiber, and K2 is only an upper bound for the fiber, so P1 may also be spurious |

Geometric irreducibility: P2 is geometrically irreducible, because V(P2) is the closure of the image of the rational parametrization (u1,u2,k) -> F (A^3 is geometrically irreducible and the map is dominant, rank 3). P1 is geometrically irreducible, because it equals the 2x2 minors of [[y3, z6, y8],[z6, y7, y9]] with z6 = y6 - 2562*y10 (checked by hand against the three quadrics; modulo the four linear generators), the rank-1 locus parametrized by (mu1, lam, mu3, y10) with y3=mu1, z6=lam*mu1, y7=lam^2*mu1, y8=mu3, y9=lam*mu3. Singular's `absPrimdecGTZ` refuses characteristic p (`s5.log`), so no absFactorize output exists.

## Step 1: minimal primes (`s1_primes.sing`, `s1.log`)

`minAssChar` of std(radical(K2)) returns two primes in seconds: prime 1 has dim 3, degree 3, 7 generators; prime 2 has dim 3, degree 4, 12 elements of its std basis (9 minimal generators in `primeP2.txt`: y7, y4+y6, y3, six quadrics). They match `runs/k2struct/e8vb.log`.

## Step 2: tangent cone by deformation to the normal cone (`s2_tc.sing`, `s2d.sing`, `cone.txt`)

Substituting t -> h t in J (17 generators) and taking `sat(J, h)` gives 27 generators, dimension 5 (the family) with fiber at h=0 of dimension 4 and degree 2. No local ordering was used. The cone is not reduced: its radical is the linear space L = V(t2, t8, t5-t6, t3+t4), multiplicity 2. G has 10 generators of lowest degree 1 or 2.

Consequence: at every point of P(L) the strict transform has Jacobian rank 3, not 4 (checked at three points in chart t1=1, `explore.sage`). The order-1 Newton-Hensel ansatz on the strict transform therefore fails with det M = 0 on the chart tried (t1=1); chart t3=1 gives the same obstruction because the cone is the same doubled L. The strict transform is singular along P(L).

## Step 3: arcs on the normalization

Correction to the ansatz: the arcs are built on the normalization of the strict transform. Singular `normal` (`s4b.sing`, `s4c3.sing`; ideals `norid.txt`, `c3/norid.txt`) adds 12 variables T(i) in chart t1=1 (10 in chart t3=1); the result has dimension 4. Over each F_p-point of P(L) the normalization has 2 points (a node), both with Jacobian rank 16 = 20 - 4, hence smooth with h (= s) a free coordinate: the arcs have order 1 in s on the normalization. Free coordinates: (t3,t5,t7) = (u1,u2,u3) and s; dependent: T(1..12), t2, t4, t6, t8 (16). 16 of the 303 relations with an invertible 16x16 Jacobian were selected by greedy rank (`sel.pkl`).

Hensel argument: V of the 16 selected relations is smooth of dimension 4 at the base point because their Jacobian in the 16 dependent coordinates is invertible; it contains the 4-dimensional irreducible germ of the normalization, so the two germs coincide. By Hensel's lemma the formal solution t(s) in F_p(u)[[s]] with the prescribed free coordinates and base point is unique, so a finite jet determines the leading G-vector F(u) exactly. Lifting was done at fixed numeric (u1,u2,k) in F_p (`numarc.sage`, `numlib.sage`): all 303 relations vanish mod s^5 in every run (resid_eq_nonzero 0), and G(s*tt) has s-valuation nu = 2 in every run.

The two branches are rational over F_p(u1,u2,k) once u3 = -2k/(k^2+3): the branch discriminant is proportional to 1 - 3*u3^2, and this substitution rationalizes it (`base_sym.sage`, base points in `tbase_branches.txt`).

Exact family. F(u)*(k^2+3) is polynomial of multidegree (1,1,2) in (u1,u2,k); it was reconstructed from 48 points per branch with 12 unknowns and verified on 8 further points per branch with zero mismatches (`interp1.sage`, `interp2.sage`, `Fnum.pkl`). This is interpolation of the Hensel output, not a symbolic Hensel lift: the symbolic 16x16 determinant over F_p(u1,u2,k) did not finish in 12 minutes and was stopped. Branch 0, with y3 = y7 = 0 identically:

    F1 ~ 10673k^2 - 20k + 30        F6 ~ 6832k^2 + 2530
    F2 ~ u2(506k^2 - 12019k - 506)  F8 ~ u2(6k^2 + 20k + 6)
    F4 ~ -6832k^2 - 2530            F9 ~ u1(-506k^2 + 8983k - 506)
    F5 ~ u1(6k^2 - 16k - 6)         F10 ~ -10673k^2 - 20k - 30

Branch 1 is stored in `Fnum.pkl` (printed by `interp2.sage`).

Base locus and order-2 arcs: the ideal of the ten numerators in Q[u1,u2,k] is the unit ideal for both branches (`sym.sage`), so F has no zero in chart t1=1 and no normal-bundle arcs of order 2 were needed there. In chart t3=1 (`chart3.sage`, `chart3x.sage`), points with t1=0 required GF(p^2): four points with two branches each give nu = 2, F nonzero, F in V(P2). Order-2 arcs at lower-dimensional strata outside these two charts (t1=t3=0, the locus k^2+3=0, the singular locus of the normalization) were not built: not run.

## Step 4: containment and rank (`sym.sage`)

- P2: for both branches, 0 of 9 generators nonvanishing on F(u) (exact polynomial identity in u1,u2,k). y1 is not in P2 and F1 is nonzero, so chart y1 serves. Jacobian of (F_i/F_1) in (u1,u2,k): exact rank 3 over the fraction field F_p(u1,u2,k) (a stronger statement than a rank at one point).
- P1: for both branches, 7 of 7 generators nonvanishing on F(u).
- Numeric cross-check (`numarc4.log`): 8 points, both branches, inP1 False, inP2 True in all.

## Step 5: geometric irreducibility screen

See the verdict section: explicit rational parametrizations for P1 and P2 replace absFactorize, which Singular's `absPrimdecGTZ` does not provide over F_p.

## Open items

- P1 is unreached. The next test is the three remaining charts (t5=1, t7=1 and the strata above) and an order-2 build at singular points of the normalization; alternatively the VB degree-4 Hilbert value (h4 vs 155) may show that no fiber relation of degree 4 reaches P1.
- The certificate covers the reduced support over F_32009 only; the second prime p=32029 replay (step 7) and kernel-plane limits (step 3 of section 10) are not run.
- Scripts depend on `strict_transform.txt`, `G.txt`, `J.txt`, `cone.txt` dumped by `s2_tc.sing` and `s3_dump.sing`.
