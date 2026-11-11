# Finite-field quantum linear algebra for the fiber program: proposal and its falsification

Status: this proposed algorithm is refuted; scope corrected 2026-11-11. The proposal below arrived as an untracked
draft. Its rejection does not establish a lower bound for all quantum algorithms over finite fields. The draft text
follows unchanged under "Proposal as received". Companion record:
[the HHL/QSVT falsification](../../evidence/hhl-qsvt-falsify/README.md) (the real-amplitude pipeline; the proposal below
cites its scratch location, `docs/local/hhl-falsify/verdict.md`).

| Claim | Verdict | Check |
|---|---|---|
| The program computes exact ranks of 32 x 32 left-multiplication matrices over F_p | wrong premise | the 32 x 32 ranks cost microseconds classically; the expensive objects are truncated-rank matrices of the fiber cones (dim of k[t]/(J + m^N) = 93,024 with about 2.3 x 10^4 columns per character block and 98,280 products at N = 16 for W8 -> N-, [w8-n16-azure](../../evidence/a5-exceptional-fibers/w8-n16-azure/README.md)) and Singular standard bases, which dominate the run times |
| Rank detection: superpose random v, test <v, A v> = 0, amplitude ~ 1/p^r flags kernel vectors | refuted | For every pure Cayley-Dickson element over an odd field, L_a is skew-symmetric, so v^T L_a v = 0 for every v. The invertible L_e1 already falsifies the predicate: it marks the entire space although its kernel contains only zero. For a corrected predicate A v = 0, the fraction in F_p^N is p^(-rank), and uniform amplitude amplification has the search scale p^(rank/2). At N = 32, rank 24 and p = 32009 this is p^12, about 1.2 x 10^54. This is a cost of the proposed search strategy, not a lower bound for quantum rank algorithms. Searching for a nonzero vector uses (p^(N-rank)-1)/(p^N-1) instead and requires positive nullity |
| Phase estimation on U = exp(2 pi i O_A / p) isolates eigenvalue 0 and yields solutions of A x = b | refuted | x -> A x is not injective when A is singular (the case of interest), so no in-place unitary O_A exists; the reversible out-of-place map (x, y) -> (x, y + A x) is a permutation whose eigenphases are additive characters, which encode Fourier data of A rather than ker A, and the draft gives no analysis showing they solve A x = b. Classical exact solving over F_p is polynomial: Gaussian elimination O(N^3), Wiedemann O(N nnz) for sparse A |
| Register cost fits Heron r2 (156 qubits) | refuted for the specified representation | N simultaneous 15-qubit field registers need 480 data qubits at N = 32 before ancillas. This rules out this explicit full-vector representation on the recorded 156-qubit target; it is not a universal qubit lower bound for every access model or space-time tradeoff |
| Citation "Van Apeldoorn, Gilyen, Brandao et al., Quantum algorithm for the rank problem (2021)" | attribution not found | the matching title is Belovs, "Span-program-based quantum algorithm for the rank problem", arXiv 1103.0842 (2011; record in [arxiv-receipts.json](../../evidence/hhl-qsvt-falsify/arxiv-receipts.json)), a query-complexity span program; no time-efficient F_p solver |
| Citation "Childs, Kothari, Somma, Quantum algorithm for linear systems of equations (2015)" | wrong title | arXiv 1511.02306, "Quantum algorithm for systems of linear equations with exponentially improved dependence on precision", real-amplitude output, not F_p |
| Citation "Modular arithmetic on near-term quantum computers (2023)" | unidentifiable | no author or identifier given |
| "For p not a prime power, embed into GF(p^k)" | ill-posed | p = 32009 and 32029 are primes; F_p is already a field |
| Novel synthesis | unsupported | the components do not compose into a correct algorithm (rows above), so there is no synthesis to be novel |

The exact [quantum-contract replay](../../evidence/a5-quantum-contracts/README.md) now checks the skew predicate,
invertible counterexample, natural signed-permutation LCU and selected kernel projectors. These are executable
falsification checks, not an implementation of the rejected solver. The real-amplitude objections in the received
draft also need correction: a generic A5 natural LCU uses at most 32 basis terms, and singularity permits kernel
filtering and thresholded pseudoinverses when the relevant spectral promise is supplied.

