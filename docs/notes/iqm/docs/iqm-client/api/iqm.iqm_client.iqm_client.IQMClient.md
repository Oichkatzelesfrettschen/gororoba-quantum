> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 25b7aab34ef3e476bb74a9804c85641fcaf76a101de9b0c9b415c1e828967d23.

# IQMClient

Module: [`iqm.iqm_client.iqm_client`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.html#module-iqm.iqm_client.iqm_client "iqm.iqm_client.iqm_client")

*class* iqm.iqm_client.iqm_client.IQMClient(*\**, *executor: [IQMServerExecutor](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.html#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor")*, *storage: [IQMServerStorage](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.html#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage")*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Provides access to IQM quantum computers, enabling quantum circuit and pulse schedule execution.

IQMClient represents a connection to a quantum computer (real or simulated), and can be used to execute two kinds of jobs:

- batches of quantum circuits (circuit-level jobs), and

- playlists of control pulse schedules (pulse-level jobs).

Parameters:  
- **executor** ([*IQMServerExecutor*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.html#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor")) – IQMServerExecutor instance mapping to backend services.

- **storage** ([*IQMServerStorage*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.html#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage")) – IQMServerStorage instance mapping to backend data repositories.

Attributes

|  |  |
|----|----|
| [`quantum_computer_name`](#iqm.iqm_client.iqm_client.IQMClient.quantum_computer_name "iqm.iqm_client.iqm_client.IQMClient.quantum_computer_name") | Name of the quantum computer this client is connected to. |

Methods

|  |  |
|----|----|
| [`cancel_job`](#iqm.iqm_client.iqm_client.IQMClient.cancel_job "iqm.iqm_client.iqm_client.IQMClient.cancel_job") | Cancel a job that has been submitted for execution. |
| [`create_circuit_job_definition`](#iqm.iqm_client.iqm_client.IQMClient.create_circuit_job_definition "iqm.iqm_client.iqm_client.IQMClient.create_circuit_job_definition") | Create a circuit execution job definition without sending it to the server. |
| [`delete_job`](#iqm.iqm_client.iqm_client.IQMClient.delete_job "iqm.iqm_client.iqm_client.IQMClient.delete_job") | Delete a job that has been submitted for execution. |
| [`from_url`](#iqm.iqm_client.iqm_client.IQMClient.from_url "iqm.iqm_client.iqm_client.IQMClient.from_url") | Utility constructor using [`IQMServerClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient"). |
| [`get_about`](#iqm.iqm_client.iqm_client.IQMClient.get_about "iqm.iqm_client.iqm_client.IQMClient.get_about") | Information about the quantum computer. |
| [`get_calibration_quality_metrics`](#iqm.iqm_client.iqm_client.IQMClient.get_calibration_quality_metrics "iqm.iqm_client.iqm_client.IQMClient.get_calibration_quality_metrics") | Retrieve the given calibration set and related quality metrics from the server. |
| [`get_calibration_set`](#iqm.iqm_client.iqm_client.IQMClient.get_calibration_set "iqm.iqm_client.iqm_client.IQMClient.get_calibration_set") | Retrieve the given calibration set from the server. |
| [`get_calibration_set_stash`](#iqm.iqm_client.iqm_client.IQMClient.get_calibration_set_stash "iqm.iqm_client.iqm_client.IQMClient.get_calibration_set_stash") | Contents of a calibration set in a stash adapter. |
| [`get_chip_label`](#iqm.iqm_client.iqm_client.IQMClient.get_chip_label "iqm.iqm_client.iqm_client.IQMClient.get_chip_label") | QPU label of the current quantum computer. |
| [`get_chip_topology`](#iqm.iqm_client.iqm_client.IQMClient.get_chip_topology "iqm.iqm_client.iqm_client.IQMClient.get_chip_topology") | Chip topology of the current quantum computer. |
| [`get_dynamic_quantum_architecture`](#iqm.iqm_client.iqm_client.IQMClient.get_dynamic_quantum_architecture "iqm.iqm_client.iqm_client.IQMClient.get_dynamic_quantum_architecture") | Retrieve the dynamic quantum architecture (DQA) for the given calibration set from the server. |
| [`get_feedback_groups`](#iqm.iqm_client.iqm_client.IQMClient.get_feedback_groups "iqm.iqm_client.iqm_client.IQMClient.get_feedback_groups") | Retrieve groups of qubits that can receive real-time feedback signals from each other. |
| [`get_health`](#iqm.iqm_client.iqm_client.IQMClient.get_health "iqm.iqm_client.iqm_client.IQMClient.get_health") | Health status of the quantum computer. |
| [`get_job`](#iqm.iqm_client.iqm_client.IQMClient.get_job "iqm.iqm_client.iqm_client.IQMClient.get_job") | Build a new job tracker object for a submitted job. |
| [`get_job_measurement_counts`](#iqm.iqm_client.iqm_client.IQMClient.get_job_measurement_counts "iqm.iqm_client.iqm_client.IQMClient.get_job_measurement_counts") | Query the measurement counts of an executed job. |
| [`get_job_measurements`](#iqm.iqm_client.iqm_client.IQMClient.get_job_measurements "iqm.iqm_client.iqm_client.IQMClient.get_job_measurements") | Query the measurement results of an executed job. |
| [`get_quality_metric_set`](#iqm.iqm_client.iqm_client.IQMClient.get_quality_metric_set "iqm.iqm_client.iqm_client.IQMClient.get_quality_metric_set") | Retrieve the latest quality metric set for the given calibration set from the server. |
| [`get_standard_compiler`](#iqm.iqm_client.iqm_client.IQMClient.get_standard_compiler "iqm.iqm_client.iqm_client.IQMClient.get_standard_compiler") | Create a compiler instance for the connected quantum computer. |
| [`get_static_quantum_architecture`](#iqm.iqm_client.iqm_client.IQMClient.get_static_quantum_architecture "iqm.iqm_client.iqm_client.IQMClient.get_static_quantum_architecture") | Retrieve the static quantum architecture (SQA) from the server. |
| [`submit_circuit_job`](#iqm.iqm_client.iqm_client.IQMClient.submit_circuit_job "iqm.iqm_client.iqm_client.IQMClient.submit_circuit_job") | Submit a circuit job to execute a circuit batch to a quantum computer. |
| [`submit_circuits`](#iqm.iqm_client.iqm_client.IQMClient.submit_circuits "iqm.iqm_client.iqm_client.IQMClient.submit_circuits") | Submit a batch of quantum circuits for execution on a quantum computer. |
| [`submit_playlist`](#iqm.iqm_client.iqm_client.IQMClient.submit_playlist "iqm.iqm_client.iqm_client.IQMClient.submit_playlist") | Submit a run definition for execution. |

*static* from_url(*iqm_server_url: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *quantum_computer: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *token: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *tokens_file: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *client_signature: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [IQMClient](#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient")  
Utility constructor using [`IQMServerClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient").

Parameters:  
- **iqm_server_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – URL for accessing the IQM Server. Has to start with http or https.

- **quantum_computer** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – ID or alias of the quantum computer to connect to, if the IQM Server instance controls more than one. If not given, uses the default one on the server.

- **token** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Long-lived authentication token in plain text format. If `token` is given no other user authentication parameters should be given.

- **tokens_file** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Path to a tokens file used for authentication. If `tokens_file` is given no other user authentication parameters should be given.

- **client_signature** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – String that IQMClient adds to User-Agent header of requests it sends to the server. The signature is appended to IQMClient’s own version information and is intended to carry additional version information, for example the version information of the caller.

Return type:  
[*IQMClient*](#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient")

Alternatively, the arguments can also be given in environment variables `IQM_SERVER_URL`, `IQM_QUANTUM_COMPUTER`, `IQM_TOKEN`, `IQM_TOKENS_FILE`. Same combination restrictions apply for values given as environment variables as for the arguments.

get_health() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Health status of the quantum computer.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_about() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Information about the quantum computer.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

submit_circuits(*circuits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") \| \_Circuit \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *\**, *qubit_mapping: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None = None*, *calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → CircuitJobTracker  
Submit a batch of quantum circuits for execution on a quantum computer.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") *\|* *\_Circuit* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Circuits to be executed.

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*) – Mapping of logical qubit names to physical qubit names. Can be set to `None` if all `circuits` already use physical qubit names. Note that the `qubit_mapping` is used for all `circuits`.

- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – ID of the calibration set to use, or `None` to use the current default calibration.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of times `circuits` are executed. Must be greater than zero.

- **options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") *\|* *None*) – Various discrete options for compiling quantum circuits to instruction schedules.

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Submits the job to the timeslot queue if set to `True`. If set to `False`, the job is submitted to the normal on-demand queue.

Returns:  
Job object, containing the ID for the created job. You can query the job status and the execution results using the methods of this object.

Return type:  
*CircuitJobTracker*

create_circuit_job_definition(*circuits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") \| \_Circuit \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *\**, *qubit_mapping: WithJsonSchema(json_schema={'anyOf': \[{'type': 'array', 'items': {'type': 'object', 'required': \['logical_name', 'physical_name'\], 'properties': {'logical_name': {'type': 'string'}, 'physical_name': {'type': 'string'}}, 'additionalProperties': False}}, {'type': 'null'}\]}, mode=None)\] \| None = None*, *calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → PostJobsRequest  
Create a circuit execution job definition without sending it to the server.

This is called in [`submit_circuits()`](#iqm.iqm_client.iqm_client.IQMClient.submit_circuits "iqm.iqm_client.iqm_client.IQMClient.submit_circuits") and does not need to be called separately in normal usage.

Can be used to inspect the circuit job definition that would be submitted by [`submit_circuit_job()`](#iqm.iqm_client.iqm_client.IQMClient.submit_circuit_job "iqm.iqm_client.iqm_client.IQMClient.submit_circuit_job"), without actually submitting it for execution.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)") *\|* *\_Circuit* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Circuits to be executed.

- **qubit_mapping** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* *BeforeValidator(func=~iqm.station_control.interface.models.circuit.\_parse_legacy_qubit_mapping,* *json_schema_input_type=PydanticUndefined),* *PlainSerializer(func=~iqm.station_control.interface.models.circuit.\_serialize_as_legacy_qubit_mapping,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={'anyOf':* *\[{'type': 'array',* *'items': {'type': 'object',* *'required':* *\['logical_name',* *'physical_name'\],* *'properties': {'logical_name': {'type': 'string'},* *'physical_name': {'type': 'string'}},* *'additionalProperties': False}},* *{'type': 'null'}\]},* *mode=None)\]* *\|* *None*) – Mapping of logical qubit names to physical qubit names. Can be set to `None` if all `circuits` already use physical qubit names. Note that the `qubit_mapping` is used for all `circuits`.

- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – ID of the calibration set to use, or `None` to use the current default calibration.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of times `circuits` are executed. Must be greater than zero.

- **options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") *\|* *None*) – Various discrete options for compiling quantum circuits to instruction schedules.

Returns:  
CircuitJobDefinition that would be submitted by equivalent call to [`submit_circuits()`](#iqm.iqm_client.iqm_client.IQMClient.submit_circuits "iqm.iqm_client.iqm_client.IQMClient.submit_circuits").

Return type:  
*PostJobsRequest*

submit_circuit_job(*circuit_job_definition: PostJobsRequest*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → CircuitJobTracker  
Submit a circuit job to execute a circuit batch to a quantum computer.

This is called in [`submit_circuits()`](#iqm.iqm_client.iqm_client.IQMClient.submit_circuits "iqm.iqm_client.iqm_client.IQMClient.submit_circuits") and does not need to be called separately in normal usage.

Parameters:  
- **circuit_job_definition** (*PostJobsRequest*) – Circuit job definition to be submitted for execution.

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Submits the job to the timeslot queue if set to `True`. If set to `False`, the job is submitted to the normal on-demand queue.

Returns:  
CircuitJobTracker object, can be used to query the results.

Return type:  
*CircuitJobTracker*

get_job(*job_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → JobTracker  
Build a new job tracker object for a submitted job.

Can be used e.g. when you wish to query the results of a job submitted in a different Python session.

Parameters:  
**job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
JobTracker object, can be used to query the results.

Return type:  
*JobTracker*

cancel_job(*job_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Cancel a job that has been submitted for execution.

A canceled job will remain in the server database, but it will not be executed. If the job is currently being executed, it is interrupted. If the job was already executed (or failed), it will remain in its current terminal state.

Parameters:  
**job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be canceled.

Return type:  
None

delete_job(*job_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Delete a job that has been submitted for execution.

Works like [`cancel_job()`](#iqm.iqm_client.iqm_client.IQMClient.cancel_job "iqm.iqm_client.iqm_client.IQMClient.cancel_job"), but also removes the job from the IQM Server database.

Warning

There is no way to recover a deleted job.

Parameters:  
**job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be deleted.

Return type:  
None

get_static_quantum_architecture() → StaticQuantumArchitecture  
Retrieve the static quantum architecture (SQA) from the server.

Caches the result and returns it on later invocations.

Returns:  
Static quantum architecture of the executor.

Return type:  
*StaticQuantumArchitecture*

get_quality_metric_set(*calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → ObservationSetWithObservationData  
Retrieve the latest quality metric set for the given calibration set from the server.

Parameters:  
**calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – ID of the calibration set for which the quality metrics are returned. If `None`, the current default calibration set is used.

Returns:  
Requested quality metric set.

Return type:  
*ObservationSetWithObservationData*

get_calibration_set(*calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → ObservationSetWithObservationData  
Retrieve the given calibration set from the server.

Parameters:  
**calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – ID of the calibration set to retrieve. If `None`, the current default calibration set is retrieved.

Returns:  
Requested calibration set.

Return type:  
*ObservationSetWithObservationData*

get_dynamic_quantum_architecture(*calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → DynamicQuantumArchitecture  
Retrieve the dynamic quantum architecture (DQA) for the given calibration set from the server.

Caches the result and returns the same result on later invocations, unless `calibration_set_id` is `None`. If `calibration_set_id` is `None`, always retrieves the result from the server because the default calibration set may have changed.

Parameters:  
**calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – ID of the calibration set for which the DQA is retrieved. If `None`, use current default calibration set on the server.

Returns:  
Dynamic quantum architecture corresponding to the given calibration set.

Return type:  
*DynamicQuantumArchitecture*

get_feedback_groups() → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\], ...\]  
Retrieve groups of qubits that can receive real-time feedback signals from each other.

Real-time feedback enables conditional gates such as cc_prx. Some hardware configurations support routing real-time feedback only between certain qubits.

Returns:  
Feedback groups. Within a group, any qubit can receive real-time feedback from any other qubit in  
the same group. A qubit can belong to multiple groups. If there is only one group, there are no restrictions regarding feedback routing.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\], …\]

get_job_measurement_counts(*job_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[CircuitMeasurementCounts\]  
Query the measurement counts of an executed job.

Parameters:  
**job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, measurement results in histogram representation.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*CircuitMeasurementCounts*\]

get_job_measurements(*job_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\]  
Query the measurement results of an executed job.

Parameters:  
**job_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, the measurement results.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\]

get_calibration_quality_metrics(*calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → ObservationFinder  
Retrieve the given calibration set and related quality metrics from the server.

Warning

This method is an experimental interface to the quality metrics and calibration data. The API may change considerably in the next versions *with no backwards compatibility*, including the API of the ObservationFinder class.

Parameters:  
**calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – ID of the calibration set to retrieve. If `None`, the current default calibration set is retrieved.

Returns:  
Requested calibration set and related quality metrics in a searchable structure.

Return type:  
*ObservationFinder*

*property* quantum_computer_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the quantum computer this client is connected to.

get_standard_compiler(*loading_rules: Sequence\[RuleType\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *exa_style_pp: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *controller_mapping: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *gate_definitions: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), QuantumOp\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → Compiler  
Create a compiler instance for the connected quantum computer.

Note

If you only intend to execute circuit-level jobs, you do not need to use this method.

The Compiler enables pulse-level access to the quantum computer. It is used for compiling

- quantum circuits to `TimeBoxes`

- TimeBoxes to abstract hardware instruction `Schedules`

- Schedules to a `Playlists`, which can be submitted for execution using [`submit_playlist()`](#iqm.iqm_client.iqm_client.IQMClient.submit_playlist "iqm.iqm_client.iqm_client.IQMClient.submit_playlist"). TODO explain RunDefinition?

Parameters:  
- **loading_rules** (*Sequence\[RuleType\]* *\|* *None*) – Observation loading rules. If `None`, will use the current default calibration set.

- **exa_style_pp** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to do EXA-style dataset post-processing by default.

- **controller_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]* *\|* *None*) – Dictionary that maps physical QPU component names to their device controller names. The dictionary is of the form: `{<component_name>: {<operation_name>: <controller name>}}`, where operation is one of the following: “drive”, “readout”, “flux” (not all components have all operations supported). If None, use the default controller mapping for the connected quantum computer.

- **gate_definitions** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *QuantumOp\]* *\|* *None*) – Names of quantum operations mapped to their definitions, see `QuantumOp`. If None, use the default quantum operations from [`iqm.pulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.html#module-iqm.pulse "(in iqm.pulse v15.0.0)").

Returns:  
The compiler object.

Return type:  
Compiler

submit_playlist(*run_definition: RunDefinition*, *\**, *context: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Any\]*, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → RunJobTracker  
Submit a run definition for execution.

Parameters:  
- **run_definition** (*RunDefinition*)

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]*)

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

Return type:  
RunJobTracker

get_chip_label() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
QPU label of the current quantum computer.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_chip_topology() → ChipTopology  
Chip topology of the current quantum computer.

Describes the QPU components and their connectivity. Similar to [`get_static_quantum_architecture()`](#iqm.iqm_client.iqm_client.IQMClient.get_static_quantum_architecture "iqm.iqm_client.iqm_client.IQMClient.get_static_quantum_architecture"), but provides more detailed information.

Return type:  
*ChipTopology*

get_calibration_set_stash(*calibration_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['default'\] = 'default'*) → \_ObservationSetStash  
Contents of a calibration set in a stash adapter.

Parameters:  
**calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\]*)

Return type:  
*\_ObservationSetStash*

Inheritance

![Inheritance diagram of iqm.iqm_client.iqm_client.IQMClient](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-9858eda60d43d51fb1396e7a56fadcce02674989.png)
