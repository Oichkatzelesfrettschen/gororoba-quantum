# A pasted technical-reference corpus: claim decomposition, exact falsifiers and hardware residue

The corpus is a conversation with a language-model persona in three registers: a draft "technical reference
guide" (Fermat's Last Theorem, Lie algebras, triality, the Albert algebra, E8 and the Gosset polytope, L-infinity
algebras, spectral triples, Virasoro and affine algebras); a "corpus audit" that joins Pais vacuum engineering,
zero-point energy, tourmaline resonators, E8 phenomenology and loop quantum gravity into one "master action";
and a derivation of the Sugawara central charge, the level-2 Kac determinant and the Coulomb-gas Kac table. The
reference-guide and conformal-algebra registers carry most of the checkable mathematics, and most of it survives
once its conventions are repaired. Every numbered claim of the audit register either fails a computation on its
own inputs or names nothing measurable. No surviving claim needs a quantum processor to settle it. The one claim
with a retained hardware realization is the sl(2) bracket, which the Ascella order interferometer already
measures.

[scripts/reference_corpus_checks.py](../../../scripts/reference_corpus_checks.py) computes every value tagged [E]
and raises when a stated result fails;
[its test](../../../tests/scripts/test_reference_corpus_checks.py) runs in the `tests` check, with the level-5 Kac
determinant (141 s) under the `audit` marker. The script draws no random number. Tags: [P] a source statement,
[E] a value the script computes, [T] a derivation given here, [I] an inference. A rank called exact comes from
elimination modulo the prime 1000003, which bounds the rational rank from below, paired with an explicit
independent solution set, which bounds the nullity from below.

## Verdicts

| Claim (corpus wording, shortened) | Verdict | Authority |
|---|---|---|
| sl(2,C): [H,E] = 2E, [H,F] = -2F, [E,F] = H; spin 1/2 of SU(2), double cover of SO(3) | survives | [E] integer matrices; the 2-dimensional representation is spin 1/2 |
| E8 roots: +-e_i +- e_j and (1/2)(+-1, ..., +-1) with an even number of minus signs | survives | [E] 240 roots, norm 2, closed under all 57600 reflections, span rank 8 |
| Root inner products are 2, +-1 and 0 | refined | [E] from one root: 1 at +2, 56 at +1, 126 at 0, 56 at -1, 1 at -2 |
| Gosset 4_21 is the E8 root system projected into 4 dimensions | refuted | [E] its 240 vertices are the roots themselves, in 8 dimensions (4 + 2 + 1 + 1), with 6720 edges; 2D Petrie projections are the usual pictures |
| Triality permutes 8_v, 8_s, 8_c | survives | [E] the D4 diagram has exactly 6 symmetries (S3) |
| Triality connects F4, Spin(8) and the octonions "through the Cayley-Dickson process" | refined | [E] octonion left multiplication gives Gamma_a = [[0, L_a], [L_conj(a), 0]] with {Gamma_a, Gamma_b} = 2 delta exactly, chirality splitting 16 = 8_s + 8_c; the link is alternativity, and at 16 dimensions the same construction fails on 42 index pairs |
| E6 is the automorphism group of J3(O) | refuted | [E] dim Der(J3(O)) = 52 (F4); the norm-preserving algebra has dimension 78 (E6, the reduced structure group) |
| "E8 > E7 > E6 = Aut(J3(O)) + U(1)" | refuted | [E] 52 + 1 = 53, not 78; the corpus also states Aut(J3(O)) = F4, contradicting itself |
| The Gosset polytope embeds E8 symmetries into 16D sedenions | undefined | no map is stated; Aut of the sedenions is G2 x S3 ([sedenion automorphisms](../../evidence/sedenion-automorphisms/README.md)) |
| L-infinity definition with shuffle sum and Koszul signs | survives | [P] Lada and Stasheff, hep-th/9209099 |
| The n = 3 L-infinity identity as printed | refuted | [E] a skew bracket on R^3 with Jacobiator e0 satisfies it, because every printed term carries l1 or l3 |
| Maurer-Cartan equation sum l_n(alpha^n)/n! = 0 | refined | holds in the shifted (symmetric, degree 1) convention; the skew convention the corpus states needs signs (-1)^(n(n-1)/2), and the series needs a nilpotent or complete filtered algebra |
| Lie algebras as L-infinity with "l_2([x, y]) = [x, y]" | refuted as written | l_2(x, y) = [x, y], with l_1 = 0 and V concentrated in degree 0 |
| f is a quasi-isomorphism if H(V) is isomorphic to H(W) | refuted | the linear component f_1 must induce the isomorphism; the zero map between two copies of a complex with nonzero cohomology is the counterexample |
| Spectral triple (A, H, D): D self-adjoint, [D, a] bounded | refined | the definition also needs a compact resolvent; D carries the metric through Connes' distance, and curvature enters through the heat-kernel coefficients of the spectral action |
| Spectral action Tr f(D/Lambda) | survives | [P] Chamseddine and Connes, hep-th/9606001 |
| Virasoro bracket with central term (c/12)(m^3 - m) | survives | [E] the cocycle identity holds on all 4913 mode triples with \|m\|, \|n\|, \|p\| <= 8 |
| Affine bracket [x t^m, y t^n] = [x, y] t^(m+n) + m delta K | refuted as written | the central term must carry the invariant form (x \| y); without it the bracket is not bilinear (x = 0 gives 0 = m delta K) |
| Fermat's Last Theorem via modularity of elliptic curves | survives as an outline | [P] Frey curve, Ribet's level lowering, and the Wiles and Taylor-Wiles modularity of semistable curves; nothing here computes it |
| Sugawara normalization, central charge and Kac table | survive with corrections | sections below |

