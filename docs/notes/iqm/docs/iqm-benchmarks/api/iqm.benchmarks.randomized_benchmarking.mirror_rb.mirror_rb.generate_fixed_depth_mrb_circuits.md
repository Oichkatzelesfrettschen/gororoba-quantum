> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_fixed_depth_mrb_circuits.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_fixed_depth_mrb_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e1798663dcd7b8f6a10e234d59ed3b79fceef6b3213b50af182d875dd06a1493.

# iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_fixed_depth_mrb_circuits

iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_fixed_depth_mrb_circuits(*qubits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *mrb_config: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*, *routing_method: [RoutingMethod](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod") = RoutingMethod.BASIC*, *optimize_sqg: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *simulation_method: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['automatic', 'statevector', 'stabilizer', 'extended_stabilizer', 'matrix_product_state'\] = 'stabilizer'*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]\]  
Generates a dictionary of MRB circuits at fixed depth, indexed by sample number.

Parameters:  
- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – List of integers specifying physical qubit labels.

- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Backend

- **mrb_config** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")) – Wraps the following parameters. *circ_samples*: number of sets of Pauli-dressed circuit samples. *pauli_samples_per_circ*: number of Pauli samples per circuit. *depth*: depth (number of canonical layers) of the circuits. *density_2q_gates*: expected density of 2Q gates. *two_qubit_gate_ensemble*: dictionary with keys being str specifying 2Q gates, and values being corresponding probabilities; default is None. *clifford_sqg_probability*: probability with which to uniformly sample Clifford 1Q gates; default is 1.0. *sqg_gate_ensemble*: dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities; default is None. *qiskit_optim_level*: Qiskit transpiler optimization level; default is 1.

- **routing_method** ([*RoutingMethod*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod")) – Qiskit transpiler routing method. Default is “basic”.

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to optimize single-qubit gates in transpilation. Default is False.

- **simulation_method** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['automatic',* *'statevector',* *'stabilizer',* *'extended_stabilizer',* *'matrix_product_state'\]*) – Qiskit’s Aer simulation method. Default is “automatic”.

Returns:  
A dictionary of lists of Pauli-dressed quantum circuits corresponding to the circuit sample index.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]\]
