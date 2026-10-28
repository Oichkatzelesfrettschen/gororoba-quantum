# LLM-persona corpus: verified results and the runs they admit

An external conversation with an LLM persona supplied a mathematics reference draft (Lie algebras, E8, triality,
the Albert algebra, L-infinity algebras, spectral triples), a speculative "scalar-ZPE / crystalline aether / E8"
synthesis, and a derivation of the Sugawara construction, the Coulomb gas and the Kac determinant. Every claim was
decomposed to first principles and checked. This report keeps what survived: the mathematics and physics now
verified, the quantum runs that can test them on Ascella, Tuna-17 and the other reachable systems, and the
corrections the same re-derivation made to earlier repository notes. The appendix lists in one line each the
claims that were removed and why.

Tags: [E] computed by [scripts/persona_corpus_checks.py](../../../scripts/persona_corpus_checks.py), which raises
when a stated identity or inequality fails ([its test](../../../tests/scripts/test_persona_corpus_checks.py) runs in
the `tests` check; the octonion Albert case and Kac level 5 carry `audit`); [T] proved here in a line or two; [P] a
standard published result; [R] settled by an existing repository record; [U] a literature result quoted from memory
that the source library does not yet hold. Nothing below has been submitted to any provider; every run still needs
its dry run, written case and the owner's approval.

## 1. Verified mathematics

**Lie algebras and exceptional structures.**

- sl(2,C) with H, E, F: [H,E] = 2E, [H,F] = -2F, [E,F] = H, structure constants c_HE^E = 2, c_HF^F = -2,
  c_EF^H = 1. The same brackets hold in the spin-1 representation, so they govern every spin, not only spin 1/2. [E]
- E8: 240 roots, 112 of the form +-e_i +-e_j and 128 of the form (1/2)(+-1, ..., +-1) with an even number of minus
  signs; inner products {-2, -1, 0, 1, 2}, with <alpha, -alpha> = -2. [E]
- The Gosset polytope 4_21 is the convex hull of those roots: 8-dimensional, 56 neighbours per vertex, 6720 edges.
  [E]
- Triality: Out(Spin(8)) = S3 permutes 8_v, 8_s, 8_c [P]. Under D4 x D4 the E8 roots split 24 + 24 + 64 + 64 + 64,
  so 248 = (28,1) + (1,28) + (8v,8v) + (8s,8s) + (8c,8c), three triality-related 64s. [E]
- Branchings: E8 > SU(5) x SU(5) gives 248 = 24 + 24 + 50 + 50 + 50 + 50. E7 > E6 x U(1) gives
  133 = 78 + 1 + 27 + 27. E8 > Spin(16)/Z2 gives 248 = 120 + 128. [E]
- The exceptional Jordan algebra J3(O) has 27 real dimensions. Exact integer ranks on the `cd_core` octonions give:
  - dim Der(J3(O)) = 52 (f4), so Aut(J3(O)) = F4;
  - the Lie algebra preserving the cubic norm N(X) = T(X^3)/3 - T(X)T(X^2)/2 + T(X)^3/6 has dimension 78 (e6).

  The same code reproduces the first two rows of the Freudenthal magic square over R, C, H: 3/8, 8/16, 21/35. [E]
- The octonionic triality triple (L_a R_a, L_a, R_a), i.e. the Moufang identity a(xy)a = (ax)(ya), holds in all 1344
  octonion cases tested. It fails in 10752 of 26880 sedenion cases (first witness a = e1 + e2, x = e1, y = e12), so
  triality does not continue up the Cayley-Dickson tower. [E]
- The sedenions add no continuous symmetry: Der(S) = Der(O) = g2, dimension 14. Their extra symmetry is Brown's
  discrete S3 in Aut(S) = G2 x S3
  ([sedenion-automorphisms](../../evidence/sedenion-automorphisms/README.md)). [R]

**Homotopy algebra and noncommutative geometry (corrected forms).**

