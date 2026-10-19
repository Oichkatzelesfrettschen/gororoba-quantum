> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.parallelize_and_transpile.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.parallelize_and_transpile.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 baf940c2d042f99dea451a0d55344f2535a33653bab8e04ba02c2c007d720fea.

# iqm.qiskit_iqm.pulse_level_utils.parallelize_and_transpile

iqm.qiskit_iqm.pulse_level_utils.parallelize_and_transpile(*circuits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]*, *components: [ComponentGrouping](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "(in IQM Pulla v15.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*, *context: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*, *perform_move_routing: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *optimize_single_qubits: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *ignore_barriers_in_1qb_optimization: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *remove_final_rzs: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *existing_moves_handling: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *optimization_level: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*, *seed_transpiler: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *num_processes: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]\]  
Transpile Qiskit circuits and parallelize them if colour grouped components were inputted.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]*) – Qiskit quantum circuits to transpile and potentially parallelize.

- **components** ([*ComponentGrouping*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "(in IQM Pulla v15.0.0)") *\|* *None*) – Physical QPU components on which to transpile (route) the circuits. If a flat list of components is provided, the [`IQMTarget`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.IQMTarget.html#iqm.qiskit_iqm.iqm_target.IQMTarget "iqm.qiskit_iqm.iqm_target.IQMTarget") will be built only on that subset of the full QPU. If colour grouped components are provided, the circuits will be parallelized such that each colour group becomes its own circuit, and the circuit will be broadcasted to parallel groups within a colour group, i.e. executed parallelly. If `None`, the default target for the full QPU will be used.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Compiler context.

- **perform_move_routing** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to perform MOVE gate routing.

- **optimize_single_qubits** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to optimize single qubit gates away.

- **ignore_barriers_in_1qb_optimization** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to ignore barriers when optimizing single qubit gates.

- **remove_final_rzs** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to remove the final z rotations.

- **existing_moves_handling** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – How to handle existing MOVE gates in the circuit, required if the circuit contains MOVE gates.

- **optimization_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The optimization level of the Qiskit transpiler.

- **seed_transpiler** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The seed of the Qiskit transpiler.

- **num_processes** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of parallel processes to use.

Returns:  
Transpiled and possibly parallelized circuits. The circuit(s) in each inner list are executed in parallel. If there is no parallelization, each inner list has just one item.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]\]
