# Adversarial review: C30 in the W8 fiber

Artifact: commit 6144d16fd, `structure/c30-bounded`, read against `w8-kp`, `arcs-iso-w8`, ledger rows A5-008, A5-012, A5-013, A5-066, A5-131, A5-137, A5-138 to A5-149, A5-218, A5-236, A5-237, and `working/azure-cases/w8-d6-n19.md`. Field: graded commutative algebra (fiber cones, blowups). Local standard: `docs/runbooks/computer-algebra.md`. Visibility: the c30 README, `templates/dual.sing` lines 21-74, `run.sh`, `w8-kp/README.md` through step 7, `arcs-iso-w8/README.md` through line 49, the named ledger rows, the Azure case, Codex item 1. Not read: `check.sing`, `quotient.txt`, the N=19 probe README, the other plane logs line by line. No tree file was changed except this report. Scratch under `(scratch directory)` (deleted after writing). Marks: proved, computed, measured, hypothesis.

## Verdict

The passage from set-theoretic equality to L = K2 is valid, and the slice surjection points the right way. At all six sampled points the planes are linear 3-spaces in V(K2) off C20. What is not proved is that those planes lie in E0. README lines 3-6, A5-066 (`survives`), `arcs-iso-w8/README.md:27-29`, A5-008, and `w8-d6-n19.md:37-40` already spend L = K2 in every degree. That sentence is a hypothesis until divisibility along the smooth branch is exact.

## SERIOUS. The jet is not the ideal (claim 2, load-bearing)

`templates/dual.sing:39` tests `subst(h,v2,0)` on `tr(...,NN)` with NN = 10. M(p) uses only `jet(H3,1)` (`dual.sing:54`). That 1-jet is exact: the Newton determinant is a unit, so the series is unique, and orders at most 10 of a polynomial composition depend only on orders at most 10 of the series. Nakayama then lifts "the linear parts span m/m^2" to "the quotients generate m = (s, v2)". README:47-49 cites that Nakayama for a different conclusion, I' on the slice equals (G'_2, G'_11, v2 s, v2^2). A congruence modulo m^11 is not membership. A pure s^11 term lies in m^11 and not in (v2).

Once equality holds, the fiber cone is a polynomial ring, by a direct count. Exponents (1,0,0,0), (0,1,0,0), (0,0,1,1), (0,0,0,2). The differences from the last have 3×3 minor 1, so the four vectors are affinely independent. Products of n generators are the distinct monomials x^a y^b z^c w^{c+2d}, a+b+c+d = n. None lies in m I^n: dividing out one variable either drops that unique count or makes the w-exponent minus the z-exponent odd, and every generator product has that difference even. So dim I^n/m I^n = binom(n+3,3). This is the fiber cone of the monomial ideal. It is not yet the fiber cone of I'. Until it is, Proj of the slice fiber cone may be a proper subscheme of the linear P^3, and "Pi_p lies in E0" (README:52) is a hypothesis. Rank M = 4 is computed and only says the image is a linear 3-space in P^23.

The surjection itself is the right direction and needs no transversality. For any ideal a, (I+a)^n sits in I^n + a, because every summand that takes a factor from a lands in a. The extended power in R/a is the image of I^n, so F(I) surjects onto F(I · O_{R/a}). Proj of a quotient of a standard graded ring is a closed subscheme. README:43 states this correctly. The embedding of the whole plane is the monomial count, not the surjection.

Measured, same gap, new point. Prime 32009, p = [1:0:11372:17997:11372:17997:0], Y0 = (5102, 21091, 13876, 14430). Draw `docs/evidence/anu_qrng/draw-2026-11-08T182935Z.json`, indices 70, 73, 75, 77, 78, 82. Every in-range value in indices 70-99 is already a control coefficient in `points.json`; this (b, c, Y0) is not one of the five planes. `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 timeout 900` on the pt1 script with that point. Exit 0, RESULT time 52 s:

- s^2 failures 0; Newton residual 0; v2 failures on the truncation 0; linear consistency 0
- Newton det -6332; (v4, v5) det 1583; vdim 1; the two dual directions agree
- K2 0/144; Lambda 9/9; P 23/48; K2:P 0/131; rank M 4
- K2 Jacobian failures 0, rank 18; K2:P Jacobian failures 0, rank 18; y0 has P nonzero 23
- rank of [M | dM/db Y0 | dM/dc Y0] = 6