## Lie and Jordan algebra

**sl(2) and the quaternion encoding.** [E] The Chevalley relations hold in integers. The Ascella encoding chi of
[hypercomplex_operators.py](../../../gororoba_quantum/hypercomplex_operators.py) sends i, j, k to I = i sigma_3,
J = i sigma_2 and K = IJ = i sigma_1, so H = -i I, E = (J - i K)/2 and F = -(J + i K)/2. The quaternion bracket
[I, J] = 2K is the corpus's [H, E] = 2E written in the compact real form, and the script checks that the order
interferometer's dark probability equals ||[A, B]||_F^2 / 8 = sin^2(theta) sin^2(phi) at three angle pairs.

**E8 and the Standard Model.** [E] The branchings 248 = 120 + 128 under Spin(16), 120 = (28,1) + (1,28) + (8,8) and
128 = (8_s, 8_s) + (8_c, 8_c) under Spin(8) x Spin(8), and 248 = (24,1) + (1,24) + (10,5) + (10bar,5bar) +
(5,10bar) + (5bar,10) under SU(5) x SU(5) are dimensionally consistent. [E] The corpus's SU(5) grouping puts
(3,2) and (1,2) in the "10" (8 states) and both right-handed quarks and the lepton singlet in the "5bar" (7
states). The standard grouping, with Y normalized so that Q = T_3 + Y/2, is 10 = (3,2)_{1/3} + (3bar,1)_{-4/3} +
(1,1)_2 and 5bar = (3bar,1)_{2/3} + (1,2)_{-1}, each traceless in Y. Both groupings contain the same 15 states,
whose Y^3 trace is zero, so the hypercharges survive and the representation assignment does not. [I] Mapping the
three generations to 8_v, 8_s and 8_c puts a generation in a vector representation of Spin(8), and Distler and
Garibaldi show that any embedding of the gravity and Standard Model gauge groups in a real or complex form of E8
"lacks certain representation-theoretic properties required by physical reality" ([P] abstract of arXiv
0905.2658; that the missing property is the chiral three-generation content is a lead from recall, unread here).
The Yukawa couplings "from E8 Clebsch-Gordan coefficients" are named without a computation.

