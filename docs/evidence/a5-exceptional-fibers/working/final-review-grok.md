I'll read `final-plan-bundle.md` and answer only the questions in its first section.The brief’s questions are clear. I’ll finish the rest of the bundle before answering.The arc test can prove reduced support over \(\mathbf F_{32009}\) for a component it dominantly covers. It does not prove the fiber scheme, a characteristic-zero component, or the attaching map. The hard step is producing an exact dominant family, not checking a minor once one exists.

## 1. Where the certificate breaks

The valid core, as stated by both consults, is: an exact arc on \(V(J)\) through the origin, with leading symbol \(c(u)\neq 0\), contained in a minimal prime \(P\) of \(\sqrt{K_2}\), and with a \(d\times d\) Jacobian minor of rank \(d=\dim P\) on a chart \(c_q\notin P\). Over a perfect field that minor means the parameter map is separably dominant, so the image is dense in the \(\mathbf F_p\)-variety \(V(P)\). Containment of the fiber in \(V(K_2)\) is already observed where the extracted quadrics generate \(K_2\): X−, 69 quadrics equal to the retained ideal (decision record, S0/S1 and the relation check); VB, 21 quadrics and \(h=10,34,80\) through degree 3 (decision record §7–§8). Quadratic generators lie in the fiber ideal in every degree, so \(V(K_F)\subseteq V(K_2)\).

That implication does not extend as far as the converged plan uses it.

**Nonreduced \(K_2\).** X− has one arithmetic prime, projective dimension 3, degree 12, and \(K_2\) is not radical: radical Hilbert values \(12,45,112,225\) against fiber values \(15,51,122\) (decision record §8). An arc meets the reduced support and is blind to nilpotents. “Dim 3 plus the unique prime” fills \(V(\sqrt{K_2})\), and leaves the quadratic scheme strictly thicker. E8-bar→N+ is the same shape: nonradical, primes \((4,11)\) and \((3,4)\). VB is the only listed pair whose \(K_2\) is radical, and even there a higher-degree element of \(K_F\) can add multiplicity or an embedded prime without leaving \(V(K_2)\). Embedded primes of nonradical \(K_2\) are not on the minAss list of the radical; X− has not been checked for them.

**Arithmetic prime versus geometric components.** `minAssChar` primality is over \(\mathbf F_{32009}\). A dominant family defined over \(\mathbf F_p\) is dense on every Galois conjugate, so it does not drop a geometric piece of that same prime. It also does not prove absolute irreducibility. Degree 12 can still split over an extension. The programme in purpose.md wants the limit set over \(\mathbf C\) for \(H=G_2(\mathbf C)\times\mathrm{SO}(2,\mathbf C)\times\mathbf C^*\). Reduction mod \(p\) can merge, add, or fatten components. A second split prime, regenerated from the \(\mathbf Q(i)\) producer (decision record §8; rewriting 32009 is invalid), is a screen. Two matching Hilbert functions are not a specialization theorem.

**Inseparability is one-sided, and the fallback is the real computation.** A nonzero minor certifies separable dominance. A zero minor certifies nothing: inseparable parametrization, a chart where \(c_q\in P\), a family stuck in \(P_1\cap P_2\), or a genuinely thin image. Degrees 3, 4, and 12 are smaller than \(p=32009\) and coprime to it, so the jet calculus up to those orders matches characteristic 0; inseparability is not forced by degree. It is forced by a bad parametrization. Over a perfect field a reduced component is generically smooth, so some separable étale family exists. A polynomial or rational family on affine 3-space exists only if that component is unirational. A general degree-12 threefold in \(\mathbf P^{14}\) is not. Orbit geometry may supply unirational arcs; a blind polynomial ansatz does not. If every \(\mathrm{GL}(3)\) remix of \(u\) kills the minor, the remaining test is the image dimension of a 3-parameter graph ideal. That is elimination again. It is smaller than Rees saturation, and it is still the step the slogan hides.

**Jets are not arcs.** \(J(x)\equiv 0\pmod{s^M}\) is a discovery object. The certificate needs \(J(x)=0\) as a polynomial or rational identity, or a DVR from normalization. Contact order is computed, not assumed: \(h_1\) equals the generator count on VB (10), E8-bar (21), and W8 (24), so there is no linear fiber equation, and the generic tangent vector need not lie on \(Y\). Expect \(\nu\ge 2\). Component degrees bound a first try, not a theorem: \(s\)-degree 4 on VB (degrees 3 and 4), and up to 12 on a general curve section of X−. Stopping at a failed ansatz does not delete the component. Daybreak’s abort “image rank \(<3\)” stops the route; the falsifier that actually fired is the ansatz.