Global dp in (s, v2, v4, v5, v9), same point: dim(G'_2, G'_11, J') = 3, dim plus (v2) = 2, 22 of 24 generators outside (G'_2, G'_11, J', v2), 22 normal forms not divisible by v2. Mora std returned 3 generators; the 24 local reductions printed nothing further at the 900 s cap (exit 124). Newton at order 24 printed no RESULT line at the same cap. A v2 = 0 saturation with v9 kept free (an earlier probe set t9 = 0 and then differentiated in v9, so its determinant 0 was the probe's): det(0) = -6332, dim of the three polynomials = 2, dim sat(·, det) = 1 with 17 generators, 22 of 24 G' outside that saturation. Divisibility is not a polynomial identity on the det-nonzero locus. The germ at the origin is still a smooth curve (Jacobian rank 3). Non-membership in the saturation does not by itself kill that germ. Exact divisibility was not computed at even one point.

## SERIOUS. The records spend the hypothesis

README:3-6 states E0 = V(K2) and F(I) = k[y]/K2 in every degree, and says the N = 19 run is not needed. A5-066 `survives` repeats it. `arcs-iso-w8/README.md:27-29` states V(K2 : P) ⊂ E0 as fact. A5-008 says every degree follows from A5-066. `w8-d6-n19.md:37-40` says the 2026-11-08 check found C30 in the fiber. A5-236 `survives` for the method is fair: the pipeline returns what it claims to compute. The equation rows have to wait until divisibility is exact on a Zariski-open of P(L0) and the K2 pullback is an identity. README:3 also writes C30 = V(K2 : P) at both primes; at 32029 that colon ideal is not retained (`w8-kp/README.md:4-6`, c30 README:95-96).

## Claim 5. The ideal arrow follows. Proved, once the sets agree

L need not be assumed radical. Fiber cones need not be reduced (A5-033: nilpotent linear forms). The squeeze:

K2 is the degree-2 kernel, and the receipts put those generators in L, so K2 ⊂ L (`w8-kp/README.md:12-14`).

K2 is radical (`w8-kp` step 2, lines 47-52) and k[y]/K2 is Cohen-Macaulay of dimension 6 (lines 12 and 16). Depth at least 1 means H_m^0 = 0, so K2 equals its saturation. The c30 README never names saturation; the Cohen-Macaulay line supplies it.

F_p is perfect, so reduced implies geometrically reduced. By the homogeneous Nullstellensatz, the ideal of a projective set is the saturation of the radical. Thus K2 = I(V_+(K2)) over an algebraic closure, contracted back.

C20 ⊂ E0 is the arc certificate (`arcs-iso-w8/README.md:9-26`, proved). If C30 ⊂ E0 as well, then V_+(K2) ⊂ V_+(L), so L ⊂ I(V_+(K2)) = K2. With K2 ⊂ L, L = K2. Reducedness of L is a consequence. No further Hilbert value is required for this arrow.

The missing hypothesis is the set-theoretic containment C30 ⊂ E0, not a radicality assumption on L. Cheapest supply: exact divisibility of G'_j along the smooth branch at the generic point of U = {both determinants nonzero}, and the identity that the 144 quadrics of K2 vanish on M(b, c) Z. One local certificate at one rational point does not spread to U. A polynomial identity, cleared of the two determinants, does. Neither was run to completion here.

## Claim 1. Proved, after repairing one sentence

README:34 says s^2 is invertible on the blowup. As a function it vanishes on {s = 0}. As an ideal sheaf it is invertible. J is principal (`w8-nm.sing:3`). Its lowest-degree form is -t2^2 - t4^2 + t5^2 + t6^2 - t7^2 - 4 t1 t9, five squares plus a hyperbolic plane, rank 7 for p odd, so not a product of linear forms (README:25-26). An irreducible initial form makes J irreducible in the UFD k[t]. V(J) is integral, the blowup is integral, and a nonzero principal ideal is an invertible ideal sheaf. Then s^2 I' is invertible, the universal property supplies Bl_{I'} B → Bl_I V(J), and G_j/G_k = G'_j/G'_k on {s = 0} too. The written chart is t1 ≠ 0. P(L0) also meets t1 = 0; step 6 uses the closure of the family over the standard chart. The falsifier (a fiber point that is not a limit of [G]) does not fire on the s^2 twist.

## Claim 3. Dimension of the family: proved. Inclusion in C30: computed at points

M is rational on U: `dual.sing:45-54` is Cramer's rule on the order-1 jet, denominator the (v4, v5) block. U is open in P^2, so the closure T of the image of U × A^4 is irreducible. {rank ≤ k} is closed. The image of the differential lands in the Zariski tangent space of the closure. Over a perfect field the smooth locus is dense, so at a general point that tangent space has dimension equal to the dimension of the closure, and this applies at both primes. Rank 6 at one point gives affine dimension at least 6 and projective dimension at least 5. README:58-62 says this. README:132 drops the "at least" and is wrong as written: equality to 5 uses the upper bound from sitting inside C30.

The new point reads rank 6. That falsifier did not fire. Tangent consistency (README:98-102) checks that six vectors lie in a codimension-18 kernel. An error inside the plane is invisible to it, and the dimension bound does not use it. The on-control reproduces the C20 rank-6 certificate by a different Jacobian; it does not validate Newton.