**The Albert algebra.** [E] The script builds H3(O) from `cd_core.cd_sign`, compares its doubled Jordan table
with the Fraction product of
[albert_algebra.py](../packages/manual/checks/albert_algebra.py) (itself checked against SageMath) on all 729
basis pairs, and computes:

- **Derivations.** The constraints D(x o y) = D(x) o y + x o D(y) have rank 677 modulo the prime, so
  dim Der <= 52. The 351 inner derivations [L_x, L_y] satisfy the constraints exactly and span rank 52, so
  dim Der = 52, the dimension of F4.
- **Norm-preserving maps.** The cubic norm comes from the trace polarization 6 t(X,Y,Z) = T(X)T(Y)T(Z) -
  T(X)T(Y o Z) - T(Y)T(X o Z) - T(Z)T(X o Y) + 2 T((X o Y) o Z), with N(I) = 1 and N(diag(2,3,5)) = 30. Linear
  maps preserving it infinitesimally satisfy constraints of rank 651, so their dimension is at most 78. The 52
  derivations and the 26 multiplications L_X by traceless X preserve it and span rank 78, so the dimension is 78,
  that of E6. The identity map scales N and lies outside this algebra.
- **Eigenvalues.** On three fixed integer elements the characteristic cubic has non-negative discriminant
  (356117, 48384, 387700), so three real roots. [I] Reading these as "three spatial dimensions" is numerology:
  every element of a Euclidean Jordan algebra of rank 3 has three real eigenvalues.

## Conformal algebra: the Sugawara and Kac derivations

[E] A vacuum-expectation engine moves the rightmost non-creation mode right by its commutator; it computes every
matrix element below in sympy's exact field.

**Sugawara.** The corpus's first convention, [J^a_m, J^b_n] = f^{abc} J^c_{m+n} + k m delta delta with sum f f =
+2 h_dual delta, needs complex structure constants for a compact algebra. [E] For su(2), f = i epsilon gives +2
delta; real epsilon gives -2 delta, which is what the corpus's second, Hermitian convention absorbs with its
factor i. Results, with K the level in the normalization 2 h_dual = 2 (su(2) at level k has K = k/2):

- [E] <0|L_2 L_{-2}|0> = c/2 with c = 3K/(K + 1), the same at mode cutoffs 3 and 4, and <0|L_3 L_{-3}|0> = 2c,
  consistent with the cubic central term. Hence c = 3k/(k + 2), the corpus's c = k dim g/(k + h_dual).
- [E] <0|J_1 S_0 J_{-1}|0> = (K + h_dual) <0|J_1 J_{-1}|0>. This fixes the normalization by requiring that the
  currents have weight 1; it is the defining condition, not an independent derivation of it, and k = -h_dual
  (the critical level) is excluded.
- [E] **The bilinear pairing is not well defined.** Pairing the state J^2_0 J^0_{-1}|0> with J^1_{-1}|0> gives -iK
  from the word and +iK from the reduced state f^{201} J^1_{-1}|0>: the linear map J^a_n -> J^a_{-n} is no
  anti-automorphism. The sesquilinear (Hermitian) form agrees with the word. None of the corpus's results uses the
  adjoint beyond <0|0> = 1, so they stand.
- [T] The corpus says the (0, 2) term of L_2 "reduces to J_0 J_0 acting on a singlet". The term is J^a_0 J^a_2,
  and it vanishes because J^a_2 |v> = sum f^{acc} K |0> = 0 by antisymmetry.

**Kac determinant.** [E] The level-2 Gram matrix in the basis L_{-2}|h>, L_{-1}^2|h> is [[4h + c/2, 6h], [6h,
8h^2 + 4h]], and at c = 1/2 its zeros are h = 0, 1/2, 1/16. For levels 1 to 5 the Gram determinant computed from
the Virasoro algebra equals

    K_N prod_{rs <= N} (h - h_{r,s})^{p(N - rs)},  h_{r,s} = (r^2 - 1) t/4 + (s^2 - 1)/(4t) + (1 - rs)/2,