**Two components, and the pairs with no prime list.** On VB, density in the degree-3 prime leaves the degree-4 prime open, and conversely (both consults; decision record §8 rules out one irreducible degree-7 scroll). A family in the intersection vanishes on both primes and fails the rank test. On E8-bar→N+, a dimension-4 family says nothing about the dimension-3 prime. Iso and W8 have no finished radical or minAss (600 s, decision record §8); the certificate cannot start there. E8-bar→N− has the same \(h_1,h_2\) as N+ and a different ideal (span rank 41); it needs its own primes.

**Other overreaches.** Germ-dimension caps (3 for X, 4 for Iso and E8-bar, 5 for W8) are adopted falsifiers in the decision record §2, not proved upper bounds, and the density argument does not use them. The fiber is at the recorded point: one-point transport by \(H\) was rejected. \(h_4=155\) on VB closes nothing. \(h_4<155\) is a new fiber relation and must be reduced modulo each VB prime and modulo \(\sqrt{K_2}\); it may cut one component, cut both, or be nilpotent. Linear type is already false: the quadratic relation ideals are nonzero. A Jacobian-dual theorem that assumes linear type does not apply. `degBound` on the old saturation is not a completion.

## 2. One VB family a reviewer can run

VB first: 8 source variables, 10 target variables, radical \(K_2\), both components dimension 3, method A degree 2 finished in 7 s (decision record §7). X− is the same script with 7 source variables, 15 target variables, one prime, and \(s\)-degree raised from 4 to 12. Polynomials are not in this bundle. Load the regenerated header (`fiber_inputs.py`, \(p=32009\), \(r=10754\)), not a file with 32009 pasted in. Launch under `MemoryMax=8G`, `MemorySwapMax=0`, `MALLOC_ARENA_MAX=2`, wall 30 min, one thread. Deterministic charts only; no seed.

Expect \(\nu\in\{1,2\}\) and an exact polynomial of \(s\)-degree at most 4 whose coefficients are polynomials in \(u=(u_1,u_2,u_3)\) of degree at most 4. Free source coordinates \((t_1,t_2,t_3,t_4)=(s,\,s u_1,\,s u_2,\,s u_3)\). Dependent coordinates \(t_5,\ldots,t_8\) are solved order by order. At order \(n\) the unknown jet appears linearly through \(dJ\); products of unknowns would appear only if all orders were solved at once. The last check is an exact identity in \(\mathbf F_p[s,u]\), not a congruence.

