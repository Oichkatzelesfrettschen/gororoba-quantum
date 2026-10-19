> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_pauli_dressed_mrb_circuits.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_pauli_dressed_mrb_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 28c95bd94a63fb4bc11027dc79f41789ff3fd07aabb1b6958a4185ece306ce4e.

# iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_pauli_dressed_mrb_circuits

iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_pauli_dressed_mrb_circuits(*qubits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *mrb_config: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*, *routing_method: [RoutingMethod](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod") = RoutingMethod.BASIC*, *optimize_sqg: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *simulation_method: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['automatic', 'statevector', 'stabilizer', 'extended_stabilizer', 'matrix_product_state'\] = 'stabilizer'*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]  
Samples a mirror circuit and generates samples of “Pauli-dressed” circuits.

For each circuit, random Pauli layers are interleaved between each layer of the circuit.

Parameters:  
- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Qubits of the backend.

- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Backend.

- **mrb_config** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")) – Wraps the following parameters. *pauli_samples_per_circ*: number of Pauli samples per circuit. *depth*: depth (number of canonical layers) of the circuits. *density_2q_gates*: expected density of 2Q gates. *two_qubit_gate_ensemble*: dictionary with keys being str specifying 2Q gates, and values being corresponding probabilities; default is None. *clifford_sqg_probability*: probability with which to uniformly sample Clifford 1Q gates; default is 1.0. *sqg_gate_ensemble*: dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities; default is None. *qiskit_optim_level*: Qiskit transpiler optimization level; default is 1.

- **routing_method** ([*RoutingMethod*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod")) – Qiskit transpiler routing method. Default is “basic”.

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to optimize single-qubit gates in transpilation. Default is False.

- **simulation_method** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['automatic',* *'statevector',* *'stabilizer',* *'extended_stabilizer',* *'matrix_product_state'\]*) – Qiskit’s Aer simulation method. Default is “automatic”.

Returns:  
Samples of “Pauli-dressed” circuits.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]
