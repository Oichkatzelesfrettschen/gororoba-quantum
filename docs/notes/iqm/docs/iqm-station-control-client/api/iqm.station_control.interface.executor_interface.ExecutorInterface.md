> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bedb54b5524926782c2cbf879e15755ddf17a14af2e01b6cb74a223375d61cff.

# ExecutorInterface

Module: [`iqm.station_control.interface.executor_interface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.html#module-iqm.station_control.interface.executor_interface "iqm.station_control.interface.executor_interface")

*class* ExecutorInterface  
Bases: [`Serializable`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.serializable.Serializable.html#iqm.station_control.interface.serializable.Serializable "iqm.station_control.interface.serializable.Serializable"), [`Generic`](https://docs.python.org/3.11/library/typing.html#typing.Generic "(in Python v3.11)")\[`T_JobDefinition`, `T_JobTracker`\]

Interface for managing quantum job execution and results retrieval.

Implementations are responsible for protocol-specific communication with execution backends, such as remote services, local processes, or hardware simulators.

Methods

|  |  |
|----|----|
| [`cancel_job`](#iqm.station_control.interface.executor_interface.ExecutorInterface.cancel_job "iqm.station_control.interface.executor_interface.ExecutorInterface.cancel_job") | Cancel a job that has been submitted for execution. |
| [`delete_job`](#iqm.station_control.interface.executor_interface.ExecutorInterface.delete_job "iqm.station_control.interface.executor_interface.ExecutorInterface.delete_job") | Delete a job that has been submitted for execution. |
| [`get_artifact_measurement_counts`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_artifact_measurement_counts "iqm.station_control.interface.executor_interface.ExecutorInterface.get_artifact_measurement_counts") | Get the measurement counts of a circuit batch execution job. |
| [`get_artifact_measurements`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_artifact_measurements "iqm.station_control.interface.executor_interface.ExecutorInterface.get_artifact_measurements") | Get the measurement results of a circuit batch execution job. |
| [`get_artifact_sweep_results`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_artifact_sweep_results "iqm.station_control.interface.executor_interface.ExecutorInterface.get_artifact_sweep_results") | Get the results of an N-dimensional sweep job. |
| [`get_channel_properties`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_channel_properties "iqm.station_control.interface.executor_interface.ExecutorInterface.get_channel_properties") | Get control channel properties, including hardware limitations and supported instructions. |
| [`get_chip_design_record`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_chip_design_record "iqm.station_control.interface.executor_interface.ExecutorInterface.get_chip_design_record") | Get the chip design record for the QPU. |
| [`get_dut_label`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_dut_label "iqm.station_control.interface.executor_interface.ExecutorInterface.get_dut_label") | Get the QPU chip label. |
| [`get_experiment_configuration`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_experiment_configuration "iqm.station_control.interface.executor_interface.ExecutorInterface.get_experiment_configuration") | Get the default experiment configuration for the backend. |
| [`get_job`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_job "iqm.station_control.interface.executor_interface.ExecutorInterface.get_job") | Get status information about an existing job. |
| [`get_job_payload`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_job_payload "iqm.station_control.interface.executor_interface.ExecutorInterface.get_job_payload") | Get the job payload, i.e. the definition used to create the job. |
| [`get_or_create_software_version_set`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_or_create_software_version_set "iqm.station_control.interface.executor_interface.ExecutorInterface.get_or_create_software_version_set") | Get software version set ID from the database, or create one if it doesn't exist. |
| [`get_settings`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_settings "iqm.station_control.interface.executor_interface.ExecutorInterface.get_settings") | Default settings tree of the quantum computer. |
| [`get_static_quantum_architecture`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_static_quantum_architecture "iqm.station_control.interface.executor_interface.ExecutorInterface.get_static_quantum_architecture") | Get the simplified QPU topology. |
| [`submit_job`](#iqm.station_control.interface.executor_interface.ExecutorInterface.submit_job "iqm.station_control.interface.executor_interface.ExecutorInterface.submit_job") | Submit a job definition for execution. |

*abstractmethod* get_experiment_configuration()  
Get the default experiment configuration for the backend.

Returns:  
Default experiment configuration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*abstractmethod* get_or_create_software_version_set(*software_version_set*)  
Get software version set ID from the database, or create one if it doesn’t exist.

Parameters:  
**software_version_set** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

*abstractmethod* get_dut_label()  
Get the QPU chip label.

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

*abstractmethod* get_chip_design_record()  
Get the chip design record for the QPU.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*abstractmethod* get_static_quantum_architecture()  
Get the simplified QPU topology.

Use [`get_chip_design_record()`](#iqm.station_control.interface.executor_interface.ExecutorInterface.get_chip_design_record "iqm.station_control.interface.executor_interface.ExecutorInterface.get_chip_design_record") for more detailed QPU topology information.

Return type:  
[*StaticQuantumArchitecture*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.html#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture "iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture")

*abstractmethod* get_channel_properties()  
Get control channel properties, including hardware limitations and supported instructions.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")\]

*abstractmethod* get_settings()  
Default settings tree of the quantum computer.

Contains the available settings of the control instruments, and their default values.

Return type:  
[*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")

*abstractmethod* submit_job(*job_definition*, *\**, *use_timeslot=False*)  
Submit a job definition for execution.

Parameters:  
- **job_definition** (*T_JobDefinition*) – The content of the job to be created (e.g. and experiment run, or a batch of quantum circuits).

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff `True`, submit the job to the priority timeslot queue; otherwise, submit it to the shared FIFO queue.

Returns:  
A [`JobTracker`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.JobTracker.html#iqm.station_control.interface.executor_interface.JobTracker "iqm.station_control.interface.executor_interface.JobTracker") instance wrapping the submitted job, providing methods to track progress and retrieve results.

Return type:  
*T_JobTracker*

*abstractmethod* get_job(*job_id*)  
Get status information about an existing job.

Allows for managing jobs submitted in previous sessions or by other clients.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – The ID of the job to query.

Returns:  
Current status and metadata of the job.

Return type:  
[*JobData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobData.html#iqm.station_control.interface.models.jobs_new.JobData "iqm.station_control.interface.models.jobs_new.JobData")

*abstractmethod* get_job_payload(*job_id*, *job_type*)  
Get the job payload, i.e. the definition used to create the job.

Parameters:  
- **job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

- **job_type** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['run',* *'circuit'\]*)

Returns:  
Job payload.

Return type:  
*T_JobDefinition*

*abstractmethod* get_artifact_sweep_results(*job_id*)  
Get the results of an N-dimensional sweep job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
Results of the sweep job.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*ndarray*\]\]

*abstractmethod* get_artifact_measurements(*job_id*)  
Get the measurement results of a circuit batch execution job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, the measurement results.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\]

*abstractmethod* get_artifact_measurement_counts(*job_id*)  
Get the measurement counts of a circuit batch execution job.

Raises an error if the results are not available.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to query.

Returns:  
For each circuit in the batch, the measurement counts.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CircuitMeasurementCounts*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.html#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts")\]

*abstractmethod* cancel_job(*job_id*)  
Cancel a job that has been submitted for execution.

A canceled job will remain in the execution record, but it will not proceed further. If the job is currently being executed, it is interrupted. If the job has already reached a terminal state (completed or failed), it will remain in that state.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be canceled.

Return type:  
*None*

*abstractmethod* delete_job(*job_id*)  
Delete a job that has been submitted for execution.

Works like [`cancel_job()`](#iqm.station_control.interface.executor_interface.ExecutorInterface.cancel_job "iqm.station_control.interface.executor_interface.ExecutorInterface.cancel_job"), but also removes the job from the IQM Server database.

Warning

There is no way to recover a deleted job.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – ID of the job to be deleted.

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.station_control.interface.executor_interface.ExecutorInterface](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-3fc64194e682d07e51f01c25566934c422fad85d.png)