```sage
# vb_arc.sage — exact arc family for E8bar->VB. Inferred procedure.
# HEADER.sing leaves ring r=32009,(t(1..8)),dp; ideal J; ideal G;  (10 gens)
# K2.sing    leaves ring y=32009,(y(1..10)),dp; ideal K2;          (21 quadrics)
p = 32009
F = GF(p)
singular.eval('option(redSB); < "HEADER.sing";')
dJ = int(singular.eval('dim(std(J));'))
if dJ < 4:
    raise RuntimeError("germ dim %s < 4; affine cone cannot cover a dim-3 component" % dJ)
# Cycle a fixed free-set if the order-1 Jacobian minor on t5..t8 is 0.
singular.eval('matrix A = jacob(J);')
# Build jets in Sage from Singular generators converted via singular.sage(J).
Rt = PolynomialRing(F, 8, "t")
t = Rt.gens()
Jgens = [Rt(f) for f in singular.sage("J").gens()]
Ggens = [Rt(f) for f in singular.sage("G").gens()]
Pu = PolynomialRing(F, 3, "u")
u = Pu.gens()
S = PolynomialRing(Pu, "s")
s = S.gen()
# Known part of the graph. Dependent jets start at 0 and are corrected.
free = [s, s*u[0], s*u[1], s*u[2]]
dep = [S(0) for _ in range(4)]
DEG = 4  # max VB component degree; escalate only to 6, then stop
for n in range(1, DEG+1):
    arc = free + dep
    # Coefficient of s^n in each J generator, linear form in the 4 unknown vectors in F^8 projected to dep.
    rows, rhs = [], []
    mons = Pu.monomials_of_degree  # bound u-degree by n; see note below
    # Evaluate dJ on the known jet of order < n and the order-n remainder.
    # Concrete linear algebra: specialize u on the deterministic grid
    # {(a,b,c): 0<=a,b,c<n+1}, solve a 4-column system over F, interpolate.
    grid = [(a, b, c) for a in range(n+1) for b in range(n+1) for c in range(n+1)]
    samples = []
    for pt in grid:
        subs = {Rt.gen(i): F(free[i].subs(s=0) if False else 0) for i in range(4)}
        # Substitute the current polynomial jet, read coeff of s^n, solve dJ(dep) = -remainder.
        # Implementation: singular.eval of the specialized numbers, lift() on the 4 dependent columns.
        samples.append(pt)  # replaced by the solved F^4 vector at pt
    # Interpolate each dependent coordinate at order n (degree <= n < p) and add s^n * that poly.
    # If the specialized dJ minor is 0 on every grid point, break and change the free set.
# Exact check — the certificate, not the jet:
arc_poly = free + dep
rem = [S(Jg.subs(dict(zip(t, arc_poly)))) for Jg in Jgens]
if any(r != 0 for r in rem):
    raise RuntimeError("jet only; refuse support-equal")
nu = min(g.valuation() for g in [S(Gg.subs(dict(zip(t, arc_poly)))) for Gg in Ggens])
c = [g[nu] for g in [S(Gg.subs(dict(zip(t, arc_poly)))) for Gg in Ggens]]  # in Pu
if all(ci == 0 for ci in c):
    raise RuntimeError("leading symbol 0 at s-degree %s" % DEG)
# Load both minimal primes of K2 (observed: dim 3, degrees 3 and 4, radical).
# For each prime P: require c in P, pick q with y_q not in P, require a nonzero 3x3 minor
# of d(c_i/c_q)/d(u_j) in Frac(Pu). Then repeat absolute-irreducibility:
# factor the minpoly of a primitive element of Frac(y/P) over F_p(z1,z2,z3).
```

The grid \(0,\ldots,n\) has \((n+1)^3\le 125\) points and a \(4\times 4\) solve; that is the memory bound, far below 8 GiB. A nonzero remainder, a zero symbol, a component equation that survives, or a minor that stays zero after the eight cyclic free-sets is a failed ansatz. It is not a statement that the component is absent. X− uses the same lift with free set of size 4 inside 7 variables, `DEG` starting at 2 and stopping at 12, and one prime.

## 3. Routes the consults did not use

**Group arcs (the one that matches the geometry).** \(Y\) is an orbit closure of \(H\), so the orbit is unirational and a one-parameter subgroup through a general point of the nullity-8 orbit is an algebraic arc on \(Y\) with no need to solve \(J=0\) in the slice. The stabilizer representation at the recorded point decomposes the fiber. That is not the rejected transport of a fiber from one point of \(Z\) to another (decision record §2). The bundle records the group and rejects transport; it does not record matrices, so this is a construction plan, not a formula I can expand here.

**Fixed-order jet linear algebra as discovery, in the shape method A already finishes.** Each order is a matrix over \(\mathbf F_p\) or \(\mathbf F_p[u]\), the regime of `probes/rank_nf.py`, not of saturation. Keep it on the discovery side of the exact check above.

**Project an \(h_4\) relation onto each VB prime.** If degree 4 drops below 155, reduce the new relation modulo each prime and modulo the radical before interpreting it.

**Hensel-lift the arc, not the Rees ideal.** `pyadic` is already the repo’s exact lift tool (PYTHON.md). A polynomial identity of \(s\)-degree \(\le 4\) in three parameters is a small system. Lift coefficients to \(\mathbf Q(i)\) and check \(J(x)=0\) there. Lifting a finished basis of the fiber ideal is what the consults correctly call premature.

**Absolute-irreducibility screen.** Function-field factorization of one primitive minpoly per VB prime, degree 3 or 4, under the same 8 GiB cap.

**Equivariant weight blocks.** Torus weights were deferred as a decomposition theorem (decision record §2). As a constraint on arc coefficients they cut unknowns before any toric claim.

