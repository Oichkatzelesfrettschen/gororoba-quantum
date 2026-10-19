> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.examples.transpile_example.transpile_example.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.examples.transpile_example.transpile_example.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ad69f587bd4eb249a05a45a7fdad9742a492b095617b2d35fd05ed456d9921af.

# iqm.qiskit_iqm.examples.transpile_example.transpile_example

iqm.qiskit_iqm.examples.transpile_example.transpile_example(*server_url: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *quantum_computer: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Run a GHZ circuit transpiled using the Qiskit transpile function.

Parameters:  
- **server_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – URL of the IQM Server used for execution (e.g. “[https://resonance.iqm.tech/](https://resonance.iqm.tech/)”). If `None`, must be provided in the environment variable `IQM_SERVER_URL`.

- **quantum_computer** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – ID or alias of the quantum computer to connect to, if the IQM Server instance controls more than one (e.g. “garnet”). `None` means connect to the default one.

Returns:  
transpiled circuit, a mapping of bitstrings representing qubit measurement results to counts for each result

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]