- L-infinity algebras: l_n has degree 2 - n, and the generalized Jacobi identity carries (-1)^{i(j-1)} besides the
  Koszul sign (Lada-Markl) [P].
  - The Maurer-Cartan equation sum l_n(alpha, ..., alpha)/n! = 0 holds for degree-1 alpha when the sum converges.
  - l_n = 0 for n > 2 gives a differential graded Lie algebra; it is an ordinary Lie algebra only when V = V_0. [T]
  - An L-infinity quasi-isomorphism is a morphism whose linear part f_1 induces the isomorphism on cohomology. [T]
- Spectral triple (A, H, D): D is self-adjoint with compact resolvent and [D, a] is bounded [P].
  - Compact resolvent makes the spectral action Tr f(D/Lambda) a finite sum when the cutoff f has compact support,
    since only finitely many eigenvalues lie in any bounded window. [T]
  - A rapidly decreasing cutoff also needs summability. With eigenvalues sqrt(log(n + 1)), f(x) = exp(-x^2) gives the
    divergent sum of 1/(n + 1). Theta-summability, Tr exp(-t D^2) < infinity for t > 0, restores finiteness for
    Gaussian-type f. [T]
  - D encodes the metric through Connes' distance; curvature enters through the heat-kernel expansion. [P]
- Affine (Kac-Moody) algebra: [x t^m, y t^n] = [x,y] t^{m+n} + m delta_{m+n,0} (x|y) K. The invariant form is
  needed for bilinearity. With (x|y) = tr(xy) the cocycle identity holds on every sl(2) loop triple tested. [E]
- Postnikov towers have Eilenberg-MacLane layers K(pi_n, n). [P]

**Conformal field theory: all verified.**

- Virasoro: [L_m, L_n] = (m - n) L_{m+n} + c/12 (m^3 - m) delta_{m+n,0}. [E]
- Sugawara, checked symbolically in k for affine sl(2):
  - S_0 has eigenvalue k + h^v = k + 2 on every level-1 current state, which fixes L_0 = S_0/(k + h^v);
  - <0|L_2 L_{-2}|0> = c/2 with c = 3k/(k + 2), the sl(2) case of c = k dim g/(k + h^v).

  Only the (1,1) normal-ordered term of L_2 contributes. The (0,2) term vanishes because J_2 annihilates the
  level-2 singlet (the corpus gave a different reason). The consistent structure-constant convention is the one
  with i: real antisymmetric constants contract to -2h^v delta. [E]
- Level-2 Gram matrix: [[4h + c/2, 6h], [6h, 8h^2 + 4h]] on (L_-2, L_-1^2). Its determinant is
  2h(16h^2 + (2c - 10)h + c), with roots (5 - c +- sqrt((c - 1)(c - 25)))/16. At c = 1/2 these are the Ising weights
  1/2 and 1/16. [E]
- Coulomb gas:
  - c = 1 - 12Q^2 and h_alpha = alpha(alpha - 2Q)/2;
  - screening charges a, b = Q +- sqrt(Q^2 + 2), with ab = -2, a^2 = 2(m + 1)/m and b^2 = 2m/(m + 1);
  - alpha_{r,s} = ((1 - r)a + (1 - s)b)/2 gives h_{r,s} = ([r(m + 1) - s m]^2 - 1)/(4m(m + 1)), checked for
    r, s <= 4. [E]
- Kac determinant, exact in h and m for N = 1..5:

  det M_N = K_N prod_{rs <= N} (h - h_{r,s})^{p(N - rs)}

  - The constant is K_N = prod ((2r)^s s!)^{m(r,s)}, where m(r,s) counts the partitions of N in which r appears
    exactly s times: K_N = 2, 32, 2304, 37748736, 8697308774400.
  - Each zero has order exactly p(N - rs). A null subspace only bounds that order from below; exactness comes from
    the degree count deg_h det M_N = sum p(N - rs), checked at every level. [E]
  - The free-field route takes alpha_{r,s} as input, so it confirms the formula; it does not derive where the
    zeros sit independently. [I]

## 2. Verified physics

- Ideal parallel plates attract with F = -pi^2 hbar c A/(240 d^4) [P].
- For two identical passive half-spaces at T = 0, the Lifshitz energy over the ideal value is
  (45/pi^4) sum_p int_0^1 Li_4(r_p^2) ds, which is at most 1 because |r_p| <= 1. It is 0.204 at eps = 6.3 and 0.223 at
  7.1. [E]
