# First-principles plan for the four failed A_5 fiber runs

Tags: [F] file (path:line), [M] measured by me (probes/, Singular 4.4.1, p=32009, nice, 2 GiB cap, host at load 36), [I] inferred.
Purpose (purpose.md): the exceptional fiber Proj F(I), F(I)=sum I^d/mI^d, of Y blown up along Z; deliver dim, degree, Hilbert function, components.

## 1. What each run computes and where it breaks
Common object [F inputs/e8_np_fiber.sing, kaggle xp_np/input.sing:5-15]: A=k[t]/J (7 slice variables, germ dim 4, X to N), I=(G), s=15 generators. h_d=dim F_d. Degree d relations K_d = {c : sum c_b P_b in mP_d+J}. Scripts take syz(U_d) of ~960 columns in the LOCAL ring ds.
- xp_np: h2=51 took 25470 s (xp_np/singular.log:4) because 3 jobs shared 4 vCPU and syz in ds tracks 961 components. It died in the degree-3 syz [F singular.log "no more memory", Appl 12.3 GB] against RLIMIT_AS=12 GiB [F kernel_run.py as_bytes 12884901888]. RSS peaked 6.7 GiB while MemAvailable was 22 GiB [F samples.tsv t=25665]. Cap-bound, not RAM-bound; also time-heavy.
- xm_nm: degree 2 only (no K3 in input.sing). Finished std: 69 relations, projdim 3, degree 12, then minAssGTZ ran 15,600 s at 4 GB RSS (time-bound, flat RSS in samples.tsv). Its result is V(K2), a superset of the fiber.
- iso_k2: K2 (68 quadrics, 17 vars) std instant; minAssGTZ ran 40,000 s at 1 GB (time-bound).
- E8 msolve: 31 variables (a,t1..t9,y1..y21), 37 equations y_i-a*G_i plus J [F e8_np.ms]. The last log line `7 407116 432548` is deg/sel/pairs, not a matrix: degree 7 selects 407,116 pairs (all of the minimal degree) [F e8_np_msolve_solo.log tail], versus 6,075 at degree 6 with matrix 206843x468377. Row count jumps 67x and the monomial table doubles to 2^28. Solo death had MemAvailable 51 GB at RSS 33.6 GB [F solo.samples.tsv], so the address-space cap killed it; but all variants die at the same step, so 2^28 slots at ~30+ virtual bytes each (about 40 GiB with the old block live during realloc) [I] is real demand.
- w8_nm: 24 generators, 325 products, 2,600 syz columns, died at 83 GB RSS before h2 (RSS rose steadily, memory-bound) [F w8_nm_fiber.samples.tsv].

## 2. Reformulations (same invariant), with measured evidence

**R1 Global ideal membership replaces the local syzygy (exact, same K_d).** Since sum c P lies in P, it lies in Q=mP+J locally iff globally. Command (probes/pG_xm_global_d2.sing): `ring r=32009,(t..),dp; sJ=std(J); P[i]=reduce(G[i]*G[j],sJ); Q=sJ,var(k)*P[i] all k,i; sQ=std(Q); N=reduce(P,sQ)`; h_d = rank of N (flint nmod_mat, probes/rank_nf.py), K_d = left kernel.
[M] X- degree 2: 17 s, 2 GiB, rank 51 (=h2, reproduces the 25459 s run). Speedup about 1500x. Yields h2 and K2 exactly. Falsifier h2=51: passed.
[M] Degree 3 with the 122 normal cubics: died "no more memory" at the 2 GiB cap (pH log). Not run higher: host has ~1 GB free. [I] needs 8-24 GiB, hours; run on Kaggle/Azure.

**R2 Normal-monomial reduction (Nakayama, exact).** Use only monomials of kbase(std(K2),d) as P_d (122 at d=3 for X-, 265 at d=3 for Iso [M]). Same h_d, columns 680 to 122.

**R3 Radical first, then decompose (exact for components; replaces minAssGTZ).** [M] Probe B/C: in K2 of X- y1^2,y5^2,y6^2 lie in K, so y1,y5,y6 are in the radical. Adding them leaves 12 variables with projdim 3, degree 12 unchanged, and `minAssChar` returns ONE component of degree 12 in 1 s (probe C), against 15,600 s unfinished for minAssGTZ. So V(K2) of X- to N- is irreducible, generically reduced, with embedded nilpotent structure. [I] GTZ's generic change of coordinates densifies the 15-variable input. Same recipe for the 7 other rows: test var(i)^2 in std, add, drop variables, then minAssChar/facstd.
Iso K2: [M] no nilpotent coordinate, no variable in K, facstd 1 piece, minAssChar timed out at 420 s. Still open; try R4/R5.

**R4 Generic linear section plus monodromy-free degree split (components of Iso K2).** Cut V (dim 4, deg 23) by 4 random hyperplanes over F_p: a 0-dimensional ideal of 23 points; `finduni`/`rur` then factor the univariate polynomial over F_p. Irreducible factors give Frobenius orbit sizes, an upper bound on the component partition. [I] Combine with R3 on subsets: components are subset sums of orbit sizes. Weaker than a decomposition; use as a cross-check on any R5 answer (degrees must sum to 23).

**R5 Component search by torus/symmetry.** [I] Find the stabilizer torus of K2 (linear solve for weights w with all generators weight-homogeneous); a multigrading makes primary components monomially structured, and Macaulay2 `decompose` or `primaryDecomposition` on the multigraded ideal is cheap. Command: M2 `needsPackage "MinimalPrimes"; decompose I` after changing coordinates to the weight basis. Falsifier: degrees sum to 23, projdim 4. This gives the kernel-stabilizer isotypic split the purpose asks for (see section 6).

