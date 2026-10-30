# A_5 exceptional fibers: measured results, tested hypotheses and what survives

The open claim `dimension32-global-topology` needs the attaching data of the A_5 zero-divisor strata: how the
kernel fibers on a nullity-8 orbit closure Y specialize as a point of Y approaches a smaller orbit Z in its closure
([kernel-bundles program](../../design/a5-kernel-bundles-nullity8-program.md)). The algebraic object is the
exceptional fiber of the blow-up of Y along the kernel-coordinate ideal I = (G) at a point of Z, with coordinate ring
the fiber cone F(I) = sum_d I^d / m I^d. Its Hilbert function h_d, dimension, degree and components describe the set
of limiting directions; the limiting kernel 8-planes along those directions are the attaching datum itself.

Every computation below runs over F_32009 with i = 10754 (a split prime, so the Q(i) inputs specialize without an
extension field), in global monomial orderings, each Singular job in a cgroup scope with `MemoryMax` and
`MemorySwapMax=0`. Results over F_p certify that reduction only; a characteristic-zero statement needs a second prime
and a specialization argument. The run directories, logs and normal-form files are unretained working data in the
git-ignored `docs/local/a5-failed-runs/`; a result enters the tracked record through the
[kernel-attachments evidence](../../evidence/a5-kernel-attachments/README.md) and its ledger.

## Pairs

| Pair (Y -> Z) | Ambient generators of G | Germ dimension bound on the fiber |
|---|---|---|
| X+ -> N+, X- -> N- | 15 | 3 |
| Iso | 17 | 4 |
| E8-bar -> N+, E8-bar -> N- | 21 | 4 |
| W8 -> N-, W8 -> N+ | 24 | 5 |
| E8-bar -> VB | 10 | not derived |

## Methods and their outcomes

**Degree-by-degree membership rank.** For each degree d, the products of d generators reduced modulo J, then exact
membership in J + m P_d in a global ordering (exact because the quotient is killed by m), Nakayama normal monomials
from the certified relations of degree d-1, and the F_p rank and left kernel with FLINT. It replaces the local `ds`
syzygy computation, which took 25,459 s against 17 s for the same X- degree-2 count. It succeeded on every pair it
ran on and certifies only the degrees it computes.

| Pair | h_1, h_2, h_3 | New relations beyond the quadrics K2 | Cost of the largest degree |
|---|---|---|---|
| X+-, X- | 15, 51, 122 | none in degree 3 | 598 s |
| Iso | 17, 85, 265 | none in degree 3 | 1,054 s |
| E8-bar -> N+ | 21, 83 | (degree 3 stopped) | 6,029 s |
| E8-bar -> N- | 21, 83 | (degree 3 not run) | 7,874 s |
| W8 -> N- | 24, 156 | (degree 3 stopped for host memory at 14 GB) | 5,619 s, 6.7 GB |
| E8-bar -> VB | 10, 34, 80 | none in degree 3 | 406 s |

**Sign symmetry under t9 -> -t9.** J- = eps J+ and G- = delta G+ coefficient by coefficient for X, and likewise for
W8 -> N+ against W8 -> N-, with no failure; those fibers follow by y_j -> +-y_j. For E8-bar the symmetry fails: the
substituted N+ generators and the N- generators span 41 dimensions of 42, and the global ideals differ, so
E8-bar -> N- is computed on its own.

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
| E8-bar -> N+ | no | 16, 69, 195, 440 | two: (4, 11), (3, 4) |
| E8-bar -> VB | yes | 10, 34, 80, 155 | two: (3, 3), (3, 4) |
| Iso, W8 -> N- | not finished in 600 s | | |

