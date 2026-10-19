> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_linear.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_linear.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 19fd020064a940830f1927a21f883db039a340f04b5a2c49f8066cfefea0ee51.

# iqm.benchmarks.entanglement.ghz.generate_ghz_linear

iqm.benchmarks.entanglement.ghz.generate_ghz_linear(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Generates a GHZ state by applying a Hadamard and a series of CX gates in a linear fashion.

The construction is symmetrized to halve the circuit depth.

Parameters:  
**num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits of the GHZ state.

Returns:  
A quantum circuit generating a GHZ state on a given number of qubits.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")
