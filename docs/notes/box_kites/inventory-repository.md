# Repository inventory: zero divisors, box-kites, algebra witnesses

Compiled 2026-10-17 from a read-only search of this repository.

## 1. Notes (docs/notes/)

- math-0403113.md (De Marrais, Box-Kites III): assessor, edge-sign and strut conventions; the 84 diagonal zero-divisor lines in 42 assessor planes; the seven octahedral box-kites. Open: statement limited to those lines, not every zero-divisor vector in an assessor plane; physics links not established.
- octonion_structure_checks.md: box-kite frustration (each of 7 signed sedenion box-kites has 12 edges, 8 sign -1 triangles; frustration minimum 4 for shared vertex signs, 3 for shared phases), associator slices spanning RM(1,3) and E8, walk-sector periods. Open: box-kite gap marked [I]; 63-of-105 anticommuting pairs and 42 zero-divisor index pairs are [E].
- reality_ripple_measurement_design.md: the seven strut labels mapped to the Fano plane; signed-kite spectral deduction via docs/sources/open_gororoba/check_signed_kite_switching.py. Open: measured interference is a design target.
- sedenion_hardware_witness_review.md: corrects an external proposal ((e1+e10)(e2-e13) = e3+e7+e8-e12, not 0; annihilator of e1+e10 corrected; a unitary cannot output the zero vector). Open: hardware witness measurements.
- math-0511691.md (Biss-Dugger-Isaksen): ann dim is a multiple of 4, at most 2^n-4n+4; the unit zero divisors of A_4 form the continuous manifold V_2(R^7) (math-0511691.md:41), and the 84 are the signed two-support basis representatives e_i + t e_j inside it (Proposition 12.1, math-0511691.md:61-62); Ann(a,b) formula. Open: A_5 strata and fixtures marked [I].
- math-0702075.md (Biss-Christensen-Dugger-Isaksen II): D-locus and T_n^c stratification; A_5 nullity table. Open: Theorem 7.5 leaves ZD_12 inside H_5^perp partly undetermined.
- 0905.2987.md (eigentheory of M_a): spectrum of left multiplication controls zero divisors; Theorem 8.2 for top-dimensional zero divisors. Open: Question 9.2 is a conjecture on computer evidence.
- cayley_dickson_rank_topology_sources.md, cayley_dickson_annihilator_sources.md: source ledgers (de Marrais, Zhilina 2608.26893).
- cayley_dickson_sparse_census.md, annihilator_kernel_limits.md: sparse annihilator census; limiting annihilators along polynomial paths (dimension 12 at e1+e18), proved only in the local chart.
- cd_associator_defect_census.md: non-associating basis triples (1848 of 4096 at D=16; 168 of 512 at D=8).
- handbacks/sedenion_geometry_and_twists.md: Reggiani and Albuquerque-Majid reproduced; Bales candidates; "not run, venue claims open".
- Also bearing on counts/nullity/witnesses (read at grep level only): 1312.1414.md, 2505.11747.md, levratti-2026-fano-css.md, 2608.28163.md, four_support_rank_loci.md, dimension32_skew_schur_charts.md, open_gororoba_handoff.md, 2507.08088.md.

## 2. Code (public functions)

gororoba_quantum/designs.py:
- left_mult_gate(dim, m, flip=None) -> Gate: x -> e_m x on log2(dim) qubits, index bit b on qubit b.
- left_mult_adjoint_gate(dim, m) -> Gate.
- design_a_associator(i, j) -> (QuantumCircuit, int, int, int): ancilla-free three-qubit octonion associator phase construction (QuantumCircuit(3, 1), gororoba_quantum/DESIGN_NOTES.md:119-141), a different construction from the controlled 4 data + 1 control fixed-pair test that AGENTS.md counts.
- lcu_witness(a_pair, b_pair, phase) -> QuantumCircuit: (L_ei + L_ej)/2 on a superposition (4 data qubits plus the ancilla on qubit index 4, five qubits in all).
- design_b_zero_divisor(a_pair, b_pair, s) -> QuantumCircuit: zero-product LCU; P(selector=0) = 0 dark (e1+e10)(e4-e15), 1 bright (e1+e10)(e4+e15); 4 data + 1 selector.
- design_d_phase_sweep(a_pair, b_pair, phase) -> QuantumCircuit: lcu_witness on b = (e_k + e^{i phase} e_l)/sqrt2, one point of Design B's phase-resolved zero-product fringe (designs.py:144-148, DESIGN_NOTES.md:278-293).
- design_c_associator_spectrum(dim, i, j, *, omit_adjoint, flip) -> QuantumCircuit: Walsh spectrum of W = L_{e_i e_j}^dag L_{e_i} L_{e_j}, the multi-bit associator distribution (DESIGN_NOTES.md:223-240).

gororoba_quantum/cd_core.py: cd_sign(dim,p,q); cd_multiply(dim,a,b); basis(dim,index,scale); left_mult_matrix_check(i,j); associator(dim,x,y,z); triple_sign(dim,i,j,k); classify_octonion_triples(); fano_completion(i,j); sedenion_zero_divisor_corpus() (336-row corpus of 6-tuples); sedenion_zero_divisors() (pairs); left_mult_matrix(dim,v); sedenion_counterexamples().

