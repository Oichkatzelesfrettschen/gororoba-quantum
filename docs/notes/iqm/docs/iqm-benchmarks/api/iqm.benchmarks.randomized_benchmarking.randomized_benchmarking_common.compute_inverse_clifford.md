> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.compute_inverse_clifford.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.compute_inverse_clifford.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b54fcf81feaf2f1ce9560d8c43163b1c275cf3e68c31a93d17953ee95f40ca40.

# iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.compute_inverse_clifford

iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.compute_inverse_clifford(*qc_inv: [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*, *clifford_dictionary: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Function to compute the inverse Clifford of a circuit.

Parameters:  
- **qc_inv** ([*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")) – The Clifford circuit to be inverted

- **clifford_dictionary** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")) – A dictionary of Clifford gates labeled by (de)stabilizers

Returns:  
A Clifford circuit

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)") \| None