- The Schwinger field m_e^2 c^3/(e hbar) is 1.32e18 V/m. At 1e16 V/m, Euler-Heisenberg polarisation changes the
  vacuum energy density by 3.9e12 J/m^3, which is 8.8e-9 of the field energy. This is ordinary QED, paid for by the
  field. [E]
- The half-wave acoustic frequency of 1 mm of tourmaline (7000 m/s) is 3.5 MHz; 1e18 W/cm^2 corresponds to
  2.7e12 V/m; the Compton length of a 1 meV scalar is 0.197 mm. [E]
- The zero-point integral of hbar omega^3/(2 pi^2 c^3) to a cutoff Lambda is hbar Lambda^4/(8 pi^2 c^3). At a 125 GeV
  cutoff that is 6.4e43 J/m^3, 1.2e53 times the observed dark-energy density of 5.3e-10 J/m^3 (Planck 2018:
  H0 = 67.4, Omega_m = 0.315). This is the cosmological-constant problem, unresolved by anything in the corpus.
  [E]
- The LQG area spectrum is 8 pi gamma l_P^2 sum_p sqrt(j_p(j_p + 1)) [P]; l_P sqrt(8 pi gamma) = 3.95e-35 m at
  gamma = 0.2375. [E]
- A coherent state is a displaced vacuum: its stress-energy is the classical field's, and its fluctuations equal
  the vacuum's. [T]