on the curve c = 13 - 6t - 6/t, with t = (m + 1)/m reproducing the corpus's h_{r,s}(m) = ((r(m+1) - sm)^2 -
1)/(4m(m+1)). The constant has a closed form the corpus did not reach: K_N = prod_{rs <= N} ((2r)^s s!)^{p(N - rs)
- p(N - r(s+1))}, giving 32, 2304, 37748736 and 8697308774400 at N = 2 to 5 [E]. The corpus's rejected guess gives
8, 96, 6144 and 5898240, so its rejection holds. [E] The degree of the determinant in h equals the total number of
parts of the partitions of N and the zero count sum p(N - rs) (1, 3, 6, 12, 20 at N = 1 to 5); with the null subspace
of dimension p(N - rs) as a lower bound on each zero's order, that degree count is what makes the multiplicities
exact for generic c, the step the corpus left open.

**Coulomb gas.** [E] Feigin-Fuchs modes L_n = (1/2) sum :a a: + beta (n+1) a_n on a Fock vacuum of momentum alpha
give c = 1 - 12 Q^2 and h = alpha^2/2 - Q alpha with beta = -Q, and <L_3 L_{-3}> = 6h + 2c. [E] Sympy confirms
ab = -2, a^2 = 2(m+1)/m and h_{alpha_{r,s}} = ((r(m+1) - sm)^2 - 1)/(4m(m+1)) symbolically. [I] The degenerate
momenta alpha_{r,s} enter as an ansatz; the corpus states that the free-field construction "produces" the singular
vector, but only the screening-charge construction does, and none is written. The Gram determinants at levels 1
to 5 are the independent evidence that these weights carry null vectors. Attributing the BRST resolution to
Feigin and Fuchs 1982 rather than to Felder (1989) is a lead from recall, unchecked.

## Vacuum, crystal, gravity and the master action

Every number is the corpus's own input run through CODATA constants [E].

| Corpus statement | Computed | Verdict |
|---|---|---|
| P = eps0 E^2 c A ~ 1e15 W at 1e13 V/m, 1 cm^2 | 2.65e19 W | refuted, 2.7e4 times larger |
| 1e13 V/m stores ~1e9 J/m^3 | eps0 E^2/2 = 4.4e14 J/m^3 | refuted, 4.4e5 times larger |
| E_crit = sqrt(2 rho_ZPE/eps0) ~ 1e13 V/m | 1.5e10 V/m from the corpus's own rho = 1e9 J/m^3 | internally inconsistent |
| B = E/c ~ 1e5 T | 3.3e4 T | survives to order |
| 1e18 W/cm^2 gives ~1e12 V/m | 2.74e12 V/m | survives |
| rho_ZPE = hbar Lambda^4/(16 pi^2 c^3) | the integrand hbar omega^3/(2 pi^2 c^3) integrates to hbar Lambda^4/(8 pi^2 c^3) | prefactor refuted by a factor 2 |
| Higgs-mass cutoff gives ~1e9 J/m^3, "consistent" | 6.4e43 J/m^3 | refuted by 34.8 orders |
| Planck cutoff gives ~1e113 J/m^3 | 5.9e111 J/m^3 | survives to 1.2 decades |
| xi = hbar/(m c) ~ 0.2 mm at 1 meV | 0.197 mm | survives |
| vev ~ M_Pl/alpha ~ 1e20 GeV | 1.67e21 GeV, above the Planck mass | refuted |
| tourmaline f = v_s/(2d) ~ 3.5 MHz at 7000 m/s, 1 mm | 3.5 MHz | survives as arithmetic on the assumed v_s |
| f_opt = f_Planck alpha^-1 phi^n | n = -206.9 for 148 Hz, -185.9 for 3.5 MHz | no content: phi^n steps by 1.618, so some integer n lands within a factor 1.27 of any frequency |
| a = l_P sqrt(8 pi gamma) ~ 2.7e-35 m, gamma = 0.2375 | 3.95e-35 m; the root of the j = 1/2 area gap is 3.67e-35 m | refuted by 1.46 |
| Casimir modulation cos(2 pi d/a), d ~ 1 nm | 6.2e25 periods per nanometer | untestable: any position jitter averages it to zero |
| strong-field dispersion (E/E_S)^2 (k l_P)^2 | 6.9e-68 at 2.74e12 V/m, 800 nm | untestable |

