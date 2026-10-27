# Independent verification of the high-nullity compact-orbit and kernel-representation statements

[verify_kernel_bundles_independent.py](verify_kernel_bundles_independent.py) re-derives five statements of this record
from `gororoba_quantum/cd_core.py` and writes [verification.json](verification.json). It builds the compact g_2 (the
derivations of the `cd_sign(8, ., .)` octonions), its lift to A_5, the phase lift, every stabilizer, every kernel
restriction and every invariant itself. From earlier records it imports only the split-coordinate helpers of
[verify_regularity_independent.py](../a5-strata-regularity/verify_regularity_independent.py) (`nilpotent_derivations`,
`expm_nilpotent`, `act_g2`, `act_boost`, `REPS`, `h_tangent`, `orbit_dim`) and `nullspace`, `y_from_split` of
[rederive_strata_equations.py](../a5-rank-strata-equations/rederive_strata_equations.py). It imports nothing from this
directory, and the record's scripts were read only after every check had run. Arithmetic is exact (Fractions, Gaussian
rationals, python-flint); no random value enters.

Verdict: statements 1 to 4 are confirmed by exact computation. Statement 5 is confirmed as a set of proofs whose
algebraic inputs the script checks; the homotopy steps themselves are written arguments, not machine-checked. Nothing
is refuted. The absolute central weights in statement 2 depend on a lift convention; they agree with the claim under one
uniform change of convention, stated below.

The run takes 8 to 34 s wall time with `GOROROBA_WORKERS=4`, depending on load on the shared host (Python 3.14.8,
python-flint 0.9.0); `--self-test` takes 4 to 16 s.

```sh
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4 "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-bundles/verify_kernel_bundles_independent.py \
    --out docs/evidence/a5-kernel-bundles/verification.json
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4 "$PYTHON" -B -W error \
    docs/evidence/a5-kernel-bundles/verify_kernel_bundles_independent.py --self-test
```

## Setup checks

- Compact g_2: the derivation equations of the `cd_sign(8, ., .)` table have a 14-dimensional solution space of skew
  matrices. Applied to each of the four octonion blocks of A_5, every derivation D satisfies L_(D e_j) = [D, L_j] for
  all 32 basis elements, so D transports ker L_y to ker L_(y + t D y). Every lift commutes with J = L_(e_16).
- Phase: the generator z -> i z has the domain lift Y_Phi (x_0 -> 2 x_16, x_16 -> -2 x_0, zero elsewhere).
  L_(Phi e_j) = Y' L_j - L_j Y_Phi holds for all 30 doubly pure j with one Y'. Y_Phi commutes with J and with every
  derivation lift.
