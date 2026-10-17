> Full piece: [https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/02-qubo-problem-formulation](https://cloud.quandela.com/webide/guide/quantum-toolbox-guide/cvarvqe/02-qubo-problem-formulation)
> Retrieved 2026-10-17T17:27Z by scripts/capture_qd_docs.py --guide from the module /src/docs/guide/quantum-toolbox-guide/cvarvqe/02-qubo-problem-formulation.en.md of https://cloud.quandela.com/webide/assets/index-DrG4GsjV.js (sha256 2f86182fa9ea5999d49645c2553e6b645e7d390249838c9261b2132f51051c7e).

# QUBO problem formulation

**Quadratic unconstrained binary optimization** (QUBO) problems are ubiquitous in finance (portfolio optimization, feature selection in credit scoring) logistics (scheduling), drug design (moleculard docking).

They are represented by a **QUBO matrix**, which is then used to compute the loss function : y = x<sup>T</sup>Qx.

Then using a variational approach we will minimize (or maximize) this function.

To be more specific, here are the steps to solve a QUBO problem :

1. **Formulation as a Quadratic Objective Function:**
   Generally an optimization problem may not have binary variables, as well it may have many constraints. Therefore one needs to cast it to a QUBO form i.e. with binary variables and all the constraints moved to the loss function. [Here is](https://arxiv.org/ftp/arxiv/papers/1811/1811.11538.pdf) a nice tutorial about it. Eventually the optimization problem should look like :

![image-20240306-103832.png](https://cloud.quandela.com/webide/docs-assets/422117411.png)

2. **Mapping to Ising hamiltonian :**
   One can map the above problem to the the problem of finding the ground state of a hamiltonian with a variable transformation : z<sub>i</sub> = 1 - 2*x<sub>i</sub>. Using this form we can apply a VQE algorithm to solve it.

3. **Implementation on Quantum Hardware:**
   The mapped QUBO problem is implemented on quantum hardware by encoding the binary variables as qubits and representing the hamiltonian as a set of quantum gates.
   QUBO problems were initally investigated by quantum annealing or adiabatic quantum computation platforms since there are particularly good at it and not universal. More recently, universal quantum computers also proposed algorithms to solve them such as CVaR-VQE presented here. To find the optimal value, we use a usual variational method to iteratively evolve the expectation value of the hamiltonian towards its ground state, which corresponds to the optimal solution of the QUBO problem. The final qubit state provides the binary values that minimize the objective function.
