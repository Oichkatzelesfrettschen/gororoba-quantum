# A_5 exceptional fibers: measured results, tested hypotheses and what survives

The open claim `dimension32-global-topology` needs the attaching data of the A_5 zero-divisor strata: how the
kernel fibers on a nullity-8 orbit closure Y specialize as a point of Y approaches a smaller orbit Z in its closure
([kernel-bundles program](../../design/a5-kernel-bundles-nullity8-program.md)). The algebraic object is the
exceptional fiber of the blow-up of Y along the kernel-coordinate ideal I = (G) at a point of Z, with coordinate ring
the fiber cone F(I) = sum_d I^d / m I^d. Its Hilbert function h_d, dimension, degree and components describe the set
of limiting directions; the limiting kernel 8-planes along those directions are the attaching datum itself.

Every computation below runs over F_32009 with i = 10754 (a split prime, so the Q(i) inputs specialize without an
extension field), in global monomial orderings, each Singular job in a cgroup scope with `MemoryMax` and
`MemorySwapMax=0`. Results over F_p certify that reduction only; a characteristic-zero statement needs a specialization
argument (a common model over a localization of Z[i] whose standard bases, membership identities and ranks specialize
at the chosen prime), and agreement at a second prime is a consistency check rather than that argument. The run directories, logs and normal-form files are unretained working data in the
git-ignored `docs/local/a5-failed-runs/`; a result enters the tracked record through the
[kernel-attachments evidence](../../evidence/a5-kernel-attachments/README.md) and its ledger.

## Pairs

| Pair (Y -> Z) | Ambient generators of G | Germ dimension bound on the fiber |
|---|---|---|
| X+ -> N+, X- -> N-, one isomorphism class | 15 | 3 |
| Iso (Iso -> N+ and Iso -> N- share J and the span of G) | 17 | 4 |
| E8-bar -> N+-, one isomorphism class | 21 | 4 |
| W8 -> N-, W8 -> N+, one isomorphism class | 24 | 5 |
| E8-bar -> VB | 10 | not derived |

## Methods and their outcomes

**Degree-by-degree membership rank.** For each degree d, the products of d generators reduced modulo J, then exact
membership in J + m P_d in a global ordering (exact because the quotient is killed by m), Nakayama normal monomials
from the certified relations of degree d-1, and the F_p rank and left kernel with FLINT. It replaces the local `ds`
syzygy computation, which took 25,459 s against 17 s for the same X- degree-2 count. It succeeded on every pair it
ran on and certifies only the degrees it computes.

| Pair | h_1, h_2, h_3 (h_4) | New relations beyond the quadrics K2 | Cost of the largest degree |
|---|---|---|---|
| X+-, X- | 15, 51, 122, 240 | none in degrees 3 and 4 (degree 4 on X-; X+ by the sign symmetry) | 14,480 s at degree 4 (Kaggle CPU) |
| Iso | 17, 85, 265, 640, 1316 (degrees 4 and 5 at 32009 and 32029) | none in degrees 3 to 5: r_16 = 1,316 = the degree-5 K2 count at 32009 and at 32029 (1,040 s) by the linear-algebra truncated rank (1,062 s, 11,260,540 KiB on the workstation); degree 4 by the full std on an 84 GB cloud VM (std 37,629 s, basis size 1,879, reduce 5,916 s, FLINT rank 640 over 141,676 monomials) and again by the jet-truncated rank below | 37,629 s at degree 4 (full std), 3,113 s (jet, N = 13) |
| E8-bar -> N+- | 21, 83, 225 (148 quadrics at 32009 and 32029; degree 3 at both primes) | none in degree 3: r_11 = 225 = the degree-3 K2 count, computed on N- at 32009 in quotient mode (Singular export 3,506 s, 2,528,352 KiB) and in raw mode with no Singular stage (4,575 s, 34.4 GB on the workstation) with equal block ranks 49 + 42 + 67 + 67, on N- at 32029 in raw mode (4,526 s) and on N+ at 32029 in quotient mode (3,346 s); the r_N ladder reads 144, 191, 225 at N = 9, 10, 11; each N- value holds for N+ by the pair flip | 3,535 s at degree 3 (quotient mode) |
| W8 -> N- | 24, 156, 600, 1725 (degrees 3 and 4 at 32029 and 32009; degree 4 at 32009 in 1,321 s) | none in degrees 3 and 4: r_13 = 1,725 = the degree-4 K2 count at 32029 (1,440 s, 12,556,708 KiB on the workstation); r_10 = 600 = the K2 count at both primes by the linear-algebra truncated rank below (raw mode 473 s, 3,146,068 KiB at 32029; quotient mode 2,141 s at 32029 and 2,460 s at 32009); every Singular route stopped for memory first: 14 GB on the host, the 30 GB Kaggle limit after 18,999 s, the kernel's cgroup OOM on an 84 GB cloud VM (78 GB scope) after 61,304 s at 77.8 GiB resident, all inside std(J + m P_3) with 600 targets, and the jet std at N = 10 at a 24 GB cap after 5,449 s | 5,619 s, 6.7 GB at degree 2; 473 s at degree 3 (linear algebra) |
| E8-bar -> VB | 10, 34, 80, 155 | none in degrees 3 and 4; degree 5 stopped at the 12 h stage cap inside std(J + m P_5), after 9 s of products, peak 12 GB (host, 15 GiB) | 5,184 s at degree 4, 2.4 GB |

**Sign symmetries between the paired orbits.** Under t9 -> -t9, J- = eps J+ and G- = delta G+ coefficient by
coefficient for X, and likewise for W8 -> N+ against W8 -> N-; those fibers follow by y_j -> +-y_j. For E8-bar,
t9 -> -t9 alone leaves the combined G span at rank 41 of 42, and the pair flip t8 -> -t8, t9 -> -t9 carries every
generator of J+ and G+ to plus or minus the N- generator of the same index, with one sign pattern at
the three producer specializations (p, i) = (32009, 10754), (32009, 21255) and (32029, 9115) (16 J and 21 G generators). The map fixes the origin, so at each of
these specializations it induces F(I+) ≅ F(I-) through y_i -> c_i y_i, with c_i the generator signs; moving the 148
N- quadrics by these signs gives exactly the N+ quadric span at 32009 and 32029 (ranks 148, 148, union 148). Every
E8-bar -> N- certificate at these primes therefore holds for N+, and conversely. The producer derives J and G over
Q(i) and emits them only at a split prime, so the identity over Q(i) itself rests on these three specializations
until the producer's characteristic-zero generators are compared directly. Iso -> N+ and Iso -> N- have
equal J and equal G span under the identity coordinates (each G generator is plus or minus its partner). The X and W8
germs differ already at dim k[t]/(J + m^3) = 27 against 35. A profile-pruned signed-permutation sweep found these
maps and no others, but its pruning reads presentation-dependent coefficients and can reject a valid map (J_b = 2 J_a
is pruned), so it certifies only the maps it found.

