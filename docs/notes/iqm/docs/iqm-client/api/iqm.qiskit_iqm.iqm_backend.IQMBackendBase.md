> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3082b3e5b3981e3b4ad0b9b2a4a47c72b280b32fffa442494871ead0ed09602b.

# IQMBackendBase

Module: [`iqm.qiskit_iqm.iqm_backend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.html#module-iqm.qiskit_iqm.iqm_backend "iqm.qiskit_iqm.iqm_backend")

*class* iqm.qiskit_iqm.iqm_backend.IQMBackendBase(*architecture: DynamicQuantumArchitecture*, *\**, *metrics: ObservationFinder \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'IQMBackend'*, *\*\*kwargs*)  
Bases: [`BackendV2`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.providers.BackendV2 "(in Qiskit v2.5)"), [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

Abstract base class for various IQM-specific backends.

Parameters:  
- **architecture** (*DynamicQuantumArchitecture*) – Dynamic quantum architecture associated with the backend instance.

- **metrics** (*ObservationFinder* *\|* *None*) – Optional calibration data and related quality metrics for the transpilation target.

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Optional name for the backend instance.

Attributes

|  |  |
|----|----|
| [`max_circuits`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.max_circuits "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.max_circuits") | Maximum number of circuits for a single job. |
| [`physical_qubits`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.physical_qubits "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.physical_qubits") | Return the list of physical qubits in the backend. |
| [`target`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.target "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.target") | Return the target without computational resonators. |
| [`target_with_resonators`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.target_with_resonators "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.target_with_resonators") | Return the target with MOVE gates and resonators included. |
| `name` | Name of the backend. |
| `description` | Optional human-readable description. |
| `online_date` | Date that the backend came online. |
| `backend_version` | Version of the backend being provided. |

Methods

|  |  |
|----|----|
| [`get_real_target`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.get_real_target "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.get_real_target") | Return the real physical target of the backend without fictional CZ gates. |
| [`get_scheduling_stage_plugin`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.get_scheduling_stage_plugin "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.get_scheduling_stage_plugin") | Return the plugin that should be used for scheduling the circuits on this backend. |
| [`has_resonators`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.has_resonators "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.has_resonators") | True iff the backend QPU has computational resonators. |
| [`index_to_qubit_name`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name") | Given a quantum register index, return the corresponding IQM-style qubit name. |
| [`qubit_name_to_index`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.qubit_name_to_index "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.qubit_name_to_index") | Given an IQM-style qubit name, return the corresponding index in the register. |
| [`run`](#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.run "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.run") | Run (or simulate) the execution of quantum circuit(s). |

*property* target*: [Target](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Target "(in Qiskit v2.5)")*  
Return the target without computational resonators.

*property* target_with_resonators*: [Target](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Target "(in Qiskit v2.5)")*  
Return the target with MOVE gates and resonators included.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – The backend does not have resonators.

*property* physical_qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Return the list of physical qubits in the backend.

has_resonators() → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
True iff the backend QPU has computational resonators.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

get_real_target() → [Target](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Target "(in Qiskit v2.5)")  
Return the real physical target of the backend without fictional CZ gates.

Return type:  
[*Target*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Target "(in Qiskit v2.5)")

qubit_name_to_index(*name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
Given an IQM-style qubit name, return the corresponding index in the register.

Parameters:  
**name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – IQM-style qubit name (‘QB1’, ‘QB2’, etc.)

Returns:  
Index of the given qubit in the quantum register.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Qubit name cannot be found on the backend.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

index_to_qubit_name(*index: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Given a quantum register index, return the corresponding IQM-style qubit name.

Parameters:  
**index** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Qubit index in the quantum register.

Returns:  
Corresponding IQM-style qubit name (‘QB1’, ‘QB2’, etc.).

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Qubit index cannot be found on the backend.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_scheduling_stage_plugin() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Return the plugin that should be used for scheduling the circuits on this backend.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

*property* max_circuits*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Maximum number of circuits for a single job.

None means unlimited.

*abstractmethod* run(*run_input: QuantumCircuit \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[QuantumCircuit\]*, *\*\*options*) → JobV1  
Run (or simulate) the execution of quantum circuit(s).

Note that the return type is `JobV1`, not [`IQMJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_job.IQMJob.html#iqm.qiskit_iqm.iqm_job.IQMJob "iqm.qiskit_iqm.iqm_job.IQMJob"), since this is what [`IQMFakeBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.html#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend") produces.

Parameters:  
**run_input** (*QuantumCircuit* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[QuantumCircuit\]*)

Return type:  
JobV1

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_backend.IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-5092e6be8f42af93d3917a356971981d0017e46a.png)
