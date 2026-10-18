> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/vqe/02-algorithm-explanation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/vqe/02-algorithm-explanation)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/vqe/02-algorithm-explanation.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# Algorithm explanation

In VQE, the aim is to find the lowest energy state of a qubit Hamiltonian, `H`.

This is achieved by using a variational method, where a quantum circuit with a parameterized wavefunction (called an ansatz) approximates the ground state of `H`. The algorithm proceeds as follows:

1. **Choose a Quantum Ansatz**

   Select a parameterized quantum circuit, `U(θ)`, to prepare the state `|ψ(θ)⟩ = U(θ)|0⟩`. The choice of ansatz can be tailored to the specific problem or selected from generic forms optimized for hardware.

2. **Express the Hamiltonian as a Sum of Pauli Terms**

   Decompose `H` into a sum of tensor products of Pauli matrices: , where P<sub>i</sub> ∈ {I, X, Y, Z}<sup>⊗n</sup> and c<sub>i</sub> are coefficients.

3. **Expectation Value Measurement**

   For each Pauli term P<sub>i</sub>, measure its expectation value in the state `|ψ(θ)⟩`:

   > ⟨P<sub>i</sub>⟩ = ⟨ψ(θ)|P<sub>i</sub>|ψ(θ)⟩

   Quantum circuits are used to measure these values, employing change of basis operations when necessary.

4. **Compute the Energy**

   Calculate the expected energy for the current set of parameters, `θ`:

   > E(θ) = Σ c<sub>i</sub> ⟨P<sub>i</sub>⟩

5. **Optimization**

   Utilize a classical optimizer to find the optimal parameters, `θ*`, that minimize `E(θ)`:

   > θ* = argmin θ E(θ)

   Common optimizers include Nelder-Mead, COBYLA, Spsa, etc…

6. **Iterate**

   Repeat steps 3-5 until convergence (i.e., changes in `E(θ)` are below a specified threshold or a maximum number of iterations is reached).

7. **Result**

   The ground state energy approximation is given by `E(θ*)`. The corresponding state, `|ψ(θ*)⟩`, approximates the ground state of `H`.
