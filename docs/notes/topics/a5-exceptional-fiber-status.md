# A_5 exceptional fibers: goal, status by layer and open theorems

This page states what the A_5 fiber program is for, where each layer stands on 2026-11-22 by the claim ledger
([`ledger.tsv`](../../evidence/a5-exceptional-fibers/ledger.tsv), 575 rows), which theorems remain between the
record and the registry claim, and what the next computations and formal proofs are. The measurements and methods
live in [a5-exceptional-fiber-findings.md](a5-exceptional-fiber-findings.md) and in the evidence directories; this
page counts and orders them. It replaces the status of 2026-11-11 (313 rows), whose open items the rows named below
have since decided.

## The goal

A_5 here is the 32-dimensional Cayley-Dickson algebra (the pathions), not the alternating group. Its zero divisors
form strata by nullity, the dimension of the kernel of left multiplication. The open registry claim
`dimension32-global-topology` asks how those strata are glued: as a point of an orbit closure Y approaches a smaller
orbit Z, which kernels arise as limits. There are 33 incidences Y -> Z between the orbits: 14 from nullity 8 to
nullity 12 plus E8-bar -> VB, 8 from nullity 12 to nullity 16, and 10 from nullity 8 to nullity 16 (the fiber track:
X+, X-, Iso, W8 and E8-bar into N+ and N-). The program answers in four layers:

1. **Directions of approach, degree by degree.** The exceptional fiber of the blowup of Y along the
   kernel-coordinate ideal I at a point of Z has coordinate ring F(I), the fiber cone, with Hilbert function
   h_d = dim_k(I^d / m I^d).
2. **Directions of approach, all degrees at once.** F(I) = k[y] / K2 says the quadric relations K2 generate the
   whole relation ideal L.
3. **Characteristic 0.** The same statements over Q(i), not only over F_32009 and F_32029.
4. **The attaching datum.** The limiting kernel planes as a set of real points: every limit realized by a real arc
   and every other plane excluded, at every point of each boundary orbit, and compatibly along chains Y -> Z -> Z'.

## Status by layer (2026-11-22)

Ledger totals: 216 proved, 114 certified, 113 survives, 62 refuted, 37 superseded, 13 open, 9 stalled, 7 rejected, 4 boundary.
Reproduce with `"$PYTHON" docs/evidence/a5-exceptional-fibers/ledger.py --summary`.

| Layer | State | Deciding rows | Open |
|---|---|---|---|
| 1, per-degree h_d | complete at both primes for the six fiber classes | A5-001, A5-005 to A5-009, A5-335 (E8-bar degree 6, the last cell of the earlier count) | none |
| 2, F(I) = k[y] / K2 in every degree | complete at both primes: VB (A5-005, A5-015, A5-016), same-sign X (A5-304), Iso (A5-067), W8 (A5-066), E8-bar -> N+- on the header slices (A5-559) and by direct Rees saturation on the weight slice at all eight sign, prime and root cells (A5-572, A5-573, A5-587) | as listed | receipts only: X+ -> N+ at 32009 has no retained K2 file (A5-304); the degree-2 receipt of E8-bar -> N+ at the root 21255 of 32009 is open (A5-571) |
| 3, characteristic 0 | all 33 incidences have a fiber cone over Q(i) on a retained slice: the 22 incidences of nullity 8 to 12 and 12 to 16 (A5-402, A5-405, A5-408), opposite-sign X (A5-270), same-sign X (A5-305), Iso, W8 and E8-bar into N+- on the weight slice (A5-446, A5-448, A5-457 with A5-474 and A5-475), and E8-bar -> VB (A5-597, this change) | as listed | the map between the header slice and the weight slice of E8-bar over Q(i) (it exists modulo 32009, A5-583); the boost direction of the V and VB orbits |
| 4, real limit sets | proved on the retained slice germ at 26 of 33 incidences: 14 of nullity 8 to 12 (A5-411), 8 of nullity 12 to 16 (A5-412), the four X incidences into N+- (A5-417); G_2(C) x C^* equivariance moves the basepoint on B9, V^a+-, N+ and N- (A5-415) | as listed | E8-bar -> VB; Iso, W8 and E8-bar into N+- (A5-418, survives); the boost direction on V and VB (A5-419, survives); A5-250 stays open for these |
| Kernel bundles and gluing | nullity-8 ordinary classes computed (A5-396, survives); composed limits lie in linear sections (A5-420) | as listed | nullity-4 classification (A5-389, open); the flat-family clause of A5-420; the global attaching maps |
| Machine-checked | the algebra (signs, nullity doubling, two-term nullity, the G_2 derivation span) and the eight W8 arc-matrix ranks (gororoba-math `rocq/quantum/A5W8ArcMatrixRanks.v`) | A5-453, A5-500 | no fiber-cone, Rees or Hilbert-function statement is formalized |

