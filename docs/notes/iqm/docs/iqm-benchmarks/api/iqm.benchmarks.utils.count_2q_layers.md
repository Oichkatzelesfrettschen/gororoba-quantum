> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.count_2q_layers.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.count_2q_layers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c03d0c08e42366e95ec8c5cbdcc7ae1f912ff28f216284bb3a2d4ffef6575550.

# iqm.benchmarks.utils.count_2q_layers

iqm.benchmarks.utils.count_2q_layers(*circuit_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Calculate the number of layers of parallel 2-qubit gates in a list of circuits.

Parameters:  
**circuit_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]*) – the list of quantum circuits to analyze.

Returns:  
The number of layers of parallel 2-qubit gates in the list of circuits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]
