> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.get_qiskit_compiler.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.get_qiskit_compiler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 34f9287425f9da50046fd27345548f8072d7c2042ad6ef8689db2f37522a6804.

# iqm.qiskit_iqm.pulse_level_utils.get_qiskit_compiler

iqm.qiskit_iqm.pulse_level_utils.get_qiskit_compiler(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend")*, *\**, *loading_rules: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[RuleType](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "(in IQM Pulla v15.0.0)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *exa_style_pp: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *controller_mapping: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *gate_definitions: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [QuantumOp](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [Compiler](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html#iqm.cpc.compiler.compiler.Compiler "(in IQM Pulla v15.0.0)")  
IQM Compiler for transforming Qiskit circuits into pulse-level jobs.

Creates a Compiler instance which contains a Qiskit backend and extra initial circuit stages for parallelizing and transpiling Qiskit circuits and converting them to IQM circuit format.

Parameters:  
- **backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend")) – Qiskit backend.

- **loading_rules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "(in IQM Pulla v15.0.0)")*\]* *\|* *None*) – Observation loading rules. If `None`, will use the current default calibration set.

- **exa_style_pp** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to do EXA-style dataset post-processing by default.

- **controller_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]* *\|* *None*) – Dictionary that maps physical QPU component names to their device controller names. The dictionary is of the form: `{<component_name>: {<operation_name>: <controller name>}}`, where operation is one of the following: “drive”, “readout”, “flux” (not all components have all operations supported).

- **gate_definitions** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)")*\]* *\|* *None*) – Names of quantum operations mapped to their definitions, see `QuantumOp`.

Returns:  
Qiskit-specific IQM Compiler.

Return type:  
[*Compiler*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html#iqm.cpc.compiler.compiler.Compiler "(in IQM Pulla v15.0.0)")
