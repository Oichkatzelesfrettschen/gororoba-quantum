> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 30c471f21c888cdbe4dc7a446249414210d79ea15a065a9bde4f2f8475ee52cc.

# IQMServerExecutor

Module: [`iqm.iqm_server_client.iqm_server_executor`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_executor.html#module-iqm.iqm_server_client.iqm_server_executor "iqm.iqm_server_client.iqm_server_executor")

*class* iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor(*client: [IQMServerClient](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient")*)  
Bases: `ExecutorInterface`

Concrete executor that communicates with a remote IQM Server to manage hardware execution and results.

Methods

|  |  |
|----|----|
| [`cancel_job`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.cancel_job "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.cancel_job") | Cancel a job that has been submitted for execution. |
| [`delete_job`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.delete_job "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.delete_job") | Delete a job that has been submitted for execution. |
| [`deserialize`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.deserialize "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.deserialize") | Reconstruct an instance from a dictionary payload. |
| [`get_artifact_measurement_counts`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_artifact_measurement_counts "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_artifact_measurement_counts") | Get the measurement counts of a circuit batch execution job. |
| [`get_artifact_measurements`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_artifact_measurements "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_artifact_measurements") | Get the measurement results of a circuit batch execution job. |
| [`get_artifact_sweep_results`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_artifact_sweep_results "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_artifact_sweep_results") | Get the results of an N-dimensional sweep job. |
| [`get_channel_properties`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_channel_properties "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_channel_properties") | Get control channel properties, including hardware limitations and supported instructions. |
| [`get_chip_design_record`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_chip_design_record "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_chip_design_record") | Get the chip design record for the QPU. |
| [`get_dut_label`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_dut_label "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_dut_label") | Get the QPU chip label. |
| [`get_experiment_configuration`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_experiment_configuration "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_experiment_configuration") | Get the default experiment configuration for the backend. |
| [`get_job`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_job "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_job") | Get status information about an existing job. |
| [`get_job_payload`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_job_payload "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_job_payload") | Get the job payload, i.e. the definition used to create the job. |
| [`get_or_create_software_version_set`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_or_create_software_version_set "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_or_create_software_version_set") | Get software version set ID from the database, or create one if it doesn't exist. |
| [`get_settings`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_settings "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_settings") | Default settings tree of the quantum computer. |
| [`get_static_quantum_architecture`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_static_quantum_architecture "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_static_quantum_architecture") | Get the simplified QPU topology. |
| [`serialize`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.serialize "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.serialize") | Serialize the object instance into a dictionary payload. |
| [`submit_job`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.submit_job "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.submit_job") | Submit a job definition for execution. |

Parameters:  
**client** ([*IQMServerClient*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient"))

get_experiment_configuration() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Get the default experiment configuration for the backend.

Returns:  
Default experiment configuration.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_or_create_software_version_set(*software_version_set: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
Get software version set ID from the database, or create one if it doesn’t exist.

Parameters:  
**software_version_set** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

get_dut_label() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Get the QPU chip label.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_chip_design_record() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Get the chip design record for the QPU.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_channel_properties() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ChannelProperties](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")\]  
Get control channel properties, including hardware limitations and supported instructions.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")\]

get_static_quantum_architecture() → StaticQuantumArchitecture  
Get the simplified QPU topology.

Use [`get_chip_design_record()`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_chip_design_record "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.get_chip_design_record") for more detailed QPU topology information.

Return type:  
*StaticQuantumArchitecture*

get_settings() → SettingNode  
Default settings tree of the quantum computer.

Contains the available settings of the control instruments, and their default values.

Return type:  
*SettingNode*

submit_job(*job_definition: RunDefinition*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → RunJobTracker\
submit_job(*job_definition: PostJobsRequest*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → CircuitJobTracker  
Submit a job definition for execution.

Parameters:  
- **job_definition** – The content of the job to be created (e.g. and experiment run, or a batch of quantum circuits).

- **use_timeslot** – Iff `True`, submit the job to the priority timeslot queue; otherwise, submit it to the shared FIFO queue.

Returns:  
A `JobTracker` instance wrapping the submitted job, providing methods to track progress and retrieve results.

get_job(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → JobData  
Get status information about an existing job.

Allows for managing jobs submitted in previous sessions or by other clients.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – The ID of the job to query.

Returns:  
Current status and metadata of the job.

Return type:  
*JobData*

get_job_payload(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*, *job_type: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['run', 'circuit'\]*) → RunDefinition \| PostJobsRequest  
Get the job payload, i.e. the definition used to create the job.

Parameters:  
- **job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

- **job_type** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['run',* *'circuit'\]*)

Returns:  
Job payload.

Return type:  
*RunDefinition* \| *PostJobsRequest*

get_artifact_sweep_results(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]\]  
Get the results of an N-dimensional sweep job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
Results of the sweep job.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]\]

get_artifact_measurements(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\]  
Get the measurement results of a circuit batch execution job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, the measurement results.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\]

get_artifact_measurement_counts(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[CircuitMeasurementCounts\]  
Get the measurement counts of a circuit batch execution job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, the measurement counts.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*CircuitMeasurementCounts*\]

cancel_job(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Cancel a job that has been submitted for execution.

A canceled job will remain in the execution record, but it will not proceed further. If the job is currently being executed, it is interrupted. If the job has already reached a terminal state (completed or failed), it will remain in that state.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be canceled.

Return type:  
None

delete_job(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Delete a job that has been submitted for execution.

Works like [`cancel_job()`](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.cancel_job "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor.cancel_job"), but also removes the job from the IQM Server database.

Warning

There is no way to recover a deleted job.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be deleted.

Return type:  
None

serialize() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Serialize the object instance into a dictionary payload.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* deserialize(*data: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*) → [IQMServerExecutor](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor")  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*IQMServerExecutor*](#iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor "iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor")

Inheritance

![Inheritance diagram of iqm.iqm_server_client.iqm_server_executor.IQMServerExecutor](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-b013bb72d468909a958bd9893a3bd9ab15648625.png)
