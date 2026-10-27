# Independent verification of the A_5 strata-regularity record

[verify_regularity_independent.py](verify_regularity_independent.py) re-derives the seven statements of
[the record](README.md) from `gororoba_quantum/cd_core.py` alone and writes [verification.json](verification.json). It
imports nothing from `strata_regularity.py`, `rederive_strata_equations.py` or `scripts/a5_zero_divisor_strata.py`:
the sedenion and A_5 sign tables come from `left_mult_matrix_exact` (re-checked against `cd_multiply_exact` on all
1280 basis pairs), and the split table, eta, the cross product, the 14 derivations (nullspace of the derivation
equations of the split octonion table, with the lift D + D re-checked as a derivation of the split sedenions), the
closure polynomials, C_z and L_y are built in the script. No random value enters; every point is listed in the
source. The author's script was read only after every check below had run, to confirm the methods differ.

Verdict: every claim 1-7 and every row of the singular-locus and germ tables is confirmed. Nothing is refuted. One
step is corroborated rather than re-proved: the symbolic drop-locus certificate of computation 5 (orbit dimension
equals dim X on X minus its lower closures), which the verifier replaces by an exhaustive slice search.

The full run took 125 s on 12 workers (Python 3.14.8, python-flint 0.9.0, Singular 4.4.1); the slice search takes
105 s of that.

```sh
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON" -B -W error \
    docs/evidence/a5-strata-regularity/verify_regularity_independent.py \
    --out docs/evidence/a5-strata-regularity/verification.json
```

## Methods that differ from the record's script

