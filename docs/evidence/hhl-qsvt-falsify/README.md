# Falsification of a proposed QSVT pipeline for 32 x 32 systems

The measurements below were retained on 2026-11-05. Interpretation corrected 2026-11-11: the measured Pauli
expansion is one encoding, and a singular matrix can admit a kernel filter or a thresholded pseudoinverse.
The [exact successor checks](../a5-quantum-contracts/README.md) expose both boundaries. The original `probe.py`,
`probe.json`, `probe.log` and source receipts keep their bytes.

Measurements: `probe.py` with `--seed` and `--seed-transpiler` from indices 0 and 1 of the ANU draw
`docs/evidence/anu_qrng/draw-2026-11-05T192646Z.json` (the `seed_source` of `probe.json`), output `probe.json` /
`probe.log`. Matrices are
left-multiplication matrices L_a of the 32-dimensional Cayley-Dickson algebra A_5 from `cd_core.left_mult_matrix`,
plus one random dense symmetric positive-definite matrix as in the proposal's demonstration. Citations checked
through the arXiv API; the returned identifiers, titles and authors are retained in `arxiv-receipts.json`.
Ranks of the integer cases are exact (`rank_exact`, python-flint `fmpz_mat`) and agree with the SVD ranks.

| Claim | Verdict | Evidence |
|---|---|---|
| 1. HHL needs sparse, well-conditioned A for poly(log N, kappa) time | holds as stated, but incomplete | HHL abstract (0811.3171): sparse A, output is x'Mx, not x. Missing preconditions: efficient preparation of b and a readout that needs only an expectation value |
| 1. Precondition classically, then solve | no demonstrated advantage in the audited workflow | This workflow computes an approximate inverse classically before the quantum step. That work must be charged against a direct classical solve. The observation does not establish the cost of every possible structured preconditioner |
| 2. Five qubits encode b in R^32 | holds | 2^5 = 32 |
| 2. State preparation depth O(log 32) = 5 | unsupported by the retained generic-state construction | The recorded StatePreparation transpilation has 26 CZ, CZ depth 26 and total depth 115; the generic uniformly-controlled construction of Mottonen et al. (quant-ph/0407010) has 2^(n+2) - 4n - 4 = 104 CNOT at n=5. Sparse witness inputs can be cheaper. Other depth/width tradeoffs need their own construction and cost |
| 3. Dense real 32 x 32 matrix has at most 64 Pauli terms | refuted | generic L_a: 497 nonzero Pauli terms; random SPD: 528 (every symmetric real Pauli string) |
| 3. LCU block encoding with one ancilla | depends on support and decomposition | The measured 497-term Pauli LCU needs 9 selector qubits and has alpha / norm between 7.8 and 8.8. The natural expansion L_a = sum_i a_i L_ei has at most 32 signed-permutation terms, at most 5 selector qubits, and alpha = sum_i abs(a_i). Two-support inputs need one selector qubit. Selector counts exclude data and implementation workspace; the Pauli figures are not lower bounds |
| 4. QSVT inversion costs O(kappa polylog(kappa/epsilon)) | holds (known) | GSLW 1806.01838; strictly O(kappa log(1/epsilon)) is Costa et al. 2111.08152 |
| 4. Applies to the A_5 matrices of the program | ordinary inversion fails; filtering remains possible | Zero divisors make ordinary inversion undefined. This does not exclude QSVT kernel filtering or a pseudoinverse on the nonzero singular subspace. For e25 +/- e8 and e1 +/- e10, exact Gram spectra are supported on 0, 2, 4, so the nonzero singular gap is sqrt(2), restricted condition number sqrt(2), and P_ker = (B-2I)(B-4I)/8 for B = L_a^T L_a. The successor certifies this polynomial exactly. It does not provide the modular fiber ranks |
| 5. Amplitude amplification reaches O(1) success with O(kappa) rounds | normalization and input overlap must be included | The measured Pauli representation has alpha / norm about 8. For the natural real-coefficient LCU, 1 <= alpha / norm <= sqrt(s), where s is coefficient support. On the two-term witnesses above alpha = norm = 2. Neither bound supplies an end-to-end circuit cost or a uniform success probability for every input |
| 6. QAE reconstructs x up to a global phase | incomplete readout specification | Estimating computational-basis probabilities alone loses relative signs and phases. Interference with a reference can recover them. An explicit N-component classical output has at least linear output size, so a claim of polylogarithmic total cost must specify a smaller output task. A universal N / epsilon bound needs its own precision, access and success model |
| 7. Hybrid workflow | no demonstrated advantage in this workflow | The classical steps already include an approximate inverse; the record supplies no complete comparison showing a gain after that cost |
| 8. IBM Falcon or Rigetti Aspen, five qubits | device claim and resource estimate need a specific implementation | The retained account snapshot named Heron r2. Five is the data-register size only. The original 10^5 to 10^6 two-qubit-gate estimate used the 497-term Pauli representation and was not a compiled resource bound. Natural SELECT/PREP, the chosen transformation and target calibration must be costed before a hardware claim |
| HB-QSVT is novel | unsupported for its listed components | Preconditioned QLSA, block encoding without sparsity, and QSVT inversion are covered by Clader-Jacobs-Sprouse 1301.2340, Childs-Kothari-Somma 1511.02306 and GSLW 1806.01838. Dequantization results such as Chia et al. 1910.06151 apply under their rank, norm, sampling-access and output assumptions; they do not remove every possible advantage |

## Relevance to the A_5 fiber program

The fiber computations are exact ranks and Groebner bases over F_p (p = 32009, 32029) of matrices with 10^5 to 10^6
rows. A real-amplitude linear-system solver alone gives neither exact modular arithmetic nor the required ranks,
normal forms and ideal-membership certificates. Lifting residues to integers can change rank: the matrix
[[1,2],[(p+1)/2,1]] has determinant -p, rank two over Q and rank one over F_p for odd p. The successor receipt checks
both retained primes. A valid reduction would have to bridge this distinction and account for access, preparation,
precision, readout and the full classical baseline. The audited proposal supplies no such reduction or benchmark.

## What survives

The proposal has no demonstrated end-to-end speedup for the fiber program. The data register has five qubits;
preparation, block encoding and readout remain part of the cost. Exact signed-permutation LCUs and bounded spectral
filters are mathematically valid candidates for operator experiments. No compiled depth or calibrated feasibility
claim follows from this record, and no argument here establishes that a single basis permutation is the only
feasible hardware instance. The existing classical algebra and exact filters provide inexpensive reference answers.
