# Cayley-Dickson quantum circuits

Quantum circuits whose structure comes from the open_gororoba Cayley-Dickson
algebra kernel. Left multiplication L_{e_m} by a basis unit is a signed
permutation of the 2^k basis states (e_p * e_q = cd_sign(dim,p,q) e_{p XOR q}),
so it is unitary on k qubits. The designs turn two algebraic defects that the
kernel measures classically -- the octonion associator and sedenion zero
divisors -- into hardware observables on the 156-qubit Heron backends, and
extend each into a family: the associator into a Walsh spectrum along the
doubling ladder (design C), the zero divisor into a phase-resolved fringe
(design D).

Run `$PYTHON cd_core.py` for the classical structure, `$PYTHON verify.py` for
the ground-truth checks, `$PYTHON designs.py` for the circuit checks, and
`$PYTHON hw_estimate.py --out ../results/hw_estimate` for the routed cost and
noisy prediction on ibm_fez. `verify.py` and `designs.py` exit nonzero on the
first failed check. predict.py computes every prediction from cd_sign and
cd_multiply; no circuit builder imports it.

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

## Phase degree along the ladder

Two finite results, checked exhaustively by `verify.py` for dims 8 through 128
and stated as conjectures beyond:

- The sign function f_m(x) = [cd_sign(dim,m,x) = -1] of L_{e_m} has algebraic
  degree log2(dim) - 1 for every m != 0. Octonion left multiplications are
  therefore Clifford (Z and CZ signs plus X), and sedenion ones carry a
  degree-3 sign (CCZ) outside the Clifford group.
- The associator phase omega_ij(x) of W_ij = L_{e_i e_j}^dagger L_{e_i} L_{e_j}
  has degree max(1, bitlen(max(i,j)) - 2): it depends only on the doubling
  level where the pair first appears. The census of unordered pairs by degree
  is 21 of degree 1 at dim 8; then 84 of degree 2, 360 of degree 3, 1488 of
  degree 4, and 6048 of degree 5 are added at dims 16, 32, 64, and 128. A
  sedenion W is quadratic (Clifford) although each of its three sedenion
  factors carries a cubic sign, so the composition cancels the cubic terms; W
  leaves the Clifford group from dim 32 on.

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

Measured (results/hw_estimate/ibm_fez_record.json, calibration
2026-10-10T08:36:41-07:00): the (1,2) ISA circuit on ibm_fez is depth 55 with
16 CZ on physical qubits 131-133, and the same circuit under the backend noise
model gives P1 = 0.9685.

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

Compilation (select_lcu.py): the ancilla-selected pair is one operator,
SELECT|a,x> = cd_sign(16,m_a,x)|a, m_a ^ x> with m_0 = i and m_1 = j. It factors
into one sign diagonal (-1)^g(a,x) over all five qubits, g = f_i ^ a(f_i ^ f_j);
X on the bits of i; and CX from the ancilla onto the bits of i ^ j. The input
|b> is loaded by H on a pivot bit of k ^ l, the sign or phase on that bit, CX
fan-out over the rest of k ^ l, and the X load of k last, so the X layer
relabels branches without touching their relative phase. g has degree 4 for
every sedenion pair, so a per-monomial Z/CZ/CCZ/C3Z emission costs more than
DiagonalGate's uniformly controlled Rz synthesis. The builder receives (i, j)
and the input specification and never the expected outcome.

Checks: `designs.py` compares the SELECT operator against its signed-permutation
definition for all 105 pairs (32 x 32, phase included), the prepared state
against its target for all 120 index pairs at 9 phases, and all 168 dark and
168 bright circuits against |a b|^2 / 8 from cd_multiply. Mutating the SELECT
sign layer or loading k before the Hadamard fails these checks.

Predicted ideal: zero-divisor pair (e1+e10)(e4-e15) gives P(anc=0) = 0; the
sign-flipped control (e1+e10)(e4+e15) gives P(anc=0) = 1.

Observable and falsifier: the suppression ratio P_zd / P_control on the same
physical qubits; ideal 0. A ratio not significantly below 1 means the
interference did not form, so the compiled product is wrong or gate error
erased it.

Measured (same record): the structural circuit is 27 CZ all-to-all; the ibm_fez
ISA circuit is depth 130 with 46 CZ on physical qubits 119, 131-134, and the
bright control compiled from the same initial layout is also 46 CZ. The noise
model gives P_zd = 0.0806 and P_control = 0.9021, ratio 0.089. The dense
compile it replaces (Householder preparation plus two controlled dense
unitaries), transpiled onto the same initial layout under the same calibration
and seeds, is 249 CZ with P_zd = 0.314, P_control = 0.677, ratio 0.464, so the
comparison holds layout quality fixed. Readout
mitigation such as TREX corrects measurement bias in expectation values and
leaves gate error in place, so the CZ count is the lever it was.

## Design C: associator Walsh spectrum along the ladder

Mechanism: prepare |+>^n, apply L_{e_j}, L_{e_i}, and L_{e_i e_j}^dagger as
separate blocks between barriers, apply H^n, and measure all n qubits. The
adjoint block is built as the transpose X^{i^j} D_{i^j} with cd_sign(dim,i,j)
as a global phase, which holds at every dimension without the octonion identity
L_{e_m}^2 = -I. The net unitary is diag(omega_ij), so

P(y) = | 2^-n sum_x omega_ij(x) (-1)^(x.y) |^2.

Quantum composition stays associative; the circuit measures where the encoding
fails L_{e_i e_j} = L_{e_i} L_{e_j}. A degree-1 phase gives a single outcome
and a degree-2 phase a flat distribution on an affine subspace; the degree-3
exemplar at dim 32 gives a non-flat one.

