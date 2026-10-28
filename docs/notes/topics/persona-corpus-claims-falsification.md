# LLM-persona corpus: claim-by-claim falsification, survivors and hardware reach

An external conversation with an LLM persona supplied four kinds of material: a review and expansion of a
mathematics reference draft (Lie algebras, E8, triality, the Albert algebra, L-infinity algebras, spectral
triples), a role-played "scalar-ZPE / crystalline aether" design critique, a "corpus audit" that ends in a master
action and a funding roadmap, and a derivation of the Sugawara construction, the Coulomb gas and the Kac
determinant. This note decomposes each claim to first principles, records its verdict, lists what survives, then
asks which survivors any provider can test. A last section re-derives the repository's own earlier falsification
notes from scratch, which the owner asked for as part of the same review.

Tags: [E] computed by [scripts/persona_corpus_claim_bounds.py](../../../scripts/persona_corpus_claim_bounds.py),
which raises when a stated identity or inequality fails ([its test](../../../tests/scripts/test_persona_corpus_claim_bounds.py)
runs in the `tests` check; the octonion Albert case and Kac level 5 carry `audit`); [T] proved here in a line or two;
[P] a standard published result; [R] settled by an existing repository record, linked; [U] a literature result
quoted from memory that the source library does not yet hold, so it carries no weight here until a source note
exists. Verdicts: **survives**, **survives corrected**, **falsified**, **unfalsifiable** (no definite content),
**untestable** (definite but beyond any reachable measurement).

## 1. Mathematics reference draft

