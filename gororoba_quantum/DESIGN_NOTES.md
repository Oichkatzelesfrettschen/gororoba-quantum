# Cayley-Dickson quantum circuits

Quantum circuits whose structure comes from the open_gororoba Cayley-Dickson
algebra kernel. Left multiplication L_{e_m} by a basis unit is a signed
permutation of the 2^k basis states (e_p * e_q = cd_sign(dim,p,q) e_{p XOR q}),
so it is unitary on k qubits. The designs turn two algebraic defects that the
kernel measures classically -- the octonion associator and sedenion zero
divisors -- into hardware observables on the 156-qubit Heron backends.

Run `$PYTHON cd_core.py` for the classical structure, `$PYTHON verify.py` for
the ground-truth checks, `$PYTHON designs.py` for ideal statevector outcomes,
and `$PYTHON hw_estimate.py --out ../results/hw_estimate` for the routed cost and
noisy prediction on ibm_fez. `verify.py` and `designs.py` exit nonzero on the
first failed check.

## Verification against the kernel

The sign table is ported from cd_kernel::cayley_dickson::signs::cd_basis_mul_sign_iter
into `cd_core.cd_sign`. `verify.py` reads each kernel CSV only after its sha256
matches every registry record under registry/data/project_csv that pins it.

- Convention pin: all 320 cells of the kernel's data/csv/multiplication_table_8D.csv
  and multiplication_table_16D.csv equal cd_sign by index and sign. This is the
  check that fixes orientation.
- Zero-divisor corpus: `sedenion_zero_divisor_corpus()` equals the kernel's 336
  signed rows of data/csv/reggiani_standard_zero_divisor_pairs.csv. The corpus
  is invariant under the rephasing e_p -> -e_p (p != 0), which flips the sign of
  all 42 octonion and 210 sedenion imaginary-imaginary products, so the corpus
  match is a structural check and carries no orientation evidence. `verify.py`
  runs that rephasing and confirms both facts.
- Octonion norm multiplicativity |x y| = |x| |y| holds on random vectors and the
  sedenion norm fails it on some vectors; both are invariant under the same
  orthogonal rephasing.
- The 42/168 associative/anti-associative split of ordered distinct octonion
  triples comes from the Cayley-Dickson signs. The all-positive XOR-indexed
  table is the group algebra of F_2^3, which is associative and splits 210/0.

## Design A: octonion associator as a Fano Z-string

Source: cd_associator, A(e_i,e_j,e_k) = (e_i e_j) e_k - e_i (e_j e_k).

Finding: W = L_{e_i e_j}^{-1} L_{e_i} L_{e_j}, with L_{e_i e_j} = cd_sign(8,i,j)
L_{e_{i^j}}, is diagonal with eigenvalue +/-1, the associator sign of (e_i, e_j,
e_k). Across the 21 unordered pairs these are exactly the 7 non-identity 3-qubit
Z-strings, three pairs each, one per Fano line by point-line duality in
PG(2,2): W is +1 precisely on the associating subspace {0, i, j, i^j}. For
(i,j)=(1,2) the net operator is Z on qubit 2. The cd_sign(8,i,j) factor is a
global sign in an uncontrolled circuit and a relative phase under coherent
control, so every controlled use of W carries it.

Mechanism: the circuit appends L_{e_j}, L_{e_i}, L_{e_{i^j}} as three separate
gates with barriers, so the hardware composes them and performs the cancellation
down to the net Z-string; numpy never multiplies the operators. The octonions
are alternative, so L_{e_m}^2 = -I and L_{e_{i^j}} = -cd_sign(8,i,j)
L_{e_i e_j}^{-1}: the circuit implements W times a global sign. A
line-completing k0 (associative) and a one-bit-away k1 (anti) get opposite
signs. A Hadamard on the differing qubit, applied before the X gates that load
k0, prepares (|e_{k0}> + |e_{k1}>)/sqrt2 for either value of that bit of k0; W
maps it to the orthogonal minus state, and a second Hadamard makes the measured
bit deterministic. Three qubits, ancilla-free.

Predicted ideal: readout bit 1 with probability 1 for all 21 pairs. Confirmed by
statevector in `designs.py`.

Observable and falsifier: the readout-bit probability; ideal 1.0. A measured
value at or below 0.5 + 3 sigma means the phase did not survive, so either the
associator sign is miscompiled or readout is worse than reported.

Measured (results/hw_estimate/ibm_fez_record.json): the (1,2) ISA circuit on
ibm_fez is depth 55 with 16 CZ on physical qubits 131-133, and the same circuit
under the backend noise model gives P1 = 0.9685.

## Design B: sedenion zero-divisor interference witness