## Completion by incidence

D done, P partial, O open; the cell names the deciding row. Sign-conjugate incidences share a row.

| Incidence | Layers 1 and 2 | Layer 3 | Layer 4 |
|---|---|---|---|
| E8-bar, Iso, W8, X+- -> B9; X+ -> V^a+, X- -> V^a- (7) | D A5-402 | D A5-402 | D A5-411, A5-415 |
| E8-bar -> V (1) | D A5-402 | D A5-402 | P A5-411; boost open (A5-414) |
| X+-, Iso, W8 -> VB (4) | D A5-405 | D A5-405 | P A5-411; boost sampled (A5-419) |
| E8-bar -> V^a+- (2) | D A5-405 | D A5-405, A5-413 | D A5-411, A5-415 |
| E8-bar -> VB (1) | D A5-005 | D A5-597 at the retained basepoint; boost sampled modulo 32029 (A5-428) | O A5-250 |
| B9, V, VB, V^a+- -> N+- (8) | D A5-408 | D A5-408 | D A5-412, A5-415 |
| X opposite sign -> N+- (2) | D A5-001 | D A5-270 | D A5-417 |
| X same sign -> N+- (2) | D A5-304 | D A5-305 | D A5-417 |
| Iso -> N+- (2) | D A5-067 | D on the weight slice, A5-446, A5-475 | P A5-418 |
| W8 -> N+- (2) | D A5-066 | D on the weight slice, A5-448, A5-475 | P A5-418 |
| E8-bar -> N+- (2) | D A5-559, A5-587 | D on the weight slice, A5-457; slice map modulo 32009, A5-583 | P A5-418 |
| Nullity-4 kernel bundles | not a fiber-cone question | | O A5-389 |

## What separates the record from the registry claim

| Theorem | Content | Missing |
|---|---|---|
| T1 | characteristic-0 fiber cones for all 33 incidences, independent of the transverse slice | the E8-bar slice map over Q(i) (A5-583 gives it modulo 32009; the header-slice quadrics are retained modulo p only), and a statement that the map found is the one the slice isomorphism induces |
| T2 | the fibers along each whole boundary orbit | a family over the boost parameter for the six incidences into V and VB (A5-414, A5-419, A5-428 sample it) |
| T3 | the two-sided real limit theorem at all 33 incidences (A5-250) | E8-bar -> VB; A5-418 for Iso, W8 and E8-bar into N+-; the boost direction |
| T4 | compatibility of composed limits 8 -> 12 -> 16 | the flat-family clause of A5-420 |
| T5 | classification of the kernel bundles | nullity 4 (A5-389); the ordinary class in nullity 8 (A5-396) |
| T6 | the global attaching maps | not started; consumes T1 to T5 |
| T7 | formal certificates in gororoba-math | every fiber-cone statement |

Order: T1 feeds T2 and T3; T5 runs beside them; T1, T3 and T5 feed T4, then T6. T7 can certify each node when it
closes and removes the dependence on one computer-algebra system.

## Results of 2026-11-22

| Result | Row | Evidence |
|---|---|---|
| The eight E8-bar weight-slice cells by direct Rees saturation, the modulo colon, the conjugation map Phi and the closed forms of det B and the unit polynomials | A5-587 to A5-592 | [e8-rees-fibers-v3-open-cells](../../evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v3-open-cells/README.md) |
| An invertible 21 x 21 map carries the weight-slice quadric ideal of E8-bar onto the header-slice ideal, at N- and N+ modulo 32009; found through the maximal tori of the two symmetry algebras, verified by mutual reduction with two controls | A5-583, certified | [e8-slice-equivalence-p32009](../../evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009/README.md) |
| Each of the 126 Pfaffian generators equals Pf(B)^3 times a 10-Pfaffian of T over Q(i), which derives the unit polynomials of A5-592; the fourth factor of generators 10 and 16 comes from the 10-Pfaffian | A5-593, A5-594 | [e8-pfaffian-schur-identity](../../evidence/a5-exceptional-fibers/working/runs/e8-pfaffian-schur-identity/README.md) |
| E8-bar -> VB over Q(i): the 21 quadrics, K2 = P1 n P2, both arc families with rank 4, so L = K2 in characteristic 0 | A5-597 | [a5-char0-transfer](../../evidence/a5-char0-transfer/README.md) |
| The modular weight-slice cells of E8-bar -> N+ and Iso -> N- regenerate with the digests of the runs | A5-577, certified | [a5-kernel-attachments](../../evidence/a5-kernel-attachments/README.md) |
| Reduced Hilbert numerators (1, 12, 10), (1, 18, 27, 4) and (1, 16, -12, 10, -5, 1); the E8-bar numerator as the sum of its two primes, their intersection and the nilradical module | A5-595 | [coefficient-structure](../../evidence/a5-exceptional-fibers/coefficient-structure/README.md) |
| The block splits of the last jump are the characters of a nodal conic and of the Segre product of two nodal conics, with no twist; a hypothesis for the final layer | A5-596, survives | the same |
The reviews that selected these computations, with each finding checked against the ledger, are in
[a5-fiber-status](../../archive/reviews/a5-fiber-status/reconciliation.md).

