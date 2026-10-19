> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.parse_gate_set.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.parse_gate_set.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 734fd15ec5a66c8eae8c04fc7b15162e1a4417749c1232295028f494cc78278d.

# iqm.benchmarks.compressive_gst.compressive_gst.parse_gate_set

iqm.benchmarks.compressive_gst.compressive_gst.parse_gate_set(*configuration: [GSTConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.html#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration")*, *num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *qubit_layouts: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\], [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Handles different gate set inputs and produces a valid gate set.

Parameters:  
- **configuration** ([*GSTConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.html#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration")) – Configuration class containing variables

- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits on which the gate set is defined

- **qubit_layouts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – A List of physical qubit layouts, as specified by integer labels, where the benchmark is meant to be run.

Returns:  
- List of gates defined as quantum circuit objects

- The names of gates, i.e. “Rx_pi_2” for a pi/2 rotation around the x-axis.

- The number of gates in the gate set

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\], [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]
