> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.qiskit_circuits_to_iqm_circuits.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.qiskit_circuits_to_iqm_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 175923222e0871cdf366d61112fe1482d1e8a64a7c7178087525d22e3bf3deeb.

# iqm.qiskit_iqm.pulse_level_utils.qiskit_circuits_to_iqm_circuits

iqm.qiskit_iqm.pulse_level_utils.qiskit_circuits_to_iqm_circuits(*circuits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]\]*, *components: [ComponentGrouping](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "(in IQM Pulla v15.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*, *context: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\]  
Convert Qiskit QuantumCircuits to IQM circuits.

Parameters:  
- **circuits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]\]*) – Qiskit QuantumCircuit objects to compile. The circuits in each inner list are executed in parallel.

- **components** ([*ComponentGrouping*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "(in IQM Pulla v15.0.0)") *\|* *None*) – Physical components on which to compile the circuits. If `None`, will use the default [`IQMTarget`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.IQMTarget.html#iqm.qiskit_iqm.iqm_target.IQMTarget "iqm.qiskit_iqm.iqm_target.IQMTarget") in the Qiskit backend, otherwise restricts to these components.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The Compiler context.

Returns:  
Converted IQM circuits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\]
