# Adversarial review: C30 in the W8 exceptional fiber

Artifact: commit `6144d16fd` supplies an algebraic-geometry argument, generated Singular programs, and finite-field records for the W8-to-N-minus fiber over primes 32009 and 32029. The fields are blowups and Rees/fiber-cone algebra, projective geometry, exact computer algebra, and evidence provenance.

Visibility: I read the brief, both agent guides, the computer-algebra runbook, every named README and ledger row, the C30 generator/templates/results, the W8 component certificate, the earlier review, the degree-6 case/probe, and the sign-isomorphism record. Later commits do not change `structure/c30-bounded/`. The review writes only this report; scratch output lives under `/tmp`.

## Findings ranked by consequence

### SERIOUS — the finite Newton jet is presented as an exact local-ideal proof

**Status: proved after an omitted argument; the recorded justification alone is insufficient.** `structure/c30-bounded/README.md:45-49` says order 10 “exceeds 1” and then invokes Nakayama to conclude
`I'|B_4=(G'_2,G'_11,v2*s,v2^2)`. The program actually substitutes order-10 Newton polynomials and checks divisibility only after truncation (`templates/dual.sing:30-40`); a finite jet does not by itself prove divisibility of the full formal restrictions.

The claim can be repaired without another long computation. The exact L0 curve at `v2=0` annihilates every `G'_j` (`README.md:25-28`). The nonzero 3-by-3 Newton determinant makes the formal solution of `(G'_2,G'_11,J')` unique, so its specialization at `v2=0` is that exact L0 solution. Hence every full formal restriction is divisible by `v2`. The linear parts of the quotients span `(s,v2)`; Nakayama then gives the claimed ideal. The remedy is to state those two exact steps and treat the order-10 calculation only as a check of the required low jets. A symbolic specialization at `v2=0`, followed by a rank-2 check of the quotient linear parts over `F_p(b,c)`, is the cheapest retained certificate.

### SERIOUS — `s^2` is not a unit on the exceptional divisor

**Status: claim 1 survives after correction.** `structure/c30-bounded/README.md:34-37` says the two blowups agree “because `s^2` is invertible there.” The element `s` vanishes over the points under discussion, so the sentence is false in precisely the place where it matters.

The correct theorem is invariance of a blowup after tensoring its center by an invertible ideal sheaf. Near the smooth point `p`, `s=0` is Cartier, so `(s^2)` is an invertible ideal even though `s^2` is not an invertible element. Multiplication by `s^{2n}` identifies the graded Rees algebras of `I'` and `s^2I'`; on `Bl_{I'}B`, both `(s^2)` and `I'` pull back to invertible ideals. The universal property of `Bl_I V(J)` therefore supplies the factor map, and a point over `p` maps over the origin with `[G]=[s^2G']=[G']`. Replace the unit claim with the Cartier/Rees-algebra argument.

### SERIOUS — the required “new” QRNG range is already consumed

**Status: computed point, refuted independence.** The brief says indices 0–69 are used and directs a new point to indices 70–99. `structure/c30-bounded/points.json:135-190` already assigns indices 70, 73, 75, 77, 78, 82, 83, 84, 88, 89, 92, 94, and 95 to retained controls. The requested valid-value selection therefore cannot produce an unused point in that range. My rerun used 70, 73 for `(b,c)` and 75, 77, 78, 82 for `Y0`; it is a new plane evaluation but reuses draw entries. The remedy is a fresh authorized unused range beyond every index in `points.json`, then a retained point ledger if independence matters.

### SERIOUS — the degree-6 registries contradict the all-degree conclusion

**Status: record defect.** If the C30 proof is accepted, `F(I)=k[y]/K2` proves `h_6=8624`; nevertheless `ledger.tsv:131,137,143,149` and `claims.json:1264-1267,1446-1449` keep the four W8 degree-6 rows open. The W8-to-N-plus rows need no second local calculation: the proved doubling automorphism carries the entire W8-to-N-minus fiber to W8-to-N-plus in every characteristic (`structure/README.md:8-22`; `ledger.tsv:14`). The same file already transports degrees 1–5 (`ledger.tsv:126-136`). Once the two proof repairs above land, rows A5-143/A5-149 and their sign-transported A5-131/A5-137 should record equality by proof, while a direct rank remains an independent computation rather than a prerequisite.

