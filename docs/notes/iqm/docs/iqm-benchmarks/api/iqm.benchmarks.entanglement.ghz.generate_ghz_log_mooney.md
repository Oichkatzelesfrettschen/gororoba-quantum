> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_log_mooney.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_log_mooney.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cb24c9aa2c224752a5a2bfae1f30a542413538b82d06c917dee9185159223888.

# iqm.benchmarks.entanglement.ghz.generate_ghz_log_mooney

iqm.benchmarks.entanglement.ghz.generate_ghz_log_mooney(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Generates a GHZ state in log-depth according to [https://arxiv.org/abs/2101.08946](https://arxiv.org/abs/2101.08946).

Parameters:  
**num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits of the GHZ state

Returns:  
A quantum circuit generating a GHZ state on a given number of qubits.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")