**Germ fingerprints.** The quotient lengths q_N = dim k[t]/(J + m^N) separate the classes at small N and agree
within each class at all three specializations (Codex re-audit, `germ-checks.jsonl`):

| Class | Variables | J, G generators | q_2, ..., q_7 |
|---|---|---|---|
| X+-, one class | 7 | 12, 15 | 8, 27, 66, 135, 246, 413 |
| E8-bar -> VB | 8 | 17, 10 | 8, 27, 66, 135, 246, 413 |
| Iso | 6 | 1, 17 | 7, 27, 77, 182, 378, 714 |
| E8-bar -> N+-, one class | 9 | 16, 21 | 9, 39, 117, 283, 594, 1127 |
| W8 -> N+-, one class | 7 | 1, 24 | 8, 35, 112, 294, 672, 1386 |

X and E8-bar -> VB share tangent embedding dimension 7 (VB's J carries the linear form 2 t2 + t8) and every measured
length, through N = 16 in the quotient-size probes (4,746, 6,105, 7,736 at N = 14, 15, 16). Their minimal generator
counts h_1 = 15 and 10 rule out an isomorphism of the ideal pairs; an isomorphism of the germs alone is open, and it
would let the E8-bar -> VB quotient computations run in X's presentation, where std(J + m^17) took 201 s against more
than 3,600 s for VB's. Their tangent cones, computed in global orderings by the normal-cone deformation, agree in
every invariant measured: after VB's linear form, each is a double structure on a linear 4-space cut out by 9 quadrics
with Hilbert numerator 1 - 9t^2 + 18t^3 - 15t^4 + 6t^5 - t^6, so the tangent cone does not separate the germs.

**Jet-truncated membership rank.** Adding m^N to J + m P_d makes the quotient finite-dimensional, so its standard
monomials all have degree below N; cutting every product and generator below degree N (`jet`) before
std leaves the ideal unchanged modulo m^N. The rank r_N of the degree-d products modulo J + m P_d + m^N is a lower
bound on h_d and nondecreasing in N. It reaches h_d for N large by the Krull intersection theorem in the localization
(the target space I^d/mI^d is finite-dimensional and killed by m), but no N is computed in advance here, so the method
certifies h_d only when r_N equals the K2 count HF(k[y]/K2, d); a plateau below that count certifies nothing and
refutes nothing. For Iso, whose G generators have orders 2 and 3 and whose J is one homogeneous quadric, a degree-d
product has no term of degree below 2d before reduction and reduction keeps that bound, so N must exceed 2d; the
other fibers have generators of lower order (E8-bar -> VB: 8 of its 10 G generators have order 1; E8-bar -> N+-: 2 of
21), so their starting N comes from the measured filtration of their own inputs. At Iso degree 4, N = 8 gave r_8 = 0 (all 640 normal forms vanish, since N = 8 = 2d; at N = 13 every
normal-form monomial has degree 8 to 12) after 2,621 s of an
untruncated std, and N = 13 with jet-cut inputs gave r_13 = 640 over 3,105 monomials in 3,113 s with an 11 GB peak,
12 times faster than the full std stage and 14 times faster than its std plus reduction. The two membership
computations share the products and the FLINT rank script; an independent pure-Python elimination of the jet normal
forms gives rank 640, and a direct linear-algebra count of K2 in degree 4 (4,845 monomials minus rank 4,205) gives
the upper bound 640, so the lower and upper bounds meet.

**Diagonal sign group.** An exhaustive search over every subset of variables (all 2^n diagonal sign changes) finds,
for each pair at 32009, exactly a Klein four-group preserving span(J) and span(G): (t2, t4, t6), (t2, t5, t7) and
their product (t4, t5, t6, t7) for W8 -> N-, X- and Iso; (t2, t4, t6, t8), (t2, t5, t7, t8) and (t4, t5, t6, t7) for
E8-bar -> N+-; (t1, t3, t4, t7), (t1, t5, t6, t7) and (t3, t4, t5, t6) for E8-bar -> VB. No other
sign change survives; single flips enlarge the W8 span from rank 24 to 45 to 48. The W8 group holds at 32029 as well,
and at both primes every W8 generator has a pure character, (0,0) 6, (0,1) 7, (1,0) 7, (1,1) 4; the Iso generators also have pure characters, (0,0) 4, (0,1) 5, (1,0) 5, (1,1) 3 (an
earlier "mixed" reading included t3 -> -t3, which is not a symmetry, among the test flips). The Smith form of the
lattice of exponent differences within every displayed J and G polynomial has invariant factors 1, ..., 1, 2, 2 at all
27 headers of the three producer specializations, so the diagonal scalings that keep every displayed generator an
eigenvector form exactly this group of order 4 over an algebraic closure in odd characteristic; a diagonal action that
mixes generators lies outside that computation. The grading splits a
linear-algebra formulation of the truncated rank into four independent blocks whose ranks add; Singular's std does
not exploit it. The same group on every pair suggests a common origin in the Cayley-Dickson sign structure; that
origin is an inference, not a derivation.

**Truncated rank by linear algebra (`fiber_rank.py`).** The same r_N comes from finite-dimensional linear algebra
over F_p with no standard basis: V_N is the space of polynomials of degree below N, W_N the image of the ideal
(J, m P_d) in V_N, computed as the span of the truncated generators J and t_k P closed under multiplication by the
variables, and r_N the rank of all degree-d products of G modulo W_N. Products are built as jets (truncated after
every multiplication) straight from the header's J and G, every degree-d monomial in G is a product, and no previous
relation or target basis enters, so the method shares no code and no intermediate file with the Singular driver. The
closure is semi-naive (each round multiplies only the basis vectors whose pivots are new) and runs in each character
block of the Klein four-group separately, with multiplication by t_k carrying block chi to chi + chi(t_k); reductions
against the echelon basis run as float64 matrix products whose partial sums stay below 2^53, so they are exact, and
the residual rows go to FLINT's `rref`. It reproduces every Singular value it was checked against:

| Pair, prime | d | N | r_N | Singular value it reproduces | Seconds |
|---|---|---|---|---|---|
| Iso, 32009 | 3 | 9, 10, 11 | 216, 265, 265 | jet ladder 216, 265, 265; h_3 = 265 | 8, 15, 27 |
| Iso, 32009 | 4 | 13 | 640 | full std and jet ladder, h_4 = 640 | 314 |
| Iso, 32029 | 4 | 13 | 640 | jet ladder, h_4 = 640 | 281 |
| E8-bar -> N-, 32009 | 2 | 6, 7, 8 | 65, 65, 83 | h_2 = 83 (13,827 s on Kaggle) | 7, 18, 53 |

Engine v6 (sha256 prefix 130f35904d21f5b4) replays every row of this table with identical r_N, and passes an
integer-only oracle on 972 small-ring cases in raw, unsplit, direct and quotient modes plus 21 fixtures built from
reviewer counterexamples (signed products inside a monomial, characteristic 2, absent character blocks, one-letter
variable names in Singular output). It then certified, at the K2 count and with no Singular value to reproduce:

| Pair, prime | d | N | r_N | K2 count | Seconds, peak |
|---|---|---|---|---|---|
| W8 -> N-, 32029 | 3 | 9, 10 | 551, 600 | 600 | 200 (raw, N = 10) |
| W8 -> N-, 32009 | 3 | 10 | 600 | 600 | 243 (quotient) |
| W8 -> N-, 32029 | 4 | 13 | 1,725 | 1,725 | 1,440, 12.6 GB |
| Iso, 32009 | 5 | 15, 16 | 1,195, 1,316 | 1,316 | 1,062, 11.3 GB (N = 16) |
| E8-bar -> N-, 32009 | 3 | 9, 10, 11 | 144, 191, 225 | 225 | 3,535 quotient, 4,575 raw (N = 11) |
| W8 -> N-, 32009 | 4 | 13 | 1,725 | 1,725 | 1,321, 12.5 GB |
| Iso, 32029 | 5 | 16 | 1,316 | 1,316 | 1,040, 11.5 GB |
| E8-bar -> N-, 32029 | 3 | 11 | 225 | 225 | 4,526 raw, 34.4 GB |
| E8-bar -> N+, 32029 | 3 | 10, 11 | 191, 225 | 225 | 3,346 quotient |
| X-, 32009 | 5 | 15, 16, 17, 19, 20 | 201, 201, 296, 417, 417 | 417 | 10,313 quotient (N = 17, v6); 3,784, 5.2 GB (N = 19, v7, Kaggle 4-core Xeon); 6,727, 6.9 GB (N = 20) |
| E8-bar -> VB, 32009 | 5 | 16 | 266 | 266 | 698 quotient (v7, workstation) |

A value below the count bounds h_d from both sides (W8 degree 3, N = 9: 551 <= h_3 <= 600; X- degree 5, N = 17:
296 <= h_5 <= 417), and the X- ladder repeats 201 at N = 15 and 16 before rising to 417 at N = 19, a second measured
plateau. The X- degree-5 and E8-bar -> VB degree-5 rows come from engine v7 (products built from the quotient
multiplication tables, sha256 prefix a197799d97287b78), whose records bind engine and header hashes, d, N and rank.


The four block ranks add to the unsplit rank (Iso degree 3, N = 9: 54 + 50 + 56 + 56 = 216, and the W_N ranks
409 + 388 + 387 + 387 = 1,571 in both forms), and enumerating every monomial multiple of every generator instead of
the closure gives the same r_N (Iso degree 3, N = 9: 216). The E8-bar -> N- degree-2 ladder sits at 65 for N = 6 and
7 and jumps to 83 at N = 8: a measured plateau below h_d, which is why a plateau certifies nothing.

**Pivot saturation of the Rees ideal (H : g^inf, then t = 0).** The pivot is a nonzerodivisor modulo J on every pair
tried, and J is radical and prime through the origin on all five pairs checked, so the route is valid. It never
finished:

| Pair | Pivot | Limit reached | Peak |
|---|---|---|---|
| X- | G_11, 64 terms | 3 h, 12 h, 12 h | 9.4 GB |
| Iso | G_16, 41 terms | 6 h | about 10 GB |
| E8-bar -> VB | G_3, 9 terms | 2 h | |
| E8-bar -> N+ | G_19 | 10 h (cloud VM, 78 GB cap) | 72 GB |
| E8-bar -> N- | G_19 | stopped | |
| W8 -> N- | | cloud VM lost contact after 25 min at 13 GB; incomplete, not a stall | |

**Candidate-ideal verification (std of a candidate L with L : g = L).** On E8-bar -> VB, std(L) in 18 variables
passed 3 GB in 14 minutes without finishing.

**Full Rees-graph elimination with msolve.** E8-bar -> N+ died in the degree-7 F4 step (407,116 pairs) under every
cap tried. E8-bar -> VB on a Kaggle TPU VM reached a degree-16 matrix of 86,010,243 x 87,648,606 at about 209 GB
resident after about 2 h before the session ended; extrapolated growth puts degree 19 near 9.2 h, past one session.

**Global minimal-prime decomposition first (`minAssGTZ`).** The generic coordinate change densifies the input: Iso
ran 40,000 s without a result. Taking the radical first and `minAssChar` decomposes X- in 1 s.

**Structure of the quadric ideal K2** (radical, minimal primes as projective dimension and degree, 3 GB, 600 s):

| Pair | K2 radical | Radical Hilbert function | Minimal primes |
|---|---|---|---|
| X- | no | 12, 45, 112, 225 | one: (3, 12) |
| E8-bar -> N+- | no | 16, 69, 195, 440 | two: (4, 11), (3, 4), computed on N+ and again on N- (9 and 14 linear generators, 12 s, Kaggle CPU), as the pair flip requires |
| E8-bar -> VB | yes | 10, 34, 80, 155 | two: (3, 3), (3, 4) |
| Iso | radical on 12 of 17 affine charts (8,000 s per chart); 5 charts unfinished | | one facstd piece, projective dimension 4, degree 23; prime split not reached (whole-ideal `minAssChar` and `minAssGTZ` each past 41,000 s) |
| W8 -> N- | yes | 24, 156, 600 | K2 = P cap (K2 : P), checked by recomputing the intersection: P is prime of projective dimension 5 and degree 20 with 9 linear generators (the unique minimal prime of facstd piece 1, `minAssChar` 1,114 s; the global radical test took 24,548 s; the kernels report seconds in fields named `_ms`) and contains K2; K2 : P has projective dimension 5, degree 30 and 131 generators (quotient 26 ms); all at p = 32009, where K2 has the same Hilbert series as at 32029, so the degrees add to 50; P and K2, hence K2 : P, are fixed by the diagonal Klein four-group; K2 : P is not yet decomposed (`minAssChar` on facstd piece 2 ran past 41,000 s) |

The quadric schemes V(K2) have projective dimension 3 and degree 12 (X-), 4 and 11 (E8-bar -> N+-), 5 and 50 (W8,
h = 24, 156, 600, 1725), 3 and 7 (E8-bar -> VB, h = 10, 34, 80, 155). Each dimension where a germ bound exists
equals that bound.

**Formal arcs on E8-bar -> VB.** The tangent cone of the strict transform has dimension 4 and degree 2 and is not
reduced; its support is the linear space V(t2, t8, t5 - t6, t3 + t4). The strict transform has Jacobian rank 3, not 4,
over that space, so a Hensel lift at order 1 has a singular Jacobian (det M = 0). On the normalization of the strict
transform each point of that space carries two smooth branches, the 16 x 16 Jacobian is invertible, and Hensel lifting
gives a unique formal arc per branch with valuation 2. The leading G-vector F(u) is rational in (u1, u2, k) after
u3 = -2k/(k^2 + 3); it was reconstructed by interpolation from 48 points per branch and agrees on 8 further points per
branch. All 9 generators of the degree-4 prime vanish on F(u), and the projective map has generic rank 3 over
F_p(u1, u2, k), so the arcs sweep the degree-4 component. All 7 generators of the degree-3 prime are nonzero on both
branches and on every numerical arc in the charts t1 = 1 and t3 = 1. Both primes are geometrically irreducible by
explicit rational parametrization; Singular's absolute decomposition refuses positive characteristic.

**Second prime.** Inputs at p = 32029, i = 9115 are regenerated from the Q(i) producer for all ten slugs, and the
regeneration at 32009 reproduces six computed inputs byte for byte and the others up to term order, sign or an
equivalent generator presentation. Degree-by-degree membership ranks at 32029 equal those at 32009 for E8-bar -> VB
(34, 80), X- and X+ (51, 122, with 69 quadrics), Iso (85, 265, with 68 quadrics), W8 -> N- (156) and E8-bar -> N+-
(83, with 148 quadrics each); each is a fiber-cone rank from its own degree driver run, not a value of
HF(k[y]/K2, d). Iso degree 4 at 32029 reaches r_13 = 640 by the jet-truncated rank (3,877 s, 10.9 GB resident),
equal to the 32029 K2 count 4,845 - 4,205 = 640 from the 68 quadrics of the 32029 degree-3 relations, so
h_4 = 640 holds at both primes; a pure-Python elimination of the 640 normal forms over 3,105 monomials returns the
same rank.

**Nullity-16 boundary fibers.** Eight fibers complete: a projective plane (B9), a conic (V) and points (VB, Va).
Ten rows stop at the modular Rees-fiber stage.

## Operational failures and their mechanisms

| Failure | Mechanism | Rule it fixed |
|---|---|---|
| X+ degree 3 killed with 6.7 GB resident and 22 GB free | `prlimit --as` caps reserved address space, not memory | cgroup `MemoryMax` only |
| Nullity-16 producer: Singular "no more memory" at 2.5 GB | a Python helper set `RLIMIT_AS` to 4 GiB in the parent; every Singular child inherited it | a solver driver sets no address-space limit |
| Orphaned Singular processes after a timeout | the outer timeout killed Python before its process-group kill ran | SIGTERM raises SystemExit; a finally block kills and reaps the group |
| A 24 h E8-bar -> VB run that no deadline stopped | a deadline-extension script stopped the `timeout` supervisor with SIGSTOP | extend a deadline with a new timer or a cgroup, never by stopping the supervisor |
| Session killed with every job, 2026-10-29 09:45 UTC | systemd-oomd acts on the whole user-session slice at high memory pressure | each heavy job in its own capped scope; reachable caps below physical memory |
| W8 degree 2 exit 137 at 6 GB | the job's own cgroup limit | passed at 12 GB |
| Kaggle TPU v5e-8 never assigned in 6 h | one batch TPU slot per account, held by a queued version the API cannot cancel | delete the queued kernel in the web UI, then push |
| Iso degree 4 and W8 degree 3, first cloud attempts, killed at 20:40 UTC | the trial VMs carried a DevTestLab daily auto-shutdown | disable the schedule at VM creation |
| E8-bar -> VB chart-5 run killed 10.2 h in | a job-keyed watcher deallocated the VM it shared with the finished Iso job | copy and hash-verify the whole work tree and confirm zero live solver processes before deallocating; never co-locate under a job-keyed deallocator |
| W8 degree 3 killed at 77.8 GiB after 61,304 s | the untruncated std(J + m P_3) reached the 78 GiB scope limit; the partial basis lives only in RAM | bound the problem (jet truncation) before buying memory |
| Copied-back cloud archives lost on a session restart | they sat in the session's temporary scratch directory | run state and results live in the repository's ignored `docs/local/`; recovered from the VM disks |
| Truncated rank 0 at Iso degree 4, N = 8, after 2,621 s | N at or below the products' m-adic order 2d, and untruncated inputs carried into std | start N above 2d and cut inputs below degree N first |

## Hypotheses tested against the data

**The fiber cone is generated by its quadric relations, F(I) = k[y]/K2.** Survives through degree 4 on E8-bar -> VB
(h_4 = 155 equals the quadric value, no new relation), on X (h_4 = 240), on W8 (h_4 = 1,725 at both primes) and on Iso (h_4 = 640, by the full std and
by the jet-truncated rank), through degree 5 on Iso at both primes (h_5 = 1,316), and through degree 4 on E8-bar -> N+- at both primes (h_4 = 495), where degree 5 lies between 861 and 952.
If it holds in every degree, the fiber is all of V(K2) and contains the degree-3 component that no arc has reached.
If the fiber were the degree-4 component alone, its Hilbert function would grow like 4d^3/6 against 7d^3/6 for
k[y]/K2, so new relations must appear in some degree; none appears through degree 4.

**The quadric ring k[y]/K2 is Cohen-Macaulay.** Survives for E8-bar -> VB, Iso and W8 -> N-; falsified for X- and
E8-bar -> N-. A graded quotient of Krull dimension a is Cohen-Macaulay exactly when a general linear system of
parameters is regular, that is when the quotient by a general linear forms has length equal to the degree e; a
non-general choice can only raise the length, and one choice with length above e proves the ring not Cohen-Macaulay,
since every system of parameters of a Cohen-Macaulay ring is regular. At 32009 the lengths are 7 = e (E8-bar -> VB, a = 4, minimal free
resolution linear with Betti numbers 21, 70, 105, 84, 35, 6), 23 = e (Iso, a = 5), 50 = e (W8, a = 6), against 15 > 12
(X-, a = 4, whose resolution has projective dimension 14, so depth 1) and 20 > 11 (E8-bar -> N-, a = 5, as its
non-equidimensional V(K2) requires). The h-vectors are 1, 6 (VB), 1, 12, 10 (Iso) and 1, 18, 27, 4 (W8). The linear
resolution makes V(K2) of E8-bar -> VB 2-regular, so by Eisenbud, Green, Hulek and Popescu (arXiv math/0404517,
Theorem 0.4) it is a linearly joined union of varieties of minimal degree; computed directly, its components are a
threefold of degree 3 spanning a P^5 and a threefold of degree 4 spanning a P^6, each of minimal degree in its span,
meeting in the P^2 where the two spans meet, and K2 is their intersection.
Consequence: a Cohen-Macaulay k[y]/K2 has only minimal associated primes, all of dimension a, so a nonzero L/K2
has dimension a and lowers the multiplicity. For E8-bar -> VB, Iso and W8, F(I) = k[y]/K2 in every degree exactly
when the analytic spread of I is a and the multiplicity of F(I) is e, that is (4, 7), (5, 23) and (6, 50); this route
does not need K2 radical. The degree-by-degree data cannot decide it, since equal Hilbert functions through degree 5
leave the multiplicity of F(I) open; the multiplicity is an asymptotic invariant, and computing it is the arc program.
For E8-bar -> VB the criterion sharpens: the analytic spread is already 4, because the certified degree-4 component lies
in the fiber, and a Cohen-Macaulay F(I) has multiplicity sum h_i >= 1 + h_1 = 1 + (10 - 4) = 7 while every
4-dimensional quotient of k[y]/K2 has multiplicity at most 7, so F(I) is Cohen-Macaulay exactly when
F(I) = k[y]/K2.
For W8 -> N- the criterion becomes geometric. Each certified degree d <= 4 is a sandwich: the truncated rank r_N
bounds h_d from below, and the 144 degree-2 relations of the membership receipt, all in L, bound it from above by the
K2 count, so every relation of F(I) through degree 4 lies in the ideal of the 144 quadrics, and a relation outside K2,
if one exists, starts in degree 5 or later, where no finite ladder closes the question. V(K2) has projective dimension
5, the germ bound, and K2 = P cap (K2 : P) is radical with P prime of degree 20 and K2 : P of degree 30 (K2 : P lies
outside P, or the degrees could not add to 50). Because a Cohen-Macaulay k[y]/K2 has only top-dimensional
associated primes, F(I) = k[y]/K2 exactly when Proj F(I) contains V(P) and every component of V(K2 : P): a fiber
inside V(P) has multiplicity at most 20, one inside V(K2 : P) at most 30, and set-theoretic equality forces
multiplicity 50 since each component then counts at least once. Arc families reaching a general point of each
top-dimensional component decide it, which makes the decomposition of K2 : P the prerequisite.

**The fiber cone F(I) is Cohen-Macaulay.** Falsified for X- and E8-bar -> N+- if their analytic spread equals a. By
D'Cruz, Raghavan and Verma (arXiv math/0212119, Theorem 2.1) a Cohen-Macaulay F(I) of dimension a has (1 - t)^a
times its Hilbert series a polynomial with nonnegative coefficients; the certified degrees alone give 1, 11, -3, 4, -1
for X- at a = 4 and 1, 16, -12, 10 for E8-bar -> N+- at a = 5. Open for E8-bar -> VB, Iso and W8, where the same
numerators are nonnegative and terminate.

**The fiber cone is reduced.** Falsified for X- and E8-bar -> N+-. Their radicals contain 3 and 5 linear forms
outside K2, and since F(I) agrees with k[y]/K2 in degree 1, those forms are nilpotent in F(I). This makes the graded
ring F(I) nonreduced; the exceptional fiber Proj F(I) is nonreduced only if a nilpotent survives on some chart, since
nilpotents supported at the irrelevant ideal vanish on Proj (k[x,y]/(x^2, xy) is nonreduced with reduced Proj), and
deciding that needs the saturation of L. The reduced support lies
in a P^11 (X-) and a P^15 (E8-bar -> N+-). Survives for E8-bar -> VB at the level of K2. Untested for Iso and W8.

**The exceptional fiber is irreducible.** Falsified for V(K2) of E8-bar -> VB (degrees 3 and 4) and of E8-bar -> N+-
(dimensions 4 and 3, so not even equidimensional), which also refutes the irreducible 2 x 7 scroll proposed for
E8-bar -> VB. Survives for X-. Reopened for the fiber of E8-bar -> VB itself: if the degree-3 component lies outside
the fiber, the fiber is the single degree-4 component.

**The limiting kernel is the same along every path into Z.** Falsified for the instances of the nullity-8 record,
which found path-dependent boundary limits. For the five fibers here the data bound V(K2), not the actual fiber
support, from below only through the certified degree-4 component of E8-bar -> VB, so path dependence on each of them
needs its own arc families with two distinct limiting planes, or a positive-dimensional image of the fiber in the
Grassmannian.

**Sign-paired orbits have isomorphic fibers.** Survives for X+ with X-, W8 -> N+ with W8 -> N- and E8-bar -> N+ with
E8-bar -> N- by explicit diagonal sign symmetries (t9 alone for the first two, t8 and t9 together for E8-bar). The X+ quadric ideal at 32029 (`working/runs/k2struct/xp_p2.sing`, radical plus `minAssChar`)
reproduces the X- structure at 32009 line for line: K2 and its radical are projective threefolds of degree 12, K2 is
not radical, h = 15, 51, 122, 240 for K2 and 12, 45, 112, 225 for the radical, and the single minimal prime has
projective dimension 3, degree 12 and three linear generators. For E8-bar the pair flip explains the equal Hilbert
functions (21, 83, 225) and the shared minimal-prime types (4, 11) and (3, 4) that were first read as evidence only.
Each symmetry induces a graded ring isomorphism F(I+) ≅ F(I-), y_i -> c_i y_i, in every degree, so a degree certified
on one side holds on the other with the same strength; `build_registry.py` records it as `transported_from`, citing
the sign-isomorphism witness. W8 -> N+ and X+ at 32009 and E8-bar -> N+ in degrees 2 and 3 at 32009 rest on it.

**Results at 32009 hold in characteristic zero.** Two primes agree on every degree computed at both (listed under
Second prime); agreement at two primes is a stability check, and a characteristic-zero statement needs a modular
argument with controlled bad primes. Neither bound transfers by itself: rank over F_p is at most the rank over Q(i)
only for one fixed matrix, the truncated-rank matrices are assembled from normal forms modulo J, and the upper bound
rests on membership identities checked mod p, so the lower bound also needs J's standard basis to specialize at p.
Falsifier: any h_d at 32029
that differs from 32009; a mismatch alone shows instability, and naming the exceptional prime needs a third.

**A completion by Groebner elimination fits this hardware.** Falsified for every formulation tried: pivot
saturation (six stalls, up to 72 GB), candidate-ideal std, full-graph msolve, local orderings and minAss-first.
Raising caps changes the wait, not the algorithm.

**Order-1 arcs suffice to certify each component.** Falsified on E8-bar -> VB by the singular Jacobian over the
non-reduced tangent cone; arcs on the normalization replace them.

## What survives

- E8-bar -> VB: Hilbert function equal to the quadric values through degree 5 at 32009 (h_5 = 266); the fiber
  contains the geometrically irreducible degree-4 three-fold, certified over F_32009 by a dominant arc family; whether
  the degree-3 component belongs to it is open, and the arcs of charts 3, 5 and 7 all land in the degree-4 component.
- X-: Hilbert function equal to the quadric values through degree 5 at 32009 (h_5 = 417); V(K2) has one irreducible reduced support of projective dimension 3 and degree 12 inside a P^11, and the fiber
  has 3 nilpotent linear directions; the fiber's support lies in that threefold and equals it only with an arc
  certificate, and the nilpotent part needs a scheme-theoretic construction rather than arcs.
- Iso: Hilbert function equal to the quadric values through degree 5 at both primes (h_4 = 640 by two methods,
  h_5 = 1,316); K2 radical on 12 of
  17 charts; no prime decomposition yet.
- W8 -> N-: Hilbert function equal to the quadric values through degree 4 at both primes (h_4 = 1,725); K2 radical, equal to P cap (K2 : P) with P prime (5, 20) and K2 : P of projective dimension 5 and
  degree 30, not yet decomposed; W8 -> N+ follows through the t9 isomorphism; F(I) = k[y]/K2 holds exactly when
  arcs reach every top-dimensional component of V(K2).
- Coverage (`claims.json`): every pair is certified through degree 3 at both primes; through degree 4 for W8 and
  Iso at both primes and for X and E8-bar -> VB at 32009; through degree 5 for Iso at both primes and for X and
  E8-bar -> VB at 32009. All certificates hold over F_p only.
- E8-bar -> N+- (one class by the pair flip): Hilbert function equal to the quadric values through degree 3 at both
  primes (h_3 = 225, by two eliminations at 32009); non-reduced, and V(K2) not equidimensional, with minimal primes
  (4, 11) and (3, 4).
- Exact degree-by-degree rank, its jet-truncated form (certifying only at the K2 count) and arc families with exact
  containment checks are the working methods; the global elimination formulations tried (pivot saturation,
  candidate std, full-graph msolve, untruncated std beyond 78 GB) are retired, while bounded homogenized or
  Macaulay-matrix formulations remain untested.

## Prior work and neighboring theory

Four independent searches (zbMATH Open and web queries, a Codex search with 15 resolved identifiers, a Grok search
with 18, and a whole reading of the papers below) find no work that computes these fiber cones, their Hilbert
functions or these exceptional fibers; a fingerprint search of every PDF and text file in the owner's workspace
repositories (4,019 distinct PDFs with a text layer) and of OEIS finds none of the five Hilbert-function sequences,
the two OEIS matches being closed forms forced by an h-vector (E8-bar -> VB is A007584, the Hilbert function of every
4-dimensional quotient with h-vector (1, 6), the 2-regular threefolds of degree 7 among them). The closest prior work studies the same algebra on the open stratum: Skiouris,
"Aphanics at the pathion level" (Zenodo record 22082732, 2026; [note](../papers/skiouris-2026-aphanics-pathion.md))
stratifies the zero-divisor locus of the 32-dimensional algebra (kernel dimension 12 or 4 at dyadic basepoints,
Proposition 2.2) and computes the curvature and holonomy of the kernel bundle there, and "Algebraic hiddenness in the
sedenion algebra" (Zenodo record 22016333; [note](../papers/skiouris-2026-algebraic-hiddenness.md)) does the same at
dimension 16; neither takes limits at a stratum boundary, blows up or computes a fiber cone. The zero-divisor
zero-divisor and annihilator loci on which the stratification rests go back to Moreno (arXiv q-alg/9710013,
math/0512517), while the nullity-8, 12 and 16 orbit closures and their relations are this repository's; Zhilina (arXiv 2608.26893,
2608.28176) adds annihilator dimensions and orthogonality graphs, and Chan and Dokovic classify the sedenion
subalgebras. The neighboring arXiv papers named here, each read whole, supply no theorem whose hypotheses the A_5 ideals
are known to meet: Kustin, Polini and Ulrich (arXiv 1505.05210, Theorem 9.1, Corollary 9.3) need a homogeneous,
linearly presented height-3 Gorenstein ideal in a polynomial ring; Corso, Ghezzi, Polini and Ulrich (arXiv
math/0302241, Theorem 2.2) require, in their hypothesis (b), at most two homogeneous minimal generating relations in
degrees at most t when n >= ell + 2 (at most one when n = ell + 1), against 21 to 148 quadrics here; Cooper and
Price (arXiv 2104.13811) and Ansaldi et al. (arXiv 2512.16165, characteristic 0) treat homogeneous determinantal,
Pfaffian and Hankel ideals in polynomial rings; Kumar and Venugopal (arXiv 2302.07486, Theorem 3.12) prove Koszul
and Cohen-Macaulay diagonal subalgebras of the Rees algebra of a submaximal-Pfaffian ideal, a setting these ideals do
not enter, and I is not of linear type here, since a linear-type ideal has a polynomial fiber cone and
h_2 < C(h_1 + 1, 2); Ghorpade and Krattenthaler (arXiv math/0105151) transfer only to dimensionally proper
sections; Jeffries, Montano and Varbaro (arXiv 1308.0582, Theorem 3.1) need a standard graded domain, one generating
degree, maximal analytic spread and their saturation condition. D'Cruz, Raghavan and Verma (arXiv math/0212119, Theorem 2.1) give the one criterion that applies, used above.
Since L_a is skew for pure a (Zhilina, arXiv 2608.28176, Lemma 2.10 and Proposition 2.12), each nullity locus is a
linear section of a Pfaffian locus of the generic 32 x 32 skew matrix, not dimensionally proper at nullity 12 and 16;
Bertram (alg-geom/9707001, Theorem 3.3, p. 14) and Massarenti (arXiv 1803.09011, Construction 2.3) give the space of
complete skew forms as the ambient blow-up, without a fiber cone. Eisenbud, Green, Hulek and Popescu (arXiv math/0404517, Theorem 0.4) classify the 2-regular reduced schemes as
linearly joined unions of varieties of minimal degree, which describes V(K2) of E8-bar -> VB. Conca, Herzog and Valla
(J. Reine Angew. Math. 474 (1996) 113-138) compute special fibers of rational normal scroll ideals by Sagbi bases, and
Conca, Herzog, Trung and Valla (Amer. J. Math. 119 (1997) 859-901)
treat diagonal subalgebras of blow-ups of projective spaces; both are identified neighbors not yet read against
that ring, so no theorem of theirs is claimed to transfer. The reading
copies live in the owner's documents repositories.

