# Falsification of the hybrid block-encoded QSVT pipeline for 32 x 32 systems (2026-11-05)

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
| 1. Precondition classically, then solve | no advantage at N = 32 | an effective preconditioner for these dense 32 x 32 instances costs about what solving does: dense LU of a 32 x 32 matrix is ~10^4 flops, so a classical preconditioning step already does the work the quantum solver is meant to replace |
| 2. Five qubits encode b in R^32 | holds | 2^5 = 32 |
| 2. State preparation depth O(log 32) = 5 | refuted | transpiled exact StatePreparation: 26 CZ, CZ depth 26, total depth 115; Mottonen et al. (quant-ph/0407010) give 2^(n+2) - 4n - 4 = 104 CNOT for the generic uniformly-controlled construction; log depth needs O(N) ancillas |
| 3. Dense real 32 x 32 matrix has at most 64 Pauli terms | refuted | generic L_a: 497 nonzero Pauli terms; random SPD: 528 (every symmetric real Pauli string) |
| 3. LCU block encoding with one ancilla | refuted | LCU over 497 terms needs ceil(log2 497) = 9 ancillas; subnormalization alpha = sum of coefficient magnitudes is 7.8 to 8.8 times the spectral norm, so the effective condition number grows by that factor and the post-selection probability falls by its square |
| 4. QSVT inversion costs O(kappa polylog(kappa/epsilon)) | holds (known) | GSLW 1806.01838; strictly O(kappa log(1/epsilon)) is Costa et al. 2111.08152 |
| 4. Applies to the A_5 matrices of the program | refuted | every zero divisor gives a singular L_a: rank 20 for the three random two-term zero divisors and 24 for the sedenion zero divisors, of 32, kappa infinite (rows two-term-25-8, two-term-27-14, two-term-2-23, sedenion-zd-1+-10). The program studies exactly the zero-divisor locus, where inversion is undefined; a pseudoinverse needs a singular-value threshold that the problem does not supply |
| 5. Amplitude amplification reaches O(1) success with O(kappa) rounds | holds only in kappa_eff = alpha kappa / norm | with alpha / norm ~ 8 the round count is ~8 kappa |
| 6. QAE reconstructs x up to a global phase | refuted as a readout of x | amplitude estimation of |x_i|^2 returns magnitudes; interference-based estimation against a reference state recovers signs, but reading out N components at precision epsilon costs O(N / epsilon) queries either way, erasing the log N advantage at every N |
| 7. Hybrid workflow | no advantage at N = 32 | the classical steps already include an approximate inverse |
| 8. IBM Falcon or Rigetti Aspen, five qubits | device claim stale | the account reaches Heron r2 only (ibm_fez, ibm_kingston, ibm_marrakesh; AGENTS.md). Gate budget: kappa_eff ~ 8 x 12 = 96 (largest generic kappa 11.7), epsilon = 1e-3 gives ~10^3 block-encoding calls of a 497-term LCU, order 10^5 to 10^6 two-qubit gates (no fidelity estimate is made here; it would need a named calibration snapshot) |
| HB-QSVT is novel | refuted for its listed components | preconditioned QLSA, block encoding without sparsity, and QSVT inversion are Clader-Jacobs-Sprouse 1301.2340, Childs-Kothari-Somma 1511.02306 and GSLW 1806.01838; for low-rank or sampled inputs the dequantization framework of Chia et al. 1910.06151 removes the exponential advantage |

## Relevance to the A_5 fiber program

The fiber computations are exact ranks and Groebner bases over F_p (p = 32009, 32029) of matrices with 10^5 to 10^6
rows. A quantum linear-system solver returns a normalized real amplitude vector to finite precision; it gives neither an
exact rank nor arithmetic in F_p. No item of the fiber program maps onto HHL or QSVT, so the pipeline earns no QPU
case. Confidence: high; a quantum algorithm for exact rank over F_p with a proven speedup at these sizes would
overturn it, and none is registered in the workspace sources.

## What survives

Claims 1 (as a precondition list), 2 (qubit count), 4 (complexity) and 5 (in kappa_eff) are textbook facts. As a
demonstration circuit, a 5-qubit inversion of a kappa = 1 matrix (for example L_a with a a single basis element, a signed
permutation matrix) is the only instance whose depth fits Heron r2, and its answer is known in closed
form, so it measures device noise rather than algebra. It is not a QPU case: at 5 qubits it routes to Kaggle simulation, and no fiber-program question depends on it.