These do not apply to the certificate. Quantum backends, Azure Quantum emulators, Braket, Quandela, IQM, IonQ, and the local RTX 4070 Ti have no exact Groebner or ideal-membership path; float rank is not evidence (PYTHON.md). The TPU device and Kaggle GPUs accelerate JAX or Aer, not Singular; the v5e-8 queue already sat 6 h with no assignment (decision record §9). Cloud and local LLMs produce text, which the lab map bars from evidence. QRNG does not prove density; a deterministic chart list avoids a seed. ANU would apply only if a later search drew integers, and those draws would have to be ledgered. GitHub-hosted runners (about 16 GB) can replay a finished identity. They are the wrong place to search. Kaggle CPU (about 30 GB, no accelerator quota) is a second-prime method-A substrate after a written case. Another Azure FX4mds_v2 saturation repeats the 72 GB post-pivot stall; the trial spending limit and the VM 2 ssh loss are operational stops.

## 4. Steps

Each cap is a cgroup `MemoryMax` with `MemorySwapMax=0`, one thread, `MALLOC_ARENA_MAX=2`. Host admission stays inside the 24 GiB concurrent budget (decision record §8). Claims are marked O (observed) or I (inferred).

| # | Work | Substrate, cap, wall | Yield | Falsifier |
|---|---|---|---|---|
| 1 | Load regenerated VB header; `dim(std(J))`, rank of \(dJ\) at 0, confirm 21 quadrics and two primes still match the receipt | Host, 4 GiB, 15 min | Germ dimension and a reusable prime basis. O: degree 2 in 7 s, radical, primes \((3,3),\ (3,4)\) | Dimension \(<4\), or primes differ from the receipt. Stop |
| 2 | Exact lift of §2, eight cyclic free-sets, \(s\)-degree \(\le 4\) | Host, 8 GiB, 30 min | Either an exact family per component or a jet/obstruction log. I | Nonzero \(J(x)\); symbol 0; minor 0 on every chart. That ansatz stops. Components stay open |
| 3 | For each family: containment in its prime, \(c_q\notin P\), one \(3\times 3\) minor, function-field factor of the primitive minpoly | Host, 8 GiB, 30 min | `support-equal` over \(\mathbf F_{32009}\) for each component that passes, separately. I, using O containment from the quadrics | Minor vanishes after remix; minpoly factors (geometric split: rename, do not drop the \(\mathbf F_p\) claim) |
| 4 | VB \(h_4\) against 155; if smaller, reduce the new relation mod each prime and mod the radical | Host, 8 GiB, 1 h. O: cubic took 406 s; 155 is the quadratic model | One more degree, plus which component a new relation meets. I | \(h_4<155\) kills “quadrics generate the fiber.” Equality certifies nothing further |
| 5 | Repeat 2–3 for X−, \(s\)-degree 2 then at most 12, one prime | Host, 8 GiB, 2 h | Reduced support of the degree-12 prime over \(\mathbf F_p\). O: \(h=15,51,122\), one arithmetic prime, nonradical | Same ansatz falsifiers. A pass still leaves the nilpotent structure open (O: radical Hilbert values differ) |
| 6 | Hensel-lift a passed family to \(\mathbf Q(i)\) and check the identity; regenerate \(J,G\) at \(p=32029\), \(r=9115\), and reduce the lifted family | Host or GitHub Actions, 8–12 GiB, 1 h | Char-0 witness for those components the lift hits. I. O: harness already emits the second header | Identity fails over \(\mathbf Q(i)\), or the second prime splits the image differently |
| 7 | VB syzygy only as a hypothesis probe: degrees of `syz`, grade, relation type. No Jacobian-dual invocation | Host, 8 GiB, 1 h | A verified hypothesis list, or a refusal. O: linear type is already false | Any required hypothesis fails, or RSS approaches the cap. Stop the scheme route |
| 8 | Iso and W8: radical then `minAssChar` in projective charts, nothing else | One cloud CPU only after 1–5, 16 GiB, 2 h, case file | The missing prime list. O: 600 s cutoff | Unfinished decomposition. No arc claim |

Stop conditions already observed, left in force: unchanged pivot saturation (six stalls, VB included, E8-bar→N+ at 72 GB), `std(L)` in 18 variables, full Rees-graph msolve, local `ds`, `minAssGTZ` first, any `RLIMIT_AS`. W8 on VM 2 is an outage, not a stall (decision record §9). A finished VB or X− support line still owes the kernel-plane map in purpose.md; the exceptional-fiber support is the limit set of directions, and the attaching datum is the limit of kernels along those directions.