Every retained plane and this one have K2 vanishing 0/144 and Lambda 9/9; at 32009, P is positive and K2:P vanishes. Six zeros of a polynomial are not an identity. Cheapest test: clear the two determinants and check that the 144 pullbacks are the zero polynomial in (b, c, Z).

## Claim 4. Proved by the citation the README calls an argument

`w8-kp` steps 5 and 6 (lines 60-65), at 32029, without P or K2:P. The 5-dimensional part of V(K2 + Lambda) is one component C20 of degree 20, and the complementary section-1 orbits sum to 30 with no split into the allowed degrees 17, 20, 30, 33. A third component is excluded. C20 ⊂ V(Lambda) is the content of that step. Lambda 9/9 nonzero keeps a plane out of C20. Sections were not replayed.

## Claim 6. Degrees at most 5: certified. Degree 6: the hypothesis in claim 5

A5-138 to A5-142 and A5-144 to A5-148 match lower and upper bounds: h_d = HF(k[y]/K2, d) for d ≤ 5 at both primes. A5-143 and A5-149 stay open at h_6 ≤ 8624. README:66 lists 24, 156, 600, 1725, 4116, 8624, 16416 from a `kbase` of std(K2). No log under `c30-bounded` retains that `kbase`. `claims.json` stores `k2_count` 8624 on the open degree-6 objects (line 1265 and three further hits). 16416 does not occur there. A truncated rank below 8624 would falsify the prediction. A rank equal to 8624 would certify h_6 only. A quadratic Gröbner basis does not stop a larger ideal from gaining a generator in degree 6, so N = 19 cannot prove the tail.

## Conjectures (none of this is posited)

1. Hypothesis. Over U, the fiber of E0 over each point of P(L0) is the linear P^3 = Pi_p, and the closure of the union is C30. Falsifier: dim I'^n/m I'^n < binom(n+3,3) for some n, or exact divisibility failing on the germ. Cheapest test: one-variable Hensel along v2 = 0 past order 10 at one point (the two-variable order-24 run and the Mora reductions both hit the 900 s cap), then the cleared-denominator identity for K2.

2. Hypothesis. C30 is a P^3-bundle over an open of P^2, or the image of one under a generically finite map of degree δ, in which case 30 = δ times the degree of the family. Rank 6 of df on a 6-dimensional source says the map onto its image is generically immersive. It does not give δ. Falsifier of "bundle": rank of [M(p) | M(q)] below 8 for distinct p, q in U, so the planes meet. They may still cover C30 after a contraction. Cheapest test: that rank at two of the existing points.

3. Hypothesis. A5-131 and A5-137 do not need a second Newton run. A5-013 proves the sign-paired fibers are isomorphic in every characteristic, and A5-130 already transports h_5 of W8 → N+ at 32009. If L = K2 is proved for N-, both open rows follow in every degree. Falsifier: the sign flip on t9 moves L0 or the Newton block, so the isomorphism does not match this chart. Cheapest test: one plane script on the sign-flipped header. The N- script is hard-wired to `w8-nm.sing`. Not run.

## What would retire the degree-6 rank

Beyond doubt, for every degree: exact divisibility on the germ at the generic point of U, the K2 identity on (b, c, Z), and the squeeze in claim 5. That is a laptop computation of the same shape as the planes. The Mora reduction of all 24 generators did not finish in 900 s, so the local half may need the one-variable Hensel or a per-generator reduce. The N = 19 job (measured preflight 375.62 GiB, forecast peak about 160 GiB, 17 to 20 h; `w8-d6-n19.md:12-13` and line 30) would then test the rank engine and the law N = 3d + 1. Its falsifiers stay: r_19 < 8624, blocks 2 and 3 unequal, a failed nonstandard-product check, and the top-stratum count 169 = (2·6+1)^2. It would not certify d > 6. Codex item 1 (`review-codex-final-report.md:47`) asked for this bounded check and said a real proof removes the run. The check ran. The proof has one membership left.

## Smaller defects

`run.sh:47` exits 0 after appending the Singular status, so a failed run looks successful to a caller that does not open the `.result` file. `run.sh:14` expands a glob of Python versions through `ls`; more than one match breaks the assignment under `set -u`. README:34 and README:132 are the two sentences repaired above. The degree-7 value 16416 has no retained `kbase` log and no `k2_count`.

## Steelman

The reduction asks the cheap question. A family of planes and one Jacobian rank replace a chart whose Bezout bound is 4·8^5 = 131072 (README:123) and a slice that stalled at 900 s (A5-237). C20 was already certified symbolically. The slice surjection, the dimension inequality in the body of step 6, the 32029 placement, and the passage from the two sets to L = K2 all hold. Six numeric planes, this one included, do exactly what the pipeline predicts. The missing piece is a membership in a smooth germ and a polynomial identity.