[I] Further failures of the audit register:

- **Spin networks are not a crystal.** Loop quantum gravity states superpose graphs with no background lattice,
  and Rovelli and Speziale show its minimal area is the spectrum of an observable that a boost leaves unchanged
  ([P] gr-qc/0205108), so "the crystalline aether IS the spin network" has no Lorentz-violating content. The
  quadratically suppressed dispersion survives existing bounds only because it is quadratic: the linear term is
  bounded beyond the Planck scale by GRB 090510 ([P] arXiv 0908.1832), and GW170817 bounds the speed of gravity to
  between -3e-15 and +7e-16 of c ([P] arXiv 1710.05834).
- **The master action fails as written.** A delta-function lattice inside sqrt(-det(g + h)) multiplies
  distributions. The +(1/4) F^2 term has the ghost sign in either metric signature. The scalar equation drops the
  factor 2 of xi phi^2 R. The Maxwell equation from eta F^2 Tr(J^2) must be d_nu[(1 - 4 eta Tr J^2) F^{nu mu}] =
  J^mu, a derivative of the coupling that the corpus omits. The J equation drops the kappa phi and eta F^2 terms.
  F^2 Tr(J^2) is a dimension-6 operator, so the action is an effective theory, not the "rigorous" framework claimed.
  A fermion in the 248 of E8 is in a real representation and carries no chirality.