## Ledger of hypotheses

Status vocabulary: *survives* (consistent with every test that ran, with the falsifier named), *open* (no deciding
test yet), *refuted* (a measurement or argument contradicts it), *rejected* (dropped on an argument without a
measurement), *superseded* (replaced by a stronger or cheaper route).

### Standing

| Hypothesis | Status | Deciding evidence or pending falsifier |
|---|---|---|
| F(I) = k[y]/K2 for E8-bar -> VB | survives through degree 5 at 32009 (h_5 = 266, r_16 by engine v7) | degree 6; degree 5 at a second prime |
| F(I) = k[y]/K2 for X+- | survives through degree 5 at 32009 (h_4 = 240; h_5 = 417, r_19, r_20 and r_21 by engine v7) | degree 6; degree 5 at a second prime |
| F(I) = k[y]/K2 for Iso | survives through degree 5 at both primes (h_5 = 1,316, r_16 by the linear-algebra truncated rank) and degree 4 at both primes (h_4 = 640 by the full std at 32009 and by the jet rank at N = 13 at both 32009 and 32029) | degree 6 |
| F(I) = k[y]/K2 for W8 | survives through degree 4 (h_4 = 1,725 at 32029 and 32009, r_13 by the linear-algebra truncated rank; h_3 = 600 at 32029 and 32009 by the linear-algebra truncated rank; the 32009 upper bound rests on the degree-2 receipt `distribute/out/a5-w8-receipt-p1` (h_2 = 156, 144 relations, membership failures 0, 6,560 s products std, 325 s membership, 6.7 GB), whose relation file spans the K2 of `runs/w8_a2` by its k2-span witness; W8 -> N+ carries degrees 1 to 4 at both primes by the t9 sign isomorphism) | degree 5 |
| F(I) = k[y]/K2 for E8-bar -> N+- | survives through degree 4 at both primes (h_4 = 495, r_15 by engines v9 and v11, r_16 by v11 at 32009); degree 5 open with 861 <= h_5 <= 952: exact arc families reach both minimal primes of sqrt(K2) at both primes (`evidence/a5-exceptional-fibers/arcs/`), so L lies in sqrt(K2) and F(I) surjects onto k[y]/sqrt(K2), whose degree-5 value is 861; the truncated ranks r_15 = r_16 = 742 are a truncation plateau | the exact h_5, by a degree-5 receipt on the 91-dimensional space sqrt(K2)_5 / K2_5 |
| k[y]/K2 is Cohen-Macaulay for E8-bar -> VB, Iso and W8 -> N- | survives (generic linear section length 7, 23, 50 equal to the degree at 32009 and at 32029; `k2_cm.py`) | none at either prime |
| For E8-bar -> VB, Iso and W8, F(I) = k[y]/K2 in all degrees iff the analytic spread and multiplicity of F(I) are (4, 7), (5, 23), (6, 50) | survives (argument: the quadric ring is Cohen-Macaulay, so L/K2 is zero or of full dimension) | none; an argument |
| For W8 -> N-, F(I) = k[y]/K2 iff Proj F(I) contains V(P) and every component of V(K2 : P) | survives (argument: K2 radical and Cohen-Macaulay, components of degree 20 and 30; a proper subfiber has multiplicity below 50) | none; an argument. Deciding it needs the decomposition of K2 : P and arcs to each component |
| Sign-paired fibers share every certified degree (W8 -> N+, X+ at 32009, E8-bar -> N+ degrees 2 and 3 at 32009) | survives (generator-wise sign isomorphisms induce F(I+) ≅ F(I-); `witnesses.jsonl`, hash-bound) | a sign witness whose relation files no longer match their recorded sha256 |
| F(I) is Cohen-Macaulay for X+- and E8-bar -> N+- | refuted if the analytic spread is 4 and 5 (negative D'Cruz-Raghavan-Verma numerators in certified degrees) | the analytic spread |
| The E8-bar -> VB fiber contains the degree-4 component | survives (certified over F_32009) | second-prime arc replay |
| The E8-bar -> VB fiber contains the degree-3 component | open, favored by the Hilbert data | arcs in the remaining charts; a relation of degree 5 or more vanishing on the degree-4 component |
| The E8-bar -> VB fiber is reduced | survives at the quadric level | an embedded or nilpotent relation in a later degree |
| Every fiber has dimension at most 3 | refuted: W8 -> VB has all of P^4 (`evidence/a5-kernel-attachments/README.md`), and for E8-bar -> N+- at 32009 and 32029 the reduced exceptional fiber over the base point is Proj(k[y]/sqrt(K2)), the union of a fourfold of degree 11 and the rational normal scroll S(1,1,2), and an arc family with Jacobian rank 5 reaches the fourfold (`evidence/a5-exceptional-fibers/arcs/`) | none at these primes; a characteristic-zero statement needs task 42 |
| k[y]/K2 is Cohen-Macaulay for X- and E8-bar -> N- | refuted at 32009 | X- depth 1 (projective dimension 14 of 15); E8-bar -> N- linear-section length 20 against degree 11, which no Cohen-Macaulay ring allows |
| V(K2) of E8-bar -> VB is a linearly joined union of two minimal-degree threefolds | survives (computed: spans P^5 and P^6 meeting in a P^2, components meeting there; 2-regular by the linear resolution) | none: same at 32009 and 32029 (`k2_cm.py`) |
| F(I) of E8-bar -> VB is Cohen-Macaulay iff F(I) = k[y]/K2 | survives (argument: analytic spread 4 from the certified component, multiplicity bound 7 both ways) | none; an argument |
| The X- fiber support is one irreducible three-fold of degree 12 in a P^11 | survives for V(K2) only: F(I) is a quotient of k[y]/K2, so the fiber support may be a proper closed subset | arc certificate inside the P^11 |
| X+ and X- fibers correspond under t9 -> -t9 | survives (exact coefficient check) | none; proven for the inputs |
| E8-bar -> N+ and N- fibers correspond under t8 -> -t8, t9 -> -t9 | survives (generator-by-generator sign identity at the three producer specializations (p, i) = (32009, 10754), (32009, 21255) and (32029, 9115); the moved N- quadrics span the N+ quadrics at 32009 and 32029) | the producer's Q(i) generators compared directly |
| W8 -> N+ and W8 -> N- fibers correspond under t9 -> -t9 | survives (exact coefficient check) | none; proven for the inputs |
| Results at 32009 hold at a second prime | survives: at p = 32029, E8-bar -> VB 34, 80; X- and X+ 51, 122 with 69 quadrics; Iso 85, 265, 640 with 68 quadrics, all equal to 32009; at 32029 also W8 -> N- 156 and E8-bar -> N+- 83 with 148 quadrics each, and E8-bar -> N+- 225 in degree 3 | a third prime, and any higher degree at 32029 |
| J is radical and prime through the origin | survives on all five pairs checked | none; checked |
| The pivot is a nonzerodivisor modulo J | survives on every pivot used | none; checked |
| Kernel-plane limits along the arcs have generic nullity 8 | open | the limit computation |
| Arcs on the normalization certify every reduced component | survives on E8-bar -> VB's degree-4 component | a component no normalized arc reaches |
| The jet-truncated rank reaches h_d at practical N | survives on Iso degree 4 (r_13 = 640, the K2 count) | W8 degree 3 at N = 10 to 14 against 600 (degree-3 driver at 32029); positive control: Iso degree 3 climbs r_9 = 216, r_10 = r_11 = 265 to the known h_3 (independent review), so a ladder that misses a known value at large N exposes a defect |
| Every pair carries a diagonal Klein four-group of sign symmetries and no larger termwise diagonal group | survives (exhaustive search over all sign vectors at 32009; Smith invariants 1, ..., 1, 2, 2 at all 27 headers of the three specializations) | an input regeneration that breaks span invariance |

### Refuted, rejected or superseded

| Hypothesis | Status | Evidence |
|---|---|---|
| The fiber cone F(I) is reduced, for X- and E8-bar -> N+- | refuted | 3 and 5 nilpotent linear forms (radical h_1 = 12 vs 15, 16 vs 21); reducedness of Proj F(I) is open |
| V(K2) of E8-bar -> VB is irreducible (a 2 x 7 scroll) | refuted | two minimal primes, degrees 3 and 4 |
| V(K2) of E8-bar -> N+- is equidimensional | refuted | primes of projective dimension 4 and 3 |
| One limiting kernel per boundary point (path independence) | refuted for the nullity-8 record's instances | path-dependent limits there; each of the five fibers needs its own arc certificate |
| One-point transport of the fiber by H-transitivity | rejected | the split boost has no kernel lift |
| The regularity of k[y]/K2 bounds the missing relations | rejected | a new relation of F(I) can appear in any degree |
| Pivot saturation completes the full fiber on this hardware | refuted | six stalls after the pivot, up to 12 h and 72 GB |
| Pivot saturation is the only completion route | superseded | certified candidate ideal, dense arc family, bounded Hilbert function, unmixed candidate |
| A certified candidate ideal L verifies cheaply | refuted for one presentation on E8-bar -> VB | std(L) in 18 variables past 3 GB in 14 minutes; a reduced presentation, bounded membership or saturation witnesses stay untested |
| Full Rees-graph elimination by msolve fits a session | refuted for the full graph | degree-7 F4 step on E8-bar -> N+; 209 GB and degree 16 of at least 19 on E8-bar -> VB; a fixed-degree homogenized or Macaulay slice after symmetry and presolve stays untested |
| `minAssGTZ` decomposes the quadric scheme directly | refuted | Iso 40,000 s without result; radical first plus `minAssChar` takes 1 s on X- |
| The local `ds` syzygy is required for h_d | superseded | global membership in J + m P_d, 17 s against 25,459 s |
| Order-1 Hensel arcs certify E8-bar -> VB | refuted | det M = 0 over the non-reduced tangent cone |
| Torus multigrading forces toric components | rejected | a grading splits blocks without forcing toric components; not tested |
| The naive leading-form test (lowest m-adic forms of the products independent modulo the tangent cone of J) certifies a degree | fails to certify on the instances run | ranks 137 of 265 (Iso degree 3) and 53 of 240 (X- degree 4) from mixed m-adic orders 2 and 3; weighted initial-ideal routes stay open |
| An untruncated std(J + m P_3) for W8 fits a 78 GB scope on an 84 GB VM | refuted | cgroup OOM at the 78 GiB limit (77.8 GiB resident) after 61,304 s |
| E8-bar -> N- needs computations of its own because no diagonal sign change carries N+ onto it | refuted | only t9 -> -t9 was tried (combined G rank 41 of 42); the full 2^9 sign search finds the pair flip t8 -> -t8, t9 -> -t9, which maps every generator to plus or minus its partner. The degree-2 run on N- (13,827 s on Kaggle), its quadric decomposition, the stopped N- Rees saturation and the 36 h N- cloud run duplicated N+ work |
| The W8 degree-3 jet std at N = 10 fits a 24 GB scope | refuted | kernel OOM kill at the 24 GB limit after 5,449 s, inside std of J + m P_3 + m^10 |
| A truncated rank plateau below the K2 count refutes convergence | rejected | Krull intersection gives eventual convergence with no N computed in advance; only equality with the K2 count certifies |
| GPU or TPU rank computation is the bottleneck | superseded by the stage times | standard-basis routes had no matrix stage; the linear-algebra truncated rank spends 60 to 97 percent of its raw-mode time in closure (E8-bar -> N+- degree 3 at N = 11: 4,397 of 4,526 s) and 99 percent of its quotient-mode time in the Singular product export, which a GPU does not shorten |
| A 4 GiB per-call cap caused the producer's "no more memory" exits | refuted | the cause is `RLIMIT_AS` inherited from a Python helper |
| Raising the per-call cap to 16 GiB fixed those exits | refuted | the cap never governed while `RLIMIT_AS` was set |
| The cancelled msolve TPU kernel held the account's TPU slot | refuted | the web UI showed it ended; deleting the queued smoke kernel freed the slot |
| The value 155 is a product 54 x 12 of earlier counts | refuted | 155 is h_4 of k[y]/K2 for E8-bar -> VB |
| Iso and W8 quadric schemes decompose chart by chart within 45 minutes per chart | refuted | 40 of 41 charts stopped at the 45-minute cap, 18 inside `radical` and 22 inside `minAssChar` (called on the original ideal rather than on its radical); the charts give affine dimension 5 (Iso) and 6 (W8) with radical certificates on 9 and 14 charts; W8 chart 10 finished with one prime of affine dimension 6 and 37 linear generators |

## Work in progress

- **Truncated-rank ladders against the K2 counts**: E8-bar -> N- degree 4 against 495 on engine v7 (r_12 = 357,
  r_13 = 440 on the workstation; N = 14, 15, 16 on Kaggle CPU sessions); E8-bar -> N+ degree 3 at 32009 in raw mode,
  which checks engine and header consistency at the specialization the N- certificate already covers. Engine v8
  computes each variable's multiplication table with one ideal-wide normal form instead of one per standard monomial;
  at E8-bar -> N- N = 12 the exports are byte-identical and the tables take 52 s instead of about 3,115 s.
- **A fresh degree-2 replay for Iso and E8-bar**, so the upper bound K2 contained in L rests on a replay rather than
  on retained receipts alone; the W8 -> N- receipt at 32009 now exists and certifies degrees 1 to 4 there.
- **Iso and W8 -> N- support decomposition**: radical then `minAssChar` on the radical, chart by chart, with caps
  above 8,000 s on Iso charts 6, 9, 10, 14, 16 and on W8 piece 2.
- **Remaining arc charts on E8-bar -> VB** (t5 = 1, t7 = 1, the locus k^2 + 3 = 0 and the singular points of the
  normalization): the search for a dominant (generic rank 3) arc family into the degree-3 component, isolated arcs
  showing only single points. Chart 5 (t5 = 1): `normal()` returns in 359 s with one ring of 21 variables and 382
  relations, and its 14 arcs with finite lead all land in the degree-4 component, none in the degree-3 component; the
  earlier 10 h runs spent their time in a diagnostic std of the normalization ideal that ran before the outputs were
  written. Because K2 is globally radical, containment of the generic point of
  every component of V(K2) in the fiber gives F(I) = k[y]/K2 in every degree: the kernel L lies in every minimal prime
  of K2 and so in K2. Chart-wise radicality certifies only the saturation of K2, so the argument needs a global
  radical test (done for E8-bar -> VB and W8, not for Iso), and it holds prime by prime.
- **Kernel-plane limits along the formal arcs**: the limiting 8-planes of ker L_y from `cd_core` along each arc,
  normalized by valuation; the attaching datum along reduced directions. Arcs over a field cannot see nilpotent
  directions (X-, E8-bar -> N+-), which need the scheme-theoretic Rees or Grassmannian construction.
- **Arc certificate for X- inside its P^11**, then for the remaining pairs once their primes exist.
