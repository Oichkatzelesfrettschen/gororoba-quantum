> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.import_native_gate_cliffords.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.import_native_gate_cliffords.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 062a0b9e25d66fc0b060da9569845fdad9c6f45551f82169c825d94d9b89ce58.

# iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.import_native_gate_cliffords

iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.import_native_gate_cliffords(*system_size: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['1q'\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\
iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.import_native_gate_cliffords(*system_size: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['2q'\]*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]  
Import native gate Clifford dictionaries.

Parameters:  
**system_size** – System size to load, either “1q” or “2q”. If None, load both dictionaries.

Returns:  
If system_size is specified, returns the dictionary for that system size. If system_size is None, returns a tuple of (1q_dict, 2q_dict).

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If system_size is not None, “1q”, or “2q”.
