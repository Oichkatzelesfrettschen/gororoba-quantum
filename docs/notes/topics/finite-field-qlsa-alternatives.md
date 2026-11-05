# Finite-field quantum linear algebra for the fiber program: proposal and its falsification

Status: refuted (2026-11-05). The proposal below arrived as an untracked draft; this header records the checks that
decide it. The draft text follows unchanged under "Proposal as received". Companion record:
[the HHL/QSVT falsification](../../evidence/hhl-qsvt-falsify/README.md) (the real-amplitude pipeline; the proposal below
cites its scratch location, `docs/local/hhl-falsify/verdict.md`).

| Claim | Verdict | Check |
|---|---|---|
| The program computes exact ranks of 32 x 32 left-multiplication matrices over F_p | wrong premise | the 32 x 32 ranks cost microseconds classically; the expensive objects are truncated-rank matrices of the fiber cones (dim of k[t]/(J + m^N) = 93,024 with about 2.3 x 10^4 columns per character block and 98,280 products at N = 16 for W8 -> N-, [w8-n16-azure](../../evidence/a5-exceptional-fibers/w8-n16-azure/README.md)) and Singular standard bases, which dominate the run times |
| Rank detection: superpose random v, test <v, A v> = 0, amplitude ~ 1/p^r flags kernel vectors | refuted | <v, A v> = 0 marks isotropic vectors of the bilinear form v^T A v, a quadric of p^(N-1) points for generic A, not ker A. The kernel fraction of F_p^N is p^(r - N), so amplitude-amplification counting needs order p^((N - r)/2) queries, exponential in the rank (N = 32, rank 24, p = 32009: about 10^18), against O(N^3) field operations for Gaussian elimination. The draft's O(sqrt(p^r)) has the exponent's sign wrong and is exponential either way |
| Phase estimation on U = exp(2 pi i O_A / p) isolates eigenvalue 0 and yields solutions of A x = b | refuted | x -> A x is not injective when A is singular (the case of interest), so no in-place unitary O_A exists; the reversible out-of-place map (x, y) -> (x, y + A x) is a permutation whose eigenphases are additive characters, which encode Fourier data of A rather than ker A, and the draft gives no analysis showing they solve A x = b. Classical exact solving over F_p is polynomial: Gaussian elimination O(N^3), Wiedemann O(N nnz) for sparse A |
| Register cost fits Heron r2 (156 qubits) | refuted | N registers of 15 qubits: 480 data qubits at N = 32 before ancillas; 3 x 10^5 at the W8 truncation size; Heron r2 has 156 physical qubits without error correction |
| Citation "Van Apeldoorn, Gilyen, Brandao et al., Quantum algorithm for the rank problem (2021)" | fabricated attribution | the matching title is Belovs, "Span-program-based quantum algorithm for the rank problem", arXiv 1103.0842 (2011), a query-complexity span program; no time-efficient F_p solver |
| Citation "Childs, Kothari, Somma, Quantum algorithm for linear systems of equations (2015)" | wrong title | arXiv 1511.02306, "Quantum algorithm for systems of linear equations with exponentially improved dependence on precision", real-amplitude output, not F_p |
| Citation "Modular arithmetic on near-term quantum computers (2023)" | unidentifiable | no author or identifier given |
| "For p not a prime power, embed into GF(p^k)" | ill-posed | p = 32009 and 32029 are primes; F_p is already a field |
| Novel synthesis | unsupported | the components do not compose into a correct algorithm (rows above), so there is no synthesis to be novel |

Consequence: no QPU, Aer or Kaggle run follows from this proposal, and no `finite_field_qlsa.py` module or roadmap
entry is added. A future proposal reopens the question only with a polynomial-time quantum algorithm for exact rank
over F_p together with a proven speedup over O(N^omega) at N >= 10^4, which no source in the workspace provides.

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