## Next computations

| Layer | Computation | Decides | Estimate from retained timings |
|---|---|---|---|
| T1 | the header-slice quadrics of E8-bar over Q(i), then `slice_bridge.py` over Q(i) or at a second prime with rational reconstruction | the slice map in characteristic 0 | the Q(i) quadric stage of a 21-generator header is the long step (the 15-generator header of X- -> N- took 30,481 s, A5-248) |
| T2 | one-parameter boost family over Q(i)(t) for the V and VB incidences | fibers along the whole orbit | `boost_e8_vb_quadrics.py` took 20 min for four points |
| T3 | the reduced-support argument of A5-418 with the retained map of A5-583, then the product theorem for the boost direction | A5-418, A5-250 | symbolic, minutes to hours |
| T5 | one stratum, one Pfaffian chart, one prime of the nullity-4 Gauss image, as a cost probe | A5-389 | unmeasured; a 1 h probe first |
| A5-596 | retain the final-layer quotient of an existing degree (an engine change) and test the multiplication of the nodal-conic model | A5-278, A5-596 | minutes at d = 2, 3 once the engine writes the quotient |
| Independence | the invariants behind A5-457, A5-474 and A5-475 in a second system | single-engine risk | not run: Macaulay2 is not installed on the compute hosts (package `macaulay2`) |

## Formal proof targets (gororoba-math)

Build order, smallest trusted base first. Each lands as a statement, a proof and a comparator configuration under
`lean/Challenge/` or as a source under `rocq/quantum/`, with the computer-algebra system reduced to a producer of
certificates that the kernel checks.

| Order | Target | System | Certifies |
|---|---|---|---|
| 1 | the conjugation map Phi as a ring automorphism of Z[i][s1..s9] with its three matrix identities, and det B in closed form | Rocq | A5-591, A5-592 |
| 2 | the Pfaffian identity Pf_4(det(B) D + X^T adj(B) X) = Pf(B)^3 Pf_10(T) for a skew matrix with a 6 x 6 block B, over a commutative ring | Lean | A5-593 in general |
| 3 | the left-inverse rank certificate extended from Z[i] to its fraction field, then arc-rank files for E8-bar and Iso | Rocq | the prose step of `A5W8ArcMatrixRanks.v`; A5-457, A5-475 |
| 4 | a checker of sparse polynomial cofactor identities q(G) = sum a_k J_k + sum b_ij s_i P_j | Rocq | K inside L (A5-474) from exported cofactors |
| 5 | a checker that a linear substitution carries one finite set of quadrics into the span of another, with the inverse | Rocq | A5-583 from `bridge-CELL.json` |
| 6 | the splitting ker C_z = C z + ker A(z, conj z) | Lean | the mechanism of A5-411 and A5-412 |
| 7 | the lemma that K inside L inside rad K, a rank-one torsion-free nilradical module and a separating order function give L = K | Lean | A5-457 without a primary decomposition by machine |
| 8 | fiber cone, Rees special fiber, Hilbert series and multiplicity | Lean | the statement layer of every row above |

## Weakest links

- **One computer-algebra system.** Ideal, radical, saturation and primary-decomposition claims rest on Singular
  4.4.1. Replays on a second host test determinism, not the algorithm. The symmetry-algebra numbers 34 and 6 of
  A5-583 are computed in python-flint and agree with the Singular-based rows A5-347 and A5-424; the L = K argument
  of A5-457 depends on `primdecGTZ` returning every associated prime.
- **Slice dependence.** A row marked characteristic 0 for Iso, W8 or E8-bar into N+- is a statement on the weight
  slice. A5-583 joins the two E8-bar presentations at one prime; nothing joins them over Q(i).
- **Basepoint dependence.** On V and VB the group G_2(C) x C^* misses the boost direction, so a result at the
  retained basepoint is a result at that point of the orbit.
- **Ledger wording.** A5-005 to A5-009 read proved with primes `both`: they are modular statements, and the
  characteristic-0 forms are the rows of the table above.