### SLOPPY — a low rank at one further point is not a falsifier of generic rank six

**Status: refuted falsifier.** Rank at least six is an open condition; one rank-six point proves generic rank at least six, while another point may lie on the rank-drop locus. `structure/c30-bounded/README.md:54-62,130-132` states the semicontinuity argument correctly. A genuine falsifier must invalidate every reported rank-six computation, the derivative formula, or the rational-family/domain argument; one special point of rank below six does not do so.

## Claim dispositions

1. **Proved after correction.** The Cartier/Rees argument above gives the factorization and preserves `[G]`; the fiber over `p` maps into `E0`.
2. **Proved after supplying the omitted formal-divisibility argument.** For the quotient local map `A=O_{B,p} -> A/J=O_{B_4,p}`, each degree map `I^n/mI^n -> (I(A/J))^n/m_{A/J}(I(A/J))^n` is surjective. Thus `F_A(I) -> F_{A/J}(I(A/J))` is surjective and `Proj` reverses it to a closed immersion. The direction in `README.md:42-49` is correct; no flatness hypothesis is needed.
3. **Proved over the stated open set.** The nonvanishing determinants define a nonempty open `U` in `P^2`; `U x P^3` is geometrically irreducible, and the closure of its rational image is geometrically irreducible. The rank-six differential makes the image projective dimension at least five. Containment in `C20 union C30`, one point outside `C20`, and irreducibility place the image in `C30`; equal dimension then gives equality (`README.md:54-65`).
4. **Proved from the retained component certificate, conditional on that certificate.** `structure/w8-kp/README.md:43-76` proves that `V(K2)` has exactly the geometrically irreducible components `C20` and `C30` at both primes. `K2+Lambda` isolates `C20` (`w8-kp/README.md:60-65`), so a plane outside `V(Lambda)` cannot lie in `C20` at 32029. Retaining explicit `P` and `K2:P` coefficients at 32029 is unnecessary for this placement.
5. **Proved; `L` need not separately be radical.** Let `S=k[y_1,...,y_24]` and `m=S_+`. Projective Nullstellensatz gives `sqrt(L^sat)=K2` after algebraic closure because the projective supports agree. The nonempty homogeneous geometrically radical ideal `K2` is saturated (`w8-kp/README.md:3-8,43-76`). Therefore
   `K2 subset L subset L^sat subset sqrt(L^sat)=K2`, so `L=K2`.
   The exact missing hypothesis would be geometric support equality and geometric radicality/saturation of `K2`, rather than equality of only `F_p`-rational points. The retained component proof supplies both. No degree-6 Hilbert comparison or low-degree primary decomposition is needed.
6. **Computed, then proved in all degrees if claims 1–5 hold.** `README.md:66-70` records `HF(S/K2,1..7)=24,156,600,1725,4116,8624,16416`; rows A5-138–A5-148 match through degree five. Claim 5 makes 8624 an exact degree-6 value, not merely a prediction.

## New plane calculation at prime 32009

The scratch script changed the retained point to QRNG entries `70=11372`, `73=17997`, `75=5102`, `77=21091`, `78=13876`, and `82=14430`, and disabled the repository result sink. `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` executed no Singular code because the sandbox denied both user-bus transports. The completed command used `ulimit -v 8388608; timeout -k 10 900 /usr/bin/time -v ... Singular -q --no-rc (scratch directory)`; it exited 0 in 48.22 s at 26,104 KiB peak RSS.