- A ground state is passive: no operation confined to a region lowers that region's energy without a measurement
  record from outside it. This is the boundary the QET ladder measures.
  [Kingston result](pais-claims-falsification.md#hardware-results-on-ibm_kingston): information excess
  +0.107 +- 0.006 against an ideal 0.115, with no arm below the record-independent floor. [R]

## 3. Quantum runs

The verified mathematics consists of theorems. A device run does not test a theorem; it tests the device's
realisation of one. Each design below therefore names its device question, an ideal law with a mutation arm that
removes the algebraic property, and a null arm ([algebra_circuit_rules.md](../algebra_circuit_rules.md#hardware-probes)).
They appear in the owner's order of preference.

### Ascella: the octonion associator in two-photon interference

Ascella offers 12 modes and up to 6 photons from source modes 0, 2, ..., 10, with threshold detectors, at 1e-6
credits a shot and 200 free credits a month, reset on the first ([quandela/README.md](../quandela/README.md)).

**Mathematics tested.** L_a L_b != L_(ab) for octonions (the non-associativity behind the failed homomorphism), and
the Schwinger fact that indistinguishable photons carry the symmetric representation of the mode unitary.

**Construction.**

- a = (e6 + e7)/sqrt2, b = (e5 + e7)/sqrt2, and ab = (-e0 - e1 - e2 + e3)/2 (all unit octonions).
- L_a L_b and L_(ab) are orthogonal 8 x 8 matrices. Both keep span(e0..e3), so each route is a 4-mode interferometer.
- Two photons enter algebra modes 2 and 3. Mapped onto Ascella's source modes 0 and 2, they occupy four adjacent
  physical modes.

**Ideal laws over two-click events** [E]:

| Route | Indistinguishable photons | Distinguishable photons | D at HOM visibility 0.875 |
|---|---|---|---|
| L_a L_b | pairs {0,3}, {1,2}, 1/2 each | all six pairs 1/6 | +0.824 |
| L_(ab) | pairs {0,2}, {1,3}, 1/2 each | all six pairs 1/6 | -0.824 |
| associative control: a = (e1 + e2)/sqrt2, b = (e1 + e3)/sqrt2, both routes | pairs {0,2}, {1,3} | all six 1/6 | -0.824 for both |

The endpoint is D = P({0,3} or {1,2}) - P({0,2} or {1,3}), conditioned on two clicks.

**What each arm shows.**

- **Associator arms:** the route difference is 2 in the ideal case and 1.65 at the calibrated visibility.
- **Associative control:** removing the associator makes the route difference exactly 0. This is the mutation arm.
- **Distinguishable photons:** D = 0 on every route. The associator appears only through two-photon interference.
  The mixture model D = V/(V + 1.5(1 - V)) ties the measured D to the published HOM visibility.

**Device question.** Does the per-run HOM visibility in `perfs_at_plan`
([calibration.md](../quandela/calibration.md)) predict the two-photon law of a compiled 4-mode unitary, or does a
mesh phase error (the residual of plans ascella-perturbed-compilation-case and ascella-heater-coupling-families)
move it? A 0.01 standard error on D takes 2630 two-click events per arm; four arms at that depth cost well under
one credit.

**Written case.** [ascella-two-photon-associator-case.md](../../design/ascella-two-photon-associator-case.md) freezes the
eight-iteration request and states seconds, credits (ceiling 1.262144), the HOM-floor decision and the procedure; it
waits for the owner's approval.

### QX as the falsifier for Tuna-17: the QET passivity ladder without real-time feed-forward

QX emulates 10 qubits (2048 shots). Tuna-17 has 17 qubits and mid-circuit measurement, but no binary-controlled
gates, so feed-forward runs in post-processing ([quantum_inspire/README.md](../quantum_inspire/README.md)).

The two-qubit QET ladder of [pais-claims-falsification.md](pais-claims-falsification.md#the-passivity-ladder-of-the-two-qubit-qet-model)
needs no real-time branch:

- Alice's X measurement precedes Bob's operation and cannot depend on it, so running each fixed Bob rotation and
  binning shots by Alice's recorded bit reproduces the feed-forward ensemble.
- The binned fixed-sign arms give the +, -, -, + table. The product-state |00> preparation is the mutation arm.
- The channel-floor margin and the information excess are the endpoints.

Ideal values at h = k = 1, rebuilt here from the Hamiltonian [E]:

| Quantity | Value |
|---|---|
| Energy Bob extracts, E_B | 0.114748 |
| Reversed-sign raise | 0.332466 |
| Binned half-contrast | 0.223607 |
| Record-flip zero, q* | 0.2566 |
| Alice's injection | 0.707107 |

**Order of work.**

1. QX runs every arm first and must reproduce these laws within shot noise. A QX miss falsifies the circuit, not the
   device.
2. Tuna-17 then decides the prediction against Kingston's +0.107 excess.

**Device question.** Tuna-17's state-dependent readout assignment
([tuna-17.md](../quantum_inspire/tuna-17.md)): the floor margin is first-order sensitive to it, and binning by the
same record cancels it in the excess.

Recorded as inbox plan [tuna17-qet-passivity-replication](../../state/plans/tuna17-qet-passivity-replication.json);
free tier, about 2.6 s a job.

### Tuna-17 itself

Item above. A 16-17 qubit critical-Ising run probing c = 1/2 and the weights 1/16 and 1/2 would measure Trotter and
noise error, not the Kac formula. It has no device question, so it is not proposed.

### IBM Heron

The QET ladder has run on ibm_kingston (three jobs, 110 s of the backup instance). Extraction against distance on a
chain of 16 or more qubits (item 4 of the Pais note) remains the only larger case. It waits on an exact free-fermion
reference checked against exact diagonalization at 12-14 qubits.

### Systems with credits before the end of November

- **IQM.** 30 credits expire 2026-11-01, and the plan grants up to 30 a month "based on availability". Garnet costs
  0.50 credits a second ([iqm/README.md](../iqm/README.md)). The QET ladder with genuine feed-forward through
  `cc_prx` (Pais note item 3) separates a Heron-specific feed-forward loss from a protocol error. It first needs a
  garnet:mock compile and one priced batch to qualify a non-pi conditional angle.
- **Quandela.** November's 200 credits cover the Ascella run above many times over.
- **Other providers.** [provider-credits.md](../../runbooks/provider-credits.md) reads their balances; none of their
  backends adds a test of section 1 or 2.

### Classical next step

The magic-square code reaches the Freudenthal triple system and the e7 and e8 rows on the same `cd_core` table,
which [adjacent-algebras.md](../packages/adjacent-algebras.md) lists as unbuilt.

## 4. Corrections to earlier repository notes

The script recomputes 34 printed numbers of [pais-claims-falsification.md](pais-claims-falsification.md),
[qpu_vacuum_cd_review_reconciliation.md](qpu_vacuum_cd_review_reconciliation.md) and
[octonion_structure_checks.md](octonion_structure_checks.md) from CODATA constants and `cd_core`, without importing
the scripts that own them; the QET model is rebuilt from its Hamiltonian. [E]

All agree, including:

- the patent and field figures;
- the Schwinger exponent -268.4 and the Euler-Heisenberg fractions;
- the Ford-Roman figures, the 8.33 pm Casimir gap and the Gertsenshtein figures;
- the QET values;
- the non-associating basis-triple counts 168, 1848 and 15960 at D = 8, 16, 32;
- the D = 16 zero-divisor products and rank 12, the 63 anticommuting pairs, and Construction A's 240 vectors.

Three statements of the Pais note were corrected there:

- The Superforce electron ratio 8.8e-46 is relative to c^4/G; against the c^4/(2G) the sentence names, it is
  1.75e-45.
- The spin-up radiation of about 2.7e-13 W is a scale estimate. A uniform ramp radiates only at its ends; a sin^2
  ramp averages 3.3e-12 W and peaks at 6.7e-12 W. Neither duration nor final rate bounds the power, which follows
  the square of omega'' (a 0.1 s quintic smoothstep peaks near 9e-8 W), so the note now states the two evaluated
  profiles only.
- The 0.254 MeV Cherenkov threshold uses the index of water at 400 nm.

Not re-derived: the Kingston measurements, the product-state values 0.581 and -0.247, and the vacuum-model cutoff
errors that the [vacuum_models](../../evidence/vacuum_models/README.md) replay defines.

## Appendix: claims removed

| Claim | Why it was removed |
|---|---|
| E6 = Aut(J3(O)); E6 = Aut + U(1) | 52 against 78 [E] |
| 4_21 is a 4D projection; it embeds E8 into the sedenions | 8-dimensional [E]; Aut(S) has dimension 14 [R] |
| <alpha, beta> = 2 for alpha = +-beta | <alpha, -alpha> = -2 [E] |
| The displayed n = 3 L-infinity identity | holds for a bracket with nonzero Jacobiator [E] |
| Kac-Moody central term without the invariant form | not bilinear [E] |
| f_opt = f_Planck alpha^-1 phi^n | any frequency lies within phi^(1/2) of the grid; 148 Hz needs n = -206.9 [E] |
| Tourmaline amplifies Casimir by more than 1e3 | at most 1, 0.22 at the stated eps [E] |
| Rotating fields curve spacetime measurably | 7e-30 over a metre at 1e13 V/m [E]; [R] Pais note |
| Coherent fields engineer the vacuum | displaced vacuum [T] |
| Three generations as 8_v, 8_s, 8_c in E8 | the 248 is real, so fermions in it are vector-like [T]; [U] Distler-Garibaldi 2010 |
| SU(5) assignments (L in the 10; u^c, e^c in the 5bar) | the corpus's "10" has 8 states and its "5bar" 7 [E] |
| v ~ 1e20 GeV with lambda ~ 0.1-1 and m ~ 1 meV | radial mass 1.8e19 to 5.8e19 GeV; 1 meV needs lambda = 3e-64 [E] |
| E_crit ~ 1e13 V/m; 1e15 W over 1 cm^2 | 1.5e10 V/m from the corpus's own density; 1.3e19 W [E] |
| ZPE with a Higgs cutoff is 1e9 J/m^3, "consistent" | 6.4e43 J/m^3, and the prefactor is 1/(8 pi^2) [E] |
| LQG area sqrt(sum j(j+1)); a = 2.7e-35 m; spin networks are a lattice | sum of roots; 3.95e-35 m [E]; no background lattice [T] |
| Casimir modulation, photon and GW dispersion signatures | 10^(-5.5e49), 4e-56 and 7e-81 [E] |
| ZPE extraction limited by Carnot | ground states are passive [T]; Kingston [R] |
| Master action and its equations of motion | delta-function metric; index mismatch [T]; scalar EOM follows in neither convention [E] |
| ZPE integrals, dodecaplex arrays, aether boundary, (infinity, n) spectral triples, "fractal" Postnikov towers, E8 selection rules, Yukawas from E8 coefficients | no definitions or observables |
