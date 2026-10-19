> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a4cefabf8c838704cf06da3566cc51502417416d58ab623e6af1f9b5fd6da214.

# IQMBackend

Module: [`iqm.qiskit_iqm.iqm_provider`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.html#module-iqm.qiskit_iqm.iqm_provider "iqm.qiskit_iqm.iqm_provider")

*class* iqm.qiskit_iqm.iqm_provider.IQMBackend(*client: [IQMClient](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient")*, *\**, *calibration_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *use_metrics: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *\*\*kwargs*)  
Bases: [`IQMBackendBase`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "iqm.qiskit_iqm.iqm_backend.IQMBackendBase")

Backend for executing quantum circuits on IQM quantum computers.

Parameters:  
- **client** ([*IQMClient*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient")) – Client instance for communicating with an IQM Server.

- **calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *UUID* *\|* *None*) – ID of the calibration set the backend will use. `None` means the IQM Server will be queried for the current default calibration set.

- **use_metrics** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, the backend will query the server for calibration data and related quality metrics, and pass these to the transpilation target(s). The default value is set to False until quality metrics become available on the Resonance API.

- **kwargs** – Optional arguments to be passed to the parent Backend initializer.

Attributes

|  |  |
|----|----|
| [`max_circuits`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.max_circuits "iqm.qiskit_iqm.iqm_provider.IQMBackend.max_circuits") | Maximum number of circuits that should be run in a single batch. |
| `name` | Name of the backend. |
| `description` | Optional human-readable description. |
| `online_date` | Date that the backend came online. |
| `backend_version` | Version of the backend being provided. |

Methods

|  |  |
|----|----|
| [`create_circuit_job_definition`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition "iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition") | Create a circuit job definition without submitting it for execution. |
| [`retrieve_job`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.retrieve_job "iqm.qiskit_iqm.iqm_provider.IQMBackend.retrieve_job") | Create and return an IQMJob instance associated with this backend with given job id. |
| [`run`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run") | Run a quantum circuit or a list of quantum circuits on the IQM quantum computer represented by this backend. |
| [`serialize_circuit`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.serialize_circuit "iqm.qiskit_iqm.iqm_provider.IQMBackend.serialize_circuit") | Serialize a quantum circuit into the IQM data transfer format. |

*property* max_circuits*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Maximum number of circuits that should be run in a single batch.

Currently there is no hard limit on the number of circuits that can be executed in a single batch/job. However, some libraries like Qiskit Experiments use this property to split multi-circuit computational tasks into multiple baches/jobs.

The default value is `None`, meaning there is no limit. You can set it to a specific integer value to force these libraries to run at most that many circuits in a single batch.

run(*run_input: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *\*\*options*) → [IQMJob](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_job.IQMJob.html#iqm.qiskit_iqm.iqm_job.IQMJob "iqm.qiskit_iqm.iqm_job.IQMJob")  
Run a quantum circuit or a list of quantum circuits on the IQM quantum computer represented by this backend.

Parameters:  
- **run_input** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]*) – The circuits to run.

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Submits the job to the timeslot queue if set to `True`. If set to `False`, the job is submitted to the normal on-demand queue.

- **options** – Keyword arguments passed on to [`create_circuit_job_definition()`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition "iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition"), and documented there.

Returns:  
Job object from which the results can be obtained once the execution has finished.

Return type:  
[*IQMJob*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_job.IQMJob.html#iqm.qiskit_iqm.iqm_job.IQMJob "iqm.qiskit_iqm.iqm_job.IQMJob")

create_circuit_job_definition(*run_input: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1024*, *circuit_compilation_options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *circuit_callback: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]\], [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *qubit_index_to_name: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\*\*unknown_options*) → PostJobsRequest  
Create a circuit job definition without submitting it for execution.

This can be used to check what would be submitted for execution by an equivalent call to [`run()`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run").

Parameters:  
- **run_input** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]*) – Same as in [`run()`](#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run").

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of repetitions of each circuit, for sampling.

- **circuit_compilation_options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") *\|* *None*) – Compilation options for the circuits, passed on to [`IQMClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient"). If `None`, the defaults of the [`CircuitCompilationOptions`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") class are used.

- **circuit_callback** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]\],* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – Callback function that, if provided, will be called for the circuits before sending them to the device. This may be useful in situations when you do not have explicit control over transpilation, but need some information on how it was done. This can happen, for example, when you use pre-implemented algorithms and experiments in Qiskit, where the implementation of the said algorithm or experiment takes care of delivering correctly transpiled circuits to the backend. This callback method gives you a chance to look into those transpiled circuits, and extract any info you need. As a side effect, you can also use this callback to modify the transpiled circuits in-place, just before execution; however, we do not recommend to use it for this purpose.

- **qubit_index_to_name** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Mapping from qubit indices in the circuit to qubit names on the device. If `None`, [`IQMBackendBase.index_to_qubit_name`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name") will be used.

- **unknown_options** – Backwards compatibility for deprecated parameters.

Returns:  
The created circuit job definition object

Return type:  
*PostJobsRequest*

retrieve_job(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [IQMJob](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_job.IQMJob.html#iqm.qiskit_iqm.iqm_job.IQMJob "iqm.qiskit_iqm.iqm_job.IQMJob")  
Create and return an IQMJob instance associated with this backend with given job id.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – ID of the job to retrieve.

Returns:  
corresponding job

Return type:  
[*IQMJob*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_job.IQMJob.html#iqm.qiskit_iqm.iqm_job.IQMJob "iqm.qiskit_iqm.iqm_job.IQMJob")

serialize_circuit(*circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*, *qubit_index_to_name: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")  
Serialize a quantum circuit into the IQM data transfer format.

Serializing is not strictly bound to the native gateset, i.e. some gates that are not explicitly mentioned in the native gateset of the backend can still be serialized. For example, the native single qubit gate for IQM backend is the ‘r’ gate, however ‘x’, ‘rx’, ‘y’ and ‘ry’ gates can also be serialized since they are just particular cases of the ‘r’ gate. If the circuit was transpiled against a backend using Qiskit’s transpiler machinery, these gates are not supposed to be present. However, when constructing circuits manually and submitting directly to the backend, it is sometimes more explicit and understandable to use these concrete gates rather than ‘r’. Serializing them explicitly makes it possible for the backend to accept such circuits.

Qiskit uses one measurement instruction per qubit (i.e. there is no measurement grouping concept). While serializing we do not group any measurements together but rather associate a unique measurement key with each measurement instruction, so that the results can later be reconstructed correctly (see [`MeasurementKey`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.html#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey") documentation for more details).

Parameters:  
- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – quantum circuit to serialize

- **qubit_index_to_name** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Mapping from qubit indices in the circuit to qubit names on the device. If `None`, [`IQMBackendBase.index_to_qubit_name`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name") will be used.

Returns:  
data transfer object representing the circuit

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – circuit contains an unsupported instruction or is not transpiled in general

Return type:  
[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_provider.IQMBackend](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-c7d255559815b21226a29bca8cbda2ae672cc66f.png)
