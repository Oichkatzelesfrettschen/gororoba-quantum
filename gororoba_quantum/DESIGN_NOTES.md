# Cayley-Dickson quantum circuits

Quantum circuits whose structure comes from the open_gororoba Cayley-Dickson
algebra kernel. Left multiplication L_{e_m} by a basis unit is a signed
permutation of the 2^k basis states (e_p * e_q = cd_sign(dim,p,q) e_{p XOR q}),
so it is unitary on k qubits. The designs turn two algebraic defects that the
kernel measures classically -- the octonion associator and sedenion zero
divisors -- into hardware observables on the 156-qubit Heron backends.

Run `$PYTHON cd_core.py` for the classical structure, `$PYTHON verify.py` for
the ground-truth checks, `$PYTHON designs.py` for ideal statevector outcomes,
and `$PYTHON hw_estimate.py` for routed cost and noisy prediction on ibm_fez.

## Verification against the kernel

The sign table is ported from cd_kernel::cayley_dickson::signs::cd_basis_mul_sign_iter
into `cd_core.cd_sign`. Three checks pin the port to the kernel's convention
rather than to itself:

- The 168 sedenion zero-divisor pairs from `sedenion_zero_divisors()` equal, set
  for set, the u_sign=+1 subset of the kernel's own
  data/csv/reggiani_standard_zero_divisor_pairs.csv (168 = 168, exact). Which
  pairs annihilate depends on the signs, so this discriminates conventions.
- Octonion norm multiplicativity |x y| = |x| |y| holds on random vectors; the
  sedenion norm fails it on some vectors, as a zero-divisor algebra must.
- The 42/168 associative/anti-associative split of ordered distinct octonion
  triples is reported but is necessary only: associative triples are the F_2
  subspaces {i, j, i^j} for any XOR-indexed sign table.

## Design A: octonion associator as a Fano Z-string

Source: cd_associator, A(e_i,e_j,e_k) = (e_i e_j) e_k - e_i (e_j e_k). The
octonions are alternative, so L_{e_m}^2 = -I.

Finding: W = L_{e_{i^j}}^{-1} L_{e_i} L_{e_j} is diagonal with eigenvalue +/-1,
the associator sign of (e_i, e_j, e_k). Across the 21 unordered pairs these are
exactly the 7 non-identity 3-qubit Z-strings, one per Fano line, by point-line
duality in PG(2,2): W is +1 precisely on the associating subspace {0, i, j, i^j}.
For (i,j)=(1,2) the net operator is Z on qubit 2.

Mechanism: the circuit appends L_{e_j}, L_{e_i}, L_{e_{i^j}} as three separate
gates with barriers, so the hardware composes them and performs the cancellation
down to the net Z-string; numpy never multiplies the operators. A line-completing
k0 (associative) and a one-bit-away k1 (anti) get opposite signs, so W maps
(|e_{k0}> + |e_{k1}>)/sqrt2 to the orthogonal minus state, and a Hadamard on the
single differing qubit makes one measured bit deterministic. Three qubits,
ancilla-free.

Predicted ideal: for (1,2), k0=3, k1=7, readout bit = 1 with probability 1.
Confirmed by statevector.

Observable and falsifier: the readout-bit probability; ideal 1.0. A measured
value at or below 0.5 + 3 sigma means the phase did not survive, so either the
associator sign is miscompiled or readout is worse than reported.

Measured: routed to ibm_fez (heavy-hex) the circuit is depth 58 with 16 CZ; the
noise model from backend calibration gives P1 = 0.946. The witness clears its
falsifier on realistic noise.

## Design B: sedenion zero-divisor interference witness

Source: find_zero_divisors(16, 1e-10). A sedenion zero divisor is a pair
a = e_i + e_j, b = e_k + s e_l (s = +/-1, disjoint indices) with a*b = 0 though
a, b are nonzero. `cd_core.sedenion_zero_divisors` enumerates the 168 signed pairs
of this family.

Mechanism: L_a = L_{e_i} + L_{e_j} is linear in a, so a one-ancilla linear
combination of unitaries applies (L_{e_i} + L_{e_j})/2 to |b> = (|e_k> +
s|e_l>)/sqrt2 and post-selects ancilla = 0. The post-selected data amplitude is
(1/2sqrt2)(e_i + e_j)(e_k + s e_l), which is 0 for a zero divisor, so
P(ancilla = 0) = 0 by perfect destructive interference. Four data qubits, one
ancilla.

Predicted ideal: zero-divisor pair (e1+e10)(e4-e15) gives P(anc=0) = 0; the
sign-flipped control (e1+e10)(e4+e15) gives P(anc=0) = 1. Confirmed by
statevector.

Observable and falsifier: the suppression ratio P_zd / P_control on the same
qubits; ideal 0. A ratio not significantly below 1 means the interference did
not form, so the compiled product is wrong or the circuit is past the coherence
budget.

Measured: all-to-all synthesis is 141 CZ at optimization_level 3; the
DiagonalGate-structured route is worse at 294 CZ. Routed to ibm_fez the circuit
is depth 820 with 224 CZ, and the noise model gives P_zd = 0.319, P_control =
0.702, ratio 0.45. The suppression is present but shallow: at 224 CZ the circuit
sits near the coherence edge, so the witness needs the sub-100-CZ compile below
or EstimatorV2 TREX mitigation to read cleanly. A hand phase-polynomial compile
-- CX for the XOR index, CZ and CCZ for the sign diagonal, a two-gate sparse
state prep replacing the Householder prep -- is the route under 100 CZ and is not
yet implemented.

## Shared engine: the Cayley-Dickson ladder

`cd_core.cd_sign` and the L_{e_m} builders are the synthesis recursion under both
designs, emitting L_{e_m} at any dimension 2^k. Doubling sends an upper-half unit
to an X on the new top qubit together with conjugation, a diagonal sign on every
basis state except e_0. This is a compiler recursion: "dimension 2^k maps to k
qubits" is a vector-space identity, and Cayley-Dickson multiplication is not a
tensor product, so the ladder is not a physical tensor-factor correspondence.

## Reference: Fano plane and the Steane code

The weight-3 codewords of the [7,4,3] Hamming code are the 7 Fano lines that also
index the octonion imaginary units, and the Steane [[7,1,3]] code uses that
incidence while dropping the octonion orientation signs. This connection is real
and standard, not novel; it is a labeled reference point, not a proposed
experiment.

## Appendix (speculative): WarpTriad p-adic ansatz

spectral_core WarpTriad weights a three-wave resonance k + p + q by
padic_triad_weight. Mapping a triad to a 3-local ZZZ term with that weight as the
rotation angle gives a QAOA-style ansatz, but with no problem to solve and no
verifiable answer it has no falsifier and stays out of the runnable set. A
classical exact-diagonalization comparison of p-adic versus uniform triad weights
is the prerequisite before any circuit.

## Running on hardware

Nothing here has touched the QPU; hw_estimate.py uses only backend metadata and a
local noise model. The 10-minute monthly budget is quantum execution time. Design
A instances are microseconds each and essentially free; Design B at 224 routed CZ
is the coherence-limited one. Both pack as disjoint instances across the 156
qubits -- a packed transpile is the way to confirm how many Design B instances
fit per shot, which is not yet measured. Re-query usage() before any submission.