scripts/algebra_circuit_fixtures.py: zero_products(); hadamard_test(i,j,k,*,leak,cleanup); measurement_basis_and_workspace(); sage_convention(); product(dim,x,y); omega(dim,i,j,k). Gates core-251/252.

scripts/qi_zero_divisor_cases.py: certify(); select_exact(i,j); logical(case), routed(...) -> cQASM; build() (4 data qubits plus 1 selector per 5-qubit replica region, Latin square of dark/bright/fixture); analyze(run_dirs); analyze_series(...); wilson(k,n); self_test().

scripts/qi_crosstalk_teleport_cases.py: disjoint_stars(backend), disjoint_paths(backend, limit) (Tuna-17 topology layouts); additivity_circuit(n, stars, config), teleport_circuit(n, paths, dialect) -> cQASM; build(catalogue); analyze(run_dirs).

scripts/qi_coupler_zz_map.py: edges(qubits), neighbors, parts; circuit_lines(nqubits, targets, quadrature, delay); readout_lines; build(profile) (tuna_17/qx); analyze_table; exact_probabilities(lines, nqubits, omega, coupling); conformance(profile); explain_spectators.

scripts/cd_associator_defect_census.py: sign_array, omega, triple_counts(dim), subspace_types(dim), pair_completions(dim), walsh, check_lifting, census.
scripts/octonion_structure_checks.py: associator_code(), box_kites() -> list[dict], walk_sectors(pair, expected), gram_moment_embedding(), convention_bridge(), left_multiplication_products(). Exact arithmetic, gates core-228/229.
scripts/singular_sector_dynamics.py: sector_split, sector_sizes, size_recursion, census_link, dilation_and_steps, lcu_circuit(i,j,t,beta) -> Qiskit circuit, amplification_unitary, amplification, population_flow, operator_boundary.
docs/sources/open_gororoba/check_signed_kite_switching.py: characteristic_polynomial, verify_graph, verify_evidence, check_controls.

## 3. Evidence

- docs/evidence/cd_associator_defect_census/census.json: classical census (triples, subspaces, pairs, walsh, blocks, lifting).
- docs/evidence/reviewer_associator_audit/: 256 basis products agree across two implementations; (e1+e10)/sqrt2 (e2-e13)/sqrt2 = (e3+e7+e8-e12)/2; (e4-e15) gives zero; M M^dag = 16 I.
- results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_tuna_17 (16384 shots per replica): P(s=0) dark 0.4908/0.455/0.4665 (ideal 0), bright 0.5175/0.4926/0.5269 (ideal 1), fixture 0.4814/0.4973/0.5184 (ideal 0.5); pooled over the three replicas (analysis.json by_case): dark 0.4708 [0.4664, 0.4752], fixture 0.4990 [0.4946, 0.5035], bright 0.5123 [0.5079, 0.5167]; readout-corrected 0.4571, 0.4836, 0.5006. The dark-fixture and bright-fixture contrasts are resolved but small (about 0.03 and 0.01 against ideal 0.5 each), so the endpoints compress to about 0.5.
- results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_qx (2048 shots): dark 0.0, bright 1.0, fixture 0.4814 to 0.5005.
- results/quantum_inspire/runs/2026-10-17T034409Z-zero_divisor_qx-batch-00/-01 (per-batch series, on branch qi/zero-divisor-per-batch-runs): dark 0, bright 1, fixture 0.4977.
- Coupler ZZ map and crosstalk/teleport runs of 2026-10-16 (not algebra witnesses).

## 4. Rules (AGENTS.md root, verbatim sections)

See AGENTS.md "Algebra circuit design rules": bullets "Zero-product witnesses" and "Observables and claims" (the LCU success law P(s=0) = ||xy||^2 / 2 for Design B, M M^dag = D I so P = ||xy||^2 / D for the universal contraction; diagonal fixed-pair witness reconstructs no coherence; 2^w Pauli settings for a selected coherence; register counts 4+1, 4+1, 8+1, 12+1+workspace; the interferometer is an associator-sign interference witness, no holonomy or braiding claim).
Quantum Inspire "Execution facts": Tuna 20 ns single-qubit, 60 ns CZ, 800 ns measurement, 200 or 500 us init, angles quantized to pi/36, ALAP scheduling, wait(n) in 20 ns cycles, mid-circuit measurement allowed, no binary-controlled gates (feed-forward in post-processing); bit order QX/Tuna q0 rightmost, Ry q0 leftmost; Ry takes no measurement statements and measures every qubit at the end (H+CNOT with a bit register failed with "error interpreting cQASM script"); write cQASM directly with explicit wait for timing.

## 5. Gates

core-001/002 (ruff), core-039 (mypy), core-228/229 (octonion_structure_checks), core-251/252 (algebra_circuit_fixtures), core-327 (crosstalk --check), core-330 (zero_divisor --replay, plus --replay-series on the branch), core-331 (crosstalk --replay, --self-test), core-332/333 (coupler ZZ map), core-348 (zero_divisor --check, --self-test).

## Reuse

Top builders: designs.design_b_zero_divisor (+ lcu_witness), designs.design_a_associator, designs.left_mult_gate. design_a_associator is the three-qubit octonion construction and lcu_witness the five-qubit (4 data + 1 ancilla) sedenion one; the AGENTS.md register counts describe the controlled sedenion tests. octonion_structure_checks.box_kites() already enumerates the seven signed sedenion box-kites.
