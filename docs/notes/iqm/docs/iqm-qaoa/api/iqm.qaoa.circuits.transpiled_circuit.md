> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.transpiled_circuit.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.transpiled_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ff0e13227d2790d05f4a622904ef6a484958a3557d6a7915d1507ed9cd2016a1.

# transpiled_circuit

iqm.qaoa.circuits.transpiled_circuit(*qaoa*, *backend=None*, *transpiler=None*, *iqm_layout=True*, *\*\*kwargs*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L228-L343)  
Build a QAOA quantum circuit for the given QAOA instance.

This function has highly varying outputs based on which transpiler is used. If no transpiler is used, the perfect [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") is returned using [`qiskit_circuit()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit.html#iqm.qaoa.circuits.qiskit_circuit "iqm.qaoa.circuits.qiskit_circuit"). Otherwise, the QAOA circuit is transpiled using one of the transpilers, respecting the topology of `backend`.

Parameters:  
- **qaoa** ([*QUBOQAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA")) – The QAOA instance object whose quantum circuit is constructed.

- **backend** (*BackendV2* *\|* *None*) – Backend that the circuit is to be run on. The connectivity of the backend is required for the transpilation. `None` means use the [`AerSimulator`](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html#qiskit_aer.AerSimulator "(in Qiskit Aer v0.17.1)") statevector simulation.

- **transpiler** ([*TranspilerOption*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.TranspilerOption.html#iqm.qaoa.circuits.TranspilerOption "iqm.qaoa.circuits.TranspilerOption") *\|* *None*) – Defines which algorithm should be used for transpilation (if any).

- **iqm_layout** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – True iff IQM Qubit Selector should be used to find the optimal layout of the circuit on the QPU.

- **\*\*kwargs** (*Any*) – Keyword arguments are passed on to `transpile()`, for examples see Keyword Args.

Keyword Arguments:  
- **initial_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – List of hardware qubits onto which the circuit qubits are mapped.

- **seed_transpiler** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Random seed for the transpilation.

Returns:  
A quantum circuit transpiled to the topology of `backend`.

Raises:  
- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the `backend` is not an IQM backend and a custom `transpiler` is selected (i.e., other than `None` or “Default”).

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the provided `transpiler` is not one of the allowed transpilers.

Return type:  
QuantumCircuit