| Question | Record's script | Verifier |
| --- | --- | --- |
| Boost symmetry | boost derivation applied to each ideal | one boost element (c, s) = (5/4, 3/4) of infinite order substituted into every ideal, reduced modulo a standard basis |
| G_2 symmetry | equivariance (imported) | the 14 derivations applied to every generator; finite unipotent elements exp(N) of 60 nilpotent derivations spanning g_2 move the points |
| Orbit decomposition | gl_2-reduced slice minors (computation 5) | 16 x 15 tangent ranks at every R_8 point of three slice searches; irreducibility of Iso and X_+- by separate arguments |
| Transverse slice | coordinate directions completing the orbit tangent | Euclidean orthogonal complement of the orbit tangent (Hermitian over Q(i) at x0) |
| Germ invariants | minimal primes through the point in a coordinate slice; tangent cone by deformation to the normal cone (the local standard basis of the draft was replaced after this verification) | minimal primes through the point; tangent cone by deformation to the normal cone, (P(h t) : h^infinity) at h = 0, global ordering only; multiplicity as the degree of that homogeneous ideal; embedding dimension from the Jacobian of the primes |
| Smoothness | germ invariants | exact Jacobian rank of the closure generators at the representative and at a moved point, plus the germ |
| Sing V(G), nullity-4 locus | slice radicals | gradient identity of G in (s, d, mu') over Z and a case analysis, plus global dimension counts |
| Intersections | orbit membership | ideal membership of a power of each target generator in the sum ideal |

## Claim 1: symmetry (confirmed, 1.1 s)

For every closure ideal of the table and for Q and G, Singular reduces to zero: the image under the boost element
(5/4, 3/4), the image under mu' -> -mu', and the 14 derivations applied to every generator. The boosts g with g(X) in
X form a closed subgroup of SO(2, C) that contains an element of infinite order (c + s = 2), so it is all of SO(2, C).
A compact rotation (u', v') -> (v', -u') fails on Q, which shows the reduction detects a non-symmetry. The rank loci
R_4 = V(QG), R_8 = W8 u E8-bar, R_12 = V u B9, R_16 = N_+ u N_- (established records) are unions of these closures, so
H and the reflection preserve every R_k. The nullity of L_y, the orbit dimension and the membership pattern are
unchanged at every representative under a product of three unipotent G_2 elements (verified automorphism of the split
octonion table), the boost, scaling by 2 and a composite G_2-boost-scaling image.

## Claim 2: twelve orbits (confirmed; the drop-locus step corroborated by search)

- *Representatives* (0.9 s). At all twelve points: nullity of the 32 x 32 rational L_y equals the listed nullity and
  equals 28 - 2 rank C_z; the rank of the 16 H-tangent vectors equals the closure dimension; the membership pattern in
  the twelve closures equals the pattern the closure-order table predicts. The twelve patterns are distinct.
- *Closure dimensions* (Singular `dim`): 12, 11, 11, 10, 10, 9, 8, 7, 7, 7, 6, 6, and 14 for V(Q) and V(G).
- *Irreducibility of the new closures.*
  - Iso: a complete intersection of dimension 11 = 15 - 4. The gradients (2 eta u', 0), (0, 2 eta v'),
    (eta v', eta u') of eta(u'), eta(v'), eta(u', v') are independent whenever u' and v' are independent, so the
    singular locus lies in VB (dimension 7, codimension 4). Serre's criterion makes Iso normal, and a normal cone is
    irreducible. `minAssGTZ` also returns one prime of dimension 11.
  - X_+: on X_+, eta(s, d) = eta(d) = 0, Delta vanishes identically and rank [u'; v'; u' x v'] = rank [s; d; s x d].
    Over d = n0 = e'_1 + e'_3 the fiber {s in n0-perp : rank [s; n0; s x n0] <= 2} is a linear 4-space (one prime,
    linear standard basis). G_2 is transitive on nonzero null vectors (fact F3), so X_+ n {d != 0} is the image of
    G_2 x F, irreducible of dimension 6 + 4 = 10. X_+ n {d = 0} = V^a_+, which lies in that closure along the curve
    (e'_1 + eps A, 0, e'_1 - eps A). X_- is the same argument with s and d exchanged. The germs of X_+- along V^a_+-
    (two sheets of dimension 3 = 10 - 7) independently show that no component of dimension 7 passes through V^a_+-.
  - VB, V^a_+-, N_+- and the pieces W8, E8-bar, B9, V are imported (image of C^2 x N, linear, and the established
    records).
- *Search for stray R_8 points* (105 s). Every point with rank C_z <= 10 on the six slices is classified by its
  minimal closure; it passes when its pattern, orbit dimension and nullity equal those of that orbit's
  representative.

  | Search | slice points | R_8 points | orbits reached | misfits |
  | --- | --- | --- | --- | --- |
  | Gaussian box, every parameter in {0, +-1} + i {0, +-1} | 354288 | 22048 | all 12 | 0 |
  | integer box [-3, 3]^5 | 100836 | 7584 | 11 (no W8: eta has no nonzero rational null pair on P2) | 0 |
  | all of F_13^5 on each slice, i = 5 | 2227752 | 119232 | all 12 | 0 |

The search does not replace a proof that the orbit dimension never drops on X minus its lower closures: a drop locus
without small Gaussian or F_13 points would escape it. Given irreducibility and that statement, X minus its lower
closures is one orbit, as Theorem 2 argues. The verifier checked that argument's logic and every input except the
symbolic certificate.

## Claim 3: incidences (confirmed)

The representative of Y lies in X exactly for the pairs of the closure-order table, and in no other closure (pattern
check). Each closure is irreducible with an open orbit of its own dimension, so it is the closure of that orbit.
W8 n E8-bar = B9: the sum ideal of W8 and E8-bar lies in the B9 ideal, and the square of every B9 generator lies in the
sum ideal. A hand proof agrees: on W8 n E8-bar the pair is isotropic, and for an isotropic independent pair x, y with
x x y = a x + b y the identities x x (x x y) = eta(x, y) x - eta(x) y = 0 and y x (x x y) = 0 (verified over
Z[x, y]) give b (x x y) = 0 and a (x x y) = 0, so x x y = 0. W8 n V = VB and V n B9 = VB: each generator of VB lies in
the sum ideal (power 1), and the sum lies in the VB ideal.

## Claim 4: singular loci (confirmed, every row)

Smoothness along an orbit is read off the transverse germ at its representative (75 pairs, 14.8 s). A cone is
singular at 0 unless it is linear, and the sampled points of each closure span a space larger than its dimension,
except V^a_+- (span 7 = dimension).

| Closure | singular orbits found | record | verdict |
| --- | --- | --- | --- |
| N_+, N_-, VB, B9, V(Q) | none (0 only) | {0} | confirmed |
| V^a_+, V^a_- | none, linear | empty | confirmed |
| V | N_+, N_- | N_+ u N_- | confirmed |
| W8 | N_+, N_- | N_+ u N_- | confirmed |
| Iso | VB, N_+, N_- | VB | confirmed |
| X_+ | V^a_+, N_+ (smooth along B9, VB, N_-) | V^a_+ | confirmed |
| X_- | V^a_-, N_- (smooth along B9, VB, N_+) | V^a_- | confirmed |
| E8-bar | V, B9, VB, V^a_+-, N_+- (smooth along X_+-) | R_12 | confirmed |
| V(G) | W8, Iso, B9, VB, V, V^a_+-, N_+- (smooth along E8-bar, X_+-) | W8 u V | confirmed |

For 42 of the 48 smooth pairs the Jacobian of the closure generators has full rank (the codimension) at the
representative and at the moved point. The other six are X_+ along B9, VB, N_- and X_- along B9, VB, N_+, where the
generators reach Jacobian rank 3 or 4 against codimension 5. The generators of X_+- therefore define a nonreduced
scheme there. Smoothness of the reduced variety along those orbits rests on the germ computation alone (one prime
through the point, embedding dimension equal to dimension, tangent-cone degree 1).

## Claim 5: nullity 4 (confirmed)

- Over Z[z'], Q = eta(s, d) - mu'^2 and G = eta(s) eta(d) - 2 mu'^2 eta(s, d) + mu'^4, with G built as Q^2 - 4 Delta.
  The characteristic polynomial of C_z, read from `left_mult_matrix_exact`, equals
  l (l^2 + Q)^3 (l^4 + 2 Q l^2 + G)^2 at four rational points, which ties Q and G to cd_core. The Hessian of Q has
  rank 15, so V(Q) is smooth off 0.
- The gradient of G is dG/ds = 2 eta(eta(d) s - mu'^2 d), dG/dd = 2 eta(eta(s) d - mu'^2 s), dG/dmu' = -4 mu' Q
  (verified over Z). Case analysis on G = 0 with dG = 0: if mu' = 0, then s = 0 or d = 0 gives a rank-1 point with
  Q = 0 (V), and s, d != 0 forces eta(s) = eta(d) = 0 (W8). If mu' != 0, then Q = 0 makes eta(s, d) = mu'^2 != 0, and
  eta(d) s = mu'^2 d makes s, d parallel (V). Conversely dG and G vanish on W8 and V. So Sing V(G) = W8 u V, and Singular
  gives dim V(G, dG) = 12.
- Points of V(Q) n V(G) where dG = lambda dQ: if mu' != 0 then lambda = 0 and s, d are parallel (V). If mu' = 0 and
  s, d are independent, then eta(d) = eta(s) = eta(s, d) = 0 (Iso). If mu' = 0 and s, d are dependent, the point is in V.
  So the dependence locus lies in Iso u V, which is sharper than the record's Iso u E8-bar; Singular gives dimension 11.
  dim V(Q, G) = 13, so V(Q) n V(G) is a complete intersection with singular locus of codimension 2: it is normal,
  irreducible as a connected cone, and smooth off Iso u V, which lies in R_8.

## Claim 6: Whitney stratification (confirmed as an argument, given claims 1, 2 and 5)

Every stratum is smooth, locally closed and H-stable (claim 1 for V(Q), V(G), R_8). The frontier condition holds:
orbit closures are unions of orbits (claims 2 and 3); V(Q) and V(Q) n V(G) are irreducible, so the closures of their
open strata are the whole sets, whose parts in R_8 are H-stable and hence unions of orbits. For Y a single orbit, the
set where condition (b) fails for (X, Y) is H-stable and nowhere dense in Y, so it is empty; the origin is a point
stratum. Pairs inside S_4 lie in the manifolds V(Q) minus 0 and V(G) minus (W8 u V), which contain both strata, so
secant limits lie in the limit tangent planes. The open stratum satisfies (b) trivially. The argument is complete;
the computational inputs are those of claims 1, 2 and 5.

## Claim 7: germ table and the link at x0 (confirmed, every row)

| Closure along orbit | dim | mult | embdim | sheets / quadric rank / meet | verdict |
| --- | --- | --- | --- | --- | --- |
| V along N_+- | 2 | 2 | 3 | 1 sheet, rank 3 | confirmed |
| W8 along N_+- | 6 | 2 | 7 | 1, rank 7 | confirmed |
| Iso along VB | 4 | 2 | 5 | 1, rank 5 | confirmed |
| Iso along N_+- | 5 | 2 | 6 | 1, rank 5 | confirmed |
| E8-bar along V | 3 | 2 | 6 | 2 smooth sheets, meet dim 0 | confirmed |
| E8-bar along V^a_+- | 4 | 2 | 7 | 2 smooth sheets, meet dim 1 | confirmed |
| X_+ along V^a_+, X_- along V^a_- | 3 | 2 | 6 | 2 smooth sheets, meet dim 0 | confirmed |
| E8-bar along B9 | 2 | 2 | 3 | 1 sheet, rank 3 | confirmed |
| E8-bar along VB | 4 | 2 | 7 | 1 | confirmed |
| E8-bar along N_+- | 5 | 3 | 8 | 1 | confirmed |
| X_+ along N_+, X_- along N_- | 4 | 2 | 7 | 1 | confirmed |
| V(G) along W8 | 2 | 2 | 3 | rank 3 | confirmed |
| V(G) along V | 6 | 2 | 7 | rank 7 | confirmed |
| V(G) along V^a_+- | 7 | 2 | 8 | rank 7 | confirmed |
| V(G) along Iso, VB, B9 | 3, 7, 5 | 2 | 4, 8, 6 | rank 2 | confirmed |
| V(G) along N_+- | 8 | 3 | 9 | tangent cone one cubic | confirmed |

The 48 remaining pairs (every closure along its own open orbit and every pair absent from the table) are smooth
germs, which confirms "every other pair is smooth". The record's draft left E8-bar along B9 as "see result.json". The
verifier finds a hypersurface in its 3-dimensional embedding with a tangent-cone quadric of rank 3: an A_1 surface
germ whose link is RP^3 by the Morse lemma.

**x0 = e_1 + e_18.** Split coordinates are u' = e'_2 - i e'_1, mu' = v' = 0. L_y has nullity 12, the orbit dimension is
7 and the pattern is that of VB. In the 8-dimensional Hermitian-orthogonal slice at x0, over Q(i):
- the germ of V is one smooth curve (dimension 1, embedding dimension 1, multiplicity 1);
- the germ of B9 is one smooth surface (2, 2, 1);
- their reduced intersection is the point, and their Zariski tangent spaces meet in 0.

In C^15 the tangent spaces have dimensions 8 (V) and 9 (B9) and meet in 7, the tangent space of VB. The normal link of
R_12 = V u B9 at x0 is therefore S^1 disjoint union S^3, confirmed at x0 itself. The real dimensions 16, 18 and 14
match the record.

## Controls

A compact rotation fails the symmetry reduction on Q, and swapping the expected patterns of V^a_+ and V^a_- makes
classification reject both representatives.