The quadric schemes V(K2) have projective dimension 3 and degree 12 (X-), 4 and 11 (E8-bar -> N+), 5 and 50 (W8,
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
equivalent generator presentation. E8-bar -> VB in degree 2 at 32029 gives h_2 = 34 with 21 relations, equal to 32009.

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

## Hypotheses tested against the data

**The fiber cone is generated by its quadric relations, F(I) = k[y]/K2.** Survives through degree 3 on X, Iso and
E8-bar -> VB and through degree 2 elsewhere. Falsifier pending: E8-bar -> VB degree 4 against the quadric value 155.
Under strain from the arcs: if it holds in every degree, the fiber is all of V(K2) and contains the degree-3 component
that no arc has reached.

**The exceptional fiber is reduced.** Falsified for X- and E8-bar -> N+. Their radicals contain 3 and 5 linear forms
outside K2, and since F(I) agrees with k[y]/K2 in degree 1, those forms are nilpotent in F(I). The reduced support lies
in a P^11 (X-) and a P^15 (E8-bar -> N+). Survives for E8-bar -> VB at the level of K2. Untested for Iso and W8.

**The exceptional fiber is irreducible.** Falsified for V(K2) of E8-bar -> VB (degrees 3 and 4) and of E8-bar -> N+
(dimensions 4 and 3, so not even equidimensional), which also refutes the irreducible 2 x 7 scroll proposed for
E8-bar -> VB. Survives for X-. Reopened for the fiber of E8-bar -> VB itself: if the degree-3 component lies outside
the fiber, the fiber is the single degree-4 component.

**The limiting kernel is the same along every path into Z.** Falsified: every hard fiber has projective dimension at
least 3, and the nullity-8 record already found path-dependent boundary limits. The attaching datum is a family.

**Sign-paired orbits have isomorphic fibers.** Survives for X+ with X- and W8 -> N+ with W8 -> N- by an explicit
coordinate symmetry. For E8-bar -> N+ and N- the transport fails but the Hilbert functions agree through degree 2
(21, 83); isomorphism is untested, and a structure computation on the N- quadrics decides it.

**Results at 32009 hold in characteristic zero.** Survives on one degree of one pair. Falsifier: any h_d at 32029
that differs from 32009; a mismatch alone shows instability, and naming the exceptional prime needs a third.

**A completion by Groebner elimination fits this hardware.** Falsified for every formulation tried: pivot
saturation (six stalls, up to 72 GB), candidate-ideal std, full-graph msolve, local orderings and minAss-first.
Raising caps changes the wait, not the algorithm.

**Order-1 arcs suffice to certify each component.** Falsified on E8-bar -> VB by the singular Jacobian over the
non-reduced tangent cone; arcs on the normalization replace them.

## What survives

- E8-bar -> VB: the fiber contains the geometrically irreducible degree-4 three-fold, certified over F_32009 by a
  dominant arc family; whether the degree-3 component belongs to it is open.
- X-: one irreducible reduced support of projective dimension 3 and degree 12 inside a P^11, with 3 nilpotent linear
  directions, so arcs certify only its support and the nilpotent part needs direct kernel limits.
- E8-bar -> N+: non-reduced and not equidimensional at the quadric level.
- Iso, W8, E8-bar -> N-: Hilbert functions through degree 3 or 2; no decomposition yet.
- Exact degree-by-degree rank and arc families with exact containment checks are the working methods; every
  global elimination is retired.

## Ledger of hypotheses

Status vocabulary: *survives* (consistent with every test that ran, with the falsifier named), *open* (no deciding
test yet), *refuted* (a measurement or argument contradicts it), *rejected* (dropped on an argument without a
measurement), *superseded* (replaced by a stronger or cheaper route).

### Standing

| Hypothesis | Status | Deciding evidence or pending falsifier |
|---|---|---|
| F(I) = k[y]/K2 for E8-bar -> VB | survives through degree 3 | degree 4 against 155 |
| F(I) = k[y]/K2 for X+- and Iso | survives through degree 3 | degree 4 not scheduled |
| F(I) = k[y]/K2 for E8-bar -> N+-, W8 | survives through degree 2 | degree 3 |
| The E8-bar -> VB fiber contains the degree-4 component | survives (certified over F_32009) | second-prime arc replay |
| The E8-bar -> VB fiber contains the degree-3 component | open | arcs in the remaining charts; degree-4 Hilbert value |
| The E8-bar -> VB fiber is reduced | survives at the quadric level | an embedded or nilpotent relation in a later degree |
| The X- fiber support is one irreducible three-fold of degree 12 in a P^11 | survives over F_32009 at the quadric level | arc certificate inside the P^11 |
| X+ and X- fibers correspond under t9 -> -t9 | survives (exact coefficient check) | none; proven for the inputs |
| W8 -> N+ and W8 -> N- fibers correspond under t9 -> -t9 | survives (exact coefficient check) | none; proven for the inputs |
| E8-bar -> N+ and E8-bar -> N- fibers are isomorphic | open | quadric structure of N-; Hilbert functions agree through degree 2 |
| Results at 32009 hold at a second prime | survives on E8-bar -> VB degree 2 | the second-prime replay of every pair |
| J is radical and prime through the origin | survives on all five pairs checked | none; checked |
| The pivot is a nonzerodivisor modulo J | survives on every pivot used | none; checked |
| Iso and W8 quadric schemes decompose chart by chart within 45 minutes per chart | open | chart jobs running |
| Kernel-plane limits along the arcs have generic nullity 8 | open | the limit computation |
| Arcs on the normalization certify every reduced component | survives on E8-bar -> VB's degree-4 component | a component no normalized arc reaches |

### Refuted, rejected or superseded

| Hypothesis | Status | Evidence |
|---|---|---|
| The exceptional fiber is reduced, for X- and E8-bar -> N+ | refuted | 3 and 5 nilpotent linear forms (radical h_1 = 12 vs 15, 16 vs 21) |
| V(K2) of E8-bar -> VB is irreducible (a 2 x 7 scroll) | refuted | two minimal primes, degrees 3 and 4 |
| V(K2) of E8-bar -> N+ is equidimensional | refuted | primes of projective dimension 4 and 3 |
| One limiting kernel per boundary point (path independence) | refuted | positive-dimensional fibers; path-dependent limits in the nullity-8 record |
| E8-bar -> N- follows from N+ by a diagonal sign change | refuted | span rank 41 of 42; global ideals differ |
| Every fiber has dimension at most 3 | rejected | germ bounds of 4 (Iso, E8-bar) and 5 (W8); V(K2) reaches 4 and 5 |
| One-point transport of the fiber by H-transitivity | rejected | the split boost has no kernel lift |
| The regularity of k[y]/K2 bounds the missing relations | rejected | a new relation of F(I) can appear in any degree |
| Pivot saturation completes the full fiber on this hardware | refuted | six stalls after the pivot, up to 12 h and 72 GB |
| Pivot saturation is the only completion route | superseded | certified candidate ideal, dense arc family, bounded Hilbert function, unmixed candidate |
| A certified candidate ideal L verifies cheaply | refuted on E8-bar -> VB | std(L) past 3 GB in 14 minutes |
| Full Rees-graph elimination by msolve fits a session | refuted | degree-7 F4 step on E8-bar -> N+; 209 GB and degree 16 of at least 19 on E8-bar -> VB |
| `minAssGTZ` decomposes the quadric scheme directly | refuted | Iso 40,000 s without result; radical first plus `minAssChar` takes 1 s on X- |
| The local `ds` syzygy is required for h_d | superseded | global membership in J + m P_d, 17 s against 25,459 s |
| Order-1 Hensel arcs certify E8-bar -> VB | refuted | det M = 0 over the non-reduced tangent cone |
| Torus multigrading forces toric components | rejected | a grading splits blocks without forcing toric components; not tested |
| GPU or TPU rank computation is the bottleneck | rejected | no measured matrix bottleneck; Singular uses neither |
| A 4 GiB per-call cap caused the producer's "no more memory" exits | refuted | the cause is `RLIMIT_AS` inherited from a Python helper |
| Raising the per-call cap to 16 GiB fixed those exits | refuted | the cap never governed while `RLIMIT_AS` was set |
| The cancelled msolve TPU kernel held the account's TPU slot | refuted | the web UI showed it ended; deleting the queued smoke kernel freed the slot |
| The value 155 is a product 54 x 12 of earlier counts | refuted | 155 is h_4 of k[y]/K2 for E8-bar -> VB |

## Work in progress

- **Degree-4 Hilbert value of E8-bar -> VB against the quadric prediction 155**: decides whether a new relation
  appears, and with it whether the degree-3 component can stay in the fiber.
- **Chart-by-chart radical and minimal primes of the Iso and W8 -> N- quadrics** (each coordinate set to 1 in turn,
  45 minutes per chart): the first structure for those pairs.
- **Second-prime degree-by-degree replay at p = 32029** for E8-bar -> VB, X+-, Iso, W8 -> N- and E8-bar -> N+-.
- **E8-bar -> N- quadric relations at 32009**, the input to its structure computation.
- **Remaining arc charts on E8-bar -> VB** (t5 = 1, t7 = 1, the locus k^2 + 3 = 0 and the singular points of the
  normalization): the search for arcs into the degree-3 component.
- **Kernel-plane limits along the formal arcs**: the limiting 8-planes of ker L_y from `cd_core` along each arc,
  normalized by valuation; the attaching datum, including on nilpotent directions.
- **Arc certificate for X- inside its P^11**, then for the remaining pairs once their primes exist.