- Lift ambiguity: the pairs (Y, Y') with L_j Y = Y' L_j for every doubly pure j form a sign graph on the 2048 unknowns.
  The script solves it with a signed union-find and gets a 2-dimensional space spanned by (I, I) and (J, -J). Skew lifts
  are therefore unique up to adding a multiple of J. That addition acts on ker L_y as a scalar under J, so it shifts all
  central weights of a fiber by one common amount and leaves every su(2) and su(3) decomposition unchanged.

## Test points

Each representative in `REPS` is moved by five products of non-compact elements. Each product combines unipotent split
G_2(C) elements exp(c N), with c rational or Gaussian rational, and the boosts (5/4, 3/4), (13/12, 5/12) and
(3/4 + i/4, 1/4 + 3i/4); the last one has c^2 - s^2 = 1 and moves lambda off the imaginary axis. Points lying exactly at
rho = 1 are added: u' = 3 e'_1 + 4 e'_2 on V^a_+-, and z = (e_1, i, 0) and z = ((1,1,1,0,0,0,0), 3, 2i (1,1,1,0,0,0,0))
on V. Every point has the expected nullity and complex H-orbit dimension (B9 9, V 8, VB 7, V^a_+- 7, N_+- 6).

The moved points cover several values of each modulus: rho^2 in {4/9, 6561/71824, 1/3481, 4/4489, 64/1261129} on
V^a_+- and V; lambda in {17/15 i, 5/4 i, 16/65 + 63/65 i, 36/325 + 323/325 i} on V; five distinct normalized Gram
matrices on B9 (two with Re G_12 != 0); four distinct rank-one Gram matrices on VB.

## Verdicts

| Statement | Verdict | Evidence (verification.json key) |
| --- | --- | --- |
| 1. N_+-: u(2) stabilizer, ker = 2 V_0 + 3 V_1, 7 -> 3 V_0 + 2 V_1, 14 -> 3 V_0 + 4 V_1 + V_2, reduced K^0(V_2(R^7)) = Z/2 | confirmed | `statement_1` |
| 2. Principal su(2) with 2 V_0 + 2 V_1; su(3) with 3 + conj(3) at rho = 1; B9 u(1) with 3 C_(-1) + 3 C_(-2); VB u(2) with V_(0,-4) + 2 V_(1,-3) + V_(0,-2) = N module minus V_(1,-1) | confirmed (central weights up to the stated convention) | `statement_2` |
| 3. Generic compact-orbit dimensions B9 14, V 12, VB 11, V^a_+- 12, N_+- 11 | confirmed | `statement_3` |
| 4. Completeness of rho, (lambda, rho) and the normalized Gram matrix | confirmed (exact level-set dimensions plus a normal-form argument; finite stabilizer components not checked) | `statement_4`, `orbit_tools` |
| 5. Unit-section homotopy types | confirmed as arguments; inputs machine-checked | `statement_5`, `statement_5_inputs` |

### Statement 1

At ten moved points on N_+ and N_- and at both representatives, the stabilizer of y in g_2 + u(1) has dimension 4. Its
center has dimension 1, and its derived algebra has dimension 3 with a negative definite Killing form, so the
stabilizer is u(2) = su(2) + u(1). The orbit dimension on the unit section is 15 - 4 = 11. The derived algebra lies in
g_2, because the phase is central.

The Killing-form Casimir Omega has the value n (n + 2)/8 on V_n. Its eigenspace dimensions give:

- on ker L_y (real dimension 16, complex 8 under J): V_0 twice and V_1 three times, so 2 V_0 + 3 V_1;
- on R^7 = Im O, through the 7 x 7 derivation matrices: 3 V_0 + 2 V_1;
- on g_2, through ad: 3 V_0 + 4 V_1 + V_2.

The script feeds these measured multiplicities, not literals, into the representation-ring step, restricting
characters with x = V_1 - 2. V_2 = V_1^2 - 1 gives rho_7 - 7 = 2x and
rho_14 - 14 = x^2 + 8x. The identity x^2 = (x^2 + 8x) - 4 (2x) puts x^2 in the ideal. The Smith normal form of the
ideal's generators, truncated at degree 8, has one free summand and the single torsion factor 2. Hence
Z[x]/(2x, x^2 + 8x) = Z + (Z/2) x, and the augmentation ideal is Z/2.

Hodgkin's hypotheses hold. G_2 is compact, connected and simply connected, so pi_1 is torsion-free. The stabilizer
SU(2) is closed and connected, and R(G_2) = Z[rho_7, rho_14] is polynomial. The Koszul complex on the two relations
gives Tor_0 = Z + Z/2. Tor_2 = 0 because Z[x] is a domain and both relations are nonzero (`tor_2_zero`). With E_2
concentrated in Tor degrees 0 and 1, every differential d_r, r >= 2, vanishes, and Tor_1 feeds only K^1. So
K^0 = Tor_0 = Z + Z/2 and reduced K^0(V_2(R^7)) = Z/2. For completeness, Tor_1 = Z, generated by the class of
(-(x + 8), 2); this was derived by hand and is not computed by the script, and the K^0 claim does not use it. As a cross-check,
the Atiyah-Hirzebruch spectral sequence reaches the same groups from H^*(V_2(R^7)) = Z, Z/2, Z in degrees 0, 6, 11:
the unit tangent bundle of S^6 has Euler class chi(S^6) = 2, and no differential connects these degrees.

### Statement 2

- *Principal.* The stabilizer is su(2) (dimension 3, derived, negative definite Killing form). Its action on the kernel
  is 2 V_0 + 2 V_1 at all fifteen moved points of V^a_+, V^a_- and V. The orbit dimension there is 12.
- *Collinear endpoint (rho = 1).* The stabilizer has dimension 8, equals its derived algebra, and has a negative
  definite Killing form; the only compact semisimple Lie algebra of dimension 8 is su(3). The script checks this at the
  three representatives and the four added rho = 1 points; the orbit dimension is 7. The Killing Casimir equals 4/9 on
  the whole 12-dimensional real kernel. Among irreducible su(3) modules only 3 and conj(3) take that value, so the
  complex rank-6 fiber is a 3 + b conj(3) with a + b = 2. The cubic trace tr_R(J rho(X)^3) equals 2 times the sum of
  the cubed weights, which is proportional to a - b. It vanishes for three generic X. The positive control replaces J by
  the non-scalar central element I0 of the commutant, under which the module is 3 + 3 or conj(3) + conj(3). For the same
  X the control trace is nonzero, which proves the cubic invariant of those X is nonzero. Hence a = b = 1.
- *B9.* At six points the stabilizer is u(1) with orbit dimension 14. The primitive generator is scaled so that its
  weights on the doubly pure space are integers with gcd 1; they are 0^8, 1^14, 2^8, and the phase coefficient is
  t = 1. Under the lift Y_Phi, with weight w defined by Z = w J, the kernel weights are 0^3 1^3.
- *VB.* At six points the stabilizer is u(2) with t = 2 and orbit dimension 11. In native normalization the kernel is
  V_(0,0) + 2 V_(1,1) + V_(0,2). At N_+- the same normalization gives V_(0,0) + 2 V_(1,1) + V_(0,2) + V_(1,-1).
- *Convention.* The claimed weights are -(w + t). That formula is the lift Y_Phi + J with the opposite orientation. The
  record's `kernel_symmetry.py` uses the domain lift R_(e_16) for the generator L_(e_16) = -Phi on the base, and the
  script checks R_(e_16) = -(Y_Phi + J) exactly (`algebra` keys `R_e16_equals_-(Y_Phi+J)` and
  `L_e16_on_base_equals_-Phi`), so the claim uses this convention. Applied to every piece at once, it maps B9 to 3 C_(-1) + 3 C_(-2), VB to
  V_(0,-4) + 2 V_(1,-3) + V_(0,-2), and N_+- to that module plus V_(1,-1), exactly as claimed. The content independent
  of any convention:
  - B9 carries two weights that differ by 1, each with multiplicity 3;
  - VB's spin-0 weights differ by 2 and its doublets sit midway;
  - the N_+- module equals the VB module plus one doublet whose central weight lies 2 below the VB doublets.

### Statement 3

The table lists the compact-orbit dimension 15 - dim(stabilizer) at moved points (five per piece) and at the recorded
representatives.

| Piece | Moved points | Representative |
| --- | --- | --- |
| B9 | 14 | 14 |
| V | 12 | 7 |
| VB | 11 | 11 |
| V^a_+- | 12 | 7 |
| N_+- | 11 | 11 |

The representatives of V and V^a_+- lie on the su(3) stratum, as the brief warned. The self-test control
`unmoved_points`, which drops the moves, fails at 7.

### Statement 4

*Openness.* At every moved point the script computes the real tangent space of the piece: the complex H-tangent
vectors moved to original coordinates, together with i times each. It intersects that space with y-perp to get the
unit-section tangent, and computes the exact rank of the differential of the stated invariants on it. Dual numbers
evaluate rho^2, u^* v / u^* u and the normalized Gram entries as real rational functions. The level-set dimension (unit
section minus rank) equals the orbit dimension at every point.

| Piece | Unit section | Invariant rank | Level set | Orbit |
| --- | --- | --- | --- | --- |
| B9 | 17 | 3 | 14 | 14 |
| V | 15 | 3 | 12 | 12 |
| VB | 13 | 2 | 11 | 11 |
| V^a_+- | 13 | 1 | 12 | 12 |

Each K-orbit is therefore open in its level set; it is also compact, hence closed.

*One orbit per level set.* The argument uses the following inputs, each checked in `orbit_tools`.

- The compact G_2 orbit of the orthonormal pair (e_1, e_2) has dimension 11 = dim V_2(R^7), and V_2(R^7) is connected
  and compact. So G_2 is transitive on orthonormal pairs, and likewise on unit vectors (orbit dimension 6).
- V^a_+-: the points are z = (u, 0, +- i u) with u.u != 0 at every test point. A phase makes u.u real and positive, so
  u = a + i b with a perpendicular to b, and G_2 then carries u to alpha e_1 + i beta e_2. Here alpha, beta >= 0 are
  fixed by rho and |u|. The level set is the single orbit of that normal form.
- V: every test point satisfies v = lambda u, mu != 0 and mu^2 + (1 + lambda^2) u.u = 0. The normal form of u above
  leaves the two sign choices of mu. The octonion automorphism with eigenvalue +1 on e_0, e_3, e_4, e_7 and -1 on
  e_1, e_2, e_5, e_6 is an automorphism because {0, 3, 4, 7} is a subgroup of (Z/2)^3 under XOR. It sends
  (u_0, mu, lambda u_0) to (-u_0, mu, -lambda u_0), and the phase -1 then gives (u_0, -mu, lambda u_0). The two signs
  lie in one orbit.
- B9: every test point has mu = 0, u.u = u.v = v.v = 0 and u x v = 0 (with the `cd_sign` cross product), and a rank-2
  Gram matrix. The compact stabilizer of the plane P = span_C(u, v) has dimension 4 and maps onto a 4-dimensional
  image in gl(P), which is all of U(P) by connectedness. The plane orbit has dimension 10, the real dimension of the
  null cross-zero planes (9 - 4 complex). So G_2 is transitive on those planes, and two bases with one Gram matrix
  differ by a unitary map of P that some stabilizer element realizes.
- VB: the Gram matrix has rank 1, so (u, v) = (alpha n, beta n) with n null. The G_2 orbit of n has dimension 11 at
  every point, so G_2 is transitive on unit null vectors, and the class [alpha : beta] is the whole invariant.

Not checked:

- Group-level stabilizers. Only Lie algebras were computed; finite stabilizer components could identify orbits further
  and do not change the level sets.
- The lambda = infinity chart of V (u = 0, rho read from v). No test point lies there.

### Statement 5

| Unit section | Argument | Inputs checked by the script |
| --- | --- | --- |
| V^a_+- | The unit section is {u : 2 \|u\|^2 = 1, u.u != 0}, which is S^13 minus the link of the quadric u.u = 0. On the cone, u -> u.u is a locally trivial fibration over C^* (scaling makes the base homogeneous), and its fiber, the affine quadric, is homotopy equivalent to S^6. So pi_1 = Z. Following u -> e^(i pi t) u from t = 0 to 1 winds u.u once and ends at -u, so the monodromy is the antipodal map of S^6, of degree (-1)^7 = -1. The Wang sequence gives H^7 = coker(-2 on H^6(S^6)) = Z/2 | V^a points have u.u != 0; the N_+- points have the same form (u, 0, +- i u) with u.u = 0 |
| V | First, V equals S = {u wedge v = 0, mu != 0, mu^2 + u.u + v.v = 0}. In split coordinates the defining relation reads -mu'^2 + eta(u') - eta(v'), which is H-invariant. V is open in S (both have complex dimension 8). The regularity record's classification puts every point of S with nullity >= 8 in V, because mu != 0 and u wedge v = 0 exclude E8-bar, so V is also closed in S. S is connected (next step), hence S = V. Second, z = mu (a, 1, b) splits off arg mu: the unit section is S^1 x Y with Y = {a wedge b = 0, a.a + b.b = -1}. Y fibers over CP^1 minus {+-i}, which retracts onto RP^1, with fiber the affine quadric w.w = -1 (homotopy equivalent to S^6). Along [cos theta : sin theta], theta from 0 to pi, the fiber returns through w -> -w. So Y is homotopy equivalent to the antipodal mapping torus of S^6 | mu != 0, v = lambda u and mu^2 + (1 + lambda^2) u.u = 0 at eight V points |
| VB | VB = {(alpha n, 0, beta n) : n null, [alpha : beta] in B = CP^1 minus {[1 : +-i]}}. Its unit section is the associated bundle P x_(U(1)) N_1, where P is the Hopf circle bundle over B and N_1 is the space of unit null vectors (V_2(R^7)). B is homotopy equivalent to a circle, so P is trivial over B and the unit section is homeomorphic to B x V_2(R^7), homotopy equivalent to S^1 x V_2(R^7) | rank-1 Gram, null, mu = 0 at six points; (n, 0, lambda n) has nullity 16 at lambda = +-i and 12 at lambda = 0, 2, 1 + i; G_2 orbit of n is 11-dimensional and n generates a quaternion subalgebra (stabilizer SU(2)) |
| B9 | G_2 acts freely on bases: the real span of Re u, Im u, Re v, Im v generates all of O (subalgebra dimension 8), so only the identity fixes the basis. By statement 4 it acts transitively on bases with a given Gram matrix. The moduli space, positive definite Hermitian 2 x 2 matrices of trace 1, is an open 3-ball. G -> G^(1/2)-transform of a fixed orthonormal null cross-zero basis is a continuous section, so the unit section is homeomorphic to G_2 x B^3. The phase coefficient t = 1 of the u(1) stabilizer says the stabilizer circle meets G_2 trivially, consistent with freeness | generated subalgebra dimension 8 at five points; plane stabilizer image 4 and plane orbit 10; t = 1 |

Not checked:

- The homotopy steps (fibration local triviality, Wang sequence, retraction of the base) are proofs written here, not
  machine-certified computations.
- The B9 model assumes that every basis of a totally null cross-zero plane is a B9 point (rank-2 pairs). The test
  points are consistent with that, and the classification argument is the regularity record's.
- The V model uses the regularity record's twelve-orbit classification for the closedness step.

## Methods that differ from the record's scripts

| Question | Record's scripts | Verifier |
| --- | --- | --- |
| Phase lift | domain lift R_(e_16) for base generator L_(e_16), inside a solved constant-triple algebra | explicit Y_Phi (rotation of x_0, x_16), checked by one Y' for all 30 doubly pure j; lift ambiguity from a signed union-find on the homogeneous system |
| Test points | explicit original-coordinate families (u = e_1 + i r e_2; z = (alpha a, i m, i beta a); coefficient frames on B9/VB) | recorded representatives moved by products of unipotent split G_2(C) elements (rational and Gaussian coefficients) and real and complex boosts |
| Representation decomposition | sympy eigenvalues of Casimir and center, joint spectral projectors | python-flint ranks of (Omega - n(n+2)/8) and rational factorization of the weight operator -J Z on each Casimir eigenspace |
| Central normalization | primitive integer vector of the center in the g_2 basis | primitive generator from the weights of -Phi Z on the doubly pure space (gcd 1, positive phase coefficient) |
| 3 + conj(3) at rho = 1 | commutant splitting element with 3 + 3 eigenspaces and an invariant symmetric pairing | Casimir 4/9 on the whole fiber plus vanishing cubic trace tr(J rho(X)^3), with the commutant-center structure I0 as positive control |
| Orbit completeness | invariants stationary along the compact tangent (`_invariants_stationary`, `_gram_stationary`) | exact rank of the invariant differential on the unit-section tangent of the piece, compared with the orbit dimension; explicit normal forms and an explicit involution for the sign of mu |
| K-theory | Koszul complex with explicit syzygy | same relations; Smith normal form of the truncated ideal and the identity x^2 = (x^2 + 8x) - 4 (2x) |

## Self-test

`--self-test` removes one property at a time, running the six controls through `parallel.ordered_map`, and requires
each check to fail:

| Control | Property removed | Observed failure |
| --- | --- | --- |
| `drop_leibniz_term` | one Leibniz term in the derivation equations | derivation space dimension 1 instead of 14 |
| `zero_phase_lift` | the phase lift | 28 failures of the lift identity |
| `no_phase_direction` | the phase from the symmetry algebra | N_+ stabilizer dimension 3, not u(2) |
| `unmoved_points` | the non-compact moves | V^a_+ orbit dimension 7 instead of 12 |
| `flip_j` | the orientation of J | B9 kernel weights 0^3 1^3 (baseline computed in the same control) become -1^3 0^3 |
| `wrong_seven_restriction` | the measured su(2) action on R^7 (replaced by the zero action) | measured 7 -> 7 V_0; the ring quotient built from the measurement becomes free, with no Z/2 |
