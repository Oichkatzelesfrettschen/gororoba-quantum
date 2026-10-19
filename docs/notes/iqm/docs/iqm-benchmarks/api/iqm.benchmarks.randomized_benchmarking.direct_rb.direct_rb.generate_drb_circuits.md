> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.generate_drb_circuits.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.generate_drb_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d803a875a7171b6cf8744615d6c8daad848a75d544d9e8a7c5b61d8286dea739.

# iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.generate_drb_circuits

iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.generate_drb_circuits(*qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *depth: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *circ_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *density_2q_gates: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.25*, *two_qubit_gate_ensemble: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *clifford_sqg_probability: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 1.0*, *sqg_gate_ensemble: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *qiskit_optim_level: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *routing_method: [RoutingMethod](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod") = RoutingMethod.BASIC*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]  
Generates lists of samples of Direct RB circuits.

The structure is: Stabilizer preparation - Layers of canonical randomly sampled gates - Stabilizer measurement

Parameters:  
- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Qubits of the backend.

- **depth** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Depth (number of canonical layers) of the circuit.

- **circ_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of circuit samples to generate.

- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Backend.

- **density_2q_gates** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Expected density of 2Q gates.

- **two_qubit_gate_ensemble** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – Dictionary with keys being str specifying 2Q gates, and values being corresponding probabilities. Default is None.

- **clifford_sqg_probability** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Probability with which to uniformly sample Clifford 1Q gates. Default is 1.0.

- **sqg_gate_ensemble** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – Dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities. Default is None.

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Qiskit transpiler optimization level. Default is 1.

- **routing_method** ([*RoutingMethod*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod")) – Qiskit transpiler routing method. Default is “basic”.

Returns:  
Dictionary with keys “transpiled”, “untranspiled” and values as lists of respective DRB circuits.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]