Predicted ideal (qubit 0 least significant): dim 8 pair (1,4) gives P(2) = 1;
dim 16 pair (1,8) gives P = 1/4 on {0, 2, 4, 6}; dim 32 pair (1,16) gives
P(0) = 9/16 and 1/16 on each of {2, 4, ..., 14}.

Checks: `designs.py` compares the composed unitary against diag(omega) and the
statevector distribution against the Walsh prediction for all 21, 105, and 465
pairs at dims 8, 16, and 32. The operator check is the stronger one: replacing
the adjoint by L itself changes W only by a global sign at dim 8, which leaves
every probability unchanged and fails the operator check by 2.0.

Controls: a sign flip of L_{e_i} at one input (flip) and the omitted adjoint
block (omit), each compiled from the experiment's initial layout. Ideal TVD from
the true distribution: 0.438, 0.328, 0.191 (flip) and 1.0 (omit) at dims 8, 16,
32.

Observable and falsifier: the full measured distribution. The run passes when it
is closer in TVD to the true prediction than to each control prediction by more
than the shot-noise TVD; a single favored outcome is not evidence.

Measured (same record): ibm_fez ISA circuits are 18, 51, and 96 CZ at dims 8,
16, 32. Noisy TVD to the true prediction is 0.065, 0.114, 0.196 against 0.372,
0.257, 0.259 to the flip prediction. Resampling the noisy distributions at 4096
shots gives a shot-noise TVD of 0.006, 0.017, 0.026 (99th percentile 0.011,
0.029, 0.037). Dims 8 and 16 separate by 0.31 and 0.14; dim 32 separates by
0.063, under twice the 99th-percentile shot noise, a thin margin that more
shots or a lower-error qubit patch widens.

## Design D: phase-resolved annihilator fringe

Mechanism: Design B's circuit on |b_phi> = (|e_k> + e^{i phi}|e_l>)/sqrt2, using
the complex-linear extension of the real multiplication matrices. With
u = (L_{e_i} + L_{e_j}) e_k, the zero-divisor relation gives (L_{e_i} +
L_{e_j}) e_l = -s u, and |u|^2 = 2 because L_{e_i} e_k and L_{e_j} e_k are
orthogonal basis vectors, so

P(anc=0 | phi) = (1 - s cos phi) / 2.

phi = 0 and pi are the real inputs; intermediate phases are interferometric
probes. Every zero divisor's element a = e_i + t e_j annihilates a
4-dimensional space spanned by its corpus partners, and (L_{e_i} + t L_{e_j})/2
has Gram spectrum {0^4, (1/2)^8, 1^4} for all 84 such a, so P(anc=0) =
<b| B^dagger B |b> probes a positive operator with a 4-dimensional kernel.
`designs.py` checks the closed form for all 168 zero divisors at 9 phases, the
exemplar sweep circuits against it, and the kernel and spectrum for every a.
A dark-to-bright rotation cos(eps)|b_dark> + sin(eps)|b_bright> predicts
P(anc=0) = sin^2(eps); its preparation is not implemented.

Observable and falsifier: fit P0 = o + A cos phi + B sin phi over the 9 phases.
The ideal has offset 1/2, visibility 2 sqrt(A^2 + B^2) = 1, and phase
atan2(B, A) = 0 for s = -1; offset, visibility, and phase separate readout bias,
decoherence, and a miscompiled relative phase, which one suppression ratio
collapses. A cosine fringe shows interference; the support-mismatched bright
control and the operator checks tie it to the sedenion product.

Measured (same record): 46 CZ per point on the dark circuit's qubits; the fit
gives offset 0.491, visibility 0.826, and phase -0.0007 rad.

## Shared engine: the Cayley-Dickson ladder

`cd_core.cd_sign` and the L_{e_m} builders are the synthesis recursion under every
design, emitting L_{e_m} at any dimension 2^k. Doubling sends an upper-half unit
to an X on the new top qubit together with conjugation, a diagonal sign on every
basis state except e_0. This is a compiler recursion: "dimension 2^k maps to k
qubits" is a vector-space identity, and Cayley-Dickson multiplication is not a
tensor product, so the ladder is not a physical tensor-factor correspondence.
The sign tables are exponential in k, so the compiler targets small dimensions.

## Prior art

The octonions are a twisted group algebra of F_2^3: e_p e_q = F(p,q) e_{p+q}
for a 2-cochain F whose coboundary is the associator, a 3-cocycle, and the
higher Cayley-Dickson algebras arise by the same cochain twist (Albuquerque and
Majid, "Quasialgebra structure of the octonions", J. Algebra 220 (1999),
arXiv:math/9802116). The Fano Z-string of design A is a circuit reading of that
associator. The ancilla-controlled sum of unitaries in designs B and D is the
linear combination of unitaries of Childs and Wiebe (arXiv:1202.5822), and
DiagonalGate synthesizes the SELECT sign by Theorem 7 of Shende, Bullock, and
Markov (quant-ph/0406176). The contribution here is the convention-pinned
algebra-to-circuit compile with exact operator checks, the degree results along
the ladder, and falsifiable observables with controls; no literature search
establishes priority for the degree results.

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
(results/hw_estimate/ibm_fez_isa.qpy), the 21 objects a submission would run:
design A, design B dark and bright, the 9-point design D sweep, and design C at
three dimensions with its two controls. The 10-minute monthly budget is quantum
execution time. 156/5 bounds the count of disjoint 5-qubit instances by qubits
alone; a packed transpile with its routing and crosstalk is the measurement of
how many fit per shot. Re-query usage() before any submission.