Source: find_zero_divisors(16, 1e-10). A sedenion zero divisor is a pair
a = e_i + e_j, b = e_k + s e_l (s = +/-1, disjoint indices) with a*b = 0 though
a, b are nonzero. `cd_core.sedenion_zero_divisors` enumerates the 168 signed pairs
of this family with a's second sign +1.

Mechanism: L_a = L_{e_i} + L_{e_j} is linear in a, so a one-ancilla linear
combination of unitaries applies (L_{e_i} + L_{e_j})/2 to |b> = (|e_k> +
s|e_l>)/sqrt2 and post-selects ancilla = 0. The post-selected data amplitude is
(1/2sqrt2)(e_i + e_j)(e_k + s e_l), so P(ancilla = 0) = |a b|^2 / 8, which is 0
for a zero divisor by perfect destructive interference. Four data qubits, one
ancilla.

Predicted ideal: zero-divisor pair (e1+e10)(e4-e15) gives P(anc=0) = 0; the
sign-flipped control (e1+e10)(e4+e15) gives P(anc=0) = 1. `designs.py` checks all
168 dark and 168 bright circuits against |a b|^2 / 8 from cd_multiply.

Observable and falsifier: the suppression ratio P_zd / P_control on the same
physical qubits; ideal 0. A ratio not significantly below 1 means the
interference did not form, so the compiled product is wrong or gate error
erased it.

Measured (results/hw_estimate/ibm_fez_record.json): the all-to-all synthesis is
141 CZ at optimization_level 3. The ibm_fez ISA circuit is depth 821 with 224 CZ
on physical qubits 25, 37, 44, 45, 46; the bright control, compiled from the same
initial layout, is 222 CZ. The noise model gives P_zd = 0.2725 and P_control =
0.7144, ratio 0.381. The suppression is present and shallow. Readout mitigation
such as TREX corrects measurement bias in expectation values and leaves the gate
and decoherence error of 224 CZ in place, so the CZ count is the lever. The
compile that exploits the structure -- one joint sign diagonal for the
ancilla-selected pair, CX for the XOR index, a Hadamard-and-CNOT sparse state
prep replacing the Householder prep -- is the route below 100 CZ.

## Shared engine: the Cayley-Dickson ladder

`cd_core.cd_sign` and the L_{e_m} builders are the synthesis recursion under both
designs, emitting L_{e_m} at any dimension 2^k. Doubling sends an upper-half unit
to an X on the new top qubit together with conjugation, a diagonal sign on every
basis state except e_0. This is a compiler recursion: "dimension 2^k maps to k
qubits" is a vector-space identity, and Cayley-Dickson multiplication is not a
tensor product, so the ladder is not a physical tensor-factor correspondence.
Quantum operator composition stays associative; the circuits detect where the
encoding map fails L_{ab} = L_a L_b.

## Prior art

The octonions are a twisted group algebra of F_2^3: e_p e_q = F(p,q) e_{p+q}
for a 2-cochain F whose coboundary is the associator, a 3-cocycle, and the
higher Cayley-Dickson algebras arise by the same cochain twist (Albuquerque and
Majid, "Quasialgebra structure of the octonions", J. Algebra 220 (1999),
arXiv:math/9802116). The
Fano Z-string of design A is a circuit reading of that associator. The
ancilla-controlled sum of unitaries in design B is the linear combination of
unitaries of Childs and Wiebe (arXiv:1202.5822). The contribution here is the
convention-pinned algebra-to-circuit compile with exact operator checks and
falsifiable observables.

## Reference: Fano plane and the Steane code

The weight-3 codewords of the [7,4,3] Hamming code are the 7 Fano lines that also
index the octonion imaginary units, and the Steane [[7,1,3]] code uses that
incidence while dropping the octonion orientation signs. This connection is real
and standard, not novel; it is a labeled reference point, not a proposed
experiment.

## Appendix (speculative): WarpTriad p-adic ansatz

spectral_core WarpTriad weights a three-wave resonance k + p + q by
padic_triad_weight, a scalar-amplitude weight that discards Fourier phase and
polarization. Mapping a triad to a 3-local ZZZ term with that weight as the
rotation angle gives a QAOA-style ansatz, but with no problem to solve and no
verifiable answer it has no falsifier and stays out of the runnable set. A
Hamiltonian or objective with exact small-instance answers, uniform and permuted
weight controls, and a classical exact-diagonalization comparison of p-adic
versus uniform weights are the prerequisites before any circuit.

## Running on hardware

Nothing here has touched the QPU; `hw_estimate.py` reads backend metadata and
runs a local noise model on the archived ISA circuits
(results/hw_estimate/ibm_fez_isa.qpy), the objects a submission would run. The
10-minute monthly budget is quantum execution time; Design A instances are
microseconds each. 156/5 bounds the count of disjoint Design B instances by
qubits alone; a packed transpile with its routing and crosstalk is the
measurement of how many fit per shot. Re-query usage() before any submission.