**R7 Cubic completeness check (cheap, no Groebner).** [M] HF of k[y]/K2 for X-: 15, 51, 122, 240, 417 (probe A). If h3 from R1/R2 equals 122 the fiber is V(K2) through degree 3; then the fiber equals V(K2) provided K2 generates (Castelnuovo-Mumford regularity of std(K2) bounds the degree of any extra generator: compute `regularity(mres(sK,0))`, [I]). Iso: HF 17, 85, 265, 640 (matches sibling [M]).

**R8 Rees-side elimination (E8-bar, msolve) is the wrong tool.** The elimination ideal of a single variable a in 31 variables forces degree-7 F4 matrices of 4e5 rows. [I] The special fiber needs only L+m with t=0, so: (a) never eliminate with a; use R1 degree by degree on the 9 slice variables with 21 generators (231 products at d=2, 9 variables). Not run (time); (b) if the Rees ideal is wanted, use the Veronese/linear section: fiber relations of degree d only need y-degree d, so truncate with `degBound=2*...`, Singular `option(degBound)` is unsound for fibers; use R1 instead. msolve flags (`-m` splits matrices, `-u` rebuilds tables, `-l 1/2` exact) do not change the 407k-row step or the 2^28 table; a different variable order (y before t, a last) changes the block structure but not the 31-variable monomial count; `-s 24` already pre-sizes. msolve is a right tool only for zero-dimensional or small-variable elimination; for this positive-dimensional graph it is not.

## 3. msolve failure, precisely
esz is the monomial hash-table capacity; at doubling the code reallocates esz*evl*sizeof(exp_t) bytes for exponents (evl about 32 for 31 variables), plus the hd array and the column map, while the old block stays mapped [F compute-flags.md:30-40]. At esz=2^28 that is about 16 GiB (16-bit exponents [I], unverified: no source in tree) to 32 GiB for exponents alone. The trigger is the degree-7 round with 407,116 pairs. `-m N` caps pairs per matrix; the table still receives every monomial. `-u` drops stale monomials but the same step reaches the same esz [F u.log]. F4 option `-l 1` vs `2` changes linear algebra, not the table. Truncating the input is unsound for an elimination. Conclusion: msolve is not the tool.

## 4. Execution plan (estimates inferred)
| Job | Route | Substrate | Mem / time [I] |
|---|---|---|---|
| X-,X+ d=2 (K2) | R1, 7 vars | build host | 2 GiB, minutes |
| X-,X+ d=3 (122 normal cubics) | R1+R2 | Azure FX4 or Kaggle CPU, one job per VM | 8-32 GiB, hours |
| X- components | R3 | build host | done (1 s) |
| X+ components | R1 K2 then R3 | build host | minutes |
| Iso K2 components | R5, R4 | build host, M2 | unknown; cap 8 GiB |
| E8-bar to N+ | R1 d=2 on 9 vars, R2, then R3 | Kaggle CPU | 4-16 GiB, hours |
| W8 to N- | R1 d=2 with 325 products | Azure 84 GB, alone | 20-60 GiB, hours |
Run with cgroup `MemoryMax`, never `prlimit --as` (it killed xp_np, msolve). One job per VM, never three on 4 vCPU. Checkpoint: write K_d (`write(":w ...")`) after each degree; R1 stages are restartable from sJ.

## 5. Packages
Macaulay2 1.26, LinBox and Singular modular.lib are installed and suffice. Normaliz only if a multigrading makes components toric (moderate build risk). OSCAR.jl and msolve master are not worth it.

## 6. Purpose-level reformulations (coordinator's list)
- **Fiber over one point + stabilizer decomposition** (preserves exactly; this is what the runs already compute). Yields: the whole fiber over the chosen point. Add: decompose F_d as a representation of the compact stabilizer K_p (su(2)+u(1) at X, nullity-8 record); the multigraded method R5 is its torus part. Yields: components up to the group, not just degree.
- **Limits of ker L_y as y to Z directly.** Compute in the 4-dim kernel Grassmannian: the Gauss map y to ker A(z,conj z) in Gr(4,16); the limit set is the closure fiber over p, of dimension at most 3. Yields the attaching datum itself, but is a different (weaker, smaller-ambient) object than Proj F(I): image of the fiber under a map. Changes the presentation, preserves the limit set if I is the Gauss-graph ideal [I]; check with the 2j-c arcs.
- **Implicitize limits along curves.** Sampled arcs give a lower bound on the fiber (dimension, components touched). Yields lower bounds only; use as the falsifier for R3 components (every arc limit must lie on the claimed fiber).
- **Weaker invariants:** analytic spread = dim F = (fiber dim)+1 from h_d growth, via R1 alone through d=3 plus R7; changes the question from components to dimension and degree.

## 7. Where the formulation could change
- Replace G by Nakayama-minimal generators (already done for 2j-c): preserves F exactly.
- Remove slice variables J solves linearly (elimpart): preserves.
- Use the 12-variable reduced ring (y1,y5,y6 dropped): preserves the support, changes the nilpotent structure of F (fiber reduced, h_d not preserved).
- Compute V(K2) only (xm_nm): upper bound on the fiber; equals it only if R7 shows no cubic or higher relations.

## 8. Critique of the Codex consult
codex-consult-v2.md did not exist when this plan was written; no critique.