| # | Claim | Decomposition | Verdict |
|---|---|---|---|
| A1 | Wiles' proof runs through modular forms and elliptic curves | [P] Wiles (with Taylor) proved modularity of semistable elliptic curves, which with Ribet's level lowering gives Fermat; full modularity is Breuil-Conrad-Diamond-Taylor | survives (pointer only) |
| A2 | sl(2,C) basis H, E, F with [H,E] = 2E, [H,F] = -2F, [E,F] = H; c_HE^E = 2, c_HF^F = -2, c_EF^H = 1 | [E] integer matrices | survives |
| A3 | These relations "describe spin-1/2 particles" | [E] the same brackets hold in the spin-1 representation (3 x 3); sl(2,C) = su(2) (x) C governs every spin, the 2 x 2 matrices are the spin-1/2 representation | survives corrected |
| A4 | E8 has 240 roots: +-e_i +-e_j and (1/2)(+-1, ..., +-1) with an even number of minus signs | [E] 112 + 128 = 240, all of norm 2 ("all permutations of" the half-integer vectors is redundant) | survives |
| A5 | The Gosset 4_21 polytope is "E8's root system projected into 4 dimensions" | [E] 4_21 is the convex hull of the 240 roots in R^8: affine dimension 8, 56 neighbours per vertex, 6720 edges. The 4D object is a different construction (the H4 folding onto two 600-cells) | falsified |
| A6 | Triality permutes 8_v, 8_s, 8_c of Spin(8) | [P] Out(Spin(8)) = S3. [E] Under D4 x D4 the E8 roots split 24 + 24 + 64 + 64 + 64, i.e. 248 = (28,1) + (1,28) + (8v,8v) + (8s,8s) + (8c,8c), three triality-related 64s | survives |
| A7 | J3(O) is the 3 x 3 Hermitian octonion matrices; "E6: automorphism group of J3(O)" | [E] exact integer ranks: dim Der(H3(O)) = 52 (f4) and the algebra preserving the cubic norm has dimension 78 (e6). The magic-square rows for R, C, H come out 3/8, 8/16, 21/35 by the same code. E6 is the norm-preserving (reduced structure) group; Aut(J3(O)) = F4 | falsified (survives corrected) |
| A8 | "The Gosset 4_21 polytope embeds symmetries of E8 into 16D (sedenions)" | [R] Aut(S) = G2 x S3, of dimension 14 ([sedenion-automorphisms](../../evidence/sedenion-automorphisms/README.md)); no construction is offered and the sedenions carry no 248-dimensional symmetry | falsified |
| A9 | Triality connects F4, Spin(8) and the octonions "through the Cayley-Dickson process", extending "to sedenions and beyond" | [E] the triality triple (L_a R_a, L_a, R_a) is the Moufang identity a(xy)a = (ax)(ya): 0 failures in 1344 octonion cases, 10752 of 26880 sedenion cases fail (first witness a = e1 + e2, x = e1, y = e12) | survives for O; falsified beyond O |
| A10 | L-infinity: graded maps l_n with the displayed higher Jacobi identity | [P] Lada-Markl: l_n has degree 2 - n and the identity carries the sign (-1)^{i(j-1)} besides the Koszul sign; both are missing | survives corrected |
| A11 | Maurer-Cartan equation sum l_n(alpha, ..., alpha)/n! = 0 for degree-1 alpha | [P] correct in the degree-(2 - n) convention, given convergence (nilpotent or complete filtered algebra) | survives |
| A12 | "If l_n = 0 for n > 2, we recover a Lie algebra" | [T] that is a differential graded Lie algebra; a Lie algebra needs V = V_0 as well (then l_1 = 0 by degree) | falsified |
| A13 | The displayed n = 3 identity `l1(l2(x,y)) - l2(l1 x, y) - (-1)^|x| l2(x, l1 y) + l3(x, y, l1 z) = 0` | [E] a degree-0 bracket with l1 = l3 = 0 and Jacobiator (1, 1, 1) satisfies it, since every term vanishes; the true n = 3 identity reduces to Jacobi there. The display is the n = 2 Leibniz rule plus a stray term | falsified |
| A14 | Quasi-isomorphism: H^n(V) = H^n(W) | [T] the isomorphism must be the one induced by the linear part f_1; abstractly isomorphic cohomology is not enough | survives corrected |
| A15 | Spectral triple (A, H, D): D self-adjoint, [D, a] bounded; "D encodes curvature"; spectral action Tr f(D/Lambda) | [T] the omitted axiom, compact resolvent, is what makes Tr f(D/Lambda) finite (D = 0 on an infinite-dimensional H satisfies the listed axioms and gives Tr f(0) = infinity). D encodes the metric (Connes distance); curvature enters through the heat-kernel expansion of the action | survives corrected |
| A16 | Spectral triples organised as (infinity, n)-categories encode "recursive symmetries" | no objects, morphisms or composition are defined | unfalsifiable |
| A17 | Virasoro [L_m, L_n] = (m - n) L_{m+n} + c/12 (m^3 - m) delta | [E] the Kac computation below runs on it | survives |
| A18 | Kac-Moody [x t^m, y t^n] = [x,y] t^{m+n} + m delta_{m+n,0} K | [E] the central term must be m delta (x\|y) K with an invariant form: as printed it takes the same value at (x, y) and (2x, y), so the bracket is not bilinear; with (x\|y) = tr(xy) the cocycle identity holds on every sl(2) loop triple tested | falsified (survives corrected) |
| A19 | Postnikov towers with K(pi_n, n) layers; "fractal extensions add self-similarity" | [P] the first half is standard; the second has no definition | survives / unfalsifiable |

## 2. Persona design critique

| # | Claim | Decomposition | Verdict |
|---|---|---|---|
| B1 | E_ZPE = int [rho_vac Phi_scalar exp(-k R_frac)] d^n x + Delta Phi_feedback | no units, no definitions of Phi_scalar, R_frac or n; an energy is added to a potential | unfalsifiable |
| B2 | Tourmaline nodes in a "4D-projected dodecaplex" maximise "scalar field coherence" | no coupling, field equation or observable | unfalsifiable |
| B3 | f_opt = f_Planck alpha^-1 phi^n | [E] f_0 = 2.54e45 Hz; 148 Hz needs n = -206.9; on the phi-grid every frequency lies within a factor phi^(1/2) = 1.27 of some f_n, so the formula predicts nothing | falsified as a prediction |
| B4 | div J_boundary = Phi_aether lapl Phi_compact with a "monoatomic gold" resonator | undefined symbols | unfalsifiable |