```text
RESULT c30-plane-p32009-new70 J and the generators of G not divisible by s^2 in the chart (0 required): 0; Newton residual terms over both directions (0 required): 0; generators not divisible by v2 (0 required): 0; linear-part consistency failures (0 required): 0
RESULT c30-plane-p32009-new70 determinant of the 3x3 Newton block -6332, determinant of the (v4,v5) block 1583 (nonzero required)
RESULT c30-plane-p32009-new70 I3 = (G_j restricted to S, divided by v2) has vdim 1, so it is the maximal ideal (s, v2) (1 required): 1
RESULT c30-plane-p32009-new70 values of M(p) agree between the two dual directions (1 required): 1
RESULT c30-plane-p32009-new70 plane: K2 generators nonzero on Pi_p: 0 of 144 (0: Pi_p lies in V(K2))
RESULT c30-plane-p32009-new70 plane: Lambda forms nonzero on Pi_p: 9 of 9 (positive: Pi_p lies outside the span of C20)
RESULT c30-plane-p32009-new70 plane: P generators nonzero on Pi_p: 23 of 48 (positive: Pi_p is not in C20 = V(P))
RESULT c30-plane-p32009-new70 plane: K2:P generators nonzero on Pi_p: 0 of 131 (0: Pi_p lies in C30 = V(K2:P))
RESULT c30-plane-p32009-new70 plane: rank of M(p) (4 required): 4
RESULT c30-plane-p32009-new70 tangent consistency: Jacobian of the K2 generators at y0 = M(p) Y0 against the six tangent vectors, nonzero entries (0 required): 0; rank of that Jacobian (18 at a smooth point of the 6-dimensional cone): 18
RESULT c30-plane-p32009-new70 tangent consistency: Jacobian of the K2:P generators at y0 against the six tangent vectors, nonzero entries (0 required): 0; rank of that Jacobian (18 at a smooth point of C30): 18
RESULT c30-plane-p32009-new70 point y0 = M(p) Y0: K2 nonzero 0, K2:P nonzero 0 (0 required), P nonzero 23 (positive: y0 is off C20)
RESULT c30-plane-p32009-new70 rank of [M(p) | dM/db Y0 | dM/dc Y0] (6: the planes sweep a cone of dimension 6, so a 5-dimensional projective set): 6, s 48
```

`c30_gen.py --check` reported 12 generated files matching. Ruff check/format, mypy, `sh -n`, ShellCheck, and `git diff --check` reported clean results.

## Conjectures and cheapest falsifiers

- **Hypothesis: the fiber over a general point of `P(L0)` is `P^3`.** The open conditions in `README.md:42-55` prove this on a nonempty dense open set, not at every point. A point on the determinant-discriminant with fiber-cone dimension or `rank M` different from four falsifies “every.” Compute the determinant locus in `F_p[b,c]`, decompose it, and test one point on each component.
- **Hypothesis: `C30` is birationally ruled by these `P^3`s over `P^2`.** The dimension equality proves that `P(E)|_U -> C30` is generically finite; it does not prove degree one, disjoint general planes, or a bundle structure on `C30`. Solve `M(b,c)Z=M(b',c')Z'` off the diagonal, or eliminate `(b,c,Z)` over a general image point. A generic fiber of degree above one falsifies birationality.
- **Hypothesis: a compactified rank-four bundle computes degree 30.** If the rational family extends to `P(E)->C30` birationally without boundary contribution, the degree is the appropriate second Segre number of `E`. Construct transition functions and compute `s_2(E)`; any value other than 30, a non-birational map, or a boundary contribution falsifies that description. The known degree 30 does not manufacture the bundle.
- **Proved transport: the W8-to-N-plus degree-6 rows equal 8624.** The sign automorphism, not another local slice, transports the full fiber and closes A5-131/A5-137 whenever the repaired N-minus proof is accepted.

## Remaining work and verdict

The cheapest route that makes the N=19 rank run unnecessary beyond doubt is textual and symbolic: replace the false unit sentence by the Cartier/Rees lemma, record the exact `v2=0` formal-solution/divisibility lemma, and retain its rational-function low-jet certificate at both primes. An independent review can then check a short proof instead of a 375.62-GiB preflight (`w8-d6-n19-probe/README.md:8-20`). The 17–20 h run would still test the `N=3d+1` convergence rule, receipt-bound engine, multiplication/closure implementation, and the predicted rank at prime 32009 (`working/azure-cases/w8-d6-n19.md:6-40`); it would cease to decide the geometry.

**Steelman.** The construction identifies the right exceptional-base locus, uses the correct fiber-cone quotient direction, supplies discriminating on/off controls, proves the required generic image dimension from one exact differential, and combines it with a strong two-component certificate. The fresh evaluation reproduces every algebraic and tangent check.

**Verdict.** The central conclusion is sound over `F_32009` and `F_32029`, but two sentences currently carry more weight than their stated reasons can bear: `s^2` is a Cartier factor rather than a unit, and a finite Newton truncation needs the exact L0 specialization before Nakayama applies. Those are repairable proof defects, not evidence for a different fiber. The QRNG-range collision and stale degree-6 rows are concrete record defects. After those repairs, the degree-6 cloud run is an independent implementation and convergence test, not necessary evidence for `F(I)=k[y]/K2`.