The surviving conclusion is workload-specific: this proposal supplies no correct speedup for the exact modular
fiber computations. A replacement must specify the input/access model, promised structure, output, error criterion,
and complete cost including preparation and readout, then compare with the strongest applicable classical method.
Matrix-product verification already supplies a finite-field-compatible polynomial quantum speedup in its stated
access model ([Buhrman and Spalek, quant-ph/0409035](https://arxiv.org/abs/quant-ph/0409035)); it does not compute
the fiber ranks. The absence of a suitable current replacement is not an impossibility theorem.

## Proposal as received


### Background
The fiber program computes exact ranks of 32‑dimensional Cayley‑Dickson left‑multiplication matrices over finite fields F_p (p = 32009, 32029). The existing HHL/QSVT pipeline fails because the matrices are dense, singular on the zero‑divisor locus, and require nine ancilla qubits for block‑encoding, while the output produces only real‑valued amplitudes that cannot represent exact finite‑field solutions. The falsification report (docs/local/hhl-falsify/verdict.md) documents these shortcomings.

### Goal
The note proposes a quantum algorithm that can detect the rank of a matrix over F_p or solve a linear system A x = b exactly, without requiring sparse matrices or real‑valued amplitude reconstruction.

### Proposed Approach
1. **Finite‑field state encoding** – The algorithm encodes each field element a ∈ F_p as a binary string of ⌈log₂ p⌉ qubits using a basis‑state map \|a\> . A vector x ∈ F_p^N is encoded as the tensor product of N such registers.
2. **Quantum rank‑detection subroutine** – The algorithm prepares a uniform super‑position of random vectors v ∈ F_p^N, applies the linear map A to obtain A v, and measures the inner product ⟨v, A v⟩ using a reversible field‑multiplication circuit. Amplitude ≈ 1/p^r indicates that v lies in the kernel of dimension r. Quantum counting estimates the number of kernel vectors with O(√p^r) queries, yielding the rank N − r with quadratic speedup over classical exhaustive search.
3. **Finite‑field linear‑system solver** – Given b ∈ F_p^N, the algorithm constructs an oracle O_A that computes A·x in‑place. Using quantum phase estimation on the unitary U = exp(2πi O_A / p) yields the eigenvalue spectrum modulo p. The algorithm isolates eigenvalue 0 and applies a controlled‑rotation to extract a uniform super‑position over solutions of A x = b. A final measurement collapses to an exact solution because the amplitudes correspond to computational basis states, not continuous amplitudes.
4. **Hybrid verification** – The algorithm returns a candidate solution \hat{x} as a computational basis state. A classical verification step computes A\hat{x} − b over F_p to confirm correctness, discarding any false positive that arises from phase‑estimation error.

### Literature Context
* Van Apeldoorn, Gilyén, Brandão et al. “Quantum algorithm for the rank problem” (2021) demonstrates quantum counting of kernel dimension for integer matrices. The note adapts their technique to finite fields by replacing integer arithmetic with modular arithmetic circuits.
* Childs, Kothari, Somma “Quantum algorithm for linear systems of equations” (2015) underlies the phase‑estimation subroutine. The note replaces their real‑valued Hamiltonian simulation with modular exponentiation.
* Recent work on quantum arithmetic over GF(p) (e.g., “Modular arithmetic on near‑term quantum computers” – 2023) supplies reversible circuits for addition, multiplication, and inversion needed by the proposed subroutines.
* No known algorithm combines these components into a finite‑field QLSA; the note therefore offers a novel synthesis of existing primitives.

### Open Questions
* **Circuit depth** – Modular multiplication over p ≈ 3×10⁴ requires O(log p) ≈ 15 bits; known reversible multipliers use O(log p) ancilla qubits and depth O(log² p). The total depth for the rank‑detection subroutine with quantum counting scales as O(√p · log² p). Feasibility on Heron r2 (156 qubits) requires careful ancilla reuse.
* **Error model** – Phase‑estimation error must be bounded to avoid spurious kernel vectors. The note proposes a precision ε = 1/(2p) to guarantee that only exact zeros are flagged.
* **Space‑time trade‑off** – Reducing ancilla count by using in‑place modular arithmetic may increase depth; the optimal balance depends on device‑specific gate times.
* **Finite‑field extension** – For p not a prime power, embedding into GF(p^k) with k = 1 is trivial; for larger fields, circuits for field multiplication become more complex.

### Next Steps
1. **Prototype modular arithmetic library** – Implement reversible addition, multiplication, and inversion for p = 32009 in Qiskit using the `qiskit.circuit.library` `ModularAddition` pattern.
2. **Implement rank‑detection oracle** – Translate the van Apeldoorn counting circuit to the finite‑field setting, verify correctness on a classical simulator.
3. **Benchmark depth and qubit count** – Run the circuit on the Aer statevector simulator, record gate count, and compare to the 156‑qubit Heron r2 budget.
4. **Integrate with existing pipeline** – Add a new module `finite_field_qlsa.py` under `gororoba_quantum/` that exposes a CLI `--rank-detect` and `--solve` commands.
5. **Document the design** – Write this note to `gororoba-quantum/docs/notes/topics/finite-field-qlsa-alternatives.md` and link it from the `RESEARCH_ROADMAP.md` under a new entry “Finite‑field quantum linear algebra”.

The note establishes a concrete research direction that respects the falsified HHL pipeline, leverages known quantum primitives, and aligns with the fiber program’s need for exact finite‑field results.
