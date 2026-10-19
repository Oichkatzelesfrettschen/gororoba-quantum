> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.qiskit_to_iqm.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.qiskit_to_iqm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c22c72515099f3d67ff28d6b443b08f999c0875569a6c6a596e8c89cd12dc5c0.

# iqm.qiskit_iqm.pulse_level_utils.qiskit_to_iqm

iqm.qiskit_iqm.pulse_level_utils.qiskit_to_iqm(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend")*, *qiskit_circuits: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") \| [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]*, *\**, *loading_rules: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[RuleType](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "(in IQM Pulla v15.0.0)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\], [Compiler](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html#iqm.cpc.compiler.compiler.Compiler "(in IQM Pulla v15.0.0)")\]  
Convert transpiled Qiskit quantum circuits to IQM format, for compiling to pulse level.

Also provides the Compiler object for compiling them, with the correct calibration set and component mapping initialized.

Parameters:  
- **backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend")) – qiskit-iqm backend used to transpile the circuits. Determines the calibration set to be used by the returned compiler.

- **qiskit_circuits** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]*) – One or many transpiled Qiskit QuantumCircuits to convert.

- **loading_rules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "(in IQM Pulla v15.0.0)")*\]* *\|* *None*) – Optional list of rules to use for loading the circuit. If not provided, will load the default calibration set from the backend.

Returns:  
Equivalent IQM circuit(s), compiler for compiling them.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\], [*Compiler*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html#iqm.cpc.compiler.compiler.Compiler "(in IQM Pulla v15.0.0)")\]
