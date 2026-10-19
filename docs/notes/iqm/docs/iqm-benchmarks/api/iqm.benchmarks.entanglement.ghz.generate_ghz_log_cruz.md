> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_log_cruz.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_log_cruz.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7ad80abb092e99dfd8d1790dc593a8260dc64841c415e18a9ea5a8ab855695bd.

# iqm.benchmarks.entanglement.ghz.generate_ghz_log_cruz

iqm.benchmarks.entanglement.ghz.generate_ghz_log_cruz(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Generates a GHZ state in log-depth according to [https://arxiv.org/abs/1807.05572](https://arxiv.org/abs/1807.05572).

Parameters:  
**num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits of the GHZ state

Returns:  
A quantum circuit generating a GHZ state on a given number of qubits.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")
