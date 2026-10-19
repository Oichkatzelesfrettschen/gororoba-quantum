> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.ParityMapping.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.ParityMapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 792e55a2f5884bc996aa34516ee6ab2e21ff81cde88839d3c4fa43bf8133b8e0.

# ParityMapping

Module: [`iqm.qaoa.transpiler.routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html#module-iqm.qaoa.transpiler.routing "iqm.qaoa.transpiler.routing")

*class* iqm.qaoa.transpiler.routing.ParityMapping(*qpu*, *initial_mapping*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L723-L797)  
Bases: [`BaseMapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseMapping.html#iqm.qaoa.transpiler.routing.BaseMapping "iqm.qaoa.transpiler.routing.BaseMapping")

Maps hardware qubits to sets of logical qubits representing parities.

This class maintains a dynamic mapping between physical (hardware) qubits and logical qubit sets that encode parity relationships used in quantum circuit synthesis of phase polynomials.

Parameters:  
- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – The QPU providing the hardware graph.

- **initial_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[HardQubit,* [*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[LogQubit\]\]*) – Initial mapping from hardware qubits to sets of logical qubits representing parities.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the initial mapping contains qubits not present in the QPU.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the initial mapping maps any hardware qubit to a parity of multiple qubits. The initial mapping may only map hardware qubits to either the empty set `set()` or to sets containing a single logical qubit, such as e.g., `{log_qb}`.

Methods

|  |  |
|----|----|
| [`cnot`](#iqm.qaoa.transpiler.routing.ParityMapping.cnot "iqm.qaoa.transpiler.routing.ParityMapping.cnot") | Simulates the effect of a CNOT gate on the parity mapping. |
| [`swap_hard`](#iqm.qaoa.transpiler.routing.ParityMapping.swap_hard "iqm.qaoa.transpiler.routing.ParityMapping.swap_hard") | Swaps the parity mapping between two hardware qubits. |

cnot(*control*, *target*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L765-L784)  
Simulates the effect of a CNOT gate on the parity mapping.

The CNOT updates the parity of the target qubit by XOR-ing it with the control qubit’s parity set.

Parameters:  
- **control** (*HardQubit*) – The control hardware qubit.

- **target** (*HardQubit*) – The target hardware qubit.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the control and target qubits are not connected in the QPU hardware graph.

Return type:  
None

swap_hard(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L786-L797)  
Swaps the parity mapping between two hardware qubits.

This corresponds to exchanging the logical parity assignments of two connected hardware qubits.

Parameters:  
**gate** (*HardEdge*) – A pair of hardware qubits (qb0, qb1) to swap.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.routing.ParityMapping](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-d4c50ab401a9e63d4f596a8c0f1801b2413f82ae.png)
