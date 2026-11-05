# Structure of the kernel-map base loci, the sign symmetry, and the same-sign / opposite-sign difference

Three exact checks explain the fibers recorded in [arcs-x/](../arcs-x/README.md), the
[kernel-attachments record](../../a5-kernel-attachments/README.md) and the
[findings note](../../../notes/topics/a5-exceptional-fiber-findings.md). Each script runs from the repository root
with `"$PYTHON"`, uses Singular in global orderings, and writes its scripts and logs beside itself.

## The doubling automorphism carries every Y -> N+ fiber onto a Y' -> N- fiber

`doubling_automorphism.py` checks with `cd_core.cd_multiply_exact` that phi(a, b) = (a, -b) is an algebra
automorphism of A_3, A_4 and A_5 on every basis pair (0 failures of 64, 256 and 1024; `logs/doubling_automorphism.txt`).
On a doubly pure y it conjugates the original coordinates z_k = y_k + i y_(16+k), so in split coordinates it negates
the slots of odd popcount, z'_1, z'_2, z'_4, z'_7, z'_8, z'_11, z'_13, z'_14. `doubling_split_action.py` applies it to
every orbit representative of the [regularity record](../../a5-strata-regularity/README.md): it exchanges X+ and X-,
V^a_+ and V^a_-, N+ and N-, maps W8, E8-bar, Iso, B9, V and VB into themselves, and preserves every nullity
(`logs/doubling_split_action.txt`).

Since L_phi(y) = phi L_y phi^-1, the kernel map commutes with phi, so phi carries the closed Gauss graph of Y and its
fiber over p onto those of phi(Y) over phi(p). G_2 x C^* acts by automorphisms and scalings and is transitive on the
6-dimensional null cone N+- minus 0, so the fiber does not depend on the base point within the orbit. Consequence, in
every characteristic: X+ -> N+ and X- -> N-, X+ -> N- and X- -> N+, and Y -> N+ and Y -> N- for Y in {W8, E8-bar,
Iso, B9, V, VB} have isomorphic fibers. The sign witnesses of [witnesses.jsonl](../witnesses.jsonl) are instances.

## Same-sign versus opposite-sign: which sheet of E8-bar is smooth

`asymmetry.py` (`logs/asymmetry.txt`, `logs/asymmetry.json`, over Q, the regularity record's `germ_job`):

| Ideal | at N- | at N+ |
|---|---|---|
| E8-bar and mu' = 0 | germ (4, 3, 7), sheets (4, 2, 7) and (4, 1, 4), meeting in dimension 3 | same |
| mu' = 0, eta(d) = 0 (the X+ conditions) | smooth (7, 1, 7) | quadric cone of rank 7, (7, 2, 8) |
| mu' = 0, eta(s) = 0 (the X- conditions) | quadric cone of rank 7 | smooth |

On N- the vector d = u' - v' = 2u' is nonzero, so eta(d) has nonzero differential and X+ is the smooth sheet of
E8-bar cut by mu' = 0; on N+ d vanishes and eta(d) lies in the square of the ideal, so X+ is the multiplicity-2 sheet.
The multiplicities add up, 1 + 2 = 3 = mult(E8-bar) along N+- (germ (5, 3, 8)), and the two sheets meet in the
3-dimensional B9 slice. The opposite-sign fibers (P^2) come from the smooth sheet and the same-sign fibers (proper
subvarieties of P^14) from the singular one. The vanishing of eta on the targets does not distinguish them, since
eta(s) = eta(d) = 0 on both N+ and N-.

## The base locus is the B9 slice; the residual is the VB curve or the origin

`base_locus.py FIELD INCIDENCE...` builds the producer's coordinate slice (nine variables, no elimination), the
Schur-coordinate ideal F (whose zero set is the nullity >= 12 locus of the source germ), and the pullbacks of the B9 and
VB closure equations. FIELD p32009 and p32029 use the split primes and roots of -1 of the fiber inputs, and q uses
Q(i). Summaries are in `logs/summary_p32009.txt`, `logs/summary_p32029.txt` and `logs/summary_q.txt`, with one
script and log per row in `sing/` and `logs/`. The three fields agree on every row:

| Incidence | germ dim | base locus V(J + F) near 0 | residual (J + F) : P_B9 |
|---|---|---|---|
| X+ -> N-, X- -> N+ | 4 | one prime, dimension 3, equal to the B9 slice | one prime, dimension 1, equal to the VB slice |
| X+ -> VB, X- -> VB | 3 | one prime, dimension 2, equal to the B9 slice | the origin (m-primary) |
| W8 -> VB | 5 | one prime, dimension 2, equal to the B9 slice | the origin |
| Iso -> VB | 4 | one prime, dimension 2, equal to the B9 slice | the origin |
| B9 -> N-, B9 -> N+ | 3 | the origin (F is m-primary) | not applicable |

Reading: on X+ -> N- the ideal is I = t2 * I' with V(t2) the B9 slice and V(I') the VB curve, so F(I) = F(I') and the
fiber is the exceptional P^2 of the blow-up along a smooth curve germ of codimension 3. On X -> VB the B9 slice is
again a divisor and the residual is m-primary with s = 3 = germ dimension, which forces the full P^2. On B9 -> N+- the
ideal is m-primary with s = 3 = germ dimension, which forces P^2. On W8 -> VB and Iso -> VB the B9 slice has
codimension 3 and 2, the colon is not a factorization, and the full P^4 and P^3 rest on the recorded certificates.

The general criterion is analytic spread (Northcott and Rees 1954, doi 10.1017/s0305004100029194): F(I) is a quotient
of k[y_1..y_s], its Krull dimension l(I) is at most the germ dimension, and F(I) = k[y] exactly when l(I) = s. Every
incidence with s above the germ dimension (V -> N+-, E8-bar -> Va+-, same-sign X, E8-bar -> N+-, E8-bar -> VB,
Iso -> N+-, W8 -> N+-) therefore has a proper fiber, as recorded; smoothness of the source germ is neither needed nor
sufficient.

## Falsifiers

A basis pair failing the automorphism identity, an orbit representative whose phi-image leaves the predicted closure, a
germ tuple different from the table, a base locus with a second prime through 0 or a prime different from the B9
pullback, a residual of a different dimension, or any disagreement between the three fields.
