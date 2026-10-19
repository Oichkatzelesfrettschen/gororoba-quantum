> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/Circuit%20Synthesis.html](https://docs.iqm.tech/4.7/iqm-qaoa/Circuit%20Synthesis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 14cb7c957a53b2086261e8dd1d10b6836162233280fc804840ae2019e037479b.

# Circuit Synthesis

The purpose of the notebook is to illustrate the circuit-synthesis tools available in the IQM QAOA Library (as of May 2026; likely to be moved elsewhere in the future).

In this case, we are interesting in synthesizing phase-polynomial quantum circuits. We consider a **diagonal Hamiltonian** \$\$ H = \sum\_{k=1}^n \sum\_{i_1 \< \cdots \< i_k} c\_{i_1 \cdots i_k} \prod\_{m=1}^k Z\_{i_m} \$\$ and we time-evolve with respect to this Hamiltonian. That is, we want to implement the unitary: \$\$ U(\varphi) = \text{e}^{-\text{i} \frac{\varphi}{2} H} = \prod\_{k=1}^n \prod\_{i_1 \< \cdots \< i_k} R\_{Z_i \cdots Z\_{i_k}} !\left( \varphi , c\_{i_1 \cdots i_k}\right) \$\$

The following two modules are completely independent from the rest of the IQM QAOA Library and therefore can be separated in the future into its own repository.

```
from iqm.qaoa.transpiler.quantum_hardware import CrystalQPUFromBackend
from iqm.qaoa.transpiler.routing import ParityMapping, CircuitSynthesis
```

Connect to Resonance and create Qiskit backend from it.

```
from iqm.qiskit_iqm import IQMProvider
```

```
import os
SERVER_URL = "https://resonance.iqm.tech"
# If the token isn't saved in the environment, replace this by the token as a string.
API_TOKEN = os.environ.get("IQM_RESONANCE_API_TOKEN")
iqm_backend = IQMProvider(SERVER_URL, token=API_TOKEN, quantum_computer="garnet").get_backend()
```

Extract info from the Qiskit backend object (mostly QPU topology).

```
my_qpu = CrystalQPUFromBackend(iqm_backend)
```

The user **has to** manually specify a mapping between hardware qubits on the QPU (by convention labelled by integers starting from 0) and the variables of the problem (here labelled by letters “a”, “b”, “c”, “d”).

```
initial_mapping = {0:{"a"}, 1:{"b"}, 4:{"c"}, 3:{"d"}}
my_mapping = ParityMapping(my_qpu, initial_mapping)  # The object to keep track of the mapping between hardware qubits and parities.
my_circ_synth = CircuitSynthesis(my_mapping)
```

There are two “regimes” of using the `CircuitSynthesis` class:

1.  Starting from a given higher-order Hamiltonian that we want to represent.

2.  Start by constructing a circuit (composed of CNOTs and RZs) and get a Hamiltonian from it.

Start from a given higher-order Hamiltonian.

```
from dimod.higherorder.polynomial import BinaryPolynomial  # Class from `dimod` package representing higher-order binary polynomials.
```

```
coeffs = {
        ("a",): 0.1,
        ("b",): 0.1,
        ("c",): 0.1,
        ("d",): 0.1,
        ("a","b"): 0.2,
        ("b","c"): 0.2,
        ("c", "d"): 0.2,
        ("d", "a"): 0.2,
        ("a", "b", "c", "d"): 0.4,
    } # Plaquette.
bp = BinaryPolynomial(coeffs, vartype = "SPIN")
```

Apply some CNOTs to the circuit synthesis object.

```
my_circ_synth.cnot(0, 1)
my_circ_synth.cnot(1, 4)
my_circ_synth.cnot(4, 3)
```

Build the qiskit circuit, providing the `bp` object of interactions. Note three things:

1.  The dark blue identity gates are used to label which parities are assigned to which qubit.

2.  The `build_qiskit` method automatically adds RZ gates to where they are needed to represent the input Hamiltonian.

3.  The warning is raised because we provided a Hamiltonian, but didn’t execute all of its interactions.

```
qc = my_circ_synth.build_qiskit_phase_separator(gamma=1, interactions=bp)
qc.draw("mpl")
```

Now we do the opposite approach: We construct a circuit first and then “find out” what Hamiltonian it represents.

```
my_circ_synth = CircuitSynthesis(my_mapping)  # Reinitialize the object.
```

This time we interleave the CNOT gates with RZ gates.

```
my_circ_synth.rz(0.1, 1)
my_circ_synth.rz(0.1, 0)
my_circ_synth.cnot(0, 1)
my_circ_synth.cnot(1, 4)
my_circ_synth.rz(0.3, 4)
my_circ_synth.cnot(4, 3)
my_circ_synth.rz(0.4, 3)
```

```
qc = my_circ_synth.build_qiskit_phase_separator(gamma=1)
qc.draw("mpl")
```

Now we have two options:

1.  Examine what kind of Hamiltonian we represent by our circuit.

2.  Examine what Hamiltonian we could have represented with the same CNOTs.

```
print(my_circ_synth.possible_ints)
print(my_circ_synth.constructed_hamiltonian_bp)
```
