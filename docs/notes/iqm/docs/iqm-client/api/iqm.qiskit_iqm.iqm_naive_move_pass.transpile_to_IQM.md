> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c9477782d15a797ad727f71a2d27a5b2dc9ba483477e2c575a342644c9cb55a2.

# iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM

iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM(*circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*, *backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "iqm.qiskit_iqm.iqm_backend.IQMBackendBase")*, *\**, *initial_layout: [Layout](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Layout "(in Qiskit v2.5)") \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *perform_move_routing: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *optimize_single_qubits: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *ignore_barriers: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *remove_final_rzs: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *existing_moves_handling: [ExistingMoveHandlingOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *restrict_to_qubits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\*\*qiskit_transpiler_kwargs*) → [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")  
Customized transpilation to IQM backends.

Works with both the Crystal and Star architectures.

Note: When transpiling a circuit with MOVE gates, you might need to set `optimization_level` lower. If `optimization_level` is set too high, the transpiler might add single qubit gates onto the resonator, which is not supported by the IQM Star architectures. If this in undesired, it is best to have the transpiler add the MOVE gates automatically, rather than manually adding them to the circuit.

Parameters:  
- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – The circuit to transpile.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "iqm.qiskit_iqm.iqm_backend.IQMBackendBase")) – The backend to transpile to.

- **initial_layout** ([*Layout*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Layout "(in Qiskit v2.5)") *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *\|* *None*) – The initial layout to use for the transpilation, same as [`transpile()`](https://quantum.cloud.ibm.com/docs/api/qiskit/compiler#qiskit.compiler.transpile "(in Qiskit v2.5)").

- **perform_move_routing** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to perform MOVE gate routing.

- **optimize_single_qubits** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to optimize single qubit gates away.

- **ignore_barriers** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to ignore barriers when optimizing single qubit gates away.

- **remove_final_rzs** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to remove the final z rotations. They do not affect the measurement outcomes of the circuit, but removing them changes its unitary propagator. Defaults to False, so that the transpiled circuit remains equivalent to the original one up to a global phase.

- **existing_moves_handling** ([*ExistingMoveHandlingOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") *\|* *None*) – How to handle existing MOVE gates in the circuit, required if the circuit contains MOVE gates.

- **restrict_to_qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Restrict the transpilation to only use these specific physical qubits. Note that you will also have to pass this information to `qiskit_IQMBackend.run()` using the `qubit_index_to_name` parameter.

- **qiskit_transpiler_kwargs** – Arguments to be passed to the Qiskit transpiler.

Returns:  
Transpiled circuit ready for running on the backend.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")