- **The sanity checks fail.** SC1's "consistent" rests on the 34.8-order error above. SC2's "feasible" lists
  equipment, not a predicted signal. SC3's "ZPE extraction limited by Carnot" is false: a ground state is passive,
  and the repository's Kingston quantum-energy-teleportation ladder measures the boundary
  ([pais-claims-falsification.md](pais-claims-falsification.md#hardware-results-on-ibm_kingston)).
- **Conflict C1's resolution** writes lim_{V -> inf} (E/V)_fixed, which names no quantity.

**The Pais claims P1 and P2, read through the Superforce.** The repository decomposes the Superforce itself in
[pais-superforce-preprints.md](../papers/pais-superforce-preprints.md). The corpus adds two claims:

- **P1, curvature from rotating fields.** [I] P1 is true in kind and empty in size. Field energy gravitates through
  the Einstein coupling 8 pi G/c^4 = 8 pi/(c^4/G), so the 1.2e44 N that Pais calls the force of unification is the
  denominator that suppresses every laboratory curvature. [E] The corpus's own laser (1e18 W/cm^2, u = I/c) gives a
  Ricci scale of 6.9e-30 m^-2 and, as an order estimate, a strain of 6.9e-40 across its 10 um waist, 6.9e-17 of
  the ~1e-23 strain LIGO resolves. Rotation above 1e9 Hz enters only through u.
- **P2, vacuum energy shift above 1e16 V/m.** [E] The Euler-Heisenberg correction is standard QED: it reaches
  1e-12 J/m^3 already at 7.1e9 V/m and is 3.9e12 J/m^3 at 1e16 V/m. The number is real and the threshold is not,
  and nothing in it is specific to Pais.

**Undefined items.** The aether boundary condition div J = Phi_aether laplacian Phi_compact, the fractional
compactification exp(-k R_frac), the dodecaplex resonator, the 148 Hz drive, the monoatomic gold substrate, the
condensate suppression of delta g by "a factor > 100", recursive Postnikov "fractals", spectral triples in
(infinity, n)-categories and motivic integration over derived categories define no quantity, so nothing in them
can be falsified.

## Survivors

1. The sl(2,C) relations and their su(2) real form, realized in the quaternion encoding as [I, J] = 2K.
2. The E8 root system in D8 coordinates and its inner-product profile (1, 56, 126, 56, 1); the 8-dimensional
   Gosset polytope with 240 vertices and 6720 edges; the dimensions of the Spin(16), Spin(8)^2 and SU(5)^2
   branchings.
3. Triality as the S3 of the D4 diagram, and Cl(8) from octonion left multiplication with 16 = 8_s + 8_c.
4. Aut(J3(O)) of dimension 52 (F4) and the norm-preserving algebra of dimension 78 (E6), correcting the corpus.
5. The hypercharges of one Standard Model generation, without the corpus's SU(5) grouping.
6. The L-infinity definition, the Maurer-Cartan equation in the shifted convention, and the spectral action;
   the spectral-triple definition with a compact resolvent added.
7. The Virasoro algebra and its cocycle; the affine algebra once (x | y) multiplies the central term.
8. c = k dim g/(k + h_dual), the weight-1 normalization, the level-2 Gram matrix and its Ising roots 0, 1/2,
   1/16.
9. The Kac product with K_N = prod ((2r)^s s!)^{p(N-rs) - p(N-r(s+1))}, checked through level 5, and the Kac
   table h_{r,s}(m) from the Coulomb gas.
10. The order-of-magnitude statements marked "survives" in the table above. None supports a device or a
    prediction.

## Reconciliation with the repository

- **E8 has two homes, now tied.** [octonion_structure_checks.md](octonion_structure_checks.md) builds E8 by
  Construction A from the associator characters of `cd_core`'s octonions. The corpus's D8 coordinates give the same
  root count, norm and reflection closure; both are E8 root systems, and the octonion route explains why the
  corpus's "E8 from Cayley-Dickson" intuition has a real core: the Fano-plane characters generate the [8,4,4]
  Hamming code.
- **The loss of division beyond the octonions is the 42-pair set.** [E] The left-multiplication Clifford test,
  exact at 8 dimensions, fails at 16 on 42 index pairs, and the script requires that set to equal the index pairs of
  `cd_core.sedenion_zero_divisor_corpus`. The repository's census reaches the same 42 pairs as the
  non-anticommuting ones ([octonion_structure_checks.md](octonion_structure_checks.md)). The corpus's gap, "loss of normed division
  algebra properties not addressed", is addressed there.
- **The sedenion "hidden symmetry" is S3.** Aut(S) = G2 x S3 is computed exactly in the repository
  ([sedenion automorphisms](../../evidence/sedenion-automorphisms/README.md),
  [Brown 1967](../papers/brown-1967-generalized-cayley-dickson.md)): no continuous symmetry beyond G2, one finite
  S3.
- **The vacuum-extraction premise is measured.** On Kingston the record-steered lowering reached 93 percent of
  ideal while no arm went below the passivity floor
  ([pais-claims-falsification.md](pais-claims-falsification.md#hardware-results-on-ibm_kingston)).

## Hardware residue, in the requested order

Every survivor is exact mathematics that the script settles. A run on any device measures that device's
realization of an encoding whose ideal law is computed classically; a case is justified only by a device question
with a mutation arm and a null arm ([algebra_circuit_rules.md](../algebra_circuit_rules.md#hardware-probes)).

1. **Ascella (Quandela, 12 modes).** The sl(2) bracket is already measured. The order interferometer reads D =
   ||[A, B]||^2/8, and its commuting-generator mutation sets the bracket to zero. In job `739a5271` (2026-10-24),
   all 27 preregistered endpoints qualified, the mutation difference read 0.1646 against an ideal 0.1727 (radius
   0.0229), the mutation dark output read 0.0008 against 0, and 1.27 percent of events fell outside the logical
   block ([retained run](../../../results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/README.md)).
   Seven later jobs found a mesh-specific coherent error; on the new-seed and replication jobs (04 to 07) the
   fitted element offsets predict its direction, not its amplitude
   ([replication case](../../design/ascella-signed-coherence-conformance.md#replication-case-job-06-and-job-07)).
   **Candidate, unsubmitted:** an associator-character interferometer on 8 of the 12 modes. For distinct
   imaginary units e_a, e_b the column signs s(x), defined by (e_a e_b) e_x = s(x) e_a (e_b e_x), form a
   nontrivial character of F_2^3 whose kernel is the quaternion subalgebra {0, a, b, a XOR b}; [E] this holds for
   all 21 pairs. A diagonal of those +-1 phases between two pair-analyzer layers turns the character into dark
   outputs on the four columns outside the kernel. The mutation keeps the mesh shape and replaces the octonion
   sign table with the associative Cl(0,3) table on the same index set, whose character is trivial for every
   pair [E], so the ideal dark outputs fall to zero; a = b (trivial by alternativity [E]) is a second mutation,
   and the zero-phase mesh is the null. A quaternionic triple cannot serve, because any two distinct octonion
   units generate a quaternion subalgebra that the remaining columns leave. Its device question is whether the
   frozen offset model transfers to a mesh family it was never fitted on. Noise simulation cannot answer that, because the offsets are properties of the
   served meshes. It needs a local Perceval dry run, the frozen predictor and a written case before approval.
2. **QX as the falsifier for Tuna-17.** No corpus claim reaches Tuna-17 scale on its own. The 42-pair result
   connects to the zero-divisor witnesses of the
   [matched-response case](../../design/tuna17-zero-divisor-matched-response.md), whose left operand
   (e1 + e10)/sqrt(2) lies in that set. The QX emulator's role, as in
   [the N = 21 conformance](../../evidence/n21_qx_conformance/README.md), is the ideal law of the exact emitted
   program. A local qxelarator run of the matched-response programs, which the case already authorizes, separates
   serialization and routing faults from device response before any Tuna-17 batch.
3. **Tuna-17.** The matched-response case is the program; this corpus adds no witness to it.
4. **IBM Heron r2.** No survivor needs 16 or more qubits or concerns a named qubit. The Ising c = 1/2 and Kac
   weights are free-fermion results that exact classical computation settles at every size a device reaches.
5. **Remaining credits, read live 2026-10-28 00:54 UTC.**

   | Provider | Balance | Note |
   |---|---|---|
   | IQM Resonance | 2.50 credits | expire 2026-11-01 00:00 UTC; no survivor warrants them |
   | Open Quantum | 25 Spark, 0 Full | every upload is public |
   | Quantum Inspire | free tier, ledger change 0 | 4994 s and 7813120 shots retained account-wide |
   | Quandela | usage only: Ascella 28 jobs and 23.29 free credits, Belenos 49 jobs and 50.27, sim:belenos 16 | the usage route reports no balance |

   IBM usage was not read in this pass. A 16-mode octonion associator order interferometer, the doubled
   S diag(L_a L_b, L_ab) S, needs Belenos's 24 modes and waits on its recovery.

## Sources pending registration

These identities were confirmed through arXiv abstracts on 2026-10-28 but are not yet records of
[SOURCES.json](../../SOURCES.json): Distler and Garibaldi 0905.2658, Lada and Stasheff hep-th/9209099,
Chamseddine and Connes hep-th/9606001, Rovelli and Speziale gr-qc/0205108, Fermi GRB 090510 0908.1832 and GW170817
1710.05834. Kac (1979), Feigin and Fuchs (1982) and Felder (1989) were not retrieved. Their statements here are
tagged [P] from abstracts or marked as leads; registration is a separate change.

## Uncertainty

[I] That the reference-guide and conformal-algebra survivors are correct: very high, resting on exact
computation; the Kac product beyond level 5 rests on Kac's theorem, not on this script. That no claim of the audit
register predicts a measurable effect: high; a derivation of the lattice constant, the scalar couplings or the
Casimir enhancement factor from a stated dynamics would reopen it. The Ascella candidate's value depends on the
offset model transferring across mesh families, which the replication jobs leave open.
