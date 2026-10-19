> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.StationControlExecutor.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.StationControlExecutor.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 afd5f7b8452a46f671a47e94aec0bee3682deaccf35e86a2e12f5b1ef6a69529.

# StationControlExecutor

Module: [`iqm.station_control.client.station_control_executor`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_executor.html#module-iqm.station_control.client.station_control_executor "iqm.station_control.client.station_control_executor")

*class* StationControlExecutor(*client*)  
Bases: [`ExecutorInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "iqm.station_control.interface.executor_interface.ExecutorInterface")

Concrete executor that communicates with a remote Station Control to manage hardware execution and results.

Methods

|  |  |
|----|----|
| [`cancel_job`](#iqm.station_control.client.station_control_executor.StationControlExecutor.cancel_job "iqm.station_control.client.station_control_executor.StationControlExecutor.cancel_job") | Cancel a job that has been submitted for execution. |
| [`delete_job`](#iqm.station_control.client.station_control_executor.StationControlExecutor.delete_job "iqm.station_control.client.station_control_executor.StationControlExecutor.delete_job") | Delete a job that has been submitted for execution. |
| [`deserialize`](#iqm.station_control.client.station_control_executor.StationControlExecutor.deserialize "iqm.station_control.client.station_control_executor.StationControlExecutor.deserialize") | Reconstruct an instance from a dictionary payload. |
| [`get_artifact_measurement_counts`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_artifact_measurement_counts "iqm.station_control.client.station_control_executor.StationControlExecutor.get_artifact_measurement_counts") | Get the measurement counts of a circuit batch execution job. |
| [`get_artifact_measurements`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_artifact_measurements "iqm.station_control.client.station_control_executor.StationControlExecutor.get_artifact_measurements") | Get the measurement results of a circuit batch execution job. |
| [`get_artifact_sweep_results`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_artifact_sweep_results "iqm.station_control.client.station_control_executor.StationControlExecutor.get_artifact_sweep_results") | Get the results of an N-dimensional sweep job. |
| [`get_channel_properties`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_channel_properties "iqm.station_control.client.station_control_executor.StationControlExecutor.get_channel_properties") | Get control channel properties, including hardware limitations and supported instructions. |
| [`get_chip_design_record`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_chip_design_record "iqm.station_control.client.station_control_executor.StationControlExecutor.get_chip_design_record") | Get the chip design record for the QPU. |
| [`get_dut_label`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_dut_label "iqm.station_control.client.station_control_executor.StationControlExecutor.get_dut_label") | Get the QPU chip label. |
| [`get_experiment_configuration`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_experiment_configuration "iqm.station_control.client.station_control_executor.StationControlExecutor.get_experiment_configuration") | Get the default experiment configuration for the backend. |
| [`get_job`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_job "iqm.station_control.client.station_control_executor.StationControlExecutor.get_job") | Get status information about an existing job. |
| [`get_job_payload`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_job_payload "iqm.station_control.client.station_control_executor.StationControlExecutor.get_job_payload") | Get the job payload, i.e. the definition used to create the job. |
| [`get_or_create_software_version_set`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_or_create_software_version_set "iqm.station_control.client.station_control_executor.StationControlExecutor.get_or_create_software_version_set") | Get software version set ID from the database, or create one if it doesn't exist. |
| [`get_settings`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_settings "iqm.station_control.client.station_control_executor.StationControlExecutor.get_settings") | Default settings tree of the quantum computer. |
| [`get_static_quantum_architecture`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_static_quantum_architecture "iqm.station_control.client.station_control_executor.StationControlExecutor.get_static_quantum_architecture") | Get the simplified QPU topology. |
| [`serialize`](#iqm.station_control.client.station_control_executor.StationControlExecutor.serialize "iqm.station_control.client.station_control_executor.StationControlExecutor.serialize") | Serialize the object instance into a dictionary payload. |
| [`submit_job`](#iqm.station_control.client.station_control_executor.StationControlExecutor.submit_job "iqm.station_control.client.station_control_executor.StationControlExecutor.submit_job") | Submit a job definition for execution. |

Parameters:  
**client** ([*StationControlClient*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_client.StationControlClient.html#iqm.station_control.client.station_control_client.StationControlClient "iqm.station_control.client.station_control_client.StationControlClient"))

get_experiment_configuration()  
Get the default experiment configuration for the backend.

Returns:  
Default experiment configuration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_or_create_software_version_set(*software_version_set*)  
Get software version set ID from the database, or create one if it doesn’t exist.

Parameters:  
**software_version_set** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

get_dut_label()  
Get the QPU chip label.

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_chip_design_record()  
Get the chip design record for the QPU.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_channel_properties()  
Get control channel properties, including hardware limitations and supported instructions.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")\]

get_static_quantum_architecture()  
Get the simplified QPU topology.

Use [`get_chip_design_record()`](#iqm.station_control.client.station_control_executor.StationControlExecutor.get_chip_design_record "iqm.station_control.client.station_control_executor.StationControlExecutor.get_chip_design_record") for more detailed QPU topology information.

Return type:  
[*StaticQuantumArchitecture*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.html#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture "iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture")

get_settings()  
Default settings tree of the quantum computer.

Contains the available settings of the control instruments, and their default values.

Return type:  
[*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")

submit_job(*job_definition: [RunDefinition](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunDefinition.html#iqm.station_control.interface.models.run.RunDefinition "iqm.station_control.interface.models.run.RunDefinition")*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [RunJobTracker](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.RunJobTracker.html#iqm.station_control.client.job_trackers.RunJobTracker "iqm.station_control.client.job_trackers.RunJobTracker")\
submit_job(*job_definition: [PostJobsRequest](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html#iqm.station_control.interface.models.circuit.PostJobsRequest "iqm.station_control.interface.models.circuit.PostJobsRequest")*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [CircuitJobTracker](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.CircuitJobTracker.html#iqm.station_control.client.job_trackers.CircuitJobTracker "iqm.station_control.client.job_trackers.CircuitJobTracker")  
Submit a job definition for execution.

Parameters:  
- **job_definition** – The content of the job to be created (e.g. and experiment run, or a batch of quantum circuits).

- **use_timeslot** – Iff `True`, submit the job to the priority timeslot queue; otherwise, submit it to the shared FIFO queue.

Returns:  
A `JobTracker` instance wrapping the submitted job, providing methods to track progress and retrieve results.

get_job(*job_id*)  
Get status information about an existing job.

Allows for managing jobs submitted in previous sessions or by other clients.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – The ID of the job to query.

Returns:  
Current status and metadata of the job.

Return type:  
[*JobData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html#iqm.station_control.interface.models.jobs_new.JobData "iqm.station_control.interface.models.jobs_new.JobData")

get_job_payload(*job_id*, *job_type*)  
Get the job payload, i.e. the definition used to create the job.

Parameters:  
- **job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

- **job_type** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['run',* *'circuit'\]*)

Returns:  
Job payload.

Return type:  
[*RunDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunDefinition.html#iqm.station_control.interface.models.run.RunDefinition "iqm.station_control.interface.models.run.RunDefinition") \| [*PostJobsRequest*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html#iqm.station_control.interface.models.circuit.PostJobsRequest "iqm.station_control.interface.models.circuit.PostJobsRequest")

get_artifact_sweep_results(*job_id*)  
Get the results of an N-dimensional sweep job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
Results of the sweep job.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*ndarray*\]\]

get_artifact_measurements(*job_id*)  
Get the measurement results of a circuit batch execution job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, the measurement results.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\]

get_artifact_measurement_counts(*job_id*)  
Get the measurement counts of a circuit batch execution job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, the measurement counts.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CircuitMeasurementCounts*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.html#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts")\]

cancel_job(*job_id*)  
Cancel a job that has been submitted for execution.

A canceled job will remain in the execution record, but it will not proceed further. If the job is currently being executed, it is interrupted. If the job has already reached a terminal state (completed or failed), it will remain in that state.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be canceled.

Return type:  
*None*

delete_job(*job_id*)  
Delete a job that has been submitted for execution.

Works like [`cancel_job()`](#iqm.station_control.client.station_control_executor.StationControlExecutor.cancel_job "iqm.station_control.client.station_control_executor.StationControlExecutor.cancel_job"), but also removes the job from the IQM Server database.

Warning

There is no way to recover a deleted job.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be deleted.

Return type:  
*None*

serialize()  
Serialize the object instance into a dictionary payload.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* deserialize(*data*)  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*StationControlExecutor*](#iqm.station_control.client.station_control_executor.StationControlExecutor "iqm.station_control.client.station_control_executor.StationControlExecutor")

Inheritance

![Inheritance diagram of iqm.station_control.client.station_control_executor.StationControlExecutor](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-611d48a7ccae8b6c37a6bfa5a30047c14fcef1f7.png)