## 3. Corpus audit, synthesis and master action

The Pais items are already decomposed in [pais-claims-falsification.md](pais-claims-falsification.md); the rows
below add only what the persona states beyond it.

| # | Claim | Decomposition | Verdict |
|---|---|---|---|
| P1 | Rotating EM fields above 1e9 Hz produce interferometrically measurable curvature | [E] the corpus's own 1e13 V/m stores 4.4e14 J/m^3; 2 G u L^2/c^4 over a metre is 7e-30. [R] radiation, active-mass and GW-conversion bounds in the Pais note | falsified |
| P2 | Fields above "E_crit ~ 1e16 V/m" change the vacuum energy by more than 1e-12 J/m^3 | [E] the Schwinger field is 1.32e18 V/m (1e16 is 0.0076 of it); Euler-Heisenberg gives Delta u = 3.9e12 J/m^3 at 1e16 V/m, 8.8e-9 of the field energy. The inequality holds in standard QED; it is ordinary vacuum polarisation paid for by the field | survives as standard QED; "engineering" falsified |
| Z1 | Casimir F = -pi^2 hbar c A/(240 d^4); tourmaline arrays amplify it by eta > 1e3 | [P] ideal-plate formula. [E] Lifshitz at T = 0 for two identical passive half-spaces: E/E_ideal = (45/pi^4) sum_p int_0^1 Li_4(r_p^2) ds <= 1 because \|r_p\| <= 1; at the corpus's own eps = 6.3 and 7.1 the ratio is 0.204 and 0.223, short of 1e3 by 4500 (optical dispersion lowers it further) | formula survives; enhancement falsified |
| Z2 | L = ... + kappa phi <rho_ZPE>, "oscillations at n f_Planck/1e27 perturb local ZPE density" | [T] <rho_ZPE> is a constant, so the term is a linear tadpole removed by shifting phi; no V(phi) is given | unfalsifiable |
| E1 | <alpha, beta> = 2 for alpha = +-beta; particle interactions follow E8 root adjacency | [E] <alpha, -alpha> = -2; inner products are {-2, -1, 0, 1, 2}. No map from roots to quantum numbers is given | corrected / unfalsifiable |
| E2 | R -> C -> H -> O -> S doubles dimension; sedenions hold "hidden symmetries" absent from O | [R] Der(S) = Der(O) = g2 (dimension 14), so no continuous symmetry is new; Brown's discrete S3 factor is ([sedenion-automorphisms](../../evidence/sedenion-automorphisms/README.md)) | survives only as the discrete S3 |
| A1' | GW dispersion omega = ck(1 + beta k^2 a^2) reveals a crystalline spacetime | [E] at a = 3.95e-35 m and 100 Hz, (ka)^2 = 6.8e-81 | untestable |
| A2' | A condensate with <phi> > phi_crit suppresses metric fluctuations by more than 100 | no coupling constants, so xi_coherence is not computable | unfalsifiable |
| C1 | Coherent fields carry a nonzero vacuum stress-energy in the limit V, N -> infinity | [T] a coherent state is a displaced vacuum D(alpha)\|0>: its stress-energy is the classical field's and its fluctuations equal the vacuum's | falsified |
| C2 | Fermion generations are 8_v, 8_s, 8_c inside E8 > Spin(16)/Z2 > Spin(8) x Spin(8) | [E] the triality-symmetric 64 + 64 + 64 exists (A6). [T] the 248 is a real representation, so fermions in it are vector-like; generations must be equivalent SM representations, and the three 64s are inequivalent under any gauge group that does not contain the outer automorphism. [U] Distler and Garibaldi (Commun. Math. Phys. 298, 2010) prove no three-generation chiral embedding exists in E8 | falsified |
| C3 | A Planck lattice keeps Lorentz invariance at wavelengths far above a | [E] corrections (a/lambda)^2 are unmeasurable at tree level. [U] radiative corrections can feed lattice-scale Lorentz violation into low-energy physics unless fine-tuned (Collins et al., PRL 93, 2004) | untestable / open |
| M1 | Tourmaline array at d = 1 mm resonates at 3.5 MHz; E_crit = sqrt(2 rho_ZPE/eps0) ~ 1e13 V/m; B_0 ~ 1e5 T; peak power ~ 1e15 W over 1 cm^2; a 1e18 W/cm^2 laser gives ~1e12 V/m | [E] 3.5 MHz correct; with the corpus's own rho_ZPE = 1e9 J/m^3, E_crit = 1.5e10 V/m (with the Planck density 3.2e62); B_0 = 3.3e4 T; c eps0 E^2/2 over 1 cm^2 is 1.3e19 W, 1.3e4 times the stated power; the laser gives 2.7e12 V/m | mixed: frequency and laser survive, E_crit and power falsified |
| M2 | V = (lambda/4!)(phi^2 - v^2)^2 + m^2 phi^2/2 with lambda ~ 0.1-1, v = M_P/alpha ~ 1e20 GeV, m ~ 1e-3 eV, coherence length 0.2 mm "matches the array spacing" | [E] M_P/alpha = 1.7e21 GeV; hbar/(mc) = 0.197 mm is correct but is 0.2 of the 1 mm spacing; the radial mass is sqrt(lambda v^2/3 - 2 m^2) = 1.8e19 to 5.8e19 GeV at v = 1e20 GeV, and a 1 meV scalar needs lambda = 3e-64 | falsified (internally inconsistent) |
| M3 | E8 > SU(5) x SU(5) > SM; generation-1 assignments; Yukawas from E8 Clebsch-Gordan coefficients | [E] 248 = 24 + 24 + 50 + 50 + 50 + 50 holds. Lambda^2 5 = (3bar,1)_{-2/3} + (3,2)_{1/6} + (1,1)_1 = u^c + Q + e^c and 5bar = d^c + L; the corpus's "10" (Q + L) has 8 states and its "5bar" (u^c, d^c, e^c) has 7. The Yukawa claim has no content | branching survives; assignments falsified |
| S1 | J3(O) unifies ZPE, crystal and E8; "3 eigenvalues = 3 spatial dimensions"; E8 > E7 > E6 = Aut(J3(O)) + U(1) | [E] Aut has dimension 52, the norm group 78; the true neighbour statement is E7 > E6 x U(1), 133 = 78 + 1 + 27 + 27. The eigenvalue reading is numerology | falsified |
| S2 | LQG area A = 8 pi gamma l_P^2 sqrt(sum j(j+1)); a = l_P sqrt(8 pi gamma) ~ 2.7e-35 m; spin networks "are" the crystal lattice | [P] the spectrum is a sum over punctures of sqrt(j(j+1)): two j = 1/2 punctures give 1.732, the corpus form 1.225. [E] l_P sqrt(8 pi gamma) = 3.95e-35 m. [T] spin-network states are diffeomorphism-invariant superpositions of graphs, with no background lattice | falsified |
| S3 | Casimir modulation cos(2 pi d/a) of amplitude 1e-6 at d ~ 1 nm; photon dispersion (E/E_S)^2 (k l_P)^2; GW polarisations set by "E8 quantum numbers" | [E] 2.5e25 periods per nm; averaging over 0.1 nm of roughness suppresses the modulation by 10^(-5.5e49); the optical shift is at most 4e-56; the third is undefined | untestable / unfalsifiable |
| SC1 | rho_ZPE = hbar Lambda^4/(16 pi^2 c^3) and a Higgs cutoff gives 1e9 J/m^3, "consistent" | [E] the integral of hbar omega^3/(2 pi^2 c^3) is hbar Lambda^4/(8 pi^2 c^3); at 125 GeV it gives 6.4e43 J/m^3, 6e34 times the claim and 1.2e53 times the observed dark-energy density 5.3e-10 J/m^3 | falsified |
| SC2 | "Experimentally feasible with existing technology" | the listed components exist; no listed measurement has a predicted signal (Z1, S3) | unfalsifiable as stated |
| SC3 | No contradictions: "ZPE extraction limited by Carnot"; "SM check, since E8 contains SU(3) x SU(2) x U(1)" | [T] a ground state is passive, so no cyclic operation extracts work from it, and Carnot needs two temperatures. [R] the Kingston QET ladder ([Pais note](pais-claims-falsification.md#hardware-results-on-ibm_kingston)) measured no arm below the record-independent floor. Containing the gauge group is not producing the chiral spectrum (C2) | falsified |
| MA | Master action and its equations of motion | [T] a metric g + sum delta^4(x - x_n) puts products of distributions under sqrt(-det); `d_nu F^{mu nu} = J^mu + eta F^{mu nu} Tr J^2` has one free index on the left and two on the right. [E] the scalar equation follows from the Lagrangian in neither box convention: with box = d_t^2 - d_x^2 the mass and quartic signs flip; with box = -d_t^2 + d_x^2 the xi R term needs +2 xi R phi and the kappa term the opposite sign | falsified |

## 4. Sugawara, Coulomb gas and Kac determinant

| # | Claim | Decomposition | Verdict |
|---|---|---|---|
| K1 | [S_0, J^b_{-1}]\|0> = (k + h^v) J^b_{-1}\|0>, fixing L_0 = S_0/(k + h^v) | [E] affine sl(2), symbolic in k: eigenvalue k + 2 on every level-1 state | survives |
| K2 | c = k dim g/(k + h^v) from <0\|L_2 L_{-2}\|0> = c/2 | [E] 3k/(k + 2) for sl(2). Only the (1,1) normal-ordered term of L_2 contributes, as claimed; the stated reason for the (0,2) term is wrong (that term is J_0 J_2 and J_2 annihilates the level-2 singlet), the conclusion right | survives (one justification corrected) |
| K3 | The structure-constant convention with sum f^{abc} f^{acd} = 2h^v delta^{bd} and no i | [E] real totally antisymmetric constants with a positive invariant form contract negatively (sum eps eps = -2 delta); the i-convention the derivation then uses is the consistent one | survives corrected |
| K4 | Level-2 Gram matrix, det = 2h(16h^2 + (2c - 10)h + c), roots (5 - c +- sqrt((c-1)(c-25)))/16, Ising values 1/2 and 1/16 | [E] exact | survives |
| K5 | Coulomb gas: c = 1 - 12Q^2, h_alpha = alpha(alpha - 2Q)/2, a, b = Q +- sqrt(Q^2 + 2), h_{r,s}(m) = ([r(m+1) - sm]^2 - 1)/(4m(m+1)) | [E] every step for r, s <= 4 | survives |
| K6 | Kac determinant det M_N = K_N prod_{rs<=N} (h - h_{r,s})^{p(N-rs)}; K_N left open, the guess prod (2n)^{p(N-n)} rejected | [E] the identity holds exactly in h and m for N = 1..5 with K_N = prod ((2r)^s s!)^{m(r,s)}, m(r,s) the number of partitions of N in which r appears exactly s times: K = 2, 32, 2304, 37748736, 8697308774400. The rejected guess gives 8 at N = 2, correctly rejected | survives, open item closed |
| K7 | Each zero has order exactly p(N - rs) "because the Gram matrix depends analytically on h" | [T] a null subspace of dimension p(N - rs) gives order at least p(N - rs); exactness follows from the degree count deg_h det M_N = sum p(N - rs), [E] at N = 1..5 | survives corrected |
| K8 | The free-field and Verma-module routes are independent | [I] the free-field route takes the degenerate momenta alpha_{r,s} as input, so it is a consistency check of the formula, not a second derivation of where the zeros sit | survives qualified |

## 5. What survives

Standard mathematics, now checked: A2, A4, A6, A11, A17, A19 (first half), and the corrected A3, A7 (Aut(J3(O)) = F4,
norm group E6), A9 for octonions only, A10, A14, A15, A18; the whole of section 4 with the corrections of K2, K3 and
K7 and the Kac constant of K6. Standard physics: the ideal Casimir formula (Z1), Euler-Heisenberg polarisation
above 1e-12 J/m^3 at 1e16 V/m (P2), the Schwinger field, the 3.5 MHz half-wave frequency and the 2.7e12 V/m laser
field (M1), the 0.197 mm Compton length of 1 meV (M2), the E8 > SU(5)^2 and D4 x D4 branchings (M3, A6), and the
discrete S3 in Aut(S) (E2).

Nothing that the corpus presents as new survives. The Pais, ZPE, crystal, aether, E8-generation, J3(O)-spacetime,
LQG-lattice and master-action claims are falsified, internally inconsistent, or carry no definite prediction.

## 6. Hardware reach of the survivors

[I] The survivors are theorems or established physics. A device run cannot falsify a theorem; it tests the device's
realisation of it, and the repository admits such a run only as a device question with a mutation arm, +, -, -, +
arms and a null arm ([algebra_circuit_rules.md](../algebra_circuit_rules.md#hardware-probes)). The physics
survivors need force, field or radiation apparatus that no provider here offers
([vacuum_field_run_opportunities.md](../vacuum_field_run_opportunities.md)). Each item below still needs its dry
run, written case and the owner's approval; nothing here is submitted.

In the owner's order of preference:

1. **Ascella.** 12 modes, at most 6 photons, threshold detectors, 1e-6 credits a shot, 200 free credits a month
   reset on the first (UTC) ([quandela/README.md](../quandela/README.md)). No survivor needs it. The closest is
   A2/A3 as the Schwinger map: N indistinguishable photons in two modes carry the spin-N/2 representation, and a
   beam splitter of angle theta sends \|1,1> to \|1,1> with probability cos^2(2 theta), against
   1 - sin^2(2 theta)/2 for distinguishable photons (the mutation arm). At theta = pi/4 that is the HOM dip, whose
   visibility Quandela publishes with every calibration (87-89 %, [calibration.md](../quandela/calibration.md)), so
   a run would repeat a published figure. The octonion identities (A7, A9) need the product of two registers or a
   16-mode dilation, which 12 modes cannot hold. Recommendation: no corpus-derived Ascella job.
2. **QX as the falsifier for Tuna-17.** QX emulates 10 qubits, 2048 shots; Tuna-17 has 17 qubits, mid-circuit
   measurement and no binary-controlled gates, so feed-forward is done in post-processing
   ([quantum_inspire/README.md](../quantum_inspire/README.md)). The one corpus claim with a device-testable core
   is SC3/C1's extraction premise, which the repository already tests with the two-qubit QET passivity ladder. Its
   fixed-sign arms binned by Alice's record (the +, -, -, + table), the product-state mutation and the channel-floor
   and information-excess endpoints need no real-time feed-forward, so they run on Tuna-17 by selection on the
   recorded bit. QX supplies the noiseless law per arm before any hardware shot; Tuna-17 then decides the
   prediction against Kingston's measured +0.107 information excess and negative floor margin. The device question
   is Tuna-17's state-dependent readout assignment ([tuna-17.md](../quantum_inspire/tuna-17.md)), to which the
   margin is first-order sensitive. Free tier, about 2.6 s a job. This is the recommended corpus-derived run.
3. **Tuna-17 itself.** As in item 2. A 16-17 qubit critical-Ising run (testing c = 1/2 through the K4/K5 weights)
   has no device question and would benchmark noise, not the Kac formula; not recommended.
4. **IBM Heron.** The QET ladder has run on ibm_kingston (three jobs, 110 s of the backup instance). The remaining
   corpus-adjacent case is the Pais note's item 4, extraction against distance on a chain of 16 or more qubits,
   which waits on an exact free-fermion reference; nothing new is proposed.
5. **Credits before the end of November.** IQM: 30 credits expire 2026-11-01, and the plan grants up to 30 a month
   "based on availability" ([iqm/README.md](../iqm/README.md)); Garnet costs 0.50 credits a second. The Pais note's
   item 3, the QET ladder with genuine feed-forward through `cc_prx` on Garnet, is the corpus-relevant use, after a
   garnet:mock compile and one priced batch qualify a non-pi conditional angle. Quandela's November 200 credits have
   no corpus use (item 1). Other providers' balances are read by
   [provider-credits.md](../../runbooks/provider-credits.md); none of their backends adds a corpus test.

Classical follow-up worth more than any of these: the magic-square code above reaches the Freudenthal triple
system and e7, e8 rows on the same `cd_core` table, which [adjacent-algebras.md](../packages/adjacent-algebras.md)
lists as unbuilt.

## Re-derivation of the earlier notes

The script recomputes 34 printed numbers of [pais-claims-falsification.md](pais-claims-falsification.md) (patents,
Superforce, QET), [qpu_vacuum_cd_review_reconciliation.md](qpu_vacuum_cd_review_reconciliation.md) and
[octonion_structure_checks.md](octonion_structure_checks.md) from CODATA constants and `cd_core`, without importing
the scripts that own them. The QET model is rebuilt from its Hamiltonian, and Bob's energy is minimised exactly as
a first harmonic in 2 theta. [E] Results:

- Agree: Eq. 1 (1.774e24 W/m^2), the surface field, pressure, charge limit, sphere fields and field mass, the
  Schwinger rate exponent (-268.4), both Euler-Heisenberg fractions, the Eq. 4 cutoff (10.60 keV), the Ford-Roman
  figures (3.72e-26 J/m^3, 42.38 orders), the 8.33 pm Casimir gap, the Gertsenshtein figures, the proton-pressure
  ratios, the 100 nm Casimir mass equivalent, 25/256, and the QET values E_B = 0.114748, E_x = 0.332466,
  contrast 0.223607, q* = 0.25658 and injection 0.707107. The algebra counts reproduce: non-associating basis
  triples 168, 1848, 15960 at D = 8, 16, 32 = (D-2)(D-4)(D+6)/2; (e1 + e10)(e4 - e15) = 0;
  (e1 + e10)(e2 - e13) = e3 + e7 + e8 - e12; rank L_(e1+e10) = 12; 63 anticommuting imaginary pairs; Construction A
  on RM(1,3) gives 240 norm-2 vectors.
- Corrected in the Pais note: the Superforce electron ratio 8.8e-46 is relative to c^4/G, while the sentence names
  c^4/(2G), against which it is 1.75e-45. The spin-up radiation "about 2.7e-13 W" is the scale
  mu0 (Q R^2 omega/(3 tau^2))^2/(6 pi c^3), not a profile result: a uniform ramp radiates only at its ends, a sin^2
  ramp averages 3.3e-12 W and peaks at 6.7e-12 W. The conclusion, negligible radiation, stands. The 0.254 MeV
  Cherenkov threshold uses the index of water at 400 nm (1.343), which the note now says.
- Not re-derived: the Kingston measurements themselves, the product-state mutation values (0.581, -0.247), which
  need the Kabsch floor of `scripts/qet_passivity_controls.py`, and the vacuum-model cutoff errors of
  vacuum_field_run_opportunities.md, whose finite evolution the [vacuum_models](../../evidence/vacuum_models/README.md)
  replay defines.
